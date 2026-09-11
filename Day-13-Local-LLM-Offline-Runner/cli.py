"""
Day 13: Local LLM Offline Runner - Interactive CLI
Jalankan inferensi LLM lokal di terminal dengan streaming real-time & benchmark speed.
"""

import sys
import os
from typing import List, Dict

from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.markdown import Markdown
from rich.prompt import Prompt, Confirm
from rich.status import Status

# Import engine lokal
from local_engine import LocalLLMEngine, ServerStatus, GenerationMetrics

console = Console()


def display_header():
    """Tampilkan banner header Day 13."""
    console.print(
        Panel.fit(
            "[bold cyan]🤖 DAY 13: LOCAL LLM OFFLINE RUNNER[/bold cyan]\n"
            "[dim white]Privacy-First Local AI Inference Engine • Zero Cloud • Real-Time Token/s[/dim white]",
            border_style="cyan",
        )
    )


def display_server_status(status: ServerStatus):
    """Tampilkan status koneksi server lokal dan daftar model."""
    status_table = Table(show_header=False, box=None, padding=(0, 2))
    status_table.add_column("Key", style="bold yellow")
    status_table.add_column("Value")

    if status.connected:
        badge = f"[bold green]🟢 CONNECTED ({status.server_type.upper()})[/bold green]"
    else:
        badge = "[bold yellow]🟡 SIMULATED OFFLINE MODE (Local Daemon Inactive)[/bold yellow]"

    status_table.add_row("Server URL", f"[underline]{status.url}[/underline]")
    status_table.add_row("Status", badge)
    status_table.add_row("Tipe Backend", status.server_type.capitalize())
    status_table.add_row("Total Model", f"{len(status.models)} model terdeteksi")

    console.print(Panel(status_table, title="[bold]📡 Server Health Status[/bold]", border_style="green" if status.connected else "yellow"))

    if not status.connected and status.error_message:
        console.print(f"[dim yellow]💡 Catatan: {status.error_message.splitlines()[0]}[/dim yellow]")

    # Tampilkan tabel model
    model_table = Table(title="📦 Model AI yang Tersedia", border_style="blue", show_lines=True)
    model_table.add_column("#", style="dim", width=4)
    model_table.add_column("Nama Model", style="bold cyan")
    model_table.add_column("Keluarga", style="magenta")
    model_table.add_column("Parameter", style="green")
    model_table.add_column("Kuantisasi", style="yellow")
    model_table.add_column("Ukuran (GB)", justify="right", style="white")

    for idx, m in enumerate(status.models, 1):
        model_table.add_row(
            str(idx),
            m.name,
            m.family,
            m.parameter_size or "-",
            m.quantization_level or "-",
            f"{m.size_gb:.2f} GB" if m.size_gb > 0 else "-"
        )

    console.print(model_table)
    console.print()


def display_metrics_card(metrics: GenerationMetrics):
    """Tampilkan kartu metrik performa inferensi (tokens/s, latency, dsb)."""
    table = Table(title="⚡ Real-time Inference Metrics", border_style="bright_magenta", show_header=True)
    table.add_column("Kecepatan (Tokens/s)", justify="center", style="bold green")
    table.add_column("TTFT (Latency Awal)", justify="center", style="bold yellow")
    table.add_column("Total Tokens", justify="center", style="cyan")
    table.add_column("Durasi Total", justify="center", style="white")
    table.add_column("Mode", justify="center", style="dim")

    mode_badge = "[dim yellow]Simulated[/dim yellow]" if metrics.is_simulated else "[bold green]Physical Device[/bold green]"
    table.add_row(
        f"{metrics.tokens_per_sec:.1f} t/s",
        f"{metrics.ttft_sec * 1000:.0f} ms",
        f"{metrics.eval_tokens} tokens",
        f"{metrics.total_duration_sec:.2f} s",
        mode_badge
    )
    console.print(table)
    console.print()


def run_chat_session(engine: LocalLLMEngine, selected_model: str):
    """Sesi percakapan interaktif dengan streaming real-time di terminal."""
    console.print(
        Panel(
            f"[bold green]💬 Memulai Chat Interaktif dengan [cyan]{selected_model}[/cyan][/bold green]\n"
            "[dim]Ketik prompt Anda dan tekan Enter. Ketik 'exit' atau 'keluar' untuk kembali ke menu utama.[/dim]",
            border_style="green"
        )
    )

    history: List[Dict[str, str]] = []

    while True:
        try:
            user_input = Prompt.ask("\n[bold cyan]👤 Anda[/bold cyan]").strip()
        except (KeyboardInterrupt, EOFError):
            console.print("\n[yellow]Kembali ke menu...[/yellow]")
            break

        if not user_input:
            continue

        if user_input.lower() in ("exit", "keluar", "q"):
            console.print("[dim]Mengakhiri sesi chat...[/dim]")
            break

        history.append({"role": "user", "content": user_input})

        console.print(f"\n[bold green]🤖 {selected_model}:[/bold green]")
        
        full_response = ""
        final_metrics = None

        # Streaming langsung ke console
        for chunk, metrics in engine.stream_chat(selected_model, history):
            if chunk:
                console.print(chunk, end="")
                sys.stdout.flush()
                full_response += chunk
            if metrics:
                final_metrics = metrics

        console.print("\n")
        history.append({"role": "assistant", "content": full_response})

        if final_metrics:
            display_metrics_card(final_metrics)


