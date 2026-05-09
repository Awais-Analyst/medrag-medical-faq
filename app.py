"""
MedRAG - ChatGPT-Style Medical FAQ Assistant
Complete UI Redesign with Chat History, Smart Sources, Premium Design
"""
import os, sys, json, re, time
import streamlit as st

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
SRC_DIR  = os.path.join(BASE_DIR, "src")
sys.path.insert(0, SRC_DIR)
sys.path.insert(0, BASE_DIR)

st.set_page_config(page_title="MedRAG", page_icon="🩺", layout="wide",
                   initial_sidebar_state="expanded")

# ══ CSS ══════════════════════════════════════════════════════════════════════
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
*, html, body { font-family: 'Inter', sans-serif !important; }

.stApp, [data-testid="stAppViewContainer"] {
    background: #0d0d0d !important;
}
[data-testid="stHeader"] { background: transparent !important; }
.main .block-container {
    background: transparent !important; color: #ececec !important;
    padding: 0 !important; max-width: 100% !important;
}

/* Sidebar */
[data-testid="stSidebar"] {
    background: #171717 !important;
    border-right: 1px solid #2a2a2a !important;
}
[data-testid="stSidebar"] * { color: #ececec !important; }
[data-testid="stSidebarContent"] { padding: 0.5rem 0.8rem !important; }

/* All text */
p, span, label, div, li, h1, h2, h3, h4, small { color: #ececec !important; }
.stMarkdown p { color: #ececec !important; }

/* Inputs */
.stTextInput > div > div > input,
.stTextArea > div > div > textarea,
[data-testid="stChatInput"] textarea {
    background: #1e1e1e !important;
    border: 1px solid #333 !important;
    border-radius: 12px !important;
    color: #ececec !important;
    font-size: 1rem !important;
}
.stTextInput > div > div > input::placeholder,
[data-testid="stChatInput"] textarea::placeholder { color: #666 !important; }
.stTextInput > div > div > input:focus { border-color: #10a37f !important; box-shadow: 0 0 0 2px rgba(16,163,127,0.2) !important; }

/* Chat input bar */
[data-testid="stChatInput"] {
    background: #1e1e1e !important;
    border: 1px solid #333 !important;
    border-radius: 16px !important;
}
[data-testid="stChatInput"] button { color: #10a37f !important; }

/* Buttons */
.stButton > button {
    background: transparent !important;
    border: 1px solid #333 !important;
    color: #ececec !important;
    border-radius: 8px !important;
    font-size: 0.88rem !important;
    padding: 0.4rem 0.9rem !important;
    transition: all 0.15s !important;
    text-align: left !important;
    width: 100% !important;
}
.stButton > button:hover { background: #2a2a2a !important; border-color: #444 !important; }

/* New chat button special */
.new-chat-btn > button {
    background: #10a37f !important;
    border: none !important;
    color: white !important;
    font-weight: 600 !important;
    border-radius: 10px !important;
    margin-bottom: 0.5rem !important;
}
.new-chat-btn > button:hover { background: #0d8f6e !important; opacity:1 !important; }

/* Chat messages */
[data-testid="stChatMessage"] {
    background: transparent !important;
    border: none !important;
    padding: 1rem 0 !important;
}
/* User message */
[data-testid="stChatMessage"][data-testid*="user"],
.stChatMessage:has([aria-label="user avatar"]) {
    background: #1a1a1a !important;
    border-radius: 14px !important;
    padding: 1rem 1.2rem !important;
}

/* Selectbox */
.stSelectbox > div > div {
    background: #1e1e1e !important;
    border: 1px solid #333 !important;
    border-radius: 8px !important;
    color: #ececec !important;
}
.stSelectbox svg { fill: #ececec !important; }

/* Slider */
.stSlider > div > div > div > div { background: #10a37f !important; }

/* Expander */
details { border: 1px solid #2a2a2a !important; border-radius: 10px !important; }
summary { color: #888 !important; font-size: 0.82rem !important; }
.streamlit-expanderContent { background: #141414 !important; }

/* Tabs */
.stTabs [data-baseweb="tab-list"] {
    background: #1a1a1a !important; border-radius: 10px !important;
    padding: 3px !important; gap: 3px !important;
}
.stTabs [data-baseweb="tab"] {
    background: transparent !important; color: #888 !important;
    border-radius: 7px !important; font-size: 0.88rem !important;
}
.stTabs [aria-selected="true"] {
    background: #10a37f !important; color: white !important;
}

/* Source chip */
.src-chip {
    display: inline-block; background: #1e2e28;
    border: 1px solid #10a37f44; border-radius: 6px;
    padding: 0.15rem 0.5rem; font-size: 0.75rem;
    color: #10a37f !important; margin: 0 3px 3px 0;
}
.score-badge {
    display: inline-block; background: #1e1e2e;
    border: 1px solid #8b5cf644; border-radius: 999px;
    padding: 0.1rem 0.45rem; font-size: 0.7rem;
    color: #a78bfa !important; margin-left: 4px;
}
.source-block {
    background: #141414; border: 1px solid #2a2a2a;
    border-radius: 10px; padding: 0.8rem 1rem;
    margin-bottom: 0.5rem; font-size: 0.86rem;
    line-height: 1.6; color: #bbb !important;
}
.source-label {
    font-size: 0.73rem; font-weight: 600;
    color: #10a37f !important; text-transform: uppercase;
    letter-spacing: 0.07em; margin-bottom: 0.4rem;
}
mark.hl { background: rgba(16,163,127,0.25); color: #5eead4 !important;
           border-radius: 3px; padding: 0 2px; }

/* History item */
.hist-item {
    padding: 0.45rem 0.6rem; border-radius: 8px;
    font-size: 0.84rem; color: #bbb !important;
    cursor: pointer; truncate: ellipsis;
    white-space: nowrap; overflow: hidden;
}
.hist-item:hover { background: #222 !important; }

/* Welcome */
.welcome-hero { text-align: center; padding: 4rem 2rem 2rem; }
.welcome-hero h1 { font-size: 2.4rem; font-weight: 700; color: #ececec !important; }
.welcome-hero p { color: #888 !important; font-size: 1.05rem; }
.suggest-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 0.6rem; max-width: 600px; margin: 1.5rem auto 0; }
.suggest-card {
    background: #1a1a1a; border: 1px solid #2a2a2a;
    border-radius: 12px; padding: 0.9rem 1rem;
    cursor: pointer; transition: border-color 0.15s;
    font-size: 0.9rem; color: #ececec !important;
}
.suggest-card:hover { border-color: #10a37f; }
.suggest-icon { font-size: 1.3rem; margin-bottom: 0.3rem; }

/* Sidebar section label */
.sb-label { font-size: 0.7rem; font-weight: 700; color: #555 !important;
            text-transform: uppercase; letter-spacing: 0.1em;
            padding: 0.6rem 0 0.2rem; }

/* Nav button active */
.nav-active > button { background: #1e2e28 !important; border-color: #10a37f44 !important; color: #10a37f !important; }
</style>
""", unsafe_allow_html=True)

# ══ SESSION STATE ═════════════════════════════════════════════════════════════
def init_state():
    defaults = {
        "messages"     : [],
        "conversations": [],
        "page"         : "chat",
        "method"       : "dense",
        "top_k"        : 3,
        "pending_q"    : None,
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v

init_state()

# ══ HELPERS ══════════════════════════════════════════════════════════════════
DOC_LABELS = {
    "doc1_diabetes": "🩸 Diabetes", "doc2_hypertension": "💓 Hypertension",
    "doc3_covid19": "🦠 COVID-19", "doc4_heart_disease": "❤️ Heart Disease",
    "doc5_mental_health": "🧠 Mental Health", "doc6_nutrition": "🥗 Nutrition",
    "doc7_infectious_diseases": "💉 Infectious Diseases", "doc8_cancer": "🎗️ Cancer",
}

def doc_label(doc_id):
    base = re.sub(r"_chunk_\d+$", "", doc_id)
    return DOC_LABELS.get(base, doc_id)

def highlight(text, query):
    stop = {"what","is","are","the","a","an","how","can","does","do","be","to","of",
            "in","on","for","and","or","with","it","i","my","me","you","at","by",
            "from","that","this","was","will","would","should","could","its"}
    kws = [w.strip("?.,!") for w in query.lower().split()
           if w.strip("?.,!") not in stop and len(w) > 2]
    result = text
    for kw in kws:
        result = re.compile(re.escape(kw), re.IGNORECASE).sub(
            lambda m: f'<mark class="hl">{m.group()}</mark>', result)
    return result

def smart_excerpt(text, query, max_chars=220):
    """Extract the single most relevant sentence from a chunk."""
    sentences = re.split(r'(?<=[.?!])\s+', text)
    qwords = set(w.lower().strip("?.,!") for w in query.split() if len(w) > 2)
    best, best_score = sentences[0] if sentences else text, 0
    for s in sentences:
        score = sum(1 for w in qwords if w in s.lower())
        if score > best_score:
            best, best_score = s, score
    return (best[:max_chars] + "…") if len(best) > max_chars else best

def get_api_key():
    try:
        return st.secrets["GROQ_API_KEY"]
    except Exception:
        return st.session_state.get("manual_key", "")

def save_to_history():
    msgs = st.session_state.messages
    if msgs:
        title = next((m["content"][:45] + "…" for m in msgs if m["role"] == "user"), "Conversation")
        st.session_state.conversations.insert(0, {"title": title, "messages": list(msgs)})
        if len(st.session_state.conversations) > 20:
            st.session_state.conversations.pop()

# ══ CACHED RESOURCES ══════════════════════════════════════════════════════════
@st.cache_resource(show_spinner="⚙️ Loading retrieval index…")
def load_retrievers():
    chunks_path = os.path.join(BASE_DIR, "data", "processed", "chunks.json")
    if not os.path.exists(chunks_path):
        import importlib.util
        spec = importlib.util.spec_from_file_location("p1", os.path.join(SRC_DIR, "part1_corpus.py"))
        m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
        m.run_corpus_pipeline()
    from part2_retrieval import build_retrievers as _b
    return _b()

@st.cache_resource(show_spinner="🔑 Connecting to Groq…")
def load_client(api_key):
    from part3_generation import get_groq_client
    return get_groq_client(api_key)

# ══ SIDEBAR ══════════════════════════════════════════════════════════════════
with st.sidebar:
    st.markdown('<div style="padding:0.8rem 0 0.6rem;font-size:1.3rem;font-weight:700;color:#ececec">🩺 MedRAG</div>', unsafe_allow_html=True)

    # New Chat
    st.markdown('<div class="new-chat-btn">', unsafe_allow_html=True)
    if st.button("✏️  New Chat", key="new_chat"):
        save_to_history()
        st.session_state.messages = []
        st.session_state.page = "chat"
        st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

    # Page nav
    st.markdown('<div class="sb-label">Navigation</div>', unsafe_allow_html=True)
    pages = [("💬", "Chat", "chat"), ("⚖️", "Compare", "compare"),
             ("📊", "Evaluation", "eval"), ("ℹ️", "About", "about")]
    for icon, label, pg in pages:
        active = "nav-active" if st.session_state.page == pg else ""
        st.markdown(f'<div class="{active}">', unsafe_allow_html=True)
        if st.button(f"{icon}  {label}", key=f"nav_{pg}"):
            st.session_state.page = pg; st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

    # Chat history
    if st.session_state.conversations:
        st.markdown('<div class="sb-label">Recent Chats</div>', unsafe_allow_html=True)
        for i, conv in enumerate(st.session_state.conversations[:8]):
            if st.button(f"🕐 {conv['title']}", key=f"hist_{i}"):
                save_to_history()
                st.session_state.messages = list(conv["messages"])
                st.session_state.page = "chat"; st.rerun()

    # Settings
    st.markdown('<div class="sb-label">Settings</div>', unsafe_allow_html=True)
    method_label = st.selectbox("Retrieval", ["Dense (Semantic)", "TF-IDF (Keyword)"],
                                 index=0 if st.session_state.method == "dense" else 1,
                                 label_visibility="collapsed")
    st.session_state.method = "dense" if "Dense" in method_label else "tfidf"
    st.session_state.top_k = st.slider("Sources (Top-K)", 1, 5,
                                        st.session_state.top_k, label_visibility="visible")

    # API Key
    try:
        st.secrets["GROQ_API_KEY"]
        st.markdown('<div style="color:#10a37f;font-size:0.8rem;margin-top:0.5rem">✅ API key active</div>', unsafe_allow_html=True)
    except Exception:
        manual = st.text_input("🔑 Groq API Key", type="password", placeholder="gsk_...",
                               label_visibility="visible")
        if manual: st.session_state["manual_key"] = manual

    # Knowledge base
    st.markdown('<div class="sb-label">Knowledge Base</div>', unsafe_allow_html=True)
    for lbl in DOC_LABELS.values():
        st.markdown(f'<div style="color:#666;font-size:0.82rem;padding:2px 0">{lbl}</div>', unsafe_allow_html=True)


# ══ MAIN AREA ════════════════════════════════════════════════════════════════
PROC = os.path.join(BASE_DIR, "data", "processed")
page = st.session_state.page

# ─── CHAT PAGE ───────────────────────────────────────────────────────────────
if page == "chat":
    # Welcome screen
    if not st.session_state.messages:
        st.markdown("""
        <div class="welcome-hero">
          <h1>🩺 MedRAG</h1>
          <p>Your AI-powered Medical FAQ Assistant<br>
          <small style="color:#555">Answers grounded in a curated medical knowledge base</small></p>
        </div>""", unsafe_allow_html=True)

        suggestions = [
            ("🩸", "What are the symptoms of diabetes?"),
            ("💓", "How is high blood pressure treated?"),
            ("🦠", "What is long COVID?"),
            ("❤️", "What causes heart disease?"),
            ("🧠", "What is the difference between stress and anxiety?"),
            ("🎗️", "What are warning signs of cancer?"),
        ]
        cols = st.columns(2)
        for i, (icon, q) in enumerate(suggestions):
            with cols[i % 2]:
                if st.button(f"{icon} {q}", key=f"sug_{i}"):
                    st.session_state.pending_q = q
                    st.rerun()

    # Render chat messages
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"], avatar="🧑" if msg["role"]=="user" else "🩺"):
            st.markdown(msg["content"])
            if msg.get("sources"):
                with st.expander(f"📎 View {len(msg['sources'])} Sources", expanded=False):
                    for rank, chunk in enumerate(msg["sources"], 1):
                        excerpt  = smart_excerpt(chunk["text"], msg.get("query",""))
                        hl_text  = highlight(excerpt, msg.get("query",""))
                        lbl      = doc_label(chunk["doc_id"])
                        score    = chunk.get("score", 0)
                        st.markdown(f"""
                        <div class="source-block">
                          <div class="source-label">Rank {rank} · {lbl}
                            <span class="score-badge">{score:.3f}</span>
                          </div>
                          {hl_text}
                        </div>""", unsafe_allow_html=True)

    # Chat input
    user_input = st.chat_input("Ask a medical question…")

    # Handle suggestion click or user input
    q = user_input or st.session_state.pop("pending_q", None)

    if q:
        api_key = get_api_key()
        if not api_key:
            st.error("⚠️ Add your Groq API key in the sidebar."); st.stop()

        # Add user message
        st.session_state.messages.append({"role": "user", "content": q})
        with st.chat_message("user", avatar="🧑"):
            st.markdown(q)

        # Generate response
        with st.chat_message("assistant", avatar="🩺"):
            with st.spinner("Thinking…"):
                try:
                    chunks, texts, tfidf_ret, dense_ret = load_retrievers()
                    client = load_client(api_key)
                    from part2_retrieval import retrieve
                    from part3_generation import generate_answer

                    ctx    = retrieve(q, tfidf_ret, dense_ret, chunks,
                                      top_k=st.session_state.top_k,
                                      method=st.session_state.method)
                    result = generate_answer(q, ctx, client)
                    answer = result["answer"]

                    st.markdown(answer)

                    # Show sources collapsed
                    with st.expander(f"📎 View {len(ctx)} Sources", expanded=False):
                        for rank, chunk in enumerate(ctx, 1):
                            excerpt  = smart_excerpt(chunk["text"], q)
                            hl_text  = highlight(excerpt, q)
                            lbl      = doc_label(chunk["doc_id"])
                            score    = chunk.get("score", 0)
                            st.markdown(f"""
                            <div class="source-block">
                              <div class="source-label">Rank {rank} · {lbl}
                                <span class="score-badge">{score:.3f}</span>
                              </div>
                              {hl_text}
                            </div>""", unsafe_allow_html=True)

                    st.session_state.messages.append({
                        "role": "assistant", "content": answer,
                        "sources": ctx, "query": q
                    })
                except Exception as e:
                    err = f"❌ Error: {e}"
                    st.error(err)
                    st.session_state.messages.append({"role":"assistant","content":err})
        st.rerun()

# ─── COMPARE PAGE ─────────────────────────────────────────────────────────────
elif page == "compare":
    st.markdown("## ⚖️ TF-IDF vs Dense — Side by Side")
    st.markdown('<p style="color:#666">Compare how both retrieval methods rank chunks for the same query.</p>', unsafe_allow_html=True)

    cq = st.text_input("Enter a query to compare:", placeholder="e.g. What causes heart disease?")
    if st.button("⚖️ Compare"):
        if cq.strip():
            try:
                chunks, texts, tfidf_ret, dense_ret = load_retrievers()
                from part2_retrieval import retrieve
                col_tf, col_dn = st.columns(2)
                for col, method, label in [(col_tf,"tfidf","📊 TF-IDF"), (col_dn,"dense","🧠 Dense")]:
                    with col:
                        st.markdown(f"### {label}")
                        for rank, c in enumerate(retrieve(cq, tfidf_ret, dense_ret, chunks, top_k=3, method=method), 1):
                            excerpt = smart_excerpt(c["text"], cq)
                            hl      = highlight(excerpt, cq)
                            st.markdown(f"""
                            <div class="source-block">
                              <div class="source-label">Rank {rank} · {doc_label(c['doc_id'])}
                                <span class="score-badge">{c['score']:.4f}</span>
                              </div>{hl}
                            </div>""", unsafe_allow_html=True)
            except Exception as e:
                st.error(f"❌ {e}")

# ─── EVALUATION PAGE ──────────────────────────────────────────────────────────
elif page == "eval":
    st.markdown("## 📊 Experimental Evaluation")
    st.markdown('<p style="color:#666">Automatically tests the RAG system on 10 queries and scores accuracy.</p>', unsafe_allow_html=True)

    if st.button("▶️ Run Full Evaluation"):
        api_key = get_api_key()
        if not api_key:
            st.error("⚠️ API key required.")
        else:
            try:
                chunks, texts, tfidf_ret, dense_ret = load_retrievers()
                client = load_client(api_key)
                from part2_retrieval import retrieve
                from part3_generation import generate_answer
                from part5_evaluation import evaluate_system
                rfn = lambda q: retrieve(q, tfidf_ret, dense_ret, chunks, top_k=3)
                gfn = lambda q, c: generate_answer(q, c, client)
                with st.spinner("Running 10 evaluation queries…"):
                    report = evaluate_system(rfn, gfn)
                st.success("✅ Evaluation complete!")
                st.rerun()
            except Exception as e:
                st.error(f"❌ {e}")

    eval_path = os.path.join(PROC, "evaluation_report.json")
    if os.path.exists(eval_path):
        with open(eval_path) as f:
            rpt = json.load(f)
        s = rpt["summary"]
        cols = st.columns(4)
        for col, val, lbl in [
            (cols[0], s["total"], "Total Queries"),
            (cols[1], s["correct"], "✅ Correct"),
            (cols[2], s["total"]-s["correct"], "⚠️ Needs Review"),
            (cols[3], f"{s['accuracy']:.0%}", "Accuracy"),
        ]:
            col.markdown(f"""
            <div style="background:#1a1a1a;border:1px solid #2a2a2a;border-radius:12px;
                        padding:1.2rem;text-align:center">
              <div style="font-size:2rem;font-weight:700;color:#10a37f">{val}</div>
              <div style="font-size:0.8rem;color:#666;margin-top:0.2rem">{lbl}</div>
            </div>""", unsafe_allow_html=True)

        st.markdown("### Results")
        for r in rpt["results"]:
            icon = "✅" if "CORRECT" in str(r.get("status","")) else \
                   "⚠️" if "PARTIAL" in str(r.get("status","")) else \
                   "ℹ️" if "DECLINED" in str(r.get("status","")) else "❌"
            with st.expander(f"{icon} {r['query']}"):
                st.markdown(f"**Category:** {r['category']}  \n**Status:** `{r['status']}`  \n**Sources:** {', '.join(r.get('sources',[]))}  \n**Answer:** {r['answer']}")
    else:
        st.info("No report yet. Click **Run Full Evaluation** above.")

# ─── ABOUT PAGE ───────────────────────────────────────────────────────────────
elif page == "about":
    st.markdown("## ℹ️ About MedRAG")
    st.markdown("""
**MedRAG** is a Retrieval-Augmented Generation (RAG) system — BSBA Semester Project.

### 🏗️ How It Works
```
Your Question
    ↓
Retrieval (TF-IDF or Dense Embeddings + FAISS)
    ↓ Top-K relevant chunks
Generation (Llama 3.3-70B via Groq API)
    ↓
Answer + Sources
```

### 📚 Knowledge Base (8 Topics, 43 Chunks)
| | Topic | Q&A Pairs |
|-|-------|-----------|
|🩸|Diabetes|10|
|💓|Hypertension|10|
|🦠|COVID-19|10|
|❤️|Heart Disease|10|
|🧠|Mental Health|10|
|🥗|Nutrition|10|
|💉|Infectious Diseases|10|
|🎗️|Cancer|10|

### 🎁 Bonus Feature
**Source Citation Highlighting** — relevant keywords highlighted in green inside each source.

### 🛠️ Tech Stack
`sentence-transformers` · `FAISS` · `scikit-learn` · `Groq API` · `Streamlit`
    """)
