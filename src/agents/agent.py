from .planner import Planner
from .researcher import Researcher
from .formatter import Formatter
from .coder import Coder
from .action import Action
from .internal_monologue import InternalMonologue
from .answer import Answer
from .runner import Runner
from .feature import Feature
from .patcher import Patcher
from .reporter import Reporter
from .decision import Decision

from src.logger import Logger
from src.project import ProjectManager
from src.state import AgentState

from src.bert.sentence import SentenceBert
from src.memory import KnowledgeBase
from src.browser.search import BingSearch,DuckDuckGoSearch,GoogleSearch
from src.browser import Browser
from src.browser import start_interaction
from src.filesystem import ReadCode
from src.services import Netlify
from src.documenter.pdf import PDF

import json
import time
import platform
import tiktoken

class Agent:
    def __init__(self, base_model: str):
        if not base_model:
            raise ValueError("base_model is required")

        self.logger = Logger()

        """
        Accumulate contextual keywords from chained prompts of all preparation agents
        """
        self.collected_context_keywords = set()
        
        """
        Agents
        """
        self.planner = Planner(base_model=base_model)
        self.researcher = Researcher(base_model=base_model)
        self.formatter = Formatter(base_model=base_model)
        self.coder = Coder(base_model=base_model)
        self.action = Action(base_model=base_model)
        self.internal_monologue = InternalMonologue(base_model=base_model)
        self.answer = Answer(base_model=base_model)
        self.runner = Runner(base_model=base_model)
        self.feature = Feature(base_model=base_model)
        self.patcher = Patcher(base_model=base_model)
        self.reporter = Reporter(base_model=base_model)
        self.decision = Decision(base_model=base_model)

        self.tokenizer = tiktoken.get_encoding("cl100k_base")

    def search_queries(self, queries: list, project_name: str) -> dict:
        results = {}
        
        knowledge_base = KnowledgeBase()
        # web_search = BingSearch()
        # web_search = DuckDuckGoSearch()
        web_search = GoogleSearch()
        browser = Browser()

        for query in queries:
            query = query.strip().lower()
            
            """
            Check if the knowledge base already has the query learned
            """
            # knowledge = knowledge_base.get_knowledge(tag=query)
            # if knowledge:
            #     results[query] = knowledge
            #     continue

            """
            Search for the query and get the first link
            """
            web_search.search(query)
            link = web_search.get_first_link()

            """
            Browse to the link and take a screenshot, then extract the text
            """
            browser.go_to(link)
            browser.screenshot(project_name)

            """
            Formatter Agent is invoked to format and learn from the contents
            """
            results[query] = self.formatter.execute(
                browser.extract_text()
            )
            
            """
            Add the newly acquired data to the knowledge base
            """
            # knowledge_base.add_knowledge(tag=query, contents=results[query])

        return results

    """
    Update the context keywords with the latest sentence/prompt
    """
    def update_contextual_keywords(self, sentence: str):
        keywords = SentenceBert(sentence).extract_keywords()
        
        for keyword in keywords:
            self.collected_context_keywords.add(keyword[0])

        return self.collected_context_keywords

    """
    Decision making Agent
    """
    def make_decision(self, prompt: str, project_name: str) -> str:
        decision = self.decision.execute(prompt)
        
        for item in decision:
            function = item["function"]
            args = item["args"]
            reply = item["reply"]
            
            ProjectManager().add_message_from_devika(project_name, reply)
            
            if function == "git_clone":
                url = args["url"]
                # Implement git clone functionality here
                
            elif function == "generate_pdf_document":
                user_prompt = args["user_prompt"]
                # Call the reporter agent to generate the PDF document
                markdown = self.reporter.execute([user_prompt], "")
                _out_pdf_file = PDF().markdown_to_pdf(markdown, project_name)
                
                project_name_space_url = project_name.replace(" ", "%20")
                pdf_download_url = "http://127.0.0.1:1337/api/download-project-pdf?project_name={}".format(project_name_space_url)
                response = f"I have generated the PDF document. You can download it from here: {pdf_download_url}"
                
                Browser().go_to(pdf_download_url)
                Browser().screenshot(project_name)
                
                ProjectManager().add_message_from_devika(project_name, response)
                
            elif function == "browser_interaction":
                user_prompt = args["user_prompt"]
                # Call the interaction agent to interact with the browser
                start_interaction(self.base_model, user_prompt, project_name)
                
            elif function == "coding_project":
                user_prompt = args["user_prompt"]
                # Call the planner, researcher, coder agents in sequence
                plan = self.planner.execute(user_prompt)
                planner_response = self.planner.parse_response(plan)
                
                research = self.researcher.execute(plan, self.collected_context_keywords)
                search_results = self.search_queries(research["queries"], project_name)
                
                code = self.coder.execute(
                    step_by_step_plan=plan,
                    user_context=research["ask_user"],
                    search_results=search_results,
                    project_name=project_name
                )
                self.coder.save_code_to_project(code, project_name)

    """
    Subsequent flow of execution
    """
    def subsequent_execute(self, prompt: str, project_name: str) -> str:
        AgentState().set_agent_active(project_name, True)
        
        conversation = ProjectManager().get_all_messages_formatted(project_name)
        code_markdown = ReadCode(project_name).code_set_to_markdown()

        response, action = self.action.execute(conversation)
        
        ProjectManager().add_message_from_devika(project_name, response)
        
        print("=====" * 10)
        print(action)
        print("=====" * 10)
        
        if action == "answer":
            response = self.answer.execute(
                conversation=conversation,
                code_markdown=code_markdown
            )
            ProjectManager().add_message_from_devika(project_name, response)
        elif action == "run":
            os_system = platform.platform()
            project_path = ProjectManager().get_project_path(project_name)

            self.runner.execute(
                conversation=conversation,
                code_markdown=code_markdown,
                os_system=os_system,
                project_path=project_path,
                project_name=project_name
            )
        elif action == "deploy":
            deploy_metadata = Netlify().deploy(project_name)
            deploy_url = deploy_metadata["deploy_url"]
            
            response = {
                "message": "Done! I deployed your project on Netflify.",
                "deploy_url": deploy_url
            }
            response = json.dumps(response, indent=4)
            
            ProjectManager().add_message_from_devika(project_name, response)
        elif action == "feature":
            code = self.feature.execute(
                conversation=conversation,
                code_markdown=code_markdown,
                system_os=os_system,
                project_name=project_name
            )
            print(code)
            print("=====" * 10)

            self.feature.save_code_to_project(code, project_name)
        elif action == "bug":
            code = self.patcher.execute(
                conversation=conversation,
                code_markdown=code_markdown,
                commands=None,
                error=prompt,
                system_os=os_system,
                project_name=project_name
            )
            print(code)
            print("=====" * 10)

            self.patcher.save_code_to_project(code, project_name)
        elif action == "report":
            markdown = self.reporter.execute(conversation, code_markdown)

            _out_pdf_file = PDF().markdown_to_pdf(markdown, project_name)

            project_name_space_url = project_name.replace(" ", "%20")
            pdf_download_url = "http://127.0.0.1:1337/api/download-project-pdf?project_name={}".format(project_name_space_url)
            response = f"I have generated the PDF document. You can download it from here: {pdf_download_url}"

            Browser().go_to(pdf_download_url)
            Browser().screenshot(project_name)

            ProjectManager().add_message_from_devika(project_name, response)

        AgentState().set_agent_active(project_name, False)
        AgentState().set_agent_completed(project_name, True)
            
    """
    Agentic flow of execution
    """
    def execute(self, prompt: str, project_name_from_user: str = None) -> str:
        if project_name_from_user:
            ProjectManager().add_message_from_user(project_name_from_user, prompt)
        
        plan = self.planner.execute(prompt)
        print(plan)
        print("=====" * 10)

        planner_response = self.planner.parse_response(plan)
        project_name = planner_response["project"]
        reply = planner_response["reply"]
        focus = planner_response["focus"]
        plans = planner_response["plans"]
        summary = planner_response["summary"]

        if project_name_from_user:
            project_name = project_name_from_user
        else:
            project_name = planner_response["project"]
            ProjectManager().create_project(project_name)
            ProjectManager().add_message_from_user(project_name, prompt)

        AgentState().set_agent_active(project_name, True)
        
        ProjectManager().add_message_from_devika(project_name, reply)
        ProjectManager().add_message_from_devika(project_name, json.dumps(plans, indent=4))
        # ProjectManager().add_message_from_devika(project_name, f"In summary: {summary}")

        self.update_contextual_keywords(focus)
        print(self.collected_context_keywords)
        
        internal_monologue = self.internal_monologue.execute(current_prompt=plan)
        print(internal_monologue)
        print("=====" * 10)

        new_state = AgentState().new_state()
        new_state["internal_monologue"] = internal_monologue
        AgentState().add_to_current_state(project_name, new_state)

        research = self.researcher.execute(plan, self.collected_context_keywords)
        print(research)
        print("=====" * 10)

        queries = research["queries"]
        queries_combined = ", ".join(queries)
        ask_user = research["ask_user"]

        ProjectManager().add_message_from_devika(
            project_name,
            f"I am browsing the web to research the following queries: {queries_combined}. If I need anything, I will make sure to ask you."
        )

        ask_user_prompt = "Nothing from the user."

        if ask_user != "":
            ProjectManager().add_message_from_devika(project_name, ask_user)
            AgentState().set_agent_active(project_name, False)
            got_user_query = False

            while not got_user_query:
                self.logger.info("Waiting for user query...")

                latest_message_from_user = ProjectManager().get_latest_message_from_user(project_name)
                validate_last_message_is_from_user = ProjectManager().validate_last_message_is_from_user(project_name)
                
                if latest_message_from_user and validate_last_message_is_from_user:
                    ask_user_prompt = latest_message_from_user["message"]
                    got_user_query = True
                    ProjectManager().add_message_from_devika(project_name, "Thanks! 🙌")
                time.sleep(5)
                
        AgentState().set_agent_active(project_name, True)
        
        search_results = self.search_queries(queries, project_name)

        print(json.dumps(search_results, indent=4))
        print("=====" * 10)

        code = self.coder.execute(
            step_by_step_plan=plan,
            user_context=ask_user_prompt,
            search_results=search_results,
            project_name=project_name
        )
        print(code)
        print("=====" * 10)

        self.coder.save_code_to_project(code, project_name)

        AgentState().set_agent_active(project_name, False)
        AgentState().set_agent_completed(project_name, True)
