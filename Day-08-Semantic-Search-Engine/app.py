"""
Day 08 - Semantic Search Engine with Vector Embeddings (Streamlit Web App)
Antarmuka Web Interaktif untuk pencarian semantik vektor, perbandingan vs keyword match,
visualisasi ruang embedding 2D (PCA), dan penambahan dokumen ke Vector Store.
"""

import os
import sys
import json
import pandas as pd
import numpy as np
from pathlib import Path
import streamlit as st

# Pastikan modul internal terbaca
sys.path.append(str(Path(__file__).parent))
from embeddings_engine import VectorDatabase, SearchResult

st.set_page_config(
    page_title="Semantic Search Engine | Day 08",
    page_icon="🔍",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom Styling
st.markdown("""
<style>
    .result-card {
        background-color: #fcfcfc;
        border: 1px solid #e0e0e0;
        border-radius: 10px;
        padding: 16px;
        margin-bottom: 14px;
        transition: all 0.2s ease-in-out;
    }
    .result-card:hover {
        border-color: #00897b;
        box-shadow: 0 4px 12px rgba(0,0,0,0.06);
    }
    .score-badge {
        background-color: #e0f2f1;
        color: #004d40;
        padding: 4px 10px;
        border-radius: 12px;
        font-weight: bold;
        font-size: 0.85rem;
    }
    .cat-chip {
        background-color: #ede7f6;
        color: #4527a0;
        padding: 3px 10px;
        border-radius: 12px;
        font-size: 0.8rem;
        font-weight: 500;
    }
</style>
""", unsafe_allow_html=True)

# Inisialisasi Database
if "vdb" not in st.session_state:
    st.session_state["vdb"] = VectorDatabase()

vdb: VectorDatabase = st.session_state["vdb"]

# Sidebar
with st.sidebar:
    st.title("⚙️ Pengaturan Vektor")
    api_key_input = st.text_input(
        "Gemini API Key",
        value=os.getenv("GEMINI_API_KEY", ""),
        type="password",
        help="Dapatkan API key gratis di aistudio.google.com"
    )
    if api_key_input:
        os.environ["GEMINI_API_KEY"] = api_key_input

    model_option = st.selectbox(
        "Embedding Model",
        options=["text-embedding-004"],
        index=0
    )

    top_k_val = st.slider("Jumlah Hasil (Top-K)", min_value=1, max_value=8, value=4)
    threshold_val = st.slider("Similarity Threshold", min_value=0.0, max_value=1.0, value=0.35, step=0.05)

    st.divider()
    if st.button("🔄 Re-Index / Sync Embeddings", use_container_width=True):
        if not os.getenv("GEMINI_API_KEY"):
            st.error("Masukkan API Key terlebih dahulu!")
        else:
            with st.spinner("Sinkronisasi vektor..."):
                updated = vdb.ensure_indexed(model_name=model_option)
                st.success(f"Sinkronisasi selesai! ({updated} vektor baru dibuat)")

    st.divider()
    st.markdown("### 📌 Tentang Proyek")
    st.markdown("""
    **Day 08 dari 30 Days of AI Challenge**
    - Vector Embeddings (text-embedding-004)
    - Cosine Similarity Semantic Ranking
    - 2D PCA Dimensionality Reduction
    - Vector Knowledge Base Indexing
    """)

# Main Content
st.title("🔍 AI Semantic Search Engine & Vector Space")
st.markdown("Pencarian cerdas berbasis makna semantik (*conceptual intent*), bukan sekadar kecocokan kata kunci (*keyword matching*).")

# Preset Queries
PRESETS = [
    "Bagaimana cara mengamankan container di lingkungan cloud?",
    "Metode optimasi kueri dan indexing pada database",
    "Cara mencegah model AI menghafal data latihan (overfitting)",
    "Perbedaan mendasar antara RAG dan fine-tuning",
    "Arsitektur berbasis peristiwa untuk decoupling microservices"
]

st.markdown("##### 💡 Contoh Pertanyaan Penelusuran:")
cols_p = st.columns(len(PRESETS))
for i, p_text in enumerate(PRESETS):
    if cols_p[i].button(f"📌 {p_text[:28]}...", key=f"btn_p_{i}", help=p_text):
        st.session_state["search_query"] = p_text

# Search Bar
search_query = st.text_input(
    "Masukkan kueri penelusuran Anda:",
    value=st.session_state.get("search_query", "Bagaimana cara mengamankan container di cloud?"),
    placeholder="Ketik topik atau pertanyaan dalam bahasa apa pun..."
)

tab_search, tab_viz, tab_ingest, tab_docs = st.tabs([
    "🔍 Hasil Pencarian (Semantic vs Keyword)",
    "🗺️ Visualisasi Ruang Vektor 2D",
    "➕ Tambah Dokumen Baru",
    "📚 Database Knowledge Base"
])

# ---------------- TAB 1: SEARCH RESULTS ----------------
with tab_search:
    if st.button("🚀 Cari Dokumen Sekarang", type="primary") or search_query:
        if not os.getenv("GEMINI_API_KEY"):
            st.error("🔑 API Key belum diatur! Masukkan GEMINI_API_KEY di sidebar atau file .env")
        else:
            with st.spinner("Menghitung vector embedding kueri & cosine similarity..."):
                try:
                    semantic_results = vdb.semantic_search(
                        query=search_query,
                        top_k=top_k_val,
                        threshold=threshold_val,
                        model_name=model_option
                    )
                    keyword_results = vdb.keyword_search(
                        query=search_query,
                        top_k=top_k_val
                    )
                except Exception as e:
                    st.error(f"Gagal melakukan pencarian: {e}")
                    semantic_results, keyword_results = [], []

            col_sem, col_key = st.columns(2, gap="large")

            # Left: Semantic Search
            with col_sem:
                st.subheader(f"🧠 Semantic Vector Search ({len(semantic_results)} hasil)")
                st.caption("Mencari dokumen berdasarkan kesamaan makna konseptual (Cosine Similarity).")

                if semantic_results:
                    for r in semantic_results:
                        st.markdown(f"""
                        <div class="result-card">
                            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 6px;">
                                <span class="cat-chip">{r.category}</span>
                                <span class="score-badge">Similarity: {r.similarity_percentage}</span>
                            </div>
                            <h4 style="margin: 0 0 6px 0; color: #00695c;">{r.title}</h4>
                            <p style="margin: 0; color: #444; font-size: 0.92rem; line-height: 1.4;">{r.content}</p>
                        </div>
                        """, unsafe_allow_html=True)
                else:
                    st.warning("Tidak ada dokumen yang melewati ambang batas kemiripan.")

            # Right: Keyword Search
            with col_key:
                st.subheader(f"🔤 Exact Keyword Search ({len(keyword_results)} hasil)")
                st.caption("Pencarian konvensional (Ctrl+F) berdasarkan kecocokan kata persis.")

                if keyword_results:
                    for r in keyword_results:
                        st.markdown(f"""
                        <div class="result-card">
                            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 6px;">
                                <span class="cat-chip">{r.category}</span>
                                <span class="score-badge" style="background-color: #ede7f6; color: #311b92;">{r.similarity_percentage}</span>
                            </div>
                            <h4 style="margin: 0 0 6px 0; color: #303f9f;">{r.title}</h4>
                            <p style="margin: 0; color: #444; font-size: 0.92rem; line-height: 1.4;">{r.content}</p>
                        </div>
                        """, unsafe_allow_html=True)
                else:
                    st.info("Pencarian kata kunci konvensional tidak menemukan kecocokan kata persis.")

# ---------------- TAB 2: 2D VECTOR SPACE ----------------
with tab_viz:
    st.subheader("🗺️ Proyeksi Ruang Vektor 2D (PCA Reduksi Dimensi)")
    st.markdown("""
    Model `text-embedding-004` memetakan setiap artikel menjadi vektor **768 Dimensi**.
    Di bawah ini adalah proyeksi 2D menggunakan algoritma **Principal Component Analysis (PCA)** untuk melihat bagaimana dokumen dengan topik serupa saling berdekatan dalam ruang vektor.
    """)

    if len(vdb.vectors) < 2:
        st.info("Diperlukan minimal 2 dokumen yang terindeks untuk visualisasi 2D.")
    else:
        projected, x_coords, y_coords = vdb.compute_2d_projection()
        if projected:
            df_plot = pd.DataFrame(projected)
            
            # Scatter Plot
            st.scatter_chart(
                df_plot,
                x="x",
                y="y",
                color="category",
                size=200,
                use_container_width=True
            )

            with st.expander("📋 Koordinat Vektor Dokumen (2D Projection)"):
                st.dataframe(df_plot[["id", "category", "title", "x", "y"]], use_container_width=True, hide_index=True)

# ---------------- TAB 3: INGEST NEW DOCS ----------------
with tab_ingest:
    st.subheader("➕ Tambahkan Dokumen ke Vector Store")
    st.markdown("Dokumen baru akan otomatis diubah menjadi vektor embedding dan disimpan ke knowledge base.")

    with st.form("form_add_doc"):
        doc_title = st.text_input("Judul Dokumen:", placeholder="Contoh: Arsitektur Micro-Frontends dengan Module Federation")
        doc_category = st.selectbox("Kategori:", ["Artificial Intelligence", "Cyber Security", "Database Engineering", "Cloud & DevOps", "Software Architecture", "Machine Learning", "General"])
        doc_content = st.text_area("Isi Konten Dokumen:", height=160, placeholder="Tuliskan penjelasan atau dokumentasi teknis...")

        submit_doc = st.form_submit_button("💾 Embed & Simpan Dokumen", type="primary", use_container_width=True)

        if submit_doc:
            if not doc_title.strip() or not doc_content.strip():
                st.warning("Judul dan isi konten tidak boleh kosong!")
            elif not os.getenv("GEMINI_API_KEY"):
                st.error("🔑 API Key belum diatur!")
            else:
                with st.spinner("Menghasilkan embedding & menyimpan..."):
                    try:
                        new_id = vdb.add_document(doc_title, doc_category, doc_content, model_name=model_option)
                        st.success(f"🎉 Dokumen '{doc_title}' berhasil diindeks dengan ID: `{new_id}`!")
                        st.rerun()
                    except Exception as e:
                        st.error(f"Gagal menambahkan dokumen: {e}")

# ---------------- TAB 4: KNOWLEDGE BASE EXPLORER ----------------
with tab_docs:
    st.subheader(f"📚 Seluruh Dokumen Knowledge Base ({len(vdb.documents)} Dokumen)")
    df_all = pd.DataFrame(vdb.documents)
    st.dataframe(df_all[["id", "category", "title", "content"]], use_container_width=True, hide_index=True)
