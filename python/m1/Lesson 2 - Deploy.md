---
title: "Lesson 2 - Deploy (Despliegue del Agente)"
source: "https://academy.langchain.com/courses/take/langsmith-deployment/multimedia/74150872-lesson-2-deploy"
author: "LangChain Academy"
created: 2026-10-09
description: "Módulo 1: Lección 2 - Despliegue del Agente (Deploying the Agent) - LangChain Academy"
tags:
  - "clippings"
  - "langgraph"
  - "deployment"
  - "ollama"
---

# Lección 2: Despliegue del Agente (`langgraph deploy`)

Esta lección cubre el proceso de empaquetado y despliegue de un agente construido con LangGraph, utilizando el archivo de configuración manifiesto **`langgraph.json`**, la herramienta de línea de comandos **`langgraph-cli`** y la plataforma **LangSmith Deployments**.

---

## 1. ¿Qué hace `langgraph deploy`?

El comando `langgraph deploy` construye un contenedor **Docker** y lo despliega (localmente o en la nube de LangSmith). 

Dentro de ese contenedor se empaquetan tres elementos esenciales:
1. **Tu Código**: El grafo del agente (`agent.py:graph`) y la aplicación web complementaria (`app.py:app`).
2. **Tus Dependencias**: Las librerías de Python requeridas (`langgraph`, `langchain-ollama`, etc.).
3. **El Entorno de Ejecución**: Variables de entorno, secretos y configuración de red.

Todo esto está orquestado por un único archivo de configuración: **`langgraph.json`**.

---

## 2. El Manifiesto de Despliegue: `langgraph.json`

