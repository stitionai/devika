"""Main file for the Devika Agent."""
import os
import logging
from threading import Thread
from flask import Flask, request, jsonify, send_file, make_response
from flask_cors import CORS
import tiktoken

from src.init import init_devika
from src.config import Config

from src.logger import Logger, route_logger
from src.project import ProjectManager
from src.state import AgentState

from src.agents import Agent
from src.llm import LLM, TOKEN_USAGE

app = Flask(__name__)
log = logging.getLogger("werkzeug")
log.disabled = True
CORS(app)

logger = Logger()

TIKTOKEN_ENC = tiktoken.get_encoding("cl100k_base")

os.environ["TOKENIZERS_PARALLELISM"] = "false"


@app.route("/api/create-project", methods=["POST"])
@route_logger(logger)
def create_project() -> jsonify:
    """Create a new project."""
    data = request.json
    project_name = data.get("project_name")
    if project_name == "": # Check if project name is empty
        return jsonify({"error": "please provide a name of your project"})
    ProjectManager().create_project(project_name)
    return jsonify({"message": "Project created"})


@app.route("/api/execute-agent", methods=["POST"])
@route_logger(logger)
def execute_agent() -> jsonify:
    """Execute the Devika Agent.
    Input:
        prompt: str
        base_model: str
        project_name: str
    """
    data = request.json
    prompt = data.get("prompt")
    base_model = data.get("base_model")
    project_name = data.get("project_name")

    if not base_model: # Check if base_model is empty
        return jsonify({"error": "base_model is required"})
    if not prompt or prompt == "": # Check if prompt is empty
        return jsonify({"error": "Please provide a proper instruction in the prompt"})

    thread = Thread(
        target=lambda: Agent(base_model=base_model).execute(prompt, project_name)
    )
    thread.start()

    return jsonify({"message": "Started Devika Agent"})


@app.route("/api/get-browser-snapshot", methods=["GET"])
@route_logger(logger)
def browser_snapshot() -> send_file:
    """Get the browser snapshot."""
    snapshot_path = request.args.get("snapshot_path")
    return send_file(snapshot_path, as_attachment=True)


@app.route("/api/download-project", methods=["GET"])
@route_logger(logger)
def download_project() -> send_file:
    """Download the project as a zip file."""
    project_name = request.args.get("project_name")
    ProjectManager().project_to_zip(project_name)
    project_path = ProjectManager().get_zip_path(project_name)
    return send_file(project_path, as_attachment=False)


@app.route("/api/download-project-pdf", methods=["GET"])
@route_logger(logger)
def download_project_pdf():
    """Download the project as a PDF file."""
    project_name = request.args.get("project_name")
    pdf_dir = Config().get_pdfs_dir()
    pdf_path = os.path.join(pdf_dir, f"{project_name}.pdf")

    response = make_response(send_file(pdf_path))
    response.headers['Content-Type'] = 'application/pdf'
    return response


@app.route("/api/get-messages", methods=["POST"])
@route_logger(logger)
def get_messages():
    """Get the messages of a project."""
    data = request.json
    project_name = data.get("project_name")
    messages = ProjectManager().get_messages(project_name)
    return jsonify({"messages": messages})


@app.route("/api/send-message", methods=["POST"])
@route_logger(logger)
def send_message():
    """Send a message to the Devika Agent."""
    data = request.json
    message = data.get("message")
    project_name = data.get("project_name")
    base_model = data.get("base_model")

    new_message = ProjectManager().new_message()
    new_message["message"] = message
    new_message["from_devika"] = False
    ProjectManager().add_message_to_project(project_name, new_message)

    if AgentState().is_agent_completed(project_name):
        thread = Thread(
            target=lambda: Agent(base_model=base_model).subsequent_execute(message, project_name)
        )
        thread.start()

    return jsonify({"message": "Message sent"})


@app.route("/api/project-list", methods=["GET"])
@route_logger(logger)
def project_list() -> jsonify:
    """Get the list of projects."""
    pm = ProjectManager()
    projects = pm.get_project_list()
    return jsonify({"projects": projects})


@app.route("/api/model-list", methods=["GET"])
@route_logger(logger)
def model_list() -> jsonify:
    """Get the list of models."""
    models = LLM().list_models()
    return jsonify({"models": models})


@app.route("/api/is-agent-active", methods=["POST"])
@route_logger(logger)
def is_agent_active() -> jsonify:
    """Check if the agent is active."""
    data = request.json
    project_name = data.get("project_name")
    is_active = AgentState().is_agent_active(project_name)
    return jsonify({"is_active": is_active})


@app.route("/api/get-agent-state", methods=["POST"])
@route_logger(logger)
def get_agent_state() -> jsonify:
    """Get the state of the agent."""
    data = request.json
    project_name = data.get("project_name")
    agent_state = AgentState().get_latest_state(project_name)
    return jsonify({"state": agent_state})


@app.route("/api/calculate-tokens", methods=["POST"])
@route_logger(logger)
def calculate_tokens() -> jsonify:
    """Calculate the number of tokens in a prompt."""
    data = request.json
    prompt = data.get("prompt")
    tokens = len(TIKTOKEN_ENC.encode(prompt))
    return jsonify({"token_usage": tokens})


@app.route("/api/token-usage", methods=["GET"])
@route_logger(logger)
def token_usage() -> jsonify:
    """Get the token usage of the Devika Agent."""
    return jsonify({"token_usage": TOKEN_USAGE})


@app.route("/api/real-time-logs", methods=["GET"])
def real_time_logs() -> jsonify:
    """Get the real-time logs."""
    log_file = Logger().read_log_file()
    return jsonify({"log_file": log_file})


@app.route("/api/get-browser-session", methods=["GET"])
@route_logger(logger)
def get_browser_session() -> jsonify:
    """Get the browser session."""
    project_name = request.args.get("project_name")
    agent_state = AgentState().get_latest_state(project_name)
    if not agent_state:
        return jsonify({"session": None})
    browser_session = agent_state["browser_session"]
    return jsonify({"session": browser_session})


@app.route("/api/get-terminal-session", methods=["GET"])
@route_logger(logger)
def get_terminal_session() -> jsonify:
    """Get the terminal session."""
    project_name = request.args.get("project_name")
    agent_state = AgentState().get_latest_state(project_name)
    if not agent_state:
        return jsonify({"terminal_state": None})
    terminal_state = agent_state["terminal_session"]
    return jsonify({"terminal_state": terminal_state})


@app.route("/api/run-code", methods=["POST"])
@route_logger(logger)
def run_code() -> jsonify:
    """Run code in the terminal."""
    data = request.json
    project_name = data.get("project_name")
    code = data.get("code")
    # TODO: Implement code execution logic
    return jsonify({"message": "Code execution not implemented yet"})


@app.route("/api/set-settings", methods=["POST"])
@route_logger(logger)
def set_settings()-> jsonify:
    """Set the settings of Devika."""
    data = request.json
    config = Config()
    config.config.update(data)
    config.save_config()
    return jsonify({"message": "Settings updated"})


@app.route("/api/get-settings", methods=["GET"])
@route_logger(logger)
def get_settings() -> jsonify:
    """Get the settings of Devika."""
    config = Config().get_config()
    return jsonify({"settings": config})


if __name__ == "__main__":
    logger.info("Booting up... This may take a few seconds")
    init_devika()
    app.run(debug=False, port=1337, host="0.0.0.0")
