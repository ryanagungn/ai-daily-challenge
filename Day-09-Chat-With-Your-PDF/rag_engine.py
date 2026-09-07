"""
Day 09 - Chat with Your PDF (RAG Engine Core Module)
Mengimplementasikan pipeline Retrieval-Augmented Generation (RAG) end-to-end:
PDF parsing (pypdf), text chunking dengan overlap, vector retrieval (text-embedding-004),
context grounding dengan mitigasi halusinasi, dan ekstraksi sitasi sumber.
"""

import os
import io
import json
from pathlib import Path
from typing import List, Dict, Any, Optional, Tuple, Union
import numpy as np
from pydantic import BaseModel, Field
from pypdf import PdfReader
from dotenv import load_dotenv

load_dotenv()

class DocumentChunk(BaseModel):
    chunk_id: int
    page_number: int
    content: str
    char_count: int

class Citation(BaseModel):
    chunk_id: int
    page_number: int
    similarity_score: float
    snippet: str

class RAGAnswer(BaseModel):
    answer: str = Field(description="Jawaban faktual dan komprehensif berdasarkan dokumen rujukan")
    citations: List[Citation] = Field(description="Daftar sitasi kutipan dokumen yang menjadi rujukan jawaban")
    confidence_rating: str = Field(description="Tingkat keyakinan: High, Medium, atau Low")
    is_grounded_in_doc: bool = Field(description="True jika seluruh jawaban didukung oleh dokumen, False jika tidak ada data relevan")

def get_gemini_client():
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise ValueError("GEMINI_API_KEY tidak ditemukan! Pastikan sudah menyetelnya di file .env")
    
    try:
        from google import genai
        return genai.Client(api_key=api_key)
    except ImportError:
        raise ImportError("Package 'google-genai' belum terpasang. Jalankan: pip install google-genai")

def cosine_similarity(vec_a: np.ndarray, vec_b: np.ndarray) -> float:
    norm_a = np.linalg.norm(vec_a)
    norm_b = np.linalg.norm(vec_b)
    if norm_a == 0 or norm_b == 0:
        return 0.0
    return float(np.dot(vec_a, vec_b) / (norm_a * norm_b))

def get_embedding(text: str, model_name: str = "text-embedding-004") -> List[float]:
    client = get_gemini_client()
    clean = text.strip()
    if not clean:
        return [0.0] * 768
    
    response = client.models.embed_content(
        model=model_name,
        contents=clean
    )
    if hasattr(response, "embeddings") and response.embeddings:
        return response.embeddings[0].values
    elif hasattr(response, "embedding") and response.embedding:
        return response.embedding.values
    return [0.0] * 768

def extract_text_from_pdf(pdf_source: Union[str, Path, bytes, io.BytesIO]) -> List[Tuple[int, str]]:
    """Mengekstrak teks per halaman dari file PDF. Mengembalikan list [(page_num, text)]."""
    if isinstance(pdf_source, (str, Path)):
        reader = PdfReader(str(pdf_source))
    elif isinstance(pdf_source, bytes):
        reader = PdfReader(io.BytesIO(pdf_source))
    else:
        reader = PdfReader(pdf_source)

    pages = []
    for idx, page in enumerate(reader.pages, 1):
        text = page.extract_text() or ""
        if text.strip():
            pages.append((idx, text.strip()))
    return pages

def chunk_text(
    pages: List[Tuple[int, str]],
    chunk_size: int = 600,
    chunk_overlap: int = 100
) -> List[DocumentChunk]:
    """Membagi teks halaman menjadi potongan chunk dengan window sliding overlap."""
    chunks: List[DocumentChunk] = []
    chunk_counter = 1

    for page_num, page_text in pages:
        start = 0
        text_len = len(page_text)

        while start < text_len:
            end = min(start + chunk_size, text_len)
            chunk_content = page_text[start:end].strip()

            if chunk_content:
                chunks.append(DocumentChunk(
                    chunk_id=chunk_counter,
                    page_number=page_num,
                    content=chunk_content,
                    char_count=len(chunk_content)
                ))
                chunk_counter += 1

            if end == text_len:
                break
            start += (chunk_size - chunk_overlap)

    return chunks

