"""
Day 01 - Smart AI Text Analyzer (Streamlit Web App)
Antarmuka Web Interaktif untuk analisis teks, sentimen, topik kunci, dan rekomendasi aksi.
"""

import os
import sys
import json
from pathlib import Path
import streamlit as st

# Pastikan path modul terbaca
sys.path.append(str(Path(__file__).parent))
from analyzer import analyze_text, AnalysisResult

st.set_page_config(
    page_title="AI Smart Text Analyzer | Day 01",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom Styling
st.markdown("""
<style>
    .metric-card {
        background-color: #f8f9fa;
        border-radius: 10px;
        padding: 15px;
        border-left: 5px solid #0066cc;
        margin-bottom: 10px;
    }
    .topic-badge {
        display: inline-block;
        background-color: #e3f2fd;
        color: #0d47a1;
        padding: 4px 12px;
        border-radius: 16px;
        margin: 4px;
        font-weight: 600;
        font-size: 0.88rem;
    }
</style>
""", unsafe_allow_html=True)

# Sidebar
with st.sidebar:
    st.title("⚙️ Pengaturan AI")
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

    st.divider()
    st.markdown("### 📌 Tentang Proyek")
    st.markdown("""
    **Day 01 dari 30 Days of AI Challenge**
    - Ekstraksi intisari otomatis
    - Analisis sentimen mendalam + skor
    - Ekstraksi kata kunci & entitas
    - Deteksi saran / poin tindakan
    """)
    st.caption("Dibuat dengan ❤️ menggunakan Python, Streamlit & Gemini API")

# Main Header
st.title("🤖 Smart AI Text & Sentiment Analyzer")
st.markdown("Analisis artikel, ulasan pelanggan, dokumen, atau teks panjang secara instan dengan kecerdasan buatan.")

col1, col2 = st.columns([1, 1], gap="medium")

with col1:
    st.subheader("📥 Input Teks")
    
    # Tab input: Manual Text vs File Upload
    input_tab1, input_tab2 = st.tabs(["✍️ Ketik / Tempel Teks", "📁 Upload File (.txt / .md)"])
    
    sample_text_default = """Pelayanan dari tim customer support sangat cepat dan ramah! Masalah refund saya selesai dalam waktu kurang dari 30 menit. Namun, saya merasa navigasi di aplikasi mobile masih agak membingungkan dan sering mengalami loading lama saat membuka riwayat transaksi. Mohon segera diperbaiki pada update versi berikutnya agar pengalaman pengguna makin maksimal."""
    
    with input_tab1:
        user_text = st.text_area(
            "Masukkan teks Anda di sini:",
            value=sample_text_default,
            height=250,
            placeholder="Tulis atau tempel teks yang ingin dianalisis..."
        )

    with input_tab2:
        uploaded_file = st.file_uploader("Pilih file teks", type=["txt", "md"])
        if uploaded_file is not None:
            user_text = uploaded_file.read().decode("utf-8")
            st.success(f"File '{uploaded_file.name}' berhasil dimuat!")

    analyze_btn = st.button("🚀 Mulai Analisis Teks", type="primary", use_container_width=True)

with col2:
    st.subheader("📊 Hasil Analisis")

    if analyze_btn:
        if not user_text.strip():
            st.warning("Silakan masukkan teks terlebih dahulu!")
        elif not os.getenv("GEMINI_API_KEY"):
            st.error("🔑 API Key belum diatur! Masukkan GEMINI_API_KEY di sidebar atau file .env")
        else:
            with st.spinner("Sedang menganalisis teks dengan Gemini AI..."):
                try:
                    result: AnalysisResult = analyze_text(user_text, model_name=model_option)
                    
                    # Metrics row
                    m1, m2, m3 = st.columns(3)
                    sentiment_val = result.sentiment.sentiment.upper()
                    sentiment_emoji = "🟢" if sentiment_val == "POSITIVE" else "🔴" if sentiment_val == "NEGATIVE" else "🟡"
                    
                    m1.metric("Sentimen", f"{sentiment_emoji} {sentiment_val}")
                    m2.metric("Skor Kepercayaan", f"{int(result.sentiment.score * 100)}%")
                    m3.metric("Panjang Teks", f"{result.word_count} kata")

                    st.info(f"💡 **Alasan Sentimen:** {result.sentiment.explanation}")

                    # Tabs for structured output
                    res_tab1, res_tab2, res_tab3, res_tab4 = st.tabs([
                        "📝 Ringkasan",
                        "🏷️ Topik Kunci",
                        "⚡ Action Items",
                        "💻 Raw JSON"
                    ])

                    with res_tab1:
                        st.markdown(f"**Bahasa Terdeteksi:** `{result.detected_language}`")
                        st.markdown("### Ringkasan Intisari:")
                        st.write(result.summary)

                    with res_tab2:
                        st.markdown("### Topik & Entitas Utama:")
                        badges_html = "".join([f'<span class="topic-badge">#{topic}</span>' for topic in result.key_topics])
                        st.markdown(badges_html, unsafe_allow_html=True)

                    with res_tab3:
                        st.markdown("### Rekomendasi / Tindakan Terdeteksi:")
                        if result.action_items:
                            for idx, item in enumerate(result.action_items, 1):
                                st.markdown(f"{idx}. {item}")
                        else:
                            st.write("Tidak ada action items eksplisit pada teks ini.")

                    with res_tab4:
                        st.json(result.model_dump())

                    # Export options
                    st.divider()
                    col_exp1, col_exp2 = st.columns(2)
                    with col_exp1:
                        st.download_button(
                            label="📥 Download JSON",
                            data=json.dumps(result.model_dump(), indent=2, ensure_ascii=False),
                            file_name="analysis_result.json",
                            mime="application/json",
                            use_container_width=True
                        )
                    with col_exp2:
                        md_content = f"""# Hasil Analisis Teks AI (Day 01)
- **Bahasa:** {result.detected_language}
- **Sentimen:** {result.sentiment.sentiment} ({result.sentiment.score * 100:.1f}%)
- **Penjelasan:** {result.sentiment.explanation}

## Ringkasan
{result.summary}

## Topik Kunci
{', '.join(['#' + t for t in result.key_topics])}

## Rekomendasi / Action Items
{chr(10).join(['- ' + item for item in result.action_items])}
"""
                        st.download_button(
                            label="📥 Download Markdown",
                            data=md_content,
                            file_name="analysis_result.md",
                            mime="text/markdown",
                            use_container_width=True
                        )

                except Exception as e:
                    st.error(f"Terjadi kesalahan saat memproses: {e}")
    else:
        st.info("👈 Masukkan teks di panel sebelah kiri lalu klik tombol **'Mulai Analisis Teks'**.")
