import sys
import os
import argparse

# Ensure project root is in sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from dotenv import load_dotenv
from project.retrieval.pipeline import RAGPipeline


def main():
    # Load API keys from .env file if present
    load_dotenv()

    parser = argparse.ArgumentParser(description="Aperture RAG Q&A Assistant CLI")
    parser.add_argument("query", type=str, help="The question to ask the Aperture documentation.")
    parser.add_argument("--mock", action="store_true", help="Run in mock/offline mode without live LLM/embedding API calls.")
    parser.add_argument("--top-k", type=int, default=3, help="Number of context chunks to retrieve.")
    parser.add_argument("--corpus", type=str, default="ai-engineer-take-home/sample_corpus", help="Path to sample corpus directory.")
    parser.add_argument("--reindex", action="store_true", help="Force re-indexing of sample corpus.")

    args = parser.parse_args()

    pipeline = RAGPipeline(corpus_dir=args.corpus, mock=args.mock)
    if args.reindex:
        indexed_count = pipeline.ingest(force_reindex=True)
        print(f"[INFO] Re-indexed {indexed_count} document chunks.")

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
