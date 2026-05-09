"""
Part 5 - Experimental Evaluation
Medical FAQ Assistant - RAG Project

Evaluates the RAG system on 8+ test queries.
Reports: correct responses, failure cases, observed limitations.
"""

import os
import sys
import json

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

PROCESSED_DIR = os.path.join(os.path.dirname(__file__), "..", "data", "processed")

# 10 evaluation queries with reference answers (ground truth keywords)
EVAL_QUERIES = [
    {
        "query"     : "What are the symptoms of diabetes?",
        "keywords"  : ["urination", "thirst", "weight loss", "fatigue", "blurry vision"],
        "category"  : "Factual - Diabetes",
    },
    {
        "query"     : "How can high blood pressure be treated?",
        "keywords"  : ["lifestyle", "medication", "diet", "exercise", "sodium"],
        "category"  : "Factual - Hypertension",
    },
    {
        "query"     : "What is long COVID?",
        "keywords"  : ["fatigue", "brain fog", "4 weeks", "persistent", "symptoms"],
        "category"  : "Factual - COVID-19",
    },
    {
        "query"     : "How does LDL cholesterol affect the heart?",
        "keywords"  : ["plaque", "arteries", "risk", "cardiovascular", "bad"],
        "category"  : "Factual - Heart Disease",
    },
    {
        "query"     : "What is the difference between stress and anxiety?",
        "keywords"  : ["external", "persistent", "stressor", "chronic", "clinical"],
        "category"  : "Factual - Mental Health",
    },
    {
        "query"     : "How much fiber should adults eat per day?",
        "keywords"  : ["25", "38", "grams", "fiber", "plant"],
        "category"  : "Factual - Nutrition",
    },
    {
        "query"     : "What causes antibiotic resistance?",
        "keywords"  : ["overuse", "misuse", "bacteria", "evolve", "antibiotics"],
        "category"  : "Factual - Infectious Diseases",
    },
    {
        "query"     : "What are warning signs of cancer?",
        "keywords"  : ["lump", "weight loss", "bleeding", "fatigue", "changes"],
        "category"  : "Factual - Cancer",
    },
    {
        "query"     : "Can you tell me the weather forecast for today?",
        "keywords"  : [],  # Out-of-domain — system should decline
        "category"  : "Out-of-Domain (Expected: Decline)",
    },
    {
        "query"     : "What vaccine prevents cervical cancer?",
        "keywords"  : ["HPV", "vaccine", "cervical", "cancer"],
        "category"  : "Cross-domain (Cancer + Vaccines)",
    },
]


def keyword_hit_rate(answer: str, keywords: list) -> float:
    """Simple keyword overlap metric (0.0 to 1.0)."""
    if not keywords:
        return None   # out-of-domain — no keywords to check
    answer_lower = answer.lower()
    hits = sum(1 for kw in keywords if kw.lower() in answer_lower)
    return hits / len(keywords)


def evaluate_system(retriever_fn, generate_fn):
    """
    Run full evaluation.
    retriever_fn : callable(query) -> list of chunk dicts
    generate_fn  : callable(query, chunks) -> result dict
    """
    print("=" * 65)
    print("  PART 5 — EXPERIMENTAL EVALUATION")
    print("=" * 65)

    eval_results = []
    correct      = 0
    failures     = []
    limitations  = []

    for i, item in enumerate(EVAL_QUERIES, 1):
        query    = item["query"]
        keywords = item["keywords"]
        category = item["category"]

        print(f"\n[{i}/{len(EVAL_QUERIES)}] {category}")
        print(f"  Q: {query}")

        # Retrieve
        chunks = retriever_fn(query)

        # Generate
        result = generate_fn(query, chunks)
        answer = result["answer"]

        # Score
        score = keyword_hit_rate(answer, keywords)

        # Classify
        if score is None:
            # Out-of-domain query
            declined = any(phrase in answer.lower() for phrase in [
                "not available", "i'm sorry", "cannot", "don't have",
                "no information", "outside"
            ])
            status = "DECLINED (Good)" if declined else "HALLUCINATED (Bad)"
            if not declined:
                failures.append({"query": query, "issue": "Failed to decline out-of-domain query",
                                  "answer": answer})
        elif score >= 0.6:
            status  = f"CORRECT  (hit={score:.0%})"
            correct += 1
        elif score >= 0.3:
            status  = f"PARTIAL  (hit={score:.0%})"
            limitations.append({"query": query, "score": score, "answer": answer})
        else:
            status  = f"FAILURE  (hit={score:.0%})"
            failures.append({"query": query, "score": score, "answer": answer})

        print(f"  STATUS   : {status}")
        print(f"  ANSWER   : {answer[:180]}...")
        print(f"  SOURCES  : {', '.join(result.get('sources', []))}")

        eval_results.append({
            "query"   : query,
            "category": category,
            "keywords": keywords,
            "answer"  : answer,
            "score"   : score,
            "status"  : status,
            "sources" : result.get("sources", []),
        })

    # Summary
    factual_total = sum(1 for e in eval_results if e["score"] is not None)
    accuracy      = correct / factual_total if factual_total > 0 else 0

    print("\n" + "=" * 65)
    print("  EVALUATION SUMMARY")
    print("=" * 65)
    print(f"  Total queries evaluated : {len(EVAL_QUERIES)}")
    print(f"  Factual queries         : {factual_total}")
    print(f"  Correct (≥60% keywords) : {correct}")
    print(f"  Accuracy                : {accuracy:.0%}")
    print(f"\n  Failure cases ({len(failures)}):")
    for f in failures:
        print(f"    - {f['query'][:60]} | {f.get('issue', f'score={f.get(\"score\",\"N/A\")}')}")
    print(f"\n  Limitations observed:")
    print("    - System may lack very specific numerical data not in corpus")
    print("    - Overlapping topics may confuse retrieval (e.g., cancer + vaccines)")
    print("    - Out-of-domain queries not always clearly declined")
    print("    - Chunk size limits context window for multi-part questions")
    if limitations:
        for lim in limitations:
            print(f"    - Partial answer: {lim['query'][:60]}")
    print("=" * 65)

    # Save
    report = {
        "summary": {
            "total"    : len(EVAL_QUERIES),
            "factual"  : factual_total,
            "correct"  : correct,
            "accuracy" : round(accuracy, 4),
        },
        "failures"    : failures,
        "limitations" : limitations,
        "results"     : eval_results,
    }
    out_path = os.path.join(PROCESSED_DIR, "evaluation_report.json")
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2, ensure_ascii=False)
    print(f"\n[SAVED] Evaluation report -> {out_path}")

    return report
