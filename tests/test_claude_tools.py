"""Tests for Claude 3 tool use functionality."""

import pytest
from typing import Dict, Any

from src.llm.tools import (
    Tool,
    ToolParameter,
    BROWSE_TOOL,
    READ_FILE_TOOL,
    WRITE_FILE_TOOL,
    RUN_CODE_TOOL,
    AVAILABLE_TOOLS
)
from src.llm.claude_client import Claude


def test_tool_parameter_creation():
    """Test creating tool parameters with various configurations."""
    param = ToolParameter(
        type="string",
        description="Test parameter",
        enum=["a", "b", "c"],
        required=True
    )
    assert param.type == "string"
    assert param.description == "Test parameter"
    assert param.enum == ["a", "b", "c"]
    assert param.required is True

    # Test without optional fields
    basic_param = ToolParameter(
        type="integer",
        description="Basic parameter"
    )
    assert basic_param.type == "integer"
    assert basic_param.description == "Basic parameter"
    assert basic_param.enum is None
    assert basic_param.required is True


def test_tool_creation():
    """Test creating tools with parameters."""
    tool = Tool(
        name="test_tool",
        description="Test tool",
        parameters={
            "param1": ToolParameter(
                type="string",
                description="Parameter 1"
            )
        },
        required=["param1"]
    )
    assert tool.name == "test_tool"
    assert tool.description == "Test tool"
    assert len(tool.parameters) == 1
    assert "param1" in tool.parameters
    assert tool.required == ["param1"]


def test_browse_tool_schema():
    """Test browse tool schema structure."""
    assert BROWSE_TOOL.name == "browse_web"
    assert "url" in BROWSE_TOOL.parameters
    assert BROWSE_TOOL.parameters["url"].type == "string"
    assert BROWSE_TOOL.required == ["url"]


def test_read_file_tool_schema():
    """Test read file tool schema structure."""
    assert READ_FILE_TOOL.name == "read_file"
    assert "path" in READ_FILE_TOOL.parameters
    assert READ_FILE_TOOL.parameters["path"].type == "string"
    assert READ_FILE_TOOL.required == ["path"]


def test_write_file_tool_schema():
    """Test write file tool schema structure."""
    assert WRITE_FILE_TOOL.name == "write_file"
    assert "path" in WRITE_FILE_TOOL.parameters
    assert "content" in WRITE_FILE_TOOL.parameters
    assert WRITE_FILE_TOOL.required == ["path", "content"]


def test_run_code_tool_schema():
    """Test run code tool schema structure."""
    assert RUN_CODE_TOOL.name == "run_code"
    assert "code" in RUN_CODE_TOOL.parameters
    assert "language" in RUN_CODE_TOOL.parameters
    assert RUN_CODE_TOOL.parameters["language"].enum == ["python", "javascript", "bash"]
    assert RUN_CODE_TOOL.required == ["code", "language"]


def test_claude_client_tool_schemas():
    """Test Claude client tool schema generation."""
    client = Claude()

    # Verify tool schemas are properly formatted for Claude API
    assert len(client.tool_schemas) == len(AVAILABLE_TOOLS)

    # Check schema structure for first tool
    schema = client.tool_schemas[0]
    assert isinstance(schema, dict)
    assert "name" in schema
    assert "description" in schema
    assert "parameters" in schema
    assert schema["parameters"]["type"] == "object"
    assert "properties" in schema["parameters"]
    assert "required" in schema["parameters"]


@pytest.mark.parametrize("model_id,should_have_tools", [
    ("claude-3-opus-20240229", True),
    ("claude-3-sonnet-20240229", True),
    ("claude-2.1", False),
    ("claude-2.0", False),
])
def test_claude_inference_tool_inclusion(model_id: str, should_have_tools: bool):
    """Test tool inclusion in Claude inference based on model."""
    client = Claude()
    prompt = "Test prompt"

    # Mock the create method to capture kwargs
    def mock_create(**kwargs) -> Dict[str, Any]:
        class MockResponse:
            content = [type("Content", (), {"text": "Mock response"})]

        # Verify tools presence based on model
        if should_have_tools:
            assert "tools" in kwargs
            assert isinstance(kwargs["tools"], list)
            assert len(kwargs["tools"]) == len(AVAILABLE_TOOLS)
        else:
            assert "tools" not in kwargs

        return MockResponse()

    # Replace create method with mock
    client.client.messages.create = mock_create

    # Run inference
    client.inference(model_id=model_id, prompt=prompt)
