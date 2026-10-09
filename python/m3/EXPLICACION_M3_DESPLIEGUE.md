# Módulo 3 — Despliegue con LangGraph CLI y Cloud

Este módulo aborda el ciclo de vida de empaquetado y despliegue de grafos usando el **LangGraph CLI**, tanto en modo desarrollo local como en entornos de nube (LangGraph Cloud / LangSmith Deployments).

---

## 1. El LangGraph CLI

El CLI de LangGraph (`langgraph-cli`) es la herramienta para compilar, probar y desplegar tus grafos.

### Comandos Principales:

### 1.1 `langgraph dev` (Desarrollo Local Inmediato)
Inicia un servidor local de desarrollo con recarga en caliente (hot reload).
```bash
# Dentro de una carpeta con langgraph.json (por ejemplo, python/deep_tutor):
uv run langgraph dev
```
- Por defecto corre en `http://localhost:2024`.
- Levanta el endpoint de salud `/ok` y la API de LangGraph.
- Se integra automáticamente con LangGraph Studio para depurar visualmente los grafos en el navegador.

### 1.2 `langgraph up` (Entorno Local Completo)
Levanta la infraestructura completa mediante Docker Compose (API Server + Redis + Postgres):
```bash
uv run langgraph up
```
- Es la simulación más fiel a la arquitectura de producción en la nube.
- Persiste los checkpoints y el store en una base de datos Postgres real local.

### 1.3 `langgraph build` (Creación de Imágenes Docker)
Construye una imagen de contenedor compatible con OCI:
```bash
uv run langgraph build -t mi-agente:latest
```
Genera la imagen lista para ser ejecutada en Kubernetes, AWS ECS, Google Cloud Run o cualquier orquestador.

### 1.4 `langgraph deploy` (Despliegue en la Nube de LangSmith)
Despliega directamente a la infraestructura administrada de LangGraph Cloud:
```bash
uv run langgraph deploy
```
Requiere una cuenta de LangSmith con un plan que soporte despliegues.

---

## 2. Consideraciones al Usar Modelos Locales (Ollama)

Cuando ejecutas un agente con Ollama dentro de un contenedor Docker o a través de `langgraph dev`:
- **Desde la máquina host (`langgraph dev`)**: El agente se comunica directamente con `http://localhost:11434`.
- **Desde un contenedor Docker**: Dentro de Docker, `localhost` apunta al contenedor, no a tu máquina host. Para comunicarte con Ollama en Linux/Docker, debes apuntar a `http://host.docker.internal:11434` o `http://172.17.0.1:11434` (la IP del puente docker0).
- Asegúrate de que Ollama permita conexiones configurando la variable `OLLAMA_HOST=0.0.0.0:11434` si es necesario.

---

## 3. Variables de Entorno y Secretos

El archivo `langgraph.json` referencia el archivo `.env`:
```json
{
  "env": "../.env"
}
```
Reglas importantes:
- Nunca comitear claves reales al repositorio Git.
- `LANGSMITH_API_KEY` se utiliza para habilitar el trazado (tracing) y la observabilidad en la plataforma LangSmith.
- Si solo estás probando en local con Ollama, el agente puede funcionar perfectamente sin conexión a internet ni claves de pago.
