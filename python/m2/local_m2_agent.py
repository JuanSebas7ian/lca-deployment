"""
m2 — Agente Local Demostrativo (Módulo 2)
Demuestra el ciclo de vida de ejecución de LangGraph con el modelo local de Ollama:
1. Definición del grafo y estado
2. Invocación síncrona / asíncrona
3. Streaming de respuestas en tiempo real
4. Aislamiento por Threads de conversación
"""

import asyncio
import os
import sys
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv(override=True)

from langchain_core.messages import HumanMessage, SystemMessage
from langchain_ollama import ChatOllama
from langgraph.graph import END, START, MessagesState, StateGraph
from langgraph.checkpoint.memory import MemorySaver

# Configurar modelo local Ollama
model_name = os.getenv("OLLAMA_MODEL", "qwen2.5:7b")
base_url = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
llm = ChatOllama(model=model_name, base_url=base_url)

# Nodo principal del agente
async def chatbot_node(state: MessagesState):
    response = await llm.ainvoke(state["messages"])
    return {"messages": [response]}

# Construir el grafo
workflow = StateGraph(MessagesState)
workflow.add_node("chatbot", chatbot_node)
workflow.add_edge(START, "chatbot")
workflow.add_edge("chatbot", END)

# Checkpointer en memoria para manejar hilos (threads)
checkpointer = MemorySaver()
app = workflow.compile(checkpointer=checkpointer)

async def main():
    print("=" * 60)
    print(f"🚀 Módulo 2: Ejecutando Agente Local con Ollama ({model_name})")
    print("=" * 60)

    # 1. Hilo 1: Conversación inicial
    thread_1_config = {"configurable": {"thread_id": "thread-1"}}
    print("\n👉 [Thread 1] Mensaje 1: 'Hola, mi nombre es Sebastián y soy dev de IA.'")
    res1 = await app.ainvoke(
        {"messages": [HumanMessage(content="Hola, mi nombre es Sebastián y soy dev de IA.")]},
        config=thread_1_config,
    )
    print(f"🤖 Agente: {res1['messages'][-1].content}\n")

    # 2. Hilo 1: Memoria dentro del mismo hilo
    print("👉 [Thread 1] Mensaje 2: '¿Recuerdas cuál es mi nombre y mi profesión?'")
    res2 = await app.ainvoke(
        {"messages": [HumanMessage(content="¿Recuerdas cuál es mi nombre y mi profesión?")]},
        config=thread_1_config,
    )
    print(f"🤖 Agente: {res2['messages'][-1].content}\n")

    # 3. Hilo 2: Demostración de aislamiento (no debe saber quién es Sebastián)
    thread_2_config = {"configurable": {"thread_id": "thread-2"}}
    print("👉 [Thread 2 (Aislado)] Mensaje 1: '¿Cuál es mi nombre?'")
    res3 = await app.ainvoke(
        {"messages": [HumanMessage(content="¿Cuál es mi nombre?")]},
        config=thread_2_config,
    )
    print(f"🤖 Agente: {res3['messages'][-1].content}\n")

    # 4. Demostración de Streaming
    print("👉 [Thread 1] Streaming en tiempo real: 'Explica en 2 líneas qué es un Thread en LangGraph.'")
    print("🤖 Agente (Stream): ", end="", flush=True)
    async for chunk, _metadata in app.astream(
        {"messages": [HumanMessage(content="Explica en 2 líneas qué es un Thread en LangGraph.")]},
        config=thread_1_config,
        stream_mode="messages",
    ):
        if chunk.content:
            print(chunk.content, end="", flush=True)
    print("\n\n✅ Demostración del Módulo 2 completada con éxito.")

if __name__ == "__main__":
    asyncio.run(main())
