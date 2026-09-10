"""
Day 12 - Web Search Augmented AI Synthesizer (Mini Perplexity Core Engine)
Mensintesiskan hasil pencarian web real-time menjadi jawaban komprehensif
dengan sitasi bernomor [1], [2] dan rekomendasi pertanyaan terkait.
"""

import os
import json
import time
from typing import List, Optional
from pydantic import BaseModel, Field
from dotenv import load_dotenv

from searcher import search_duckduckgo_web, WebResult

load_dotenv()

class PerplexityResponse(BaseModel):
    query: str
    answer_markdown: str = Field(description="Jawaban sintetis faktual lengkap dengan sitasi bernomor seperti [1], [2]")
    sources: List[WebResult] = Field(description="Daftar sumber web yang dirujuk dalam jawaban")
    related_questions: List[str] = Field(description="3 pertanyaan lanjutan yang relevan untuk memperdalam topik")
    search_latency_ms: float
    total_latency_ms: float

class SynthesisRaw(BaseModel):
    answer_markdown: str = Field(description="Jawaban informatif dengan sitasi [1], [2], [3] tepat di akhir klausa atau kalimat")
    related_questions: List[str] = Field(description="3 pertanyaan pencarian lanjutan yang menarik")

def get_gemini_client():
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise ValueError("GEMINI_API_KEY tidak ditemukan! Pastikan sudah menyetelnya di file .env")
    
    try:
        from google import genai
        return genai.Client(api_key=api_key)
    except ImportError:
        raise ImportError("Package 'google-genai' belum terpasang. Jalankan: pip install google-genai")

def synthesize_web_answer(
    user_query: str,
    max_search_results: int = 5,
    model_name: str = "gemini-2.5-flash"
) -> PerplexityResponse:
    """
    Pipeline Mini-Perplexity:
    1. Cari web secara real-time via DuckDuckGo
    2. Format snippets & URL sumber dengan index [1], [2], dst
    3. Minta Gemini mensintesis jawaban faktual dengan rujukan sitasi
    """
    total_start = time.time()
    
    # 1. Real-time Web Search
    search_start = time.time()
    web_sources = search_duckduckgo_web(user_query, max_results=max_search_results)
    search_elapsed_ms = (time.time() - search_start) * 1000

    # 2. Format konteks web
    formatted_sources = []
    for s in web_sources:
        formatted_sources.append(
            f"[{s.index}] Sumber: {s.title} ({s.domain})\nURL: {s.url}\nCuplikan: {s.snippet}"
        )
    sources_context = "\n\n".join(formatted_sources)

    # 3. Prompting AI Synthesizer
    client = get_gemini_client()

    system_instruction = """
    Kamu adalah Perplexity AI - Mesin Pencari & Asisten Sintesis Pengetahuan Real-Time kelas dunia.
    Tugasmu adalah menjawab pertanyaan pengguna secara komprehensif, akurat, dan netral HANYA berdasarkan cuplikan hasil pencarian web yang disediakan.

    ATURAN SITASI KETAT:
    1. Setiap klausa atau fakta penting WAJIB menyertakan nomor sitasi dalam kurung siku, contoh: [1], [2], atau [1][3].
    2. Nomor sitasi [X] HARUS sesuai persis dengan nomor indeks sumber yang ada pada konteks.
    3. Susun jawaban dalam format Markdown yang rapi dengan sub-heading, bullet points, atau tabel perbandingan jika diperlukan.
    4. Jika terdapat informasi yang saling bertentangan antar sumber, sebutkan perbedaannya secara objektif.
    5. Rekomendasikan 3 pertanyaan lanjutan (related questions) yang relevan untuk dieksplorasi pengguna.
    """

    prompt = f"""
    === HASIL PENCARIAN WEB TERBARU ===
    {sources_context}
    ====================================

    Pertanyaan Pengguna: "{user_query}"
    """

    response = client.models.generate_content(
        model=model_name,
        contents=prompt,
        config={
            "response_mime_type": "application/json",
            "response_schema": SynthesisRaw,
            "temperature": 0.2,
            "system_instruction": system_instruction
        }
    )

    parsed = json.loads(response.text)
    total_elapsed_ms = (time.time() - total_start) * 1000

    return PerplexityResponse(
        query=user_query,
        answer_markdown=parsed["answer_markdown"],
        sources=web_sources,
        related_questions=parsed.get("related_questions", []),
        search_latency_ms=round(search_elapsed_ms, 2),
        total_latency_ms=round(total_elapsed_ms, 2)
    )
