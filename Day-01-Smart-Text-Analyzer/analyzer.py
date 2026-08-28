"""
Day 01 - Smart AI Text Analyzer Core Module
Mendukung ekstraksi intisari, analisis sentimen mendalam, ekstraksi topik kunci,
dan action points menggunakan model Gemini 2.5 Flash / Pro.
"""

import os
import json
from typing import List, Optional
from pydantic import BaseModel, Field
from dotenv import load_dotenv

load_dotenv()

class SentimentDetail(BaseModel):
    sentiment: str = Field(description="Sentimen utama: POSITIVE, NEGATIVE, atau NEUTRAL")
    score: float = Field(description="Skor kepercayaan sentimen dari 0.0 sampai 1.0")
    explanation: str = Field(description="Alasan singkat penentuan sentimen")

class AnalysisResult(BaseModel):
    summary: str = Field(description="Ringkasan padat dan informatif dari teks yang diberikan")
    sentiment: SentimentDetail = Field(description="Detail analisis sentimen")
    key_topics: List[str] = Field(description="Daftar 3-5 topik/kata kunci utama")
    action_items: List[str] = Field(description="Daftar poin tindakan atau rekomendasi dari teks")
    detected_language: str = Field(description="Bahasa utama teks (misal: Indonesian, English)")
    word_count: int = Field(description="Jumlah kata dalam teks asli")

def get_gemini_client():
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise ValueError("GEMINI_API_KEY tidak ditemukan! Pastikan sudah menyetelnya di file .env")
    
    try:
        from google import genai
        return genai.Client(api_key=api_key)
    except ImportError:
        raise ImportError("Package 'google-genai' belum terpasang. Jalankan: pip install google-genai")

def analyze_text(text: str, model_name: str = "gemini-2.5-flash") -> AnalysisResult:
    """
    Menganalisis teks menggunakan Google Gemini API dengan output terstruktur (Pydantic).
    """
    clean_text = text.strip()
    if not clean_text:
        raise ValueError("Teks input tidak boleh kosong.")

    word_count = len(clean_text.split())
    client = get_gemini_client()

    prompt = f"""
    Kamu adalah asisten analis teks dan sentimen profesional multi-bahasa.
    Analisis teks berikut secara mendalam dan kembalikan output sesuai skema yang diminta:

    === TEKS INPUT ===
    {clean_text}
    ==================

    Instruksi Tambahan:
    - Ringkasan harus padat, jelas, dan menangkap inti permasalahan atau informasi.
    - Tentukan sentimen secara objektif dan berikan skor keyakinan 0.0 - 1.0.
    - Ekstrak 3-5 topik atau entitas paling penting.
    - Jika ada komplain, saran, atau langkah lanjutan, masukkan ke action_items.
    """

    response = client.models.generate_content(
        model=model_name,
        contents=prompt,
        config={
            "response_mime_type": "application/json",
            "response_schema": AnalysisResult,
            "temperature": 0.2,
        },
    )

    result_json = response.text
    parsed_dict = json.loads(result_json)
    parsed_dict["word_count"] = word_count
    return AnalysisResult(**parsed_dict)
