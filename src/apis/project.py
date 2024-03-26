from flask import blueprints, request, jsonify, send_file, make_response
from src.logger import Logger, route_logger
from src.config import Config
from src.project import ProjectManager
from ..state import AgentState

import os

project_bp = blueprints.Blueprint("project", __name__)

logger = Logger()
manager = ProjectManager()


# Project APIs
@project_bp.route("/api/create-project", methods=["POST"])
@route_logger(logger)
def create_project():
    data = request.json
    project_name = data.get("project_name")
    manager.create_project(project_name)
    return jsonify({"message": "Project created"})


@project_bp.route("/api/delete-project", methods=["POST"])
@route_logger(logger)
def delete_project():
    data = request.json
    project_name = data.get("project_name")
    manager.delete_project(project_name)
    AgentState().delete_state(project_name)
    return jsonify({"message": "Project deleted"})


@project_bp.route("/api/download-project", methods=["GET"])
@route_logger(logger)
def download_project():
    project_name = request.args.get("project_name")
    manager.project_to_zip(project_name)
    project_path = manager.get_zip_path(project_name)
    return send_file(project_path, as_attachment=False)


@project_bp.route("/api/download-project-pdf", methods=["GET"])
@route_logger(logger)
def download_project_pdf():
    project_name = request.args.get("project_name")
    pdf_dir = Config().get_pdfs_dir()
    pdf_path = os.path.join(pdf_dir, f"{project_name}.pdf")

    response = make_response(send_file(pdf_path))
    response.headers['Content-Type'] = 'project_bplication/pdf'
    return response
