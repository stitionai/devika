from typing import Optional
from sqlmodel import Field, Session, SQLModel, create_engine
from rank_bm25 import BM25Okapi  # Added BM25Okapi import
from src.config import Config

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
        self.knowledge_entries = self.get_all_knowledge_entries()  # New: Load knowledge entries
        if self.knowledge_entries:
            self.tokenized_contents = [entry.contents.split() for entry in self.knowledge_entries]
            self.bm25 = BM25Okapi(self.tokenized_contents)
        else:
            self.tokenized_contents = []
            self.bm25 = None

    def add_knowledge(self, tag: str, contents: str):
        knowledge = Knowledge(tag=tag, contents=contents)
        with Session(self.engine) as session:
            session.add(knowledge)
            session.commit()
        self.knowledge_entries.append(knowledge)  # Update knowledge entries

    def get_knowledge(self, tag: str) -> str:
        if self.bm25:  # Check if BM25 is initialized
            return self.search_knowledge(tag)
        else:
            return self.search_knowledge_exact(tag)

    def search_knowledge(self, tag: str) -> str:
        scores = self.bm25.get_scores(tag.split())  # Calculate BM25 scores
        max_score_index = scores.index(max(scores))
        return self.knowledge_entries[max_score_index].contents

    def search_knowledge_exact(self, tag: str) -> str:
        with Session(self.engine) as session:
            knowledge = session.query(Knowledge).filter(Knowledge.tag == tag).first()
            if knowledge:
                return knowledge.contents
            return None

    def get_all_knowledge_entries(self):
        with Session(self.engine) as session:
            return session.query(Knowledge).all()
