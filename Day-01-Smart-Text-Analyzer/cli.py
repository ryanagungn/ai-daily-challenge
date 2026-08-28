"""
Day 01 - Smart AI Text Analyzer (CLI Version)
Menjalankan analisis teks langsung dari terminal dengan antarmuka modern (Rich).
"""

import sys
import argparse
from pathlib import Path
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.markdown import Markdown

# Pastikan path modul terbaca
sys.path.append(str(Path(__file__).parent))
from analyzer import analyze_text, AnalysisResult

console = Console()

def display_result(result: AnalysisResult):
    console.print()
    console.rule("[bold cyan]📊 HASIL ANALISIS TEKS AI[/bold cyan]")
    console.print()

    # Meta Info Table
    table = Table(show_header=True, header_style="bold magenta", expand=True)
    table.add_column("Atribut", style="dim", width=22)
    table.add_column("Detail", style="bold")

    sentiment_color = {
        "POSITIVE": "green",
        "NEGATIVE": "red",
        "NEUTRAL": "yellow"
    }.get(result.sentiment.sentiment.upper(), "white")

    table.add_row("Bahasa Terdeteksi", result.detected_language)
    table.add_row("Jumlah Kata", f"{result.word_count} kata")
    table.add_row(
        "Sentimen",
        f"[{sentiment_color}]{result.sentiment.sentiment} (Skor: {result.sentiment.score:.2f})[/{sentiment_color}]"
    )
    table.add_row("Penjelasan Sentimen", result.sentiment.explanation)
    console.print(table)
    console.print()

    # Summary Panel
    console.print(Panel(
        result.summary,
        title="[bold green]📝 Ringkasan Intisari[/bold green]",
        border_style="green",
        padding=(1, 2)
    ))
    console.print()

    # Key Topics & Action Items
    topics_str = " • ".join([f"[bold cyan]#{t}[/bold cyan]" for t in result.key_topics])
    console.print(Panel(
        topics_str,
        title="[bold cyan]🏷️ Topik / Kata Kunci Utama[/bold cyan]",
        border_style="cyan"
    ))
    console.print()

    if result.action_items:
        actions_md = "\n".join([f"- {item}" for item in result.action_items])
        console.print(Panel(
            Markdown(actions_md),
            title="[bold yellow]⚡ Poin Tindakan / Rekomendasi[/bold yellow]",
            border_style="yellow"
        ))
        console.print()

def main():
    parser = argparse.ArgumentParser(description="AI Smart Text & Sentiment Analyzer CLI")
    parser.add_argument("-f", "--file", help="Path ke file teks (.txt / .md) yang ingin dianalisis")
    parser.add_argument("-t", "--text", help="Teks langsung yang ingin dianalisis")
    parser.add_argument("-m", "--model", default="gemini-2.5-flash", help="Nama model Gemini (default: gemini-2.5-flash)")
    
    args = parser.parse_args()

    content = ""
    if args.file:
        file_path = Path(args.file)
        if not file_path.exists():
            console.print(f"[bold red]Error:[/bold red] File '{args.file}' tidak ditemukan!")
            sys.exit(1)
        content = file_path.read_text(encoding="utf-8")
    elif args.text:
        content = args.text
    else:
        console.print(Panel.fit(
            "[bold cyan]🤖 AI Smart Text & Sentiment Analyzer (Day 01)[/bold cyan]\n"
            "[dim]Masukkan atau tempel teks Anda di bawah ini, lalu tekan Ctrl+Z (Windows) atau Ctrl+D (Mac/Linux) lalu Enter:[/dim]",
            border_style="cyan"
        ))
        try:
            content = sys.stdin.read()
        except KeyboardInterrupt:
            console.print("\n[yellow]Operasi dibatalkan.[/yellow]")
            sys.exit(0)

    if not content.strip():
        console.print("[bold red]Teks input kosong. Tidak ada yang dianalisis.[/bold red]")
        sys.exit(1)

    with console.status("[bold green]Sedang menganalisis teks dengan Gemini AI...[/bold green]", spinner="dots"):
        try:
            result = analyze_text(content, model_name=args.model)
            display_result(result)
        except Exception as e:
            console.print(f"\n[bold red]Gagal melakukan analisis:[/bold red] {e}")
            sys.exit(1)

if __name__ == "__main__":
    main()
