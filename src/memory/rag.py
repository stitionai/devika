"""
Vector Search for Code Docs + Docs Loading
Implements RAG (Retrieval Augmented Generation) for code understanding
"""

import os
from typing import List, Dict, Optional
import chromadb
from chromadb.config import Settings
from chromadb.utils import embedding_functions

from src.bert.sentence import SentenceBERT
from src.config import Config

class CodeRAG:
    def __init__(self, project_name: str):
        config = Config()
        self.project_name = project_name.lower().replace(" ", "-")
        self.db_path = os.path.join(config.get_projects_dir(), ".vector_db")
        os.makedirs(self.db_path, exist_ok=True)

        # Initialize ChromaDB with persistence
        self.client = chromadb.PersistentClient(path=self.db_path)
        self.sentence_transformer = embedding_functions.SentenceTransformerEmbeddingFunction(
            model_name="all-MiniLM-L6-v2"
        )

        # Get or create collection for this project
        self.collection = self.client.get_or_create_collection(
            name=f"code_{self.project_name}",
            embedding_function=self.sentence_transformer
        )

    def chunk_code(self, code: str, chunk_size: int = 1000) -> List[str]:
        """Split code into smaller chunks while preserving context."""
        chunks = []
        lines = code.split('\n')
        current_chunk = []
        current_size = 0

        for line in lines:
            line_size = len(line)
            if current_size + line_size > chunk_size and current_chunk:
                chunks.append('\n'.join(current_chunk))
                current_chunk = []
                current_size = 0
            current_chunk.append(line)
            current_size += line_size

        if current_chunk:
            chunks.append('\n'.join(current_chunk))
        return chunks

    def add_code(self, filename: str, code: str):
        """Add code to the vector database with chunking."""
        chunks = self.chunk_code(code)

        # Generate unique IDs for chunks
        chunk_ids = [f"{filename}_{i}" for i in range(len(chunks))]

        # Add chunks to collection
        self.collection.add(
            documents=chunks,
            ids=chunk_ids,
            metadatas=[{"filename": filename, "chunk": i} for i in range(len(chunks))]
        )

    def query_similar(self, query: str, n_results: int = 5) -> List[Dict]:
        """Query the vector database for similar code chunks."""
        results = self.collection.query(
            query_texts=[query],
            n_results=n_results
        )

        return [{
            "text": doc,
            "metadata": meta,
            "distance": dist
        } for doc, meta, dist in zip(
            results["documents"][0],
            results["metadatas"][0],
            results["distances"][0]
        )]

    def summarize_code(self, code: str) -> str:
        """Extract key information from code using SentenceBERT."""
        bert = SentenceBERT(code)
        keywords = bert.extract_keywords(top_n=10)
        return ", ".join([kw[0] for kw in keywords])

    def get_context(self, query: str, n_results: int = 5) -> Dict:
        """Get relevant code context for a query."""
        similar_chunks = self.query_similar(query, n_results)

        context = {
            "relevant_code": [],
            "summary": [],
            "files": set()
        }

        for chunk in similar_chunks:
            context["relevant_code"].append({
                "code": chunk["text"],
                "file": chunk["metadata"]["filename"],
                "relevance": 1 - chunk["distance"]  # Convert distance to similarity score
            })
            context["files"].add(chunk["metadata"]["filename"])
            context["summary"].append(self.summarize_code(chunk["text"]))

        return context
