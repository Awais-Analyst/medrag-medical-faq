"""
Part 1 - Corpus Preparation and Chunking
Medical FAQ Assistant - RAG Project
"""

import os
import re
import json
import string

# ─── CONFIG ───────────────────────────────────────────────────────────────────
RAW_DIR       = os.path.join(os.path.dirname(__file__), "..", "data", "raw")
PROCESSED_DIR = os.path.join(os.path.dirname(__file__), "..", "data", "processed")
CHUNK_SIZE    = 200   # words per chunk
CHUNK_OVERLAP = 50    # overlapping words between chunks

os.makedirs(PROCESSED_DIR, exist_ok=True)


# ─── STEP 1: Load Raw Documents ───────────────────────────────────────────────
def load_documents(raw_dir):
    """Load all .txt documents from the raw folder."""
    documents = []
    for filename in sorted(os.listdir(raw_dir)):
        if filename.endswith(".txt"):
            filepath = os.path.join(raw_dir, filename)
            with open(filepath, "r", encoding="utf-8") as f:
                text = f.read()
            documents.append({
                "doc_id"  : filename.replace(".txt", ""),
                "filename": filename,
                "raw_text": text
            })
            print(f"  [LOADED] {filename}  ({len(text.split())} words)")
    return documents


# ─── STEP 2: Preprocess Text ──────────────────────────────────────────────────
def preprocess_text(text):
    """Clean and normalize text."""
    # Remove excessive whitespace / newlines
    text = re.sub(r'\r\n|\r', '\n', text)
    text = re.sub(r'\n{3,}', '\n\n', text)
    text = re.sub(r'[ \t]+', ' ', text)
    # Strip leading/trailing whitespace
    text = text.strip()
    return text


# ─── STEP 3: Chunk Text ───────────────────────────────────────────────────────
def chunk_text(text, doc_id, chunk_size=CHUNK_SIZE, overlap=CHUNK_OVERLAP):
    """
    Split text into overlapping word-level chunks.
    Each chunk is tagged with its source document.
    """
    words  = text.split()
    chunks = []
    start  = 0
    idx    = 0

    while start < len(words):
        end        = min(start + chunk_size, len(words))
        chunk_text = " ".join(words[start:end])
        chunks.append({
            "chunk_id" : f"{doc_id}_chunk_{idx}",
            "doc_id"   : doc_id,
            "text"     : chunk_text,
            "start_word": start,
            "end_word"  : end
        })
        idx   += 1
        start += chunk_size - overlap  # slide window

    return chunks


# ─── STEP 4: Save Processed Corpus ───────────────────────────────────────────
def save_corpus(documents, chunks, processed_dir):
    """Save preprocessed documents and chunks to JSON."""
    # Save clean documents
    docs_path = os.path.join(processed_dir, "preprocessed_docs.json")
    with open(docs_path, "w", encoding="utf-8") as f:
        json.dump(documents, f, indent=2, ensure_ascii=False)
    print(f"\n  [SAVED] Preprocessed docs  -> {docs_path}")

    # Save chunks
    chunks_path = os.path.join(processed_dir, "chunks.json")
    with open(chunks_path, "w", encoding="utf-8") as f:
        json.dump(chunks, f, indent=2, ensure_ascii=False)
    print(f"  [SAVED] Chunks             -> {chunks_path}")

    return docs_path, chunks_path


# ─── MAIN ─────────────────────────────────────────────────────────────────────
def run_corpus_pipeline():
    print("=" * 60)
    print("  PART 1 — CORPUS PREPARATION & CHUNKING")
    print("=" * 60)

    # Load
    print("\n[1/4] Loading raw documents...")
    documents = load_documents(RAW_DIR)
    print(f"\n  Total documents loaded: {len(documents)}")

    # Preprocess
    print("\n[2/4] Preprocessing text...")
    for doc in documents:
        doc["clean_text"] = preprocess_text(doc["raw_text"])
        del doc["raw_text"]  # save memory
    print(f"  Done. Cleaned {len(documents)} documents.")

    # Chunk
    print("\n[3/4] Chunking documents...")
    all_chunks = []
    for doc in documents:
        doc_chunks = chunk_text(doc["clean_text"], doc["doc_id"])
        all_chunks.extend(doc_chunks)
        print(f"  {doc['doc_id']:35s}  ->  {len(doc_chunks):3d} chunks")

    print(f"\n  Total chunks created: {len(all_chunks)}")

    # Save
    print("\n[4/4] Saving processed data...")
    save_corpus(documents, all_chunks, PROCESSED_DIR)

    # Summary
    print("\n" + "=" * 60)
    print("  CORPUS PIPELINE COMPLETE")
    print(f"  Documents : {len(documents)}")
    print(f"  Chunks    : {len(all_chunks)}")
    print(f"  Chunk size: {CHUNK_SIZE} words  |  Overlap: {CHUNK_OVERLAP} words")
    print("=" * 60)

    return documents, all_chunks


if __name__ == "__main__":
    docs, chunks = run_corpus_pipeline()
