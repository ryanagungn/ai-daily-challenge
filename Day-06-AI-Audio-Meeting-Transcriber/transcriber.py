"""
Day 06 - AI Audio Meeting Transcriber & Minutes Summarizer Core Module
Mentranskripsikan rekaman audio rapat (meeting), mengekstrak ringkasan eksekutif,
topik diskusi per pembicara, keputusan kunci, dan daftar tindakan (Action Items)
menggunakan Gemini 2.5 Flash Audio Multimodal.
"""

import os
import json
import mimetypes
from pathlib import Path
from typing import List, Literal, Optional, Union
from pydantic import BaseModel, Field
from dotenv import load_dotenv

load_dotenv()

class ActionItem(BaseModel):
    task: str = Field(description="Deskripsi tugas atau tindakan yang harus dilakukan")
    assignee: str = Field(description="Nama penanggung jawab tugas (misal: 'Siti Rahmawati' atau 'Team DevOps')")
    priority: Literal["High", "Medium", "Low"] = Field(description="Tingkat prioritas tindakan")
    deadline: Optional[str] = Field(default=None, description="Tenggat waktu atau target penyelesaian jika disebutkan")

class TopicDiscussion(BaseModel):
    topic_name: str = Field(description="Nama topik atau agenda yang dibahas")
    summary: str = Field(description="Ringkasan poin-poin penting yang didiskusikan")
    key_speakers: List[str] = Field(description="Nama-nama pembicara yang aktif dalam topik ini")

class MeetingMinutes(BaseModel):
    meeting_title: str = Field(description="Judul atau topik utama rapat")
    meeting_date: Optional[str] = Field(default=None, description="Tanggal rapat jika disebutkan")
    duration_estimate: Optional[str] = Field(default=None, description="Estimasi durasi rapat")
    attendees: List[str] = Field(description="Daftar nama peserta/pembicara yang hadir dalam rapat")
    executive_summary: str = Field(description="Ringkasan eksekutif menyeluruh dari hasil rapat (2-4 kalimat)")
    discussion_topics: List[TopicDiscussion] = Field(description="Rincian pembahasan per topik/agenda")
    key_decisions: List[str] = Field(description="Daftar keputusan final yang disepakati bersama")
    action_items: List[ActionItem] = Field(description="Daftar action items yang terstruktur dan dapat dieksekusi")
    overall_sentiment_and_tone: str = Field(
        description="Analisis suasana/tone rapat (misal: 'Produktif & Kolaboratif', 'Urgensi Tinggi')"
    )
    full_transcript: str = Field(
        description="Transkrip lengkap percakapan kata per kata dengan label pembicara dan perkiraan timestamp"
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

def get_audio_mime_type(file_path: Path) -> str:
    ext = file_path.suffix.lower()
    mime_map = {
        ".mp3": "audio/mp3",
        ".wav": "audio/wav",
        ".m4a": "audio/m4a",
        ".ogg": "audio/ogg",
        ".flac": "audio/flac",
        ".aac": "audio/aac",
        ".webm": "audio/webm"
    }
    return mime_map.get(ext, "audio/mp3")

def process_meeting_audio(
    audio_source: Union[str, Path, bytes],
    mime_type: Optional[str] = None,
    language_hint: str = "Bahasa Indonesia",
    model_name: str = "gemini-2.5-flash"
) -> MeetingMinutes:
    """
    Mentranskripsikan file audio dan menghasilkan notulen rapat terstruktur.
    """
    client = get_gemini_client()
    from google.genai import types

    audio_part = None
    if isinstance(audio_source, (str, Path)):
        p = Path(audio_source)
        if not p.exists():
            raise FileNotFoundError(f"File audio tidak ditemukan: {p}")
        detected_mime = mime_type or get_audio_mime_type(p)
        audio_bytes = p.read_bytes()
        audio_part = types.Part.from_bytes(data=audio_bytes, mime_type=detected_mime)
    elif isinstance(audio_source, bytes):
        if not mime_type:
            mime_type = "audio/wav"
        audio_part = types.Part.from_bytes(data=audio_source, mime_type=mime_type)
    else:
        raise TypeError("audio_source harus berupa path file atau raw bytes.")

    prompt = f"""
    Kamu adalah Notulis Profesional (Executive Meeting Secretary) dan Speech-to-Text Specialist tingkat tinggi.
    Dengarkan rekaman audio rapat ini secara teliti dan buatkan Notulen Rapat (Meeting Minutes) yang komprehensif.

    Bahasa Utama Audio: {language_hint}

    Instruksi Pembuatan Notulen:
    1. Transkripsikan seluruh percakapan secara akurat ke dalam `full_transcript`, sertakan label pembicara (speaker diarization).
    2. Ekstrak judul rapat, tanggal, dan daftar seluruh nama peserta/hadirin (`attendees`).
    3. Tuliskan `executive_summary` yang padat dan jelas mengenai tujuan dan hasil rapat.
    4. Kelompokkan topik-topik bahasan utama ke dalam `discussion_topics`.
    5. Catat semua `key_decisions` yang disepakati.
    6. Buat daftar `action_items` konkret: apa tugasnya, siapa penanggung jawabnya (assignee), prioritasnya, dan deadline (jika ada).
    7. Evaluasi `overall_sentiment_and_tone` dari diskusi tersebut.
    """

    response = client.models.generate_content(
        model=model_name,
        contents=[audio_part, prompt],
        config={
            "response_mime_type": "application/json",
            "response_schema": MeetingMinutes,
            "temperature": 0.2,
        },
    )

    parsed_dict = json.loads(response.text)
    return MeetingMinutes(**parsed_dict)

def process_meeting_text_transcript(
    transcript_text: str,
    language_hint: str = "Bahasa Indonesia",
    model_name: str = "gemini-2.5-flash"
) -> MeetingMinutes:
    """
    Menghasilkan notulen rapat terstruktur dari teks transkrip / catatan mentah rapat.
    """
    client = get_gemini_client()

    prompt = f"""
    Kamu adalah Notulis Profesional (Executive Meeting Secretary).
    Analisis teks transkrip rapat berikut dan buatkan Notulen Rapat (Meeting Minutes) yang sangat terstruktur:

    === TEKS TRANSKRIP RAPAT ===
    {transcript_text.strip()}
    ============================

    Instruksi:
    1. Ekstrak judul rapat, tanggal, dan daftar seluruh nama peserta/hadirin (`attendees`).
    2. Tuliskan `executive_summary` menyeluruh.
    3. Rincikan topik-topik bahasan utama ke dalam `discussion_topics`.
    4. Tuliskan `key_decisions` yang diambil.
    5. Ekstrak `action_items` lengkap dengan penanggung jawab (`assignee`), prioritas (`High/Medium/Low`), dan tenggat waktu.
    6. Evaluasi tone dan sertakan transkrip bersih pada `full_transcript`.
    """

    response = client.models.generate_content(
        model=model_name,
        contents=prompt,
        config={
            "response_mime_type": "application/json",
            "response_schema": MeetingMinutes,
            "temperature": 0.2,
        },
    )

    parsed_dict = json.loads(response.text)
    return MeetingMinutes(**parsed_dict)
