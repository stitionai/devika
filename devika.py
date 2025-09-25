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
    """Handle a socket connection event.
    
    This function is triggered when a client connects to the server. It logs the connection details and emits a response
    back to the client indicating that the server is connected.
    
    Args:
        data (dict): Data received with the connection event.
    """
    print("Socket connected :: ", data)
    emit_agent("socket_response", {"data": "Server Connected"})


@app.route("/api/data", methods=["GET"])
@route_logger(logger)
def data():
    """Handle GET requests to the /api/data endpoint.
    
    This function retrieves a list of projects from the manager, lists available language models, and defines a set of
    search engines. It then returns these details in a JSON response.
    
    Returns:
        jsonify: A JSON object containing the project list, model list, and search engine options.
    """
    project = manager.get_project_list()
    models = LLM().list_models()
    search_engines = ["Bing", "Google", "DuckDuckGo"]
    return jsonify({"projects": project, "models": models, "search_engines": search_engines})


@app.route("/api/messages", methods=["POST"])
def get_messages():
    """Handle POST requests to retrieve messages for a specific project.
    
    This function processes incoming JSON data, extracts the project name, and retrieves associated messages using the
    `manager` object. It then returns the messages in a JSON response.
    
    Returns:
        dict: A dictionary containing the list of messages under the key "messages".
    """
    data = request.json
    project_name = data.get("project_name")
    messages = manager.get_messages(project_name)
    return jsonify({"messages": messages})


# Main socket
@socketio.on('user-message')
def handle_message(data):
    """Handle user messages received through a WebSocket connection.
    
    This function processes incoming user messages and delegates the appropriate task to an AI agent based on the current
    state of the project. It checks whether there is an active or completed agent session, and either starts a new execution
    or continues with subsequent execution accordingly.
    
    Args:
        data (dict): A dictionary containing message details such as 'message', 'base_model', 'project_name', and 'search_engine'.
    """
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
    """Check if an agent is active for a given project.
    
    This function retrieves the project name from the request JSON payload and checks the activation status of the agent
    associated with that project. It returns a JSON response indicating whether the agent is active or not.
    
    Returns:
        dict: A dictionary with a single key "is_active" containing a boolean value indicating
            the activation status of the agent.
    """
    data = request.json
    project_name = data.get("project_name")
    is_active = AgentState.is_agent_active(project_name)
    return jsonify({"is_active": is_active})


@app.route("/api/get-agent-state", methods=["POST"])
@route_logger(logger)
def get_agent_state():
    """Get the latest state of an agent for a given project.
    
    This function handles POST requests to retrieve the current state of an agent associated with a specified project. It
    extracts the project name from the JSON data in the request, fetches the latest state using the
    `AgentState.get_latest_state` method, and returns the state as part of a JSON response.
    
    Args:
        project_name (str): The name of the project for which to retrieve the agent's state.
    
    Returns:
        dict: A dictionary containing the agent's state under the key "state".
    """
    data = request.json
    project_name = data.get("project_name")
    agent_state = AgentState.get_latest_state(project_name)
    return jsonify({"state": agent_state})


@app.route("/api/get-browser-snapshot", methods=["GET"])
@route_logger(logger)
def browser_snapshot():
    """Retrieve and download a browser snapshot.
    
    This function handles GET requests to the "/api/get-browser-snapshot" endpoint. It retrieves the 'snapshot_path'
    parameter from the query string and returns the file located at that path as an attachment.
    
    Returns:
        Response: A Flask response object containing the file specified by 'snapshot_path' as an attachment.
    """
    snapshot_path = request.args.get("snapshot_path")
    return send_file(snapshot_path, as_attachment=True)


