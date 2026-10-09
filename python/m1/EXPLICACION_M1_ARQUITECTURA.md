# Módulo 1 — Arquitectura de Despliegue de LangGraph

Este módulo explica cómo se estructura y ejecuta un sistema de agentes basado en LangGraph en entornos de producción y desarrollo local.

---

## 1. Las Tres Capas de la Pila

1. **LangChain**: Proporciona primitivas fundamentales: integraciones de modelos (como `ChatOllama` para ejecución local y privada con tus propios LLMs), herramientas (`Tools`), esquemas de mensajes (`HumanMessage`, `AIMessage`).
2. **LangGraph**: El motor de orquestación de grafos. Permite crear ciclos, ramificaciones, control de estados tipados (`MessagesState`) y puntos de control (`Checkpointer`).
3. **LangGraph Deployment (Agent Server)**: La capa de infraestructura. Convierte tu grafo en una API REST y WebSocket/SSE lista para producción con colas, trabajadores asíncronos y persistencia en base de datos.


---

## 2. Componentes del Agent Server

Cuando despliegas con LangGraph (ya sea en local con `langgraph dev` o en la nube), el sistema se compone de:

```
[ Cliente / SDK / UI ]
          │ (HTTP / SSE / WebSocket)
          ▼
   [ API Server ]  <─── Autenticación & Validación
          │
    (Cola de tareas)
          ▼
       [ Redis ]
          │
    (Distribución de ejecuciones)
          ▼
  [ Worker Container ]  <─── Ejecuta los nodos de LangGraph y llamadas a LLMs
       │            │
       ▼            ▼
 [ Checkpointer ] [ Store ]
       └──────┬─────┘
              ▼
         [ Postgres ]  <─── Persistencia de estado y memoria a largo plazo
```

### Componentes clave:
- **API Server**: Expone endpoints como `/runs`, `/threads`, `/assistants`, `/ok`. No ejecuta el grafo pesado directamente; encola las peticiones.
- **Redis**: Cola en memoria de alto rendimiento para distribuir tareas y coordinar ejecuciones concurrentes.
- **Workers**: Procesos independientes que toman las tareas de la cola y ejecutan la lógica del grafo. Si un worker falla, el estado se reanuda desde el último checkpoint.
- **Postgres**: Base de datos relacional donde se guardan:
  - **Checkpointer**: El historial detallado paso a paso de cada conversación (thread).
  - **Store**: Memoria compartida entre múltiples threads (perfiles de usuario, documentos).

---

## 3. Flujo de Vida de una Ejecución (Run Lifecycle)

1. **Recepción**: El cliente invoca `client.runs.create(thread_id, assistant_id, input=...)` o `client.runs.stream(...)`.
2. **Encolado**: El API Server valida permisos y empuja la tarea a la cola de Redis.
3. **Ejecución de Supersteps**: Un worker toma la tarea. En cada "superstep" (ejecución de un nodo del grafo):
   - El nodo genera un nuevo estado.
   - El worker escribe el nuevo estado en el **Checkpointer** en Postgres.
   - Se emiten eventos de streaming (SSE) de vuelta al cliente.
4. **Finalización**: El run alcanza el nodo `END` o se interrumpe si requiere interacción humana (Human-in-the-loop).

---

## 4. Archivo de Configuración: `langgraph.json`

Cada proyecto o microservicio de LangGraph se describe con un archivo [`langgraph.json`](file:///home/juansebas7ian/Proyectos/GitHub/lca-deployment/python/deep_tutor/langgraph.json):

```json
{
  "dependencies": ["."],
  "graphs": {
    "tutor": "./agent/agent.py:graph"
  },
  "http": {
    "app": "./ui/app.py:app"
  },
  "env": "../.env"
}
```

- **`dependencies`**: Rutas o paquetes que deben instalarse en el contenedor.
- **`graphs`**: Diccionario de grafos expuestos. En este ejemplo, el grafo exportado en `agent.py` se expone bajo el identificador `"tutor"`.
- **`http`**: *(Opcional)* Servidor FastAPI complementario para servir páginas web o rutas personalizadas en el mismo puerto.
- **`env`**: Ruta al archivo de variables de entorno.
- **`auth`**: *(Opcional, visto en Módulo 5)* Ruta al archivo de autenticación personalizada (`auth.py:auth`).
