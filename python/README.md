# LangSmith Deployment — Python (Local Ollama Edition)

You can find the original course at [LangSmith Deployments](https://academy.langchain.com/courses/take/langsmith-deployments).

> 🇪🇸 **Guía en Español**: Consulta [`README_ES.md`](README_ES.md) para documentación detallada en español y explicaciones paso a paso de cada módulo (M0 a M6).

---

## 🦙 Local Ollama Architecture

This repository has been adapted to run **100% locally using Ollama** instead of requiring paid cloud APIs (OpenAI or Anthropic).

- **Default Local Model**: `gemma4:12b` (via `http://localhost:11434`)
- **Local Embedding Model**: `embeddinggemma:latest`
- **Zero Paid Cloud API Requirement**: You do **not** need an `OPENAI_API_KEY` or `ANTHROPIC_API_KEY` to run the agents, demos, or tests locally.

---

## Setup

### Prerequisites

- **Ollama**: Installed and running locally (`curl -fsSL https://ollama.com/install.sh | sh` or desktop app).
  - Verify your local model:
    ```bash
    ollama list
    ```
- **Python**: 3.11–3.13
- **uv package manager**: See [Installing uv](#installing-uv)
- **Docker** (optional, recommended): For running `langgraph dev` or full multi-container deployment (`langgraph up`).
- **LangSmith account** (optional for local execution): Only needed if you want cloud tracing or deploying to LangSmith Cloud.

### Installation

1. Move to the `python` directory:

```bash
cd python
```

2. Configure environment variables:

```bash
cp .env.example .env
```

Your `.env` is pre-configured for **Ollama**:

```bash
# Model provider configuration (Default: local Ollama)
MODEL_PROVIDER=ollama
OLLAMA_MODEL=gemma4:12b
OLLAMA_BASE_URL=http://localhost:11434

# LangSmith — tracing and deployment (Optional for local-only testing)
LANGSMITH_API_KEY=lsv2_...
LANGSMITH_PROJECT=lca-deployment
LANGSMITH_TRACING=true
DEEP_TUTOR_API_KEY=${LANGSMITH_API_KEY}
```

> 💡 **Note**: Cloud providers (OpenAI, Anthropic, Google GenAI) are supported as optional fallbacks by changing `MODEL_PROVIDER`, but are **not required**.

3. Install dependencies:

```bash
uv sync
```

4. Validate local setup and agents:

```bash
uv run python validate_local_setup.py
```

---

## Setup Your Coding Agent

Using a coding agent to build your agents is encouraged throughout this course. Two additions make it significantly more effective: the LangChain Docs MCP server and the LangSmith tracing plugin.

### LangChain Docs MCP Server

Adding the LangChain Docs MCP server gives your coding agent direct access to LangChain, LangGraph, and LangSmith documentation — including search and a loaded skill that covers core concepts. Add it once and it is available in all your projects.

[Full setup instructions](https://docs.langchain.com/use-these-docs#use-our-mcp-server)

### LangSmith Skills

LangSmith skills give your coding agent on-demand capabilities for querying traces, generating datasets, and defining evaluators — directly from within your agent session.

[Full setup instructions](https://docs.langchain.com/langsmith/skills)

---

## Getting Started with LangSmith

- Create a [LangSmith](https://smith.langchain.com/) account
- Create a LangSmith API key

<img width="600" alt="LangSmith API key - step 1" src="https://github.com/user-attachments/assets/e39b8364-c3e3-4c75-a287-d9d4685caad5" />
<img width="600" alt="LangSmith API key - step 2" src="https://github.com/user-attachments/assets/2e916b2d-e3b0-4c59-a178-c5818604b8fe" />

### Installing uv

See the [uv installation docs](https://docs.astral.sh/uv/getting-started/installation/) for full instructions. Common options:


```bash
# macOS / Linux
curl -LsSf https://astral.sh/uv/install.sh | sh

# macOS with Homebrew
brew install uv

# Windows
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
```
