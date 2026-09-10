# Day 12: Live Web-Search Augmented AI (Mini Perplexity Clone) 🌐

Aplikasi Mesin Pencari & Sintesis AI cerdas bergaya **Perplexity AI** yang merayapi web secara real-time via DuckDuckGo, mengekstrak rujukan multi-sumber (*titles, snippets, clean URLs, domain*), dan mensintesis jawaban faktual mendalam lengkap dengan **sitasi bernomor (*footnote citations*) `[1]`, `[2]`** dan **rekomendasi pertanyaan terkait (*related questions*)**.

Tersedia dalam 2 mode: **Interactive Web UI (Streamlit - Perplexity Style)** dan **Terminal CLI (Rich UI)**.

---

## ✨ Fitur Utama
- **🌐 Real-Time Web Scraping & Search:** Mengambil hasil pencarian web terbaru via DuckDuckGo tanpa memerlukan API key mesin pencari berbayar.
- **📑 Numbered Footnote Citations:** Setiap klausa atau fakta penting dalam jawaban menyertakan rujukan indeks `[1]`, `[2]` yang terhubung langsung ke kartu sumber web terkait.
- **⚖️ Multi-Source Conflict Resolution:** Menyaring dan merekonsiliasi fakta dari berbagai situs untuk meminimalkan halusinasi dan bias.
- **💡 Automated Related Search Questions:** Menyarankan 3 pertanyaan lanjutan yang relevan dan dapat diklik langsung untuk penelusuran berantai.
- **🎨 Perplexity-Inspired Aesthetic:** Kartu pratinjau sumber di bagian atas, jawaban terstruktur dengan sub-heading & bullet points, serta tombol ekspor Markdown / JSON.

---

## 🚀 Cara Menjalankan

### 1. Masuk ke Direktori Day 12
```bash
cd Day-12-Web-Search-Augmented-AI
```

### 2. Jalankan Versi Web UI (Streamlit)
```bash
streamlit run app.py
```
> Buka browser pada `http://localhost:8501`. Coba klik tombol topik terkini seperti *"Apa itu Model Context Protocol (MCP) dari Anthropic?"* atau tanyakan berita teknologi hari ini!

### 3. Jalankan Versi Terminal (CLI)
```bash
# Tanya langsung dari terminal:
python cli.py -q "Perkembangan arsitektur DeepSeek-V3 dan MoE"

# Ambil hingga 7 sumber web:
python cli.py -q "Berita AI terbaru minggu ini" -n 7

# Mode interaktif:
python cli.py
```

---

## 🧠 Konsep & Tech Stack yang Dipelajari
- **Search-Augmented Generation (SAG):** Mengatasi batasan *knowledge cutoff* LLM dengan menginjeksi informasi web terkini langsung ke dalam context window.
- **URL & Snippet Cleansing:** Mengekstrak link tujuan asli dari redirect engine DuckDuckGo dan membersihkan tag HTML mentah.
- **Perplexity-style Grounding:** Mendesain *system instruction* yang menuntut sitasi kurung siku ketat untuk akuntabilitas jawaban berbasis data publik.
