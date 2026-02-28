import json
from jinja2 import Environment, BaseLoader
from src.llm import LLM
from src.services.utils import retry_wrapper, validate_responses

PROMPT = open("src/agents/enhanced_planner/prompt.jinja2", "r").read().strip()

class EnhancedPlanner:
    """Enhanced planner with better reasoning and context awareness"""
    
    def __init__(self, base_model: str):
        self.llm = LLM(model_id=base_model)

    def render(self, prompt: str, context: dict = None) -> str:
        env = Environment(loader=BaseLoader())
        template = env.from_string(PROMPT)
        return template.render(
            prompt=prompt,
            context=context or {}
        )
    
    @validate_responses
    def validate_response(self, response: str):
        required_fields = ["project", "reply", "focus", "plans", "summary", "complexity", "estimated_time", "dependencies"]
        
        for field in required_fields:
            if field not in response:
                return False
        
        return response
    
    def parse_response(self, response: dict):
        """Parse and structure the enhanced planner response"""
        return {
            "project": response.get("project", "").strip(),
            "reply": response.get("reply", "").strip(),
            "focus": response.get("focus", "").strip(),
            "plans": response.get("plans", {}),
            "summary": response.get("summary", "").strip(),
            "complexity": response.get("complexity", "medium"),
            "estimated_time": response.get("estimated_time", "unknown"),
            "dependencies": response.get("dependencies", []),
            "risks": response.get("risks", []),
            "success_criteria": response.get("success_criteria", [])
        }

    @retry_wrapper
    def execute(self, prompt: str, project_name: str, context: dict = None) -> dict:
        rendered_prompt = self.render(prompt, context)
        response = self.llm.inference(rendered_prompt, project_name)
        
        valid_response = self.validate_response(response)
        return self.parse_response(valid_response)