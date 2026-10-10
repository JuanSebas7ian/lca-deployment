---
title: "Lesson 3 - Agent Client y SDK (Conexión al Agente con SDKs)"
source: "https://academy.langchain.com/courses/take/langsmith-deployment"
author: "LangChain Academy / LCA Deployment"
created: 2026-10-09
description: "Módulo 1: Lección 3 - Explicación de qué es un SDK, por qué las librerías terminan en -sdk, y el rol de agent_client.py en la integración del agente con la interfaz web."
tags:
  - "langgraph"
  - "sdk"
  - "agent_client"
  - "fastapi"
  - "streaming"
  - "deployment"
---

# Lección 3: Clientes de Agentes y el uso de SDKs (`agent_client.py`)

En esta lección se explica qué es un **SDK**, por qué existen paquetes que terminan en `-sdk` (como `langgraph-sdk`), y cómo se estructura el módulo **`agent_client.py`** para conectar una aplicación web (FastAPI / frontend) con un agente de LangGraph desplegado.

---

## 1. ¿Qué es un SDK y por qué terminan en `-sdk`?

**SDK** significa **Software Development Kit** (*Kit de Desarrollo de Software*).

### La Necesidad: APIs REST vs. Clientes Nativos
Cuando un servicio backend o agente (como LangGraph Server, LangSmith, AWS o Stripe) se despliega, expone una **API HTTP/REST** con múltiples endpoints:
- `POST /threads`
- `POST /assistants`
- `POST /runs/stream`
- `PUT /store/items`

Sin un SDK, tendríamos que escribir código HTTP manual con librerías como `requests` o `httpx`:

```python
# ❌ Enfoque manual sin SDK (propenso a errores, verboso, sin tipos)
import httpx

async with httpx.AsyncClient() as client:
    resp = await client.post(
        f"{deployment_url}/runs/stream",
        headers={"x-api-key": api_key, "Content-Type": "application/json"},
        json={"assistant_id": "...", "input": {"messages": [...]}}
    )
    # Ahora tendrías que parsear manualmente el stream de Server-Sent Events (SSE)
```

### ¿Qué aporta un SDK?
Un SDK como **`langgraph-sdk`** encapsula toda esa complejidad en clases y métodos nativos de Python:

```python
# ✅ Enfoque limpio con el SDK de LangGraph
from langgraph_sdk import get_client

client = get_client(url=deployment_url, api_key=api_key)
await client.runs.stream(thread_id, assistant_id, input=...)
```

### Ventajas clave de las librerías `-sdk`:
1. **Abstracción:** Oculta detalles de red como rutas URL, serialización/deserialización JSON y encabezados HTTP.
2. **Streaming y WebSockets:** Gestiona de forma nativa protocolos como SSE (*Server-Sent Events*) y lectura token a token.
3. **Autenticación y Reintentos:** Manejo automático de encabezados de autorización, tokens temporales y lógica de reintentos ante desconexiones.
4. **Tipado Estático y Autocompletado:** Tu editor (VS Code, IDEs con Pyright/Pylance) reconoce los tipos de datos, parámetros y métodos disponibles (`.store`, `.assistants`, `.threads`, etc.).

---

## 2. Arquitectura: La UI y el Agente Desplegado

En este proyecto, el agente no corre en el mismo proceso ni en el mismo hilo que la interfaz web:

```
┌─────────────────────────────────┐
│     Navegador del Estudiante    │
│        (HTML / JS / CSS)        │
└───────────────┬─────────────────┘
                │ HTTP / REST
                ▼
┌─────────────────────────────────┐
│     FastAPI (ui/app.py)         │
│  - Rutas: /register, /login,    │
│    /chat, /resources            │
└───────────────┬─────────────────┘
                │ Llama a funciones de
                ▼
┌─────────────────────────────────┐
│       ui/agent_client.py        │
│   (Usa langgraph-sdk Client)    │
└───────────────┬─────────────────┘
                │ HTTP / SSE / REST
                ▼
┌─────────────────────────────────┐
│     Servidor LangGraph          │
│   (Grafo "tutor" en ejecución)  │
│   - Checkpointer                │
│   - LangGraph Store             │
└─────────────────────────────────┘
```

Esta separación desacopla la capa de presentación de la lógica del agente, permitiendo escalar el servidor del agente o migrarlo a la nube sin modificar la lógica de la UI.

---

## 3. Desglose de `ui/agent_client.py`

