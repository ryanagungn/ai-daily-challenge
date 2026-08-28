"""
Day 02 - AI Code Reviewer & Refactor Assistant Core Module
Menganalisis kode sumber, mendeteksi bug, celah keamanan (vulnerability),
inefisiensi performa, dan menghasilkan kode refaktor yang bersih (clean code)
menggunakan model Gemini 2.5 Flash.
"""

import os
import json
from typing import List, Literal, Optional
from pydantic import BaseModel, Field
from dotenv import load_dotenv

load_dotenv()

class CodeIssue(BaseModel):
    category: Literal["Security", "Bug", "Performance", "Code Smell", "Style / Best Practice"] = Field(
        description="Kategori masalah pada kode"
    )
    severity: Literal["Critical", "High", "Medium", "Low", "Info"] = Field(
        description="Tingkat keparahan masalah"
    )
    line_number: Optional[str] = Field(
        default=None,
        description="Perkiraan baris kode yang bermasalah (misal: 'Line 14' atau 'Lines 20-25')"
    )
    title: str = Field(description="Judul singkat masalah")
    description: str = Field(description="Penjelasan detail mengapa hal ini menjadi masalah")
    suggestion: str = Field(description="Solusi perbaikan konkret")

class CodeReviewResult(BaseModel):
    language: str = Field(description="Bahasa pemrograman yang terdeteksi (Python, JS, Go, dll)")
    quality_score: int = Field(
        ge=1, le=10,
        description="Skor kualitas kode keseluruhan dari 1 (sangat buruk) sampai 10 (sempurna)"
    )
    executive_summary: str = Field(
        description="Ringkasan eksekutif tentang kondisi kode dan temuan utama"
    )
    issues: List[CodeIssue] = Field(
        default_factory=list,
        description="Daftar semua masalah yang ditemukan"
    )
    refactored_code: str = Field(
        description="Seluruh kode setelah diperbaiki dan direfaktor secara lengkap tanpa placeholder"
    )
    explanation_of_changes: List[str] = Field(
        description="Daftar poin perubahan penting yang dilakukan pada kode refaktor"
    )
    time_complexity_before: Optional[str] = Field(
        default=None,
        description="Estimasi kompleksitas waktu sebelum refaktor (misal: O(N^2))"
    )
    time_complexity_after: Optional[str] = Field(
        default=None,
        description="Estimasi kompleksitas waktu setelah refaktor (misal: O(N))"
    )

def get_gemini_client():
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise ValueError("GEMINI_API_KEY tidak ditemukan! Pastikan sudah menyetelnya di file .env")
    
    try:
        from google import genai
        return genai.Client(api_key=api_key)
    except ImportError:
        raise ImportError("Package 'google-genai' belum terpasang. Jalankan: pip install google-genai")

def review_code(
    code_content: str,
    language_hint: Optional[str] = None,
    focus: str = "General (All)",
    model_name: str = "gemini-2.5-flash"
) -> CodeReviewResult:
    """
    Melakukan review kode komprehensif dan menghasilkan refactoring terstruktur.
    """
    clean_code = code_content.strip()
    if not clean_code:
        raise ValueError("Kode input tidak boleh kosong.")

    client = get_gemini_client()

    prompt = f"""
    Kamu adalah Senior Software Engineer, Security Auditor, dan Clean Code Specialist kelas dunia.
    Tugasmu adalah mereview kode berikut secara mendalam, objektif, dan kritis.

    === KODE SUMBER ===
    {clean_code}
    ===================

    Fokus Review Tambahan: {focus}
    Petunjuk Bahasa (jika ada): {language_hint or "Auto-detect"}

    Instruksi Penilaian & Refactoring:
    1. Periksa celah keamanan (OWASP top 10, SQL Injection, XSS, Hardcoded Secrets, unsafe eval/exec, insecure deserialization).
    2. Deteksi bug logika, unhandled exceptions, memory leaks, resource leaks (file unclosed), mutable default arguments.
    3. Evaluasi performa (N+1 queries, unnecessary loops, suboptimal algorithms, data structure misuse).
    4. Terapkan Clean Code, SOLID Principles, naming convention, type hints/docstrings sesuai standar bahasa.
    5. Tuliskan `refactored_code` LENGKAP dari awal sampai akhir, siap dijalankan (jangan gunakan potongan '... rest of code').
    6. Berikan skor objektif 1-10 berdasarkan standar industri produksi.
    """

    response = client.models.generate_content(
        model=model_name,
        contents=prompt,
        config={
            "response_mime_type": "application/json",
            "response_schema": CodeReviewResult,
            "temperature": 0.1,
        },
    )

    result_json = response.text
    parsed_dict = json.loads(result_json)
    return CodeReviewResult(**parsed_dict)
