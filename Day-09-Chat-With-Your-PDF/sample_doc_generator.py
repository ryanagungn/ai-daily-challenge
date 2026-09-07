"""
Day 09 - Sample Document & PDF Generator
Menghasilkan dokumen PDF dan teks contoh (AI Engineering Playbook) untuk pengujian sistem RAG.
"""

from pathlib import Path
from pypdf import PdfReader

OUTPUT_DIR = Path(__file__).parent

SAMPLE_TEXT = """PEDOMAN ARSITEKTUR AI & RAG ENTERPRISE 2024
PT Inovasi Teknologi Cerdas Nusantara

BAB 1: VISI DAN STANDAR PENGEMBANGAN AI
Dokumen ini merupakan standar resmi implementasi kecerdasan buatan bagi seluruh tim engineering.
Tujuan utama adalah membangun sistem Retrieval-Augmented Generation (RAG) yang aman, deterministik, dan bebas halusinasi.
Seluruh model bahasa yang digunakan harus melewati evaluasi kepatuhan privasi data dan memiliki guardrail anti-prompt injection.

BAB 2: STANDAR RETRIEVAL & VECTOR DATABASE
1. Rekomendasi Vector Database:
   - Untuk lingkungan local development dan testing: gunakan ChromaDB atau SQLite Vector.
   - Untuk lingkungan staging dan production: gunakan Qdrant atau Pinecone Serverless dengan replikasi multi-region.
2. Kebijakan Chunking Teks:
   - Ukuran chunk standar (chunk size): 500 sampai 800 karakter.
   - Overlap antar chunk: 100 karakter untuk menjaga kesinambungan semantik kalimat.
3. Model Embedding:
   - Standar embedding yang disetujui adalah text-embedding-004 (768 dimensi) dengan metrik jarak Cosine Similarity.
   - Ambang batas minimum similarity (threshold) untuk context grounding adalah 0.45.

BAB 3: KEAMANAN DATA & PERLINDUNGAN PRIVASI (PII)
1. Dilarang keras mengirimkan data mentah nasabah (PII seperti NIK KTP, nomor kartu kredit, kata sandi, dan rekam medis) ke API LLM publik.
2. Masking Data Otomatis:
   - Seluruh data teks harus melewati pipeline Anonymizer sebelum proses chunking dan indexing vektor.
   - Log query pengguna disimpan maksimal selama 30 hari dalam format terenkripsi AES-256.

BAB 4: SLA PERFORMA & ANGGARAN BIAYA TOKEN
1. Service Level Agreement (SLA):
   - Latency maksimum end-to-end untuk respon RAG adalah 1.5 detik (1500 ms).
   - Waktu proses retrieval vektor harus di bawah 150 ms (P95).
2. Kuota dan Anggaran Biaya:
   - Anggaran maksimum per project cluster adalah $500 USD per bulan.
   - Wajib menerapkan semantic caching menggunakan Redis untuk kueri berulang guna memangkas biaya token hingga 40%.

BAB 5: TIM PENANGGUNG JAWAB & KONTAK ON-CALL
- Head of AI Engineering: Dr. Budi Santoso (budi.santoso@inovasitech.id)
- Lead Platform & Security: Siti Rahmawati (siti.rahma@inovasitech.id)
- On-call Emergency Slack Channel: #ai-incident-response (SLA respon 15 menit untuk insiden P1).
"""

def generate_pdf(filename: Path, text: str):
    # Buat PDF sederhana multi-baris yang valid
    lines = [line.strip() for line in text.split("\n") if line.strip()]
    
    stream_content = "BT\n/F1 10 Tf\n14 TL\n50 740 Td\n"
    for line in lines:
        clean_line = line.replace("\\\\", "\\\\\\\\").replace("(", "\\(").replace(")", "\\)")
        # Handle simple ascii
        safe_line = "".join([c if ord(c) < 128 else "" for c in clean_line])
        stream_content += f"({safe_line}) '\n"
    stream_content += "ET\n"
    
    stream_bytes = stream_content.encode("latin1")
    stream_len = len(stream_bytes)
    
    pdf_bytes = bytearray()
    pdf_bytes.extend(b"%PDF-1.4\n")
    
    offsets = []
    
    # Obj 1: Catalog
    offsets.append(len(pdf_bytes))
    pdf_bytes.extend(b"1 0 obj << /Type /Catalog /Pages 2 0 R >> endobj\n")
    
    # Obj 2: Pages
    offsets.append(len(pdf_bytes))
    pdf_bytes.extend(b"2 0 obj << /Type /Pages /Kids [3 0 R] /Count 1 >> endobj\n")
    
    # Obj 3: Page
    offsets.append(len(pdf_bytes))
    pdf_bytes.extend(b"3 0 obj << /Type /Page /Parent 2 0 R /MediaBox [0 0 612 792] /Resources << /Font << /F1 4 0 R >> >> /Contents 5 0 R >> endobj\n")
    
    # Obj 4: Font
    offsets.append(len(pdf_bytes))
    pdf_bytes.extend(b"4 0 obj << /Type /Font /Subtype /Type1 /BaseFont /Helvetica >> endobj\n")
    
    # Obj 5: Stream
    offsets.append(len(pdf_bytes))
    pdf_bytes.extend(f"5 0 obj << /Length {stream_len} >> stream\n".encode("latin1"))
    pdf_bytes.extend(stream_bytes)
    pdf_bytes.extend(b"\nendstream\nendobj\n")
    
    # Xref
    xref_offset = len(pdf_bytes)
    pdf_bytes.extend(b"xref\n0 6\n0000000000 65535 f \n")
    for off in offsets:
        pdf_bytes.extend(f"{off:010d} 00000 n \n".encode("latin1"))
        
    pdf_bytes.extend(b"trailer << /Size 6 /Root 1 0 R >>\nstartxref\n")
    pdf_bytes.extend(f"{xref_offset}\n%%EOF".encode("latin1"))
    
    filename.write_bytes(pdf_bytes)
    print(f"Sample PDF generated at: {filename}")

def main():
    # 1. Simpan Text
    txt_path = OUTPUT_DIR / "sample_ai_playbook.txt"
    txt_path.write_text(SAMPLE_TEXT.strip(), encoding="utf-8")
    print(f"Sample text generated at: {txt_path}")

    # 2. Simpan PDF
    pdf_path = OUTPUT_DIR / "sample_ai_playbook.pdf"
    generate_pdf(pdf_path, SAMPLE_TEXT.strip())

if __name__ == "__main__":
    main()
