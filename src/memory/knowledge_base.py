from typing import Optional
from sqlmodel import Field, Session, SQLModel, create_engine

from src.config import Config

"""
TODO: The tag check should be a BM25 search, it's just a simple equality check now.
"""

class Knowledge(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    tag: str
    contents: str

class KnowledgeBase:
    def __init__(self):
        config = Config()
        sqlite_path = config.get_sqlite_db()
        self.engine = create_engine(f"sqlite:///{sqlite_path}")
        SQLModel.metadata.create_all(self.engine)

    def add_knowledge(self, tag: str, contents: str):
        knowledge = Knowledge(tag=tag, contents=contents)
        with Session(self.engine) as session:
            session.add(knowledge)
            session.commit()

    def get_knowledge(self, tag: str) -> str:
        with Session(self.engine) as session:
            knowledge = session.query(Knowledge).filter(Knowledge.tag == tag).first()
            if knowledge:
                return knowledge.contents
            return None