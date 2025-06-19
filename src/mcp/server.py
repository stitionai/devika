"""
MCP Server Implementation for Devika
Provides standardized communication interface for AI agents
"""

import asyncio
import json
import logging
from typing import Dict, Any, List, Optional
from dataclasses import dataclass
from datetime import datetime

from src.config import Config
from src.logger import Logger
from src.project import ProjectManager
from src.agents import Agent
from src.llm import LLM
from .protocol import MCPMessage, MCPProtocol, ErrorCode

class MCPServer:
    """Model Context Protocol Server for Devika"""
    
    def __init__(self):
        self.config = Config()
        self.logger = Logger()
        self.project_manager = ProjectManager()
        self.protocol = MCPProtocol()
        self.tools = {}
        self.sessions = {}
        
        self._register_core_handlers()
        self._register_tools()
    
    def _register_core_handlers(self):
        """Register core MCP protocol handlers"""
        self.protocol.register_handler("initialize", self._handle_initialize)
        self.protocol.register_handler("tools/list", self._handle_list_tools)
        self.protocol.register_handler("tools/call", self._handle_call_tool)
        self.protocol.register_handler("resources/list", self._handle_list_resources)
        self.protocol.register_handler("resources/read", self._handle_read_resource)
        self.protocol.register_handler("prompts/list", self._handle_list_prompts)
        self.protocol.register_handler("prompts/get", self._handle_get_prompt)
        self.protocol.register_handler("logging/setLevel", self._handle_set_log_level)
    
    def _register_tools(self):
        """Register MCP tools"""
        from .tools import MCPTools
        tools_instance = MCPTools()
        
        # Map tool methods to their API endpoints
        self.tools = {
            "devika/project/create": tools_instance.create_project,
            "devika/project/list": tools_instance.list_projects,
            "devika/project/files": tools_instance.get_project_files,
            "devika/code/analyze": tools_instance.analyze_code,
            "devika/code/generate": tools_instance.generate_code,
            "devika/agent/execute": tools_instance.execute_agent,
            "devika/search/web": tools_instance.search_web,
            "devika/browser/navigate": tools_instance.navigate_browser,
            "devika/file/read": tools_instance.read_file,
            "devika/file/write": tools_instance.write_file
        }
    
    async def handle_request(self, request_data: Dict[str, Any]) -> MCPMessage:
        """Handle incoming MCP request"""
        self.logger.info(f"MCP Request: {json.dumps(request_data)[:200]}...")
        return await self.protocol.handle_message(request_data)
    
    async def _handle_initialize(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle initialization request"""
        return {
            "protocolVersion": "2024-11-05",
            "capabilities": self.protocol.get_capabilities(),
            "serverInfo": self.protocol.get_server_info()
        }
    
    async def _handle_list_tools(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle tools list request"""
        tools_list = []
        
        for tool_name, tool_info in self.protocol.tools.items():
            tools_list.append({
                "name": tool_name,
                "description": tool_info["description"],
                "inputSchema": tool_info["inputSchema"]
            })
        
        return {"tools": tools_list}
    
    async def _handle_call_tool(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle tool call request"""
        tool_name = params.get("name")
        arguments = params.get("arguments", {})
        
        if not tool_name:
            raise ValueError("Tool name is required")
        
        if tool_name not in self.tools:
            raise ValueError(f"Tool not found: {tool_name}")
        
        result = await self.tools[tool_name](arguments)
        
        return {
            "content": [
                {
                    "type": "text",
                    "text": json.dumps(result, indent=2)
                }
            ]
        }
    
    async def _handle_list_resources(self, params: Dict[str, Any]) -> Dict[str, Any]:
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
    
    async def _handle_read_resource(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle resource read request"""
        uri = params.get("uri")
        
        if not uri:
            raise ValueError("Resource URI is required")
        
        if uri == "devika://projects":
            projects = self.project_manager.get_project_list()
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
            content = self.logger.read_log_file()
        else:
            raise ValueError(f"Unknown resource URI: {uri}")
        
        return {
            "contents": [
                {
                    "uri": uri,
                    "mimeType": "application/json" if uri != "devika://logs" else "text/plain",
                    "text": json.dumps(content) if uri != "devika://logs" else content
                }
            ]
        }
    
    async def _handle_list_prompts(self, params: Dict[str, Any]) -> Dict[str, Any]:
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
    
    async def _handle_get_prompt(self, params: Dict[str, Any]) -> Dict[str, Any]:
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
    
    async def _handle_set_log_level(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle log level setting"""
        level = params.get("level", "INFO")
        
        # Set log level (implementation would depend on logging setup)
        self.logger.info(f"Log level set to: {level}")
        
        return {"success": True, "level": level}
    
    def get_capabilities(self) -> Dict[str, Any]:
        """Get server capabilities"""
        return self.protocol.get_capabilities()
    
    def get_server_info(self) -> Dict[str, Any]:
        """Get server information"""
        return self.protocol.get_server_info()