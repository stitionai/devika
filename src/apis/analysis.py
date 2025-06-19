from flask import blueprints, request, jsonify
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

@analysis_bp.route("/api/code-review", methods=["POST"])
@route_logger(logger)
def code_review():
    data = request.json
    project_name = data.get("project_name")
    base_model = data.get("base_model", "gpt-3.5-turbo")
    review_type = data.get("review_type", "general")
    
    try:
        code_markdown = ReadCode(project_name).code_set_to_markdown()
        reviewer = CodeReviewer(base_model=base_model)
        result = reviewer.execute(code_markdown, review_type, project_name)
        
        return jsonify({"status": "success", "review": result})
    except Exception as e:
        logger.error(f"Code review error: {str(e)}")
        return jsonify({"status": "error", "message": str(e)}), 500

@analysis_bp.route("/api/generate-tests", methods=["POST"])
@route_logger(logger)
def generate_tests():
    data = request.json
    project_name = data.get("project_name")
    base_model = data.get("base_model", "gpt-3.5-turbo")
    test_type = data.get("test_type", "unit")
    
    try:
        code_markdown = ReadCode(project_name).code_set_to_markdown()
        test_generator = TestGenerator(base_model=base_model)
        result = test_generator.execute(code_markdown, test_type, project_name)
        
        if result:
            test_generator.save_tests_to_project(result, project_name)
            return jsonify({"status": "success", "message": "Tests generated successfully"})
        else:
            return jsonify({"status": "error", "message": "Failed to generate tests"}), 500
    except Exception as e:
        logger.error(f"Test generation error: {str(e)}")
        return jsonify({"status": "error", "message": str(e)}), 500

@analysis_bp.route("/api/performance-analysis", methods=["POST"])
@route_logger(logger)
def performance_analysis():
    data = request.json
    project_name = data.get("project_name")
    base_model = data.get("base_model", "gpt-3.5-turbo")
    performance_metrics = data.get("performance_metrics", "")
    
    try:
        code_markdown = ReadCode(project_name).code_set_to_markdown()
        optimizer = PerformanceOptimizer(base_model=base_model)
        result = optimizer.execute(code_markdown, performance_metrics, project_name)
        
        return jsonify({"status": "success", "analysis": result})
    except Exception as e:
        logger.error(f"Performance analysis error: {str(e)}")
        return jsonify({"status": "error", "message": str(e)}), 500

@analysis_bp.route("/api/security-audit", methods=["POST"])
@route_logger(logger)
def security_audit():
    data = request.json
    project_name = data.get("project_name")
    base_model = data.get("base_model", "gpt-3.5-turbo")
    audit_type = data.get("audit_type", "comprehensive")
    
    try:
        code_markdown = ReadCode(project_name).code_set_to_markdown()
        auditor = SecurityAuditor(base_model=base_model)
        result = auditor.execute(code_markdown, audit_type, project_name)
        
        return jsonify({"status": "success", "audit": result})
    except Exception as e:
        logger.error(f"Security audit error: {str(e)}")
        return jsonify({"status": "error", "message": str(e)}), 500

@analysis_bp.route("/api/generate-documentation", methods=["POST"])
@route_logger(logger)
def generate_documentation():
    data = request.json
    project_name = data.get("project_name")
    base_model = data.get("base_model", "gpt-3.5-turbo")
    doc_type = data.get("doc_type", "api")
    
    try:
        code_markdown = ReadCode(project_name).code_set_to_markdown()
        doc_generator = DocumentationGenerator(base_model=base_model)
        result = doc_generator.execute(code_markdown, doc_type, project_name)
        
        if result:
            doc_generator.save_docs_to_project(result, project_name)
            return jsonify({"status": "success", "message": "Documentation generated successfully"})
        else:
            return jsonify({"status": "error", "message": "Failed to generate documentation"}), 500
    except Exception as e:
        logger.error(f"Documentation generation error: {str(e)}")
        return jsonify({"status": "error", "message": str(e)}), 500

@analysis_bp.route("/api/dependency-analysis", methods=["POST"])
@route_logger(logger)
def dependency_analysis():
    data = request.json
    project_name = data.get("project_name")
    base_model = data.get("base_model", "gpt-3.5-turbo")
    
    try:
        code_markdown = ReadCode(project_name).code_set_to_markdown()
        
        # Get package files content
        package_files = ""
        try:
            project_files = manager.get_project_files(project_name)
            for file in project_files:
                if file['file'] in ['package.json', 'requirements.txt', 'Cargo.toml', 'go.mod', 'composer.json']:
                    package_files += f"File: {file['file']}\n{file['code']}\n\n"
        except:
            pass
        
        dependency_manager = DependencyManager(base_model=base_model)
        result = dependency_manager.execute(code_markdown, package_files, project_name)
        
        return jsonify({"status": "success", "analysis": result})
    except Exception as e:
        logger.error(f"Dependency analysis error: {str(e)}")
        return jsonify({"status": "error", "message": str(e)}), 500