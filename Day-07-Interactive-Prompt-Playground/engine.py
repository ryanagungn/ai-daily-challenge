"""
Day 07 - Interactive Prompt Engineering Engine
Menyediakan modul eksekusi prompt dengan dynamic variable interpolation,
hyperparameter tuning, benchmark A/B testing, AI prompt optimizer, dan code generator.
"""

import os
import re
import time
import json
from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field
from dotenv import load_dotenv

load_dotenv()

class ExecutionMetrics(BaseModel):
    latency_ms: float
    output_char_count: int
    output_word_count: int
    model_used: str
    temperature: float
    top_p: float

class ExecutionResult(BaseModel):
    output_text: str
    interpolated_prompt: str
    metrics: ExecutionMetrics

class PromptOptimizationResult(BaseModel):
    original_prompt: str
    optimized_system_instruction: str = Field(description="System instruction yang lebih tajam dan terstruktur")
    optimized_user_prompt: str = Field(description="Prompt pengguna yang disempurnakan dengan role, konteks, batasan, dan format output")
    key_improvements: List[str] = Field(description="Daftar poin peningkatan yang diterapkan pada prompt baru")
    recommended_temperature: float = Field(description="Rekomendasi nilai temperature ideal (0.0 - 1.0)")

def get_gemini_client():
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise ValueError("GEMINI_API_KEY tidak ditemukan! Pastikan sudah menyetelnya di file .env")
    
    try:
        from google import genai
        return genai.Client(api_key=api_key)
    except ImportError:
        raise ImportError("Package 'google-genai' belum terpasang. Jalankan: pip install google-genai")

def extract_variables_from_template(template: str) -> List[str]:
    """Mengekstrak nama variabel dalam pola {{nama_variabel}}."""
    return sorted(list(set(re.findall(r"\{\{([a-zA-Z0-9_]+)\}\}", template))))

def interpolate_variables(template: str, variables: Dict[str, str]) -> str:
    """Mengganti {{variabel}} dengan nilai aktual."""
    result = template
    for key, value in variables.items():
        pattern = r"\{\{" + re.escape(key) + r"\}\}"
        result = re.sub(pattern, str(value), result)
    return result

def run_prompt_inference(
    prompt_template: str,
    variables: Optional[Dict[str, str]] = None,
    system_instruction: Optional[str] = None,
    model_name: str = "gemini-2.5-flash",
    temperature: float = 0.7,
    top_p: float = 0.95,
    max_output_tokens: Optional[int] = 1024,
) -> ExecutionResult:
    """
    Mengeksekusi prompt ke model Gemini dengan parameter kustom dan mengukur performa.
    """
    client = get_gemini_client()
    final_prompt = interpolate_variables(prompt_template, variables or {})
    
    from google.genai import types
    config = types.GenerateContentConfig(
        temperature=temperature,
        top_p=top_p,
        max_output_tokens=max_output_tokens,
        system_instruction=system_instruction if system_instruction and system_instruction.strip() else None
    )

    start_time = time.time()
    response = client.models.generate_content(
        model=model_name,
        contents=final_prompt,
        config=config
    )
    elapsed_ms = (time.time() - start_time) * 1000

    out_text = response.text or ""

    metrics = ExecutionMetrics(
        latency_ms=round(elapsed_ms, 2),
        output_char_count=len(out_text),
        output_word_count=len(out_text.split()),
        model_used=model_name,
        temperature=temperature,
        top_p=top_p
    )

    return ExecutionResult(
        output_text=out_text,
        interpolated_prompt=final_prompt,
        metrics=metrics
    )

def optimize_prompt(
    raw_prompt: str,
    goal: str = "Tingkatkan ketepatan, struktur jawaban, dan minimalkan halusinasi",
    model_name: str = "gemini-2.5-flash"
) -> PromptOptimizationResult:
    """
    Mengoptimalkan prompt menggunakan prinsip Prompt Engineering profesional (Role, Delimiters, CoT, Few-Shot).
    """
    client = get_gemini_client()

    meta_prompt = f"""
    Kamu adalah Master of Prompt Engineering kelas dunia.
    Tugasmu adalah menganalisis prompt mentah berikut dan merancangnya kembali menjadi prompt tingkat profesional:

    === PROMPT ASLI ===
    {raw_prompt}
    ===================

    Target / Tujuan Optimasi: {goal}

    Terapkan teknik terbaik:
    1. Role Definition & System Instruction yang kuat.
    2. Context & Clear Delimiters (misal: XML tags seperti <input>, <constraints> atau triple quotes).
    3. Output Format yang eksplisit (Markdown, Bullet Points, atau JSON).
    4. Guardrails (Batasan apa yang TIDAK boleh dilakukan model).
    5. Nilai rekomendasi temperature.
    """

    response = client.models.generate_content(
        model=model_name,
        contents=meta_prompt,
        config={
            "response_mime_type": "application/json",
            "response_schema": PromptOptimizationResult,
            "temperature": 0.2,
        }
    )

    parsed_dict = json.loads(response.text)
    parsed_dict["original_prompt"] = raw_prompt
    return PromptOptimizationResult(**parsed_dict)

def generate_python_snippet(
    prompt_template: str,
    system_instruction: Optional[str],
    variables: Dict[str, str],
    temperature: float,
    top_p: float,
    model_name: str = "gemini-2.5-flash"
) -> str:
    """Menghasilkan snippet kode Python mandiri siap copy-paste."""
    sys_inst_code = f'        system_instruction="""{system_instruction}""",\n' if system_instruction else ""
    vars_json = json.dumps(variables, indent=4)
    
    return f'''import os
from google import genai
from google.genai import types
from dotenv import load_dotenv

load_dotenv()

client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

variables = {vars_json}
prompt_template = """{prompt_template}"""

# Interpolate variables
final_prompt = prompt_template
for k, v in variables.items():
    final_prompt = final_prompt.replace(f"{{{{{k}}}}}", str(v))

response = client.models.generate_content(
    model="{model_name}",
    contents=final_prompt,
    config=types.GenerateContentConfig(
{sys_inst_code}        temperature={temperature},
        top_p={top_p}
    )
)

print(response.text)
'''
