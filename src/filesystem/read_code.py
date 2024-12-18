import os
from typing import Dict, List

from src.config import Config
from src.memory.rag import CodeRAG

"""
TODO: Replace this with `code2prompt` - https://github.com/mufeedvh/code2prompt
"""

class ReadCode:
    def __init__(self, project_name: str):
        config = Config()
        self.project_name = project_name.lower().replace(" ", "-")
        self.directory_path = os.path.join(config.get_projects_dir(), self.project_name)
        self.rag = CodeRAG(project_name)

    def read_directory(self) -> List[Dict[str, str]]:
        files_list = []
        for root, _dirs, files in os.walk(self.directory_path):
            for file in files:
                try:
                    file_path = os.path.join(root, file)
                    with open(file_path, 'r') as file_content:
                        code = file_content.read()
                        files_list.append({"filename": file_path, "code": code})
                        self.rag.add_code(file_path, code)
                except:
                    pass
        return files_list

    def code_set_to_markdown(self) -> str:
        code_set = self.read_directory()
        markdown = ""
        for code in code_set:
            markdown += f"### {code['filename']}:\n\n"
            summary = self.rag.summarize_code(code['code'])
            if summary:
                markdown += f"Summary: {summary}\n\n"
            markdown += f"```\n{code['code']}\n```\n\n"
            markdown += "---\n\n"
        return markdown

    def get_code_context(self, query: str, n_results: int = 5) -> Dict:
        return self.rag.get_context(query, n_results)
