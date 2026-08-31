"""
Day 04 - AI Flashcard & Quiz Generator (Streamlit Web App)
Antarmuka Web Interaktif untuk belajar dengan Flashcards & Kuis Pilihan Ganda otomatis.
"""

import os
import sys
import json
from pathlib import Path
import streamlit as st

# Pastikan modul internal terbaca
sys.path.append(str(Path(__file__).parent))
from generator import generate_study_deck, export_to_anki_csv, StudyDeck

st.set_page_config(
    page_title="AI Flashcard & Quiz Generator | Day 04",
    page_icon="📇",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom Styling
st.markdown("""
<style>
    .flashcard-box {
        background: linear-gradient(135deg, #1e3c72 0%, #2a5298 100%);
        color: white;
        padding: 40px;
        border-radius: 16px;
        min-height: 220px;
        display: flex;
        flex-direction: column;
        justify-content: center;
        align-items: center;
        text-align: center;
        box-shadow: 0 10px 20px rgba(0,0,0,0.15);
        margin-bottom: 20px;
    }
    .flashcard-back {
        background: linear-gradient(135deg, #11998e 0%, #38ef7d 100%);
        color: #0f382c;
    }
    .quiz-card {
        background-color: #f8f9fa;
        border: 1px solid #e9ecef;
        border-radius: 12px;
        padding: 20px;
        margin-bottom: 20px;
    }
    .tag-badge {
        background-color: rgba(255,255,255,0.25);
        padding: 4px 12px;
        border-radius: 20px;
        font-size: 0.8rem;
        margin-bottom: 10px;
    }
</style>
""", unsafe_allow_html=True)

# Preset Topics
SAMPLE_MATERIAL_ML = """
Arsitektur Transformer dan Mekanisme Perhatian (Attention Mechanism)

Transformer adalah arsitektur deep learning yang diperkenalkan dalam paper 'Attention Is All You Need' (Vaswani et al., 2017). Berbeda dengan RNN atau LSTM yang memproses data sekuensial secara bertahap (step-by-step), Transformer memproses seluruh sekuens input secara paralel, sehingga sangat efisien dalam pelatihan data skala besar.

Komponen Utama Transformer:
1. Self-Attention Mechanism: Menghitung bobot keterkaitan antar setiap kata dalam kalimat tanpa memandang posisinya. Menggunakan rumus Query (Q), Key (K), dan Value (V) dengan matriks Softmax((QK^T)/sqrt(d_k))V.
2. Multi-Head Attention: Menjalankan mekanisme self-attention secara paralel pada beberapa representasi sub-ruang yang berbeda.
3. Positional Encoding: Memberikan informasi urutan posisi kata ke dalam embedding karena Transformer tidak memiliki loop berulang bawaan seperti RNN.
4. Feed-Forward Neural Network & Layer Normalization: Lapisan fully connected dan normalisasi residual di setiap blok encoder/decoder.

Aplikasi Transformer:
Transformer menjadi fondasi dasar bagi model bahasa modern (LLM) seperti GPT-4, BERT, Gemini, LLaMA, serta model vision (Vision Transformer/ViT).
"""

# Sidebar
with st.sidebar:
    st.title("⚙️ Pengaturan Pembelajaran")
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

    num_cards = st.slider("Jumlah Flashcards", min_value=3, max_value=10, value=5)
    num_questions = st.slider("Jumlah Soal Kuis", min_value=3, max_value=10, value=5)
    difficulty_option = st.selectbox("Tingkat Kesulitan", ["Easy", "Medium", "Hard"], index=1)

    st.divider()
    st.markdown("### 📌 Tentang Proyek")
    st.markdown("""
    **Day 04 dari 30 Days of AI Challenge**
    - Structured JSON generation with Pydantic
    - Spaced Repetition Flashcards & Anki TSV export
    - Interactive Multiple-Choice Quiz Engine
    """)

# Main Content
st.title("📇 AI Flashcard & Interactive Quiz Generator")
st.markdown("Ubah catatan teks, artikel teknis, atau silabus menjadi kartu belajar interaktif dan kuis pilihan ganda secara instan.")

# Input Section
col_inp1, col_inp2 = st.columns([1, 1], gap="medium")

with col_inp1:
    st.subheader("📥 Materi Pembelajaran")
    
    if st.button("📄 Load Contoh Materi: Transformer & Deep Learning", use_container_width=True):
        st.session_state["study_text_input"] = SAMPLE_MATERIAL_ML

    study_text = st.text_area(
        "Tempel materi atau topik pembelajaran di sini:",
        value=st.session_state.get("study_text_input", SAMPLE_MATERIAL_ML),
        height=260,
        placeholder="Masukkan teks, rangkuman, atau artikel yang ingin dipelajari..."
    )

    generate_btn = st.button("🚀 Buat Flashcards & Kuis", type="primary", use_container_width=True)

with col_inp2:
    st.subheader("📋 Ringkasan Materi")
    if "deck_result" in st.session_state:
        deck: StudyDeck = st.session_state["deck_result"]
        st.success(f"**Topik:** {deck.topic_title}")
        st.info(f"**Target Level:** `{deck.target_audience}`\n\n{deck.summary}")
        
        m1, m2 = st.columns(2)
        m1.metric("Total Flashcards", f"{len(deck.flashcards)} Kartu")
        m2.metric("Total Soal Kuis", f"{len(deck.quiz)} Pertanyaan")
    else:
        st.info("👈 Masukkan materi di sebelah kiri lalu klik tombol **'Buat Flashcards & Kuis'**.")

if generate_btn:
    if not study_text.strip():
        st.warning("Silakan masukkan teks materi terlebih dahulu!")
    elif not os.getenv("GEMINI_API_KEY"):
        st.error("🔑 API Key belum diatur! Masukkan GEMINI_API_KEY di sidebar atau file .env")
    else:
        with st.spinner("🤖 Sedang menyusun Flashcards & Kuis Interaktif dengan Gemini AI..."):
            try:
                deck = generate_study_deck(
                    content=study_text,
                    num_cards=num_cards,
                    num_questions=num_questions,
                    difficulty=difficulty_option,
                    model_name=model_option
                )
                st.session_state["deck_result"] = deck
                st.session_state["card_index"] = 0
                st.session_state["is_flipped"] = False
                st.session_state["quiz_answers"] = {}
                st.session_state["quiz_submitted"] = False
                st.rerun()
            except Exception as e:
                st.error(f"Gagal memproses materi: {e}")

# Interactive Deck Viewer
if "deck_result" in st.session_state:
    deck: StudyDeck = st.session_state["deck_result"]
    st.divider()

    tab_flashcard, tab_quiz, tab_export, tab_json = st.tabs([
        f"📇 Flashcards ({len(deck.flashcards)})",
        f"🎮 Kuis Interaktif ({len(deck.quiz)})",
        "📥 Export (Anki / Markdown)",
        "💻 Raw JSON"
    ])

    # 1. Flashcard Tab
    with tab_flashcard:
        card_idx = st.session_state.get("card_index", 0)
        total_cards = len(deck.flashcards)
        current_card = deck.flashcards[card_idx]
        is_flipped = st.session_state.get("is_flipped", False)

        st.caption(f"Kartu #{card_idx + 1} dari {total_cards}")

        # Card Display
        if not is_flipped:
            st.markdown(f"""
            <div class="flashcard-box">
                <span class="tag-badge">🏷️ {current_card.category_tag}</span>
                <h3 style="color: white; margin: 10px 0;">{current_card.front}</h3>
                <small style="opacity: 0.8;">(Klik 'Balik Kartu' untuk melihat jawaban)</small>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown(f"""
            <div class="flashcard-box flashcard-back">
                <span class="tag-badge" style="background-color: rgba(0,0,0,0.15); color: #004d40;">💡 Jawaban / Penjelasan</span>
                <h3 style="color: #004d40; margin: 10px 0;">{current_card.back}</h3>
            </div>
            """, unsafe_allow_html=True)

        if current_card.hint:
            with st.expander("💡 Lihat Petunjuk (Hint)"):
                st.write(current_card.hint)

        col_fc1, col_fc2, col_fc3 = st.columns([1, 2, 1])
        with col_fc1:
            if st.button("⬅️ Sebelumnya", disabled=(card_idx == 0), use_container_width=True):
                st.session_state["card_index"] -= 1
                st.session_state["is_flipped"] = False
                st.rerun()
        with col_fc2:
            flip_label = "🔄 Balik ke Depan" if is_flipped else "🔄 Balik Kartu (Lihat Jawaban)"
            if st.button(flip_label, type="secondary", use_container_width=True):
                st.session_state["is_flipped"] = not is_flipped
                st.rerun()
        with col_fc3:
            if st.button("Berikutnya ➡️", disabled=(card_idx == total_cards - 1), use_container_width=True):
                st.session_state["card_index"] += 1
                st.session_state["is_flipped"] = False
                st.rerun()

    # 2. Quiz Tab
    with tab_quiz:
        st.markdown(f"### Kuis Pilihan Ganda: {deck.topic_title}")
        st.caption("Pilih satu jawaban yang paling tepat untuk masing-masing pertanyaan di bawah ini:")

        with st.form("quiz_form"):
            user_answers = {}
            for q in deck.quiz:
                st.markdown(f"""
                <div class="quiz-card">
                    <strong>Pertanyaan #{q.question_number}</strong> <span style="color: #888;">({q.difficulty})</span>
                    <p style="font-size: 1.1rem; margin-top: 5px;">{q.question}</p>
                </div>
                """, unsafe_allow_html=True)

                options_dict = {f"{opt.id}. {opt.text}": opt.id for opt in q.options}
                choice = st.radio(
                    f"Pilihan untuk #{q.question_number}:",
                    options=list(options_dict.keys()),
                    key=f"q_radio_{q.question_number}",
                    index=None
                )
                if choice:
                    user_answers[q.question_number] = options_dict[choice]

            submitted = st.form_submit_button("🏁 Kirim & Nilai Jawaban", type="primary", use_container_width=True)

            if submitted:
                st.session_state["quiz_submitted"] = True
                st.session_state["quiz_answers"] = user_answers

        # Evaluation results
        if st.session_state.get("quiz_submitted", False):
            saved_answers = st.session_state.get("quiz_answers", {})
            score = 0
            st.divider()
            st.subheader("📊 Hasil Penilaian Kuis")

            for q in deck.quiz:
                ans = saved_answers.get(q.question_number)
                is_correct = (ans == q.correct_option_id)
                if is_correct:
                    score += 1
                    st.success(f"✅ **Pertanyaan #{q.question_number}: BENAR!** (Jawaban: {q.correct_option_id})")
                else:
                    st.error(f"❌ **Pertanyaan #{q.question_number}: KURANG TEPAT!** Jawaban Anda: `{ans or 'Belum dijawab'}` | Jawaban Benar: `{q.correct_option_id}`")
                
                st.info(f"💡 **Penjelasan:** {q.explanation}")
                st.markdown("---")

            total_q = len(deck.quiz)
            final_pct = (score / total_q) * 100
            st.metric("Skor Akhir Anda", f"{score} / {total_q} ({final_pct:.0f}%)")

    # 3. Export Tab
    with tab_export:
        st.subheader("📥 Export Materi Belajar")
        col_ex1, col_ex2, col_ex3 = st.columns(3)

        with col_ex1:
            anki_data = export_to_anki_csv(deck)
            st.download_button(
                "📇 Download Anki Deck (.tsv)",
                data=anki_data,
                file_name=f"anki_deck_{deck.topic_title.lower().replace(' ', '_')}.tsv",
                mime="text/tab-separated-values",
                use_container_width=True
            )
            st.caption("Kompatibel untuk di-import langsung ke aplikasi **Anki**.")

        with col_ex2:
            st.download_button(
                "💾 Download JSON Data",
                data=deck.model_dump_json(indent=2),
                file_name="study_deck.json",
                mime="application/json",
                use_container_width=True
            )

        with col_ex3:
            # Markdown study sheet
            md_doc = f"# Ringkasan Materi: {deck.topic_title}\n\n{deck.summary}\n\n## Flashcards\n"
            for c in deck.flashcards:
                md_doc += f"- **Q:** {c.front}\n  - **A:** {c.back}\n\n"
            md_doc += "## Kuis Soal & Jawaban\n"
            for q in deck.quiz:
                md_doc += f"### #{q.question_number}. {q.question}\n"
                for o in q.options:
                    mark = "✅ " if o.id == q.correct_option_id else ""
                    md_doc += f"- {mark}{o.id}. {o.text}\n"
                md_doc += f"\n*Penjelasan: {q.explanation}*\n\n"

            st.download_button(
                "📝 Download Lembar Belajar (Markdown)",
                data=md_doc,
                file_name="study_guide.md",
                mime="text/markdown",
                use_container_width=True
            )

    # 4. Raw JSON Tab
    with tab_json:
        st.json(deck.model_dump())
