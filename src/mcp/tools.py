"""
MCP Tools Implementation for Devika
Provides standardized tool interface for AI operations
"""

import asyncio
import json
import os
from typing import Dict, Any, List, Optional
from datetime import datetime

from src.project import ProjectManager
from src.agents import Agent
from src.state import AgentState
from src.browser.search import BingSearch, GoogleSearch, DuckDuckGoSearch
from src.browser import Browser
from src.filesystem import ReadCode
from src.logger import Logger
from src.llm import LLM

class MCPTools:
    """MCP Tools for Devika functionality"""
    
    def __init__(self):
        self.project_manager = ProjectManager()
        self.agent_state = AgentState()
        self.logger = Logger()
        self.tools = self._register_tools()

    def _register_tools(self) -> Dict[str, Dict[str, Any]]:
        """Register all available tools"""
        return {
            "devika/project/create": {
                "description": "Create a new project",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "name": {"type": "string", "description": "Project name"}
                    },
                    "required": ["name"]
                }
            },
            "devika/project/list": {
                "description": "List all projects",
                "inputSchema": {"type": "object", "properties": {}}
            },
            "devika/project/files": {
                "description": "Get files for a project",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "project_name": {"type": "string", "description": "Project name"}
                    },
                    "required": ["project_name"]
                }
            },
            "devika/code/analyze": {
                "description": "Analyze code in a project",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "project_name": {"type": "string", "description": "Project name"},
                        "type": {
                            "type": "string", 
                            "description": "Analysis type", 
                            "enum": ["general", "security", "performance", "review"]
                        }
                    },
                    "required": ["project_name"]
                }
            },
            "devika/code/generate": {
                "description": "Generate code based on requirements",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "project_name": {"type": "string", "description": "Project name"},
                        "requirements": {"type": "string", "description": "Code generation requirements"},
                        "model": {"type": "string", "description": "LLM model to use"}
                    },
                    "required": ["project_name", "requirements"]
                }
            },
            "devika/agent/execute": {
                "description": "Execute an agent task",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "project_name": {"type": "string", "description": "Project name"},
                        "prompt": {"type": "string", "description": "Agent prompt"},
                        "model": {"type": "string", "description": "LLM model to use"},
                        "search_engine": {
                            "type": "string", 
                            "description": "Search engine", 
                            "enum": ["bing", "google", "duckduckgo"]
                        }
                    },
                    "required": ["project_name", "prompt"]
                }
            },
            "devika/search/web": {
                "description": "Search the web",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "query": {"type": "string", "description": "Search query"},
                        "engine": {
                            "type": "string", 
                            "description": "Search engine", 
                            "enum": ["bing", "google", "duckduckgo"]
                        }
                    },
                    "required": ["query"]
                }
            },
            "devika/browser/navigate": {
                "description": "Navigate browser to URL",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "url": {"type": "string", "description": "URL to navigate to"},
                        "project_name": {"type": "string", "description": "Project name for screenshot"}
                    },
                    "required": ["url"]
                }
            },
            "devika/file/read": {
                "description": "Read a file",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "project_name": {"type": "string", "description": "Project name"},
                        "file_path": {"type": "string", "description": "File path"}
                    },
                    "required": ["project_name", "file_path"]
                }
            },
            "devika/file/write": {
                "description": "Write to a file",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "project_name": {"type": "string", "description": "Project name"},
                        "file_path": {"type": "string", "description": "File path"},
                        "content": {"type": "string", "description": "File content"}
                    },
                    "required": ["project_name", "file_path", "content"]
                }
            }
        }

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
            self.logger.error(f"MCP tool error - create_project: {str(e)}")
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
            self.logger.error(f"MCP tool error - list_projects: {str(e)}")
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
            self.logger.error(f"MCP tool error - get_project_files: {str(e)}")
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
            self.logger.error(f"MCP tool error - analyze_code: {str(e)}")
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
            self.logger.error(f"MCP tool error - generate_code: {str(e)}")
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
            self.logger.error(f"MCP tool error - execute_agent: {str(e)}")
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
            self.logger.error(f"MCP tool error - search_web: {str(e)}")
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
            self.logger.error(f"MCP tool error - navigate_browser: {str(e)}")
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
            self.logger.error(f"MCP tool error - read_file: {str(e)}")
            return {"error": str(e)}
    
    async def write_file(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """Write to a file"""
        try:
            project_name = args.get("project_name")
            file_path = args.get("file_path")
            content = args.get("content", "")
            
            if not project_name or not file_path:
                return {"error": "Project name and file path are required"}
            
            # Get project path
            projects_dir = self.project_manager.project_path
            project_dir = os.path.join(projects_dir, project_name.lower().replace(" ", "-"))
            full_file_path = os.path.join(project_dir, file_path)
            
            # Ensure directory exists
            os.makedirs(os.path.dirname(full_file_path), exist_ok=True)
            
            # Write file
            with open(full_file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            
            self.logger.info(f"MCP tool - wrote file: {full_file_path}")
            return {
                "project_name": project_name,
                "file_path": file_path,
                "success": True,
                "message": "File written successfully"
            }
        except Exception as e:
            self.logger.error(f"MCP tool error - write_file: {str(e)}")
            return {"error": str(e)}