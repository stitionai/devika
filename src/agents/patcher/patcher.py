import os
import time
from typing import Dict, List, Union

from src.state import AgentState
from src.agents import BaseWriterAgent


class Patcher(BaseWriterAgent):
    """Patcher agent class"""

    _prompt = (
        open(
            os.path.join(os.path.dirname(__file__), "prompt.jinja2"),
            "r",
            encoding="utf-8",
        )
        .read()
        .strip()
    )

    def validate_response(self, response: str) -> Union[List[Dict[str, str]], bool]:
        response = response.strip()

        response = response.split("~~~", 1)[1]
        response = response[: response.rfind("~~~")]
        response = response.strip()

        result = []
        current_file = None
        current_code = []
        code_block = False

        for line in response.split("\n"):
            if line.startswith("File: "):
                if current_file and current_code:
                    result.append(
                        {"file": current_file, "code": "\n".join(current_code)}
                    )
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

    def emulate_code_writing(self, code_set: list, project_name: str):
        for file in code_set:
            file = file["file"]
            code = file["code"]

            new_state = AgentState().new_state()
            new_state["internal_monologue"] = "Writing code..."
            new_state["terminal_session"]["title"] = f"Editing {file}"
            new_state["terminal_session"]["command"] = f"vim {file}"
            new_state["terminal_session"]["output"] = code
            AgentState().add_to_current_state(project_name, new_state)
            time.sleep(1)

    def execute(
        self,
        conversation: str,
        code_markdown: str,
        commands: list,
        error: str,
        system_os: dict,
        project_name: str,
    ) -> str:
        prompt = self.render(
            conversation=conversation,
            code=code_markdown,
            commands=commands,
            error=error,
            system_os=system_os,
        )
        response = self.llm.inference(prompt, project_name)

        valid_response = self.validate_response(response)

        while not valid_response:
            print("Invalid response from the model, trying again...")
            return self.execute(
                conversation, code_markdown, commands, error, system_os, project_name
            )

        self.emulate_code_writing(valid_response, project_name)

        return valid_response
