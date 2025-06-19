from typing import Dict, Any, List
from datetime import datetime

class MCPHandlers:
    """MCP Protocol Handlers"""
    
    async def handle_initialize(self, params: Dict[str, Any], server) -> Dict[str, Any]:
        """Handle initialization request"""
        return {
            "protocolVersion": "2024-11-05",
            "capabilities": server.get_capabilities(),
            "serverInfo": server.get_server_info()
        }
    
    async def handle_list_tools(self, params: Dict[str, Any], server) -> Dict[str, Any]:
        """Handle tools list request"""
        tools = []
        
        for tool_name in server.tools.keys():
            # Extract tool info from name and create description
            parts = tool_name.split("/")
            category = parts[1] if len(parts) > 1 else "general"
            action = parts[2] if len(parts) > 2 else parts[-1]
            
            tools.append({
                "name": tool_name,
                "description": f"{category.title()} tool: {action.replace('_', ' ').title()}",
                "inputSchema": {
                    "type": "object",
                    "properties": self._get_tool_schema(tool_name),
                    "required": self._get_required_params(tool_name)
                }
            })
        
        return {"tools": tools}
    
    async def handle_call_tool(self, params: Dict[str, Any], server) -> Dict[str, Any]:
        """Handle tool call request"""
        tool_name = params.get("name")
        arguments = params.get("arguments", {})
        
        if not tool_name:
            raise ValueError("Tool name is required")
        
        result = await server.call_tool(tool_name, arguments)
        
        return {
            "content": [
                {
                    "type": "text",
                    "text": str(result)
                }
            ]
        }
    
    async def handle_list_resources(self, params: Dict[str, Any], server) -> Dict[str, Any]:
        """Handle resources list request"""
        resources = [
            {
                "uri": "devika://projects",
                "name": "Projects",
                "description": "List of all Devika projects",
                "mimeType": "application/json"
            },
            {
                "uri": "devika://agent-state",
                "name": "Agent State",
                "description": "Current agent state and status",
                "mimeType": "application/json"
            },
            {
                "uri": "devika://logs",
                "name": "System Logs",
                "description": "Devika system logs",
                "mimeType": "text/plain"
            }
        ]
        
        return {"resources": resources}
    
    async def handle_read_resource(self, params: Dict[str, Any], server) -> Dict[str, Any]:
        """Handle resource read request"""
        uri = params.get("uri")
        
        if not uri:
            raise ValueError("Resource URI is required")
        
        if uri == "devika://projects":
            projects = server.project_manager.get_project_list()
            content = {
                "projects": projects,
                "count": len(projects),
                "timestamp": datetime.now().isoformat()
            }
        elif uri == "devika://agent-state":
            # Get agent state for all projects
            content = {
                "agent_states": {},
                "timestamp": datetime.now().isoformat()
            }
        elif uri == "devika://logs":
            content = server.logger.read_log_file()
        else:
            raise ValueError(f"Unknown resource URI: {uri}")
        
        return {
            "contents": [
                {
                    "uri": uri,
                    "mimeType": "application/json" if uri != "devika://logs" else "text/plain",
                    "text": str(content)
                }
            ]
        }
    
    async def handle_list_prompts(self, params: Dict[str, Any], server) -> Dict[str, Any]:
        """Handle prompts list request"""
        prompts = [
            {
                "name": "devika/code-review",
                "description": "Perform a comprehensive code review",
                "arguments": [
                    {
                        "name": "project_name",
                        "description": "Name of the project to review",
                        "required": True
                    },
                    {
                        "name": "review_type",
                        "description": "Type of review (comprehensive, security, performance)",
                        "required": False
                    }
                ]
            },
            {
                "name": "devika/generate-code",
                "description": "Generate code based on requirements",
                "arguments": [
                    {
                        "name": "project_name",
                        "description": "Name of the project",
                        "required": True
                    },
                    {
                        "name": "requirements",
                        "description": "Code generation requirements",
                        "required": True
                    },
                    {
                        "name": "model",
                        "description": "LLM model to use",
                        "required": False
                    }
                ]
            },
            {
                "name": "devika/analyze-project",
                "description": "Analyze a project comprehensively",
                "arguments": [
                    {
                        "name": "project_name",
                        "description": "Name of the project to analyze",
                        "required": True
                    },
                    {
                        "name": "analysis_type",
                        "description": "Type of analysis (security, performance, general)",
                        "required": False
                    }
                ]
            }
        ]
        
        return {"prompts": prompts}
    
    async def handle_get_prompt(self, params: Dict[str, Any], server) -> Dict[str, Any]:
        """Handle prompt get request"""
        name = params.get("name")
        arguments = params.get("arguments", {})
        
        if not name:
            raise ValueError("Prompt name is required")
        
        if name == "devika/code-review":
            project_name = arguments.get("project_name", "")
            review_type = arguments.get("review_type", "comprehensive")
            
            prompt = f"""Please perform a {review_type} code review for the project '{project_name}'.

Focus on:
- Code quality and best practices
- Security vulnerabilities
- Performance optimizations
- Architecture and design patterns
- Documentation and maintainability

Provide detailed feedback with specific recommendations for improvement."""
            
        elif name == "devika/generate-code":
            project_name = arguments.get("project_name", "")
            requirements = arguments.get("requirements", "")
            
            prompt = f"""Generate code for the project '{project_name}' based on the following requirements:

{requirements}

Please ensure the code:
- Follows best practices and coding standards
- Is well-documented and maintainable
- Includes proper error handling
- Is secure and performant
- Follows the project's existing architecture"""
            
        elif name == "devika/analyze-project":
            project_name = arguments.get("project_name", "")
            analysis_type = arguments.get("analysis_type", "general")
            
            prompt = f"""Perform a {analysis_type} analysis of the project '{project_name}'.

Please analyze:
- Code structure and organization
- Dependencies and their security status
- Performance bottlenecks
- Security vulnerabilities
- Code quality metrics
- Potential improvements

Provide actionable recommendations for each area."""
            
        else:
            raise ValueError(f"Unknown prompt: {name}")
        
        return {
            "description": f"Generated prompt for {name}",
            "messages": [
                {
                    "role": "user",
                    "content": {
                        "type": "text",
                        "text": prompt
                    }
                }
            ]
        }
    
    async def handle_set_log_level(self, params: Dict[str, Any], server) -> Dict[str, Any]:
        """Handle log level setting"""
        level = params.get("level", "INFO")
        
        # Set log level (implementation would depend on logging setup)
        server.logger.info(f"Log level set to: {level}")
        
        return {"success": True, "level": level}
    
    def _get_tool_schema(self, tool_name: str) -> Dict[str, Any]:
        """Get schema for tool parameters"""
        schemas = {
            "devika/project/create": {
                "name": {"type": "string", "description": "Project name"}
            },
            "devika/project/list": {},
            "devika/project/files": {
                "project_name": {"type": "string", "description": "Project name"}
            },
            "devika/code/analyze": {
                "project_name": {"type": "string", "description": "Project name"},
                "type": {"type": "string", "description": "Analysis type", "enum": ["general", "security", "performance", "review"]}
            },
            "devika/code/generate": {
                "project_name": {"type": "string", "description": "Project name"},
                "requirements": {"type": "string", "description": "Code generation requirements"},
                "model": {"type": "string", "description": "LLM model to use"}
            },
            "devika/code/review": {
                "project_name": {"type": "string", "description": "Project name"},
                "review_type": {"type": "string", "description": "Review type", "enum": ["comprehensive", "security", "performance"]}
            },
            "devika/agent/execute": {
                "project_name": {"type": "string", "description": "Project name"},
                "prompt": {"type": "string", "description": "Agent prompt"},
                "model": {"type": "string", "description": "LLM model to use"},
                "search_engine": {"type": "string", "description": "Search engine", "enum": ["bing", "google", "duckduckgo"]}
            },
            "devika/agent/status": {
                "project_name": {"type": "string", "description": "Project name"}
            },
            "devika/search/web": {
                "query": {"type": "string", "description": "Search query"},
                "engine": {"type": "string", "description": "Search engine", "enum": ["bing", "google", "duckduckgo"]}
            },
            "devika/browser/navigate": {
                "url": {"type": "string", "description": "URL to navigate to"},
                "project_name": {"type": "string", "description": "Project name for screenshot"}
            },
            "devika/terminal/execute": {
                "command": {"type": "string", "description": "Command to execute"},
                "project_name": {"type": "string", "description": "Project name"}
            },
            "devika/file/read": {
                "project_name": {"type": "string", "description": "Project name"},
                "file_path": {"type": "string", "description": "File path"}
            },
            "devika/file/write": {
                "project_name": {"type": "string", "description": "Project name"},
                "file_path": {"type": "string", "description": "File path"},
                "content": {"type": "string", "description": "File content"}
            },
            "devika/file/create": {
                "project_name": {"type": "string", "description": "Project name"},
                "file_path": {"type": "string", "description": "File path"},
                "content": {"type": "string", "description": "File content"}
            },
            "devika/file/delete": {
                "project_name": {"type": "string", "description": "Project name"},
                "file_path": {"type": "string", "description": "File path"}
            }
        }
        
        return schemas.get(tool_name, {})
    
    def _get_required_params(self, tool_name: str) -> List[str]:
        """Get required parameters for tool"""
        required = {
            "devika/project/create": ["name"],
            "devika/project/list": [],
            "devika/project/files": ["project_name"],
            "devika/code/analyze": ["project_name"],
            "devika/code/generate": ["project_name", "requirements"],
            "devika/code/review": ["project_name"],
            "devika/agent/execute": ["project_name", "prompt"],
            "devika/agent/status": ["project_name"],
            "devika/search/web": ["query"],
            "devika/browser/navigate": ["url"],
            "devika/terminal/execute": ["command"],
            "devika/file/read": ["project_name", "file_path"],
            "devika/file/write": ["project_name", "file_path"],
            "devika/file/create": ["project_name", "file_path"],
            "devika/file/delete": ["project_name", "file_path"]
        }
        
        return required.get(tool_name, [])