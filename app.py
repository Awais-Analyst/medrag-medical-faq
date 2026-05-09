"""
MedRAG - Medical FAQ Assistant (Streamlit Cloud Ready)
RAG Project - BSBA Program
"""

import os, sys, json, re, time
import streamlit as st

# ── Path setup ────────────────────────────────────────────────────────────────
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
SRC_DIR  = os.path.join(BASE_DIR, "src")
sys.path.insert(0, SRC_DIR)
sys.path.insert(0, BASE_DIR)

# ── Streamlit page config (MUST be first st call) ─────────────────────────────
st.set_page_config(
    page_title="MedRAG – Medical FAQ Assistant",
    page_icon="🩺",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── CSS: Full dark theme override (fixes all white/invisible issues) ───────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

/* ─ Root & body ─ */
*, html, body { font-family: 'Inter', sans-serif !important; }

/* ─ Main app background ─ */
.stApp, [data-testid="stAppViewContainer"] {
    background: linear-gradient(135deg, #0f0c29 0%, #302b63 50%, #24243e 100%) !important;
}
[data-testid="stHeader"] { background: transparent !important; }

/* ─ Main content area ─ */
[data-testid="stMainBlockContainer"], .main .block-container {
    background: transparent !important;
    color: #e8e8f0 !important;
    padding-top: 1.5rem !important;
}

/* ─ Sidebar ─ */
[data-testid="stSidebar"], [data-testid="stSidebarContent"] {
    background: rgba(15,12,41,0.95) !important;
    border-right: 1px solid rgba(139,92,246,0.3) !important;
}
[data-testid="stSidebar"] * { color: #e8e8f0 !important; }

/* ─ All text ─ */
p, span, label, div, li, td, th, h1, h2, h3, h4, h5, h6 {
    color: #e8e8f0 !important;
}

/* ─ Markdown ─ */
.stMarkdown, .stMarkdown p { color: #e8e8f0 !important; }

/* ─ Text inputs ─ */
.stTextInput > div > div > input,
.stTextArea > div > div > textarea {
    background: rgba(255,255,255,0.08) !important;
    border: 1px solid rgba(139,92,246,0.5) !important;
    border-radius: 10px !important;
    color: #e8e8f0 !important;
    font-size: 1rem !important;
}
.stTextInput > div > div > input::placeholder,
.stTextArea > div > div > textarea::placeholder {
    color: #9ca3af !important;
}
.stTextInput > div > div > input:focus,
.stTextArea > div > div > textarea:focus {
    border-color: #8b5cf6 !important;
    box-shadow: 0 0 0 2px rgba(139,92,246,0.3) !important;
}

/* ─ Buttons ─ */
.stButton > button {
    background: linear-gradient(135deg, #6366f1, #8b5cf6) !important;
    color: #ffffff !important;
    border: none !important;
    border-radius: 10px !important;
    font-weight: 600 !important;
    padding: 0.5rem 1.5rem !important;
    font-size: 0.95rem !important;
    transition: all 0.2s !important;
}
.stButton > button:hover { opacity: 0.85 !important; transform: translateY(-1px) !important; }

/* ─ Selectbox / dropdown ─ */
.stSelectbox > div > div,
[data-testid="stSelectbox"] > div > div {
    background: rgba(255,255,255,0.08) !important;
    border: 1px solid rgba(139,92,246,0.4) !important;
    border-radius: 10px !important;
    color: #e8e8f0 !important;
}
.stSelectbox svg { fill: #e8e8f0 !important; }

/* ─ Slider ─ */
.stSlider > div > div > div > div { background: #8b5cf6 !important; }

/* ─ Tabs ─ */
.stTabs [data-baseweb="tab-list"] {
    background: rgba(255,255,255,0.05) !important;
    border-radius: 12px !important;
    padding: 4px !important;
    gap: 4px !important;
}
.stTabs [data-baseweb="tab"] {
    background: transparent !important;
    color: #9ca3af !important;
    border-radius: 8px !important;
    font-weight: 500 !important;
    padding: 0.5rem 1rem !important;
}
.stTabs [aria-selected="true"] {
    background: linear-gradient(135deg, #6366f1, #8b5cf6) !important;
    color: #ffffff !important;
}

/* ─ Expander ─ */
.streamlit-expanderHeader {
    background: rgba(99,102,241,0.15) !important;
    border: 1px solid rgba(99,102,241,0.3) !important;
    border-radius: 10px !important;
    color: #e8e8f0 !important;
}
.streamlit-expanderContent {
    background: rgba(255,255,255,0.04) !important;
    border: 1px solid rgba(255,255,255,0.1) !important;
    border-radius: 0 0 10px 10px !important;
    color: #e8e8f0 !important;
}

/* ─ Info / warning / success / error boxes ─ */
[data-testid="stAlert"] {
    border-radius: 10px !important;
}

/* ─ Spinner ─ */
.stSpinner > div { border-top-color: #8b5cf6 !important; }

/* ─ Divider ─ */
hr { border-color: rgba(139,92,246,0.3) !important; }

/* ══ Custom Components ══════════════════════════════════════════════════════ */

/* Hero banner */
.hero {
    background: linear-gradient(135deg,rgba(99,102,241,0.25),rgba(168,85,247,0.25));
    border: 1px solid rgba(168,85,247,0.45);
    border-radius: 18px;
    padding: 2.2rem 2.5rem;
    margin-bottom: 1.8rem;
    text-align: center;
}
.hero h1 { font-size:2.2rem; font-weight:700; color:#e0d7ff !important; margin:0; }
.hero p  { color:#c4b5fd !important; font-size:1.05rem; margin-top:0.5rem; }

/* Answer card */
.answer-card {
    background: rgba(99,102,241,0.12);
    border: 1px solid rgba(99,102,241,0.45);
    border-radius: 14px;
    padding: 1.5rem 1.8rem;
    margin: 1rem 0;
}
.answer-card h3 { color:#a78bfa !important; margin-top:0; font-size:1.1rem; }
.answer-card p  { color:#e8e8f0 !important; font-size:1.05rem; line-height:1.75; }
.answer-card small { color:#6b7280 !important; }

/* Source card */
.source-card {
    background: rgba(255,255,255,0.04);
    border: 1px solid rgba(255,255,255,0.12);
    border-radius: 12px;
    padding: 1rem 1.2rem;
    margin-bottom: 0.8rem;
    transition: border-color 0.2s;
}
.source-card:hover { border-color: rgba(168,85,247,0.5); }
.src-header { font-size:0.78rem; font-weight:600; color:#a78bfa !important;
              text-transform:uppercase; letter-spacing:0.08em; margin-bottom:0.5rem; }
.score-badge { display:inline-block; background:rgba(168,85,247,0.25);
               color:#d8b4fe !important; border-radius:999px;
               padding:0.1rem 0.55rem; font-size:0.72rem; font-weight:600;
               margin-left:0.5rem; }
.src-text { font-size:0.9rem; line-height:1.65; color:#d1d5db !important; }

/* Highlight */
mark.hl { background:rgba(250,204,21,0.35); color:#fef3c7 !important;
           border-radius:3px; padding:0 2px; }

/* Metric box */
.metric-box { background:rgba(255,255,255,0.06); border-radius:12px;
              padding:1.2rem; text-align:center;
              border:1px solid rgba(139,92,246,0.3); }
.metric-val { font-size:2.2rem; font-weight:700; color:#a78bfa !important; }
.metric-lbl { font-size:0.82rem; color:#9ca3af !important; margin-top:0.3rem; }

/* Sidebar section header */
.sb-header { font-size:0.72rem; font-weight:700; color:#7c3aed !important;
             text-transform:uppercase; letter-spacing:0.1em;
             margin:1rem 0 0.4rem; }
</style>
""", unsafe_allow_html=True)


# ══ HELPERS ══════════════════════════════════════════════════════════════════

DOC_LABELS = {
    "doc1_diabetes"           : "🩸 Diabetes",
    "doc2_hypertension"       : "💓 Hypertension",
    "doc3_covid19"            : "🦠 COVID-19",
    "doc4_heart_disease"      : "❤️ Heart Disease",
    "doc5_mental_health"      : "🧠 Mental Health",
    "doc6_nutrition"          : "🥗 Nutrition",
    "doc7_infectious_diseases": "💉 Infectious Diseases",
    "doc8_cancer"             : "🎗️ Cancer",
}

def doc_label(doc_id):
    base = re.sub(r"_chunk_\d+$", "", doc_id)
    return DOC_LABELS.get(base, doc_id)

def highlight(text, query):
    stop = {"what","is","are","the","a","an","how","can","does","do","be","to","of",
            "in","on","for","and","or","with","it","i","my","me","you","your","at",
            "by","from","that","this","was","were","will","would","should","could"}
    kws = [w.strip("?.,!") for w in query.lower().split()
           if w.strip("?.,!") not in stop and len(w) > 2]
    result = text
    for kw in kws:
        result = re.compile(re.escape(kw), re.IGNORECASE).sub(
            lambda m: f'<mark class="hl">{m.group()}</mark>', result)
    return result

def get_api_key():
    """Get Groq key from Streamlit secrets or sidebar input."""
    try:
        return st.secrets["GROQ_API_KEY"]
    except Exception:
        return st.session_state.get("groq_key", "")


# ══ CACHED LOADERS ═══════════════════════════════════════════════════════════

@st.cache_resource(show_spinner="⚙️ Building retrieval index…")
def load_retrievers():
    # Auto-run corpus pipeline if chunks don't exist
    chunks_path = os.path.join(BASE_DIR, "data", "processed", "chunks.json")
    if not os.path.exists(chunks_path):
        import importlib.util
        spec = importlib.util.spec_from_file_location(
            "part1", os.path.join(SRC_DIR, "part1_corpus.py"))
        m = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(m)
        m.run_corpus_pipeline()

    from part2_retrieval import build_retrievers as _build
    return _build()

@st.cache_resource(show_spinner="🔑 Connecting to Groq…")
def load_client(api_key):
    from part3_generation import get_groq_client
    return get_groq_client(api_key)


# ══ SIDEBAR ══════════════════════════════════════════════════════════════════

with st.sidebar:
    st.markdown('<div style="text-align:center;padding:0.5rem 0 1rem">'
                '<span style="font-size:2.5rem">🩺</span><br>'
                '<span style="font-weight:700;font-size:1.1rem;color:#a78bfa">MedRAG</span></div>',
                unsafe_allow_html=True)
    st.markdown("---")

    # API Key — only show input if not in secrets
    try:
        st.secrets["GROQ_API_KEY"]
        st.success("✅ API key loaded from secrets")
    except Exception:
        manual_key = st.text_input("🔑 Groq API Key", type="password",
                                    placeholder="gsk_...",
                                    help="Get free key at console.groq.com")
        if manual_key:
            st.session_state["groq_key"] = manual_key

    st.markdown('<div class="sb-header">⚙️ Retrieval Settings</div>', unsafe_allow_html=True)
    retrieval_method = st.selectbox(
        "Method", ["Dense (Sentence Transformers)", "TF-IDF (Keyword)"],
        label_visibility="collapsed"
    )
    method_key = "dense" if "Dense" in retrieval_method else "tfidf"
    top_k = st.slider("Top-K Chunks", 1, 5, 3)

    st.markdown('<div class="sb-header">📚 Knowledge Base</div>', unsafe_allow_html=True)
    for lbl in DOC_LABELS.values():
        st.markdown(f'<div style="color:#d1d5db;font-size:0.88rem;padding:2px 0">{lbl}</div>',
                    unsafe_allow_html=True)

    st.markdown("---")
    st.markdown('<div style="color:#6b7280;font-size:0.78rem;text-align:center">'
                'BSBA RAG Project<br>Llama 3.3-70B · Groq API</div>',
                unsafe_allow_html=True)


# ══ MAIN TABS ════════════════════════════════════════════════════════════════

tab_qa, tab_cmp, tab_eval, tab_about = st.tabs(
    ["💬 Ask a Question", "⚖️ Compare Methods", "📊 Evaluation", "ℹ️ About"]
)

# ─────────────────────────────────────────────────────────────────────────────
#  TAB 1 ── Q&A
# ─────────────────────────────────────────────────────────────────────────────
with tab_qa:
    st.markdown("""
    <div class="hero">
      <h1>🩺 MedRAG — Medical FAQ Assistant</h1>
      <p>Ask any medical question — answers are grounded in our curated knowledge base.</p>
    </div>""", unsafe_allow_html=True)

    query = st.text_input("", placeholder="e.g. What are the symptoms of diabetes?",
                          label_visibility="collapsed")
    c1, c2 = st.columns([1, 5])
    with c1:
        ask = st.button("🔍 Ask", use_container_width=True, key="ask_btn")
    with c2:
        st.markdown('<small style="color:#9ca3af">Try: '
                    '<i>How is hypertension treated? · What is long COVID? · '
                    'Can diabetes be prevented?</i></small>',
                    unsafe_allow_html=True)

    if ask and query.strip():
        api_key = get_api_key()
        if not api_key:
            st.error("⚠️ Enter your Groq API key in the sidebar.")
        else:
            try:
                chunks, texts, tfidf_ret, dense_ret = load_retrievers()
                client = load_client(api_key)

                from part2_retrieval import retrieve
                from part3_generation import generate_answer

                with st.spinner("🔍 Retrieving relevant chunks…"):
                    t0 = time.time()
                    ctx = retrieve(query, tfidf_ret, dense_ret, chunks,
                                   top_k=top_k, method=method_key)
                    rt = time.time() - t0

                with st.spinner("🤖 Generating answer with Llama 3…"):
                    t0  = time.time()
                    res = generate_answer(query, ctx, client)
                    gt  = time.time() - t0

                # ── Answer ────────────────────────────────────────────────
                st.markdown(f"""
                <div class="answer-card">
                  <h3>💡 Answer</h3>
                  <p>{res['answer']}</p>
                  <small>🔍 Retrieved in {rt*1000:.0f}ms &nbsp;·&nbsp;
                  🤖 Generated in {gt:.1f}s &nbsp;·&nbsp;
                  📡 {retrieval_method}</small>
                </div>""", unsafe_allow_html=True)

                # ── Sources with citation highlighting (BONUS) ────────────
                st.markdown("### 📎 Retrieved Evidence")
                st.markdown('<small style="color:#9ca3af">Query keywords are '
                            '<mark class="hl">highlighted</mark> in each source.</small>',
                            unsafe_allow_html=True)

                for rank, chunk in enumerate(ctx, 1):
                    hl = highlight(chunk["text"], query)
                    st.markdown(f"""
                    <div class="source-card">
                      <div class="src-header">
                        Rank {rank} &nbsp;·&nbsp; {doc_label(chunk['doc_id'])}
                        <span class="score-badge">score: {chunk['score']:.3f}</span>
                      </div>
                      <div class="src-text">{hl}</div>
                    </div>""", unsafe_allow_html=True)

            except Exception as e:
                st.error(f"❌ Error: {e}")

    elif ask:
        st.warning("Please enter a question first.")


# ─────────────────────────────────────────────────────────────────────────────
#  TAB 2 ── RETRIEVAL COMPARISON
# ─────────────────────────────────────────────────────────────────────────────
with tab_cmp:
    st.markdown("## ⚖️ TF-IDF vs Dense Embedding — Side by Side")
    st.markdown('<p style="color:#9ca3af">See how both methods retrieve different chunks for the same query.</p>',
                unsafe_allow_html=True)

    cq = st.text_input("", placeholder="e.g. What causes cancer?",
                        key="cmp_q", label_visibility="collapsed")
    if st.button("⚖️ Compare", key="cmp_btn"):
        if cq.strip():
            try:
                chunks, texts, tfidf_ret, dense_ret = load_retrievers()
                from part2_retrieval import retrieve

                col_tf, col_dn = st.columns(2)

                for col, method, label in [
                    (col_tf, "tfidf", "📊 TF-IDF (Keyword)"),
                    (col_dn, "dense", "🧠 Dense (Embeddings)"),
                ]:
                    with col:
                        st.markdown(f"### {label}")
                        res_chunks = retrieve(cq, tfidf_ret, dense_ret,
                                              chunks, top_k=3, method=method)
                        for rank, c in enumerate(res_chunks, 1):
                            hl = highlight(c["text"], cq)
                            st.markdown(f"""
                            <div class="source-card">
                              <div class="src-header">Rank {rank} · {doc_label(c['doc_id'])}
                                <span class="score-badge">{c['score']:.4f}</span>
                              </div>
                              <div class="src-text">{hl}</div>
                            </div>""", unsafe_allow_html=True)
            except Exception as e:
                st.error(f"❌ {e}")
        else:
            st.warning("Enter a query to compare.")


# ─────────────────────────────────────────────────────────────────────────────
#  TAB 3 ── EVALUATION
# ─────────────────────────────────────────────────────────────────────────────
with tab_eval:
    st.markdown("## 📊 Experimental Evaluation")
    PROC = os.path.join(BASE_DIR, "data", "processed")
    eval_path = os.path.join(PROC, "evaluation_report.json")

    if st.button("▶️ Run Full Evaluation", key="run_eval"):
        api_key = get_api_key()
        if not api_key:
            st.error("⚠️ Groq API key required.")
        else:
            try:
                chunks, texts, tfidf_ret, dense_ret = load_retrievers()
                client = load_client(api_key)
                from part2_retrieval import retrieve
                from part3_generation import generate_answer
                from part5_evaluation import evaluate_system

                def rfn(q): return retrieve(q, tfidf_ret, dense_ret, chunks, top_k=3)
                def gfn(q, c): return generate_answer(q, c, client)

                with st.spinner("🔬 Running evaluation on 10 queries…"):
                    report = evaluate_system(rfn, gfn)
                st.success("✅ Evaluation complete! Results saved.")
                st.rerun()
            except Exception as e:
                st.error(f"❌ {e}")

    if os.path.exists(eval_path):
        with open(eval_path, "r", encoding="utf-8") as f:
            rpt = json.load(f)
        s = rpt["summary"]

        cols = st.columns(4)
        for col, val, lbl in [
            (cols[0], s["total"],   "Total Queries"),
            (cols[1], s["correct"], "Correct ✅"),
            (cols[2], s["total"] - s["correct"], "Needs Review"),
            (cols[3], f"{s['accuracy']:.0%}", "Accuracy"),
        ]:
            col.markdown(f"""
            <div class="metric-box">
              <div class="metric-val">{val}</div>
              <div class="metric-lbl">{lbl}</div>
            </div>""", unsafe_allow_html=True)

        st.markdown("### 📋 Query Results")
        for r in rpt["results"]:
            icon = ("✅" if "CORRECT" in str(r.get("status","")) else
                    "⚠️" if "PARTIAL" in str(r.get("status","")) else
                    "ℹ️" if "DECLINED" in str(r.get("status","")) else "❌")
            with st.expander(f"{icon} {r['query']}"):
                st.markdown(f"**Category:** {r['category']}")
                st.markdown(f"**Status:** `{r['status']}`")
                st.markdown(f"**Sources:** {', '.join(r.get('sources', []))}")
                st.markdown(f"**Answer:** {r['answer']}")

        if rpt.get("failures"):
            st.markdown("### ❌ Failure Cases")
            for f in rpt["failures"]:
                st.warning(f"**Q:** {f['query']}\n\n**Issue:** {f.get('issue','Low keyword overlap')}")

        st.markdown("### ⚠️ Observed Limitations")
        for lim in [
            "Static corpus — no real-time or updated medical info",
            "Fixed chunk size limits context for complex multi-part questions",
            "Out-of-domain queries not always clearly declined",
            "Overlapping topics may cause retrieval confusion",
            "No numerical fact-checking beyond keyword overlap scoring",
        ]:
            st.markdown(f"- {lim}")
    else:
        st.info("No evaluation report found. Click **Run Full Evaluation** above.")


# ─────────────────────────────────────────────────────────────────────────────
#  TAB 4 ── ABOUT
# ─────────────────────────────────────────────────────────────────────────────
with tab_about:
    st.markdown("## ℹ️ About MedRAG")
    st.markdown("""
**MedRAG** is a Retrieval-Augmented Generation (RAG) system built as a semester project
for the *AI in Business Analytics* course.

### 🏗️ Architecture
```
User Query
    │
    ▼
┌─────────────────────────────────────────────┐
│  Retrieval Module                           │
│  TF-IDF (scikit-learn)  OR                 │
│  Dense Embeddings (sentence-transformers)  │
│  → Top-K relevant chunks from 8 docs       │
└──────────────────┬──────────────────────────┘
                   │ context chunks
                   ▼
┌─────────────────────────────────────────────┐
│  Generation Module                         │
│  Groq API → Llama 3.3-70B                  │
│  → Grounded, factual answer                │
└──────────────────┬──────────────────────────┘
                   │ answer + sources
                   ▼
┌─────────────────────────────────────────────┐
│  Streamlit UI                              │
│  Citation highlighting (Bonus ✨)          │
│  Retrieval comparison · Evaluation         │
└─────────────────────────────────────────────┘
```

### 📁 Knowledge Base (8 Documents — 10 Q&A pairs each)
| # | Topic | Chunks |
|---|-------|--------|
| 1 | 🩸 Diabetes | 5 |
| 2 | 💓 Hypertension | 5 |
| 3 | 🦠 COVID-19 | 5 |
| 4 | ❤️ Heart Disease | 5 |
| 5 | 🧠 Mental Health | 5 |
| 6 | 🥗 Nutrition & Diet | 6 |
| 7 | 💉 Infectious Diseases & Vaccines | 6 |
| 8 | 🎗️ Cancer Awareness | 6 |
| | **Total** | **43 chunks** |

### 🛠️ Tech Stack
| Component | Technology |
|-----------|-----------|
| TF-IDF Retrieval | scikit-learn |
| Dense Embeddings | sentence-transformers (all-MiniLM-L6-v2) |
| Vector Search | FAISS |
| LLM Generation | Groq API (Llama 3.3-70B) |
| UI | Streamlit |

### 🎁 Bonus Feature
**Source Citation Highlighting** — query keywords are highlighted in yellow
inside each retrieved chunk so you can see exactly what drove the answer.
    """)