El archivo `langgraph.json` vive en la raíz del proyecto del agente (por ejemplo, en [`python/deep_tutor/langgraph.json`](file:///home/juansebas7ian/Proyectos/GitHub/lca-deployment/python/deep_tutor/langgraph.json)):

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

### Desglose de Parámetros:

- **`graphs` (El Código del Agente)**:
  - Mapea un identificador (`"tutor"`) a la ruta del archivo y la variable exportada (`"./agent/agent.py:graph"`).
  - El nombre `"tutor"` es el `graph_id` visible en LangSmith y la API de LangGraph.
- **`http.app` (Rutas Personalizadas con FastAPI)**:
  - Apunta a una aplicación FastAPI (`app.py:app`) servida en el mismo puerto que la API del agente.
  - Esto permite desplegar tanto la interfaz web (UI) como el backend del agente en un único servicio, sin necesidad de un servidor separado.
- **`dependencies` (Dependencias)**:
  - Apunta al directorio que contiene el archivo de paquetes (`pyproject.toml`).
  - Al indicar `["."]`, LangGraph empaqueta únicamente las dependencias necesarias para producción de ese agente específico, separándolas de las dependencias de desarrollo local del repositorio principal.
- **`env` (Variables de Entorno)**:
  - Ruta relativa al archivo de variables de entorno (`"../.env"`).
  - En desarrollo local (`langgraph dev`), carga todas las variables en el proceso.
  - En despliegue en la nube (`langgraph deploy`), LangSmith sube las variables excepto las **variables reservadas** (`LANGSMITH_API_KEY`, `LANGSMITH_PROJECT`), las cuales LangSmith gestiona automáticamente.

---

## 3. Claves y la Solución para `DEEP_TUTOR_API_KEY`

El servidor web del Deep Tutor corre dentro del mismo contenedor y hace peticiones al SDK de LangGraph para crear hilos (`threads`), guardar en el `Store` y recibir streaming.

Esa llamada hacia el propio servidor requiere autenticación:
- LangSmith reserva y descarta la variable `LANGSMITH_API_KEY` durante el despliegue a la nube.
- Para solucionar esto, en el archivo [`.env`](file:///home/juansebas7ian/Proyectos/GitHub/lca-deployment/python/.env) creamos un alias no reservado:
  ```bash
  LANGSMITH_API_KEY=lsv2_pt_...
  DEEP_TUTOR_API_KEY=${LANGSMITH_API_KEY}
  ```
- La CLI de LangGraph expande `${LANGSMITH_API_KEY}` en tiempo de lectura, subiendo `DEEP_TUTOR_API_KEY` sin que sea filtrada.

> 🦙 **Nota de Modelos Locales (Ollama):** Para la ejecución del LLM, el archivo `.env` está configurado con:
> ```bash
> MODEL_PROVIDER=ollama
> OLLAMA_MODEL=qwen2.5:7b
> OLLAMA_BASE_URL=http://localhost:11434
> ```
> De este modo, los agentes no requieren claves de OpenAI ni incurren en costos.

---

## 4. Esquema Completo de `langgraph.json`

`langgraph.json` soporta configuración avanzada para infraestructura de producción:

| Sección | Parámetros Clave | Descripción |
| :--- | :--- | :--- |
| **🐳 Docker** | `base_image`, `image_distro`, `python_version`, `pip_installer`, `dockerfile_lines` | Control fino de la imagen base (Debian/Wolfi), versión de Python (3.11–3.13) e instalador (`uv` o `pip`). |
| **🤖 Graphs** | `graphs` | Diccionario de grafos expuestos (`"id": "ruta.py:grafo"`). |
| **💾 Checkpointer**| `checkpointer.backend`, `checkpointer.ttl` | Configuración del backend (`postgres`, `mongo`, o `custom`) y políticas de tiempo de vida (TTL). |
| **🗄️ Store** | `store.index.embed`, `store.index.dims`, `store.ttl` | Configuración de búsqueda semántica con embeddings y expiración de memoria a largo plazo. |
| **🌐 API Server** | `http.app`, `http.cors`, `auth`, `webhooks`, `http.disable_*` | Handlers de autenticación (`auth.py:auth`), políticas CORS, webhooks de salida y desactivación de endpoints no utilizados. |

---

## 5. Ejecución Local: `langgraph dev`

Antes de desplegar en producción, se prueba localmente con:

```bash
cd python/deep_tutor
uv run langgraph dev
```

### Lo que levanta este comando:
1. **API Server**: En `http://localhost:2024`.
2. **Interfaz de Documentación**: Swagger / OpenAPI en `http://localhost:2024/docs`.
3. **LangGraph Studio**: `https://smith.langchain.com/studio?baseUrl=http://localhost:2024` para depuración visual del grafo e inspección del estado de los nodos.
4. **UI del Tutor**: En `http://localhost:2024/` gracias a la ruta FastAPI montada en `http.app`.

---

## 6. Despliegue en Producción: `langgraph deploy`

Una vez verificado el funcionamiento en local:

```bash
cd python/deep_tutor
uv run langgraph deploy
```

### Flujo de Ejecución de `langgraph deploy`:
1. **Autenticación**: Valida tu `LANGSMITH_API_KEY`.
2. **Filtrado de variables**: Omite variables reservadas del sistema y empaqueta las demás.
3. **Compilación de Contenedor**: Construye la imagen Docker en local (o solicita un remote build si Docker no está corriendo).
4. **Subida y Aprovisionamiento**: Sube el archivo comprimido a LangSmith Cloud y provisiona el microservicio.
5. **URL Pública**: Devuelve una URL segura (`https://tutor-<hash>.us.langgraph.app`).

---

## 7. Panel de "Deployments" en LangSmith

En la interfaz web de LangSmith, bajo la pestaña **Deployments**:
- **Indicador de Estado**: Semáforo verde cuando el contenedor está en ejecución y saludable.
- **Studio en la Nube**: Permite ejecutar pruebas y crear hilos directamente contra el contenedor en vivo.
- **Gestión de Revisiones y Variables**: Permite añadir, editar o rotar variables de entorno sin reconstruir el código manualmente.

---

## 8. Resumen de la Lección

1. `langgraph.json` es el **manifiesto único** que define código (`graphs`), dependencias (`dependencies`), servidor web (`http.app`) y entorno (`env`).
2. Se usa `langgraph dev` para pruebas locales con hot-reload y LangGraph Studio.
3. `langgraph deploy` compila la imagen de Docker y gestiona el despliegue en la infraestructura gestionada de LangSmith.
4. El alias `DEEP_TUTOR_API_KEY` permite al frontend interno interactuar con la propia API del agente sin sufrir el filtrado de variables reservadas.
