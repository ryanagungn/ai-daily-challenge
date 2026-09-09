# Day 11: Hybrid Search with BM25, Dense Vectors & Re-ranking 🔀

Aplikasi Mesin Pencari Tingkat Lanjut (*Advanced Search Engine*) yang mengombinasikan **Sparse Keyword Retrieval (BM25)** dan **Dense Semantic Retrieval (text-embedding-004)** menggunakan algoritma fusi standar industri **Reciprocal Rank Fusion (RRF)**, serta dilengkapi tahap **Cross-Encoder Re-ranking** bertenaga **Gemini 2.5 Flash**.

Tersedia dalam 2 mode: **Interactive Web UI (Streamlit)** dengan visualisasi perbandingan 3-arah, dan **Terminal CLI (Rich UI)**.

---

## ✨ Fitur Utama
- **⚡ Okapi BM25 Lexical Search (Pure Python):** Pencarian kata kunci presisi tinggi untuk menangkap ID unik, kode error sistem (misal `ERR_REDIS_CONN_TIMEOUT`), dan nomor CVE kerentanan.
- **🧠 Dense Vector Semantic Search:** Menangkap parafrase makna konseptual dan sinonim menggunakan model `text-embedding-004` dan *Cosine Similarity*.
- **🔀 Reciprocal Rank Fusion (RRF):** Algoritma penggabungan peringkat tanpa memerlukan normalisasi skor absolut yang rumit:
  $$\text{RRF}(d) = w_{\text{bm25}} \cdot \frac{1}{k + r_{\text{bm25}}(d)} + w_{\text{dense}} \cdot \frac{1}{k + r_{\text{dense}}(d)}$$
- **⚖️ Dynamic Weight Tuning:** Geser rasio bobot secara dinamis antara fokus leksikal (BM25) dan fokus semantik (Dense Vector).
- **🎯 Cross-Encoder LLM Re-ranker:** Model Gemini membaca pasangan kueri dan isi dokumen untuk menghasilkan skor relevansi (0-100) dan alasan argumentatif mengapa dokumen tersebut menjawab kueri.

---

## 🚀 Cara Menjalankan

### 1. Masuk ke Direktori Day 11
```bash
cd Day-11-Hybrid-Search-Reranking
```

### 2. Jalankan Versi Web UI (Streamlit)
```bash
streamlit run app.py
```
> Buka browser pada `http://localhost:8501`. Klik tombol preset contoh kueri untuk mengamati bagaimana BM25 unggul pada error code eksak, sementara Vector unggul pada makna konseptual, dan Hybrid RRF memberikan hasil paling seimbang!

### 3. Jalankan Versi Terminal (CLI)
```bash
# Pencarian Hybrid RRF:
python cli.py -q "ERR_REDIS_CONN_TIMEOUT"

# Pencarian Hybrid dengan Cross-Encoder Re-ranking:
python cli.py -q "mencegah pencurian token sesi javascript" --rerank

# Sesuaikan bobot (misal 80% BM25, 20% Vector):
python cli.py -q "CVE-2024-38856" --bm25-weight 0.8 --dense-weight 0.2
```

---

## 🧠 Konsep & Tech Stack yang Dipelajari
- **BM25 Algorithm Math:** Memahami Term Frequency (TF), Inverse Document Frequency (IDF), dan Document Length Normalization ($k_1$ dan $b$).
- **Sparse + Dense Hybrid Architecture:** Mengapa sistem pencarian modern kelas produksi (seperti di Elasticsearch, Pinecone, Cohere) selalu menggunakan pendekatan hybrid untuk mencegah kegagalan *vocabulary mismatch*.
- **Cross-Encoder vs Bi-Encoder:** Bi-Encoder (Dense Embeddings) memproses kueri dan dokumen secara terpisah untuk pencarian cepat, sedangkan Cross-Encoder memproses keduanya bersamaan untuk akurasi re-ranking tertinggi.
