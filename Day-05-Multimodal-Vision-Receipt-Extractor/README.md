# Day 05: Multimodal Vision Receipt & Invoice Extractor 🧾

Aplikasi Computer Vision & Document AI cerdas berbasis LLM Multimodal (*Gemini 2.5 Flash Vision*) yang mengekstrak data terstruktur dari foto struk belanja fisik, faktur restoran, atau kuitansi pembayaran, lengkap dengan verifikasi integritas matematika keuangan dan ekspor CSV/JSON.

Tersedia dalam 2 mode: **Interactive Web UI (Streamlit)** dengan dukungan Webcam, dan **Terminal CLI (Rich UI)**.

---

## ✨ Fitur Utama
- **👁️ Multimodal OCR Understanding:** Membaca teks, tabel belanjaan, nomor invoice, dan total belanjaan langsung dari gambar beresolusi tinggi maupun foto kamera hp.
- **🛒 Line-Item Breakdown Extraction:** Mengekstrak setiap baris produk belanjaan beserta kuantitas, harga satuan, dan total harga.
- **💰 Financial Breakdown & Math Reconciliation:** Memisahkan Subtotal, Pajak Restoran/PPN, Service Charge, Diskon, dan Grand Total, sekaligus memvalidasi apakah perhitungan matematika pada struk akurat.
- **🏷️ Automated Expense Categorization:** Mengklasifikasikan transaksi secara otomatis (*Food & Beverage*, *Electronics*, *Office*, *Travel*, dll).
- **📸 Flexible Input:** Mendukung upload gambar (`PNG`, `JPG`, `WEBP`), capture langsung via Webcam/Kamera, atau sample generator sintetis.
- **📥 Accounting Export:** Download hasil ekstraksi ke format CSV (siap untuk Excel) atau JSON.

---

## 🚀 Cara Menjalankan

### 1. Masuk ke Direktori Day 05
```bash
cd Day-05-Multimodal-Vision-Receipt-Extractor
```

### 2. Jalankan Versi Web UI (Streamlit)
```bash
streamlit run app.py
```
> Buka browser pada `http://localhost:8501`. Pilih tab "Gunakan Sample Demo" atau upload foto struk belanja Anda sendiri.

### 3. Jalankan Versi Terminal (CLI)
```bash
# Ekstrak data dari sample struk bawaan:
python cli.py

# Ekstrak dari file gambar struk kustom:
python cli.py -i path/to/my_receipt.jpg --json-out hasil_struk.json --csv-out items.csv
```

---

## 🧠 Konsep & Tech Stack yang Dipelajari
- **Vision-Language Models (VLMs):** Mengirim gambar langsung sebagai part/content ke model Gemini API tanpa perlu pipeline OCR eksternal (seperti Tesseract) yang rumit.
- **Spatial Reasoning on Documents:** Kemampuan model multimodal dalam mengasosiasikan teks baris harga di kolom kanan dengan nama produk di kolom kiri.
- **Data Structuring with Pydantic:** Menjamin tipe data numerik (float) untuk keperluan akuntansi dan pembukuan otomatis.