def run_benchmark_suite(engine: LocalLLMEngine, selected_model: str):
    """Menjalankan benchmark throughput dan TTFT."""
    console.print(
        Panel(
            f"[bold magenta]⚡ Menjalankan Benchmark Inferensi: [cyan]{selected_model}[/cyan][/bold magenta]\n"
            "[dim]Menguji throughput token per detik dan waktu tanggap (TTFT)...[/dim]",
            border_style="magenta"
        )
    )

    benchmark_prompt = "Jelaskan perbedaan mendasar antara Cloud AI dan Local LLM dari aspek privasi, biaya, dan latensi dalam 2 paragraf padat."
    console.print(f"[bold yellow]Test Prompt:[/bold yellow] [dim]{benchmark_prompt}[/dim]\n")

    with Status("[bold cyan]Menghasilkan token inferensi...", spinner="dots"):
        result = engine.run_benchmark(selected_model, benchmark_prompt=benchmark_prompt)

    metrics = result["metrics"]
    console.print("[bold green]Hasil Preview Respons:[/bold green]")
    console.print(Panel(result["output_preview"], border_style="dim"))

    table = Table(title=f"📊 Benchmark Score: {selected_model}", border_style="cyan")
    table.add_column("Metrik Pengujian", style="bold white")
    table.add_column("Nilai Hasil", style="bold yellow")
    table.add_column("Keterangan", style="dim")

    table.add_row("Throughput Speed", f"{metrics['tokens_per_sec']} tokens/sec", "Kecepatan generasi kata per detik")
    table.add_row("Time to First Token (TTFT)", f"{metrics['ttft_sec'] * 1000:.1f} ms", "Waktu yang dibutuhkan sebelum token pertama muncul")
    table.add_row("Total Generation Duration", f"{metrics['total_duration_sec']} detik", "Waktu total respons selesai")
    table.add_row("Total Output Tokens", f"{metrics['eval_tokens']} tokens", "Jumlah token keluaran yang diproduksi")
    table.add_row("Inference Mode", "Simulated" if metrics['is_simulated'] else "Physical Hardware", "Daemon lokal vs Fallback")

    console.print(table)
    console.print()


def show_setup_guide():
    """Tampilkan panduan instalasi Ollama & Local AI."""
    guide = """
# 🛡️ Panduan Menjalankan Local AI Offline (Ollama)

### 1. Mengapa Menjalankan LLM Lokal?
* **100% Kerahasiaan Data (Privacy-First)**: Dokumen perusahaan, kode rahasia, atau data pribadi tidak dikirim ke internet.
* **Zero Cost**: Tidak ada tagihan token bulanan seperti cloud API.
* **Offline Operation**: Tetap bekerja tanpa koneksi internet sama sekali.

### 2. Langkah Instalasi Ollama:
1. Download installer resmi dari: **https://ollama.com**
2. Jalankan instalasi di Windows / Mac / Linux.
3. Buka Terminal / CMD baru dan ketik:
   ```bash
   ollama serve
   ```
4. Unduh model berbobot ringan (rekomendasi untuk laptop standar):
   ```bash
   ollama pull llama3.2:1b
   ollama pull deepseek-r1:1.5b
   ```
5. Untuk PC dengan GPU dedicated (Nvidia RTX / 8GB+ VRAM):
   ```bash
   ollama pull mistral:7b
   ollama pull llama3.1:8b
   ```

### 3. Integrasi Alternatif:
Aplikasi ini juga mendukung **LM Studio**, **Llama.cpp server**, atau **LocalAI** melalui OpenAI-compatible endpoint di port `1234` atau `8080`.
"""
    console.print(Markdown(guide))
    console.print()


def main():
    """Entry point utama CLI."""
    display_header()
    engine = LocalLLMEngine()

    while True:
        status = engine.check_health()
        display_server_status(status)

        console.print("[bold]Pilihan Tindakan:[/bold]")
        console.print("  [1] 💬 Mulai Chat Interaktif (Streaming)")
        console.print("  [2] ⚡ Uji Benchmark Kecepatan (Tokens/s & Latensi)")
        console.print("  [3] 🔄 Refresh / Ganti URL Server")
        console.print("  [4] 📖 Panduan Setup Ollama & Model Lokal")
        console.print("  [5] ❌ Keluar")

        choice = Prompt.ask("\n[bold cyan]Pilih menu (1-5)[/bold cyan]", choices=["1", "2", "3", "4", "5"], default="1")

        if choice == "1":
            # Pilih model
            model_names = status.model_names
            if not model_names:
                console.print("[red]Tidak ada model yang ditemukan.[/red]")
                continue
            
            console.print("\n[bold]Pilih Model:[/bold]")
            for i, name in enumerate(model_names, 1):
                console.print(f"  [{i}] {name}")
            
            idx_str = Prompt.ask("[cyan]Pilih nomor model[/cyan]", default="1")
            try:
                sel_idx = int(idx_str) - 1
                if 0 <= sel_idx < len(model_names):
                    chosen_model = model_names[sel_idx]
                else:
                    chosen_model = model_names[0]
            except ValueError:
                chosen_model = model_names[0]

            run_chat_session(engine, chosen_model)

        elif choice == "2":
            model_names = status.model_names
            chosen_model = model_names[0] if model_names else "llama3.2:1b"
            run_benchmark_suite(engine, chosen_model)

        elif choice == "3":
            new_url = Prompt.ask("[cyan]Masukkan URL server baru[/cyan]", default=engine.base_url)
            engine = LocalLLMEngine(base_url=new_url)
            console.print(f"[green]URL diubah ke {engine.base_url}[/green]")

        elif choice == "4":
            show_setup_guide()

        elif choice == "5":
            console.print("[bold cyan]Terima kasih telah menggunakan Local LLM Offline Runner![/bold cyan]")
            break


if __name__ == "__main__":
    main()
