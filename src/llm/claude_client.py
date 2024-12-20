from typing import Optional, List, Dict, Any
from anthropic import Anthropic

from src.config import Config
from src.llm.tools import AVAILABLE_TOOLS, Tool

class Claude:
    def __init__(self):
        config = Config()
        api_key = config.get_claude_api_key()
        self.client = Anthropic(
            api_key=api_key,
        )
        self.tool_schemas = [
            {
                "name": tool.name,
                "description": tool.description,
                "parameters": {
                    "type": "object",
                    "properties": {
                        name: {
                            "type": param.type,
                            "description": param.description,
                            **({"enum": param.enum} if param.enum else {})
                        }
                        for name, param in tool.parameters.items()
                    },
                    "required": tool.required
                }
            }
            for tool in AVAILABLE_TOOLS
        ]

    def inference(
        self,
        model_id: str,
        prompt: str,
        tools: Optional[List[Dict[str, Any]]] = None
    ) -> str:
        kwargs = {
            "max_tokens": 4096,
            "messages": [
                {
                    "role": "user",
                    "content": prompt.strip(),
                }
            ],
            "model": model_id,
            "temperature": 0
        }

        # Add tool schemas for Claude 3 models
        if "claude-3" in model_id:
            kwargs["tools"] = tools or self.tool_schemas

        message = self.client.messages.create(**kwargs)
        return message.content[0].text
