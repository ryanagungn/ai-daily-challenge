"""
Day 10 - Technical Documentation & Codebase Q&A Search Engine Core Module
Mengimplementasikan Header-based Semantic Chunking untuk Markdown,
ekstraksi blok kode, indexing vektor (text-embedding-004), dan developer Q&A.
"""

import os
import re
import json
import time
from pathlib import Path
from typing import List, Dict, Any, Optional, Tuple
import numpy as np
from pydantic import BaseModel, Field
from dotenv import load_dotenv

load_dotenv()

CACHE_FILE = Path(__file__).parent / "docs_vector_cache.json"

class CodeSnippet(BaseModel):
    language: str
    code: str

class DocChunk(BaseModel):
    chunk_id: int
    file_name: str
    file_path: str
    header_breadcrumb: str
    content: str
    char_count: int
    code_blocks: List[CodeSnippet] = Field(default_factory=list)

class DocCitation(BaseModel):
    file_name: str
    header_breadcrumb: str
    similarity_score: float
    relevance_pct: str
    snippet: str

class TechnicalAnswer(BaseModel):
    direct_answer: str = Field(description="Jawaban teknis mendalam dengan penjelasan arsitektur, langkah-langkah, dan blok kode")
    referenced_sections: List[DocCitation] = Field(description="Daftar referensi bab dan file dokumentasi yang digunakan")
    suggested_follow_up_questions: List[str] = Field(description="2-3 pertanyaan teknis lanjutan yang relevan")
    confidence: str = Field(description="Tingkat keyakinan: High, Medium, Low")

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

def extract_code_blocks(text: str) -> List[CodeSnippet]:
    """Mengekstrak blok kode markdown fenced (```lang ... ```)."""
    pattern = r"```([a-zA-Z0-9_\-\+]*)\n(.*?)```"
    matches = re.findall(pattern, text, re.DOTALL)
    snippets = []
    for lang, code in matches:
        snippets.append(CodeSnippet(
            language=lang.strip() or "text",
            code=code.strip()
        ))
    return snippets

def parse_markdown_to_chunks(file_path: Path, base_dir: Path) -> List[DocChunk]:
    """
    Header-based Semantic Chunking: Memecah file markdown berdasarkan hierarki heading (#, ##, ###)
    sehingga setiap fungsi, bab, atau topik tetap utuh dan memiliki konteks breadcrumb.
    """
    text = file_path.read_text(encoding="utf-8")
    rel_path = str(file_path.relative_to(base_dir)).replace("\\", "/")
    
    lines = text.split("\n")
    chunks: List[DocChunk] = []
    
    current_headers = ["Root"]
    current_content = []
    chunk_counter = 1

    def save_current_chunk():
        nonlocal chunk_counter
        body = "\n".join(current_content).strip()
        if body:
            breadcrumb = " > ".join(current_headers)
            chunks.append(DocChunk(
                chunk_id=chunk_counter,
                file_name=file_path.name,
                file_path=rel_path,
                header_breadcrumb=breadcrumb,
                content=body,
                char_count=len(body),
                code_blocks=extract_code_blocks(body)
            ))
            chunk_counter += 1

    for line in lines:
        header_match = re.match(r"^(#{1,4})\s+(.*)$", line)
        if header_match:
            # Simpan chunk sebelumnya jika ada konten
            save_current_chunk()
            current_content = []

            level = len(header_match.group(1))
            title = header_match.group(2).strip()

            # Perbarui hierarki breadcrumb
            if level == 1:
                current_headers = [title]
            elif level == 2:
                current_headers = current_headers[:1] + [title]
            elif level == 3:
                current_headers = current_headers[:2] + [title]
            else:
                current_headers = current_headers[:3] + [title]
        else:
            current_content.append(line)

    save_current_chunk()
    return chunks

