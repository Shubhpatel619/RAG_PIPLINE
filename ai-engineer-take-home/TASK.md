# Take-Home Task: RAG-Based Q&A Assistant

**Role:** AI/LLM Engineer
**Level:** 1+ years professional software engineering experience
**Format:** Take-home, submitted as code
**Time budget:** Plan for 3-5 focused hours. You have 3 calendar days to submit; if you need more time, tell us, no penalty for asking.

## Overview

You're given a small folder of documentation for a fictional product called **Aperture** (see `sample_corpus/`). Your task is to build a command-line tool that answers user questions using only the information in these documents, retrieving relevant passages before generating an answer (retrieval-augmented generation, RAG), rather than relying on the model's general knowledge.

We care less about a polished UI and more about whether the core mechanics are correct, the edge cases are handled deliberately, and the code is something a teammate could read and extend.

## What to build

A script or small CLI, run like:

```bash
python qa.py "How do I reset my Aperture API key?"
```

It should:

1. **Ingest and chunk** the documents in `sample_corpus/` into retrievable units.
2. **Embed and index** those chunks (any approach: a hosted embeddings API, a local model, or even TF-IDF/BM25 if you want to avoid an API dependency, your call, just explain the tradeoff).
3. **Retrieve** the top-k chunks relevant to the question.
4. **Generate an answer** using an LLM, grounded in the retrieved chunks, and **cite which document(s)** the answer came from.
5. **Refuse gracefully** when the answer isn't in the docs. If a question isn't covered by `sample_corpus/`, the tool should say so explicitly, not guess or hallucinate. This is the single most important behavior we're testing.

## Constraints

- **Python 3.10+.**
- **LLM access:** use any provider (OpenAI, Anthropic, a local model, whatever you have available). Read the API key from an environment variable, never hard-code it. If you don't want to spend API budget on this, that's fine: implement a `--mock` mode (or similar) that swaps in a deterministic stub so we can run and grade your retrieval/orchestration logic without live API calls. Tell us in the README which mode to use.
- **Libraries:** no restriction. You may use a framework (LangChain, LlamaIndex, etc.) if you're comfortable with it, or write the pipeline directly. We're evaluating whether you understand what's happening, not which library you picked.
- Should run after `pip install -r requirements.txt` with one command. No manual setup steps beyond an API key.

## Deliverables

1. **Code** (a git repo, zip, or GitHub link).
2. **`requirements.txt`** or equivalent.
3. **README** covering:
   - How to run it (setup + example commands).
   - How it works, briefly: chunking strategy, retrieval approach, how the "don't know" case is detected.
   - What you'd do differently with more time, and why you made the tradeoffs you did.
4. **At least 3 automated tests** (pytest or similar) covering, at minimum: chunking/retrieval behaving as expected, and the "not in the docs" fallback actually triggering.

## Bonus (optional, not required to pass)

Pick zero or more if you have time left and want to show more:

- A small evaluation set (5-10 question/expected-answer pairs) with a script that scores your pipeline against it.
- Handling for documents that contradict each other over time (see `changelog.md`, hint: something changes between versions), and answering with the current state rather than an outdated one.
- A second callable "tool" alongside retrieval (e.g., a date lookup or simple calculator) with the model deciding when to use it, a minimal step toward agentic behavior.
- Basic resistance to instructions embedded inside a document (a naive prompt-injection guard).

## Submission

Send the repo/zip/link plus a one-line note on how long you spent. We'll review the code async, then talk through your design decisions in a 30-minute follow-up conversation, no live coding in that call, just discussion.
