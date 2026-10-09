# Módulo 4 — Persistencia y Memoria (Checkpointer vs Store)

En LangGraph, la persistencia se divide en dos sistemas complementarios fundamentales: el **Checkpointer** y el **Store**. Comprender sus diferencias y responsabilidades es esencial para diseñar agentes con memoria confiable.

---

## 1. Los Dos Pilares de la Persistencia

| Característica | Checkpointer | Store |
| :--- | :--- | :--- |
| **Alcance (Scope)** | **Por Hilo (Thread-scoped)** | **Global / Entre Hilos (Cross-thread)** |
| **Propósito** | Historial de mensajes y estado de ejecución del grafo paso a paso. | Memoria a largo plazo: perfiles de usuario, preferencias, documentos, reglas aprendidas. |
| **Escritura** | Automática: LangGraph escribe el estado tras cada superstep del grafo. | Explícita: Tu código invoca `store.put(namespace, key, value)`. |
| **Acceso desde el SDK** | Solo lectura (`client.threads.get_state(thread_id)`). | Lectura y Escritura (`client.store.put_item(...)`, `client.store.get_item(...)`). |
| **Motor de almacenamiento** | Tabla de checkpoints en Postgres (o `MemorySaver` en RAM). | Tabla de pares clave-valor estructurados en Postgres (o `InMemoryStore` en RAM). |

---

## 2. El Checkpointer en Detalle

El Checkpointer registra cada transición de estado en el grafo:
1. Permite pausar y reanudar la ejecución (Human-in-the-loop).
2. Permite rebobinar o bifurcar conversaciones (Time-travel debugging).
3. Asegura tolerancia a fallos: si un worker o servidor colapsa a mitad de un run, el trabajo se reanuda desde el último superstep completado.

Ejemplo de lectura del historial de un hilo:
```python
state = await client.threads.get_state(thread_id)
messages = state["values"]["messages"]
```

---

## 3. El Store en Detalle: Namespaces y Llaves

El Store organiza la información jerárquicamente utilizando **Namespaces** (tuplas de cadenas) y una **clave (key)**:

```python
namespace = ("users", "estudiante_123")
await store.aput(
    namespace,
    key="profile",
    value={
        "nombre": "Juan",
        "nivel": "Avanzado",
        "tema_favorito": "Modelos Locales"
    }
)
```

Cualquier nodo del grafo que declare el argumento `store: BaseStore` puede leer o modificar datos en cualquier namespace:
```python
async def tutor_node(state: MessagesState, config: RunnableConfig, *, store: BaseStore):
    user_id = config["configurable"]["user_id"]
    item = await store.aget(("users", user_id), key="profile")
    perfil = item.value if item else {}
    ...
```

---

## 4. Scripts y Demostraciones del Módulo

### 4.1 Demostración Local (Probada con Ollama):
Ejecuta la simulación completa de persistencia en local:
```bash
cd python
uv run python m4/l2/local_persistence_demo.py
```
Este script valida:
1. Almacenamiento del perfil en el `Store` en el namespace `("users", "juan")`.
2. Interacción en el hilo `thread-A` donde el tutor responde reconociendo al usuario.
3. Apertura de un nuevo hilo `thread-B` (vacío en el Checkpointer), pero donde el agente mantiene el conocimiento de quién es el usuario gracias al `Store`.
4. Inspección del historial de checkpoints guardados.

### 4.2 Scripts Oficiales del Curso:
- [`python/m4/l2/store.py`](file:///home/juansebas7ian/Proyectos/GitHub/lca-deployment/python/m4/l2/store.py): Escribe y lee perfiles en el Store a través del SDK del servidor.
- [`python/m4/l2/checkpointer.py`](file:///home/juansebas7ian/Proyectos/GitHub/lca-deployment/python/m4/l2/checkpointer.py): Ejecuta una consulta al agente y examina los checkpoints creados en la base de datos.
