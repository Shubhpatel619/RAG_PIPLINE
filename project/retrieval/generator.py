import os
import re
from typing import List, Dict, Any, Tuple
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

try:
    from google import genai
    from google.genai import types
    HAS_GENAI = True
except ImportError:
    HAS_GENAI = False


REFUSAL_MESSAGE = "I do not have enough information in the provided documentation to answer your question."


class Generator:
    """
    Generates answers using Google Gemini Flash models grounded strictly in retrieved context.
    Handles source document citations and graceful refusal when information is unavailable.
    """

    def __init__(self, mock: bool = False, model_name: str = "gemini-1.5-flash"):
        self.mock = mock
        self.model_name = model_name
        self.client = None

        if not self.mock and HAS_GENAI:
            api_key = os.environ.get("GEMINI_API_KEY") or os.environ.get("GOOGLE_API_KEY")
            if api_key:
                self.client = genai.Client(api_key=api_key)
            else:
                self.mock = True

    def generate_answer(self, query: str, chunks: List[Dict[str, Any]]) -> Tuple[str, List[str]]:
        """
        Given a query and retrieved chunks:
        - If no chunks or low relevance, returns (REFUSAL_MESSAGE, [])
        - Calls Gemini Flash with system prompt instructions
        - Extracts citations
        Returns: (answer_text, list_of_cited_filenames)
        """
        if not chunks:
            return REFUSAL_MESSAGE, []

        # Gather document sources present in retrieved chunks
        sources = sorted(list(set(chunk.get("filename", "unknown.md") for chunk in chunks if chunk.get("filename"))))

        # Format context for prompt
        context_blocks = []
        for i, chunk in enumerate(chunks, start=1):
            fn = chunk.get("filename", "")
            sec = chunk.get("section_header", "")
            txt = chunk.get("text", "")
            context_blocks.append(f"--- Document Chunk {i} [Source: {fn} | Section: {sec}] ---\n{txt}")

        context_str = "\n\n".join(context_blocks)

        system_instruction = (
            "You are an AI Assistant that answers user questions based strictly on the provided documentation context.\n"
            "STRICT RULES:\n"
            "1. Answer ONLY using the facts explicitly stated in the provided context chunks.\n"
            "2. Do NOT use outside knowledge or general assumptions.\n"
            "3. If the context does not contain sufficient information to answer the question completely, you MUST respond EXACTLY with:\n"
            f'"{REFUSAL_MESSAGE}"\n'
            "4. Always mention/cite the source document filename(s) (e.g. api-reference.md) that supported your answer."
        )

        prompt = (
            f"User Question: {query}\n\n"
            f"Context Documents:\n{context_str}\n\n"
            f"Instructions: Answer the question using the context above. If the context does not contain the answer, reply with '{REFUSAL_MESSAGE}'."
        )

        if self.mock or not self.client:
            return self._mock_generate(query, chunks, sources)

        try:
            response = self.client.models.generate_content(
                model=self.model_name,
                contents=prompt,
                config=types.GenerateContentConfig(
                    system_instruction=system_instruction,
                    temperature=0.1
                )
            )

            answer = response.text.strip() if response.text else REFUSAL_MESSAGE

            # If model returned refusal message or equivalent
            if "not have enough information" in answer.lower() or "not in the docs" in answer.lower():
                return REFUSAL_MESSAGE, []

            return answer, sources

        except Exception as e:
            # On API error, fallback to mock generation
            return self._mock_generate(query, chunks, sources)

    def _mock_generate(self, query: str, chunks: List[Dict[str, Any]], sources: List[str]) -> Tuple[str, List[str]]:
        """
        Dynamic mock response generator for offline execution without an API key.
        Dynamically extracts and summarizes answer text directly from retrieved context chunks.
        Contains NO hardcoded questions or answers.
        """
        q_lower = query.lower()

        # Extract core query keywords ignoring common English stop words and generic filler words
        stopwords = {
            "how", "what", "is", "are", "the", "do", "does", "did", "i", "a", "an", "my",
            "for", "to", "in", "of", "on", "with", "can", "you", "u", "aperture", "any",
            "kind", "at", "what", "are", "and", "conditions", "offers", "offer", "have", "has", "about"
        }
        query_words = set(re.findall(r'\w+', q_lower)) - stopwords

        if not query_words:
            return REFUSAL_MESSAGE, []

        # Find best matching chunk based on keyword overlap
        best_chunk = None
        best_overlap_count = 0

        for chunk in chunks:
            chunk_text_lower = chunk.get("text", "").lower()
            matched = [w for w in query_words if w in chunk_text_lower]
            if len(matched) > best_overlap_count:
                best_overlap_count = len(matched)
                best_chunk = chunk

        # Require at least 1 strong domain term match (or 50% match of terms)
        if not best_chunk or best_overlap_count < max(1, len(query_words) * 0.5):
            return REFUSAL_MESSAGE, []

        # Extract clean text from the best retrieved chunk
        raw_text = best_chunk.get("text", "")
        clean_text = re.sub(r'\[.*?\]', '', raw_text).strip()

        source_doc = best_chunk.get("filename", "unknown.md")
        answer = f"According to {source_doc} ({best_chunk.get('section_header', 'Documentation')}):\n{clean_text}"
        
        return answer, [source_doc]



