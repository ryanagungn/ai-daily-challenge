# Day 04: AI Flashcard & Interactive Quiz Generator 📇

Aplikasi EdTech cerdas berbasis LLM yang mengubah catatan kuliah, artikel teknologi, atau dokumentasi menjadi **Kartu Belajar (*Flashcards*)** dan **Kuis Pilihan Ganda Interaktif** dengan output terstruktur (*Structured Output via Pydantic*) serta kemampuan ekspor ke **Anki**.

Tersedia dalam 2 mode: **Interactive Web UI (Streamlit)** dan **Terminal Interactive Game (Rich UI)**.

---

## ✨ Fitur Utama
- **📇 Automated Flashcard Deck Creation:** Mengekstrak konsep kunci, rumus, dan definisi penting lengkap dengan *hint* dan label kategori.
- **🎮 Interactive Quiz Engine:** Menghasilkan 4 pilihan ganda (A, B, C, D) dengan 1 jawaban benar dan 3 pengecoh (*distractor*) yang meyakinkan, serta penilaian skor otomatis.
- **💡 Educational Explanations:** Memberikan penjelasan komprehensif mengapa suatu pilihan benar dan mengapa opsi lainnya keliru.
- **🔄 Anki TSV/CSV Export:** Hasil flashcards dapat diekspor langsung ke format yang siap di-import ke software **Anki** untuk metode *Spaced Repetition*.
- **📝 Multi-Format Study Sheet:** Download lembar ringkasan belajar dalam format Markdown atau JSON.
- **🎯 Dynamic Difficulty Tuning:** Mengatur tingkat kesulitan (*Easy*, *Medium*, *Hard*) dan jumlah kartu/soal secara dinamis.

---

## 🚀 Cara Menjalankan

### 1. Masuk ke Direktori Day 04
```bash
cd Day-04-AI-Flashcard-Quiz-Generator
```

### 2. Jalankan Versi Web UI (Streamlit)
```bash
streamlit run app.py
```
> Buka browser pada `http://localhost:8501`. Klik tombol **"Load Contoh Materi"** untuk mencoba demo pembelajaran arsitektur Transformer dan LLM!

### 3. Jalankan Versi Terminal (CLI / Game Interaktif)
```bash
# Mainkan kuis & flashcard dari file materi:
python cli.py -f sample_notes.txt

# Buat kuis langsung berdasarkan topik teks:
python cli.py -t "Dasar Containerization Docker & Kubernetes" -d Hard

# Export flashcards ke format Anki:
python cli.py -f sample_notes.txt --anki-out my_anki_deck.tsv
```

---

## 🧠 Konsep & Tech Stack yang Dipelajari
- **Complex Nested Pydantic Schemas:** Mengontrol LLM agar menghasilkan data bersarang yang ketat (`StudyDeck` -> `List[Flashcard]`, `List[QuizQuestion]` -> `List[QuizOption]`).
- **Pedagogical Distractor Design:** Merancang prompt rekayasa instruksi agar pilihan pengecoh kuis memiliki nilai edukatif tinggi dan tidak terlalu mudah ditebak.
- **Interoperability (Anki Integration):** Menghubungkan output AI generatif dengan ekosistem perangkat lunak pembelajaran *spaced repetition* pihak ketiga.
