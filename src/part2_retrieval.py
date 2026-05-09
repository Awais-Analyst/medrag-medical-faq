"""
Part 2 - Embeddings and Retrieval Module
Medical FAQ Assistant - RAG Project

Implements:
  - TF-IDF Retrieval (classical keyword-based)
  - Dense Embedding Retrieval (Sentence Transformers + FAISS)
  - Saves index to disk for fast reloads on Streamlit Cloud
  - Comparison of both methods on 8 test queries
"""

import os
import sys
import json
import time
import pickle
import numpy as np

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from sentence_transformers import SentenceTransformer
import faiss

# ─── CONFIG ───────────────────────────────────────────────────────────────────
BASE_DIR       = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PROCESSED_DIR  = os.path.join(BASE_DIR, "data", "processed")
CHUNKS_FILE    = os.path.join(PROCESSED_DIR, "chunks.json")
TFIDF_PKL      = os.path.join(PROCESSED_DIR, "tfidf_vectorizer.pkl")
FAISS_IDX      = os.path.join(PROCESSED_DIR, "faiss_index.bin")
EMBEDDINGS_NPY = os.path.join(PROCESSED_DIR, "embeddings.npy")

EMBED_MODEL = "all-MiniLM-L6-v2"
TOP_K       = 3

TEST_QUERIES = [
    "What are the symptoms of diabetes?",
    "How can high blood pressure be treated?",
    "What is long COVID and its effects?",
    "How does cholesterol affect heart health?",
    "What is the difference between stress and anxiety?",
    "How much water should a person drink daily?",
    "What causes antibiotic resistance?",
    "What are common warning signs of cancer?",
]


# ─── LOAD CHUNKS ──────────────────────────────────────────────────────────────
def load_chunks(chunks_file=CHUNKS_FILE):
    with open(chunks_file, "r", encoding="utf-8") as f:
        chunks = json.load(f)
    texts = [c["text"] for c in chunks]
    return chunks, texts


# ─────────────────────────────────────────────────────────────────────────────
#  METHOD 1: TF-IDF RETRIEVAL
# ─────────────────────────────────────────────────────────────────────────────
class TFIDFRetriever:
    def __init__(self, texts, pkl_path=TFIDF_PKL):
        if os.path.exists(pkl_path):
            print("  [TF-IDF] Loading saved vectorizer from disk...")
            with open(pkl_path, "rb") as f:
                saved = pickle.load(f)
            self.vectorizer  = saved["vectorizer"]
            self.tfidf_matrix = saved["matrix"]
        else:
            print("  [TF-IDF] Building vectorizer...")
            self.vectorizer = TfidfVectorizer(
                stop_words="english", ngram_range=(1, 2), max_features=10000
            )
            self.tfidf_matrix = self.vectorizer.fit_transform(texts)
            with open(pkl_path, "wb") as f:
                pickle.dump({"vectorizer": self.vectorizer,
                             "matrix": self.tfidf_matrix}, f)
            print(f"  [TF-IDF] Saved -> {pkl_path}")

    def retrieve(self, query, top_k=TOP_K):
        query_vec = self.vectorizer.transform([query])
        scores    = cosine_similarity(query_vec, self.tfidf_matrix).flatten()
        top_idx   = np.argsort(scores)[::-1][:top_k]
        return top_idx.tolist(), scores[top_idx].tolist()


# ─────────────────────────────────────────────────────────────────────────────
#  METHOD 2: DENSE EMBEDDING RETRIEVAL
# ─────────────────────────────────────────────────────────────────────────────
class DenseRetriever:
    def __init__(self, texts, idx_path=FAISS_IDX, emb_path=EMBEDDINGS_NPY):
        print("  [Dense] Loading Sentence Transformer model...")
        self.model = SentenceTransformer(EMBED_MODEL)

        if os.path.exists(idx_path) and os.path.exists(emb_path):
            print("  [Dense] Loading saved FAISS index from disk...")
            self.index = faiss.read_index(idx_path)
        else:
            print("  [Dense] Building FAISS index (first time)...")
            embeddings = self.model.encode(
                texts, show_progress_bar=True, convert_to_numpy=True
            )
            faiss.normalize_L2(embeddings)
            np.save(emb_path, embeddings)

            dim        = embeddings.shape[1]
            self.index = faiss.IndexFlatIP(dim)
            self.index.add(embeddings)
            faiss.write_index(self.index, idx_path)
            print(f"  [Dense] Saved index -> {idx_path}")

        print(f"  [Dense] FAISS index ready ({self.index.ntotal} vectors).")

    def retrieve(self, query, top_k=TOP_K):
        q_emb = self.model.encode([query], convert_to_numpy=True)
        faiss.normalize_L2(q_emb)
        scores, indices = self.index.search(q_emb, top_k)
        return indices[0].tolist(), scores[0].tolist()


