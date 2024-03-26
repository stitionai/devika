import json
from datetime import datetime
from typing import Optional
from sqlmodel import Field, Session, SQLModel, create_engine

from src.config import Config

class AgentStateModel(SQLModel, table=True):
    __tablename__ = "agent_state"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    project: str
    state_stack_json: str

class AgentState:
    def __init__(self):
        config = Config()
        sqlite_path = config.get_sqlite_db()
        self.engine = create_engine(f"sqlite:///{sqlite_path}")
        SQLModel.metadata.create_all(self.engine)

    def new_state(self):
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        return {
            "internal_monologue": None,
            "browser_session": {
                "url": None,
                "screenshot": None
            },
            "terminal_session": {
                "command": None,
                "output": None,
                "title": None
            },
            "step": None,
            "message": None,
            "completed": False,
            "agent_is_active": True,
            "token_usage": 0,
            "timestamp": timestamp
        }

    def delete_state(self, project: str):
        with Session(self.engine) as session:
            agent_state = session.query(AgentStateModel).filter(AgentStateModel.project == project).first()
            if agent_state:
                session.delete(agent_state)
                session.commit()

    def add_to_current_state(self, project: str, state: dict):
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

    def get_current_state(self, project: str):
        with Session(self.engine) as session:
            agent_state = session.query(AgentStateModel).filter(AgentStateModel.project == project).first()
            if agent_state:
                return json.loads(agent_state.state_stack_json)
            return None
 
    def update_latest_state(self, project: str, state: dict):
        with Session(self.engine) as session:
            agent_state = session.query(AgentStateModel).filter(AgentStateModel.project == project).first()
            if agent_state:
                state_stack = json.loads(agent_state.state_stack_json)
                state_stack[-1] = state
                agent_state.state_stack_json = json.dumps(state_stack)
                session.commit()
            else:
                state_stack = [state]
                agent_state = AgentStateModel(project=project, state_stack_json=json.dumps(state_stack))
                session.add(agent_state)
                session.commit()

    def get_latest_state(self, project: str):
        with Session(self.engine) as session:
            agent_state = session.query(AgentStateModel).filter(AgentStateModel.project == project).first()
            if agent_state:
                return json.loads(agent_state.state_stack_json)[-1]
            return None

    def set_agent_active(self, project: str, is_active: bool):
        with Session(self.engine) as session:
            agent_state = session.query(AgentStateModel).filter(AgentStateModel.project == project).first()
            if agent_state:
                state_stack = json.loads(agent_state.state_stack_json)
                state_stack[-1]["agent_is_active"] = is_active
                agent_state.state_stack_json = json.dumps(state_stack)
                session.commit()
            else:
                state_stack = [self.new_state()]
                state_stack[-1]["agent_is_active"] = is_active
                agent_state = AgentStateModel(project=project, state_stack_json=json.dumps(state_stack))
                session.add(agent_state)
                session.commit()

    def is_agent_active(self, project: str):
        with Session(self.engine) as session:
            agent_state = session.query(AgentStateModel).filter(AgentStateModel.project == project).first()
            if agent_state:
                return json.loads(agent_state.state_stack_json)[-1]["agent_is_active"]
            return None

    def set_agent_completed(self, project: str, is_completed: bool):
        with Session(self.engine) as session:
            agent_state = session.query(AgentStateModel).filter(AgentStateModel.project == project).first()
            if agent_state:
                state_stack = json.loads(agent_state.state_stack_json)
                state_stack[-1]["completed"] = is_completed
                agent_state.state_stack_json = json.dumps(state_stack)
                session.commit()
            else:
                state_stack = [self.new_state()]
                state_stack[-1]["completed"] = is_completed
                agent_state = AgentStateModel(project=project, state_stack_json=json.dumps(state_stack))
                session.add(agent_state)
                session.commit()
                
    def is_agent_completed(self, project: str):
        with Session(self.engine) as session:
            agent_state = session.query(AgentStateModel).filter(AgentStateModel.project == project).first()
            if agent_state:
                return json.loads(agent_state.state_stack_json)[-1]["completed"]
            return None
            
    def update_token_usage(self, project: str, token_usage: int):
        with Session(self.engine) as session:
            agent_state = session.query(AgentStateModel).filter(AgentStateModel.project == project).first()
            print(agent_state)
            if agent_state:
                state_stack = json.loads(agent_state.state_stack_json)
                state_stack[-1]["token_usage"] += token_usage
                agent_state.state_stack_json = json.dumps(state_stack)
                session.commit()
            else:
                state_stack = [self.new_state()]
                state_stack[-1]["token_usage"] = token_usage
                agent_state = AgentStateModel(project=project, state_stack_json=json.dumps(state_stack))
                session.add(agent_state)
                session.commit()

    def get_latest_token_usage(self, project: str):
        with Session(self.engine) as session:
            agent_state = session.query(AgentStateModel).filter(AgentStateModel.project == project).first()
            if agent_state:
                return json.loads(agent_state.state_stack_json)[-1]["token_usage"]
            return 0