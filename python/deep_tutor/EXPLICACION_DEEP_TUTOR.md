# Deep Tutor — El Agente Principal del Curso

El **Deep Tutor** es la aplicación integral construida a lo largo del curso. Es un agente pedagógico interactivo diseñado con la arquitectura **Deep Agent**, capaz de guiar al estudiante módulo por módulo, consultar la documentación de LangChain y persistir el progreso de cada estudiante.

---

## 1. Arquitectura de Componentes

```
python/deep_tutor/
├── agent/
│   ├── __init__.py
│   └── agent.py         # Definición del agente Deep Tutor con modelo Ollama
├── skills/              # Habilidades del tutor (revelación progresiva)
│   ├── module-1/        # Habilidad e información para el Módulo 1
│   ├── module-2/
│   ├── module-3/
│   ├── module-4/
│   ├── module-5/
│   └── module-6/
├── ui/
│   ├── app.py           # Servidor FastAPI con rutas personalizadas (/chat, /login, etc.)
│   ├── index.html       # Frontend web interactivo con diagramas y panel de chat
│   └── agent_client.py  # Cliente que conecta FastAPI con LangGraph SDK
├── langgraph.json       # Manifiesto de despliegue para LangGraph
└── AGENTS.md            # Reglas pedagógicas y personalidad del tutor
```

---

## 2. Adaptación a Modelos Locales (Ollama)

En [`agent/agent.py`](file:///home/juansebas7ian/Proyectos/GitHub/lca-deployment/python/deep_tutor/agent/agent.py):
- Se lee la variable `MODEL_PROVIDER` de [`.env`](file:///home/juansebas7ian/Proyectos/GitHub/lca-deployment/python/.env) (configurada en `ollama`).
- Se instancia automáticamente `ChatOllama(model="gemma4:12b")`.
- El prompt dinámico (`tutor_prompt`) inyecta de forma segura el contexto del módulo y del estudiante (manejando con seguridad entornos de prueba donde el contexto sea nulo).
- Las herramientas de documentación MCP cuentan con protección ante desconexiones de red, permitiendo que el tutor funcione de forma 100% offline.

---

## 3. Cómo Ejecutar el Tutor en Local

### Opción 1: Servidor Completo de LangGraph (`langgraph dev`)
```bash
cd python/deep_tutor
uv run langgraph dev
```
Esto iniciará:
- El servidor de LangGraph en `http://localhost:2024`.
- La interfaz web y rutas de FastAPI en el mismo puerto.
- Abre tu navegador en `http://localhost:2024` para interactuar con la interfaz del tutor.

### Opción 2: Prueba Rápida en Python desde Terminal
Puedes invocar el grafo directamente con un comando:
```bash
cd python
uv run python -c "
import asyncio, sys
sys.path.insert(0, 'deep_tutor')
from agent.agent import graph

async def chat():
    res = await graph.ainvoke({'messages': [{'role': 'user', 'content': 'Hola tutor, ¿qué aprenderemos en el curso?'}]})
    print(res['messages'][-1].content)

asyncio.run(chat())
"
```
