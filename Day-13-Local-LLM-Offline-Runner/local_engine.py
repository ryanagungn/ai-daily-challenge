"""
Day 13: Local LLM Offline Runner
Engine module for local AI inference (Ollama, LM Studio, llama.cpp, LocalAI)
with live streaming and tokens/sec benchmark metrics.
"""

import time
import json
import requests
from typing import Generator, List, Dict, Any, Optional, Tuple
from dataclasses import dataclass, field


@dataclass
class GenerationMetrics:
    """Metrik performa inferensi lokal secara real-time."""
    total_tokens: int = 0
    prompt_tokens: int = 0
    eval_tokens: int = 0
    total_duration_sec: float = 0.0
    ttft_sec: float = 0.0  # Time to First Token
    tokens_per_sec: float = 0.0
    model_name: str = ""
    is_simulated: bool = False

    def to_dict(self) -> Dict[str, Any]:
        return {
            "total_tokens": self.total_tokens,
            "prompt_tokens": self.prompt_tokens,
            "eval_tokens": self.eval_tokens,
            "total_duration_sec": round(self.total_duration_sec, 3),
            "ttft_sec": round(self.ttft_sec, 3),
            "tokens_per_sec": round(self.tokens_per_sec, 1),
            "model_name": self.model_name,
            "is_simulated": self.is_simulated,
        }


@dataclass
class LocalModelInfo:
    """Informasi model lokal yang terpasang."""
    name: str
    size_gb: float = 0.0
    family: str = "unknown"
    parameter_size: str = ""
    quantization_level: str = ""
    modified_at: str = ""


@dataclass
class ServerStatus:
    """Status koneksi ke local LLM daemon."""
    connected: bool
    server_type: str  # 'ollama', 'openai_compatible', 'simulated'
    url: str
    models: List[LocalModelInfo] = field(default_factory=list)
    error_message: Optional[str] = None

    @property
    def model_names(self) -> List[str]:
        return [m.name for m in self.models]


