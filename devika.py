from flask import Flask, request, jsonify, send_file, make_response
from flask_cors import CORS
import os
import logging
from threading import Thread
import tiktoken
from src.init import init_devika
from src.config import Config
from src.logger import Logger, route_logger
from src.project import ProjectManager
from src.state import AgentState
from src.agents import Agent
from src.llm import LLM

app = Flask(__name__)
log = logging.getLogger("werkzeug")
log.disabled = True
CORS(app)

logger = Logger()

TIKTOKEN_ENC = tiktoken.get_encoding("cl100k_base")

os.environ["TOKENIZERS_PARALLELISM"] = "false"

@app.route("/api/create-project", methods=["POST"])
@route_logger(logger)
def create_project():
    data = request.json
    project_name = data.get("project_name")
    if not project_name:
        return jsonify({"error": "Project name is required"}), 400
    ProjectManager().create_project(project_name)
    return jsonify({"message": "Project created"}), 201

@app.route("/api/execute-agent", methods=["POST"])
@route_logger(logger)
def execute_agent():
    data = request.json
    prompt = data.get("prompt")
    base_model = data.get("base_model")
    project_name = data.get("project_name")
    web_search = data.get("web_search")

    if not base_model:
        return jsonify({"error": "base_model is required"}), 400
    if not all([prompt, project_name]):
        return jsonify({"error": "prompt and project_name are required"}), 400

    thread = Thread(
        target=lambda: Agent(base_model=base_model).execute(prompt, project_name, web_search)
    )
    thread.start()

    return jsonify({"message": "Started Devika Agent"}), 202

@app.route("/api/get-browser-snapshot", methods=["GET"])
@route_logger(logger)
def browser_snapshot():
    snapshot_path = request.args.get("snapshot_path")
    if not snapshot_path or not os.path.exists(snapshot_path):
        return jsonify({"error": "Snapshot not found"}), 404
    return send_file(snapshot_path, as_attachment=True)


@app.route("/api/download-project", methods=["GET"])
@route_logger(logger)
def download_project():
    pass

@app.route("/api/download-project-pdf", methods=["GET"])
@route_logger(logger)
def download_project_pdf():
    pass

@app.route("/api/get-messages", methods=["POST"])
@route_logger(logger)
def get_messages():
    pass

@app.route("/api/send-message", methods=["POST"])
@route_logger(logger)
def send_message():
    pass

@app.route("/api/project-list", methods=["GET"])
@route_logger(logger)
def project_list():
    pass

@app.route("/api/model-list", methods=["GET"])
@route_logger(logger)
def model_list():
    pass

@app.route("/api/is-agent-active", methods=["POST"])
@route_logger(logger)
def is_agent_active():
    pass

@app.route("/api/get-agent-state", methods=["POST"])
@route_logger(logger)
def get_agent_state():
    pass

@app.route("/api/calculate-tokens", methods=["POST"])
@route_logger(logger)
def calculate_tokens():
    pass

@app.route("/api/token-usage", methods=["GET"])
@route_logger(logger)
def token_usage():
    pass

@app.route("/api/real-time-logs", methods=["GET"])
def real_time_logs():
    pass

@app.route("/api/get-browser-session", methods=["GET"])
@route_logger(logger)
def get_browser_session():
    pass

@app.route("/api/get-terminal-session", methods=["GET"])
@route_logger(logger)
def get_terminal_session():
    pass

@app.route("/api/run-code", methods=["POST"])
@route_logger(logger)
def run_code():
    pass

@app.route("/api/set-settings", methods=["POST"])
@route_logger(logger)
def set_settings():
    pass

@app.route("/api/get-settings", methods=["GET"])
@route_logger(logger)
def get_settings():
    pass

if __name__ == "__main__":
    logger.info("Booting up... This may take a few seconds")
    init_devika()
    app.run(debug=False, port=1337, host="0.0.0.0")