# ─── COMPARISON RUNNER ────────────────────────────────────────────────────────
def run_comparison(tfidf_ret, dense_ret, chunks, queries=TEST_QUERIES, top_k=TOP_K):
    results = []
    print("\n" + "=" * 70)
    print("  RETRIEVAL COMPARISON  (TF-IDF  vs  Dense Embeddings)")
    print("=" * 70)

    for qi, query in enumerate(queries, 1):
        print(f"\n[Query {qi}] {query}")
        print("-" * 70)

        t0 = time.time()
        tfidf_idx, tfidf_scores = tfidf_ret.retrieve(query, top_k)
        tfidf_time = time.time() - t0

        t0 = time.time()
        dense_idx, dense_scores = dense_ret.retrieve(query, top_k)
        dense_time = time.time() - t0

        print(f"  TF-IDF ({tfidf_time*1000:.1f}ms)  |  Dense ({dense_time*1000:.1f}ms)")

        tfidf_chunks = [chunks[i] for i in tfidf_idx]
        dense_chunks = [chunks[i] for i in dense_idx]

        for rank in range(top_k):
            tf_c = tfidf_chunks[rank]
            dn_c = dense_chunks[rank]
            print(f"  Rank {rank+1}:")
            print(f"    TF-IDF [{tfidf_scores[rank]:.4f}] {tf_c['doc_id']}  |  "
                  f"{tf_c['text'][:70]}...")
            print(f"    Dense  [{dense_scores[rank]:.4f}] {dn_c['doc_id']}  |  "
                  f"{dn_c['text'][:70]}...")

        results.append({
            "query"       : query,
            "tfidf_chunks": [{"chunk_id": c["chunk_id"], "doc_id": c["doc_id"],
                               "text": c["text"], "score": float(s)}
                              for c, s in zip(tfidf_chunks, tfidf_scores)],
            "dense_chunks": [{"chunk_id": c["chunk_id"], "doc_id": c["doc_id"],
                               "text": c["text"], "score": float(s)}
                              for c, s in zip(dense_chunks, dense_scores)],
        })

    out_path = os.path.join(PROCESSED_DIR, "retrieval_comparison.json")
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    print(f"\n[SAVED] Retrieval comparison -> {out_path}")
    return results


# ─── PUBLIC API ───────────────────────────────────────────────────────────────
def build_retrievers():
    print("\n[Part 2] Loading chunks...")
    chunks, texts = load_chunks()
    print(f"  Loaded {len(chunks)} chunks.")

    print("\n[Part 2] Building TF-IDF retriever...")
    tfidf_ret = TFIDFRetriever(texts)

    print("\n[Part 2] Building Dense retriever...")
    dense_ret = DenseRetriever(texts)

    return chunks, texts, tfidf_ret, dense_ret


def retrieve(query, tfidf_ret, dense_ret, chunks, top_k=TOP_K, method="dense"):
    if method == "tfidf":
        idx, scores = tfidf_ret.retrieve(query, top_k)
    else:
        idx, scores = dense_ret.retrieve(query, top_k)
    return [
        {**chunks[i], "score": float(scores[rank])}
        for rank, i in enumerate(idx)
    ]


# ─── MAIN ─────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    chunks, texts, tfidf_ret, dense_ret = build_retrievers()
    run_comparison(tfidf_ret, dense_ret, chunks)
    print("\n  Part 2 complete.")
