import os
import time

from jinja2 import Environment, BaseLoader
from typing import List, Dict, Union

from src.config import Config
from src.llm import LLM
from src.state import AgentState
from src.services.utils import retry_wrapper
from src.socket_instance import emit_agent

PROMPT = open("src/agents/feature/prompt.jinja2", "r").read().strip()


class Feature:
    def __init__(self, base_model: str):
        config = Config()
        self.project_dir = config.get_projects_dir()
        
        self.llm = LLM(model_id=base_model)

    def render(
        self,
        conversation: list,
        code_markdown: str,
        system_os: str
    ) -> str:
        env = Environment(loader=BaseLoader())
        template = env.from_string(PROMPT)
        return template.render(
            conversation=conversation,
            code_markdown=code_markdown,
            system_os=system_os
        )

    def validate_response(self, response: str) -> Union[List[Dict[str, str]], bool]:
        response = response.strip()

        response = response.split("~~~", 1)[1]
        response = response[:response.rfind("~~~")]
        response = response.strip()

        result = []
        current_file = None
        current_code = []
        code_block = False

        for line in response.split("\n"):
            if line.startswith("File: "):
                if current_file and current_code:
                    result.append({"file": current_file, "code": "\n".join(current_code)})
                current_file = line.split("`")[1].strip()
                current_code = []
                code_block = False
            elif line.startswith("```"):
                code_block = not code_block
            else:
                current_code.append(line)

        if current_file and current_code:
            result.append({"file": current_file, "code": "\n".join(current_code)})

        return result

    def save_code_to_project(self, response: List[Dict[str, str]], project_name: str):
        file_path_dir = None
        project_name = project_name.lower().replace(" ", "-")

        for file in response:
            file_path = os.path.join(self.project_dir, project_name, file['file'])
            file_path_dir = os.path.dirname(file_path)
            os.makedirs(file_path_dir, exist_ok=True)
    
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(file["code"])
        
        return file_path_dir

    def get_project_path(self, project_name: str):
        project_name = project_name.lower().replace(" ", "-")
        return f"{self.project_dir}/{project_name}"

    def response_to_markdown_prompt(self, response: List[Dict[str, str]]) -> str:
        response = "\n".join([f"File: `{file['file']}`:\n```\n{file['code']}\n```" for file in response])
        return f"~~~\n{response}\n~~~"

    def emulate_code_writing(self, code_set: list, project_name: str):
        files = []
        for file in code_set:
            filename = file["file"]
            code = file["code"]

            new_state = AgentState().new_state()
            new_state["internal_monologue"] = "Writing code..."
            new_state["terminal_session"]["title"] = f"Editing {filename}"
            new_state["terminal_session"]["command"] = f"vim {filename}"
            new_state["terminal_session"]["output"] = code
            files.append({
                "file": filename,
                "code": code,
            })
            AgentState().add_to_current_state(project_name, new_state)
            time.sleep(1)
        emit_agent("code", {
            "files": files,
            "from": "feature"
        })

    @retry_wrapper
    def execute(
        self,
        conversation: list,
        code_markdown: str,
        system_os: str,
        project_name: str
    ) -> str:
        prompt = self.render(conversation, code_markdown, system_os)
        response = self.llm.inference(prompt, project_name)
        
        valid_response = self.validate_response(response)
        
        if not valid_response:
            return False
        
        self.emulate_code_writing(valid_response, project_name)

        return valid_response
