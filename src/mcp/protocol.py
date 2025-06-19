"""
MCP Protocol Implementation for Devika
Provides standardized communication interface for AI agents
"""

import json
import asyncio
from typing import Dict, Any, List, Optional, Union
from dataclasses import dataclass, asdict
from datetime import datetime
from enum import Enum

class MessageType(Enum):
    REQUEST = "request"
    RESPONSE = "response"
    NOTIFICATION = "notification"

class ErrorCode(Enum):
    PARSE_ERROR = -32700
    INVALID_REQUEST = -32600
    METHOD_NOT_FOUND = -32601
    INVALID_PARAMS = -32602
    INTERNAL_ERROR = -32603

@dataclass
class MCPMessage:
    jsonrpc: str = "2.0"
    id: Optional[Union[str, int]] = None
    method: Optional[str] = None
    params: Optional[Dict[str, Any]] = None
    result: Optional[Any] = None
    error: Optional[Dict[str, Any]] = None

    def to_dict(self) -> Dict[str, Any]:
        return {k: v for k, v in asdict(self).items() if v is not None}

@dataclass
class MCPError:
    code: int
    message: str
    data: Optional[Any] = None

    def to_dict(self) -> Dict[str, Any]:
        result = {"code": self.code, "message": self.message}
        if self.data is not None:
            result["data"] = self.data
        return result

class MCPProtocol:
    """MCP Protocol handler for Devika"""
    
    def __init__(self):
        self.handlers = {}
        self.capabilities = {
            "tools": {"listChanged": True},
            "resources": {"subscribe": True, "listChanged": True},
            "prompts": {"listChanged": True},
            "logging": {}
        }
        
        self.server_info = {
            "name": "devika-mcp-server",
            "version": "1.0.0",
            "description": "Devika AI Software Engineer MCP Server",
            "author": "Devika Team",
            "homepage": "https://github.com/stitionai/devika"
        }

    def register_handler(self, method: str, handler):
        """Register a method handler"""
        self.handlers[method] = handler

    async def handle_message(self, message_data: Dict[str, Any]) -> MCPMessage:
        """Handle incoming MCP message"""
        try:
            # Validate message format
            if not isinstance(message_data, dict):
                return self._create_error_response(
                    None, ErrorCode.PARSE_ERROR, "Invalid JSON format"
                )

            if message_data.get("jsonrpc") != "2.0":
                return self._create_error_response(
                    message_data.get("id"), ErrorCode.INVALID_REQUEST, "Invalid JSON-RPC version"
                )

            method = message_data.get("method")
            if not method:
                return self._create_error_response(
                    message_data.get("id"), ErrorCode.INVALID_REQUEST, "Missing method"
                )

            # Check if handler exists
            if method not in self.handlers:
                return self._create_error_response(
                    message_data.get("id"), ErrorCode.METHOD_NOT_FOUND, f"Method '{method}' not found"
                )

            # Execute handler
            handler = self.handlers[method]
            params = message_data.get("params", {})
            
            try:
                result = await handler(params)
                return MCPMessage(
                    id=message_data.get("id"),
                    result=result
                )
            except Exception as e:
                return self._create_error_response(
                    message_data.get("id"), ErrorCode.INTERNAL_ERROR, str(e)
                )

        except Exception as e:
            return self._create_error_response(
                None, ErrorCode.PARSE_ERROR, f"Parse error: {str(e)}"
            )

    def _create_error_response(self, request_id: Optional[Union[str, int]], 
                             error_code: ErrorCode, message: str) -> MCPMessage:
        """Create an error response"""
        return MCPMessage(
            id=request_id,
            error=MCPError(code=error_code.value, message=message).to_dict()
        )

    def get_capabilities(self) -> Dict[str, Any]:
        """Get server capabilities"""
        return self.capabilities

    def get_server_info(self) -> Dict[str, Any]:
        """Get server information"""
        return self.server_info