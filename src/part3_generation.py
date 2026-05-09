"""
Part 3 - Generation Module
Medical FAQ Assistant - RAG Project

Uses Groq API (Llama 3.3-70B) to generate answers from retrieved context.
For each query shows:  question -> retrieved context -> final answer
"""

import os
import json
from groq import Groq

# ─── CONFIG ───────────────────────────────────────────────────────────────────
PROCESSED_DIR = os.path.join(os.path.dirname(__file__), "..", "data", "processed")
GROQ_MODEL    = "llama-3.3-70b-versatile"   # free on Groq

SYSTEM_PROMPT = """You are a helpful and accurate Medical FAQ Assistant.
You answer user questions ONLY based on the provided medical context.
If the context does not contain enough information to answer the question, 
say: "I'm sorry, this information is not available in my knowledge base."
Keep answers clear, factual, and concise (2-4 sentences unless more detail is needed).
Do NOT make up information beyond what is given in the context."""


def get_groq_client(api_key: str):
    """Initialize and return a Groq client."""
    return Groq(api_key=api_key)


def generate_answer(query: str, context_chunks: list, client: Groq) -> dict:
    """
    Generate an answer for a query using retrieved context via Groq LLM.

    Returns a dict with:
        - question
        - context (formatted string)
        - answer
        - sources (list of doc_ids)
    """
    # Format context
    context_parts = []
    sources = []
    for i, chunk in enumerate(context_chunks, 1):
        context_parts.append(
            f"[Source {i} - {chunk['doc_id']}]:\n{chunk['text']}"
        )
        if chunk["doc_id"] not in sources:
            sources.append(chunk["doc_id"])

    context_str = "\n\n".join(context_parts)

    # Build messages
    user_message = f"""Context:
{context_str}

Question: {query}

Please answer the question based only on the context above."""

    # Call Groq API
    response = client.chat.completions.create(
        model=GROQ_MODEL,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user",   "content": user_message},
        ],
        temperature=0.2,
        max_tokens=512,
    )

    answer = response.choices[0].message.content.strip()

    return {
        "question": query,
        "context" : context_str,
        "answer"  : answer,
        "sources" : sources,
    }


def run_generation_demo(client, retriever_fn, queries: list = None):
    """
    Run the full generation pipeline on a list of queries.
    retriever_fn: callable(query) -> list of chunk dicts
    """
    if queries is None:
        from src.part2_retrieval import TEST_QUERIES
        queries = TEST_QUERIES

    results = []
    print("\n" + "=" * 60)
    print("  PART 3 — GENERATION MODULE (Groq + Llama 3)")
    print("=" * 60)

    for i, query in enumerate(queries, 1):
        print(f"\n[Query {i}/{len(queries)}]: {query}")
        print("-" * 60)

        # Retrieve context
        context_chunks = retriever_fn(query)

        # Generate answer
        result = generate_answer(query, context_chunks, client)

        print(f"  SOURCES  : {', '.join(result['sources'])}")
        print(f"  ANSWER   : {result['answer'][:200]}...")

        results.append(result)

    # Save
    out_path = os.path.join(PROCESSED_DIR, "generation_results.json")
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    print(f"\n[SAVED] Generation results -> {out_path}")
    return results


if __name__ == "__main__":
    # Quick standalone test
    import sys
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
    from src.part2_retrieval import build_retrievers, retrieve, TEST_QUERIES

    api_key = os.environ.get("GROQ_API_KEY", "")
    if not api_key:
        print("ERROR: Please set GROQ_API_KEY environment variable.")
        sys.exit(1)

    client = get_groq_client(api_key)
    chunks, texts, tfidf_ret, dense_ret = build_retrievers()

    def retriever_fn(query):
        return retrieve(query, tfidf_ret, dense_ret, chunks, method="dense")

    run_generation_demo(client, retriever_fn, TEST_QUERIES[:3])
