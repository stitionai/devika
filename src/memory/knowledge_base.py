from sqlmodel import select
from typing import List
import numpy as np
from rank_bm25 import BM25Okapi  # Make sure to install this package

class KnowledgeBase:
    def __init__(self):
        config = Config()
        sqlite_path = config.get_sqlite_db()
        self.engine = create_engine(f"sqlite:///{sqlite_path}")
        SQLModel.metadata.create_all(self.engine)

        # Load all knowledge entries from the database
        with Session(self.engine) as session:
            query = select(Knowledge)
            self.knowledge_entries = session.exec(query).all()

        # Preprocess knowledge contents
        self.tokenized_contents = [entry.contents.lower().split() for entry in self.knowledge_entries]
        self.bm25 = BM25Okapi(self.tokenized_contents)

    def add_knowledge(self, tag: str, contents: str):
        knowledge = Knowledge(tag=tag, contents=contents)
        with Session(self.engine) as session:
            session.add(knowledge)
            session.commit()

            # Update in-memory data structures
            self.knowledge_entries.append(knowledge)
            self.tokenized_contents.append(contents.lower().split())
            self.bm25 = BM25Okapi(self.tokenized_contents)

    def get_knowledge(self, tag: str, n_results: int = 5) -> List[str]:
        # Calculate BM25 scores for the query
        tokenized_query = tag.lower().split()
        scores = self.bm25.get_scores(tokenized_query)

        # Sort knowledge entries based on scores
        sorted_indices = np.argsort(scores)[::-1]

        # Return top N knowledge entries
        results = []
        for idx in sorted_indices[:n_results]:
            results.append(self.knowledge_entries[idx].contents)
        return results
