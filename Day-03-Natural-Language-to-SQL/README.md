# Day 03: Natural Language to SQL Analytics Engine 🗄️

Aplikasi Text-to-SQL cerdas berbasis LLM yang menerjemahkan pertanyaan bahasa manusia (Indonesia & Inggris) menjadi query SQL SQLite, memvalidasi keamanan operasi (*Read-Only Guardrail*), mengeksekusi langsung ke database, serta secara otomatis menyajikan grafik visualisasi dan insight bisnis.

Tersedia dalam 2 mode: **Interactive Web UI (Streamlit)** dan **Terminal REPL/CLI (Rich UI)**.

---

## ✨ Fitur Utama
- **🗣️ Natural Language to SQL:** Menerjemahkan bahasa manusia menjadi query SQL kompleks dengan JOIN, GROUP BY, agregasi SUM/AVG/COUNT, dan subquery.
- **🛡️ SQL Safety & Anti-Destructive Guardrail:** Memfilter dan menolak keyword berbahaya (`DROP`, `DELETE`, `UPDATE`, `INSERT`, `TRUNCATE`).
- **📊 Auto Data Visualization:** Menyarankan dan merender grafik yang paling cocok (Bar Chart, Line Chart, atau Data Table) secara dinamis.
- **💡 Business Insights Extractor:** Menjelaskan makna bisnis dan rekomendasi di balik data yang dihasilkan.
- **⚡ SQLite In-Memory / Local Seed Data:** Dilengkapi data sintetis e-commerce realistis (Customers, Products, Categories, Orders, Order Items).
- **📝 Live SQL Editor:** Memungkinkan pengguna mengedit atau menyesuaikan query SQL yang digenerate sebelum eksekusi ulang.

---

## 🚀 Cara Menjalankan

### 1. Masuk ke Direktori Day 03
```bash
cd Day-03-Natural-Language-to-SQL
```

### 2. Jalankan Versi Web UI (Streamlit)
```bash
streamlit run app.py
```
> Buka browser pada `http://localhost:8501`. Klik tombol preset contoh pertanyaan atau ketik pertanyaan analitik Anda sendiri!

### 3. Jalankan Versi Terminal (CLI / REPL)
```bash
# Mode Interaktif (Tanya langsung di terminal):
python cli.py

# Mode Satu Pertanyaan:
python cli.py -q "Siapa 5 pelanggan dengan total belanja tertinggi?"

# Lihat Skema Database:
python cli.py --schema
```

---

## 🧠 Konsep & Tech Stack yang Dipelajari
- **In-Context Schema Injection:** Menginjeksi skema DDL relasional ke context window LLM agar model menghasilkan query yang akurat tanpa halusinasi nama tabel/kolom.
- **Guardrails & Security Filtering:** Memisahkan peran AI sebagai perancang query dan lapisan validator deterministic untuk mencegah SQL injection atau operasi destruktif.
- **Structured Schema (Pydantic):** Mengurai rekomendasi sumbu X/Y visualisasi dan metadata insight bisnis.
