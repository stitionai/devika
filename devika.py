"""
    DO NOT REARRANGE THE ORDER OF THE FUNCTION CALLS AND VARIABLE DECLARATIONS
    AS IT MAY CAUSE IMPORT ERRORS AND OTHER ISSUES
"""
from gevent import monkey
monkey.patch_all()
from src.init import init_devika
init_devika()


from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
from src.socket_instance import socketio, emit_agent
import os
import logging
from threading import Thread
import tiktoken

from src.apis.project import project_bp
from src.config import Config
from src.logger import Logger, route_logger
from src.project import ProjectManager
from src.state import AgentState
from src.agents import Agent
from src.llm import LLM


app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": # Change the origin to your frontend URL
                             [
                                 "https://localhost:3000",
                                 "http://localhost:3000",
                                 ]}}) 
app.register_blueprint(project_bp)
socketio.init_app(app)


log = logging.getLogger("werkzeug")
log.disabled = True


TIKTOKEN_ENC = tiktoken.get_encoding("cl100k_base")

os.environ["TOKENIZERS_PARALLELISM"] = "false"

manager = ProjectManager()
AgentState = AgentState()
config = Config()
logger = Logger()


# initial socket
@socketio.on('socket_connect')
def test_connect(data):
    print("Socket connected :: ", data)
    emit_agent("socket_response", {"data": "Server Connected"})


@app.route("/api/data", methods=["GET"])
@route_logger(logger)
def data():
    project = manager.get_project_list()
    models = LLM().list_models()
    search_engines = ["Bing", "Google", "DuckDuckGo"]
    return jsonify({"projects": project, "models": models, "search_engines": search_engines})


@app.route("/api/messages", methods=["POST"])
def get_messages():
    data = request.json
    project_name = data.get("project_name")
    messages = manager.get_messages(project_name)
    return jsonify({"messages": messages})


# Main socket
@socketio.on('user-message')
def handle_message(data):
    logger.info(f"User message: {data}")
    message = data.get('message')
    base_model = data.get('base_model')
    project_name = data.get('project_name')
    search_engine = data.get('search_engine').lower()

    agent = Agent(base_model=base_model, search_engine=search_engine)

    state = AgentState.get_latest_state(project_name)
    if not state:
        thread = Thread(target=lambda: agent.execute(message, project_name))
        thread.start()
    else:
        if AgentState.is_agent_completed(project_name):
            thread = Thread(target=lambda: agent.subsequent_execute(message, project_name))
            thread.start()
        else:
            emit_agent("info", {"type": "warning", "message": "previous agent doesn't completed it's task."})
            last_state = AgentState.get_latest_state(project_name)
            if last_state["agent_is_active"] or not last_state["completed"]:
                thread = Thread(target=lambda: agent.execute(message, project_name))
                thread.start()
            else:
                thread = Thread(target=lambda: agent.subsequent_execute(message, project_name))
                thread.start()

@app.route("/api/is-agent-active", methods=["POST"])
@route_logger(logger)
def is_agent_active():
    data = request.json
    project_name = data.get("project_name")
    is_active = AgentState.is_agent_active(project_name)
    return jsonify({"is_active": is_active})


@app.route("/api/get-agent-state", methods=["POST"])
@route_logger(logger)
def get_agent_state():
    data = request.json
    project_name = data.get("project_name")
    agent_state = AgentState.get_latest_state(project_name)
    return jsonify({"state": agent_state})


@app.route("/api/get-browser-snapshot", methods=["GET"])
@route_logger(logger)
def browser_snapshot():
    snapshot_path = request.args.get("snapshot_path")
    return send_file(snapshot_path, as_attachment=True)


@app.route("/api/get-browser-session", methods=["GET"])
@route_logger(logger)
def get_browser_session():
    project_name = request.args.get("project_name")
    agent_state = AgentState.get_latest_state(project_name)
    if not agent_state:
        return jsonify({"session": None})
    else:
        browser_session = agent_state["browser_session"]
        return jsonify({"session": browser_session})


@app.route("/api/get-terminal-session", methods=["GET"])
@route_logger(logger)
def get_terminal_session():
    project_name = request.args.get("project_name")
    agent_state = AgentState.get_latest_state(project_name)
    if not agent_state:
        return jsonify({"terminal_state": None})
    else:
        terminal_state = agent_state["terminal_session"]
        return jsonify({"terminal_state": terminal_state})


@app.route("/api/run-code", methods=["POST"])
@route_logger(logger)
def run_code():
    data = request.json
    project_name = data.get("project_name")
    code = data.get("code")
    # TODO: Implement code execution logic
    return jsonify({"message": "Code execution started"})


@app.route("/api/calculate-tokens", methods=["POST"])
@route_logger(logger)
def calculate_tokens():
    data = request.json
    prompt = data.get("prompt")
    tokens = len(TIKTOKEN_ENC.encode(prompt))
    return jsonify({"token_usage": tokens})


@app.route("/api/token-usage", methods=["GET"])
@route_logger(logger)
def token_usage():
    project_name = request.args.get("project_name")
    token_count = AgentState.get_latest_token_usage(project_name)
    return jsonify({"token_usage": token_count})


@app.route("/api/logs", methods=["GET"])
def real_time_logs():
    log_file = logger.read_log_file()
    return jsonify({"logs": log_file})


@app.route("/api/settings", methods=["POST"])
@route_logger(logger)
def set_settings():
    data = request.json
    config.update_config(data)
    return jsonify({"message": "Settings updated"})


@app.route("/api/settings", methods=["GET"])
@route_logger(logger)
def get_settings():
    configs = config.get_config()
    return jsonify({"settings": configs})


@app.route("/api/status", methods=["GET"])
@route_logger(logger)
def status():
    return jsonify({"status": "server is running!"})

if __name__ == "__main__":
    logger.info("Devika is up and running!")
    socketio.run(app, debug=False, port=1337, host="0.0.0.0")
