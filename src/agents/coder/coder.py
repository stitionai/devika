import os
import time

from jinja2 import Environment, BaseLoader
from typing import List, Dict, Union

from src.config import Config
from src.llm import LLM
from src.state import AgentState

# Load the template for generating prompts
PROMPT = open("src/agents/coder/prompt.jinja2", "r").read().strip()

class Coder:
    def __init__(self, base_model: str):
        # Initialize Coder class with base model and project directory
        config = Config()
        self.project_dir = config.get_projects_dir()
        self.llm = LLM(model_id=base_model)
        self.env = Environment(loader=BaseLoader())
        self.template = self.env.from_string(PROMPT)

    # Render the prompt using Jinja2 template
    def render(self, step_by_step_plan: str, user_context: str, search_results: dict) -> str:
        return self.template.render(step_by_step_plan=step_by_step_plan, user_context=user_context, search_results=search_results)

    def validate_response(self, response: str) -> Union[List[Dict[str, str]], bool]:
        # Validate the response received from the model
        response = response.strip()
    
        # Check if the response contains the expected delimiter
        if "~~~" not in response:
            self.logger.error("Response format is invalid")
            return False
    
        response = response.split("~~~", 1)[1]
    
        # Check if the response contains any content after splitting
        if not response:
            self.logger.error("Response content is empty")
            return False
    
        response = response[:response.rfind("~~~")]
        response = response.strip()
    
        # Proceed with further processing
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

    

    # Save code snippets to the specified project directory
    def save_code_to_project(self, response: List[Dict[str, str]], project_name: str):
        project_name = project_name.lower().replace(" ", "-")
        file_path_dir = os.path.join(self.project_dir, project_name)

        for file in response:
            file_path = os.path.join(file_path_dir, file['file'])
            os.makedirs(os.path.dirname(file_path), exist_ok=True)
            with open(file_path, "w") as f:
                f.write(file["code"])

        return file_path_dir

    # Convert code snippets to markdown format for display
    def response_to_markdown_prompt(self, response: List[Dict[str, str]]) -> str:
        return "\n".join([f"File: `{file['file']}`:\n```\n{file['code']}\n```" for file in response])

    # Emulate writing code by updating the terminal state
    def emulate_code_writing(self, code_set: list, project_name: str):
        for current_file in code_set:
            file_path = os.path.join(self.project_dir, project_name.lower().replace(" ", "-"), current_file["file"])
            AgentState().update_terminal_state(project_name, f"Editing {file_path}", f"vim {file_path}", current_file["code"])
            time.sleep(2)

    
    # Execute the coding process by rendering the prompt, performing inference, and handling responses
    def execute(self, step_by_step_plan: str, user_context: str, search_results: dict, project_name: str) -> str:
        prompt = self.render(step_by_step_plan, user_context, search_results)
        response = self.llm.inference(prompt, project_name)
        valid_response = self.validate_response(response)
        
        if not valid_response:
            print("Invalid response from the model, trying again...")
            return self.execute(step_by_step_plan, user_context, search_results, project_name)
        
        print(valid_response)
        
        self.emulate_code_writing(valid_response, project_name)
        return valid_response
