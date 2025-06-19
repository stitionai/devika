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

@dataclass
class MCPRequest:
    id: str
    method: str
    params: Dict[str, Any]
    timestamp: datetime

@dataclass
class MCPResponse:
    id: str
    result: Optional[Dict[str, Any]] = None
    error: Optional[Dict[str, Any]] = None

class MCPServer:
    """Model Context Protocol Server for Devika"""
    
    def __init__(self):
        self.config = Config()
        self.logger = Logger()
        self.project_manager = ProjectManager()
        self.tools = {}
        self.handlers = {}
        self.sessions = {}
        
        self._register_core_tools()
        self._register_core_handlers()
    
    def _register_core_tools(self):
        """Register core MCP tools"""
        from .tools import MCPTools
        tools = MCPTools()
        
        self.tools.update({
            "devika/project/create": tools.create_project,
            "devika/project/list": tools.list_projects,
            "devika/project/files": tools.get_project_files,
            "devika/code/analyze": tools.analyze_code,
            "devika/code/generate": tools.generate_code,
            "devika/code/review": tools.review_code,
            "devika/agent/execute": tools.execute_agent,
            "devika/agent/status": tools.get_agent_status,
            "devika/search/web": tools.search_web,
            "devika/browser/navigate": tools.navigate_browser,
            "devika/terminal/execute": tools.execute_command,
            "devika/file/read": tools.read_file,
            "devika/file/write": tools.write_file,
            "devika/file/create": tools.create_file,
            "devika/file/delete": tools.delete_file,
        })
    
    def _register_core_handlers(self):
        """Register core MCP handlers"""
        from .handlers import MCPHandlers
        handlers = MCPHandlers()
        
        self.handlers.update({
            "initialize": handlers.handle_initialize,
            "tools/list": handlers.handle_list_tools,
            "tools/call": handlers.handle_call_tool,
            "resources/list": handlers.handle_list_resources,
            "resources/read": handlers.handle_read_resource,
            "prompts/list": handlers.handle_list_prompts,
            "prompts/get": handlers.handle_get_prompt,
            "logging/setLevel": handlers.handle_set_log_level,
        })
    
    async def handle_request(self, request_data: Dict[str, Any]) -> MCPResponse:
        """Handle incoming MCP request"""
        try:
            request = MCPRequest(
                id=request_data.get("id", ""),
                method=request_data.get("method", ""),
                params=request_data.get("params", {}),
                timestamp=datetime.now()
            )
            
            self.logger.info(f"MCP Request: {request.method}")
            
            if request.method not in self.handlers:
                return MCPResponse(
                    id=request.id,
                    error={
                        "code": -32601,
                        "message": f"Method not found: {request.method}"
                    }
                )
            
            handler = self.handlers[request.method]
            result = await handler(request.params, self)
            
            return MCPResponse(id=request.id, result=result)
            
        except Exception as e:
            self.logger.error(f"MCP Error: {str(e)}")
            return MCPResponse(
                id=request_data.get("id", ""),
                error={
                    "code": -32603,
                    "message": f"Internal error: {str(e)}"
                }
            )
    
    async def call_tool(self, tool_name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Call a registered tool"""
        if tool_name not in self.tools:
            raise ValueError(f"Tool not found: {tool_name}")
        
        tool = self.tools[tool_name]
        return await tool(arguments)
    
    def register_tool(self, name: str, tool_func):
        """Register a new tool"""
        self.tools[name] = tool_func
        self.logger.info(f"Registered MCP tool: {name}")
    
    def register_handler(self, method: str, handler_func):
        """Register a new handler"""
        self.handlers[method] = handler_func
        self.logger.info(f"Registered MCP handler: {method}")
    
    def get_capabilities(self) -> Dict[str, Any]:
        """Get server capabilities"""
        return {
            "tools": {
                "listChanged": True
            },
            "resources": {
                "subscribe": True,
                "listChanged": True
            },
            "prompts": {
                "listChanged": True
            },
            "logging": {}
        }
    
    def get_server_info(self) -> Dict[str, Any]:
        """Get server information"""
        return {
            "name": "devika-mcp-server",
            "version": "1.0.0",
            "description": "Devika AI Software Engineer MCP Server",
            "author": "Devika Team",
            "homepage": "https://github.com/stitionai/devika"
        }