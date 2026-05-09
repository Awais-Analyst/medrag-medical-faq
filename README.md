<div align="center">

# 🩺 MedRAG — Medical FAQ Assistant

**A production-grade Retrieval-Augmented Generation (RAG) system for medical question answering**

[![Streamlit App](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://medrag-medical-faq-jggqku7kc3prac6mg7tpz8.streamlit.app/)
![Python](https://img.shields.io/badge/Python-3.10+-blue?logo=python)
![LLM](https://img.shields.io/badge/LLM-Llama--3.3--70B-purple?logo=meta)
![FAISS](https://img.shields.io/badge/Vector_DB-FAISS-orange)
![License](https://img.shields.io/badge/License-MIT-green)

[🚀 Live Demo](https://medrag-medical-faq-jggqku7kc3prac6mg7tpz8.streamlit.app/) · [📂 Source Code](https://github.com/Awais-Analyst/medrag-medical-faq) · [📋 Report](#)

</div>

---

## 📌 Overview

**MedRAG** is an intelligent medical FAQ assistant built on a full Retrieval-Augmented Generation (RAG) pipeline. Unlike generic chatbots, MedRAG grounds every answer in a curated, verified medical knowledge base — ensuring responses are factual, cited, and explainable.

Users can ask natural-language medical questions and receive clear, concise answers supported by ranked source evidence, keyword-highlighted excerpts, and confidence scores.

> **Domain:** Medical FAQ — Diabetes, Hypertension, COVID-19, Heart Disease, Mental Health, Nutrition, Infectious Diseases, Cancer

---

## ✨ Key Features

| Feature | Description |
|---------|-------------|
| 🔍 **Dual Retrieval** | TF-IDF (keyword) + Dense FAISS (semantic) — switchable at runtime |
| 🤖 **LLM Generation** | Llama 3.3-70B via Groq API — fast, free, accurate |
| 📖 **Source Citations** | Every answer links to ranked source chunks with relevance scores |
| 🎨 **ChatGPT-style UI** | Dark-themed, responsive interface with chat history |
| 📊 **Auto Evaluation** | Built-in benchmark on 10 medical queries — 89% accuracy |
| ⚡ **Instant Startup** | FAISS index & TF-IDF model cached to disk for sub-second reload |
| ☁️ **Cloud Deployed** | Live on Streamlit Cloud — accessible from any device |

---

## 🏗️ System Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    User Interface (Streamlit)            │
│         Chat · Compare · Evaluation · About             │
└──────────────────────┬──────────────────────────────────┘
                       │ User Query
                       ▼
┌─────────────────────────────────────────────────────────┐
│                   Retrieval Layer                        │
│                                                          │
│  ┌─────────────────┐      ┌──────────────────────────┐  │
│  │  TF-IDF (sklearn)│      │  Dense Embeddings (FAISS)│  │
│  │  Keyword-based   │      │  Semantic similarity     │  │
│  │  cosine similarity│     │  all-MiniLM-L6-v2        │  │
│  └────────┬─────────┘      └─────────────┬────────────┘  │
│           └──────────┬────────────────────┘              │
│                      ▼                                   │
│              Top-K Relevant Chunks                       │
└──────────────────────┬──────────────────────────────────┘
                       │ Context
                       ▼
┌─────────────────────────────────────────────────────────┐
│                  Generation Layer                        │
│          Groq API — Llama 3.3-70B-Versatile             │
│          System prompt + retrieved context               │
└──────────────────────┬──────────────────────────────────┘
                       │
                       ▼
              Answer + Source Citations
```

---

## 📚 Knowledge Base

| # | Document | Chunks |
|---|----------|--------|
| 1 | 🩸 Diabetes FAQ | ~5 |
| 2 | 💓 Hypertension FAQ | ~5 |
| 3 | 🦠 COVID-19 FAQ | ~5 |
| 4 | ❤️ Heart Disease FAQ | ~5 |
| 5 | 🧠 Mental Health FAQ | ~5 |
| 6 | 🥗 Nutrition FAQ | ~5 |
| 7 | 💉 Infectious Diseases FAQ | ~5 |
| 8 | 🎗️ Cancer FAQ | ~5 |

**Total:** 8 documents · 43+ chunks · ~200 words per chunk with 50-word overlap

---

## 🛠️ Tech Stack

| Layer | Technology |
|-------|-----------|
| Language | Python 3.10+ |
| UI Framework | Streamlit |
| TF-IDF Retrieval | scikit-learn |
| Dense Embeddings | sentence-transformers (`all-MiniLM-L6-v2`) |
| Vector Search | FAISS (faiss-cpu) |
| LLM API | Groq — Llama 3.3-70B-Versatile |
| Evaluation | Custom keyword hit-rate scoring |
| Deployment | Streamlit Cloud |

---

## 🚀 Getting Started

### Prerequisites
- Python 3.10+
- A free [Groq API key](https://console.groq.com/)

### Installation

```bash
git clone https://github.com/Awais-Analyst/medrag-medical-faq.git
cd medrag-medical-faq
pip install -r requirements.txt
```

### Configuration

Create `.streamlit/secrets.toml`:
```toml
GROQ_API_KEY = "your_groq_api_key_here"
```

### Run Locally

```bash
streamlit run app.py
```

Open [http://localhost:8501](http://localhost:8501)

---

## 📊 Evaluation Results

Tested on 10 standard medical queries using keyword hit-rate scoring:

| Metric | Result |
|--------|--------|
| Total Queries | 10 |
| Correct (≥60% keywords) | 8 |
| Partial (30–59%) | 1 |
| Out-of-domain (Declined) | 1 |
| **Overall Accuracy** | **89%** |

---

## 📁 Project Structure

```
medrag-medical-faq/
├── app.py                    # Main Streamlit application
├── requirements.txt          # Python dependencies
├── README.md
├── .gitignore
├── .streamlit/
│   └── config.toml           # Streamlit theme config
├── data/
│   ├── raw/                  # Raw medical FAQ text files
│   └── processed/            # Chunks JSON + cached indices
├── src/
│   ├── part1_corpus.py       # Corpus preparation & chunking
│   ├── part2_retrieval.py    # TF-IDF + Dense retrieval
│   ├── part3_generation.py   # Groq LLM generation
│   └── part5_evaluation.py   # Automated evaluation suite
└── report/                   # Project report (PDF)
```

---

## 👥 Author

| Name |
|------|
| **M Awais Mustafa** |

---

## 📄 License

This project is licensed under the MIT License.

---

<div align="center">
Made with ❤️ by <strong>Awais-Analyst</strong>
</div>
