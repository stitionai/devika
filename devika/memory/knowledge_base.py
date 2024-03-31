"""Knowledge base module for Devika."""

from typing import Optional

from rank_bm25 import BM25Okapi  # type: ignore
from sqlalchemy import Select
from sqlmodel import Field, Session, SQLModel, create_engine

from devika.config import Config


# TODO: Add list of tags to knowledge
class Knowledge(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    tag: str
    contents: str


class KnowledgeBase:
    """Database for storing and retrieving knowledge items."""

    def __init__(self):
        config = Config()
        sqlite_path = config.get_sqlite_db()
        self.engine = create_engine(f"sqlite:///{sqlite_path}")
        SQLModel.metadata.create_all(self.engine)
        self.bm25 = None
        self.update_bm25()

    def update_bm25(self):
        with Session(self.engine) as session:
            knowledge_items = session.exec(Select(Knowledge.tag)).all()
            corpus = [item.tag.split() for item in knowledge_items]

            if not corpus:
                return

            self.bm25 = BM25Okapi(corpus)

    def get_knowledge(self, tag: str) -> str | None:
        if not self.bm25:
            return None

        with Session(self.engine) as session:
            scores = self.bm25.get_scores(tag.split())
            highest_score_index = scores.index(max(scores))
            knowledge = session.exec(Select(Knowledge)).all()[highest_score_index]
            if knowledge:
                return knowledge.contents

        return None
