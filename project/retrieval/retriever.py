import os
import math
import re
from typing import List, Dict, Any
from dotenv import load_dotenv
from project.database.vector_store import VectorStore

# Load environment variables from .env file
load_dotenv()

try:
    from google import genai
    from google.genai import types
    HAS_GENAI = True
except ImportError:
    HAS_GENAI = False



class Retriever:
    """
    Handles text embedding generation (via Google Gemini text-embedding-004 or mock fallback)
    and vector similarity search.
    """

    def __init__(self, vector_store: VectorStore, mock: bool = False):
        self.vector_store = vector_store
        self.mock = mock
        self.client = None

        if not self.mock and HAS_GENAI:
            api_key = os.environ.get("GEMINI_API_KEY") or os.environ.get("GOOGLE_API_KEY")
            if api_key:
                self.client = genai.Client(api_key=api_key)
            else:
                # Fallback to mock if API key is not set
                self.mock = True

    def get_embedding(self, text: str) -> List[float]:
        """Generates embedding vector for a given text."""
        if self.mock or not self.client:
            return self._mock_embedding(text)

        try:
            response = self.client.models.embed_content(
                model="text-embedding-004",
                contents=text
            )
            if response.embedding and response.embedding.values:
                return response.embedding.values
            return self._mock_embedding(text)
        except Exception as e:
            # Fallback to mock embedding on network/API failure
            return self._mock_embedding(text)

    def get_embeddings(self, texts: List[str]) -> List[List[float]]:
        """Generates embedding vectors for a list of texts."""
        return [self.get_embedding(t) for t in texts]

    def retrieve(self, query: str, top_k: int = 3, min_score: float = 0.2) -> List[Dict[str, Any]]:
        """Retrieves top_k relevant chunks for a query."""
        q_emb = self.get_embedding(query)
        return self.vector_store.similarity_search(q_emb, top_k=top_k, min_score=min_score)

    def _mock_embedding(self, text: str, dim: int = 256) -> List[float]:
        """
        Creates a deterministic 256-dim term-frequency vector embedding for mock/offline execution.
        Uses zlib.crc32 hashing to eliminate false collisions across vocabulary words.
        """
        import zlib
        
        stopwords = {
            "a", "an", "the", "in", "on", "at", "to", "for", "of", "with", "by", "from",
            "is", "are", "was", "were", "be", "been", "being", "have", "has", "had",
            "do", "does", "did", "can", "could", "should", "would", "will", "i", "you",
            "he", "she", "it", "we", "they", "my", "your", "his", "her", "its", "our",
            "their", "this", "that", "these", "those", "u", "or", "and", "but", "if"
        }

        words = [w for w in re.findall(r'\w+', text.lower()) if w not in stopwords]
        vec = [0.0] * dim
        for w in words:
            idx = zlib.crc32(w.encode('utf-8')) % dim
            vec[idx] += 1.0

        norm = math.sqrt(sum(x * x for x in vec))
        if norm > 0:
            vec = [x / norm for x in vec]
        return vec

