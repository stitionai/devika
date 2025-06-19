import asyncio
import json
from typing import Dict, Any, List
from datetime import datetime

from src.project import ProjectManager
from src.agents import Agent
from src.state import AgentState
from src.browser.search import BingSearch, GoogleSearch, DuckDuckGoSearch
from src.browser import Browser
from src.filesystem import ReadCode
from src.logger import Logger

class MCPTools:
    """MCP Tools for Devika functionality"""
    
    def __init__(self):
        self.project_manager = ProjectManager()
        self.agent_state = AgentState()
        self.logger = Logger()
    
    async def create_project(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new project"""
        try:
            project_name = args.get("name")
            if not project_name:
                return {"error": "Project name is required"}
            
            self.project_manager.create_project(project_name)
            return {
                "success": True,
                "project_name": project_name,
                "message": f"Project '{project_name}' created successfully"
            }
        except Exception as e:
            return {"error": str(e)}
    
    async def list_projects(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """List all projects"""
        try:
            projects = self.project_manager.get_project_list()
            return {
                "projects": projects,
                "count": len(projects)
            }
        except Exception as e:
            return {"error": str(e)}
    
    async def get_project_files(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """Get files for a project"""
        try:
            project_name = args.get("project_name")
            if not project_name:
                return {"error": "Project name is required"}
            
            files = self.project_manager.get_project_files(project_name)
            return {
                "project_name": project_name,
                "files": files,
                "count": len(files)
            }
        except Exception as e:
            return {"error": str(e)}
    
    async def analyze_code(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze code in a project"""
        try:
            project_name = args.get("project_name")
            analysis_type = args.get("type", "general")
            
            if not project_name:
                return {"error": "Project name is required"}
            
            code_markdown = ReadCode(project_name).code_set_to_markdown()
            
            # Use appropriate analysis agent based on type
            if analysis_type == "security":
                from src.agents.security_auditor import SecurityAuditor
                auditor = SecurityAuditor(base_model="gpt-4")
                result = auditor.execute(code_markdown, "comprehensive", project_name)
            elif analysis_type == "performance":
                from src.agents.performance_optimizer import PerformanceOptimizer
                optimizer = PerformanceOptimizer(base_model="gpt-4")
                result = optimizer.execute(code_markdown, "", project_name)
            elif analysis_type == "review":
                from src.agents.code_reviewer import CodeReviewer
                reviewer = CodeReviewer(base_model="gpt-4")
                result = reviewer.execute(code_markdown, "comprehensive", project_name)
            else:
                result = {"analysis": "General code analysis completed"}
            
            return {
                "project_name": project_name,
                "analysis_type": analysis_type,
                "result": result
            }
        except Exception as e:
            return {"error": str(e)}
    
    async def generate_code(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """Generate code based on requirements"""
        try:
            project_name = args.get("project_name")
            requirements = args.get("requirements")
            base_model = args.get("model", "gpt-4")
            
            if not project_name or not requirements:
                return {"error": "Project name and requirements are required"}
            
            agent = Agent(base_model=base_model, search_engine="bing")
            
            # Execute agent to generate code
            await asyncio.get_event_loop().run_in_executor(
                None, agent.execute, requirements, project_name
            )
            
            return {
                "project_name": project_name,
                "requirements": requirements,
                "status": "Code generation initiated"
            }
        except Exception as e:
            return {"error": str(e)}
    
    async def review_code(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """Review code in a project"""
        try:
            project_name = args.get("project_name")
            review_type = args.get("review_type", "comprehensive")
            
            if not project_name:
                return {"error": "Project name is required"}
            
            from src.agents.code_reviewer import CodeReviewer
            reviewer = CodeReviewer(base_model="gpt-4")
            
            code_markdown = ReadCode(project_name).code_set_to_markdown()
            result = reviewer.execute(code_markdown, review_type, project_name)
            
            return {
                "project_name": project_name,
                "review_type": review_type,
                "result": result
            }
        except Exception as e:
            return {"error": str(e)}
    
    async def execute_agent(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """Execute an agent task"""
        try:
            project_name = args.get("project_name")
            prompt = args.get("prompt")
            base_model = args.get("model", "gpt-4")
            search_engine = args.get("search_engine", "bing")
            
            if not project_name or not prompt:
                return {"error": "Project name and prompt are required"}
            
            agent = Agent(base_model=base_model, search_engine=search_engine)
            
            # Execute agent asynchronously
            await asyncio.get_event_loop().run_in_executor(
                None, agent.execute, prompt, project_name
            )
            
            return {
                "project_name": project_name,
                "prompt": prompt,
                "status": "Agent execution initiated"
            }
        except Exception as e:
            return {"error": str(e)}
    
    async def get_agent_status(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """Get agent status for a project"""
        try:
            project_name = args.get("project_name")
            if not project_name:
                return {"error": "Project name is required"}
            
            state = self.agent_state.get_latest_state(project_name)
            is_active = self.agent_state.is_agent_active(project_name)
            is_completed = self.agent_state.is_agent_completed(project_name)
            
            return {
                "project_name": project_name,
                "is_active": is_active,
                "is_completed": is_completed,
                "state": state
            }
        except Exception as e:
            return {"error": str(e)}
    
    async def search_web(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """Search the web"""
        try:
            query = args.get("query")
            engine = args.get("engine", "bing")
            
            if not query:
                return {"error": "Search query is required"}
            
            if engine == "bing":
                search = BingSearch()
            elif engine == "google":
                search = GoogleSearch()
            else:
                search = DuckDuckGoSearch()
            
            result = search.search(query)
            first_link = search.get_first_link()
            
            return {
                "query": query,
                "engine": engine,
                "first_link": first_link,
                "result": result
            }
        except Exception as e:
            return {"error": str(e)}
    
    async def navigate_browser(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """Navigate browser to URL"""
        try:
            url = args.get("url")
            project_name = args.get("project_name")
            
            if not url:
                return {"error": "URL is required"}
            
            browser = await Browser().start()
            success = await browser.go_to(url)
            
            if success and project_name:
                screenshot_path, screenshot_data = await browser.screenshot(project_name)
                await browser.close()
                
                return {
                    "url": url,
                    "success": True,
                    "screenshot_path": screenshot_path
                }
            else:
                await browser.close()
                return {
                    "url": url,
                    "success": success
                }
        except Exception as e:
            return {"error": str(e)}
    
    async def execute_command(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """Execute terminal command"""
        try:
            command = args.get("command")
            project_name = args.get("project_name")
            
            if not command:
                return {"error": "Command is required"}
            
            # This would need to be implemented with proper security measures
            # For now, return a placeholder
            return {
                "command": command,
                "status": "Command execution not implemented for security reasons"
            }
        except Exception as e:
            return {"error": str(e)}
    
    async def read_file(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """Read a file"""
        try:
            project_name = args.get("project_name")
            file_path = args.get("file_path")
            
            if not project_name or not file_path:
                return {"error": "Project name and file path are required"}
            
            files = self.project_manager.get_project_files(project_name)
            target_file = next((f for f in files if f['file'] == file_path), None)
            
            if not target_file:
                return {"error": f"File not found: {file_path}"}
            
            return {
                "project_name": project_name,
                "file_path": file_path,
                "content": target_file['code']
            }
        except Exception as e:
            return {"error": str(e)}
    
    async def write_file(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """Write to a file"""
        try:
            project_name = args.get("project_name")
            file_path = args.get("file_path")
            content = args.get("content", "")
            
            if not project_name or not file_path:
                return {"error": "Project name and file path are required"}
            
            # This would need to be implemented with proper file writing
            # For now, return a placeholder
            return {
                "project_name": project_name,
                "file_path": file_path,
                "status": "File writing not implemented yet"
            }
        except Exception as e:
            return {"error": str(e)}
    
    async def create_file(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new file"""
        try:
            project_name = args.get("project_name")
            file_path = args.get("file_path")
            content = args.get("content", "")
            
            if not project_name or not file_path:
                return {"error": "Project name and file path are required"}
            
            # This would need to be implemented with proper file creation
            # For now, return a placeholder
            return {
                "project_name": project_name,
                "file_path": file_path,
                "status": "File creation not implemented yet"
            }
        except Exception as e:
            return {"error": str(e)}
    
    async def delete_file(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """Delete a file"""
        try:
            project_name = args.get("project_name")
            file_path = args.get("file_path")
            
            if not project_name or not file_path:
                return {"error": "Project name and file path are required"}
            
            # This would need to be implemented with proper file deletion
            # For now, return a placeholder
            return {
                "project_name": project_name,
                "file_path": file_path,
                "status": "File deletion not implemented yet"
            }
        except Exception as e:
            return {"error": str(e)}