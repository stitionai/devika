import os
import time
import logging
from contextlib import contextmanager
from typing import List, Dict, Union

from jinja2 import Environment, BaseLoader

from src.config import Config
from src.llm import LLM
from src.state import AgentState

# Load the prompt template from the file
PROMPT_TEMPLATE_PATH = "src/agents/feature/prompt.jinja2"
PROMPT_TEMPLATE_CONTENTS = open(PROMPT_TEMPLATE_PATH, "r").read().strip()


class Feature:
    def __init__(self, base_model: str):
        # Initialize Feature with the specified base model
        self.llm = LLM(model_id=base_model)
        
        # Load the Jinja2 template environment
        self.env = Environment(loader=BaseLoader())
        
        # Compile the prompt template
        self.template = self.env.from_string(PROMPT_TEMPLATE_CONTENTS)
        
        # Get the project directory from configuration
        config = Config()
        self.project_dir = config.get_projects_dir()
        
        # Set up logging
        self.logger = logging.getLogger(__name__)

    def render(
        self,
        conversation: list,
        code_markdown: str,
        system_os: str
    ) -> str:
        # Render the prompt using the provided parameters
        return self.template.render(
            conversation=conversation,
            code_markdown=code_markdown,
            system_os=system_os
        )

    def validate_response(self, response: str) -> Union[List[Dict[str, str]], bool]:
        # Validate the response received from the model
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

    @contextmanager
    def open_file(self, file_path: str, mode: str = 'w'):
        """Context manager for opening files."""
        with open(file_path, mode) as file:
            yield file

    def save_code_to_project(self, response: List[Dict[str, str]], project_name: str):
    # Save the generated code to the specified project directory
    project_name = project_name.lower().replace(" ", "-")
    project_dir = f"{self.project_dir}/{project_name}"
    os.makedirs(project_dir, exist_ok=True)

    for file in response:
        file_path = os.path.join(project_dir, file['file'])
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        
        with open(file_path, "w") as f:
            f.write(file["code"])

    return project_dir


    def get_project_path(self, project_name: str):
        # Get the path to the specified project directory
        project_name = project_name.lower().replace(" ", "-")
        return f"{self.project_dir}/{project_name}"

    def response_to_markdown_prompt(self, response: List[Dict[str, str]]) -> str:
        # Convert the response containing code snippets to Markdown format
        response = "\n".join([f"File: `{file['file']}`:\n```\n{file['code']}\n```" for file in response])
        return f"~~~\n{response}\n~~~"

    def emulate_code_writing(self, code_set: list, project_name: str):
        # Emulate writing code by updating the agent state
        for file in code_set:
            filename = file["file"]
            code = file["code"]

            new_state = AgentState().new_state()
            new_state["internal_monologue"] = "Writing code..."
            new_state["terminal_session"]["title"] = f"Editing {filename}"
            new_state["terminal_session"]["command"] = f"vim {filename}"
            new_state["terminal_session"]["output"] = code
            AgentState().add_to_current_state(project_name, new_state)
            time.sleep(1)

    def execute(
        self,
        conversation: list,
        code_markdown: str,
        system_os: str,
        project_name: str
    ) -> str:
        # Execute the feature workflow
        prompt = self.render(conversation, code_markdown, system_os)
        response = self.llm.inference(prompt, project_name)
        
        valid_response = self.validate_response(response)
        
        while not valid_response:
            self.logger.warning("Invalid response from the model, trying again...")
            return self.execute(conversation, code_markdown, system_os, project_name)
        
        self.emulate_code_writing(valid_response, project_name)

        return valid_response 
