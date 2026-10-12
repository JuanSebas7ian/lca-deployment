"""
Script de Validación Integral del Entorno Local (LangSmith / LangGraph Deployment)
Valida que todos los agentes, módulos y modelos locales de Ollama funcionen al 100%.
"""

import asyncio
import os
import sys
import subprocess
from dotenv import load_dotenv

load_dotenv(override=True)

PASS = "✅"
FAIL = "❌"
INFO = "ℹ️"

async def test_ollama():
    print(f"\n{INFO} 1. Verificando conexión con Ollama...")
    try:
        from langchain_ollama import ChatOllama
        model_name = os.getenv("OLLAMA_MODEL", "gemma4:12b")
        base_url = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
        llm = ChatOllama(model=model_name, base_url=base_url)
        res = await llm.ainvoke("Di 'Ollama OK'")
        print(f"{PASS} Ollama ({model_name}) respondió correctamente: {res.content.strip()[:60]}")
        return True
    except Exception as e:
        print(f"{FAIL} Fallo al conectar con Ollama: {e}")
        return False

async def test_deep_tutor():
    print(f"\n{INFO} 2. Verificando agente principal (deep_tutor)...")
    try:
        sys.path.insert(0, os.path.abspath("deep_tutor"))
        from agent.agent import graph
        res = await graph.ainvoke({"messages": [{"role": "user", "content": "Di 'Tutor OK'"}]})
        content = res["messages"][-1].content
        print(f"{PASS} deep_tutor ejecutó y respondió: {str(content).strip()[:60]}")
        return True
    except Exception as e:
        print(f"{FAIL} Fallo en deep_tutor: {e}")
        return False

async def test_m5_l5():
    print(f"\n{INFO} 3. Verificando agente autenticado de Módulo 5 (m5/l5)...")
    try:
        sys.path.insert(0, os.path.abspath("m5/l5"))
        from agent.agent import graph as m5_graph
        res = await m5_graph.ainvoke({"messages": [{"role": "user", "content": "Di 'M5 OK'"}]})
        content = res["messages"][-1].content
        print(f"{PASS} m5/l5 ejecutó y respondió: {str(content).strip()[:60]}")
        return True
    except Exception as e:
        print(f"{FAIL} Fallo en m5/l5: {e}")
        return False

def run_script(path: str, label: str):
    print(f"\n{INFO} 4. Ejecutando demostración {label} ({path})...")
    res = subprocess.run([sys.executable, path], capture_output=True, text=True)
    if res.returncode == 0:
        print(f"{PASS} {label} ejecutó exitosamente.")
        return True
    else:
        print(f"{FAIL} {label} falló con código {res.returncode}:")
        print(res.stderr[:200])
        return False

async def main():
    print("=" * 65)
    print("🚀 INICIANDO VALIDACIÓN DEL ENTORNO LOCAL Y AGENTES")
    print("=" * 65)

    results = []
    results.append(await test_ollama())
    results.append(await test_deep_tutor())
    results.append(await test_m5_l5())
    results.append(run_script("m2/local_m2_agent.py", "Módulo 2 (Threads & Streaming)"))
    results.append(run_script("m4/l2/local_persistence_demo.py", "Módulo 4 (Checkpointer & Store)"))
    results.append(run_script("m5/local_auth_demo.py", "Módulo 5 (Auth & Autorización)"))

    print("\n" + "=" * 65)
    if all(results):
        print(f"{PASS} ¡TODAS LAS VALIDACIONES PASARON EXITOSAMENTE! (6/6)")
        print("Todo el entorno está listo para correr el curso 100% en local.")
    else:
        passed = sum(1 for r in results if r)
        print(f"⚠️ Se completaron {passed}/6 pruebas. Revisa los mensajes anteriores.")
    print("=" * 65)

if __name__ == "__main__":
    asyncio.run(main())
