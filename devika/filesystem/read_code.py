"""Code to Markdown Convertor."""

import os

from devika.config import Config


class CodeToMarkdownConvertor:
    """Code to read the code from the project directory and convert it to markdown."""

    def __init__(self, project_name: str):
        config = Config()
        project_path = config.get_projects_dir()
        self.directory_path = os.path.join(
            project_path, project_name.lower().replace(" ", "-")
        )

    def _read_directory(self):
        files_list = []
        for root, _, files in os.walk(self.directory_path):
            for file in files:
                try:
                    file_path = os.path.join(root, file)
                    with open(file_path, "r", encoding="utf-8") as file_content:
                        files_list.append(
                            {"filename": file_path, "code": file_content.read()}
                        )
                except FileNotFoundError:
                    pass

        return files_list

    def convert(self):
        """Collect all the codes of the project to a markdown file."""
        code_set = self._read_directory()
        markdown = ""
        for code in code_set:
            markdown += f"### {code['filename']}:\n\n"
            markdown += f"```\n{code['code']}\n```\n\n"
            markdown += "---\n\n"
        return markdown
