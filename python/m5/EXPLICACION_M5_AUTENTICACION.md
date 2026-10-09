# Módulo 5 — Autenticación y Autorización en LangGraph

En aplicaciones empresariales o SaaS multi-inquilino (multi-tenant), es crítico proteger los agentes para que los usuarios solo puedan acceder a sus propias conversaciones y datos. Este módulo explica cómo implementar **Autenticación (AuthN)** y **Autorización (AuthZ)** nativa en LangGraph.

---

## 1. Autenticación vs Autorización

- **Autenticación (AuthN — ¿Quién eres?)**: Valida las credenciales del cliente (por ejemplo, verificando un JSON Web Token o Bearer Token en el encabezado HTTP). Si las credenciales son válidas, produce un objeto de identidad del usuario (`user dict`).
- **Autorización (AuthZ — ¿Qué tienes permitido hacer?)**: Determina si ese usuario autenticado tiene permisos para realizar una acción específica sobre un recurso (por ejemplo, si Bob puede leer el `thread_id` creado por Alice).

> ⚠️ **Lección clave del curso:** *Estar autenticado NO significa estar autorizado*. Un sistema que solo valida tokens pero no restringe hilos permitiría que cualquier usuario autenticado lea las conversaciones de todos los demás.

---

## 2. El Pipeline de Autenticación de LangGraph

LangGraph proporciona la clase `Auth` en `langgraph_sdk.auth`:

### 2.1 El Handler `@auth.authenticate`
Se ejecuta en cada petición HTTP entrante antes de tocar cualquier grafo:

```python
from langgraph_sdk import Auth

auth = Auth()

@auth.authenticate
async def get_current_user(authorization: str | None) -> Auth.types.MinimalUserDict:
    if not authorization:
        raise Auth.exceptions.HTTPException(status_code=401, detail="Token no proporcionado")
    
    scheme, _, token = authorization.partition(" ")
    if scheme.lower() != "bearer":
        raise Auth.exceptions.HTTPException(status_code=401, detail="Esquema inválido")
    
    # Validar token con tu base de datos o proveedor (Auth0, Supabase, Firebase)
    user = validate_token_in_db(token)
    return {
        "identity": user["id"],       # Requerido: identificador único
        "name": user["name"],
        "role": user["role"],         # e.g., 'admin', 'student'
    }
```

---

## 3. Control de Acceso con `@auth.on` (Autorización)

Para asegurar los hilos y los runs, se registran decoradores `@auth.on`:

```python
# Proteger la lectura de hilos (solo el creador o un admin puede leerlo)
@auth.on.threads.read
async def on_read_thread(ctx, value):
    user = ctx.user
    thread_owner = value.get("metadata", {}).get("owner")
    if user.get("role") == "admin" or thread_owner == user["identity"]:
        return
    raise Auth.exceptions.HTTPException(status_code=403, detail="Acceso denegado")
```

---

## 4. Consumo de la Identidad dentro del Grafo

Cuando una petición pasa la autenticación, LangGraph inyecta automáticamente la información del usuario en la configuración del grafo bajo `langgraph_auth_user`:

```python
def mi_nodo(state: MessagesState, config: RunnableConfig):
    user = config["configurable"].get("langgraph_auth_user", {})
    identity = user.get("identity")
    user_name = user.get("name")
    
    # El LLM o la lógica de negocio puede personalizar la respuesta
    return {"messages": [AIMessage(content=f"Hola {user_name}, procesando tu solicitud.")]}
```

---

## 5. Scripts y Demostraciones del Módulo

### 5.1 Demostración Local (Probada con Ollama):
Hemos desarrollado una demostración completa que simula todo el pipeline en local:
```bash
cd python
uv run python m5/local_auth_demo.py
```
Este script demuestra:
1. Autenticación de dos usuarios con diferentes roles (Alice: `admin`, Bob: `student`).
2. Generación de un hilo protegido para Alice.
3. El intento de acceso no autorizado de Bob siendo interceptado y bloqueado con un `403 Forbidden`.
4. Respuestas contextualizadas generadas por el modelo local `qwen2.5:7b` reconociendo la identidad de cada usuario.

### 5.2 Lecciones y Ejercicios Incluidos:
- [`python/m5/l2/`](file:///home/juansebas7ian/Proyectos/GitHub/lca-deployment/python/m5/l2): Autenticación básica y ejercicio sobre por qué AuthN ≠ AuthZ.
- [`python/m5/l3a/`](file:///home/juansebas7ian/Proyectos/GitHub/lca-deployment/python/m5/l3a), [`l3b`](file:///home/juansebas7ian/Proyectos/GitHub/lca-deployment/python/m5/l3b), [`l3c`](file:///home/juansebas7ian/Proyectos/GitHub/lca-deployment/python/m5/l3c): Conversaciones privadas y aislamiento de recursos.
- [`python/m5/l4/`](file:///home/juansebas7ian/Proyectos/GitHub/lca-deployment/python/m5/l4): Integración con proveedores de identidad externos.
- [`python/m5/l5/`](file:///home/juansebas7ian/Proyectos/GitHub/lca-deployment/python/m5/l5): El agente tutor completo con autenticación integrada y modelo local Ollama.
