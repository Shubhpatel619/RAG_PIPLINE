import sqlite3
import json
from pathlib import Path
from typing import List, Dict, Any, Tuple
import numpy as np


class VectorStore:
    """
    Lightweight, persistent Vector Store using SQLite and NumPy cosine similarity.
    """

    def __init__(self, db_path: str = "project/database/vector_store.db"):
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_db()

    def _init_db(self):
        """Initializes SQLite schema."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS chunks (
                    chunk_id TEXT PRIMARY KEY,
                    doc_id TEXT,
                    filename TEXT,
                    title TEXT,
                    section_header TEXT,
                    text TEXT,
                    embedding TEXT
                )
            """)
            conn.commit()

    def clear(self):
        """Clears all records in vector store."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM chunks")
            conn.commit()

    def add_chunks(self, chunks: List[Dict[str, Any]], embeddings: List[List[float]]):
        """
        Stores chunks and their vector embeddings in SQLite.
        """
        if len(chunks) != len(embeddings):
            raise ValueError("Chunks and embeddings must have equal length.")

        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            for chunk, emb in zip(chunks, embeddings):
                cursor.execute("""
                    INSERT OR REPLACE INTO chunks (chunk_id, doc_id, filename, title, section_header, text, embedding)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                """, (
                    chunk["chunk_id"],
                    chunk.get("doc_id", ""),
                    chunk.get("filename", ""),
                    chunk.get("title", ""),
                    chunk.get("section_header", ""),
                    chunk.get("text", ""),
                    json.dumps(emb)
                ))
            conn.commit()

    def get_all_chunks(self) -> List[Tuple[Dict[str, Any], np.ndarray]]:
        """Retrieves all chunks and associated embedding numpy arrays."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT chunk_id, doc_id, filename, title, section_header, text, embedding FROM chunks")
            rows = cursor.fetchall()

        results = []
        for row in rows:
            chunk = {
                "chunk_id": row[0],
                "doc_id": row[1],
                "filename": row[2],
                "title": row[3],
                "section_header": row[4],
                "text": row[5]
            }
            emb = np.array(json.loads(row[6]), dtype=np.float32)
            results.append((chunk, emb))
        return results

    def similarity_search(self, query_embedding: List[float], top_k: int = 3, min_score: float = 0.2) -> List[Dict[str, Any]]:
        """
        Performs cosine similarity search against stored embeddings.
        Returns top_k matching chunks with similarity score attached.
        """
        all_data = self.get_all_chunks()
        if not all_data:
            return []

        q_vec = np.array(query_embedding, dtype=np.float32)
        q_norm = np.linalg.norm(q_vec)
        if q_norm == 0:
            return []

        q_vec_norm = q_vec / q_norm

        scored_chunks = []
        for chunk, emb_vec in all_data:
            emb_norm = np.linalg.norm(emb_vec)
            if emb_norm == 0:
                continue
            score = float(np.dot(q_vec_norm, emb_vec / emb_norm))
            if score >= min_score:
                chunk_copy = dict(chunk)
                chunk_copy["score"] = score
                scored_chunks.append(chunk_copy)

        scored_chunks.sort(key=lambda x: x["score"], reverse=True)
        return scored_chunks[:top_k]

    def count(self) -> int:
        """Returns total chunk count."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM chunks")
            return cursor.fetchone()[0]
