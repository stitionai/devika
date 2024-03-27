from jinja2 import Environment, BaseLoader

from src.llm import LLM

PROMPT = open("src/agents/planner/prompt.jinja2").read().strip()

class Planner:
    def __init__(self, base_model: str):
        self.llm = LLM(model_id=base_model)

    def render(self, prompt: str) -> str:
        env = Environment(loader=BaseLoader())
        template = env.from_string(PROMPT)
        return template.render(prompt=prompt)
    
    def validate_response(self, response: str) -> bool:
        return True
    
    def parse_response(self, response: str):
        result = {
            "project": "",
            "reply": "",
            "focus": "",
            "plans": {},
            "summary": ""
        }

        current_section = None
        current_step = None

        for line in response.split("\n"):
            line = line.strip()

            if line.startswith("Project Name:"):
                current_section = "project"
                result["project"] = line.split(":", 1)[1].strip()            
            elif line.startswith("Your Reply to the Human Prompter:"):
                current_section = "reply"
                result["reply"] = line.split(":", 1)[1].strip()
            elif line.startswith("Current Focus:"):
                current_section = "focus"
                result["focus"] = line.split(":", 1)[1].strip()
            elif line.startswith("Plan:"):
                current_section = "plans"
            elif line.startswith("Summary:"):
                current_section = "summary"
                result["summary"] = line.split(":", 1)[1].strip()
            elif current_section == "reply":
                result["reply"] += " " + line
            elif current_section == "focus":
                result["focus"] += " " + line
            elif current_section == "plans":
                if line.startswith("- [ ] Step"):
                    current_step = line.split(":")[0].strip().split(" ")[-1]
                    result["plans"][int(current_step)] = line.split(":", 1)[1].strip()
                elif current_step:
                    result["plans"][int(current_step)] += " " + line
            elif current_section == "summary":
                result["summary"] += " " + line.replace("```", "")

        result["project"] = result["project"].strip()
        result["reply"] = result["reply"].strip()
        result["focus"] = result["focus"].strip()
        result["summary"] = result["summary"].strip()

        return result    

    def execute(self, prompt: str, project_name: str) -> str:
        prompt = self.render(prompt)
        response = self.llm.inference(prompt, project_name)
        return response