El archivo [`ui/agent_client.py`](file:///home/juansebas7ian/Proyectos/GitHub/lca-deployment/python/deep_tutor/ui/agent_client.py) contiene tres funciones esenciales:

### A. Creación y Autenticación del Cliente: `create_client`

```python
def create_client(deployment_url: str) -> LangGraphClient:
    """Create a LangGraph client connected to the deployment."""
    api_key = os.environ.get("DEEP_TUTOR_API_KEY", "")
    return get_client(url=deployment_url, api_key=api_key)
```
- Lee la clave de API (`DEEP_TUTOR_API_KEY`) si existe.
- Llama a `get_client` del SDK para instanciar un [`LangGraphClient`](file:///home/juansebas7ian/Proyectos/GitHub/lca-deployment/python/deep_tutor/ui/agent_client.py#L15).

---

### B. Streaming en Tiempo Real: `stream_response`

```python
async def stream_response(
    client: LangGraphClient,
    thread_id: str,
    assistant_id: str,
    message: str,
) -> AsyncGenerator[str, None]:
    """Send a message and stream the agent's response."""
    async for event in client.runs.stream(
        thread_id,
        assistant_id,
        input={"messages": [{"role": "user", "content": message}]},
        stream_mode="messages-tuple",
    ):
        if event.event != "messages":
            continue
        message_chunk, _metadata = event.data
        if message_chunk.get("type") != "AIMessageChunk":
            continue  # ignora llamadas intermedias a herramientas; solo muestra la respuesta
        content = message_chunk.get("content", "")
        if isinstance(content, list):
            content = "".join(
                b.get("text", "") for b in content
                if isinstance(b, dict) and b.get("type") == "text"
            )
        if content:
            yield content
```

- **`client.runs.stream(...)`**: Dispara la ejecución del agente en modo streaming.
- **Filtro de mensajes:** Durante la ejecución, el agente puede emitir llamadas a herramientas (`tool_calls`) o respuestas de herramientas. El código filtra para procesar únicamente trozos de tipo `AIMessageChunk`.
- **Generador Asíncrono (`yield`):** Emite el texto token a token hacia FastAPI, que lo envía directamente al navegador mediante un `StreamingResponse`.

---

### C. Sesiones y Módulos del Estudiante: `create_student_sessions`

```python
async def create_student_sessions(
    client: LangGraphClient,
    first_name: str = "Student",
    last_name: str = "",
    email: str = "",
    namespace: str = "",
) -> list[dict]:
    """Create one assistant + thread per module for a student."""
    student_name = f"{first_name} {last_name}".strip()
    sessions = []
    for module in MODULES:
        assistant = await client.assistants.create(
            graph_id="tutor",
            name=f"{student_name} — {module['id']}",
            context={
                "module_id": module["id"],
                "store_namespace": namespace,
            },
        )
        thread = await client.threads.create()
        sessions.append({
            "module_id": module["id"],
            "assistant_id": assistant["assistant_id"],
            "thread_id": thread["thread_id"],
        })
    return sessions
```

- **Múltiples Módulos:** Por cada módulo del curso (`module-1`, `module-2`, etc.), crea un asistente especializado con su propio contexto.
- **Hilos independientes:** Crea un hilo de conversación (`thread`) por módulo, garantizando que el historial de chat de un tema no interfiera con otro.

---

## 4. Caso Práctico: Importancia del Tipado con el SDK

Al utilizar SDKs en Python, tipar adecuadamente los clientes evita errores sutiles de análisis estático (Pyright / Pylance / mypy).

### El Problema
Si en el caché de la aplicación web ([ui/app.py](file:///home/juansebas7ian/Proyectos/GitHub/lca-deployment/python/deep_tutor/ui/app.py)) se anota el cliente como tipo genérico `object`:
```python
# ❌ Inadecuado:
_client_cache: dict[str, object] = {}

def get_cached_client(deployment_url: str):
    ...
```
El analizador estático inferirá que el cliente devuelto es de clase `object`. Al intentar acceder a métodos del SDK como:
```python
await client.store.put_item(...)
```
El IDE generará el error:
> `Cannot access attribute "store" for class "object"` / `Object of class "object" has no attribute "store"`

### La Solución
Importar y anotar explícitamente el tipo de cliente expuesto por el SDK:
```python
# ✅ Correcto:
from langgraph_sdk.client import LangGraphClient

_client_cache: dict[str, LangGraphClient] = {}

def get_cached_client(deployment_url: str) -> LangGraphClient:
    ...
```
Esto habilita la verificación estática de tipos, el autocompletado en el editor y previene errores en tiempo de ejecución.
