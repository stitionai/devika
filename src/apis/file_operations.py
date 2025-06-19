from flask import blueprints, request, jsonify
from werkzeug.utils import secure_filename
import os
import json
from src.logger import Logger, route_logger
from src.config import Config
from src.project import ProjectManager

file_ops_bp = blueprints.Blueprint("file_operations", __name__)
logger = Logger()
manager = ProjectManager()
config = Config()

@file_ops_bp.route("/api/save-file", methods=["POST"])
@route_logger(logger)
def save_file():
    try:
        data = request.json
        project_name = secure_filename(data.get("project_name"))
        file_path = data.get("file_path")
        content = data.get("content", "")
        
        if not project_name or not file_path:
            return jsonify({"error": "Missing required fields"}), 400
        
        # Construct full file path
        projects_dir = config.get_projects_dir()
        project_dir = os.path.join(projects_dir, project_name.lower().replace(" ", "-"))
        full_file_path = os.path.join(project_dir, file_path)
        
        # Ensure directory exists
        os.makedirs(os.path.dirname(full_file_path), exist_ok=True)
        
        # Write file
        with open(full_file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        logger.info(f"Saved file: {full_file_path}")
        return jsonify({"status": "success", "message": "File saved successfully"})
        
    except Exception as e:
        logger.error(f"Error saving file: {str(e)}")
        return jsonify({"error": f"Failed to save file: {str(e)}"}), 500

@file_ops_bp.route("/api/create-file", methods=["POST"])
@route_logger(logger)
def create_file():
    try:
        data = request.json
        project_name = secure_filename(data.get("project_name"))
        file_path = data.get("file_path")
        content = data.get("content", "")
        
        if not project_name or not file_path:
            return jsonify({"error": "Missing required fields"}), 400
        
        # Construct full file path
        projects_dir = config.get_projects_dir()
        project_dir = os.path.join(projects_dir, project_name.lower().replace(" ", "-"))
        full_file_path = os.path.join(project_dir, file_path)
        
        # Check if file already exists
        if os.path.exists(full_file_path):
            return jsonify({"error": "File already exists"}), 409
        
        # Ensure directory exists
        os.makedirs(os.path.dirname(full_file_path), exist_ok=True)
        
        # Create file
        with open(full_file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        logger.info(f"Created file: {full_file_path}")
        return jsonify({"status": "success", "message": "File created successfully"})
        
    except Exception as e:
        logger.error(f"Error creating file: {str(e)}")
        return jsonify({"error": f"Failed to create file: {str(e)}"}), 500

@file_ops_bp.route("/api/delete-file", methods=["POST"])
@route_logger(logger)
def delete_file():
    try:
        data = request.json
        project_name = secure_filename(data.get("project_name"))
        file_path = data.get("file_path")
        
        if not project_name or not file_path:
            return jsonify({"error": "Missing required fields"}), 400
        
        # Construct full file path
        projects_dir = config.get_projects_dir()
        project_dir = os.path.join(projects_dir, project_name.lower().replace(" ", "-"))
        full_file_path = os.path.join(project_dir, file_path)
        
        # Check if file exists
        if not os.path.exists(full_file_path):
            return jsonify({"error": "File not found"}), 404
        
        # Delete file
        os.remove(full_file_path)
        
        logger.info(f"Deleted file: {full_file_path}")
        return jsonify({"status": "success", "message": "File deleted successfully"})
        
    except Exception as e:
        logger.error(f"Error deleting file: {str(e)}")
        return jsonify({"error": f"Failed to delete file: {str(e)}"}), 500

@file_ops_bp.route("/api/rename-file", methods=["POST"])
@route_logger(logger)
def rename_file():
    try:
        data = request.json
        project_name = secure_filename(data.get("project_name"))
        old_path = data.get("old_path")
        new_path = data.get("new_path")
        
        if not project_name or not old_path or not new_path:
            return jsonify({"error": "Missing required fields"}), 400
        
        # Construct full file paths
        projects_dir = config.get_projects_dir()
        project_dir = os.path.join(projects_dir, project_name.lower().replace(" ", "-"))
        old_full_path = os.path.join(project_dir, old_path)
        new_full_path = os.path.join(project_dir, new_path)
        
        # Check if old file exists
        if not os.path.exists(old_full_path):
            return jsonify({"error": "File not found"}), 404
        
        # Check if new file already exists
        if os.path.exists(new_full_path):
            return jsonify({"error": "Target file already exists"}), 409
        
        # Ensure target directory exists
        os.makedirs(os.path.dirname(new_full_path), exist_ok=True)
        
        # Rename file
        os.rename(old_full_path, new_full_path)
        
        logger.info(f"Renamed file: {old_full_path} -> {new_full_path}")
        return jsonify({"status": "success", "message": "File renamed successfully"})
        
    except Exception as e:
        logger.error(f"Error renaming file: {str(e)}")
        return jsonify({"error": f"Failed to rename file: {str(e)}"}), 500

@file_ops_bp.route("/api/create-folder", methods=["POST"])
@route_logger(logger)
def create_folder():
    try:
        data = request.json
        project_name = secure_filename(data.get("project_name"))
        folder_path = data.get("folder_path")
        
        if not project_name or not folder_path:
            return jsonify({"error": "Missing required fields"}), 400
        
        # Construct full folder path
        projects_dir = config.get_projects_dir()
        project_dir = os.path.join(projects_dir, project_name.lower().replace(" ", "-"))
        full_folder_path = os.path.join(project_dir, folder_path)
        
        # Check if folder already exists
        if os.path.exists(full_folder_path):
            return jsonify({"error": "Folder already exists"}), 409
        
        # Create folder
        os.makedirs(full_folder_path, exist_ok=True)
        
        logger.info(f"Created folder: {full_folder_path}")
        return jsonify({"status": "success", "message": "Folder created successfully"})
        
    except Exception as e:
        logger.error(f"Error creating folder: {str(e)}")
        return jsonify({"error": f"Failed to create folder: {str(e)}"}), 500

@file_ops_bp.route("/api/get-file-content", methods=["GET"])
@route_logger(logger)
def get_file_content():
    try:
        project_name = secure_filename(request.args.get("project_name"))
        file_path = request.args.get("file_path")
        
        if not project_name or not file_path:
            return jsonify({"error": "Missing required parameters"}), 400
        
        # Construct full file path
        projects_dir = config.get_projects_dir()
        project_dir = os.path.join(projects_dir, project_name.lower().replace(" ", "-"))
        full_file_path = os.path.join(project_dir, file_path)
        
        # Check if file exists
        if not os.path.exists(full_file_path):
            return jsonify({"error": "File not found"}), 404
        
        # Read file content
        with open(full_file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        return jsonify({
            "status": "success",
            "content": content,
            "file_path": file_path
        })
        
    except Exception as e:
        logger.error(f"Error reading file: {str(e)}")
        return jsonify({"error": f"Failed to read file: {str(e)}"}), 500