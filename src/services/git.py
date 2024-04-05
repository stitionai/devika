import json
import git as GitPython

from jinja2 import Environment, BaseLoader
from src.llm import LLM
PROMPT = open("src/services/prompt.jinja2").read().strip()

class Git:
    
    def __init__(self, path, base_model: str):
        self.llm = LLM(model_id=base_model)
        try:
            self.repo = GitPython.Repo(path)
        except GitPython.exc.InvalidGitRepositoryError:
            self.repo = self.initialize(path)

    def render(
        self, conversation: str, code_markdown: str, code_diff: str
    ) -> str:
        env = Environment(loader=BaseLoader())
        template = env.from_string(PROMPT)
        return template.render(
            conversation=conversation,
            code_markdown=code_markdown,
            code_diff=code_diff
        )

    def validate_response(self, response: str):
        response = response.strip().replace("```json", "```")
        
        try:
            response = response.split("```")[1].split("```")[0]
            response = json.loads(response)
        except Exception as _:
            return False

        if "commit_message" not in response:
            return False
        else:
            return response["commit_message"]

    def initialize(self, path):
        return GitPython.Repo.init(path)

    def commit(self, message):
        self.repo.index.add("*")
        self.repo.index.commit(message)

    def generate_commit_message(self, project_name, conversation, code_markdown):
        # Get the code diff
        try:
            code_diff = self.repo.git.diff()
        except GitPython.exc.GitCommandError:
            code_diff = ""

        prompt = self.render(conversation, code_markdown, code_diff)
        response = self.llm.inference(prompt, project_name)
        print(response)

        valid_response = self.validate_response(response)

        while not valid_response:
            print("Invalid response from the model, trying again...")
            return self.generate_commit_message(project_name, conversation, code_markdown)

        return valid_response

    def reset_to_previous_commit(self):
        try:
            self.repo.git.reset("--hard", "HEAD^")
            return True
        except GitPython.exc.GitCommandError as e:
            print(f"Error resetting to previous commit: {e}")
            return False

    def clone(self, url, path):
        return GitPython.Repo.clone_from(url, path)

    def get_branches(self):
        return self.repo.branches

    def get_commits(self, branch):
        return self.repo.iter_commits(branch)

    def get_commit(self, commit):
        return self.repo.commit(commit)

    def get_file(self, commit, file):
        return self.repo.git.show(f'{commit}:{file}')