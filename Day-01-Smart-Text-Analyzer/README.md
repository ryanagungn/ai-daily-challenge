# Day 01: Smart AI Text & Sentiment Analyzer 🤖

Aplikasi analisis teks cerdas berbasis LLM yang mengekstraksi ringkasan intisari, menganalisis sentimen mendalam beserta alasan & skor kepercayaan, mendeteksi topik/entitas utama, serta mengekstrak poin tindakan (action items) dari teks panjang maupun ulasan pelanggan.

Tersedia dalam 2 mode: **Interactive Web UI (Streamlit)** dan **Terminal CLI (Rich UI)**.

---

## ✨ Fitur Utama
- **📝 Ekstraksi Ringkasan Otomatis:** Menyaring inti pesan secara padat dan akurat.
- **📊 Analisis Sentimen Objektif:** Mengkategorikan teks (`POSITIVE`, `NEGATIVE`, `NEUTRAL`) dilengkapi skor 0.0 - 1.0 serta penjelasan argumentatif.
- **🏷️ Deteksi Topik Kunci:** Mengekstrak kata kunci utama dan entitas penting.
- **⚡ Action Items Extractor:** Mengidentifikasi saran, keluhan mendesak, atau langkah lanjutan dari teks.
- **💾 Export Format:** Download hasil analisis dalam format `JSON` atau `Markdown`.
- **🛡️ Output Terstruktur:** Menggunakan skema Pydantic (`Structured Outputs`) untuk jaminan validitas data JSON.

---

## 🚀 Cara Menjalankan

### 1. Install Dependencies
Pastikan dependencies sudah terpasang:
```bash
pip install -r ../requirements.txt
```

### 2. Set API Key
Buat file `.env` di root repository atau atur environment variable:
```bash
export GEMINI_API_KEY="your_api_key_here"
# Windows PowerShell:
$env:GEMINI_API_KEY="your_api_key_here"
```

### 3. Jalankan Versi Web UI (Streamlit)
```bash
streamlit run app.py
```
Akses di browser pada: `http://localhost:8501`

### 4. Jalankan Versi CLI
```bash
# Menggunakan file contoh bahasa Indonesia:
python cli.py -f sample_id.txt

# Menggunakan file contoh bahasa Inggris:
python cli.py -f sample_en.txt

# Menggunakan input langsung:
python cli.py -t "Aplikasi ini sangat bagus tapi sering crash saat checkout."
```

---

## 🧠 Konsep & Tech Stack yang Dipelajari
- **LLM Structured Output:** Menggunakan `Pydantic` dan `response_schema` untuk parsing terstruktur tanpa risiko format parsing error.
- **Streamlit:** Membangun antarmuka web interaktif Python dalam hitungan menit.
- **Rich CLI:** Membuat antarmuka konsol terminal dengan tabel, panel warna, dan markdown rendering.
- **Multi-language Sentiment Analysis:** Analisis sentimen lintas bahasa (Indonesia, Inggris, dll).
