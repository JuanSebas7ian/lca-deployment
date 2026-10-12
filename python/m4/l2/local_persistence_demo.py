"""
m4 — Demostración Local de Persistencia (Módulo 4)
Demuestra los dos pilares de almacenamiento de LangGraph con el modelo local de Ollama:
1. El Checkpointer: Guarda el estado de ejecución paso a paso DENTRO de un thread (historial, variables de estado, mensajes).
2. El Store: Almacena memoria compartida a largo plazo ENTRE múltiples threads (perfiles de usuario, preferencias, documentos).
"""

import asyncio
import os
from dotenv import load_dotenv

load_dotenv(override=True)

from langchain_core.messages import HumanMessage, SystemMessage
from langchain_core.runnables import RunnableConfig
from langchain_ollama import ChatOllama
from langgraph.graph import END, START, MessagesState, StateGraph
from langgraph.checkpoint.memory import MemorySaver
from langgraph.store.memory import InMemoryStore
from langgraph.store.base import BaseStore

# Configuración del modelo
model_name = os.getenv("OLLAMA_MODEL", "gemma4:12b")
base_url = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
llm = ChatOllama(model=model_name, base_url=base_url)

# Función de nodo que interactúa con el Store y con el estado del Checkpointer
async def personalized_tutor_node(state: MessagesState, config: RunnableConfig, *, store: BaseStore):

    # Obtener el namespace del usuario desde la configuración
    user_id = config.get("configurable", {}).get("user_id", "default_user")
    namespace = ("users", user_id)

    # Leer datos del Store (memoria a largo plazo)
    user_profile = await store.aget(namespace, key="profile")
    profile_data = user_profile.value if user_profile else {}

    student_name = profile_data.get("name", "Estudiante")
    interests = profile_data.get("interests", "tecnología en general")

    system_instruction = (
        f"Eres un tutor de IA. El estudiante se llama {student_name} y sus intereses son: {interests}. "
        f"Adapta tus respuestas brevemente mencionando su contexto cuando sea oportuno."
    )

    messages = [SystemMessage(content=system_instruction)] + state["messages"]
    response = await llm.ainvoke(messages)
    return {"messages": [response]}

# Construir el grafo
workflow = StateGraph(MessagesState)
workflow.add_node("tutor", personalized_tutor_node)
workflow.add_edge(START, "tutor")
workflow.add_edge("tutor", END)

# Checkpointer (por thread) y Store (global / cross-thread)
checkpointer = MemorySaver()
store = InMemoryStore()

app = workflow.compile(checkpointer=checkpointer, store=store)

async def main():
    print("=" * 65)
    print(f"📦 Módulo 4: Checkpointer vs Store en Local con Ollama ({model_name})")
    print("=" * 65)

    # -----------------------------------------------------------------------
    # PASO 1: Guardar información persistente en el STORE (Cross-Thread)
    # -----------------------------------------------------------------------
    print("\n1️⃣  [STORE] Guardando perfil del usuario 'juan' en el namespace ('users', 'juan')...")
    await store.aput(
        namespace=("users", "juan"),
        key="profile",
        value={"name": "Juan Sebastián", "interests": "Machine Learning local y LangGraph", "nivel": "Avanzado"},
    )
    print("✅ Perfil guardado en el Store.")

    # -----------------------------------------------------------------------
    # PASO 2: Conversación en THREAD-A (El Checkpointer guarda este hilo)
    # -----------------------------------------------------------------------
    config_thread_a = {"configurable": {"thread_id": "thread-A", "user_id": "juan"}}
    print("\n2️⃣  [CHECKPOINTER - Thread A] Primer mensaje:")
    res_a1 = await app.ainvoke(
        {"messages": [HumanMessage(content="Hola, ¿me recuerdas en qué puedo enfocar mi estudio hoy?")]},
        config=config_thread_a,
    )
    print(f"🤖 Tutor: {res_a1['messages'][-1].content}\n")

    # -----------------------------------------------------------------------
    # PASO 3: Conversación en THREAD-B (Nuevo hilo, pero MISMO usuario)
    # -----------------------------------------------------------------------
    config_thread_b = {"configurable": {"thread_id": "thread-B", "user_id": "juan"}}
    print("3️⃣  [STORE en Thread B] Nuevo hilo 'thread-B', pero con el mismo 'user_id':")
    print("   (Demuestra cómo el Store persiste entre hilos distintos)")
    res_b1 = await app.ainvoke(
        {"messages": [HumanMessage(content="¿Cómo te presentarías ante mí en una línea?")]},
        config=config_thread_b,
    )
    print(f"🤖 Tutor: {res_b1['messages'][-1].content}\n")

    # -----------------------------------------------------------------------
    # PASO 4: Inspección de checkpoints del Checkpointer
    # -----------------------------------------------------------------------
    print("4️⃣  [CHECKPOINTER] Inspeccionando estado guardado en Thread A:")
    state_a = await app.aget_state(config_thread_a)
    print(f"   Mensajes guardados en el Checkpointer para Thread A: {len(state_a.values['messages'])}")
    for m in state_a.values["messages"]:
        print(f"   - [{m.__class__.__name__}]: {m.content[:70]}...")

    print("\n✅ Demostración del Módulo 4 completada con éxito.")

if __name__ == "__main__":
    asyncio.run(main())
