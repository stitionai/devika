import os

from src.config import Config

"""
TODO: Replace this with `code2prompt` - https://github.com/mufeedvh/code2prompt
"""

class ReadCode:
    def __init__(self, project_name: str):
        config = Config()
        project_path = config.get_projects_dir()
        blacklist_dir = config.get_blacklist_dir()
        self.directory_path = os.path.join(project_path, project_name.lower().replace(" ", "-"))
        self.blacklist_dirs = [dir.strip() for dir in blacklist_dir.split(', ')]

    def read_directory(self):
        files_list = []
        
        for root, _dirs, files in os.walk(self.directory_path):
            for file in files:
                try:
                    file_path = os.path.join(root, file)
                    if any(blacklist_dir in file_path for blacklist_dir in self.blacklist_dirs):
                        print(f"SKIPPED FILE: {file_path}")
                        continue
                    with open(file_path, 'r') as file_content:
                        files_list.append({"filename": file_path, "code": file_content.read()})
                except:
                    pass

        return files_list

    def code_set_to_markdown(self):
        code_set = self.read_directory()
        markdown = ""
        for code in code_set:
            markdown += f"### {code['filename']}:\n\n"
            markdown += f"```\n{code['code']}\n```\n\n"
            markdown += "---\n\n"
        return markdown
