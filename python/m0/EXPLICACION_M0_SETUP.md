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
- **`qwen2.5:7b`** *(Recomendado y configurado por defecto)*: Excelente soporte para llamadas a herramientas (Tool Calling estructurado), respuestas en español fluidas y bajo consumo de memoria.
- **`gemma4:12b`**: Gran capacidad de razonamiento y soporte nativo de function calling.
- **`qwen2.5-coder-32b-iq4:latest`**: Modelo grande especializado en código.
- **`qwen2.5-coder:7b`**: Modelo ligero para tareas de programación.

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
OLLAMA_MODEL=qwen2.5:7b
OLLAMA_BASE_URL=http://localhost:11434
```

> 🦙 **Nota sobre modelos:** Por defecto todo el proyecto funciona 100% con **Ollama** (`qwen2.5:7b`) sin costo ni necesidad de credenciales de OpenAI o Anthropic. Solo si tú decides explícitamente en el futuro conectar APIs en la nube, podrías cambiar `MODEL_PROVIDER=openai` (o `anthropic` / `google_genai`) y añadir la API key respectiva.

---

## 4. Verificación del Setup

Para verificar que tu entorno y el modelo local responden correctamente, ejecuta desde la carpeta `python/`:

```bash
uv run python -c "from langchain_ollama import ChatOllama; llm = ChatOllama(model='qwen2.5:7b'); print(llm.invoke('Hola, confirma que el setup está listo').content)"
```
