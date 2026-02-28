import json
import os
from datetime import datetime
from typing import Optional
from sqlmodel import Field, Session, SQLModel, create_engine
from src.socket_instance import emit_agent
from src.config import Config
from src.logger import Logger


class AgentStateModel(SQLModel, table=True):
    __tablename__ = "agent_state"

    id: Optional[int] = Field(default=None, primary_key=True)
    project: str
    state_stack_json: str


class AgentState:
    def __init__(self):
        config = Config()
        self.logger = Logger()
        sqlite_path = config.get_sqlite_db()
        self.engine = create_engine(f"sqlite:///{sqlite_path}")
        SQLModel.metadata.create_all(self.engine)

    def new_state(self):
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        return {
            "internal_monologue": '',
            "browser_session": {
                "url": None,
                "screenshot": None
            },
            "terminal_session": {
                "command": None,
                "output": None,
                "title": None
            },
            "step": int(),
            "message": None,
            "completed": False,
            "agent_is_active": True,
            "token_usage": 0,
            "timestamp": timestamp
        }

    def create_state(self, project: str):
        try:
            with Session(self.engine) as session:
                new_state = self.new_state()
                new_state["step"] = 1
                new_state["internal_monologue"] = "I'm starting the work..."
                agent_state = AgentStateModel(project=project, state_stack_json=json.dumps([new_state]))
                session.add(agent_state)
                session.commit()
                emit_agent("agent-state", [new_state])
        except Exception as e:
            self.logger.error(f"Error creating state for project {project}: {str(e)}")

    def delete_state(self, project: str):
        try:
            with Session(self.engine) as session:
                agent_state = session.query(AgentStateModel).filter(AgentStateModel.project == project).all()
                if agent_state:
                    for state in agent_state:
                        session.delete(state)
                    session.commit()
        except Exception as e:
            self.logger.error(f"Error deleting state for project {project}: {str(e)}")

    def add_to_current_state(self, project: str, state: dict):
        try:
            with Session(self.engine) as session:
                agent_state = session.query(AgentStateModel).filter(AgentStateModel.project == project).first()
                if agent_state:
                    state_stack = json.loads(agent_state.state_stack_json)
                    state_stack.append(state)
                    agent_state.state_stack_json = json.dumps(state_stack)
                    session.commit()
                else:
                    state_stack = [state]
                    agent_state = AgentStateModel(project=project, state_stack_json=json.dumps(state_stack))
                    session.add(agent_state)
                    session.commit()
                emit_agent("agent-state", state_stack)
        except Exception as e:
            self.logger.error(f"Error adding to current state for project {project}: {str(e)}")

    def get_current_state(self, project: str):
        try:
            with Session(self.engine) as session:
                agent_state = session.query(AgentStateModel).filter(AgentStateModel.project == project).first()
                if agent_state:
                    return json.loads(agent_state.state_stack_json)
                return None
        except Exception as e:
            self.logger.error(f"Error getting current state for project {project}: {str(e)}")
            return None

    def update_latest_state(self, project: str, state: dict):
        try:
            with Session(self.engine) as session:
                agent_state = session.query(AgentStateModel).filter(AgentStateModel.project == project).first()
                if agent_state:
                    state_stack = json.loads(agent_state.state_stack_json)
                    if state_stack:
                        state_stack[-1] = state
                    else:
                        state_stack = [state]
                    agent_state.state_stack_json = json.dumps(state_stack)
                    session.commit()
                else:
                    state_stack = [state]
                    agent_state = AgentStateModel(project=project, state_stack_json=json.dumps(state_stack))
                    session.add(agent_state)
                    session.commit()
                emit_agent("agent-state", state_stack)
        except Exception as e:
            self.logger.error(f"Error updating latest state for project {project}: {str(e)}")

    def get_latest_state(self, project: str):
        try:
            with Session(self.engine) as session:
                agent_state = session.query(AgentStateModel).filter(AgentStateModel.project == project).first()
                if agent_state:
                    state_stack = json.loads(agent_state.state_stack_json)
                    if state_stack:
                        return state_stack[-1]
                return None
        except Exception as e:
            self.logger.error(f"Error getting latest state for project {project}: {str(e)}")
            return None

    def set_agent_active(self, project: str, is_active: bool):
        try:
            with Session(self.engine) as session:
                agent_state = session.query(AgentStateModel).filter(AgentStateModel.project == project).first()
                if agent_state:
                    state_stack = json.loads(agent_state.state_stack_json)
                    if state_stack:
                        state_stack[-1]["agent_is_active"] = is_active
                    else:
                        new_state = self.new_state()
                        new_state["agent_is_active"] = is_active
                        state_stack = [new_state]
                    agent_state.state_stack_json = json.dumps(state_stack)
                    session.commit()
                else:
                    state_stack = [self.new_state()]
                    state_stack[-1]["agent_is_active"] = is_active
                    agent_state = AgentStateModel(project=project, state_stack_json=json.dumps(state_stack))
                    session.add(agent_state)
                    session.commit()
                emit_agent("agent-state", state_stack)
        except Exception as e:
            self.logger.error(f"Error setting agent active for project {project}: {str(e)}")

    def is_agent_active(self, project: str):
        try:
            with Session(self.engine) as session:
                agent_state = session.query(AgentStateModel).filter(AgentStateModel.project == project).first()
                if agent_state:
                    state_stack = json.loads(agent_state.state_stack_json)
                    if state_stack:
                        return state_stack[-1].get("agent_is_active", False)
                return False
        except Exception as e:
            self.logger.error(f"Error checking if agent is active for project {project}: {str(e)}")
            return False

    def set_agent_completed(self, project: str, is_completed: bool):
        try:
            with Session(self.engine) as session:
                agent_state = session.query(AgentStateModel).filter(AgentStateModel.project == project).first()
                if agent_state:
                    state_stack = json.loads(agent_state.state_stack_json)
                    if state_stack:
                        state_stack[-1]["internal_monologue"] = "Agent has completed the task."
                        state_stack[-1]["completed"] = is_completed
                    else:
                        new_state = self.new_state()
                        new_state["completed"] = is_completed
                        state_stack = [new_state]
                    agent_state.state_stack_json = json.dumps(state_stack)
                    session.commit()
                else:
                    state_stack = [self.new_state()]
                    state_stack[-1]["completed"] = is_completed
                    agent_state = AgentStateModel(project=project, state_stack_json=json.dumps(state_stack))
                    session.add(agent_state)
                    session.commit()
                emit_agent("agent-state", state_stack)
        except Exception as e:
            self.logger.error(f"Error setting agent completed for project {project}: {str(e)}")

    def is_agent_completed(self, project: str):
        try:
            with Session(self.engine) as session:
                agent_state = session.query(AgentStateModel).filter(AgentStateModel.project == project).first()
                if agent_state:
                    state_stack = json.loads(agent_state.state_stack_json)
                    if state_stack:
                        return state_stack[-1].get("completed", False)
                return False
        except Exception as e:
            self.logger.error(f"Error checking if agent is completed for project {project}: {str(e)}")
            return False
            
    def update_token_usage(self, project: str, token_usage: int):
        try:
            with Session(self.engine) as session:
                agent_state = session.query(AgentStateModel).filter(AgentStateModel.project == project).first()
                if agent_state:
                    state_stack = json.loads(agent_state.state_stack_json)
                    if state_stack:
                        state_stack[-1]["token_usage"] += token_usage
                    else:
                        new_state = self.new_state()
                        new_state["token_usage"] = token_usage
                        state_stack = [new_state]
                    agent_state.state_stack_json = json.dumps(state_stack)
                    session.commit()
                else:
                    state_stack = [self.new_state()]
                    state_stack[-1]["token_usage"] = token_usage
                    agent_state = AgentStateModel(project=project, state_stack_json=json.dumps(state_stack))
                    session.add(agent_state)
                    session.commit()
        except Exception as e:
            self.logger.error(f"Error updating token usage for project {project}: {str(e)}")

    def get_latest_token_usage(self, project: str):
        try:
            with Session(self.engine) as session:
                agent_state = session.query(AgentStateModel).filter(AgentStateModel.project == project).first()
                if agent_state:
                    state_stack = json.loads(agent_state.state_stack_json)
                    if state_stack:
                        return state_stack[-1].get("token_usage", 0)
                return 0
        except Exception as e:
            self.logger.error(f"Error getting token usage for project {project}: {str(e)}")
            return 0