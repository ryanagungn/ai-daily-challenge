# Day 06: AI Audio Meeting Transcriber & Minutes Summarizer 🎙️

Aplikasi Speech-to-Text & Document Intelligence cerdas berbasis LLM Multimodal (*Gemini 2.5 Flash Audio*) yang mendengarkan file rekaman audio rapat atau podcast, mentranskripsikan percakapan kata per kata (*Speaker Diarization*), mengekstrak ringkasan eksekutif, keputusan kunci, dan tabel *Action Items* terstruktur dengan penanggung jawab (PIC) serta deadline.

Tersedia dalam 2 mode: **Interactive Web UI (Streamlit)** dengan pemutar audio dan **Terminal CLI (Rich UI)**.

---

## ✨ Fitur Utama
- **🎧 Native Multimodal Audio Processing:** Mengirim file audio langsung (`.mp3`, `.wav`, `.m4a`, `.ogg`, `.flac`) tanpa perlu model whisper eksternal yang berat.
- **👥 Speaker Diarization & Transcription:** Mengenali pergantian pembicara dan mencatat transkripsi dialog dengan runut.
- **⚡ Automated Action Items Checklist:** Mengidentifikasi tugas-tugas konkret, menentukan PIC (assignee), tingkat urgensi/prioritas (*High*, *Medium*, *Low*), dan batas waktu.
- **🎯 Key Decisions Extractor:** Menyaring poin kesepakatan final rapat agar tidak hilang dalam diskusi panjang.
- **📊 Discussion Topics Breakdown:** Membagi topik bahasan menjadi sub-bab yang mudah dibaca.
- **📥 Professional Export:** Download Notulen Resmi dalam format Markdown (siap dikirim via email/Notion) atau JSON.

---

## 🚀 Cara Menjalankan

### 1. Masuk ke Direktori Day 06
```bash
cd Day-06-AI-Audio-Meeting-Transcriber
```

### 2. Jalankan Versi Web UI (Streamlit)
```bash
streamlit run app.py
```
> Buka browser pada `http://localhost:8501`. Anda bisa mengupload rekaman audio (.mp3/.wav/.m4a) atau langsung mencoba demo sample Sprint Planning internal!

### 3. Jalankan Versi Terminal (CLI)
```bash
# Transkrip dari file audio langsung:
python cli.py -a path/to/recording.mp3

# Buat notulen dari file teks/catatan rapat:
python cli.py -t sample_meeting_transcript.txt --md-out notulen_resmi.md

# Jalankan sample meeting bawaan:
python cli.py
```

---

## 🧠 Konsep & Tech Stack yang Dipelajari
- **Audio Multimodality:** Mengirim data audio biner (`types.Part.from_bytes`) langsung ke Gemini API untuk inferensi ucapan bahasa manusia.
- **Conversational Intelligence:** Mengekstrak intisari pertemuan dari percakapan santai menjadi notulen formal tingkat eksekutif.
- **Structured Schema (Pydantic):** Mengorganisasi tugas dan keputusan ke dalam skema data terstruktur untuk integrasi ke Jira / Trello / Asana.
