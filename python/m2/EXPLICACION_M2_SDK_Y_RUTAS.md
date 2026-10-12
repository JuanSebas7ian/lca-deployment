# Módulo 2 — LangGraph SDK y Rutas Personalizadas

Este módulo profundiza en cómo las aplicaciones cliente (frontends, microservicios o scripts de automatización) se comunican con los agentes desplegados a través del **LangGraph SDK** y cómo se implementan **Rutas Personalizadas** (Custom Routes).

---

## 1. El LangGraph SDK

El SDK (`langgraph-sdk`) es el cliente oficial para interactuar con cualquier despliegue de LangGraph:

```python
from langgraph_sdk import get_client

client = get_client(url="http://localhost:2024", api_key="...")
```

### Conceptos Clave:
1. **Graphs**: La definición abstracta del flujo de trabajo (e.g., `"tutor"`).
2. **Assistants**: Una configuración específica de un grafo con metadatos o contexto predeterminado (por ejemplo, un asistente para "módulo 1" y otro para "módulo 2" sobre el mismo grafo).
3. **Threads**: Un hilo de conversación. El checkpointer aísla el historial de mensajes por `thread_id`.
4. **Runs**: Una ejecución de un agente dentro de un hilo. Puede ser:
   - Síncrono bloqueante: `await client.runs.wait(thread_id, assistant_id, input=...)`
   - En Streaming (SSE): `client.runs.stream(thread_id, assistant_id, input=..., stream_mode="messages-tuple")`

---

## 2. Invocación vs Streaming

### Esperar Respuesta Completa (`wait`):
Ideal para jobs en segundo plano o respuestas donde no se requiere retroalimentación visual inmediata.
```python
result = await client.runs.wait(
    thread["thread_id"],
    "tutor",
    input={"messages": [{"role": "user", "content": "¿Qué es LangGraph?"}]},
)
print(result["messages"][-1]["content"])
```

### Streaming de Tokens en Tiempo Real (`stream`):
Ideal para interfaces de usuario interactivas:
```python
async for event in client.runs.stream(
    thread["thread_id"],
    "tutor",
    input={"messages": [{"role": "user", "content": "¿Qué es LangGraph?"}]},
    stream_mode="messages-tuple",
):
    if event.event == "messages":
        message_chunk, _metadata = event.data
        if message_chunk.get("type") == "AIMessageChunk":
            print(message_chunk.get("content", ""), end="", flush=True)
```

---

## 3. Rutas Personalizadas con FastAPI (Custom Routes)

En aplicaciones reales a menudo se requiere un backend intermedio que maneje autenticación, registro de usuarios o sirva un frontend estático (HTML/JS) junto al agente.

LangGraph permite especificar en `langgraph.json`:
```json
{
  "http": {
    "app": "./ui/app.py:app"
  }
}
```
En este patrón, FastAPI corre en el mismo puerto que el servidor de LangGraph y puede exponer endpoints como `/login`, `/register`, `/chat`, actuando como proxy hacia el SDK de LangGraph.

---

## 4. Scripts y Demostraciones del Módulo

### 4.1 Agente Local Demostrativo (Probado con Ollama):
Hemos creado un script independiente para probar todos los conceptos de este módulo en local sin necesidad de levantar contenedores:
```bash
cd python
uv run python m2/local_m2_agent.py
```
Este script demuestra:
- Creación del grafo con `ChatOllama`.
- Manejo de dos hilos independientes (`thread-1` y `thread-2`).
- Comprobación de que el hilo 2 no tiene acceso a la información privada del hilo 1.
- Streaming en vivo de la respuesta del modelo `gemma4:12b`.

### 4.2 Scripts Oficiales contra el Servidor de LangGraph:
Si tienes corriendo el servidor local de desarrollo (`langgraph dev` en `deep_tutor`):
- [`python/m2/m2.1-connecting.py`](file:///home/juansebas7ian/Proyectos/GitHub/lca-deployment/python/m2/m2.1-connecting.py): Conexión, creación de hilos y streaming contra el grafo desplegado.
- [`python/m2/m2.2-assistants.py`](file:///home/juansebas7ian/Proyectos/GitHub/lca-deployment/python/m2/m2.2-assistants.py): Creación y comparación de múltiples asistentes configurados con diferentes contextos.
