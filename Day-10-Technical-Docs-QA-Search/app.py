"""
Day 10 - Technical Documentation & Codebase Q&A Search Engine (Streamlit Web App)
Antarmuka Web Interaktif untuk eksplorasi dokumentasi teknis, tanya jawab arsitektur,
dan inspeksi blok kode berbasis Semantic Header Chunking.
"""

import os
import sys
from pathlib import Path
import streamlit as st

# Pastikan modul internal terbaca
sys.path.append(str(Path(__file__).parent))
from docs_engine import TechnicalDocsEngine, TechnicalAnswer

DOCS_DIR = Path(__file__).parent / "sample_docs"

st.set_page_config(
    page_title="Technical Docs Q&A Search | Day 10",
    page_icon="🛠️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom Styling
st.markdown("""
<style>
    .ref-card {
        background-color: #f8f9fa;
        border-left: 4px solid #1565c0;
        padding: 12px;
        margin-bottom: 10px;
        border-radius: 6px;
    }
    .badge-file {
        background-color: #e3f2fd;
        color: #0d47a1;
        padding: 3px 10px;
        border-radius: 12px;
        font-weight: bold;
        font-size: 0.8rem;
    }
</style>
""", unsafe_allow_html=True)

# Inisialisasi Engine di Session State
if "docs_engine" not in st.session_state:
    st.session_state["docs_engine"] = TechnicalDocsEngine(DOCS_DIR)

engine: TechnicalDocsEngine = st.session_state["docs_engine"]

# Sidebar
with st.sidebar:
    st.title("⚙️ Pengaturan Docs AI")
    api_key_input = st.text_input(
        "Gemini API Key",
        value=os.getenv("GEMINI_API_KEY", ""),
        type="password",
        help="Dapatkan API key gratis di aistudio.google.com"
    )
    if api_key_input:
        os.environ["GEMINI_API_KEY"] = api_key_input

    model_option = st.selectbox(
        "Pilih Model Gemini",
        options=["gemini-2.5-flash", "gemini-2.5-pro"],
        index=0
    )

    top_k_val = st.slider("Jumlah Bab Rujukan (Top-K)", min_value=2, max_value=6, value=3)

    if st.button("🔄 Re-Index Dokumentasi", use_container_width=True):
        if not os.getenv("GEMINI_API_KEY"):
            st.error("Masukkan API Key terlebih dahulu!")
        else:
            with st.spinner("Mengindeks ulang dokumen..."):
                engine.load_or_index_docs(force_reindex=True)
                st.success(f"Berhasil diindeks ulang! ({len(engine.chunks)} sections)")

    st.divider()
    st.subheader("📂 File Dokumentasi Tersedia")
    md_files = sorted(list(DOCS_DIR.glob("*.md")))
    for f in md_files:
        st.caption(f"📄 `{f.name}`")

    st.divider()
    st.markdown("### 📌 Tentang Proyek")
    st.markdown("""
    **Day 10 dari 30 Days of AI Challenge**
    - Header-Based Semantic Markdown Chunking
    - Code Block Extraction & Language Detection
    - Dense Vector Search (text-embedding-004)
    - Architecture & Codebase Q&A Assistant
    """)

# Main Content
st.title("🛠️ Technical Docs & Codebase Q&A Search Engine")
st.markdown("Cari arsitektur sistem, spesifikasi API endpoint, dan best practice deployment secara semantik.")

# Preset Questions
PRESETS = [
    "Bagaimana mekanisme rotasi token JWT dan di mana token disimpan?",
    "Berapa kapasitas connection pool PostgreSQL dan bagaimana strategi index-nya?",
    "Jelaskan konfigurasi liveness dan readiness probes di Kubernetes",
    "Bagaimana arsitektur caching dengan Redis dan retry policy di RabbitMQ?",
    "Bagaimana format request dan response untuk endpoint POST /auth/login?"
]

st.markdown("##### 💡 Pertanyaan Teknis Siap Uji:")
cols_p = st.columns(3)
for i, pq in enumerate(PRESETS[:3]):
    if cols_p[i].button(pq, key=f"btn_pq_{i}", use_container_width=True):
        st.session_state["active_q"] = pq

cols_p2 = st.columns(2)
for j, pq2 in enumerate(PRESETS[3:]):
    if cols_p2[j].button(pq2, key=f"btn_pq2_{j}", use_container_width=True):
        st.session_state["active_q"] = pq2

tab_qa, tab_browser, tab_chunks = st.tabs([
    "💬 Technical Q&A Assistant",
    "📖 File Browser & Markdown Viewer",
    "🔍 Struktur Bab Terindeks"
])

# ----------------- TAB 1: QA ASSISTANT -----------------
with tab_qa:
    user_query = st.text_input(
        "Ajukan pertanyaan teknis tentang arsitektur sistem:",
        value=st.session_state.get("active_q", "Bagaimana mekanisme rotasi token JWT dan di mana token disimpan?"),
        placeholder="Tuliskan pertanyaan seputar database, API, keamanan, atau deployment..."
    )

    if st.button("🚀 Cari di Dokumentasi", type="primary", use_container_width=True) or "last_docs_answer" in st.session_state:
        if st.button("🚀 Cari di Dokumentasi", type="primary", use_container_width=True):
            if not user_query.strip():
                st.warning("Masukkan pertanyaan terlebih dahulu!")
            elif not os.getenv("GEMINI_API_KEY"):
                st.error("🔑 API Key belum diatur! Masukkan GEMINI_API_KEY di sidebar.")
            else:
                with st.spinner("Mencari rujukan bab & menganalisis kode..."):
                    try:
                        ans: TechnicalAnswer = engine.ask_technical_question(
                            question=user_query,
                            top_k=top_k_val,
                            model_name=model_option
                        )
                        st.session_state["last_docs_answer"] = ans
                        st.session_state["last_docs_query"] = user_query
                    except Exception as e:
                        st.error(f"Error proses: {e}")

        if "last_docs_answer" in st.session_state:
            ans: TechnicalAnswer = st.session_state["last_docs_answer"]
            st.divider()

            col_ans, col_ref = st.columns([1.3, 1], gap="large")

            with col_ans:
                st.subheader("💡 Penjelasan Arsitektur & Rekomendasi:")
                st.markdown(ans.direct_answer)

                if ans.suggested_follow_up_questions:
                    st.markdown("##### 📌 Saran Pertanyaan Lanjutan:")
                    for fq in ans.suggested_follow_up_questions:
                        if st.button(f"👉 {fq}", key=f"fq_{fq}"):
                            st.session_state["active_q"] = fq
                            st.rerun()

            with col_ref:
                st.subheader("📑 Rujukan Bagian Dokumentasi:")
                for c in ans.referenced_sections:
                    st.markdown(f"""
                    <div class="ref-card">
                        <span class="badge-file">{c.file_name}</span>
                        <strong style="color: #0d47a1; margin-left: 6px;">{c.relevance_pct}</strong><br>
                        <small style="color: #666;">Hierarki: <strong>{c.header_breadcrumb}</strong></small>
                        <p style="margin: 6px 0 0 0; color: #333; font-size: 0.88rem;">{c.snippet}</p>
                    </div>
                    """, unsafe_allow_html=True)

# ----------------- TAB 2: FILE BROWSER -----------------
with tab_browser:
    st.subheader("📖 Lihat Dokumen Asli")
    selected_doc = st.selectbox("Pilih Dokumen:", [f.name for f in md_files])
    if selected_doc:
        doc_content = (DOCS_DIR / selected_doc).read_text(encoding="utf-8")
        st.markdown(doc_content)

# ----------------- TAB 3: INDEXED CHUNKS -----------------
with tab_chunks:
    st.subheader(f"🔍 Daftar Seluruh Bab Terindeks ({len(engine.chunks)} Chunks)")
    for ch in engine.chunks:
        with st.expander(f"#{ch.chunk_id} [{ch.file_name}] {ch.header_breadcrumb}"):
            st.write(f"Panjang Karakter: **{ch.char_count}**")
            st.text(ch.content)
            if ch.code_blocks:
                st.markdown("**Blok Kode:**")
                for cb in ch.code_blocks:
                    st.code(cb.code, language=cb.language)
