import os
import time
import json
from jinja2 import Environment, BaseLoader
from typing import List, Dict, Union
from src.project import ProjectManager
from src.state import AgentState
from src.config import Config
from src.llm import LLM
from src.state import AgentState
from src.agents.researcher import Researcher
from src.agents.formatter import Formatter
from src.browser.search import BingSearch, GoogleSearch, DuckDuckGoSearch
from src.socket_instance import emit_agent
from src.browser import Browser
from src.logger import Logger
import asyncio
from src.services.utils import retry_wrapper

PROMPT = open("src/agents/feature/prompt.jinja2", "r").read().strip()
PLAN_PROMPT = open("src/agents/feature/plan.jinja2", "r").read().strip()

class Feature:
    def __init__(self, base_model: str, search_engine: str):
        config = Config()
        self.project_dir = config.get_projects_dir()
        self.researcher = Researcher(base_model=base_model)
        self.formatter = Formatter(base_model=base_model)
        self.logger = Logger()
        self.engine = search_engine

        self.llm = LLM(model_id=base_model)

    def render(
        self,
        conversation: list,
        code_markdown: str,
        system_os: str,
        search_results: dict,
        user_context: str
    ) -> str:
        env = Environment(loader=BaseLoader())
        template = env.from_string(PROMPT)
        return template.render(
            conversation=conversation,
            code_markdown=code_markdown,
            system_os=system_os,
            search_results=search_results,
            user_context=user_context
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

    def featuer_plan_render(self, conversation: list, code_markdown: str) -> str:
        env = Environment(loader=BaseLoader())
        template = env.from_string(PLAN_PROMPT)
        return template.render(
            conversation=conversation,
            code_markdown=code_markdown
        )

    def parse_response(self, response: str):
        result = {
            "plans": {}
        }

        current_section = None
        current_step = None

        for line in response.split("\n"):
            line = line.strip()

            if line.startswith("Plan:"):
                current_section = "plans"
            elif current_section == "plans":
                if line.startswith("- [ ] Step"):
                    current_step = line.split(":")[0].strip().split(" ")[-1]
                    result["plans"][int(current_step)] = line.split(":", 1)[1].strip()
                elif current_step:
                    result["plans"][int(current_step)] += " " + line

        return result    

    async def open_page(self, project_name, pdf_download_url):
        browser = await Browser().start()

        await browser.go_to(pdf_download_url)
        _, raw = await browser.screenshot(project_name)
        data = await browser.extract_text()
        await browser.close()

        return browser, raw, data


    def search_queries(self, queries: list, project_name: str) -> dict:
        results = {}

        web_search = None

        if self.engine == "bing":
            web_search = BingSearch()
        elif self.engine == "google":
            web_search = GoogleSearch()
        else:
            web_search = DuckDuckGoSearch()

        self.logger.info(f"\nSearch Engine :: {self.engine}")

        for query in queries:
            query = query.strip().lower()   

            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            
            web_search.search(query)

            link = web_search.get_first_link()
            print("\nLink :: ", link, '\n')

            browser, raw, data = loop.run_until_complete(self.open_page(project_name, link))
            emit_agent("screenshot", {"data": raw, "project_name": project_name}, False)
            results[query] = self.formatter.execute(data, project_name)

            self.logger.info(f"got the search results for : {query}")
            # knowledge_base.add_knowledge(tag=query, contents=results[query])
        return results

    @retry_wrapper
    def execute(
        self,
        conversation: list,
        code_markdown: str,
        system_os: str,
        project_name: str
    ) -> str:
        
        new_state = AgentState().new_state()
        new_state["internal_monologue"] = "So I have to implement this new feature..."
        new_state["terminal_session"]["title"] = "Terminal"
        new_state["terminal_session"]["command"] = """echo "Waiting..." """
        new_state["terminal_session"]["output"] = "Waiting..."
        AgentState().add_to_current_state(project_name, new_state)
        time.sleep(1)

        plan_prompt = self.featuer_plan_render(conversation, code_markdown)
        plan = self.llm.inference(plan_prompt, project_name)
        plan_response = self.parse_response(plan)
        plans = plan_response["plans"]
        ProjectManager().add_message_from_devika(project_name, json.dumps(plans, indent=4))

        research = self.researcher.execute(plans, [], project_name=project_name)
        queries = research["queries"]
        queries_combined = ", ".join(queries)
        ask_user = research["ask_user"]

        if (queries and len(queries) > 0) or ask_user != "":
            ProjectManager().add_message_from_devika(
                project_name,
                f"I am browsing the web to research the following queries: {queries_combined}."
                f"\n If I need anything, I will make sure to ask you."
            )
        if not queries and len(queries) == 0:
            ProjectManager().add_message_from_devika(project_name,
                                                         "I think I can proceed without searching the web.")

        ask_user_prompt = "Nothing from the user."

        if ask_user != "" and ask_user is not None:
            ProjectManager().add_message_from_devika(project_name, ask_user)
            AgentState().set_agent_active(project_name, False)
            got_user_query = False

            while not got_user_query:
                self.logger.info("Waiting for user query...")

                latest_message_from_user = ProjectManager().get_latest_message_from_user(project_name)
                validate_last_message_is_from_user = ProjectManager().validate_last_message_is_from_user(
                    project_name)

                if latest_message_from_user and validate_last_message_is_from_user:
                    ask_user_prompt = latest_message_from_user["message"]
                    got_user_query = True
                    ProjectManager().add_message_from_devika(project_name, "Thanks! 🙌")
                time.sleep(5)

        AgentState().set_agent_active(project_name, True)

        if queries and len(queries) > 0:
            search_results = self.search_queries(queries, project_name)
        else:
            search_results = {}

        prompt = self.render(conversation, code_markdown, system_os, search_results, ask_user_prompt)
        response = self.llm.inference(prompt, project_name)
        
        valid_response = self.validate_response(response)
        
        if not valid_response:
            return False
        
        self.emulate_code_writing(valid_response, project_name)

        return valid_response
