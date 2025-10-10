"""Tool schemas for Claude 3 function calling.

This module defines the tool schemas for Claude 3's function calling capabilities.
Each tool follows Claude's function calling schema format.
"""

from typing import Dict, List, Optional
from dataclasses import dataclass


@dataclass
class ToolParameter:
    """Parameter definition for a tool."""
    type: str
    description: str
    enum: Optional[List[str]] = None
    required: bool = True


@dataclass
class Tool:
    """Tool definition following Claude's schema."""
    name: str
    description: str
    parameters: Dict[str, ToolParameter]
    required: List[str]


# Core tool definitions
BROWSE_TOOL = Tool(
    name="browse_web",
    description="Browse a web page and extract its content",
    parameters={
        "url": ToolParameter(
            type="string",
            description="The URL to browse"
        )
    },
    required=["url"]
)

READ_FILE_TOOL = Tool(
    name="read_file",
    description="Read the contents of a file",
    parameters={
        "path": ToolParameter(
            type="string",
            description="The path to the file to read"
        )
    },
    required=["path"]
)

WRITE_FILE_TOOL = Tool(
    name="write_file",
    description="Write content to a file",
    parameters={
        "path": ToolParameter(
            type="string",
            description="The path to write the file to"
        ),
        "content": ToolParameter(
            type="string",
            description="The content to write to the file"
        )
    },
    required=["path", "content"]
)

RUN_CODE_TOOL = Tool(
    name="run_code",
    description="Execute code in a sandboxed environment",
    parameters={
        "code": ToolParameter(
            type="string",
            description="The code to execute"
        ),
        "language": ToolParameter(
            type="string",
            description="The programming language",
            enum=["python", "javascript", "bash"]
        )
    },
    required=["code", "language"]
)

# List of all available tools
AVAILABLE_TOOLS = [
    BROWSE_TOOL,
    READ_FILE_TOOL,
    WRITE_FILE_TOOL,
    RUN_CODE_TOOL
]
