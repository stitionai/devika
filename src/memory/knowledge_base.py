from typing import Optional
from sqlmodel import Field, Session, SQLModel, create_engine
from src.config import Config
import faiss
import numpy as np
from sentence_transformers import SentenceTransformer


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
        self.knowledge_entries = self.get_all_knowledge_entries()
        self.model = SentenceTransformer('all-MiniLM-L6-v2')
        self.index = None
        self.update_index()

    def add_knowledge(self, tag: str, contents: str):
        knowledge = Knowledge(tag=tag, contents=contents)
        with Session(self.engine) as session:
            session.add(knowledge)
            session.commit()
            session.refresh(knowledge)  # Reload the object from the session
        self.knowledge_entries.append(knowledge)
        self.update_index()

    def update_index(self):
        if self.knowledge_entries:
            embeddings = self.model.encode([entry.contents for entry in self.knowledge_entries])
            self.index = faiss.IndexFlatL2(embeddings.shape[1])
            self.index.add(np.array(embeddings))
        else:
            self.index = None

    def get_knowledge(self, query: str) -> Optional[str]:
        if self.index:
            return self.search_knowledge(query)
        else:
            return None

    def search_knowledge(self, query: str) -> Optional[str]:
        query_embedding = self.model.encode([query])[0]
        _, indices = self.index.search(np.array([query_embedding]), 1)
        if indices.size > 0:
            return self.knowledge_entries[indices[0][0]].contents
        else:
            return None

    def get_all_knowledge_entries(self):
        with Session(self.engine) as session:
            return session.query(Knowledge).all()
