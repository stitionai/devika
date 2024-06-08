import os
import json
import zipfile
from datetime import datetime
from typing import Optional
from src.socket_instance import emit_agent
from sqlmodel import Field, Session, SQLModel, create_engine
from src.config import Config


class Projects(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    project: str
    message_stack_json: str


class ProjectManager:
    def __init__(self):
        config = Config()
        sqlite_path = config.get_sqlite_db()
        self.project_path = config.get_projects_dir()
        self.engine = create_engine(f"sqlite:///{sqlite_path}")
        SQLModel.metadata.create_all(self.engine)

    def new_message(self):
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        return {
            "from_devika": True,
            "message": None,
            "timestamp": timestamp
        }

    def create_project(self, project: str):
        with Session(self.engine) as session:
            project_state = Projects(project=project, message_stack_json=json.dumps([]))
            session.add(project_state)
            session.commit()

    def delete_project(self, project: str):
        with Session(self.engine) as session:
            project_state = session.query(Projects).filter(Projects.project == project).first()
            if project_state:
                session.delete(project_state)
                session.commit()

    def add_message_to_project(self, project: str, message: dict):
        with Session(self.engine) as session:
            project_state = session.query(Projects).filter(Projects.project == project).first()
            if project_state:
                message_stack = json.loads(project_state.message_stack_json)
                message_stack.append(message)
                project_state.message_stack_json = json.dumps(message_stack)
                session.commit()
            else:
                message_stack = [message]
                project_state = Projects(project=project, message_stack_json=json.dumps(message_stack))
                session.add(project_state)
                session.commit()

    def add_message_from_devika(self, project: str, message: str):
        new_message = self.new_message()
        new_message["message"] = message
        emit_agent("server-message", {"messages": new_message})
        self.add_message_to_project(project, new_message)

    def add_message_from_user(self, project: str, message: str):
        new_message = self.new_message()
        new_message["message"] = message
        new_message["from_devika"] = False
        emit_agent("server-message", {"messages": new_message})
        self.add_message_to_project(project, new_message)

    def get_messages(self, project: str):
        with Session(self.engine) as session:
            project_state = session.query(Projects).filter(Projects.project == project).first()
            if project_state:
                return json.loads(project_state.message_stack_json)
            return None

    def get_latest_message_from_user(self, project: str):
        with Session(self.engine) as session:
            project_state = session.query(Projects).filter(Projects.project == project).first()
            if project_state:
                message_stack = json.loads(project_state.message_stack_json)
                for message in reversed(message_stack):
                    if not message["from_devika"]:
                        return message
            return None

    def validate_last_message_is_from_user(self, project: str):
        with Session(self.engine) as session:
            project_state = session.query(Projects).filter(Projects.project == project).first()
            if project_state:
                message_stack = json.loads(project_state.message_stack_json)
                if message_stack:
                    return not message_stack[-1]["from_devika"]
            return False

    def get_latest_message_from_devika(self, project: str):
        with Session(self.engine) as session:
            project_state = session.query(Projects).filter(Projects.project == project).first()
            if project_state:
                message_stack = json.loads(project_state.message_stack_json)
                for message in reversed(message_stack):
                    if message["from_devika"]:
                        return message
            return None

    def get_project_list(self):
        with Session(self.engine) as session:
            projects = session.query(Projects).all()
            return [project.project for project in projects]

    def get_all_messages_formatted(self, project: str):
        formatted_messages = []

        with Session(self.engine) as session:
            project_state = session.query(Projects).filter(Projects.project == project).first()
            if project_state:
                message_stack = json.loads(project_state.message_stack_json)
                for message in message_stack:
                    if message["from_devika"]:
                        formatted_messages.append(f"Devika: {message['message']}")
                    else:
                        formatted_messages.append(f"User: {message['message']}")

            return formatted_messages

    def get_project_path(self, project: str):
        return os.path.join(self.project_path, project.lower().replace(" ", "-"))

    def project_to_zip(self, project: str):
        project_path = self.get_project_path(project)
        zip_path = f"{project_path}.zip"

        with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for root, dirs, files in os.walk(project_path):
                for file in files:
                    relative_path = os.path.relpath(os.path.join(root, file), os.path.join(project_path, '..'))
                    zipf.write(os.path.join(root, file), arcname=relative_path)

        return zip_path

    def get_zip_path(self, project: str):
        return f"{self.get_project_path(project)}.zip"
    
    def get_project_files(self, project_name: str):
        if not project_name:
            return []

        project_directory = "-".join(project_name.split(" "))
        base_path = os.path.abspath(os.path.join(os.getcwd(), 'data', 'projects'))
        directory = os.path.join(base_path, project_directory)

        # Ensure the directory is within the allowed base path
        if not os.path.exists(directory) or not os.path.commonprefix([directory, base_path]) == base_path:
            return []

        files = []
        for root, _, filenames in os.walk(directory):
            for filename in filenames:
                file_relative_path = os.path.relpath(root, directory)
                if file_relative_path == '.':
                    file_relative_path = ''
                file_path = os.path.join(file_relative_path, filename)
                try:
                    with open(os.path.join(root, filename), 'r') as file:
                        files.append({
                            "file": file_path,
                            "code": file.read()
                        })
                except Exception as e:
                    print(f"Error reading file {filename}: {e}")
        return files
