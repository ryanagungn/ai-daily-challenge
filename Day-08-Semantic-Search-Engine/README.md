# Day 08: Semantic Search Engine with Vector Embeddings 🔍

Aplikasi Mesin Pencari Semantik cerdas berbasis **Vector Embeddings** (`text-embedding-004`) dan kalkulasi **Cosine Similarity** matematis murni. Sistem ini memahami makna kontekstual dari kueri pencarian pengguna (bahkan saat kata kunci persis tidak muncul di dalam teks) dan menyediakan visualisasi interaktif **Ruang Vektor 2D (PCA)**.

Tersedia dalam 2 mode: **Interactive Web UI (Streamlit)** dan **Terminal CLI (Rich UI)**.

---

## ✨ Fitur Utama
- **🧠 Semantic Concept Matching:** Mencocokkan kueri dengan dokumen berdasarkan kedekatan arah vektor semantik 768 dimensi menggunakan *Cosine Similarity*.
- **⚖️ Side-by-Side Comparison:** Membandingkan hasil *Semantic AI Search* vs *Exact Keyword Search* secara langsung untuk melihat keunggulan pencarian berbasis AI.
- **🗺️ 2D Vector Space Visualizer:** Memetakan posisi vektor dokumen ke koordinat 2D menggunakan algoritma *Principal Component Analysis (PCA / SVD)* untuk melihat pengelompokan (*clustering*) topik.
- **⚡ Local Vector Caching:** Menyimpan vektor yang sudah di-generate ke file JSON lokal untuk menghemat kuota API dan mempercepat pencarian.
- **➕ Dynamic Document Ingestion:** Tambahkan artikel atau catatan baru kapan saja dan sistem akan langsung meng-embed serta memperbarui indeks vektor.

---

## 🚀 Cara Menjalankan

### 1. Masuk ke Direktori Day 08
```bash
cd Day-08-Semantic-Search-Engine
```

### 2. Jalankan Versi Web UI (Streamlit)
```bash
streamlit run app.py
```
> Buka browser pada `http://localhost:8501`. Coba ketik pertanyaan konseptual seperti *"Bagaimana cara mengamankan container cloud?"* dan bandingkan hasil pencarian semantik vs kata kunci biasa!

### 3. Jalankan Versi Terminal (CLI)
```bash
# Lakukan pencarian semantik:
python cli.py -q "cara mencegah kebocoran data di cloud"

# Bandingkan dengan pencarian kata kunci:
python cli.py -q "cara mencegah kebocoran data di cloud" --compare

# Lihat semua dokumen yang terindeks:
python cli.py --list-docs

# Tambah dokumen baru langsung dari terminal:
python cli.py --add-title "Optimasi Index SQLite" --add-category "Database" --add-content "Index B-Tree pada SQLite mempercepat pencarian WHERE."
```

---

## 🧠 Konsep & Tech Stack yang Dipelajari
- **Vector Embeddings Fundamentals:** Memahami representasi teks ke dalam ruang vektor berdimensi tinggi (*Dense Vectors*).
- **Cosine Similarity Math:** Menghitung jarak sudut kosinus antar vektor $\cos(\theta) = \frac{\mathbf{A} \cdot \mathbf{B}}{\|\mathbf{A}\| \|\mathbf{B}\|}$.
- **Dimensionality Reduction (PCA via SVD):** Memproyeksikan data 768 dimensi ke ruang 2D menggunakan aljabar linear NumPy murni tanpa library eksternal yang berat.
- **Foundations for RAG:** Konsep indexing dan similarity search ini adalah fondasi utama untuk membangun sistem *Retrieval-Augmented Generation (RAG)*.
