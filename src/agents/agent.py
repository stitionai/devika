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
from .code_reviewer import CodeReviewer
from .test_generator import TestGenerator
from .performance_optimizer import PerformanceOptimizer
from .security_auditor import SecurityAuditor
from .documentation_generator import DocumentationGenerator
from .dependency_manager import DependencyManager

from src.project import ProjectManager
from src.state import AgentState
from src.logger import Logger

from src.bert.sentence import SentenceBert
from src.memory import KnowledgeBase
from src.browser.search import BingSearch, GoogleSearch, DuckDuckGoSearch
from src.browser import Browser
from src.browser import start_interaction
from src.filesystem import ReadCode
from src.services import Netlify
from src.documenter.pdf import PDF

import json
import time
import platform
import tiktoken
import asyncio

from src.socket_instance import emit_agent


class Agent:
    def __init__(self, base_model: str, search_engine: str, browser: Browser = None):
        if not base_model:
            raise ValueError("base_model is required")

        self.logger = Logger()

        """
        Accumulate contextual keywords from chained prompts of all preparation agents
        """
        self.collected_context_keywords = []

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
        self.code_reviewer = CodeReviewer(base_model=base_model)
        self.test_generator = TestGenerator(base_model=base_model)
        self.performance_optimizer = PerformanceOptimizer(base_model=base_model)
        self.security_auditor = SecurityAuditor(base_model=base_model)
        self.documentation_generator = DocumentationGenerator(base_model=base_model)
        self.dependency_manager = DependencyManager(base_model=base_model)

        self.project_manager = ProjectManager()
        self.agent_state = AgentState()
        self.engine = search_engine
        self.tokenizer = tiktoken.get_encoding("cl100k_base")

    async def open_page(self, project_name, url):
        browser = await Browser().start()

        await browser.go_to(url)
        _, raw = await browser.screenshot(project_name)
        data = await browser.extract_text()
        await browser.close()

        return browser, raw, data

    def search_queries(self, queries: list, project_name: str) -> dict:
        results = {}

        knowledge_base = KnowledgeBase()

        if self.engine == "bing":
            web_search = BingSearch()
        elif self.engine == "google":
            web_search = GoogleSearch()
        else:
            web_search = DuckDuckGoSearch()

        self.logger.info(f"\nSearch Engine :: {self.engine}")

        for query in queries:
            query = query.strip().lower()

            # knowledge = knowledge_base.get_knowledge(tag=query)
            # if knowledge:
            #     results[query] = knowledge
            #     continue

            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)

            web_search.search(query)

            link = web_search.get_first_link()
            print("\nLink :: ", link, '\n')
            if not link:
                continue
            browser, raw, data = loop.run_until_complete(self.open_page(project_name, link))
            emit_agent("screenshot", {"data": raw, "project_name": project_name}, False)
            results[query] = self.formatter.execute(data, project_name)

            self.logger.info(f"got the search results for : {query}")
            # knowledge_base.add_knowledge(tag=query, contents=results[query])
        return results

    def update_contextual_keywords(self, sentence: str):
        """
            Update the context keywords with the latest sentence/prompt
        """
        keywords = SentenceBert(sentence).extract_keywords()
        for keyword in keywords:
            self.collected_context_keywords.append(keyword[0])

        return self.collected_context_keywords

    def make_decision(self, prompt: str, project_name: str) -> str:
        decision = self.decision.execute(prompt, project_name)

        for item in decision:
            function = item["function"]
            args = item["args"]
            reply = item["reply"]

            self.project_manager.add_message_from_devika(project_name, reply)

            if function == "git_clone":
                url = args["url"]
                # Implement git clone functionality here

            elif function == "generate_pdf_document":
                user_prompt = args["user_prompt"]
                # Call the reporter agent to generate the PDF document
                markdown = self.reporter.execute([user_prompt], "", project_name)
                _out_pdf_file = PDF().markdown_to_pdf(markdown, project_name)

                project_name_space_url = project_name.replace(" ", "%20")
                pdf_download_url = "http://127.0.0.1:1337/api/download-project-pdf?project_name={}".format(
                    project_name_space_url)
                response = f"I have generated the PDF document. You can download it from here: {pdf_download_url}"

                #asyncio.run(self.open_page(project_name, pdf_download_url))

                self.project_manager.add_message_from_devika(project_name, response)

            elif function == "browser_interaction":
                user_prompt = args["user_prompt"]
                # Call the interaction agent to interact with the browser
                start_interaction(self.base_model, user_prompt, project_name)

            elif function == "coding_project":
                user_prompt = args["user_prompt"]
                # Call the planner, researcher, coder agents in sequence
                plan = self.planner.execute(user_prompt, project_name)
                planner_response = self.planner.parse_response(plan)

                research = self.researcher.execute(plan, self.collected_context_keywords, project_name)
                search_results = self.search_queries(research["queries"], project_name)

                code = self.coder.execute(
                    step_by_step_plan=plan,
                    user_context=research["ask_user"],
                    search_results=search_results,
                    project_name=project_name
                )
                self.coder.save_code_to_project(code, project_name)

    def subsequent_execute(self, prompt: str, project_name: str):
        """
        Subsequent flow of execution
        """
        new_message = self.project_manager.new_message()
        new_message['message'] = prompt
        new_message['from_devika'] = False
        self.project_manager.add_message_from_user(project_name, new_message['message'])

        os_system = platform.platform()

        self.agent_state.set_agent_active(project_name, True)

        conversation = self.project_manager.get_all_messages_formatted(project_name)
        code_markdown = ReadCode(project_name).code_set_to_markdown()

        response, action = self.action.execute(conversation, project_name)

        self.project_manager.add_message_from_devika(project_name, response)

        print("\naction :: ", action, '\n')

        if action == "answer":
            response = self.answer.execute(
                conversation=conversation,
                code_markdown=code_markdown,
                project_name=project_name
            )
            self.project_manager.add_message_from_devika(project_name, response)

        elif action == "run":
            project_path = self.project_manager.get_project_path(project_name)
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
                "message": "Done! I deployed your project on Netlify.",
                "deploy_url": deploy_url
            }
            response = json.dumps(response, indent=4)

            self.project_manager.add_message_from_devika(project_name, response)

        elif action == "feature":
            code = self.feature.execute(
                conversation=conversation,
                code_markdown=code_markdown,
                system_os=os_system,
                project_name=project_name
            )
            print("\nfeature code :: ", code, '\n')
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
            print("\nbug code :: ", code, '\n')
            self.patcher.save_code_to_project(code, project_name)

        elif action == "report":
            markdown = self.reporter.execute(conversation, code_markdown, project_name)

            _out_pdf_file = PDF().markdown_to_pdf(markdown, project_name)

            project_name_space_url = project_name.replace(" ", "%20")
            pdf_download_url = "http://127.0.0.1:1337/api/download-project-pdf?project_name={}".format(
                project_name_space_url)
            response = f"I have generated the PDF document. You can download it from here: {pdf_download_url}"

            #asyncio.run(self.open_page(project_name, pdf_download_url))

            self.project_manager.add_message_from_devika(project_name, response)

        elif action == "review":
            review_result = self.code_reviewer.execute(
                code_markdown=code_markdown,
                review_type="comprehensive",
                project_name=project_name
            )
            
            # Format the review result for display
            review_summary = f"""
            ## Code Review Results
            
            **Overall Score:** {review_result['review']['overall_score']}/10
            **Summary:** {review_result['review']['summary']}
            
            ### Strengths:
            {chr(10).join([f"- {strength}" for strength in review_result['review']['strengths']])}
            
            ### Issues Found:
            {chr(10).join([f"- **{issue['severity'].upper()}**: {issue['description']}" for issue in review_result['review']['issues']])}
            
            ### Recommendations:
            {chr(10).join([f"- {rec}" for rec in review_result['review']['recommendations']])}
            """
            
            self.project_manager.add_message_from_devika(project_name, review_summary)

        elif action == "test":
            tests = self.test_generator.execute(
                code_markdown=code_markdown,
                test_type="unit",
                project_name=project_name
            )
            self.test_generator.save_tests_to_project(tests, project_name)
            
            response = "I have generated comprehensive unit tests for your project. The test files have been created and are ready to run."
            self.project_manager.add_message_from_devika(project_name, response)

        elif action == "optimize":
            optimization_result = self.performance_optimizer.execute(
                code_markdown=code_markdown,
                performance_metrics="",
                project_name=project_name
            )
            
            # Format the optimization result for display
            optimization_summary = f"""
            ## Performance Analysis Results
            
            **Performance Score:** {optimization_result['analysis']['overall_performance_score']}/10
            
            ### Bottlenecks Identified:
            {chr(10).join([f"- **{bottleneck['impact'].upper()}**: {bottleneck['issue']} ({bottleneck['location']})" for bottleneck in optimization_result['analysis']['bottlenecks']])}
            
            ### Optimization Recommendations:
            {chr(10).join([f"- **{opt['priority'].upper()}**: {opt['description']} (Expected gain: {opt['expected_gain']})" for opt in optimization_result['optimizations']])}
            """
            
            self.project_manager.add_message_from_devika(project_name, optimization_summary)

        elif action == "security":
            security_result = self.security_auditor.execute(
                code_markdown=code_markdown,
                audit_type="comprehensive",
                project_name=project_name
            )
            
            # Format the security result for display
            security_summary = f"""
            ## Security Audit Results
            
            **Security Score:** {security_result['security_score']}/10
            **Overall Risk:** {security_result['overall_risk'].upper()}
            
            ### Vulnerabilities Found:
            {chr(10).join([f"- **{vuln['severity'].upper()}**: {vuln['title']} - {vuln['description']}" for vuln in security_result['vulnerabilities']])}
            
            ### Security Recommendations:
            {chr(10).join([f"- **{rec['priority'].upper()}**: {rec['recommendation']}" for rec in security_result['security_recommendations']])}
            """
            
            self.project_manager.add_message_from_devika(project_name, security_summary)

        elif action == "document":
            docs = self.documentation_generator.execute(
                code_markdown=code_markdown,
                doc_type="comprehensive",
                project_name=project_name
            )
            self.documentation_generator.save_docs_to_project(docs, project_name)
            
            response = "I have generated comprehensive documentation for your project including README, API docs, and contributing guidelines."
            self.project_manager.add_message_from_devika(project_name, response)

        elif action == "dependencies":
            # Get package files content for analysis
            package_files = ""
            try:
                project_files = self.project_manager.get_project_files(project_name)
                for file in project_files:
                    if file['file'] in ['package.json', 'requirements.txt', 'Cargo.toml', 'go.mod', 'composer.json']:
                        package_files += f"File: {file['file']}\n{file['code']}\n\n"
            except:
                pass
            
            dependency_result = self.dependency_manager.execute(
                code_markdown=code_markdown,
                package_files=package_files,
                project_name=project_name
            )
            
            # Format the dependency result for display
            dependency_summary = f"""
            ## Dependency Analysis Results
            
            **Total Dependencies:** {dependency_result['dependencies']['total_count']}
            **Security Issues:** {dependency_result['security_summary']['total_vulnerable_packages']} packages with vulnerabilities
            
            ### Critical Actions Needed:
            {chr(10).join([f"- **{rec['priority'].upper()}**: {rec['description']} (`{rec['command']}`)" for rec in dependency_result['recommendations'] if rec['priority'] in ['critical', 'high']])}
            
            ### License Analysis:
            - Compatible: {', '.join(dependency_result['license_analysis']['compatible_licenses'])}
            - Conflicts: {len(dependency_result['license_analysis']['license_conflicts'])} found
            """
            
            self.project_manager.add_message_from_devika(project_name, dependency_summary)

        self.agent_state.set_agent_active(project_name, False)
        self.agent_state.set_agent_completed(project_name, True)

    def execute(self, prompt: str, project_name: str) -> str:
        """
        Agentic flow of execution
        """
        if project_name:
            self.project_manager.add_message_from_user(project_name, prompt)

        self.agent_state.create_state(project=project_name)

        plan = self.planner.execute(prompt, project_name)
        print("\nplan :: ", plan, '\n')

        planner_response = self.planner.parse_response(plan)
        reply = planner_response["reply"]
        focus = planner_response["focus"]
        plans = planner_response["plans"]
        summary = planner_response["summary"]

        self.project_manager.add_message_from_devika(project_name, reply)
        self.project_manager.add_message_from_devika(project_name, json.dumps(plans, indent=4))
        # self.project_manager.add_message_from_devika(project_name, f"In summary: {summary}")

        self.update_contextual_keywords(focus)
        print("\ncontext_keywords :: ", self.collected_context_keywords, '\n')

        internal_monologue = self.internal_monologue.execute(current_prompt=plan, project_name=project_name)
        print("\ninternal_monologue :: ", internal_monologue, '\n')

        new_state = self.agent_state.new_state()
        new_state["internal_monologue"] = internal_monologue
        self.agent_state.add_to_current_state(project_name, new_state)

        research = self.researcher.execute(plan, self.collected_context_keywords, project_name=project_name)
        print("\nresearch :: ", research, '\n')

        queries = research["queries"]
        queries_combined = ", ".join(queries)
        ask_user = research["ask_user"]

        if (queries and len(queries) > 0) or ask_user != "":
            self.project_manager.add_message_from_devika(
                project_name,
                f"I am browsing the web to research the following queries: {queries_combined}."
                f"\n If I need anything, I will make sure to ask you."
            )
        if not queries and len(queries) == 0:
            self.project_manager.add_message_from_devika(
                project_name,
                "I think I can proceed without searching the web."
            )

        ask_user_prompt = "Nothing from the user."

        if ask_user != "" and ask_user is not None:
            self.project_manager.add_message_from_devika(project_name, ask_user)
            self.agent_state.set_agent_active(project_name, False)
            got_user_query = False

            while not got_user_query:
                self.logger.info("Waiting for user query...")

                latest_message_from_user = self.project_manager.get_latest_message_from_user(project_name)
                validate_last_message_is_from_user = self.project_manager.validate_last_message_is_from_user(
                    project_name)

                if latest_message_from_user and validate_last_message_is_from_user:
                    ask_user_prompt = latest_message_from_user["message"]
                    got_user_query = True
                    self.project_manager.add_message_from_devika(project_name, "Thanks! 🙌")
                time.sleep(5)

        self.agent_state.set_agent_active(project_name, True)

        if queries and len(queries) > 0:
            search_results = self.search_queries(queries, project_name)

        else:
            search_results = {}

        code = self.coder.execute(
            step_by_step_plan=plan,
            user_context=ask_user_prompt,
            search_results=search_results,
            project_name=project_name
        )
        print("\ncode :: ", code, '\n')

        self.coder.save_code_to_project(code, project_name)

        self.agent_state.set_agent_active(project_name, False)
        self.agent_state.set_agent_completed(project_name, True)
        self.project_manager.add_message_from_devika(
            project_name,
            "I have completed the my task. \n"
            "if you would like me to do anything else, please let me know. \n"
        )