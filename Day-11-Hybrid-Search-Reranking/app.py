"""
Day 11 - Hybrid Search & Re-ranking (Streamlit Web App)
Antarmuka Web Interaktif untuk mengeksplorasi perpaduan Sparse Retrieval (BM25),
Dense Vector Embeddings, Reciprocal Rank Fusion (RRF), dan Cross-Encoder Re-ranking.
"""

import os
import sys
import pandas as pd
from pathlib import Path
import streamlit as st

# Pastikan modul internal terbaca
sys.path.append(str(Path(__file__).parent))
from hybrid_engine import HybridSearchEngine, RankedItem, ReRankedItem

st.set_page_config(
    page_title="Hybrid Search & Re-ranking | Day 11",
    page_icon="🔀",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom Styling
st.markdown("""
<style>
    .search-card {
        background-color: #fcfcfc;
        border: 1px solid #e2e8f0;
        border-radius: 8px;
        padding: 14px;
        margin-bottom: 12px;
        font-size: 0.9rem;
    }
    .badge-rrf {
        background-color: #e8f5e9;
        color: #1b5e20;
        padding: 3px 8px;
        border-radius: 12px;
        font-weight: bold;
    }
    .badge-bm25 {
        background-color: #fff3e0;
        color: #e65100;
        padding: 3px 8px;
        border-radius: 12px;
        font-weight: bold;
    }
    .badge-dense {
        background-color: #e1f5fe;
        color: #01579b;
        padding: 3px 8px;
        border-radius: 12px;
        font-weight: bold;
    }
    .rerank-card {
        background-color: #f0fdf4;
        border-left: 5px solid #22c55e;
        padding: 14px;
        border-radius: 8px;
        margin-bottom: 12px;
    }
</style>
""", unsafe_allow_html=True)

# Inisialisasi Engine di Session State
if "hybrid_engine" not in st.session_state:
    st.session_state["hybrid_engine"] = HybridSearchEngine()

engine: HybridSearchEngine = st.session_state["hybrid_engine"]

# Sidebar
with st.sidebar:
    st.title("⚙️ Parameter Hybrid Search")
    api_key_input = st.text_input(
        "Gemini API Key",
        value=os.getenv("GEMINI_API_KEY", ""),
        type="password",
        help="Dapatkan API key gratis di aistudio.google.com"
    )
    if api_key_input:
        os.environ["GEMINI_API_KEY"] = api_key_input

    model_option = st.selectbox(
        "Model Gemini",
        options=["gemini-2.5-flash", "gemini-2.5-pro"],
        index=0
    )

    top_k_val = st.slider("Jumlah Hasil (Top-K)", min_value=2, max_value=8, value=4)

    st.divider()
    st.subheader("⚖️ Bobot Pembobotan (Alpha)")
    bm25_ratio = st.slider(
        "Rasio Bobot: BM25 (Kiri) vs Dense Vector (Kanan)",
        min_value=0.0,
        max_value=1.0,
        value=0.5,
        step=0.1,
        help="0.0 = 100% Vector Semantik, 1.0 = 100% BM25 Kata Kunci Eksak, 0.5 = 50:50 RRF Balanced"
    )
    dense_ratio = round(1.0 - bm25_ratio, 2)
    st.caption(f"Bobot BM25: **{bm25_ratio*100:.0f}%** | Bobot Vector: **{dense_ratio*100:.0f}%**")

    st.divider()
    enable_rerank = st.checkbox("Aktifkan LLM Cross-Encoder Re-ranker", value=True, help="Menggunakan Gemini untuk menilai ulang dan menyaring kandidat secara presisi")

    st.divider()
    st.markdown("### 📌 Tentang Proyek")
    st.markdown("""
    **Day 11 dari 30 Days of AI Challenge**
    - Sparse BM25 (Okapi) Lexical Match
    - Dense Vector Semantic Similarity
    - Reciprocal Rank Fusion (RRF)
    - Cross-Encoder LLM Re-ranking
    """)

# Main Content
st.title("🔀 Hybrid Search Engine & Cross-Encoder Re-ranking")
st.markdown("Menggabungkan kekuatan pencarian kata kunci eksak (**BM25**) dan pemahaman semantik (**Dense Vectors**) dengan algoritma fusi **Reciprocal Rank Fusion (RRF)**.")

# Preset Queries
PRESETS = [
    ("Kueri Error Eksak", "ERR_REDIS_CONN_TIMEOUT"),
    ("Kode Kerentanan", "CVE-2024-38856"),
    ("Makna Konseptual", "Bagaimana cara mengamankan sesi login dari pencurian token script?"),
    ("Sinergi Hybrid", "HTTP 429 Too Many Requests exponential backoff"),
    ("Parafrase Bebas", "Trik database jutaan baris supaya kueri tidak lambat")
]

st.markdown("##### 💡 Uji Kasus Pencarian:")
cols_p = st.columns(len(PRESETS))
for i, (label, q_text) in enumerate(PRESETS):
    if cols_p[i].button(f"📌 {label}", key=f"btn_p_{i}", help=q_text, use_container_width=True):
        st.session_state["hybrid_query"] = q_text

search_query = st.text_input(
    "Masukkan kueri penelusuran:",
    value=st.session_state.get("hybrid_query", "ERR_REDIS_CONN_TIMEOUT"),
    placeholder="Ketik kata kunci eksak, kode error, atau pertanyaan bebas..."
)

tab_3way, tab_rerank, tab_corpus = st.tabs([
    "📊 Perbandingan 3 Arah (BM25 vs Vector vs Hybrid RRF)",
    "🎯 Hasil Cross-Encoder Re-ranking",
    "📚 Database Corpus"
])

# ----------------- TAB 1: 3-WAY COMPARISON -----------------
with tab_3way:
    if st.button("🚀 Jalankan Hybrid Retrieval", type="primary", use_container_width=True) or search_query:
        if not os.getenv("GEMINI_API_KEY"):
            st.error("🔑 API Key belum diatur! Masukkan GEMINI_API_KEY di sidebar.")
        else:
            with st.spinner("Menjalankan BM25, Dense Vector, dan RRF Fusion..."):
                try:
                    bm25_res = engine.search_bm25_only(search_query, top_k=top_k_val)
                    dense_res = engine.search_dense_only(search_query, top_k=top_k_val)
                    hybrid_res = engine.hybrid_search_rrf(
                        query=search_query,
                        top_k=top_k_val,
                        bm25_weight=bm25_ratio,
                        dense_weight=dense_ratio
                    )
                    st.session_state["last_hybrid_res"] = hybrid_res
                    st.session_state["last_query"] = search_query
                except Exception as e:
                    st.error(f"Error proses: {e}")
                    bm25_res, dense_res, hybrid_res = [], [], []

            col_b, col_d, col_h = st.columns(3, gap="medium")

            # Column 1: BM25 Only
            with col_b:
                st.subheader("1️⃣ BM25 Lexical (Kata Kunci)")
                st.caption("Hebat untuk kode error, ID teknis, dan kata unik.")
                if bm25_res:
                    for rank, (score, doc) in enumerate(bm25_res, 1):
                        st.markdown(f"""
                        <div class="search-card">
                            <span class="badge-bm25">Rank #{rank} | Score: {score:.2f}</span>
                            <h4 style="margin: 6px 0 4px 0; color: #e65100;">{doc['title']}</h4>
                            <p style="margin: 0; color: #555;">{doc['content'][:110]}...</p>
                        </div>
                        """, unsafe_allow_html=True)
                else:
                    st.warning("BM25: Tidak ada kecocokan kata persis.")

            # Column 2: Dense Vector Only
            with col_d:
                st.subheader("2️⃣ Dense Vector (Semantik)")
                st.caption("Hebat untuk parafrase konsep dan sinonim.")
                if dense_res:
                    for rank, (sim, doc) in enumerate(dense_res, 1):
                        st.markdown(f"""
                        <div class="search-card">
                            <span class="badge-dense">Rank #{rank} | Sim: {sim*100:.1f}%</span>
                            <h4 style="margin: 6px 0 4px 0; color: #01579b;">{doc['title']}</h4>
                            <p style="margin: 0; color: #555;">{doc['content'][:110]}...</p>
                        </div>
                        """, unsafe_allow_html=True)
                else:
                    st.warning("Vector: Tidak ada hasil.")

            # Column 3: Hybrid RRF Fusion
            with col_h:
                st.subheader("3️⃣ Hybrid RRF Fusion (Kombinasi)")
                st.caption("Menggabungkan peringkat terbaik dari kedua dunia.")
                if hybrid_res:
                    for rank, it in enumerate(hybrid_res, 1):
                        bm_badge = f"BM25 #{it.bm25_rank}" if it.bm25_rank else "BM25 -"
                        de_badge = f"Vector #{it.dense_rank}" if it.dense_rank else "Vector -"
                        st.markdown(f"""
                        <div class="search-card" style="border-color: #2e7d32; background-color: #f1f8e9;">
                            <span class="badge-rrf">RRF Rank #{rank} | Score: {it.rrf_score:.4f}</span><br>
                            <small style="color: #666;">({bm_badge} | {de_badge})</small>
                            <h4 style="margin: 6px 0 4px 0; color: #2e7d32;">{it.title}</h4>
                            <p style="margin: 0; color: #333;">{it.content[:110]}...</p>
                        </div>
                        """, unsafe_allow_html=True)
                else:
                    st.warning("Hybrid: Tidak ada hasil.")

# ----------------- TAB 2: RE-RANKING -----------------
with tab_rerank:
    st.subheader("🎯 Hasil Re-ranking Cross-Encoder (LLM Scoring)")
    st.markdown("Model **Gemini 2.5 Flash** bertindak sebagai *Cross-Encoder* yang membaca kueri bersama isi dokumen kandidat untuk memberikan skor relevansi 0-100 dan alasan argumentatif.")

    if "last_hybrid_res" in st.session_state and enable_rerank:
        candidates = st.session_state["last_hybrid_res"]
        active_q = st.session_state.get("last_query", search_query)

        if st.button("🔄 Eksekusi Ulang Re-ranking", use_container_width=True) or "last_rerank_res" not in st.session_state:
            with st.spinner("🤖 Gemini sedang mengevaluasi relevansi kandidat dokumen..."):
                try:
                    reranked_data = engine.rerank_with_llm(active_q, candidates, model_name=model_option)
                    st.session_state["last_rerank_res"] = reranked_data
                except Exception as e:
                    st.error(f"Gagal re-ranking: {e}")

        if "last_rerank_res" in st.session_state:
            rerank_list = st.session_state["last_rerank_res"]
            for idx, item in enumerate(rerank_list, 1):
                score_color = "#15803d" if item.relevance_score >= 80 else "#b45309" if item.relevance_score >= 50 else "#b91c1c"
                st.markdown(f"""
                <div class="rerank-card">
                    <div style="display: flex; justify-content: space-between; align-items: center;">
                        <span style="font-weight: bold; font-size: 1.1rem; color: {score_color};">#{idx} Skor Relevansi: {item.relevance_score} / 100</span>
                        <span style="font-size: 0.85rem; background-color: #e2e8f0; padding: 2px 8px; border-radius: 8px;">{item.category}</span>
                    </div>
                    <h3 style="margin: 8px 0 6px 0; color: #1e293b;">{item.title}</h3>
                    <p style="margin: 0 0 8px 0; color: #475569; font-size: 0.95rem;">{item.content}</p>
                    <div style="background-color: white; padding: 8px; border-radius: 6px; border: 1px dashed #cbd5e1;">
                        💡 <strong>Alasan Evaluasi AI:</strong> <span style="color: #334155;">{item.reasoning}</span>
                    </div>
                </div>
                """, unsafe_allow_html=True)
    else:
        st.info("Jalankan pencarian di Tab 1 dengan checkbox 'Aktifkan LLM Cross-Encoder Re-ranker' dicentang.")

# ----------------- TAB 3: CORPUS -----------------
with tab_corpus:
    st.subheader(f"📚 Dokumen Terdaftar dalam Corpus ({len(engine.corpus)} Dokumen)")
    df_c = pd.DataFrame(engine.corpus)
    st.dataframe(df_c[["id", "category", "title", "content"]], use_container_width=True, hide_index=True)
