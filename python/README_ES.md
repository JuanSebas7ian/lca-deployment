# Curso de Despliegue de LangSmith & LangGraph — Guía en Español

Bienvenido al repositorio del curso **LangSmith Deployment / LangGraph Deployment** adaptado para ejecutarse **100% en local con modelos de Ollama** (`qwen2.5:7b`).

> 🦙 **Nota Importante sobre Modelos:** Todo este repositorio ha sido adaptado para funcionar con **Ollama** de forma local. **NO necesitas cuenta ni API keys de pago de OpenAI (`OPENAI_API_KEY`) ni de Anthropic**. Los agentes, los grafos y las pruebas se ejecutan directamente contra tu servidor de Ollama (`http://localhost:11434`).

---

## 🚀 Resumen de Adaptaciones Realizadas

1. **Soporte Nativo de Modelos Locales (Ollama en vez de OpenAI / Anthropic)**:
   - Configurado en [`python/.env`](file:///home/juansebas7ian/Proyectos/GitHub/lca-deployment/python/.env) con `MODEL_PROVIDER=ollama`, `OLLAMA_MODEL=qwen2.5:7b` y `OLLAMA_BASE_URL=http://localhost:11434`.
   - Compatibilidad total con los modelos disponibles en tu equipo (`qwen2.5:7b`, `gemma4:12b`, `qwen2.5-coder-32b-iq4:latest`, `qwen2.5-coder:7b`).
   - Se seleccionó `qwen2.5:7b` por su óptimo rendimiento en llamadas a funciones estructuradas (tool calling), velocidad y bajo consumo de memoria.
2. **Código de Agentes Adaptado**:
   - [`python/deep_tutor/agent/agent.py`](file:///home/juansebas7ian/Proyectos/GitHub/lca-deployment/python/deep_tutor/agent/agent.py): Agente central adaptado para instanciar dinámicamente Ollama (`ChatOllama`), con manejo seguro de contexto y tolerancia ante fallos de conexión externa de herramientas MCP.
   - [`python/m5/l5/agent/agent.py`](file:///home/juansebas7ian/Proyectos/GitHub/lca-deployment/python/m5/l5/agent/agent.py): Tutor protegido con autenticación adaptado para Ollama.
   - [`python/m6/dacli_tutor/deepagents.toml`](file:///home/juansebas7ian/Proyectos/GitHub/lca-deployment/python/m6/dacli_tutor/deepagents.toml): Configuración de Deep Agents CLI apuntando a `ollama:qwen2.5:7b`.
3. **Agentes y Scripts de Demostración Locales Creados**:
   - [`python/m2/local_m2_agent.py`](file:///home/juansebas7ian/Proyectos/GitHub/lca-deployment/python/m2/local_m2_agent.py): Demuestra ciclos de vida, hilos independientes y streaming con Ollama.
   - [`python/m4/l2/local_persistence_demo.py`](file:///home/juansebas7ian/Proyectos/GitHub/lca-deployment/python/m4/l2/local_persistence_demo.py): Demuestra el Checkpointer y el Store a largo plazo con Ollama.
   - [`python/m5/local_auth_demo.py`](file:///home/juansebas7ian/Proyectos/GitHub/lca-deployment/python/m5/local_auth_demo.py): Demuestra el pipeline de autenticación Bearer y autorización por roles con Ollama.
4. **Documentación Completa en Español de Cada Módulo**:
   - Cada módulo cuenta con su propio `.md` explicativo con teoría, arquitectura y comandos paso a paso.
   - Suite de validación automatizada en [`python/validate_local_setup.py`](file:///home/juansebas7ian/Proyectos/GitHub/lca-deployment/python/validate_local_setup.py).

---

## 📚 Índice de Módulos del Curso

| Módulo | Título | Documentación Detallada |
| :--- | :--- | :--- |
| **M0** | **Setup y Configuración** | [EXPLICACION_M0_SETUP.md](file:///home/juansebas7ian/Proyectos/GitHub/lca-deployment/python/m0/EXPLICACION_M0_SETUP.md) |
| **M1** | **Arquitectura de Despliegue** | [EXPLICACION_M1_ARQUITECTURA.md](file:///home/juansebas7ian/Proyectos/GitHub/lca-deployment/python/m1/EXPLICACION_M1_ARQUITECTURA.md) |
| **M2** | **LangGraph SDK y Rutas** | [EXPLICACION_M2_SDK_Y_RUTAS.md](file:///home/juansebas7ian/Proyectos/GitHub/lca-deployment/python/m2/EXPLICACION_M2_SDK_Y_RUTAS.md) |
| **M3** | **Despliegue con CLI y Cloud** | [EXPLICACION_M3_DESPLIEGUE.md](file:///home/juansebas7ian/Proyectos/GitHub/lca-deployment/python/m3/EXPLICACION_M3_DESPLIEGUE.md) |
| **M4** | **Persistencia: Checkpointer vs Store** | [EXPLICACION_M4_PERSISTENCIA.md](file:///home/juansebas7ian/Proyectos/GitHub/lca-deployment/python/m4/EXPLICACION_M4_PERSISTENCIA.md) |
| **M5** | **Autenticación y Handlers** | [EXPLICACION_M5_AUTENTICACION.md](file:///home/juansebas7ian/Proyectos/GitHub/lca-deployment/python/m5/EXPLICACION_M5_AUTENTICACION.md) |
| **M6** | **Deep Agents CLI (dacli)** | [EXPLICACION_M6_DEEP_AGENTS.md](file:///home/juansebas7ian/Proyectos/GitHub/lca-deployment/python/m6/EXPLICACION_M6_DEEP_AGENTS.md) |
| **App**| **Deep Tutor (Agente Principal)** | [EXPLICACION_DEEP_TUTOR.md](file:///home/juansebas7ian/Proyectos/GitHub/lca-deployment/python/deep_tutor/EXPLICACION_DEEP_TUTOR.md) |

---

## ⚡ Guía de Inicio Rápido

### 1. Verificar Entorno
```bash
cd python
uv sync
```

### 2. Probar el Agente Principal (Deep Tutor)
```bash
uv run python -c "
import asyncio, sys
sys.path.insert(0, 'deep_tutor')
from agent.agent import graph

async def test():
    res = await graph.ainvoke({'messages': [{'role': 'user', 'content': 'Hola tutor, ¿qué es LangGraph?'}]})
    print(res['messages'][-1].content)

asyncio.run(test())
"
```

### 3. Ejecutar las Demostraciones de los Módulos
```bash
# Demostración del Módulo 2 (Threads y Streaming)
uv run python m2/local_m2_agent.py

# Demostración del Módulo 4 (Checkpointer y Store)
uv run python m4/l2/local_persistence_demo.py

# Demostración del Módulo 5 (Autenticación y Autorización)
uv run python m5/local_auth_demo.py

# Demostración del Módulo 6 (Deep Agents CLI)
cd m6/dacli_tutor
uv run deepagents -n "Resume las responsabilidades del tutor"
```
