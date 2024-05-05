import time
import json
import os
import subprocess

from jinja2 import Environment, BaseLoader

from src.agents.patcher import Patcher

from src.llm import LLM
from src.state import AgentState
from src.project import ProjectManager
from src.services.utils import retry_wrapper, validate_responses

PROMPT = open("src/agents/runner/prompt.jinja2", "r").read().strip()
RERUNNER_PROMPT = open("src/agents/runner/rerunner.jinja2", "r").read().strip()

class Runner:
    def __init__(self, base_model: str):
        self.base_model = base_model
        self.llm = LLM(model_id=base_model)

    def render(
        self,
        conversation: str,
        code_markdown: str,
        system_os: str
    ) -> str:
        env = Environment(loader=BaseLoader())
        template = env.from_string(PROMPT)
        return template.render(
            conversation=conversation,
            code_markdown=code_markdown,
            system_os=system_os,
        )

    def render_rerunner(
        self,
        conversation: str,
        code_markdown: str,
        system_os: str,
        commands: list,
        error: str
    ):
        env = Environment(loader=BaseLoader())
        template = env.from_string(RERUNNER_PROMPT)
        return template.render(
            conversation=conversation,
            code_markdown=code_markdown,
            system_os=system_os,
            commands=commands,
            error=error
        )

    @validate_responses
    def validate_response(self, response: str):
        if "commands" not in response:
            return False
        else:
            return response["commands"]
    
    @validate_responses
    def validate_rerunner_response(self, response: str):
        if "action" not in response and "response" not in response:
            return False
        else:
            return response

    @retry_wrapper
    def run_code(
        self,
        commands: list,
        project_path: str,
        project_name: str,
        conversation: list,
        code_markdown: str,
        system_os: str
    ):  
        retries = 0
        
        for command in commands:
            command_set = command.split(" ")
            command_failed = False
            
            process = subprocess.run(
                command_set,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                cwd=project_path
            )
            command_output = process.stdout.decode('utf-8')
            command_failed = process.returncode != 0
            
            new_state = AgentState().new_state()
            new_state["internal_monologue"] = "Running code..."
            new_state["terminal_session"]["title"] = "Terminal"
            new_state["terminal_session"]["command"] = command
            new_state["terminal_session"]["output"] = command_output
            AgentState().add_to_current_state(project_name, new_state)
            time.sleep(1)
            
            while command_failed and retries < 2:
                new_state = AgentState().new_state()
                new_state["internal_monologue"] = "Oh seems like there is some error... :("
                new_state["terminal_session"]["title"] = "Terminal"
                new_state["terminal_session"]["command"] = command
                new_state["terminal_session"]["output"] = command_output
                AgentState().add_to_current_state(project_name, new_state)
                time.sleep(1)
                
                prompt = self.render_rerunner(
                    conversation=conversation,
                    code_markdown=code_markdown,
                    system_os=system_os,
                    commands=commands,
                    error=command_output
                )
                
                response = self.llm.inference(prompt, project_name)
                
                valid_response = self.validate_rerunner_response(response)
                
                if not valid_response:
                    return False
                
                action = valid_response["action"]
                
                if action == "command":
                    command = valid_response["command"]
                    response = valid_response["response"]
                    
                    ProjectManager().add_message_from_devika(project_name, response)
                    
                    command_set = command.split(" ")
                    command_failed = False
                    
                    process = subprocess.run(
                        command_set,
                        stdout=subprocess.PIPE,
                        stderr=subprocess.PIPE,
                        cwd=project_path
                    )
                    command_output = process.stdout.decode('utf-8')
                    command_failed = process.returncode != 0
                    
                    new_state = AgentState().new_state()
                    new_state["internal_monologue"] = "Running code..."
                    new_state["terminal_session"]["title"] = "Terminal"
                    new_state["terminal_session"]["command"] = command
                    new_state["terminal_session"]["output"] = command_output
                    AgentState().add_to_current_state(project_name, new_state)
                    time.sleep(1)
                    
                    if command_failed:
                        retries += 1
                    else:
                        break
                elif action == "patch":
                    response = valid_response["response"]
                    
                    ProjectManager().add_message_from_devika(project_name, response)
                    
                    code = Patcher(base_model=self.base_model).execute(
                        conversation=conversation,
                        code_markdown=code_markdown,
                        commands=commands,
                        error=command_output,
                        system_os=system_os,
                        project_name=project_name
                    )
                    
                    Patcher(base_model=self.base_model).save_code_to_project(code, project_name)
                    
                    command_set = command.split(" ")
                    command_failed = False
                    
                    process = subprocess.run(
                        command_set,
                        stdout=subprocess.PIPE,
                        stderr=subprocess.PIPE,
                        cwd=project_path
                    )
                    command_output = process.stdout.decode('utf-8')
                    command_failed = process.returncode != 0
                    
                    new_state = AgentState().new_state()
                    new_state["internal_monologue"] = "Running code..."
                    new_state["terminal_session"]["title"] = "Terminal"
                    new_state["terminal_session"]["command"] = command
                    new_state["terminal_session"]["output"] = command_output
                    AgentState().add_to_current_state(project_name, new_state)
                    time.sleep(1)
                    
                    if command_failed:
                        retries += 1
                    else:
                        break

    @retry_wrapper
    def execute(
        self,
        conversation: list,
        code_markdown: str,
        os_system: str,
        project_path: str,
        project_name: str
    ) -> str:
        prompt = self.render(conversation, code_markdown, os_system)
        response = self.llm.inference(prompt, project_name)
        
        valid_response = self.validate_response(response)
        
        self.run_code(
            valid_response,
            project_path,
            project_name,
            conversation,
            code_markdown,
            os_system
        )

        return valid_response