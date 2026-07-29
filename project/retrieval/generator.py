import os
from typing import List, Tuple, Dict, Any
from dotenv import load_dotenv

from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.documents import Document

load_dotenv()

REFUSAL_MESSAGE = "I do not have enough information in the provided documentation to answer your question."


class LangChainGenerator:
    """
    Generates grounded answers using LangChain ChatGoogleGenerativeAI.
    Strictly enforces zero-hallucination refusal rules and document citations.
    """

    def __init__(self, model_name: str = "gemini-flash-latest"):

        api_key = os.environ.get("GEMINI_API_KEY") or os.environ.get("GOOGLE_API_KEY")
        if not api_key:
            raise ValueError("GEMINI_API_KEY is missing. Please set GEMINI_API_KEY in your .env file or environment.")

        self.llm = ChatGoogleGenerativeAI(
            model=model_name,
            google_api_key=api_key,
            temperature=0.1
        )

        self.system_prompt = (
            "You are an AI Assistant that answers user questions based strictly on the provided Aperture documentation context.\n"
            "STRICT RULES:\n"
            "1. Answer ONLY using the facts explicitly stated in the provided context chunks.\n"
            "2. Do NOT use outside general knowledge or make assumptions.\n"
            "3. If the provided context chunks do not contain sufficient information to answer the question completely, you MUST respond EXACTLY with:\n"
            f'"{REFUSAL_MESSAGE}"\n'
            "4. Mention/cite the source document filename(s) (e.g. api-reference.md, billing-faq.md) that supported your answer."
        )

        self.prompt_template = ChatPromptTemplate.from_messages([
            ("system", self.system_prompt),
            ("human", "Question: {query}\n\nRetrieved Documentation Context:\n{context}\n\nAnswer:")
        ])

    def generate_answer(self, query: str, doc_score_tuples: List[Tuple[Document, float]]) -> Tuple[str, List[str]]:
        """
        Given a query and retrieved LangChain Document objects:
        - Constructs prompt context
        - Calls ChatGoogleGenerativeAI chain
        - Returns (answer_text, list_of_cited_sources)
        """
        if not doc_score_tuples:
            return REFUSAL_MESSAGE, []

        documents = [t[0] for t in doc_score_tuples]
        sources = sorted(list(set(doc.metadata.get("filename", "unknown.md") for doc in documents)))

        context_blocks = []
        for i, doc in enumerate(documents, start=1):
            fn = doc.metadata.get("filename", "unknown.md")
            context_blocks.append(f"--- Document {i} [Source: {fn}] ---\n{doc.page_content}")

        context_str = "\n\n".join(context_blocks)

        chain = self.prompt_template | self.llm
        response = chain.invoke({"query": query, "context": context_str})

        raw_content = response.content
        if isinstance(raw_content, str):
            answer = raw_content.strip()
        elif isinstance(raw_content, list):
            answer = "".join([block.get("text", "") if isinstance(block, dict) else str(block) for block in raw_content]).strip()
        else:
            answer = str(raw_content).strip() if raw_content else REFUSAL_MESSAGE

        if not answer:
            answer = REFUSAL_MESSAGE


        if "not have enough information" in answer.lower() or "not in the docs" in answer.lower():
            return REFUSAL_MESSAGE, []

        return answer, sources