class LocalLLMEngine:
    """
    Engine untuk mengontrol inferensi LLM lokal (Ollama / LM Studio / Llama.cpp)
    dilengkapi fallback simulasi offline yang realistis jika daemon belum aktif.
    """

    DEFAULT_OLLAMA_URL = "http://localhost:11434"
    DEFAULT_LMSTUDIO_URL = "http://localhost:1234/v1"

    SIMULATED_MODELS = [
        LocalModelInfo(
            name="llama3.2:1b (Simulated)",
            size_gb=1.3,
            family="llama",
            parameter_size="1.3B",
            quantization_level="Q4_K_M"
        ),
        LocalModelInfo(
            name="deepseek-r1:1.5b (Simulated)",
            size_gb=1.1,
            family="deepseek",
            parameter_size="1.5B",
            quantization_level="Q4_K_M"
        ),
        LocalModelInfo(
            name="mistral:7b (Simulated)",
            size_gb=4.1,
            family="mistral",
            parameter_size="7.2B",
            quantization_level="Q4_0"
        ),
    ]

    def __init__(self, base_url: str = DEFAULT_OLLAMA_URL, timeout: float = 3.0):
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout

    def check_health(self) -> ServerStatus:
        """
        Cek apakah local daemon (Ollama atau OpenAI-compatible) aktif dan ambil daftar model.
        """
        # 1. Coba periksa Ollama API (/api/tags)
        try:
            ollama_url = f"{self.base_url}/api/tags"
            resp = requests.get(ollama_url, timeout=self.timeout)
            if resp.status_code == 200:
                data = resp.json()
                raw_models = data.get("models", [])
                models = []
                for m in raw_models:
                    size_bytes = m.get("size", 0)
                    size_gb = round(size_bytes / (1024 ** 3), 2)
                    details = m.get("details", {})
                    models.append(LocalModelInfo(
                        name=m.get("name", "unknown"),
                        size_gb=size_gb,
                        family=details.get("family", "llama"),
                        parameter_size=details.get("parameter_size", ""),
                        quantization_level=details.get("quantization_level", ""),
                        modified_at=m.get("modified_at", "")[:10]
                    ))
                
                # Jika Ollama aktif tapi belum ada model yang di-pull
                if not models:
                    models = [
                        LocalModelInfo(
                            name="(Belum ada model terpasang - Jalankan 'ollama pull llama3.2:1b')",
                            size_gb=0.0
                        )
                    ]

                return ServerStatus(
                    connected=True,
                    server_type="ollama",
                    url=self.base_url,
                    models=models
                )
        except requests.exceptions.RequestException:
            pass

        # 2. Coba periksa OpenAI-compatible endpoint (/v1/models)
        try:
            openai_url = f"{self.base_url}/v1/models"
            resp = requests.get(openai_url, timeout=self.timeout)
            if resp.status_code == 200:
                data = resp.json()
                raw_models = data.get("data", [])
                models = [
                    LocalModelInfo(
                        name=m.get("id", "local-model"),
                        size_gb=0.0,
                        family="openai-compatible"
                    )
                    for m in raw_models
                ]
                return ServerStatus(
                    connected=True,
                    server_type="openai_compatible",
                    url=self.base_url,
                    models=models
                )
        except requests.exceptions.RequestException:
            pass

        # 3. Jika offline, kembalikan status simulasi yang informatif
        return ServerStatus(
            connected=False,
            server_type="simulated",
            url=self.base_url,
            models=self.SIMULATED_MODELS,
            error_message=(
                f"Koneksi ke local LLM daemon di '{self.base_url}' tidak dapat dijangkau.\n"
                "Mode Simulasi Offline diaktifkan otomatis agar aplikasi tetap dapat dicoba.\n"
                "Untuk menggunakan model fisik lokal, jalankan perintah: 'ollama serve' di terminal."
            )
        )

    def stream_chat(
        self,
        model: str,
        messages: List[Dict[str, str]],
        system_prompt: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 1024,
        force_simulated: bool = False
    ) -> Generator[Tuple[str, Optional[GenerationMetrics]], None, None]:
        """
        Streaming chat response generator token-by-token.
        Menghasilkan tuple: (chunk_text, final_metrics_or_None).
        Pada yield terakhir, final_metrics berisi statistik performa inferensi.
        """
        status = self.check_health()
        
        if force_simulated or not status.connected:
            yield from self._stream_simulated(model, messages)
            return

        if status.server_type == "ollama":
            yield from self._stream_ollama(model, messages, system_prompt, temperature)
        elif status.server_type == "openai_compatible":
            yield from self._stream_openai_compatible(model, messages, system_prompt, temperature, max_tokens)
        else:
            yield from self._stream_simulated(model, messages)

    def _stream_ollama(
        self,
        model: str,
        messages: List[Dict[str, str]],
        system_prompt: Optional[str] = None,
        temperature: float = 0.7
    ) -> Generator[Tuple[str, Optional[GenerationMetrics]], None, None]:
        """Streaming dari Ollama API (/api/chat)."""
        payload_messages = []
        if system_prompt:
            payload_messages.append({"role": "system", "content": system_prompt})
        payload_messages.extend(messages)

        payload = {
            "model": model,
            "messages": payload_messages,
            "options": {
                "temperature": temperature,
            },
            "stream": True
        }

        url = f"{self.base_url}/api/chat"
        start_time = time.perf_counter()
        first_token_time = None
        total_chunks = 0
        total_chars = 0
        final_meta = {}

        try:
            with requests.post(url, json=payload, stream=True, timeout=120) as resp:
                resp.raise_for_status()
                for line in resp.iter_lines(decode_unicode=True):
                    if not line:
                        continue
                    try:
                        data = json.loads(line)
                        message = data.get("message", {})
                        chunk = message.get("content", "")
                        
                        if chunk:
                            if first_token_time is None:
                                first_token_time = time.perf_counter()
                            total_chunks += 1
                            total_chars += len(chunk)
                            yield chunk, None

                        if data.get("done", False):
                            final_meta = data
                    except json.JSONDecodeError:
                        continue

            total_duration = time.perf_counter() - start_time
            ttft = (first_token_time - start_time) if first_token_time else total_duration

            # Ekstrak data eval dari metadata Ollama jika ada
            eval_count = final_meta.get("eval_count", total_chunks)
            prompt_eval_count = final_meta.get("prompt_eval_count", 0)
            eval_duration_ns = final_meta.get("eval_duration", 0)

            if eval_duration_ns > 0:
                eval_duration_sec = eval_duration_ns / 1e9
                tps = eval_count / eval_duration_sec if eval_duration_sec > 0 else 0.0
            else:
                generation_duration = (total_duration - ttft) if (total_duration - ttft) > 0 else total_duration
                tps = eval_count / generation_duration if generation_duration > 0 else 0.0

            metrics = GenerationMetrics(
                total_tokens=eval_count + prompt_eval_count,
                prompt_tokens=prompt_eval_count,
                eval_tokens=eval_count,
                total_duration_sec=total_duration,
                ttft_sec=ttft,
                tokens_per_sec=tps,
                model_name=model,
                is_simulated=False
            )
            yield "", metrics

        except Exception as e:
            yield f"\n[Error saat inferensi Ollama: {str(e)}]\n", None

    def _stream_openai_compatible(
        self,
        model: str,
        messages: List[Dict[str, str]],
        system_prompt: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 1024
    ) -> Generator[Tuple[str, Optional[GenerationMetrics]], None, None]:
        """Streaming dari OpenAI-compatible API (/v1/chat/completions)."""
        payload_messages = []
        if system_prompt:
            payload_messages.append({"role": "system", "content": system_prompt})
        payload_messages.extend(messages)

        payload = {
            "model": model,
            "messages": payload_messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
            "stream": True
        }

        url = f"{self.base_url}/v1/chat/completions"
        start_time = time.perf_counter()
        first_token_time = None
        eval_tokens = 0

        try:
            with requests.post(url, json=payload, stream=True, timeout=120) as resp:
                resp.raise_for_status()
                for line in resp.iter_lines(decode_unicode=True):
                    if not line or not line.startswith("data: "):
                        continue
                    line_data = line[6:].strip()
                    if line_data == "[DONE]":
                        break
                    try:
                        data = json.loads(line_data)
                        delta = data.get("choices", [{}])[0].get("delta", {})
                        chunk = delta.get("content", "")
                        if chunk:
                            if first_token_time is None:
                                first_token_time = time.perf_counter()
                            eval_tokens += 1
                            yield chunk, None
                    except json.JSONDecodeError:
                        continue

            total_duration = time.perf_counter() - start_time
            ttft = (first_token_time - start_time) if first_token_time else total_duration
            gen_duration = (total_duration - ttft) if (total_duration - ttft) > 0 else total_duration
            tps = eval_tokens / gen_duration if gen_duration > 0 else 0.0

            metrics = GenerationMetrics(
                total_tokens=eval_tokens,
                eval_tokens=eval_tokens,
                total_duration_sec=total_duration,
                ttft_sec=ttft,
                tokens_per_sec=tps,
                model_name=model,
                is_simulated=False
            )
            yield "", metrics

        except Exception as e:
            yield f"\n[Error saat inferensi OpenAI-compatible: {str(e)}]\n", None

    def _stream_simulated(
        self,
        model: str,
        messages: List[Dict[str, str]]
    ) -> Generator[Tuple[str, Optional[GenerationMetrics]], None, None]:
        """
        Simulasi inferensi offline yang cerdas, cepat, dan realistis.
        Membantu pengguna memahami keuntungan local LLM dan cara setup tanpa error.
        """
        start_time = time.perf_counter()
        time.sleep(0.12)  # Simulasikan latency TTFT perangkat lokal (VRAM/RAM loading)
        first_token_time = time.perf_counter()

        last_user_msg = ""
        for m in reversed(messages):
            if m.get("role") == "user":
                last_user_msg = m.get("content", "").strip().lower()
                break

        # Jawaban simulasi cerdas berbasis konteks
        if "halo" in last_user_msg or "hai" in last_user_msg:
            full_response = (
                f"Halo! Saya adalah **{model}** yang berjalan di mode **Local AI Inference Engine**.\n\n"
                "Keuntungan utama menjalankan LLM secara lokal:\n"
                "1. 🔒 **100% Privasi & Zero Telemetry**: Data Anda tidak pernah dikirim ke server cloud mana pun.\n"
                "2. 💸 **Bebas Biaya Token API**: Anda dapat melakukan inferensi jutaan prompt tanpa biaya langganan.\n"
                "3. ⚡ **Offline Resilience**: Dapat beroperasi penuh di kapal laut, hutan, atau bunker tanpa koneksi internet!"
            )
        elif "ollama" in last_user_msg or "install" in last_user_msg or "setup" in last_user_msg:
            full_response = (
                "Berikut panduan cepat menjalankan model AI lokal dengan **Ollama** di Windows/Linux/Mac:\n\n"
                "### 1. Download & Instal Ollama\n"
                "Kunjungi situs resmi [ollama.com](https://ollama.com) dan download installer.\n\n"
                "### 2. Jalankan Daemon Server\n"
                "Buka terminal atau Command Prompt dan jalankan:\n"
                "```bash\nollama serve\n```\n\n"
                "### 3. Unduh Model Pilihan Anda\n"
                "Untuk RAM/GPU ringan (laptop standar):\n"
                "```bash\nollama pull llama3.2:1b\nollama pull deepseek-r1:1.5b\n```\n"
                "Untuk GPU 8GB+ VRAM:\n"
                "```bash\nollama pull mistral:7b\nollama pull llama3.1:8b\n```\n\n"
                "Setelah model terunduh, refresh aplikasi ini untuk langsung menggunakannya secara fisik!"
            )
        elif "transformer" in last_user_msg:
            full_response = (
                "**Arsitektur Transformer** diperkenalkan oleh Vaswani et al. (2017) melalui paper monumental "
                "*'Attention Is All You Need'*. Inti kekuatannya terletak pada mekanisme **Multi-Head Self-Attention**, "
                "yang memungkinkan model memproses seluruh token dalam kalimat secara paralel tanpa batasan sequential seperti LSTM/RNN.\n\n"
                "Arsitektur ini terdiri dari dua blok utama: **Encoder** (memahami representasi kontekstual masukan) "
                "dan **Decoder** (menghasilkan token keluaran secara autoregresif). Model modern seperti LLaMA, GPT, "
                "dan Mistral menggunakan varian *Decoder-Only* yang dioptimasi dengan FlashAttention dan RoPE (Rotary Position Embeddings).\n\n"
                "Dengan teknik **Kuantisasi GGUF (Q4_K_M)**, bobot model 16-bit dapat dikompresi menjadi 4-bit, sehingga "
                "arsitektur Transformer berkapasitas 7 miliar parameter dapat dieksekusi mulus pada laptop berspesifikasi 8GB RAM!"
            )
        else:
            full_response = (
                f"Saya menerima masukan Anda: *\"{last_user_msg[:60]}...\"*\n\n"
                f"Ini adalah respons dari **{model}** melalui **Local Offline Inference Engine**.\n\n"
                "### Keamanan & Data Sovereignty\n"
                "Setiap karakter dalam pesan ini diproses secara lokal di CPU/GPU lokal mesin Anda. "
                "Tidak ada log yang dikirim ke server pihak ketiga, menjaga kerahasiaan data internal perusahaan, "
                "rahasia dagang, atau dokumen medis sensitif Anda.\n\n"
                "**Tips Optimasi Hardware Lokal:**\n"
                "- **VRAM GPU Dedicated (Nvidia CUDA/Apple Silicon Metal)**: Memberikan kecepatan tertinggi (~40-90 tokens/detik).\n"
                "- **Kuantisasi 4-bit (Q4)**: Menghemat hingga 70% memori tanpa penurunan akurasi penalaran yang signifikan.\n"
                "- **Context Window Management**: Menjaga efisiensi pemakaian KV Cache saat percakapan panjang."
            )

        # Simulasikan streaming token dengan kecepatan lokal (~30 tokens/sec)
        words = full_response.split(" ")
        token_count = 0

        for i, word in enumerate(words):
            chunk = word + (" " if i < len(words) - 1 else "")
            token_count += 1
            time.sleep(0.025)  # ~40 tokens/sec simulation speed
            yield chunk, None

        total_duration = time.perf_counter() - start_time
        ttft = first_token_time - start_time
        gen_duration = total_duration - ttft
        tps = token_count / gen_duration if gen_duration > 0 else 35.0

        metrics = GenerationMetrics(
            total_tokens=token_count + 15,
            prompt_tokens=15,
            eval_tokens=token_count,
            total_duration_sec=total_duration,
            ttft_sec=ttft,
            tokens_per_sec=tps,
            model_name=model,
            is_simulated=True
        )
        yield "", metrics

    def run_benchmark(
        self,
        model: str,
        benchmark_prompt: str = "Jelaskan konsep Kuantisasi 4-bit pada model AI lokal dalam 2 paragraf padat.",
        system_prompt: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Menjalankan benchmark inferensi lokal standar untuk mengukur TTFT dan throughput (tokens/sec).
        """
        messages = [{"role": "user", "content": benchmark_prompt}]
        full_text = ""
        final_metrics: Optional[GenerationMetrics] = None

        start = time.perf_counter()
        for chunk, metrics in self.stream_chat(model, messages, system_prompt=system_prompt):
            if chunk:
                full_text += chunk
            if metrics:
                final_metrics = metrics

        total_wall_time = time.perf_counter() - start

        if final_metrics is None:
            final_metrics = GenerationMetrics(
                total_tokens=len(full_text.split()),
                eval_tokens=len(full_text.split()),
                total_duration_sec=total_wall_time,
                ttft_sec=0.1,
                tokens_per_sec=len(full_text.split()) / total_wall_time if total_wall_time > 0 else 0.0,
                model_name=model
            )

        return {
            "model": model,
            "prompt": benchmark_prompt,
            "output_preview": full_text[:180] + ("..." if len(full_text) > 180 else ""),
            "metrics": final_metrics.to_dict()
        }
