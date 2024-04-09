import json
import asyncio
from src.llm import LLM
from src.browser.search import DuckDuckGoSearch, BingSearch, GoogleSearch
from src.browser import Browser
from jinja2 import Environment, BaseLoader
from src.state import AgentState
from src.project import ProjectManager
import time 
from src.agents.formatter import Formatter
from src.socket_instance import emit_agent

PROMPT = open("src/agents/error_analyzer/prompt.jinja2", "r").read().strip()

class ErrorAnalyzer:
    def __init__(self, base_model: str, search_engine: str):
        self.base_model = base_model
        self.engine = search_engine
        self.llm = LLM(model_id=base_model)
        self.formatter = Formatter(base_model=base_model)

    def render(
        self,
        conversation: str,
        code_markdown: str,
        commands: list,
        system_os: str,
        error: str
    ):
        env = Environment(loader=BaseLoader())
        template = env.from_string(PROMPT)
        return template.render(
            conversation=conversation,
            code_markdown=code_markdown,
            commands=commands,
            system_os=system_os,
            error=error
        )
    
    def validate(self, response: str):
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

    def execute(
        self,
        conversation: list,
        code_markdown: str,
        commands: list,
        error: str,
        system_os: str,
        project_name: str
    ):  
        prompt = self.render(
            conversation=conversation,
            code_markdown=code_markdown,
            system_os=system_os,
            commands=commands,
            error=error
        )
        response = self.llm.inference(prompt, project_name)

        valid_response = self.validate(response)
        while not valid_response:
            print("Invalid response from the model, trying again...")
            return self.execute(
                conversation,
                code_markdown,
                commands,
                error,
                system_os,
                project_name
            )
        
        response = valid_response
        command_error = error
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
            if commands is not None and len(commands) > 0:
                new_state = AgentState().new_state()
                new_state["internal_monologue"] = "Uh oh, an unseen error. Let's do web search to get it fixed."
                new_state["terminal_session"]["title"] = "Terminal"
                new_state["terminal_session"]["command"] = commands[-1]
                new_state["terminal_session"]["output"] = command_error
                AgentState().add_to_current_state(project_name, new_state)
                time.sleep(1)

            if main_cause is not None:
                error = error + " " + main_cause
            
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            
            web_search = None

            if self.engine == "duckduckgo":
                web_search = DuckDuckGoSearch()
            elif self.engine == "bing":
                web_search = BingSearch()
            elif self.engine == "google":
                web_search = GoogleSearch()

            web_search.search(error)
            link = web_search.get_first_link()
            browser, raw, error_context = loop.run_until_complete(self.open_page(project_name, link))
            emit_agent("screenshot", {"data": raw, "project_name": project_name}, False)
            results[error] = self.formatter.execute(error_context, project_name)
        else:
            if commands is not None and len(commands) > 0:
                new_state = AgentState().new_state()
                new_state["internal_monologue"] = "Oh seems like there is some error... :(. Trying to fix it"
                new_state["terminal_session"]["title"] = "Terminal"
                new_state["terminal_session"]["command"] = commands[-1]
                new_state["terminal_session"]["output"] = error
                AgentState().add_to_current_state(project_name, new_state)
                time.sleep(1)
            
            ProjectManager().add_message_from_devika(project_name, "I can resolve this error myself. Let me try...")
            error = total_error
        
        return results[error]