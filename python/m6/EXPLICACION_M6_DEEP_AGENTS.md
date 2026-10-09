# Módulo 6 — Deep Agents y el CLI de Deep Agents (dacli)

En este módulo se introduce la arquitectura de **Deep Agents** y la herramienta de línea de comandos **`deepagents`** (anteriormente conocida como `dacli`). Esta arquitectura permite construir agentes con capacidades avanzadas de autonomía, habilidades modulares (skills) y memoria persistente basada en sistemas de archivos.

---

## 1. ¿Qué es un Deep Agent?

Un Deep Agent no es un simple chatbot de un solo turno; es un agente autónomo de múltiples pasos que opera con:

1. **Memoria Declarativa (`AGENTS.md`)**: Define las directrices de personalidad, restricciones operativas y reglas pedagógicas que el modelo lee al inicio.
2. **Habilidades Progresivas (Progressive Disclosure Skills)**: Cada habilidad reside en una carpeta (`/skills/<nombre_skill>/`) con su `SKILL.md`. El agente solo lee la documentación detallada cuando la tarea específica lo requiere, ahorrando tokens en la ventana de contexto.
3. **Backend de Sistema de Archivos (`FilesystemBackend`)**: Permite al agente interactuar con archivos virtuales o reales con permisos controlados (por ejemplo, modo de solo lectura sobre las habilidades mediante `FilesystemPermission`).
4. **Herramientas de Búsqueda y MCP**: Integración con servidores MCP para consultar documentación oficial o herramientas externas.

---

## 2. Configuración: `deepagents.toml`

La configuración del agente CLI se define en [`deepagents.toml`](file:///home/juansebas7ian/Proyectos/GitHub/lca-deployment/python/m6/dacli_tutor/deepagents.toml):

```toml
[agent]
name = "deep_tutor"
model = "ollama:qwen2.5:7b"

[auth]
provider = "anonymous"

[frontend]
enabled = true
app_name = "LangChain Tutor"

[memories]
backend = "store"
```

El proyecto ya está configurado para utilizar el modelo local **`ollama:qwen2.5:7b`**.

---

## 3. Uso del CLI `deepagents` con Modelos Locales

El CLI `deepagents` viene instalado en el entorno virtual de Python.

### 3.1 Ejecución Interactiva (Modo Chat en Terminal):
```bash
cd python/m6/dacli_tutor
uv run deepagents
```

### 3.2 Tarea No Interactiva (One-Shot):
```bash
cd python/m6/dacli_tutor
uv run deepagents -n "Hola tutor, resume en dos puntos qué aprenderemos en este módulo"
```

### 3.3 Configuración de Modelo por Defecto:
Ya hemos dejado configurado el modelo por defecto en el CLI para que utilice Ollama:
```bash
uv run deepagents --default-model ollama:qwen2.5:7b
```

---

## 4. Frontend Personalizado (Bring Your Own UI)

El módulo incluye un servidor web en [`python/m6/ui/app.py`](file:///home/juansebas7ian/Proyectos/GitHub/lca-deployment/python/m6/ui/app.py) que se conecta mediante el SDK de LangGraph al agente de Deep Agents.

Para iniciarlo:
```bash
cd python
uv run uvicorn m6.ui.app:app --reload --port 8000
```
La interfaz web proporciona:
- Panel de chat en tiempo real.
- Selector de módulos y lecciones.
- Inspección de los eventos y herramientas invocadas por el agente.
