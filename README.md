# 🩺 MedRAG — Medical FAQ Assistant

A **Retrieval-Augmented Generation (RAG)** system that answers medical questions using a curated knowledge base of 8 medical topics.

**Live Demo:** [![Open in Streamlit](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://your-app.streamlit.app)

---

## 📌 Project Info
- **Course:** AI in Business Analytics (BSBA)
- **Domain:** Medical FAQ Assistant
- **LLM:** Llama 3.3-70B via Groq API (free)

## 🏗️ Architecture
```
User Query → Retrieval (TF-IDF or Dense Embeddings) → Top-K Chunks → Llama 3.3 (Groq) → Answer + Citations
```

## 📁 Project Structure
```
Project/
├── app.py                    # Streamlit UI (Parts 4 + Bonus)
├── requirements.txt
├── .streamlit/
│   └── config.toml           # Dark theme config
├── data/
│   ├── raw/                  # 8 medical FAQ documents
│   └── processed/            # Chunks, TF-IDF index, FAISS index
└── src/
    ├── part1_corpus.py       # Corpus preparation & chunking
    ├── part2_retrieval.py    # TF-IDF + Dense retrieval
    ├── part3_generation.py   # Groq LLM generation
    └── part5_evaluation.py   # Evaluation on 10 queries
```

## 🚀 Run Locally
```bash
pip install -r requirements.txt
streamlit run app.py
```

## ☁️ Deploy on Streamlit Cloud
1. Push this repo to GitHub
2. Go to [share.streamlit.io](https://share.streamlit.io)
3. Connect your GitHub repo → select `app.py`
4. In **Settings → Secrets**, add:
```toml
GROQ_API_KEY = "gsk_your_key_here"
```

## 🛠️ Tech Stack
| Component | Library |
|-----------|---------|
| TF-IDF Retrieval | scikit-learn |
| Dense Embeddings | sentence-transformers |
| Vector Search | FAISS |
| LLM | Groq API (Llama 3.3-70B) |
| UI | Streamlit |

## 🎁 Bonus Feature
**Source Citation Highlighting** — query keywords highlighted in retrieved evidence chunks.

## ⚠️ Submission Requirements
- [x] Source Code
- [x] Final Report (PDF)
- [ ] Blog Post
- [x] GitHub Link
- [x] Screenshots/Results
