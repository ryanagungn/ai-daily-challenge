"""
Day 04 - AI Flashcard & Quiz Generator Core Module
Mengubah catatan teks, artikel, atau topik pembelajaran menjadi Flashcards & Kuis Interaktif
berbasis skema Pydantic terstruktur dengan Gemini 2.5 Flash.
"""

import os
import json
from typing import List, Literal, Optional
from pydantic import BaseModel, Field
from dotenv import load_dotenv

load_dotenv()

class Flashcard(BaseModel):
    front: str = Field(description="Pertanyaan, konsep, atau istilah di sisi depan kartu")
    back: str = Field(description="Jawaban, definisi, atau penjelasan padat di sisi belakang kartu")
    hint: Optional[str] = Field(default=None, description="Petunjuk singkat untuk membantu mengingat")
    category_tag: str = Field(description="Kategori atau subtopik singkat kartu (misal: 'Arsitektur', 'Formula')")

class QuizOption(BaseModel):
    id: Literal["A", "B", "C", "D"] = Field(description="Label pilihan jawaban: A, B, C, atau D")
    text: str = Field(description="Isi teks pilihan jawaban")

class QuizQuestion(BaseModel):
    question_number: int = Field(description="Nomor urut pertanyaan kuis (1, 2, 3...)")
    question: str = Field(description="Teks pertanyaan kuis pilihan ganda yang menantang dan jelas")
    options: List[QuizOption] = Field(
        description="4 opsi jawaban (A, B, C, D) dengan 1 jawaban benar dan 3 distractor yang masuk akal"
    )
    correct_option_id: Literal["A", "B", "C", "D"] = Field(description="ID pilihan jawaban yang benar (A/B/C/D)")
    explanation: str = Field(description="Penjelasan detail mengapa jawaban tersebut benar dan opsi lain salah")
    difficulty: Literal["Easy", "Medium", "Hard"] = Field(description="Tingkat kesulitan pertanyaan")

class StudyDeck(BaseModel):
    topic_title: str = Field(description="Judul topik materi pembelajaran")
    summary: str = Field(description="Ringkasan eksekutif 2-3 kalimat mengenai materi yang dipelajari")
    target_audience: str = Field(description="Target level pembelajar (misal: 'Pemula', 'Menengah', 'Lanjutan')")
    flashcards: List[Flashcard] = Field(description="Daftar kartu flashcard untuk spaced repetition")
    quiz: List[QuizQuestion] = Field(description="Daftar pertanyaan kuis pilihan ganda")

def get_gemini_client():
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise ValueError("GEMINI_API_KEY tidak ditemukan! Pastikan sudah menyetelnya di file .env")
    
    try:
        from google import genai
        return genai.Client(api_key=api_key)
    except ImportError:
        raise ImportError("Package 'google-genai' belum terpasang. Jalankan: pip install google-genai")

def generate_study_deck(
    content: str,
    num_cards: int = 5,
    num_questions: int = 5,
    difficulty: str = "Medium",
    model_name: str = "gemini-2.5-flash"
) -> StudyDeck:
    """
    Menghasilkan Flashcards dan Kuis Pilihan Ganda dari materi/catatan teks.
    """
    clean_text = content.strip()
    if not clean_text:
        raise ValueError("Materi atau teks pembelajaran tidak boleh kosong.")

    client = get_gemini_client()

    prompt = f"""
    Kamu adalah Ahli Pedagogi Pembelajaran dan Pembuat Kurikulum Digital (EdTech Specialist).
    Tugasmu adalah menyusun Flashcards dan Kuis Pilihan Ganda berkualitas tinggi dari materi berikut:

    === MATERI PEMBELAJARAN ===
    {clean_text}
    ===========================

    Instruksi Pembuatan:
    1. Buat tepat {num_cards} Flashcards yang menguji pemahaman konsep kunci, rumus, definisi, atau fakta penting.
    2. Buat tepat {num_questions} Kuis Pilihan Ganda tingkat {difficulty}.
    3. Setiap soal kuis HARUS memiliki 4 opsi (A, B, C, D) dengan 1 jawaban benar dan 3 pengecoh (distractor) yang meyakinkan.
    4. Sediakan penjelasan edukatif mengapa jawaban benar dan mengapa pengecoh salah.
    5. Gunakan bahasa yang sama dengan materi input (Bahasa Indonesia jika materi berbahasa Indonesia).
    """

    response = client.models.generate_content(
        model=model_name,
        contents=prompt,
        config={
            "response_mime_type": "application/json",
            "response_schema": StudyDeck,
            "temperature": 0.2,
        },
    )

    parsed_dict = json.loads(response.text)
    return StudyDeck(**parsed_dict)

def export_to_anki_csv(deck: StudyDeck) -> str:
    """Mengonversi flashcard ke format TSV/CSV yang kompatibel untuk diimpor ke aplikasi Anki."""
    lines = ["#separator:tab", "#html:true", "#tags column:3"]
    for card in deck.flashcards:
        front_clean = card.front.replace("\t", " ").replace("\n", "<br>")
        back_clean = card.back.replace("\t", " ").replace("\n", "<br>")
        if card.hint:
            front_clean += f" <small style='color: gray;'>[Hint: {card.hint}]</small>"
        tag_clean = card.category_tag.replace(" ", "_")
        lines.append(f"{front_clean}\t{back_clean}\t{tag_clean}")
    return "\n".join(lines)