class PDFRAGSession:
    """Mengelola siklus hidup RAG: Chunking -> Vector Indexing -> Retrieval -> Generation."""

    def __init__(self, chunk_size: int = 600, chunk_overlap: int = 100):
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.chunks: List[DocumentChunk] = []
        self.embeddings: List[np.ndarray] = []
        self.document_name: str = "Unknown"

    def load_and_index_document(
        self,
        source: Union[str, Path, bytes],
        doc_name: str = "document.pdf",
        model_name: str = "text-embedding-004"
    ) -> int:
        """Membaca dokumen, melakukan chunking, dan menghitung embeddings untuk semua chunk."""
        self.document_name = doc_name

        if isinstance(source, (str, Path)) and str(source).endswith(".txt"):
            text = Path(source).read_text(encoding="utf-8")
            pages = [(1, text)]
        elif isinstance(source, bytes) and doc_name.endswith(".txt"):
            text = source.decode("utf-8")
            pages = [(1, text)]
        else:
            pages = extract_text_from_pdf(source)

        if not pages:
            raise ValueError("Tidak ada teks yang dapat diekstrak dari dokumen ini.")

        self.chunks = chunk_text(pages, self.chunk_size, self.chunk_overlap)
        
        # Hitung embeddings untuk seluruh chunks
        self.embeddings = []
        for chunk in self.chunks:
            vec = get_embedding(chunk.content, model_name=model_name)
            self.embeddings.append(np.array(vec))

        return len(self.chunks)

    def retrieve_relevant_chunks(
        self,
        query: str,
        top_k: int = 4,
        threshold: float = 0.35,
        model_name: str = "text-embedding-004"
    ) -> List[Tuple[float, DocumentChunk]]:
        """Mencari chunk paling relevan berdasarkan Cosine Similarity."""
        query_vec = np.array(get_embedding(query, model_name=model_name))

        scored = []
        for idx, chunk in enumerate(self.chunks):
            chunk_vec = self.embeddings[idx]
            sim = cosine_similarity(query_vec, chunk_vec)
            if sim >= threshold:
                scored.append((sim, chunk))

        scored.sort(key=lambda x: x[0], reverse=True)
        return scored[:top_k]

    def ask(
        self,
        question: str,
        top_k: int = 4,
        threshold: float = 0.35,
        model_name: str = "gemini-2.5-flash"
    ) -> RAGAnswer:
        """
        Menjawab pertanyaan pengguna secara akurat dengan context grounding dari dokumen.
        """
        clean_q = question.strip()
        if not clean_q:
            raise ValueError("Pertanyaan tidak boleh kosong.")

        # 1. Retrieval
        scored_chunks = self.retrieve_relevant_chunks(clean_q, top_k=top_k, threshold=threshold)

        if not scored_chunks:
            return RAGAnswer(
                answer="Maaf, informasi mengenai pertanyaan Anda tidak ditemukan di dalam dokumen ini (tidak ada bagian teks yang memenuhi ambang batas relevansi).",
                citations=[],
                confidence_rating="Low",
                is_grounded_in_doc=False
            )

        # 2. Susun Context Prompt
        context_blocks = []
        citations: List[Citation] = []

        for sim, chunk in scored_chunks:
            context_blocks.append(
                f"--- [KUTIPAN CHUNK #{chunk.chunk_id} | Halaman {chunk.page_number} | Relevance: {sim*100:.1f}%] ---\n{chunk.content}"
            )
            citations.append(Citation(
                chunk_id=chunk.chunk_id,
                page_number=chunk.page_number,
                similarity_score=round(sim, 4),
                snippet=chunk.content[:180] + "..." if len(chunk.content) > 180 else chunk.content
            ))

        formatted_context = "\n\n".join(context_blocks)

        system_instruction = f"""
        Kamu adalah Asisten RAG (Retrieval-Augmented Generation) yang profesional, tepat, dan jujur.
        Tugasmu adalah menjawab pertanyaan pengguna HANYA berdasarkan konteks dokumen yang diberikan.

        === KONTEKS DOKUMEN: {self.document_name} ===
        {formatted_context}
        ============================================

        ATURAN KETAT:
        1. Jawab secara faktual dan komprehensif menggunakan fakta yang tertera pada konteks di atas.
        2. Cantumkan rujukan spesifik (misal: "Berdasarkan Bab 2...", atau "[Chunk #X]").
        3. DILARANG KERAS berhalusinasi atau menambahkan asumsi di luar isi dokumen.
        4. Jika jawaban tidak tertera pada dokumen, katakan secara lugas bahwa informasi tidak tersedia di dokumen.
        """

        client = get_gemini_client()
        response = client.models.generate_content(
            model=model_name,
            contents=f"Pertanyaan Pengguna: {clean_q}",
            config={
                "response_mime_type": "application/json",
                "response_schema": RAGAnswer,
                "temperature": 0.1,
                "system_instruction": system_instruction
            }
        )

        parsed = json.loads(response.text)
        parsed["citations"] = [c.model_dump() for c in citations]
        return RAGAnswer(**parsed)
