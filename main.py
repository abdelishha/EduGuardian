"""
EduGuardian — Main Entry Point
================================
HOW TO RUN:
  Double-click start.bat   (easiest)
  OR run: python -m main

Then open: http://localhost:5000
"""

import sys
import io
import os
import asyncio
import traceback

# Fix Windows terminal encoding so special characters display correctly
if hasattr(sys.stdout, 'buffer'):
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
if hasattr(sys.stderr, 'buffer'):
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from dotenv import load_dotenv

# ------------------------------------------------------------------
# Load .env and verify API key
# ------------------------------------------------------------------
load_dotenv()
api_key = os.getenv("GOOGLE_API_KEY", "")

if not api_key or api_key == "your_google_api_key_here":
    print("\n" + "="*60)
    print("[ERROR] No Google API Key found!")
    print("="*60)
    print("1. Go to: https://aistudio.google.com")
    print("2. Click 'Get API Key'")
    print("3. Open the '.env' file in this folder")
    print("4. Replace 'your_google_api_key_here' with your key")
    print("5. Save and run again.")
    print("="*60 + "\n")
    sys.exit(1)

os.environ["GOOGLE_API_KEY"] = api_key

# ------------------------------------------------------------------
# Import ADK AFTER setting the API key
# ------------------------------------------------------------------
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai import types as genai_types
from agents.orchestrator_agent import create_orchestrator_agent

# ------------------------------------------------------------------
# Flask app
# ------------------------------------------------------------------
app = Flask(__name__, static_folder="ui")
CORS(app)

# ------------------------------------------------------------------
# Build the agent system (one-time setup at startup)
# ------------------------------------------------------------------
print("[*] Building EduGuardian agent team...")
session_service = InMemorySessionService()
root_agent = create_orchestrator_agent()
APP_NAME = "edu_guardian"

runner = Runner(
    agent=root_agent,
    app_name=APP_NAME,
    session_service=session_service,
)
print("[OK] All agents ready!")

# Cache session IDs per user so we keep conversation history
_session_cache: dict[str, str] = {}


async def _get_or_create_session(user_id: str) -> str:
    """Return an existing session ID or create a fresh one (async-safe for ADK 1.3)."""
    if user_id in _session_cache:
        return _session_cache[user_id]

    # create_session may be async or sync depending on ADK version — handle both
    result = session_service.create_session(app_name=APP_NAME, user_id=user_id)
    if asyncio.iscoroutine(result):
        session = await result
    else:
        session = result

    _session_cache[user_id] = session.id
    print(f"[+] Session created for {user_id}: {session.id}")
    return session.id


async def _run_agent(user_id: str, message: str) -> str:
    """Send a message through the full 4-agent pipeline and return the text reply."""
    session_id = await _get_or_create_session(user_id)

    content = genai_types.Content(
        role="user",
        parts=[genai_types.Part(text=message)]
    )

    final_text = ""
    last_agent_name = "eduguardian_orchestrator"

    async for event in runner.run_async(
        user_id=user_id,
        session_id=session_id,
        new_message=content,
    ):
        # Catch-all: check if the agent name is mentioned anywhere in the event string representation
        # because ADK hides sub-agent routing inside complex function call objects or tool results.
        event_str = str(event)
        for sub_agent in ["tutor_agent", "wellness_agent", "study_plan_agent"]:
            if f"name='{sub_agent}'" in event_str or f'name="{sub_agent}"' in event_str or f"'{sub_agent}'" in event_str or f'"{sub_agent}"' in event_str:
                last_agent_name = sub_agent

        if event.is_final_response() and event.content:
            for part in event.content.parts:
                if hasattr(part, "text") and part.text:
                    final_text += part.text

    reply = final_text.strip() or "I had trouble generating a response. Please try again!"
    return reply, last_agent_name

# ------------------------------------------------------------------
# Routes
# ------------------------------------------------------------------

@app.route("/")
def serve_index():
    return send_from_directory("ui", "index.html")


@app.route("/<path:filename>")
def serve_static(filename):
    return send_from_directory("ui", filename)


@app.route("/api/health")
def health():
    return jsonify({"status": "ok", "agents": 4, "mcp": "connected"})


@app.route("/api/chat", methods=["POST"])
def chat():
    data = request.get_json(silent=True) or {}
    message = (data.get("message") or "").strip()
    user_id = (data.get("user_id") or "student_default").strip()

    if not message:
        return jsonify({"error": "Empty message"}), 400

    print(f"[MSG] {user_id}: {message[:80]}")

    try:
        # asyncio.run() creates a fresh event loop each time — works with Flask
        reply, active_agent = asyncio.run(_run_agent(user_id, message))
        print(f"[OK] Reply ({len(reply)} chars) from {active_agent}")
        return jsonify({
            "response": reply,
            "active_agent": active_agent,
            "status": "success"
        })

    except Exception as exc:
        err_detail = traceback.format_exc()
        print(f"[ERR] Exception: {type(exc).__name__}: {exc}")
        print(f"[ERR] Full traceback:\n{err_detail}", flush=True)
        return jsonify({
            "response": "I encountered a technical issue. Please try again in a moment.",
            "error": str(exc),
            "status": "error"
        }), 500


@app.route("/api/reset", methods=["POST"])
def reset():
    data = request.get_json(silent=True) or {}
    user_id = data.get("user_id", "student_default")
    _session_cache.pop(user_id, None)
    print(f"[~] Session cleared for {user_id}")
    return jsonify({"status": "reset"})


# ------------------------------------------------------------------
# Start
# ------------------------------------------------------------------
if __name__ == "__main__":
    print("\n" + "="*60)
    print("  EduGuardian - Starting Up")
    print("="*60)
    print("  [OK] Tutor Agent       - Academic expert")
    print("  [OK] Wellness Agent    - Mental health support + HITL")
    print("  [OK] Study Planner     - Schedule builder")
    print("  [OK] MCP Server        - 4 tools connected")
    print("="*60)
    print("  >> Browser: http://localhost:5000")
    print("  >> Stop:    CTRL+C")
    print("="*60 + "\n")
    app.run(host="0.0.0.0", port=5000, debug=False)
