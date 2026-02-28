from flask import blueprints, request, jsonify
from werkzeug.utils import secure_filename
from src.logger import Logger, route_logger
from src.agents.code_reviewer import CodeReviewer
from src.agents.test_generator import TestGenerator
from src.agents.performance_optimizer import PerformanceOptimizer
from src.agents.security_auditor import SecurityAuditor
from src.agents.documentation_generator import DocumentationGenerator
from src.agents.dependency_manager import DependencyManager
from src.filesystem import ReadCode
from src.project import ProjectManager

analysis_bp = blueprints.Blueprint("analysis", __name__)
logger = Logger()
manager = ProjectManager()

def validate_request_data(data, required_fields):
    """Validate request data and return error if missing required fields"""
    if not data:
        return {"error": "No data provided"}, 400
    
    missing_fields = [field for field in required_fields if not data.get(field)]
    if missing_fields:
        return {"error": f"Missing required fields: {', '.join(missing_fields)}"}, 400
    
    return None, None

@analysis_bp.route("/api/code-review", methods=["POST"])
@route_logger(logger)
def code_review():
    try:
        data = request.json
        error_response, status_code = validate_request_data(data, ["project_name"])
        if error_response:
            return jsonify(error_response), status_code
        
        project_name = secure_filename(data.get("project_name"))
        base_model = data.get("base_model", "gpt-3.5-turbo")
        review_type = data.get("review_type", "general")
        
        # Check if project exists
        if not manager.get_project_files(project_name):
            return jsonify({"status": "error", "message": "Project not found or has no files"}), 404
        
        code_markdown = ReadCode(project_name).code_set_to_markdown()
        if not code_markdown.strip():
            return jsonify({"status": "error", "message": "No code found in project"}), 400
            
        reviewer = CodeReviewer(base_model=base_model)
        result = reviewer.execute(code_markdown, review_type, project_name)
        
        if result:
            return jsonify({"status": "success", "review": result})
        else:
            return jsonify({"status": "error", "message": "Code review failed to generate results"}), 500
            
    except Exception as e:
        logger.error(f"Code review error: {str(e)}")
        return jsonify({"status": "error", "message": f"Internal server error: {str(e)}"}), 500

@analysis_bp.route("/api/generate-tests", methods=["POST"])
@route_logger(logger)
def generate_tests():
    try:
        data = request.json
        error_response, status_code = validate_request_data(data, ["project_name"])
        if error_response:
            return jsonify(error_response), status_code
        
        project_name = secure_filename(data.get("project_name"))
        base_model = data.get("base_model", "gpt-3.5-turbo")
        test_type = data.get("test_type", "unit")
        
        # Check if project exists
        if not manager.get_project_files(project_name):
            return jsonify({"status": "error", "message": "Project not found or has no files"}), 404
        
        code_markdown = ReadCode(project_name).code_set_to_markdown()
        if not code_markdown.strip():
            return jsonify({"status": "error", "message": "No code found in project"}), 400
            
        test_generator = TestGenerator(base_model=base_model)
        result = test_generator.execute(code_markdown, test_type, project_name)
        
        if result:
            test_generator.save_tests_to_project(result, project_name)
            return jsonify({"status": "success", "message": "Tests generated successfully", "test_count": len(result)})
        else:
            return jsonify({"status": "error", "message": "Failed to generate tests"}), 500
            
    except Exception as e:
        logger.error(f"Test generation error: {str(e)}")
        return jsonify({"status": "error", "message": f"Internal server error: {str(e)}"}), 500

@analysis_bp.route("/api/performance-analysis", methods=["POST"])
@route_logger(logger)
def performance_analysis():
    try:
        data = request.json
        error_response, status_code = validate_request_data(data, ["project_name"])
        if error_response:
            return jsonify(error_response), status_code
        
        project_name = secure_filename(data.get("project_name"))
        base_model = data.get("base_model", "gpt-3.5-turbo")
        performance_metrics = data.get("performance_metrics", "")
        
        # Check if project exists
        if not manager.get_project_files(project_name):
            return jsonify({"status": "error", "message": "Project not found or has no files"}), 404
        
        code_markdown = ReadCode(project_name).code_set_to_markdown()
        if not code_markdown.strip():
            return jsonify({"status": "error", "message": "No code found in project"}), 400
            
        optimizer = PerformanceOptimizer(base_model=base_model)
        result = optimizer.execute(code_markdown, performance_metrics, project_name)
        
        if result:
            return jsonify({"status": "success", "analysis": result})
        else:
            return jsonify({"status": "error", "message": "Performance analysis failed to generate results"}), 500
            
    except Exception as e:
        logger.error(f"Performance analysis error: {str(e)}")
        return jsonify({"status": "error", "message": f"Internal server error: {str(e)}"}), 500

