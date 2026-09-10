"""
Day 12 - Live Web-Search Augmented AI (CLI Version)
Menjalankan pencarian web real-time dan sintesis jawaban (Perplexity-style) dari terminal.
"""

import sys
import argparse
from pathlib import Path
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.markdown import Markdown

# Pastikan modul internal terbaca
sys.path.append(str(Path(__file__).parent))
from synthesizer import synthesize_web_answer, PerplexityResponse

console = Console()

def display_perplexity_result(res: PerplexityResponse):
    console.print()
    console.rule(f"[bold cyan]🌐 MINI PERPLEXITY: '{res.query}'[/bold cyan]")
    console.print(f"[dim]⏱️ Waktu Pencarian: {res.search_latency_ms:.0f} ms | Total Latensi: {res.total_latency_ms:.0f} ms[/dim]\n")

    # 1. Sources Card
    if res.sources:
        table = Table(title="🔗 Sumber Web yang Dirujuk", show_header=True, header_style="bold magenta", expand=True)
        table.add_column("No", width=5, justify="center")
        table.add_column("Domain", width=20, style="bold cyan")
        table.add_column("Judul & Link URL", style="white")

        for s in res.sources:
            table.add_row(f"[{s.index}]", s.domain, f"[bold]{s.title}[/bold]\n[dim underline]{s.url}[/dim underline]")

        console.print(table)
        console.print()

    # 2. Synthesized Answer Panel
    console.print(Panel(
        Markdown(res.answer_markdown),
        title="[bold green]🧠 Sintesis Jawaban Terverifikasi (Footnote Citations)[/bold green]",
        border_style="green",
        padding=(1, 2)
    ))
    console.print()

    # 3. Related Questions
    if res.related_questions:
        q_text = "\n".join([f"- 💡 {q}" for q in res.related_questions])
        console.print(Panel(Markdown(q_text), title="[bold yellow]Pertanyaan Terkait[/bold yellow]", border_style="yellow"))
        console.print()

def main():
    parser = argparse.ArgumentParser(description="Live Web-Search Augmented AI CLI (Mini Perplexity)")
    parser.add_argument("-q", "--query", help="Pertanyaan yang membutuhkan data web terbaru")
    parser.add_argument("-n", "--num-sources", type=int, default=5, help="Jumlah sumber web yang dirayapi (default: 5)")
    parser.add_argument("-m", "--model", default="gemini-2.5-flash", help="Model Gemini (default: gemini-2.5-flash)")

    args = parser.parse_args()

    query_str = args.query
    if not query_str:
        console.print(Panel.fit(
            "[bold cyan]🌐 Mini Perplexity - Web Search Augmented AI (Day 12)[/bold cyan]\n"
            "[dim]Tanyakan topik apa pun yang membutuhkan pencarian web real-time & sitasi multi-sumber.[/dim]\n"
            "[yellow]Contoh: 'Berita teknologi terkini hari ini', 'Perkembangan model AI terbaru 2024'[/yellow]",
            border_style="cyan"
        ))
        try:
            query_str = input("Cari Web > ").strip()
        except KeyboardInterrupt:
            sys.exit(0)

    if not query_str:
        console.print("[bold red]Kueri pencarian tidak boleh kosong.[/bold red]")
        sys.exit(1)

    with console.status("[bold green]Merayapi web & mensintesis jawaban dengan Gemini...[/bold green]", spinner="dots"):
        try:
            res = synthesize_web_answer(query_str, max_search_results=args.num_sources, model_name=args.model)
            display_perplexity_result(res)
        except Exception as e:
            console.print(f"[bold red]Gagal melakukan sintesis web:[/bold red] {e}")

if __name__ == "__main__":
    main()
