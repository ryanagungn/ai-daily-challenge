"""
Day 09 - Chat with Your PDF (Streamlit Web App)
Antarmuka Web Interaktif untuk Tanya Jawab Dokumen PDF berbasis Retrieval-Augmented Generation (RAG).
"""

import os
import sys
from pathlib import Path
import streamlit as st

# Pastikan modul internal terbaca
sys.path.append(str(Path(__file__).parent))
from rag_engine import PDFRAGSession, RAGAnswer

st.set_page_config(
    page_title="Chat with Your PDF (RAG) | Day 09",
    page_icon="📄",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom Styling
st.markdown("""
<style>
    .citation-card {
        background-color: #f8f9fa;
        border-left: 4px solid #00897b;
        padding: 10px;
        margin-bottom: 8px;
        border-radius: 6px;
        font-size: 0.88rem;
    }
    .badge-conf {
        padding: 3px 8px;
        border-radius: 12px;
        font-size: 0.75rem;
        font-weight: bold;
    }
</style>
""", unsafe_allow_html=True)

# State Management
if "rag_session" not in st.session_state:
    st.session_state["rag_session"] = None

if "messages" not in st.session_state:
    st.session_state["messages"] = []

# Sidebar
with st.sidebar:
    st.title("⚙️ Pengaturan RAG")
    api_key_input = st.text_input(
        "Gemini API Key",
        value=os.getenv("GEMINI_API_KEY", ""),
        type="password",
        help="Dapatkan API key gratis di aistudio.google.com"
    )
    if api_key_input:
        os.environ["GEMINI_API_KEY"] = api_key_input

    model_option = st.selectbox(
        "Model LLM",
        options=["gemini-2.5-flash", "gemini-2.5-pro"],
        index=0
    )

    top_k_chunks = st.slider("Jumlah Chunks Relevan (Top-K)", min_value=2, max_value=6, value=3)
    chunk_size_val = st.slider("Ukuran Chunk (Karakter)", min_value=300, max_value=1000, value=600, step=50)

    st.divider()
    st.subheader("📁 Sumber Dokumen")
    
    uploaded_file = st.file_uploader("Upload File PDF / TXT", type=["pdf", "txt"])
    use_sample = st.button("📄 Gunakan Sample Dokumen (AI Playbook)", use_container_width=True)

    st.divider()
    st.markdown("### 📌 Tentang Proyek")
    st.markdown("""
    **Day 09 dari 30 Days of AI Challenge**
    - Retrieval-Augmented Generation (RAG)
    - PDF Chunking & Semantic Vector Retrieval
    - Anti-Hallucination Context Grounding
    - Source Citation Attribution
    """)

# Helper loader
def load_document_to_session(source, name):
    if not os.getenv("GEMINI_API_KEY"):
        st.error("🔑 API Key belum diatur! Masukkan GEMINI_API_KEY di sidebar.")
        return False

    session = PDFRAGSession(chunk_size=chunk_size_val, chunk_overlap=100)
    with st.spinner(f"Memproses dan mengindeks '{name}'..."):
        try:
            total_chunks = session.load_and_index_document(source, doc_name=name)
            st.session_state["rag_session"] = session
            st.session_state["doc_name"] = name
            st.session_state["total_chunks"] = total_chunks
            st.session_state["messages"] = []
            return True
        except Exception as e:
            st.error(f"Gagal memproses dokumen: {e}")
            return False

if use_sample:
    sample_pdf = Path(__file__).parent / "sample_ai_playbook.pdf"
    if sample_pdf.exists():
        load_document_to_session(sample_pdf, sample_pdf.name)

if uploaded_file is not None:
    if st.session_state.get("doc_name") != uploaded_file.name:
        load_document_to_session(uploaded_file.read(), uploaded_file.name)

# Main Area
st.title("📄 Chat with Your PDF (Simple RAG)")
st.markdown("Tanya jawab akurat berbasis dokumen Anda dengan sitasi sumber dan pencegahan halusinasi.")

session: PDFRAGSession = st.session_state.get("rag_session")

if session is None:
    st.info("👈 Silakan upload file PDF Anda di sidebar atau klik tombol **'Gunakan Sample Dokumen'** untuk memulai percakapan!")
else:
    doc_name = st.session_state.get("doc_name", "Dokumen")
    total_chunks = st.session_state.get("total_chunks", 0)

    # Document active badge
    col_st1, col_st2 = st.columns([3, 1])
    with col_st1:
        st.success(f"📂 **Dokumen Aktif:** `{doc_name}` ({total_chunks} chunks terindeks)")
    with col_st2:
        if st.button("🗑️ Bersihkan Chat", use_container_width=True):
            st.session_state["messages"] = []
            st.rerun()

    # Preset Question Pills
    st.markdown("##### 💡 Contoh Pertanyaan Cepat:")
    cols_pre = st.columns(3)
    preset_q = [
        "Vector database apa yang direkomendasikan untuk production?",
        "Berapa batas SLA latency respon RAG?",
        "Apa aturan terkait perlindungan data privasi PII?"
    ]
    for i, pq in enumerate(preset_q):
        if cols_pre[i].button(pq, key=f"btn_pq_{i}", use_container_width=True):
            st.session_state["pending_query"] = pq

    # Display Chat History
    for msg in st.session_state["messages"]:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])
            if "citations" in msg and msg["citations"]:
                with st.expander(f"📑 Lihat Rujukan Sitasi ({len(msg['citations'])} Chunks)"):
                    for c in msg["citations"]:
                        st.markdown(f"""
                        <div class="citation-card">
                            <strong>Chunk #{c['chunk_id']} (Hal {c['page_number']}) — Relevansi: {c['similarity_score']*100:.1f}%</strong><br>
                            <em>"{c['snippet']}"</em>
                        </div>
                        """, unsafe_allow_html=True)

    # Chat Input
    query_input = st.chat_input("Ketik pertanyaan seputar dokumen Anda di sini...")
    if "pending_query" in st.session_state:
        query_input = st.session_state.pop("pending_query")

    if query_input:
        # Display user message
        st.session_state["messages"].append({"role": "user", "content": query_input})
        with st.chat_message("user"):
            st.markdown(query_input)

        # Generate Assistant Response
        with st.chat_message("assistant"):
            with st.spinner("Mencari konteks & menyusun jawaban..."):
                ans: RAGAnswer = session.ask(
                    question=query_input,
                    top_k=top_k_chunks,
                    model_name=model_option
                )

                st.markdown(ans.answer)

                if ans.citations:
                    with st.expander(f"📑 Lihat Rujukan Sitasi ({len(ans.citations)} Chunks)"):
                        for c in ans.citations:
                            st.markdown(f"""
                            <div class="citation-card">
                                <strong>Chunk #{c.chunk_id} (Hal {c.page_number}) — Relevansi: {c.similarity_score*100:.1f}%</strong><br>
                                <em>"{c.snippet}"</em>
                            </div>
                            """, unsafe_allow_html=True)

                st.session_state["messages"].append({
                    "role": "assistant",
                    "content": ans.answer,
                    "citations": [c.model_dump() for c in ans.citations]
                })

    # Chunk Inspector Expander
    with st.expander("🔍 Introspeksi Pemotongan Teks (All Document Chunks)"):
        st.write(f"Total Chunks: **{len(session.chunks)}**")
        for ch in session.chunks:
            st.caption(f"**Chunk #{ch.chunk_id}** | Halaman: {ch.page_number} | Panjang: {ch.char_count} karakter")
            st.text(ch.content)
            st.divider()
