import os

from src.config import Config
from code2prompt import code2prompt  # Import code2prompt library

class ReadCode:
  def __init__(self, project_name: str):
    config = Config()
    project_path = config.get_projects_dir()
    self.directory_path = os.path.join(project_path, project_name.lower().replace(" ", "-"))

  def generate_prompt(self):
    """
    Generates a prompt from the project directory using code2prompt.

    Returns:
      str: The generated prompt
    """
    prompt = code2prompt(self.directory_path)
    return prompt

  def code_set_to_markdown(self, with_prompt=True):
    """
    Converts code files in the project directory to markdown format (optional).

    Args:
      with_prompt (bool, optional): Include the generated prompt (default: True).

    Returns:
      str: The generated markdown content
    """
    markdown = ""
    # Generate prompt (optional)
    if with_prompt:
      prompt = self.generate_prompt()
      markdown += f"### Generated Prompt:\n\n{prompt}\n\n"

    # Existing logic for converting code to markdown
    code_set = self.read_directory()
    for code in code_set:
      markdown += f"### {code['filename']}:\n\n"
      markdown += f"`\n{code['code']}\n`\n\n"
      markdown += "---\n\n"
    return markdown

  def read_directory(self):
    files_list = []
    for root, _dirs, files in os.walk(self.directory_path):
      for file in files:
        try:
          file_path = os.path.join(root, file)
          with open(file_path, 'r') as file_content:
            files_list.append({"filename": file_path, "code": file_content.read()})
        except:
          pass

    return files_list
