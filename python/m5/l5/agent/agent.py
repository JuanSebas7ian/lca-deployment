"""
Deep Tutor Agent

Tutor agent using create_deep_agent with FilesystemBackend.

Personality and teaching guidelines are loaded from AGENTS.md via MemoryMiddleware.
Module skills are loaded from /skills/ via SkillsMiddleware (progressive disclosure).
The dynamic prompt injects per-session context: student name, module, and goals.

Assistant context (set per assistant in LangSmith):
- module_id:       which module to load (e.g. "module-1")
- store_namespace: student's Store namespace (derived from email, e.g. "jane@example_com")
"""

import asyncio
from dataclasses import dataclass
from pathlib import Path

from deepagents import create_deep_agent
from deepagents.backends.filesystem import FilesystemBackend
from deepagents.middleware.permissions import FilesystemPermission
from langchain.agents.middleware import ModelRequest, dynamic_prompt
from langchain.chat_models import init_chat_model
from langchain_mcp_adapters.client import MultiServerMCPClient

import os
from dotenv import load_dotenv

# Ensure environment variables are loaded
load_dotenv(override=True)

# ---------------------------------------------------------------------------
# Model configuration
# ---------------------------------------------------------------------------
def get_model():
    """Returns the chat model configured via environment variables."""
    provider = os.getenv("MODEL_PROVIDER", "ollama").lower()
    if provider == "ollama":
        from langchain_ollama import ChatOllama
        model_name = os.getenv("OLLAMA_MODEL", "gemma4:12b")
        base_url = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
        return ChatOllama(model=model_name, base_url=base_url)
    elif provider == "anthropic":
        return init_chat_model(os.getenv("ANTHROPIC_MODEL", "anthropic:claude-sonnet-4-6"))
    elif provider == "openai":
        return init_chat_model(os.getenv("OPENAI_MODEL", "openai:gpt-4o"))
    elif provider in ("google", "google_genai"):
        return init_chat_model(os.getenv("GOOGLE_MODEL", "google_genai:gemini-2.5-flash"))
    else:
        return init_chat_model(provider)

model = get_model()


# ---------------------------------------------------------------------------
# Context schema
# ---------------------------------------------------------------------------
@dataclass
class ContextSchema:
    module_id: str = "module-1"
    store_namespace: str = ""  # derived from student email


# ---------------------------------------------------------------------------
# Dynamic system prompt
# ---------------------------------------------------------------------------
@dynamic_prompt
async def tutor_prompt(request: ModelRequest) -> str:
    ctx = request.runtime.context
    module_id = getattr(ctx, "module_id", "module-1") if ctx else "module-1"
    store_namespace = getattr(ctx, "store_namespace", "") if ctx else ""
    student_name = "Student"
    goals = ""

    if store_namespace and request.runtime.store:
        item = await request.runtime.store.aget((store_namespace,), key="profile")
        if item is not None:
            profile = item.value
            student_name = f"{profile.get('first_name', '')} {profile.get('last_name', '')}".strip() or "Student"
            goals = profile.get("goals", "")

    goals_line = f"\n\nThe student's goals: {goals}" if goals else ""
    return (
        f"Your student's name is {student_name}. "
        f"They are working on {module_id}.{goals_line}\n\n"
        f"On your first response, read /skills/{module_id}/SKILL.md. "
        f"That file contains your teaching instructions — follow them. "
        f"When you need to answer a factual question, read /skills/{module_id}/information.md."
    )


# ---------------------------------------------------------------------------
# MCP tools
# ---------------------------------------------------------------------------
mcp_tools = []
try:
    _mcp_client = MultiServerMCPClient({
        "docs": {
            "url": "https://docs.langchain.com/mcp",
            "transport": "http",
        }
    })
    try:
        loop = asyncio.get_running_loop()
    except RuntimeError:
        loop = None

    if loop is None:
        mcp_tools = asyncio.run(_mcp_client.get_tools())
    else:
        import concurrent.futures
        with concurrent.futures.ThreadPoolExecutor() as pool:
            mcp_tools = pool.submit(asyncio.run, _mcp_client.get_tools()).result(timeout=10)
except Exception:
    mcp_tools = []




# ---------------------------------------------------------------------------
# Agent
# ---------------------------------------------------------------------------
backend = FilesystemBackend(
    root_dir=Path(__file__).parent.parent,
    virtual_mode=True,
)

graph = create_deep_agent(
    model=model,
    tools=[*mcp_tools],
    middleware=[tutor_prompt],
    backend=backend,
    memory=["/AGENTS.md"],
    skills=["/skills/"],
    permissions=[
        FilesystemPermission(operations=["write"], paths=["/skills/**"], mode="deny"),
    ],
    context_schema=ContextSchema,
)
