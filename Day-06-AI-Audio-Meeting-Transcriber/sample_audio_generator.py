"""
Day 06 - Sample Audio & Meeting Generator
Menghasilkan file audio WAV sintetis dan file catatan meeting contoh untuk pengujian.
"""

import math
import wave
import struct
from pathlib import Path

OUTPUT_DIR = Path(__file__).parent

SAMPLE_TRANSCRIPT = """
[00:00] Budi Santoso (Product Lead): Selamat pagi semuanya. Terima kasih sudah hadir di Sprint Planning & Quarterly Review Q4 kita hari ini. Agenda utama kita adalah evaluasi rilis fitur AI Text Analyzer dan persiapan arsitektur backend untuk integrasi Vector Database di sprint berikutnya.

[00:45] Siti Rahmawati (Lead Backend Engineer): Pagi Mas Budi. Dari sisi backend, performa API saat ini cukup stabil dengan latency rata-rata 350ms. Namun, untuk integrasi Vector DB, tim kami merekomendasikan menggunakan ChromaDB untuk tahap local testing, dan beralih ke Qdrant atau Pinecone saat production deployment di bulan depan.

[01:30] Ahmad Hidayat (DevOps & Security): Setuju dengan Mbak Siti. Dari sisi security dan compliance, kita perlu memastikan API Key OpenAI dan Gemini tersimpan aman di GCP Secret Manager atau AWS Secrets Manager, bukan di environment variable statis di container server.

[02:10] Budi Santoso: Bagus sekali. Jadi keputusannya:
1. Siti akan memimpin implementasi POC Vector DB menggunakan ChromaDB sampai hari Jumat ini.
2. Ahmad akan setup Secret Manager dan pipeline CI/CD di GitHub Actions paling lambat tanggal 15 September.
3. Saya akan menyusun dokumen PRD untuk fitur Multimodal Vision dan mempresentasikannya ke stakeholder minggu depan.

[02:50] Siti Rahmawati: Siap Mas Budi, nanti estimasi kebutuhan resource server akan saya share di Slack channel #ai-engineering.

[03:10] Budi Santoso: Baik, meeting kita sudahi sampai di sini. Semangat semuanya dan selamat bekerja!
"""

def generate_sample_meeting_files():
    # 1. Simpan Transcript Text
    text_path = OUTPUT_DIR / "sample_meeting_transcript.txt"
    text_path.write_text(SAMPLE_TRANSCRIPT.strip(), encoding="utf-8")
    print(f"Sample meeting transcript saved to {text_path}")

    # 2. Buat file audio WAV sintetis (Chime & Audio carrier waves)
    wav_path = OUTPUT_DIR / "sample_meeting_chime.wav"
    sample_rate = 44100
    duration = 3.0  # 3 detik tone chime
    freqs = [440.0, 554.37, 659.25, 880.0]  # A Major chord chime

    num_samples = int(sample_rate * duration)
    with wave.open(str(wav_path), "w") as wav_file:
        wav_file.setnchannels(1)  # Mono
        wav_file.setsampwidth(2)  # 16-bit
        wav_file.setframerate(sample_rate)

        for i in range(num_samples):
            t = float(i) / sample_rate
            envelope = math.exp(-2.0 * t)  # Decay
            val = sum(math.sin(2.0 * math.pi * f * t) for f in freqs) / len(freqs)
            sample = int(val * envelope * 32767.0 * 0.8)
            sample = max(-32768, min(32767, sample))
            wav_file.writeframes(struct.pack("<h", sample))

    print(f"Sample WAV audio saved to {wav_path}")

if __name__ == "__main__":
    generate_sample_meeting_files()
