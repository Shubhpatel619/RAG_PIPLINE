# Internal Rubric: RAG Take-Home (do not share with candidate)

Calibrated for **1+ years of professional experience**. We are not looking for senior-level system design depth or production hardening. We are looking for: does this person understand what a RAG pipeline actually does (not just "call the framework"), do they handle the obvious failure mode (hallucinating an answer that isn't in the docs), and can they write code and a README a teammate could pick up.

## Scoring (100 pts)

| Area | Points | What to look for |
|---|---|---|
| Core functionality | 35 | Chunking is sensible (not one giant blob, not one chunk per character); retrieval actually narrows to relevant chunks rather than stuffing the whole corpus into the prompt; answer is grounded in retrieved text; citation names the actual source document. |
| "I don't know" handling | 15 | Ask a question not covered by the corpus (see test cases below) and confirm it says so rather than guessing. Single highest-signal check; weight it accordingly. |
| Code quality | 20 | Reasonable structure (ingestion/retrieval/generation are separable, not one 300-line `main()`); sane error handling (missing API key, empty corpus, empty query); no obviously copy-pasted boilerplate the candidate can't explain. |
| Tests | 10 | At least the required 3; do they test behavior (retrieval returns relevant chunk, fallback triggers) rather than trivial asserts. |
| README / communication | 10 | Can you run it from the README alone; do they explain *why* they made their chunking/retrieval choices, not just restate what the code does. |
| Judgment / bonus | 10 | Did they note tradeoffs unprompted (e.g., "TF-IDF instead of embeddings because X"); did they attempt any bonus item well (a half-done bonus is worth more than a skipped one, a broken one is worth less than skipping it). |

**Passing bar:** roughly 60/100. Hard floor: failing the "I don't know" check (test case 4 below) means the candidate does not pass, regardless of other scores.

## Calibration notes for 1-year experience

Expect and don't penalize:
- Using a framework (LangChain, LlamaIndex) instead of hand-rolling retrieval.
- In-memory/naive vector search (numpy cosine similarity, no real vector DB).
- Not handling concurrency, auth, or multi-user concerns, none of that is in scope.

One more flag not covered by the scoring table above: hard-coded API keys in source (should be read from env).

## Built-in test cases you can run against any submission

Ask these against `sample_corpus/` and check the answer:

1. "How do I reset my Aperture API key?" → should describe the dashboard revoke-and-regenerate flow (`api-reference.md`), not claim there's a reset endpoint (there explicitly isn't one).
2. "What's the current API rate limit?" → should say **100/min** (v3.1, current), not 60/min (superseded v2.0 value in `changelog.md`). Tests handling of conflicting/time-ordered info; bonus signal only, don't require it for a pass.
3. "Does Aperture support Asana?" → should say no / roadmap only, not fabricate support. (Out-of-scope, negative-answer test.)
4. "What's Aperture's refund policy for annual contracts?" → **not covered anywhere in the corpus.** The correct behavior is an explicit "not in the docs." This is the primary hallucination trap and the hard floor referenced in the Passing bar above.

## Suggested debrief-call questions

Use 2-3 of these, don't run through all of them:

- "How would this change if the corpus were 100,000 documents instead of 6?"
- "How would you know, systematically, if your retrieval was actually returning the right chunks, beyond eyeballing a few examples?"
- "What would you change if two documents gave conflicting answers and neither was clearly newer?"
- "Where could a malicious document in the corpus cause a problem, and how would you guard against it?" (relevant if they attempted the prompt-injection bonus, but fair to ask even if they didn't)
