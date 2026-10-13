"""
app.py
──────────────────────────────────────────────────────────────────────────────
Flask Backend — Nutrition Agentic AI Application
REST API endpoints for the web frontend.
"""

import os
import uuid
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from dotenv import load_dotenv

from agent import run_agent, generate_plan_for_profile, get_session_history, clear_session
from plan_saver import save_plan_to_md, list_saved_plans, read_plan
from guardrails import validate_user_profile

load_dotenv()

# ── App setup ─────────────────────────────────────────────────────────────────
app = Flask(__name__, static_folder="static", static_url_path="")
app.secret_key = os.getenv("FLASK_SECRET_KEY", "nutrition-ai-2024")
CORS(app)

# ── Serve the frontend ────────────────────────────────────────────────────────
@app.route("/")
def index():
    return send_from_directory("static", "index.html")


# ── API: Generate personalized nutrition plan ─────────────────────────────────
@app.route("/api/generate-plan", methods=["POST"])
def api_generate_plan():
    """
    POST /api/generate-plan
    Body: { name, age, diet, medical_history, city, country, goals, weight, height }
    Returns: { plan, filename, session_id }
    """
    data = request.get_json(silent=True) or {}

    # Validate profile
    is_valid, err = validate_user_profile(data)
    if not is_valid:
        return jsonify({"error": err}), 400

    # Generate plan
    plan_text = generate_plan_for_profile(data)

    # Save to .md file
    filename = save_plan_to_md(plan_text, data)

    # Create session
    session_id = str(uuid.uuid4())

    return jsonify({
        "plan": plan_text,
        "filename": os.path.basename(filename),
        "session_id": session_id,
        "status": "success",
    })


# ── API: Chat with the agent ───────────────────────────────────────────────────
@app.route("/api/chat", methods=["POST"])
def api_chat():
    """
    POST /api/chat
    Body: { message, profile, session_id }
    Returns: { response, tool_used, safe }
    """
    data       = request.get_json(silent=True) or {}
    message    = data.get("message", "").strip()
    profile    = data.get("profile", {})
    session_id = data.get("session_id", str(uuid.uuid4()))

    if not message:
        return jsonify({"error": "Message cannot be empty."}), 400

    result = run_agent(message, profile, session_id)
    result["session_id"] = session_id
    return jsonify(result)


# ── API: List saved plans ─────────────────────────────────────────────────────
@app.route("/api/plans", methods=["GET"])
def api_list_plans():
    """GET /api/plans — Returns list of saved plan files."""
    plans = list_saved_plans()
    return jsonify({"plans": plans})


# ── API: Download a saved plan ────────────────────────────────────────────────
@app.route("/api/plans/<filename>", methods=["GET"])
def api_get_plan(filename):
    """GET /api/plans/<filename> — Download a saved plan."""
    # Security: only allow .md files from plans directory
    if not filename.endswith(".md") or ".." in filename or "/" in filename:
        return jsonify({"error": "Invalid filename."}), 400

    content = read_plan(filename)
    if not content:
        return jsonify({"error": "Plan not found."}), 404

    return content, 200, {
        "Content-Type": "text/markdown; charset=utf-8",
        "Content-Disposition": f'attachment; filename="{filename}"',
    }


# ── API: Session history ──────────────────────────────────────────────────────
@app.route("/api/session/<session_id>", methods=["GET"])
def api_session_history(session_id):
    """GET /api/session/<session_id> — Return conversation history."""
    history = get_session_history(session_id)
    return jsonify({"history": history, "count": len(history)})


# ── API: Clear session ────────────────────────────────────────────────────────
@app.route("/api/session/<session_id>", methods=["DELETE"])
def api_clear_session(session_id):
    """DELETE /api/session/<session_id> — Clear conversation history."""
    clear_session(session_id)
    return jsonify({"status": "cleared"})


# ── API: Health check ─────────────────────────────────────────────────────────
@app.route("/api/health", methods=["GET"])
def api_health():
    """GET /api/health — Service health check."""
    ibm_configured = bool(os.getenv("IBM_API_KEY") and os.getenv("IBM_PROJECT_ID"))
    return jsonify({
        "status": "healthy",
        "service": "NutriAI — IBM Granite Nutrition Agent",
        "version": "1.0.0",
        "ibm_granite_configured": ibm_configured,
        "mode": "live" if ibm_configured else "demo",
    })


# ── Entry point ───────────────────────────────────────────────────────────────
if __name__ == "__main__":
    port = int(os.getenv("PORT", 5000))
    print(f"\n{'='*60}")
    print("  🥗 NutriAI — IBM Granite Nutrition Agent")
    print(f"  Running on: http://localhost:{port}")
    print(f"  API Docs:   http://localhost:{port}/api/health")
    print(f"{'='*60}\n")
    app.run(host="0.0.0.0", port=port, debug=False)
