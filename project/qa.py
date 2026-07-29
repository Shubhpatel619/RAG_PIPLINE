import sys
import os
import argparse

# Ensure project root is in sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from dotenv import load_dotenv
from project.retrieval.pipeline import RAGPipeline


def main():
    load_dotenv()

    api_key = os.environ.get("GEMINI_API_KEY") or os.environ.get("GOOGLE_API_KEY")
    if not api_key:
        print("[ERROR] GEMINI_API_KEY is missing. Please set GEMINI_API_KEY in your .env file or environment.")
        sys.exit(1)

    parser = argparse.ArgumentParser(description="Aperture LangChain RAG Q&A Assistant CLI")
    parser.add_argument("query", type=str, help="The question to ask the Aperture documentation.")
    parser.add_argument("--top-k", type=int, default=3, help="Number of context chunks to retrieve.")
    parser.add_argument("--corpus", type=str, default="ai-engineer-take-home/sample_corpus", help="Path to sample corpus directory.")
    parser.add_argument("--reindex", action="store_true", help="Force re-indexing of sample corpus into FAISS.")

    args = parser.parse_args()

    pipeline = RAGPipeline(corpus_dir=args.corpus)
    if args.reindex:
        count = pipeline.ingest(force_reindex=True)
        print(f"[INFO] Re-indexed {count} document chunks into LangChain FAISS VectorStore.")

    result = pipeline.answer_question(args.query, top_k=args.top_k)

    print("\n" + "=" * 60)
    print(f"QUESTION: {result['query']}")
    print("=" * 60)
    print("\nANSWER:\n")
    print(result['answer'])
    
    if result['citations']:
        print("\nCITATIONS:")
        for citation in result['citations']:
            print(f" - {citation}")
            
    print("=" * 60 + "\n")


if __name__ == "__main__":
    main()
