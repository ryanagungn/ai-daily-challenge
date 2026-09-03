# Day 07: Interactive Prompt Engineering Playground & Studio 🧪

Aplikasi Studio & Sandbox Prompt Engineering cerdas yang memungkinkan developer menguji parameter model (`temperature`, `top_p`, `max_tokens`), menguji template variabel dinamis `{{var}}`, melakukan perbandingan **A/B Testing** antar dua prompt sekaligus, mengoptimalkan prompt secara otomatis dengan AI, serta mengekspor konfigurasi prompt langsung ke kode Python SDK.

Tersedia dalam 2 mode: **Interactive Web UI (Streamlit)** dan **Terminal CLI (Rich UI)**.

---

## ✨ Fitur Utama
- **🎛️ Full Hyperparameter Sandbox:** Uji respons model pada berbagai variasi `Temperature` (0.0 - 2.0), `Top-P`, dan `Max Output Tokens` dengan latency measurement (ms).
- **🧩 Dynamic Variable Templating:** Gunakan format `{{variable_name}}` pada prompt template, sistem akan otomatis menyediakan input form variabel secara dinamis.
- **⚔️ A/B Prompt Comparator:** Uji dan bandingkan 2 prompt / persona yang berbeda pada input data yang sama secara berdampingan (*Side-by-Side*).
- **🚀 AI Prompt Optimizer:** Masukkan draft prompt biasa, AI Prompt Specialist akan merancang ulang prompt Anda dengan teknik *Role Definition*, *Context Delimiters*, dan *Structured Constraints*.
- **🐍 Python Code Generator:** Salin kode Python mandiri siap pakai (`google-genai` SDK) dari konfigurasi prompt yang sedang aktif.
- **📚 Curated Template Library:** Dilengkapi preset template siap pakai (Feynman Explainer, JSON Extractor, Code Refactor, dll).

---

## 🚀 Cara Menjalankan

### 1. Masuk ke Direktori Day 07
```bash
cd Day-07-Interactive-Prompt-Playground
```

### 2. Jalankan Versi Web UI (Streamlit)
```bash
streamlit run app.py
```
> Buka browser pada `http://localhost:8501`. Coba jalankan template siap pakai atau uji A/B prompt comparator!

### 3. Jalankan Versi Terminal (CLI)
```bash
# Lihat daftar preset:
python cli.py --list-presets

# Jalankan preset tertentu:
python cli.py --preset feynman_explainer

# Optimalkan draft prompt mentah:
python cli.py --optimize "Tuliskan email promosi diskon 20%"

# Generate kode Python dari prompt kustom:
python cli.py -p "Buatkan resep {{makanan}} untuk {{porsi}} orang" --export-code
```

---

## 🧠 Konsep & Tech Stack yang Dipelajari
- **Prompt Engineering Fundamentals:** Menguasai dampak `temperature` terhadap determinisme vs kreativitas model, serta pentingnya pemisahan *System Instruction* dan *User Prompt*.
- **A/B Testing & Evaluation:** Membandingkan kualitas respons model berdasarkan waktu eksekusi (latency) dan keteraturan output.
- **Dynamic Templating:** Regex extraction untuk parsing variabel dinamis pada string prompt.
