"""
Day 03 - Text to SQL AI Engine
Menerjemahkan pertanyaan bahasa manusia (Indonesia & Inggris) menjadi query SQL SQLite,
memvalidasi keamanan query, dan memberikan penjelasan serta rekomendasi visualisasi.
"""

import os
import re
import json
from typing import List, Optional, Dict, Any, Tuple
from pydantic import BaseModel, Field
from dotenv import load_dotenv

from database import get_schema_description, execute_query

load_dotenv()

class SQLGenerationResult(BaseModel):
    sql_query: str = Field(description="SQL query SQLite yang valid, optimal, dan aman")
    explanation: str = Field(description="Penjelasan dalam bahasa Indonesia tentang bagaimana query ini bekerja")
    tables_used: List[str] = Field(description="Daftar tabel yang digunakan dalam query")
    is_safe: bool = Field(description="True jika query hanya membaca data (SELECT), False jika destruktif")
    chart_recommendation: str = Field(
        description="Rekomendasi jenis visualisasi: 'bar_chart', 'line_chart', 'pie_chart', atau 'table'"
    )
    x_axis_column: Optional[str] = Field(
        default=None,
        description="Nama kolom untuk sumbu X grafik (kategori/label/tanggal)"
    )
    y_axis_column: Optional[str] = Field(
        default=None,
        description="Nama kolom untuk sumbu Y grafik (metrik numerik seperti total/jumlah)"
    )
    business_insights: str = Field(
        description="Penjelasan singkat apa makna bisnis dari query ini dan insight yang bisa didapat"
    )

DANGEROUS_KEYWORDS = ["DROP", "DELETE", "TRUNCATE", "UPDATE", "INSERT", "ALTER", "GRANT", "REVOKE"]

def get_gemini_client():
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise ValueError("GEMINI_API_KEY tidak ditemukan! Pastikan sudah menyetelnya di file .env")
    
    try:
        from google import genai
        return genai.Client(api_key=api_key)
    except ImportError:
        raise ImportError("Package 'google-genai' belum terpasang. Jalankan: pip install google-genai")

def validate_sql_safety(query: str) -> Tuple[bool, str]:
    """Validasi agar query hanya berupa SELECT read-only."""
    clean = query.strip().upper()
    
    # Cek keyword berbahaya
    for kw in DANGEROUS_KEYWORDS:
        if re.search(r'\b' + kw + r'\b', clean):
            return False, f"Query ditolak karena mengandung operasi destruktif: '{kw}'."
            
    if not clean.startswith("SELECT") and not clean.startswith("WITH"):
        return False, "Hanya operasi SELECT read-only yang diizinkan."

    return True, "Query aman."

def generate_sql_from_natural_language(
    user_question: str,
    model_name: str = "gemini-2.5-flash"
) -> SQLGenerationResult:
    """
    Menghasilkan SQL query berdasarkan pertanyaan pengguna menggunakan schema context.
    """
    clean_question = user_question.strip()
    if not clean_question:
        raise ValueError("Pertanyaan tidak boleh kosong.")

    client = get_gemini_client()
    schema_info = get_schema_description()

    prompt = f"""
    Kamu adalah Principal Data Analyst & SQL Expert (SQLite).
    Tugasmu adalah menerjemahkan pertanyaan pengguna menjadi query SQL SQLite yang akurat, efisien, dan bersih.

    {schema_info}

    === PERTANYAAN PENGGUNA ===
    "{clean_question}"
    ===========================

    Panduan Khusus Penulisan SQL:
    1. HANYA gunakan SELECT query (jangan gunakan INSERT/UPDATE/DELETE/DROP).
    2. Gunakan JOIN yang tepat antar tabel (misal: orders.customer_id = customers.customer_id).
    3. Jika diminta agregasi (total, rata-rata, jumlah), gunakan SUM(), AVG(), COUNT() dengan GROUP BY yang sesuai.
    4. Format alias kolom dengan nama yang ramah dibaca (misal: total_belanja, total_orders, nama_kategori).
    5. Urutkan dengan ORDER BY dan batasi dengan LIMIT jika relevan (misal: "Top 5 ...").
    6. Tentukan rekomendasi grafik ('bar_chart', 'line_chart', 'pie_chart', atau 'table') serta kolom x dan y yang tepat.
    """

    response = client.models.generate_content(
        model=model_name,
        contents=prompt,
        config={
            "response_mime_type": "application/json",
            "response_schema": SQLGenerationResult,
            "temperature": 0.1,
        },
    )

    parsed_dict = json.loads(response.text)
    result = SQLGenerationResult(**parsed_dict)
    
    # Double validation
    is_safe, reason = validate_sql_safety(result.sql_query)
    if not is_safe:
        result.is_safe = False
        result.explanation = f"[SECURITY BLOCKED] {reason}"
    
    return result

def query_database_with_nl(user_question: str, model_name: str = "gemini-2.5-flash") -> Dict[str, Any]:
    """
    Pipeline lengkap: Pertanyaan -> SQL Generator -> Eksekusi Database -> Hasil Lengkap.
    """
    gen_result = generate_sql_from_natural_language(user_question, model_name=model_name)
    
    if not gen_result.is_safe:
        return {
            "success": False,
            "error": gen_result.explanation,
            "sql": gen_result.sql_query,
            "result_meta": gen_result
        }

    try:
        columns, rows, elapsed_ms = execute_query(gen_result.sql_query)
        return {
            "success": True,
            "columns": columns,
            "rows": rows,
            "row_count": len(rows),
            "execution_time_ms": round(elapsed_ms, 2),
            "sql": gen_result.sql_query,
            "result_meta": gen_result
        }
    except Exception as e:
        return {
            "success": False,
            "error": f"Kesalahan saat menjalankan SQL: {str(e)}",
            "sql": gen_result.sql_query,
            "result_meta": gen_result
        }
