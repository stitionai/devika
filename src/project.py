import os
import json
import zipfile
from datetime import datetime
from typing import Optional
from sqlmodel import Field, Session, SQLModel, create_engine

from src.config import Config

class Projects(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    project: str
    message_stack_json: str

class ProjectManager:
    def __init__(self):
        # Initialize the ProjectManager class
        config = Config()
        sqlite_path = config.get_sqlite_db()
        self.project_path = config.get_projects_dir()
        self.engine = create_engine(f"sqlite:///{sqlite_path}")
        SQLModel.metadata.create_all(self.engine)

    def new_message(self):
         # Create a new message dictionary with timestamp
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        return {
            "from_devika": True,
            "message": None,
            "timestamp": timestamp
        }
        
     # Methods for managing projects
    def _get_project_state(self, session, project: str):
        return session.query(Projects).filter(Projects.project == project).first()

    def _commit_session(self, session):
        session.commit()

    def _add_project_state(self, session, project: str, message_stack: list):
        project_state = Projects(project=project, message_stack_json=json.dumps(message_stack))
        session.add(project_state)
        self._commit_session(session)

    def _update_project_state(self, session, project_state, message_stack):
        project_state.message_stack_json = json.dumps(message_stack)
        self._commit_session(session)

    def _create_session(self):
        return Session(self.engine)

    def create_project(self, project: str):
        with self._create_session() as session:
            self._add_project_state(session, project, [])

    def delete_project(self, project: str):
        with self._create_session() as session:
            project_state = self._get_project_state(session, project)
            if project_state:
                session.delete(project_state)
                self._commit_session(session)

    # Methods for adding messages
    def _get_message_stack(self, project_state):
        return json.loads(project_state.message_stack_json) if project_state else []

    def _add_message_to_stack(self, message_stack, message):
        message_stack.append(message)

    def add_message_to_project(self, project: str, message: dict):
        with self._create_session() as session:
            project_state = self._get_project_state(session, project)
            message_stack = self._get_message_stack(project_state)
            self._add_message_to_stack(message_stack, message)
            self._update_project_state(session, project_state, message_stack)

    def add_message_from_devika(self, project: str, message: str):
        new_message = self.new_message()
        new_message["message"] = message
        self.add_message_to_project(project, new_message)

    def add_message_from_user(self, project: str, message: str):
        new_message = self.new_message()
        new_message["message"] = message
        new_message["from_devika"] = False
        self.add_message_to_project(project, new_message)

    # Methods for retrieving messages
    def get_messages(self, project: str):
        with self._create_session() as session:
            project_state = self._get_project_state(session, project)
            return self._get_message_stack(project_state)

    def _get_latest_message(self, project_state, from_devika: bool):
        message_stack = self._get_message_stack(project_state)
        for message in reversed(message_stack):
            if message["from_devika"] == from_devika:
                return message

    def get_latest_message_from_user(self, project: str):
        with self._create_session() as session:
            project_state = self._get_project_state(session, project)
            return self._get_latest_message(project_state, from_devika=False)

    def validate_last_message_is_from_user(self, project: str):
        with self._create_session() as session:
            project_state = self._get_project_state(session, project)
            return self._get_latest_message(project_state, from_devika=True) is None

    def get_latest_message_from_devika(self, project: str):
        with self._create_session() as session:
            project_state = self._get_project_state(session, project)
            return self._get_latest_message(project_state, from_devika=True)

    # Methods for project management
    def get_project_list(self):
        with self._create_session() as session:
            return [project.project for project in session.query(Projects).all()]

    def get_all_messages_formatted(self, project: str):
        formatted_messages = []
        with self._create_session() as session:
            project_state = self._get_project_state(session, project)
            if project_state:
                message_stack = self._get_message_stack(project_state)
                for message in message_stack:
                    sender = "Devika" if message["from_devika"] else "User"
                    formatted_messages.append(f"{sender}: {message['message']}")
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
