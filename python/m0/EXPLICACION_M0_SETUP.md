# Módulo 0 — Configuración del Entorno y Modelos Locales

Este módulo cubre la preparación de las herramientas necesarias para ejecutar el curso **LangSmith / LangGraph Deployment** de manera 100% local, utilizando **Ollama** y el gestor de paquetes ultra-rápido **`uv`**.

---

## 1. Herramientas del Entorno

### 1.1 Gestor de Paquetes: `uv`
En este proyecto usamos [`uv`](https://docs.astral.sh/uv/) en lugar de `pip` tradicional:
- Resuelve dependencias y entornos virtuales en milisegundos.
- Se asegura de que todas las versiones de `langgraph`, `langchain-ollama`, `deepagents` y `fastapi` coincidan según [`python/pyproject.toml`](file:///home/juansebas7ian/Proyectos/GitHub/lca-deployment/python/pyproject.toml).

Comando para sincronizar e instalar dependencias:
```bash
cd python
uv sync
```

---

## 2. Modelos Locales con Ollama

El proyecto ha sido adaptado para funcionar con modelos locales servidos mediante **Ollama** en `http://localhost:11434`.

### Modelos Disponibles en tu Máquina:
- **`gemma4:12b`** *(Configurado por defecto)*: Gran capacidad de razonamiento, context window de 256k, visión, soporte de thinking y tool calling estructurado nativo.
- **`embeddinggemma:latest`**: Modelo local de embeddings (307M params, dimensión 768) para indexación y búsqueda semántica.

Verificar que Ollama esté activo:
```bash
ollama list
```

---

## 3. Configuración de Variables de Entorno (`.env`)

El archivo [`.env`](file:///home/juansebas7ian/Proyectos/GitHub/lca-deployment/python/.env) dentro de `python/` contiene:

```bash
# LangSmith — tracing (opcional para ejecución puramente local)
LANGSMITH_API_KEY=lsv2_...
LANGSMITH_PROJECT=lca-deployment
DEEP_TUTOR_API_KEY=${LANGSMITH_API_KEY}

# Configuración del Proveedor de Modelos
MODEL_PROVIDER=ollama
OLLAMA_MODEL=gemma4:12b
OLLAMA_BASE_URL=http://localhost:11434
```

> 🦙 **Nota sobre modelos:** Por defecto todo el proyecto funciona 100% con **Ollama** (`gemma4:12b`) sin costo ni necesidad de credenciales de OpenAI o Anthropic. Solo si tú decides explícitamente en el futuro conectar APIs en la nube, podrías cambiar `MODEL_PROVIDER=openai` (o `anthropic` / `google_genai`) y añadir la API key respectiva.

---

## 4. Verificación del Setup

Para verificar que tu entorno y el modelo local responden correctamente, ejecuta desde la carpeta `python/`:

```bash
uv run python -c "from langchain_ollama import ChatOllama; llm = ChatOllama(model='gemma4:12b'); print(llm.invoke('Hola, confirma que el setup está listo').content)"
```
