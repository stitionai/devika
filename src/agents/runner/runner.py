import time
import json
import os
import subprocess
from jinja2 import Environment, BaseLoader
from src.agents.patcher import Patcher
from src.agents.formatter import Formatter
from src.browser.search import DuckDuckGoSearch, BingSearch, GoogleSearch
from src.llm import LLM
from src.state import AgentState
from src.project import ProjectManager
from src.browser import Browser
import asyncio
from src.socket_instance import emit_agent


PROMPT = open("src/agents/runner/prompt.jinja2", "r").read().strip()
RERUNNER_PROMPT = open("src/agents/runner/rerunner.jinja2", "r").read().strip()
ERROR_ANALYZER_PROMPT = open("src/agents/runner/error_analyzer.jinja2", "r").read().strip()

class Runner:
    def __init__(self, base_model: str, search_engine: str):
        self.base_model = base_model
        self.llm = LLM(model_id=base_model)
        self.formatter = Formatter(base_model=base_model)
        self.search_engine = search_engine

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
        error: str,
        error_context: str
    ):
        env = Environment(loader=BaseLoader())
        template = env.from_string(RERUNNER_PROMPT)
        return template.render(
            conversation=conversation,
            code_markdown=code_markdown,
            system_os=system_os,
            commands=commands,
            error=error,
            error_context = error_context
        )
    
    def render_error_analyzer(
        self,
        conversation: str,
        code_markdown: str,
        commands: list,
        system_os: str,
        error: str
    ):
        env = Environment(loader=BaseLoader())
        template = env.from_string(ERROR_ANALYZER_PROMPT)
        return template.render(
            conversation=conversation,
            code_markdown=code_markdown,
            commands=commands,
            system_os=system_os,
            error=error
        )
    
    def validate_error_analyzer_response(self, response: str):
        response = response.strip().replace("```json", "```")
        
        if response.startswith("```") and response.endswith("```"):
            response = response[3:-3].strip()
 
        try:
            response = json.loads(response)
        except Exception as _:
            return False

        if "error" not in response or "need_web" not in response:
            return False
        elif response["need_web"]!="True" and response["need_web"]!="False":
            return False
        else: 
            return response
    
    async def open_page(self, project_name, pdf_download_url):
        browser = await Browser().start()

        await browser.go_to(pdf_download_url)
        _, raw = await browser.screenshot(project_name)
        data = await browser.extract_text()
        await browser.close()

        return browser, raw, data

    def validate_response(self, response: str):
        response = response.strip().replace("```json", "```")
        
        if response.startswith("```") and response.endswith("```"):
            response = response[3:-3].strip()
 
        try:
            response = json.loads(response)
        except Exception as _:
            return False

        if "commands" not in response:
            return False
        else:
            return response["commands"]
        
    def validate_rerunner_response(self, response: str):
        response = response.strip().replace("```json", "```")
        
        if response.startswith("```") and response.endswith("```"):
            response = response[3:-3].strip()
 
        print(response)
 
        try:
            response = json.loads(response)
        except Exception as _:
            return False
        
        print(response)

        if "action" not in response and "response" not in response:
            return False
        else:
            return response

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
            command_error = process.stderr.decode('utf-8')
            command_failed = process.returncode != 0
            
            new_state = AgentState().new_state()
            new_state["internal_monologue"] = "Running code..."
            new_state["terminal_session"]["title"] = "Terminal"
            new_state["terminal_session"]["command"] = command
            new_state["terminal_session"]["output"] = command_output
            AgentState().add_to_current_state(project_name, new_state)
            time.sleep(1)
            
            #Re-runner starts here if there is some error
            while command_failed and retries < 2:
                new_state = AgentState().new_state()
                new_state["internal_monologue"] = "Oh seems like there is some error... :(. Trying to fix it"
                new_state["terminal_session"]["title"] = "Terminal"
                new_state["terminal_session"]["command"] = command
                new_state["terminal_session"]["output"] = command_error
                
                #Error analyzer prompt
                prompt = self.render_error_analyzer(
                    conversation=conversation,
                    code_markdown=code_markdown,
                    system_os=system_os,
                    commands=commands,
                    error=command_error
                )
                response = self.llm.inference(prompt, project_name)
                
                valid_response = self.validate_error_analyzer_response(response)
                while not valid_response:
                    print("Invalid response from the model, trying again...")
                    return self.run_code(
                        commands,
                        project_path,
                        project_name,
                        conversation,
                        code_markdown,
                        system_os
                    )
                    
                response = json.loads(response)
                error = response["error"]
                need_web = response["need_web"]
                main_cause = None
                
                if "main_cause" in response:
                    main_cause = response["main_cause"]
                
                total_error = error
                if main_cause is not None:
                    total_error = error + " " + main_cause
                
                results = {total_error: "Web searching wasn't required for this error."}

                if need_web=="True":
                    ProjectManager().add_message_from_devika(project_name, "I need to search the web to fix the error...")
                    new_state = AgentState().new_state()
                    new_state["internal_monologue"] = "Uh oh, an unseen error. Let's do web search to get it fixed."
                    new_state["terminal_session"]["title"] = "Terminal"
                    new_state["terminal_session"]["command"] = command
                    new_state["terminal_session"]["output"] = command_error
                    AgentState().add_to_current_state(project_name, new_state)
                    time.sleep(1)

                    if main_cause is not None:
                        error = error + " " + main_cause
                    
                    loop = asyncio.new_event_loop()
                    asyncio.set_event_loop(loop)
                    
                    web_search = None

                    if self.search_engine == "duckduckgo":
                        web_search = DuckDuckGoSearch()
                    elif self.search_engine == "bing":
                        web_search = BingSearch()
                    elif self.search_engine == "google":
                        web_search = GoogleSearch()

                    web_search.search(error)
                    link = web_search.get_first_link()
                    browser, raw, error_context = loop.run_until_complete(self.open_page(project_name, link))
                    emit_agent("screenshot", {"data": raw, "project_name": project_name}, False)
                    results[error] = self.formatter.execute(error_context, project_name)
                else:
                    ProjectManager().add_message_from_devika(project_name, "I can resolve this error myself. Let me try...")
                    error = total_error
                    AgentState().add_to_current_state(project_name, new_state)
                    time.sleep(1)
                
                prompt = self.render_rerunner(
                    conversation=conversation,
                    code_markdown=code_markdown,
                    system_os=system_os,
                    commands=commands,
                    error=command_error,
                    error_context = results[error]
                )
                
                response = self.llm.inference(prompt, project_name)
                
                valid_response = self.validate_rerunner_response(response)
                
                while not valid_response:
                    print("Invalid response from the model, trying again...")
                    return self.run_code(
                        commands,
                        project_path,
                        project_name,
                        conversation,
                        code_markdown,
                        system_os
                    )
                
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
                        error=command_error,
                        error_context = results[error],
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
        
        while not valid_response:
            print("Invalid response from the model, trying again...")
            return self.execute(conversation, code_markdown, os_system, project_path, project_name)
        
        print("=====" * 10)
        print(valid_response)
        
        self.run_code(
            valid_response,
            project_path,
            project_name,
            conversation,
            code_markdown,
            os_system
        )

        return valid_response