class TechnicalDocsEngine:
    def __init__(self, docs_dir: Path, cache_path: Path = CACHE_FILE):
        self.docs_dir = docs_dir
        self.cache_path = cache_path
        self.chunks: List[DocChunk] = []
        self.vectors: Dict[str, List[float]] = {}
        self.load_or_index_docs()

    def load_or_index_docs(self, force_reindex: bool = False, model_name: str = "text-embedding-004"):
        """Scan folder dokumen, lakukan header chunking, dan load/generate vector embeddings."""
        # 1. Parse all Markdown files
        self.chunks = []
        md_files = sorted(list(self.docs_dir.glob("**/*.md")) + list(self.docs_dir.glob("**/*.txt")))
        
        for f in md_files:
            file_chunks = parse_markdown_to_chunks(f, self.docs_dir)
            self.chunks.extend(file_chunks)

        # 2. Vector Cache
        if not force_reindex and self.cache_path.exists():
            try:
                self.vectors = json.loads(self.cache_path.read_text(encoding="utf-8"))
            except Exception:
                self.vectors = {}

        # 3. Embed missing chunks
        updated = False
        for ch in self.chunks:
            chunk_key = f"{ch.file_path}::{ch.header_breadcrumb}"
            if chunk_key not in self.vectors or force_reindex:
                embed_payload = f"File: {ch.file_path}\nSection: {ch.header_breadcrumb}\n{ch.content}"
                vec = get_embedding(embed_payload, model_name=model_name)
                self.vectors[chunk_key] = vec
                updated = True

        if updated:
            self.cache_path.write_text(json.dumps(self.vectors), encoding="utf-8")

    def search_docs(
        self,
        query: str,
        top_k: int = 4,
        threshold: float = 0.35,
        model_name: str = "text-embedding-004"
    ) -> List[Tuple[float, DocChunk]]:
        """Mencari bab dokumentasi paling relevan menggunakan Cosine Similarity."""
        query_vec = np.array(get_embedding(query, model_name=model_name))
        scored = []

        for ch in self.chunks:
            chunk_key = f"{ch.file_path}::{ch.header_breadcrumb}"
            vec = np.array(self.vectors.get(chunk_key, []))
            if len(vec) == 0:
                continue

            sim = cosine_similarity(query_vec, vec)
            if sim >= threshold:
                scored.append((sim, ch))

        scored.sort(key=lambda x: x[0], reverse=True)
        return scored[:top_k]

    def ask_technical_question(
        self,
        question: str,
        top_k: int = 4,
        threshold: float = 0.35,
        model_name: str = "gemini-2.5-flash"
    ) -> TechnicalAnswer:
        """
        Menjawab pertanyaan teknis/arsitektur/API dengan merujuk langsung ke file & bab dokumentasi.
        """
        clean_q = question.strip()
        scored_chunks = self.search_docs(clean_q, top_k=top_k, threshold=threshold)

        if not scored_chunks:
            return TechnicalAnswer(
                direct_answer="Maaf, informasi mengenai pertanyaan tersebut tidak ditemukan dalam dokumentasi teknis yang terindeks.",
                referenced_sections=[],
                suggested_follow_up_questions=["Bagaimana arsitektur umum backend?", "Bagaimana cara autentikasi API?"],
                confidence="Low"
            )

        context_blocks = []
        citations: List[DocCitation] = []

        for sim, ch in scored_chunks:
            context_blocks.append(
                f"=== FILE: {ch.file_path} | SECTION: {ch.header_breadcrumb} (Relevance: {sim*100:.1f}%) ===\n{ch.content}"
            )
            snippet = ch.content[:220] + "..." if len(ch.content) > 220 else ch.content
            citations.append(DocCitation(
                file_name=ch.file_name,
                header_breadcrumb=ch.header_breadcrumb,
                similarity_score=round(sim, 4),
                relevance_pct=f"{sim * 100:.1f}%",
                snippet=snippet
            ))

        formatted_context = "\n\n".join(context_blocks)

        system_instruction = f"""
        Kamu adalah Staff Principal Software Engineer & Technical Documentation Assistant.
        Jawab pertanyaan developer dengan jelas, tepat sasaran, profesional, dan sertakan contoh kode jika relevan.
        
        Rujukan Dokumentasi Resmi:
        {formatted_context}

        Panduan Menjawab:
        1. Berikan penjelasan teknis yang komprehensif langsung menjawab inti pertanyaan.
        2. Tuliskan blok kode (Markdown fenced ```) yang rapi dengan nama bahasa pemrograman jika pertanyaan membahas koding / API / konfigurasi.
        3. Sebutkan secara eksplisit file dan bagian yang menjadi rujukan (misal: "Berdasarkan `authentication.md` bagian `## 1. JWT Token Specifications`...").
        4. Jangan membuat asumsi yang bertentangan dengan dokumentasi di atas.
        """

        client = get_gemini_client()
        response = client.models.generate_content(
            model=model_name,
            contents=f"Pertanyaan Pengembang: {clean_q}",
            config={
                "response_mime_type": "application/json",
                "response_schema": TechnicalAnswer,
                "temperature": 0.1,
                "system_instruction": system_instruction
            }
        )

        parsed = json.loads(response.text)
        parsed["referenced_sections"] = [c.model_dump() for c in citations]
        return TechnicalAnswer(**parsed)
