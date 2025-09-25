from flask import blueprints, request, jsonify, send_file, make_response
from werkzeug.utils import secure_filename
from src.logger import Logger, route_logger
from src.config import Config
from src.project import ProjectManager
from ..state import AgentState

import os

project_bp = blueprints.Blueprint("project", __name__)

logger = Logger()
manager = ProjectManager()


# Project APIs

@project_bp.route("/api/get-project-files", methods=["GET"])
@route_logger(logger)
def project_files():
    """Retrieve a list of files associated with a specified project.
    
    This function handles GET requests to the `/api/get-project-files` endpoint. It extracts the project name from the
    request arguments, sanitizes it using `secure_filename`, and then retrieves a list of files associated with that project
    from the project manager. The list of files is returned as a JSON response.
    
    Args:
        project_name (str): The name of the project for which to retrieve files. This is extracted from the request arguments.
    
    Returns:
        dict: A dictionary containing the list of files under the key "files".
    """
    project_name = secure_filename(request.args.get("project_name"))
    files = manager.get_project_files(project_name)  
    return jsonify({"files": files})

@project_bp.route("/api/create-project", methods=["POST"])
@route_logger(logger)
def create_project():
    """Create a new project.
    
    This function handles the creation of a new project by extracting the project name from the request JSON, securing the
    filename, and then creating the project using the manager. It returns a JSON response indicating the successful creation
    of the project.
    
    Returns:
        dict: A dictionary with a "message" key containing the success message.
    """
    data = request.json
    project_name = data.get("project_name")
    manager.create_project(secure_filename(project_name))
    return jsonify({"message": "Project created"})


@project_bp.route("/api/delete-project", methods=["POST"])
@route_logger(logger)
def delete_project():
    """Delete a specified project.
    
    This function handles the deletion of a project by extracting the project name from the request JSON, deleting the
    project using the `manager.delete_project` method, and clearing any associated state with the
    `AgentState().delete_state` method. It then returns a success message indicating that the project has been deleted.
    
    Returns:
        jsonify: A JSON response containing a success message: "Project deleted".
    """
    data = request.json
    project_name = secure_filename(data.get("project_name"))
    manager.delete_project(project_name)
    AgentState().delete_state(project_name)
    return jsonify({"message": "Project deleted"})


@project_bp.route("/api/download-project", methods=["GET"])
@route_logger(logger)
def download_project():
    """Downloads a project file by its name.
    
    This function retrieves the project name from the request arguments, creates a zip archive of the project using the
    manager's `project_to_zip` method, and then sends the generated zip file to the client.
    
    Returns:
        Response: A Flask response object containing the zipped project file.
    """
    project_name = secure_filename(request.args.get("project_name"))
    manager.project_to_zip(project_name)
    project_path = manager.get_zip_path(project_name)
    return send_file(project_path, as_attachment=False)


@project_bp.route("/api/download-project-pdf", methods=["GET"])
@route_logger(logger)
def download_project_pdf():
    """Download a project PDF file.
    
    This function handles the request to download a PDF file associated with a specific project. It retrieves the project
    name from the query parameters, constructs the path to the PDF file, and sends it as a response. If the specified
    project name does not correspond to an existing PDF file, it raises a `FileNotFoundError`.
    
    Args:
        project_name (str): The name of the project whose PDF is to be downloaded, provided as a query parameter.
    
    Returns:
        Response: A Flask response object containing the PDF file if found.
    """
    project_name = secure_filename(request.args.get("project_name"))
    pdf_dir = Config().get_pdfs_dir()
    pdf_path = os.path.join(pdf_dir, f"{project_name}.pdf")

    response = make_response(send_file(pdf_path))
    response.headers['Content-Type'] = 'project_bplication/pdf'
    return response
