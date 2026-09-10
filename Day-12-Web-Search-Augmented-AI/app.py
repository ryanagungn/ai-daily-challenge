"""
Day 12 - Live Web-Search Augmented AI (Streamlit Web App)
Antarmuka Web Interaktif bergaya Perplexity AI untuk pencarian web real-time,
ekstraksi multi-sumber, dan sintesis jawaban berbasis sitasi rujukan.
"""

import os
import sys
from pathlib import Path
import streamlit as st

# Pastikan modul internal terbaca
sys.path.append(str(Path(__file__).parent))
from synthesizer import synthesize_web_answer, PerplexityResponse, WebResult

st.set_page_config(
    page_title="Mini Perplexity (Web AI) | Day 12",
    page_icon="🌐",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom Styling (Perplexity-inspired)
st.markdown("""
<style>
    .source-box {
        background-color: #f8fafc;
        border: 1px solid #e2e8f0;
        border-radius: 8px;
        padding: 10px;
        height: 100px;
        display: flex;
        flex-direction: column;
        justify-content: space-between;
        margin-bottom: 8px;
        transition: all 0.2s ease;
    }
    .source-box:hover {
        border-color: #0284c7;
        box-shadow: 0 4px 10px rgba(0,0,0,0.05);
    }
    .badge-src {
        background-color: #e0f2fe;
        color: #0369a1;
        padding: 2px 6px;
        border-radius: 6px;
        font-size: 0.75rem;
        font-weight: bold;
    }
    .answer-container {
        background-color: #ffffff;
        border: 1px solid #e2e8f0;
        border-radius: 12px;
        padding: 24px;
        margin-top: 15px;
        line-height: 1.6;
    }
</style>
""", unsafe_allow_html=True)

# State
if "history" not in st.session_state:
    st.session_state["history"] = []

# Sidebar
with st.sidebar:
    st.title("⚙️ Pengaturan Web AI")
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

    num_sources = st.slider("Maksimal Sumber Web", min_value=3, max_value=8, value=5)

    st.divider()
    st.markdown("### 📌 Tentang Proyek")
    st.markdown("""
    **Day 12 dari 30 Days of AI Challenge**
    - Live DuckDuckGo Web Search Integration
    - Real-Time Multi-Source Synthesis
    - Numbered Footnote Citations `[1]`, `[2]`
    - Perplexity-Inspired UX Architecture
    """)

# Main Content
st.title("🌐 Mini Perplexity — Live Web-Search AI")
st.markdown("Pencarian informasi langsung ke web secara real-time dengan sintesis jawaban komprehensif dan rujukan sitasi sumber.")

# Preset Chips
PRESETS = [
    "Apa itu Model Context Protocol (MCP) dari Anthropic?",
    "Perkembangan arsitektur DeepSeek-V3 dan MoE",
    "Berita peluncuran AI dan hardware terbaru bulan ini",
    "Framework Agentic AI paling populer untuk production"
]

st.markdown("##### 💡 Topik Penelusuran Populer:")
cols_pr = st.columns(len(PRESETS))
for i, pr in enumerate(PRESETS):
    if cols_pr[i].button(pr, key=f"btn_p_{i}", use_container_width=True):
        st.session_state["active_search"] = pr

# Search Input
user_query = st.text_input(
    "Tanyakan apa saja seputar topik terkini di web:",
    value=st.session_state.get("active_search", "Apa itu Model Context Protocol (MCP) dari Anthropic?"),
    placeholder="Ketik topik atau pertanyaan terkini..."
)

col_btn1, col_btn2 = st.columns([1, 4])
with col_btn1:
    search_clicked = st.button("🚀 Cari & Sintesis", type="primary", use_container_width=True)

if search_clicked or "last_perplexity_res" in st.session_state:
    if search_clicked:
        if not user_query.strip():
            st.warning("Masukkan pertanyaan terlebih dahulu!")
        elif not os.getenv("GEMINI_API_KEY"):
            st.error("🔑 API Key belum diatur! Masukkan GEMINI_API_KEY di sidebar.")
        else:
            with st.spinner("🔍 Menjelajahi web & mensintesis jawaban dengan Gemini..."):
                try:
                    res: PerplexityResponse = synthesize_web_answer(
                        user_query=user_query,
                        max_search_results=num_sources,
                        model_name=model_option
                    )
                    st.session_state["last_perplexity_res"] = res
                    st.session_state["history"].append(res)
                except Exception as e:
                    st.error(f"Gagal melakukan pencarian: {e}")

    if "last_perplexity_res" in st.session_state:
        res: PerplexityResponse = st.session_state["last_perplexity_res"]

        st.divider()
        st.caption(f"⏱️ Waktu Pencarian Web: **{res.search_latency_ms:.0f} ms** | Total Latensi: **{res.total_latency_ms:.0f} ms**")

        # 1. Sources Row
        st.markdown(f"#### 🔗 Sumber Web Rujukan ({len(res.sources)} Sumber):")
        cols_src = st.columns(min(len(res.sources), 4))
        for idx, src in enumerate(res.sources):
            col = cols_src[idx % min(len(res.sources), 4)]
            with col:
                st.markdown(f"""
                <div class="source-box">
                    <div>
                        <span class="badge-src">[{src.index}] {src.domain}</span>
                        <div style="font-weight: bold; font-size: 0.85rem; margin-top: 4px; overflow: hidden; text-overflow: ellipsis; display: -webkit-box; -webkit-line-clamp: 2; -webkit-box-orient: vertical;">
                            {src.title}
                        </div>
                    </div>
                    <a href="{src.url}" target="_blank" style="font-size: 0.75rem; color: #0284c7; text-decoration: none;">Buka Link ↗</a>
                </div>
                """, unsafe_allow_html=True)

        # 2. Main Synthesized Answer
        st.markdown("#### 🧠 Jawaban Sintetis:")
        st.markdown(f"""
        <div class="answer-container">
        """, unsafe_allow_html=True)
        st.markdown(res.answer_markdown)
        st.markdown("</div>", unsafe_allow_html=True)

        # 3. Related Questions
        if res.related_questions:
            st.markdown("---")
            st.markdown("##### 💡 Pertanyaan Terkait:")
            cols_rel = st.columns(len(res.related_questions))
            for k, rel_q in enumerate(res.related_questions):
                if cols_rel[k].button(f"👉 {rel_q}", key=f"rel_{k}", use_container_width=True):
                    st.session_state["active_search"] = rel_q
                    st.rerun()

        # 4. Export
        st.divider()
        col_ex1, col_ex2 = st.columns(2)
        with col_ex1:
            sources_md = "\n".join([f"- [{s.index}] [{s.title}]({s.url}) - *{s.domain}*" for s in res.sources])
            full_md = f"# {res.query}\n\n{res.answer_markdown}\n\n## Sumber Rujukan\n{sources_md}\n"
            st.download_button(
                "📥 Download Hasil (Markdown)",
                data=full_md,
                file_name=f"perplexity_{res.query[:20].lower().replace(' ', '_')}.md",
                mime="text/markdown",
                use_container_width=True
            )
        with col_ex2:
            st.download_button(
                "💾 Download Data (JSON)",
                data=res.model_dump_json(indent=2),
                file_name="perplexity_result.json",
                mime="application/json",
                use_container_width=True
            )