@app.route("/api/get-browser-session", methods=["GET"])
@route_logger(logger)
def get_browser_session():
    """Retrieve the browser session for a given project.
    
    This function handles GET requests to the '/api/get-browser-session' endpoint. It retrieves the latest agent state for
    the specified project and returns the associated browser session. If no agent state is found, it returns None.
    
    Args:
        project_name (str): The name of the project for which to retrieve the browser session.
    
    Returns:
        dict: A JSON response containing the browser session or None if no agent state is available.
    """
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
    """Get the terminal session state for a specified project.
    
    This function retrieves the latest terminal session state associated with a given project name.  It queries the
    AgentState to find the most recent state and returns it in JSON format. If no state is found, it returns a JSON object
    indicating that the terminal state is None.
    
    Args:
        project_name (str): The name of the project for which to retrieve the terminal session state.
    
    Returns:
        jsonify: A JSON response containing either the terminal state or None if no state is available.
    """
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
    """Run a piece of user-provided code within a specified project.
    
    This function is responsible for handling POST requests to the `/api/run-code` endpoint. It extracts the project name
    and the code from the JSON payload of the request. The actual execution logic for the code is yet to be implemented
    (marked with a TODO).
    
    Returns:
        dict: A JSON response indicating that code execution has started.
    """
    data = request.json
    project_name = data.get("project_name")
    code = data.get("code")
    # TODO: Implement code execution logic
    return jsonify({"message": "Code execution started"})


@app.route("/api/calculate-tokens", methods=["POST"])
@route_logger(logger)
def calculate_tokens():
    """Calculate the number of tokens in a given prompt.
    
    This function receives a JSON payload containing a 'prompt' key, encodes the prompt using TIKTOKEN_ENC, and returns the
    total number of tokens used by the encoded prompt.
    
    Returns:
        dict: A dictionary containing the token usage under the key 'token_usage'.
    """
    data = request.json
    prompt = data.get("prompt")
    tokens = len(TIKTOKEN_ENC.encode(prompt))
    return jsonify({"token_usage": tokens})


@app.route("/api/token-usage", methods=["GET"])
@route_logger(logger)
def token_usage():
    """Retrieve and return the latest token usage count for a specified project.
    
    This function handles GET requests to the `/api/token-usage` endpoint. It retrieves the `project_name` from the query
    parameters, fetches the latest token usage count using the `AgentState.get_latest_token_usage` method, and returns it as
    a JSON response.
    
    Args:
        project_name (str): The name of the project for which to retrieve the token usage count.
    
    Returns:
        dict: A dictionary containing the token usage count under the key `"token_usage"`.
    """
    project_name = request.args.get("project_name")
    token_count = AgentState.get_latest_token_usage(project_name)
    return jsonify({"token_usage": token_count})


@app.route("/api/logs", methods=["GET"])
def real_time_logs():
    """Retrieve and return real-time logs from the application.
    
    This function reads the current content of the log file and returns it as a JSON response. The log data is fetched using
    the `read_log_file` method from the `logger` module.
    
    Returns:
        flask.Response: A JSON response containing the logs.
    """
    log_file = logger.read_log_file()
    return jsonify({"logs": log_file})


@app.route("/api/settings", methods=["POST"])
@route_logger(logger)
def set_settings():
    """Set application settings through an API endpoint.
    
    This function handles a POST request to update the application's configuration. It expects JSON data in the request
    body, which is then used to update the current configuration. After updating the settings, it returns a JSON response
    indicating that the settings have been updated.
    
    Returns:
        dict: A JSON object containing a message indicating successful setting update.
    """
    data = request.json
    config.update_config(data)
    return jsonify({"message": "Settings updated"})


@app.route("/api/settings", methods=["GET"])
@route_logger(logger)
def get_settings():
    """Retrieve the current application settings.
    
    This function fetches the configuration settings from the `config` module and returns them as a JSON response. It uses
    the `route_logger` decorator to log route access.
    
    Returns:
        dict: A dictionary containing the application settings.
    """
    configs = config.get_config()
    return jsonify({"settings": configs})


@app.route("/api/status", methods=["GET"])
@route_logger(logger)
def status():
    """Return the current status of the server.
    
    This function handles GET requests to the `/api/status` endpoint and returns a JSON response indicating that the server
    is running.
    
    Returns:
        dict: A dictionary with a single key-value pair, `{"status": "server is running!"}`.
    """
    return jsonify({"status": "server is running!"})

if __name__ == "__main__":
    logger.info("Devika is up and running!")
    socketio.run(app, debug=False, port=1337, host="0.0.0.0")