@analysis_bp.route("/api/security-audit", methods=["POST"])
@route_logger(logger)
def security_audit():
    try:
        data = request.json
        error_response, status_code = validate_request_data(data, ["project_name"])
        if error_response:
            return jsonify(error_response), status_code
        
        project_name = secure_filename(data.get("project_name"))
        base_model = data.get("base_model", "gpt-3.5-turbo")
        audit_type = data.get("audit_type", "comprehensive")
        
        # Check if project exists
        if not manager.get_project_files(project_name):
            return jsonify({"status": "error", "message": "Project not found or has no files"}), 404
        
        code_markdown = ReadCode(project_name).code_set_to_markdown()
        if not code_markdown.strip():
            return jsonify({"status": "error", "message": "No code found in project"}), 400
            
        auditor = SecurityAuditor(base_model=base_model)
        result = auditor.execute(code_markdown, audit_type, project_name)
        
        if result:
            return jsonify({"status": "success", "audit": result})
        else:
            return jsonify({"status": "error", "message": "Security audit failed to generate results"}), 500
            
    except Exception as e:
        logger.error(f"Security audit error: {str(e)}")
        return jsonify({"status": "error", "message": f"Internal server error: {str(e)}"}), 500

@analysis_bp.route("/api/generate-documentation", methods=["POST"])
@route_logger(logger)
def generate_documentation():
    try:
        data = request.json
        error_response, status_code = validate_request_data(data, ["project_name"])
        if error_response:
            return jsonify(error_response), status_code
        
        project_name = secure_filename(data.get("project_name"))
        base_model = data.get("base_model", "gpt-3.5-turbo")
        doc_type = data.get("doc_type", "api")
        
        # Check if project exists
        if not manager.get_project_files(project_name):
            return jsonify({"status": "error", "message": "Project not found or has no files"}), 404
        
        code_markdown = ReadCode(project_name).code_set_to_markdown()
        if not code_markdown.strip():
            return jsonify({"status": "error", "message": "No code found in project"}), 400
            
        doc_generator = DocumentationGenerator(base_model=base_model)
        result = doc_generator.execute(code_markdown, doc_type, project_name)
        
        if result:
            doc_generator.save_docs_to_project(result, project_name)
            return jsonify({"status": "success", "message": "Documentation generated successfully", "doc_count": len(result)})
        else:
            return jsonify({"status": "error", "message": "Failed to generate documentation"}), 500
            
    except Exception as e:
        logger.error(f"Documentation generation error: {str(e)}")
        return jsonify({"status": "error", "message": f"Internal server error: {str(e)}"}), 500

@analysis_bp.route("/api/dependency-analysis", methods=["POST"])
@route_logger(logger)
def dependency_analysis():
    try:
        data = request.json
        error_response, status_code = validate_request_data(data, ["project_name"])
        if error_response:
            return jsonify(error_response), status_code
        
        project_name = secure_filename(data.get("project_name"))
        base_model = data.get("base_model", "gpt-3.5-turbo")
        
        # Check if project exists
        project_files = manager.get_project_files(project_name)
        if not project_files:
            return jsonify({"status": "error", "message": "Project not found or has no files"}), 404
        
        code_markdown = ReadCode(project_name).code_set_to_markdown()
        
        # Get package files content
        package_files = ""
        package_file_names = ['package.json', 'requirements.txt', 'Cargo.toml', 'go.mod', 'composer.json', 'pom.xml', 'build.gradle']
        
        for file in project_files:
            if file['file'] in package_file_names:
                package_files += f"File: {file['file']}\n{file['code']}\n\n"
        
        if not package_files.strip() and not code_markdown.strip():
            return jsonify({"status": "error", "message": "No dependency files or code found in project"}), 400
        
        dependency_manager = DependencyManager(base_model=base_model)
        result = dependency_manager.execute(code_markdown, package_files, project_name)
        
        if result:
            return jsonify({"status": "success", "analysis": result})
        else:
            return jsonify({"status": "error", "message": "Dependency analysis failed to generate results"}), 500
            
    except Exception as e:
        logger.error(f"Dependency analysis error: {str(e)}")
        return jsonify({"status": "error", "message": f"Internal server error: {str(e)}"}), 500