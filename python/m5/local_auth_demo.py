"""
m5 — Demostración Local de Autenticación y Autorización (Módulo 5)
Demuestra cómo funciona el sistema de autenticación y autorización de LangGraph:
1. Validación de Bearer Tokens (@auth.authenticate)
2. Inyección de identidad en el grafo (langgraph_auth_user)
3. Reglas de autorización (@auth.on) para impedir accesos cruzados no autorizados entre usuarios
4. Generación de respuestas personalizadas por rol/usuario con el modelo local Ollama
"""

import asyncio
import os
from dotenv import load_dotenv

load_dotenv(override=True)

from langchain_core.messages import AIMessage, HumanMessage
from langchain_core.runnables import RunnableConfig
from langchain_ollama import ChatOllama
from langgraph.graph import END, START, MessagesState, StateGraph
from langgraph.checkpoint.memory import MemorySaver

# Modelo local
model_name = os.getenv("OLLAMA_MODEL", "gemma4:12b")
base_url = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
llm = ChatOllama(model=model_name, base_url=base_url)

# Base de datos simulada de usuarios y tokens
USERS_DB = {
    "alice-token": {"id": "user_alice", "name": "Alice", "role": "admin"},
    "bob-token":   {"id": "user_bob",   "name": "Bob",   "role": "student"},
}

# 1. Simulación del Handler de Autenticación (@auth.authenticate)
def authenticate_token(bearer_header: str | None) -> dict:
    if not bearer_header or not bearer_header.startswith("Bearer "):
        raise PermissionError("401: Token Bearer ausente o con formato incorrecto")
    token = bearer_header.split(" ", 1)[1]
    if token not in USERS_DB:
        raise PermissionError("401: Token no válido")
    return USERS_DB[token]

# 2. Simulación de Control de Acceso por Hilo / Autorización (@auth.on)
class ThreadAccessManager:
    def __init__(self):
        # Mapea thread_id -> owner_user_id
        self.thread_owners = {}

    def create_thread(self, thread_id: str, user: dict):
        self.thread_owners[thread_id] = user["id"]
        return {"thread_id": thread_id, "owner": user["name"]}

    def verify_read_access(self, thread_id: str, user: dict):
        owner_id = self.thread_owners.get(thread_id)
        # Los admins pueden ver todo, los usuarios normales solo sus propios hilos
        if user["role"] == "admin" or owner_id == user["id"]:
            return True
        raise PermissionError(f"403 Prohibido: El usuario '{user['name']}' no tiene permiso para acceder al hilo de '{owner_id}'")

# 3. Grafo del Agente protegido
async def secure_chat_node(state: MessagesState, config: RunnableConfig) -> dict:
    # La identidad del usuario autenticado llega a través de configurable
    auth_user = config.get("configurable", {}).get("langgraph_auth_user", {})
    user_name = auth_user.get("name", "Invitado")
    role = auth_user.get("role", "usuario")

    prompt = [
        {"role": "system", "content": f"Eres un asistente seguro. El usuario actual es {user_name} (Rol: {role}). Salúdalo y responde brevemente."},
    ] + state["messages"]

    res = await llm.ainvoke(prompt)
    return {"messages": [res]}

workflow = StateGraph(MessagesState)
workflow.add_node("agent", secure_chat_node)
workflow.add_edge(START, "agent")
workflow.add_edge("agent", END)

checkpointer = MemorySaver()
app = workflow.compile(checkpointer=checkpointer)

async def main():
    print("=" * 65)
    print(f"🔒 Módulo 5: Autenticación & Autorización Local ({model_name})")
    print("=" * 65)

    access_mgr = ThreadAccessManager()

    # Paso 1: Autenticar a Alice y Bob
    alice = authenticate_token("Bearer alice-token")
    bob = authenticate_token("Bearer bob-token")
    print(f"✅ Autenticada: {alice['name']} (Rol: {alice['role']})")
    print(f"✅ Autenticado: {bob['name']} (Rol: {bob['role']})")

    # Paso 2: Alice crea su thread privado y conversa
    alice_thread = access_mgr.create_thread("thread-alice-secret", alice)
    print(f"\n📂 Alice crea hilo privado: {alice_thread['thread_id']}")

    config_alice = {
        "configurable": {
            "thread_id": alice_thread["thread_id"],
            "langgraph_auth_user": alice,
        }
    }
    res_alice = await app.ainvoke(
        {"messages": [HumanMessage(content="¿Tengo acceso a la consola de administración?")]},
        config=config_alice,
    )
    print(f"🤖 Asistente (para Alice): {res_alice['messages'][-1].content}\n")

    # Paso 3: Bob intenta acceder al hilo de Alice (Demostración de Autorización 403)
    print("🚨 Bob (estudiante) intenta leer el hilo privado de Alice...")
    try:
        access_mgr.verify_read_access(alice_thread["thread_id"], bob)
        print("❌ Error de seguridad: Bob pudo acceder al hilo de Alice")
    except PermissionError as e:
        print(f"🛡️  [AUTORIZACIÓN EXITOSA] Bloqueado con éxito: {e}")

    # Paso 4: Bob conversa en su propio hilo
    bob_thread = access_mgr.create_thread("thread-bob-public", bob)
    config_bob = {
        "configurable": {
            "thread_id": bob_thread["thread_id"],
            "langgraph_auth_user": bob,
        }
    }
    res_bob = await app.ainvoke(
        {"messages": [HumanMessage(content="¿Qué ejercicios tengo pendientes hoy?")]},
        config=config_bob,
    )
    print(f"\n🤖 Asistente (para Bob en su hilo): {res_bob['messages'][-1].content}")

    print("\n✅ Demostración del Módulo 5 completada con éxito.")

if __name__ == "__main__":
    asyncio.run(main())
