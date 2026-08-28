# Day 02: AI Code Reviewer & Refactor Assistant 🛡️

Aplikasi audit dan refactoring kode cerdas berbasis LLM yang mendeteksi kerentanan keamanan (SQL Injection, XSS, Hardcoded secrets), bug logika, inefisiensi performa (O-Notation), serta secara otomatis menghasilkan kode refaktor bersih (*Clean Code*) yang siap pakai.

Tersedia dalam 2 mode: **Interactive Web UI (Streamlit)** dan **Terminal CLI (Rich UI)**.

---

## ✨ Fitur Utama
- **🔒 Security Vulnerability Detection:** Mendeteksi celah keamanan berbahaya (SQLi, insecure `eval()`, hardcoded secrets, unsafe deserialization).
- **🐛 Bug & Resource Leak Spotting:** Mengidentifikasi mutable default arguments, unclosed DB/file handlers, unhandled exceptions.
- **⚡ Algorithmic Performance Audit:** Menganalisis kompleksitas waktu/ruang (O-Notation) dan menyarankan struktur data optimal.
- **✨ Full Clean Code Refactoring:** Memberikan kode pengganti yang utuh, rapi, bertipe data (type hints), dan modular.
- **📊 Code Quality Score (1-10):** Skor kualitas objektif untuk memudahkan benchmarking kualitas kode.
- **🎯 Multi-Focus Filtering:** Pilihan fokus review (*Security*, *Performance*, *Clean Code*, atau *General*).

---

## 🚀 Cara Menjalankan

### 1. Masuk ke Direktori Day 02
```bash
cd Day-02-AI-Code-Reviewer
```

### 2. Jalankan Versi Web UI (Streamlit)
```bash
streamlit run app.py
```
> Buka browser pada `http://localhost:8501`. Terdapat tombol instan untuk memuat contoh kode Python & JavaScript yang memiliki bug.

### 3. Jalankan Versi CLI (Terminal)
```bash
# Review file Python contoh:
python cli.py -f sample_buggy_python.py

# Review file JavaScript contoh dengan fokus keamanan:
python cli.py -f sample_buggy_js.js --focus "Security Focus"

# Simpan langsung hasil refactor ke file baru:
python cli.py -f sample_buggy_python.py -o refactored_python.py
```

---

## 🧠 Konsep & Tech Stack yang Dipelajari
- **Static Analysis with LLM Reasoning:** Mengombinasikan pemahaman semantik LLM untuk menemukan bug kompleks yang sering luput dari linter tradisional.
- **Structured Schema (Pydantic):** Mengurai isu kode ke dalam kategori dan tingkat keparahan terstruktur (`Critical`, `High`, `Medium`, `Low`).
- **Code Refactoring & Optimization:** Mengubah algoritma $O(N^2)$ menjadi $O(N)$ secara otomatis.
