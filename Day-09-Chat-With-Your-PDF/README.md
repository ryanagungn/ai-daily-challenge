# Day 09: Chat with Your PDF (Simple RAG) 📄

Aplikasi Tanya Jawab Dokumen cerdas berbasis **Retrieval-Augmented Generation (RAG)** menggunakan model embedding `text-embedding-004` dan `Gemini 2.5 Flash`. Sistem ini mengekstrak teks dari PDF (`pypdf`), melakukan chunking dengan *sliding window overlap*, mengindeks vektor, menyaring konteks paling relevan melalui *Cosine Similarity*, dan menyusun jawaban akurat lengkap dengan **sitasi sumber** dan **guardrail anti-halusinasi**.

Tersedia dalam 2 mode: **Interactive Web UI (Streamlit Chatbot)** dan **Terminal CLI (Rich UI)**.

---

## ✨ Fitur Utama
- **📑 Full RAG Architecture:** Pipeline terintegrasi: Ekstraksi PDF $\rightarrow$ Text Chunking $\rightarrow$ Dense Vector Indexing $\rightarrow$ Semantic Retrieval $\rightarrow$ Grounded Answer Generation.
- **🛡️ Anti-Hallucination Guardrail:** Model secara ketat diinstruksikan hanya menjawab berdasarkan fakta yang terdapat pada kutipan dokumen. Jika data tidak ada, model dengan jujur menyatakan tidak ditemukan.
- **🔍 Grounding Citations:** Setiap respon dilengkapi daftar rujukan kutipan (*chunk id*, nomor halaman dokumen, skor relevansi, dan cuplikan teks asli).
- **💬 Conversational UI:** Antarmuka chat interaktif modern dengan riwayat percakapan menggunakan komponen `st.chat_message` dan `st.chat_input`.
- **✂️ Chunk Inspector:** Panel visual untuk memeriksa hasil segmentasi teks per halaman sebelum diindeks.

---

## 🚀 Cara Menjalankan

### 1. Masuk ke Direktori Day 09
```bash
cd Day-09-Chat-With-Your-PDF
```

### 2. Jalankan Versi Web UI (Streamlit)
```bash
streamlit run app.py
```
> Buka browser pada `http://localhost:8501`. Klik tombol **"Gunakan Sample Dokumen (AI Playbook)"** di sidebar atau unggah dokumen PDF Anda sendiri!

### 3. Jalankan Versi Terminal (CLI)
```bash
# Tanya jawab interaktif dengan sample PDF bawaan:
python cli.py

# Ajukan satu pertanyaan langsung ke file PDF tertentu:
python cli.py -f sample_ai_playbook.pdf -q "Berapa batas SLA latency respon RAG?"

# Tanya dokumen PDF milik Anda sendiri:
python cli.py -f path/to/document.pdf
```

---

## 🧠 Konsep & Tech Stack yang Dipelajari
- **PDF Extraction (pypdf):** Mengurai teks halaman demi halaman dari format binary PDF.
- **Chunking with Overlap:** Mengatur `chunk_size` (misal 500 karakter) dan `chunk_overlap` (misal 100 karakter) agar batas kalimat tidak terpotong kasar.
- **In-Context Grounding:** Menginjeksi cuplikan dokumen terbaik ke dalam `system_instruction` untuk membatasi ruang pengetahuan LLM hanya pada dokumen tersebut.
