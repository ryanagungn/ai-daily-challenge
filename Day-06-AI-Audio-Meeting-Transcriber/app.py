"""
Day 06 - AI Audio Meeting Transcriber & Minutes Summarizer (Streamlit Web App)
Antarmuka Web Interaktif untuk transkripsi audio rapat, ekstraksi notulen otomatis, dan manajemen action items.
"""

import os
import sys
import json
import pandas as pd
from pathlib import Path
import streamlit as st

# Pastikan modul internal terbaca
sys.path.append(str(Path(__file__).parent))
from transcriber import process_meeting_audio, process_meeting_text_transcript, MeetingMinutes

st.set_page_config(
    page_title="AI Meeting Minutes & Transcriber | Day 06",
    page_icon="🎙️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom Styling
st.markdown("""
<style>
    .header-card {
        background-color: #f0f4f8;
        border-radius: 12px;
        padding: 20px;
        border-left: 6px solid #1976d2;
        margin-bottom: 20px;
    }
    .attendee-chip {
        display: inline-block;
        background-color: #e3f2fd;
        color: #0d47a1;
        padding: 4px 12px;
        border-radius: 16px;
        font-size: 0.85rem;
        margin: 2px 4px;
        font-weight: 500;
    }
    .decision-box {
        background-color: #e8f5e9;
        border-left: 4px solid #2e7d32;
        padding: 12px;
        border-radius: 6px;
        margin-bottom: 8px;
    }
</style>
""", unsafe_allow_html=True)

# Sample Text
SAMPLE_MEETING_TEXT = """[00:00] Budi Santoso (Product Lead): Selamat pagi semuanya. Terima kasih sudah hadir di Sprint Planning & Quarterly Review Q4 kita hari ini. Agenda utama kita adalah evaluasi rilis fitur AI Text Analyzer dan persiapan arsitektur backend untuk integrasi Vector Database di sprint berikutnya.

[00:45] Siti Rahmawati (Lead Backend Engineer): Pagi Mas Budi. Dari sisi backend, performa API saat ini cukup stabil dengan latency rata-rata 350ms. Namun, untuk integrasi Vector DB, tim kami merekomendasikan menggunakan ChromaDB untuk tahap local testing, dan beralih ke Qdrant atau Pinecone saat production deployment di bulan depan.

[01:30] Ahmad Hidayat (DevOps & Security): Setuju dengan Mbak Siti. Dari sisi security dan compliance, kita perlu memastikan API Key OpenAI dan Gemini tersimpan aman di GCP Secret Manager atau AWS Secrets Manager, bukan di environment variable statis di container server.

[02:10] Budi Santoso: Bagus sekali. Jadi keputusannya:
1. Siti akan memimpin implementasi POC Vector DB menggunakan ChromaDB sampai hari Jumat ini.
2. Ahmad akan setup Secret Manager dan pipeline CI/CD di GitHub Actions paling lambat tanggal 15 September.
3. Saya akan menyusun dokumen PRD untuk fitur Multimodal Vision dan mempresentasikannya ke stakeholder minggu depan.

[02:50] Siti Rahmawati: Siap Mas Budi, nanti estimasi kebutuhan resource server akan saya share di Slack channel #ai-engineering.

[03:10] Budi Santoso: Baik, meeting kita sudahi sampai di sini. Semangat semuanya dan selamat bekerja!"""

# Sidebar
with st.sidebar:
    st.title("⚙️ Pengaturan Audio AI")
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

    lang_option = st.selectbox(
        "Bahasa Utama Audio",
        options=["Bahasa Indonesia", "English", "Campuran / Otomatis"],
        index=0
    )

    st.divider()
    st.markdown("### 📌 Tentang Proyek")
    st.markdown("""
    **Day 06 dari 30 Days of AI Challenge**
    - Audio Speech-to-Text with Speaker Diarization
    - Executive Summary & Action Items Extraction
    - Key Decisions & Topic Summaries
    """)

# Main Content
st.title("🎙️ AI Audio Meeting Transcriber & Minutes Summarizer")
st.markdown("Ubah rekaman suara rapat atau podcast menjadi transkrip lengkap, ringkasan eksekutif, dan daftar *Action Items* otomatis.")

col_left, col_right = st.columns([1, 1], gap="large")

with col_left:
    st.subheader("📥 Input Sumber Rapat")
    
    input_tab1, input_tab2, input_tab3 = st.tabs([
        "🎵 Upload Audio (.mp3/.wav/.m4a)",
        "✍️ Tempel Transkrip Teks",
        "📄 Gunakan Demo Sample"
    ])

    audio_bytes_data = None
    audio_mime = None
    text_input_data = None

    with input_tab1:
        uploaded_audio = st.file_uploader(
            "Upload file rekaman audio:",
            type=["mp3", "wav", "m4a", "ogg", "flac", "aac"]
        )
        if uploaded_audio is not None:
            audio_bytes_data = uploaded_audio.read()
            audio_mime = uploaded_audio.type or "audio/mp3"
            st.audio(audio_bytes_data, format=audio_mime)
            st.success(f"File '{uploaded_audio.name}' ({len(audio_bytes_data) // 1024} KB) siap diproses.")

    with input_tab2:
        text_transcript = st.text_area(
            "Tempel catatan rapat atau transkrip teks mentah:",
            height=260,
            placeholder="[00:00] Pembicara A: Selamat pagi...\n[01:00] Pembicara B: ..."
        )
        if text_transcript.strip():
            text_input_data = text_transcript

    with input_tab3:
        st.markdown("Gunakan contoh meeting internal tim AI Engineer (Sprint Planning Q4):")
        st.text_area("Preview Sample:", value=SAMPLE_MEETING_TEXT, height=180, disabled=True)
        if st.button("Pilih Sample Ini", use_container_width=True):
            text_input_data = SAMPLE_MEETING_TEXT
            st.success("Sample meeting dimuat!")

    process_btn = st.button("🚀 Buat Notulen & Transkripsi", type="primary", use_container_width=True)

with col_right:
    st.subheader("📋 Hasil Notulen Rapat")

    if process_btn:
        if not audio_bytes_data and not text_input_data:
            st.warning("Silakan upload file audio atau masukkan teks rapat terlebih dahulu!")
        elif not os.getenv("GEMINI_API_KEY"):
            st.error("🔑 API Key belum diatur! Masukkan GEMINI_API_KEY di sidebar atau file .env")
        else:
            with st.spinner("🤖 Mendengarkan audio & menyusun notulen rapat dengan Gemini AI..."):
                try:
                    if audio_bytes_data:
                        result: MeetingMinutes = process_meeting_audio(
                            audio_source=audio_bytes_data,
                            mime_type=audio_mime,
                            language_hint=lang_option,
                            model_name=model_option
                        )
                    else:
                        result: MeetingMinutes = process_meeting_text_transcript(
                            transcript_text=text_input_data,
                            language_hint=lang_option,
                            model_name=model_option
                        )
                    st.session_state["meeting_result"] = result
                except Exception as e:
                    st.error(f"Gagal memproses meeting: {e}")

    if "meeting_result" in st.session_state:
        res: MeetingMinutes = st.session_state["meeting_result"]

        # Header Metadata Card
        attendees_badges = "".join([f'<span class="attendee-chip">👤 {a}</span>' for a in res.attendees]) if res.attendees else "<em>Tidak disebutkan</em>"
        st.markdown(f"""
        <div class="header-card">
            <h3 style="margin: 0 0 8px 0; color: #0d47a1;">{res.meeting_title}</h3>
            <p style="margin: 0 0 6px 0; color: #555; font-size: 0.9rem;">
                📅 <strong>Tanggal:</strong> {res.meeting_date or '-'} | ⏱️ <strong>Durasi:</strong> {res.duration_estimate or '-'} | 🎭 <strong>Suasana:</strong> {res.overall_sentiment_and_tone}
            </p>
            <div style="margin-top: 8px;"><strong>Peserta:</strong> {attendees_badges}</div>
        </div>
        """, unsafe_allow_html=True)

        # Tabs for Content
        tab_summary, tab_actions, tab_topics, tab_transcript, tab_export = st.tabs([
            "📝 Ringkasan & Keputusan",
            f"⚡ Action Items ({len(res.action_items)})",
            "🗣️ Topik Diskusi",
            "💬 Full Transcript",
            "📥 Export"
        ])

        with tab_summary:
            st.markdown("### Ringkasan Eksekutif:")
            st.info(res.executive_summary)

            st.markdown("### 🎯 Keputusan Kunci yang Disepakati:")
            if res.key_decisions:
                for d in res.key_decisions:
                    st.markdown(f"""<div class="decision-box">✅ <strong>{d}</strong></div>""", unsafe_allow_html=True)
            else:
                st.write("Tidak ada keputusan formal yang dicatat.")

        with tab_actions:
            st.markdown("### Daftar Tugas & Tindak Lanjut:")
            if res.action_items:
                df_actions = pd.DataFrame([{
                    "Tugas": it.task,
                    "PIC / Assignee": it.assignee,
                    "Prioritas": it.priority,
                    "Deadline": it.deadline or "-"
                } for it in res.action_items])
                st.dataframe(df_actions, use_container_width=True, hide_index=True)
            else:
                st.write("Tidak ada action items terdeteksi.")

        with tab_topics:
            st.markdown("### Rincian Pembahasan Topik:")
            for t in res.discussion_topics:
                with st.expander(f"🔹 {t.topic_name} (Pembicara: {', '.join(t.key_speakers)})", expanded=True):
                    st.write(t.summary)

        with tab_transcript:
            st.markdown("### Transkripsi Lengkap:")
            st.text_area("Full Transcript", value=res.full_transcript, height=300)

        with tab_export:
            st.markdown("### Download Notulen Resmi:")
            col_ex1, col_ex2 = st.columns(2)
            
            with col_ex1:
                md_doc = f"""# Notulen Rapat: {res.meeting_title}
- **Tanggal:** {res.meeting_date or '-'} | **Durasi:** {res.duration_estimate or '-'}
- **Peserta:** {', '.join(res.attendees)}
- **Suasana/Tone:** {res.overall_sentiment_and_tone}

## Ringkasan Eksekutif
{res.executive_summary}

## Keputusan Kunci
{chr(10).join(['- ' + d for d in res.key_decisions])}

## Action Items
| No | Tugas | PIC | Prioritas | Deadline |
|:---:|:---|:---|:---:|:---|
"""
                for idx, it in enumerate(res.action_items, 1):
                    md_doc += f"| {idx} | {it.task} | {it.assignee} | {it.priority} | {it.deadline or '-'} |\n"

                md_doc += f"\n## Transkrip Lengkap\n\n{res.full_transcript}\n"

                st.download_button(
                    "📄 Download Notulen (Markdown)",
                    data=md_doc,
                    file_name=f"notulen_{res.meeting_title.lower().replace(' ', '_')}.md",
                    mime="text/markdown",
                    use_container_width=True
                )

            with col_ex2:
                st.download_button(
                    "💾 Download Data (JSON)",
                    data=res.model_dump_json(indent=2),
                    file_name="meeting_minutes.json",
                    mime="application/json",
                    use_container_width=True
                )
    else:
        st.info("👈 Masukkan file audio atau teks di sebelah kiri, lalu klik **'Buat Notulen & Transkripsi'**.")
