# Day 10: Technical Documentation & Codebase Q&A Search Engine 🛠️

Aplikasi Asisten Pencarian Dokumentasi Teknis & Arsitektur Sistem berbasis **Header-Based Semantic Chunking** dan **Dense Vector Embeddings** (`text-embedding-004`). Sistem ini memecah file Markdown (`.md`) berdasarkan hierarki heading (`#`, `##`, `###`) sehingga konteks sub-bab, blok kode, dan tabel tidak terpotong acak, lalu menyajikan jawaban teknis mendalam lengkap dengan blok kode sintaks dan referensi bab yang dirujuk.

Tersedia dalam 2 mode: **Interactive Web UI (Streamlit)** dan **Terminal CLI (Rich UI)**.

---

## ✨ Fitur Utama
- **📑 Header-Based Semantic Chunking:** Mempertahankan struktur logis dokumen Markdown (breadcrumb: `# Bab > ## Sub-bab`) sehingga konteks teknis tetap utuh dan tidak terpotong kasar seperti pada character-based splitting biasa.
- **💻 Code Block Extraction & Language Detection:** Mengekstrak dan mengenali bahasa pemrograman dari blok kode fenced (```python, ```sql, ```bash, ```dockerfile, dll).
- **🔍 Dense Vector Semantic Search:** Mengindeks vektor 768 dimensi dan mencocokkan kueri developer dengan konsep teknis yang relevan menggunakan *Cosine Similarity*.
- **🛠️ Developer-Centric Technical Answers:** Menjawab pertanyaan seputar arsitektur sistem, skema database, autentikasi JWT, alur deployment, dan spesifikasi API langsung dengan blok kode siap pakai.
- **💡 Suggested Follow-Up Questions:** Menyarankan 2-3 pertanyaan teknis lanjutan yang relevan untuk memperdalam pemahaman developer.
- **📖 Integrated Markdown Browser:** Membaca dokumen Markdown asli secara langsung dalam antarmuka web.

---

## 🚀 Cara Menjalankan

### 1. Masuk ke Direktori Day 10
```bash
cd Day-10-Technical-Docs-QA-Search
```

### 2. Jalankan Versi Web UI (Streamlit)
```bash
streamlit run app.py
```
> Buka browser pada `http://localhost:8501`. Klik tombol preset contoh pertanyaan teknis atau ajukan pertanyaan spesifik seputar arsitektur microservices dan Kubernetes deployment!

### 3. Jalankan Versi Terminal (CLI)
```bash
# Tanya langsung dari terminal:
python cli.py -q "Bagaimana mekanisme rotasi token JWT?"

# Tampilkan semua hierarki bab yang terindeks:
python cli.py --list-sections

# Mode tanya jawab interaktif:
python cli.py

# Arahkan ke folder dokumentasi kustom Anda:
python cli.py -d path/to/my_markdown_docs
```

---

## 🧠 Konsep & Tech Stack yang Dipelajari
- **Semantic Chunking for Tech Docs:** Memanfaatkan hierarki heading Markdown sebagai batas alami pemotongan teks (*Natural Context Boundaries*).
- **Code-Aware Retrieval:** Menjaga keutuhan blok kode saat indexing agar model LLM menerima sintaks yang valid dan dapat dieksekusi.
- **Developer Experience (DX) in RAG:** Menyediakan sitasi breadcrumb yang jelas sehingga engineer dapat langsung melompat ke bab dokumen sumber terkait.
