"""
Day 10 - Technical Documentation & Codebase Q&A (CLI Version)
Mencari dan menanyakan dokumentasi arsitektur sistem langsung dari terminal.
"""

import sys
import argparse
from pathlib import Path
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.syntax import Syntax
from rich.markdown import Markdown

# Pastikan modul internal terbaca
sys.path.append(str(Path(__file__).parent))
from docs_engine import TechnicalDocsEngine, TechnicalAnswer

console = Console()

def display_answer(q: str, ans: TechnicalAnswer):
    console.print()
    console.rule("[bold cyan]🛠️ JAWABAN TEKNIS DOKUMENTASI[/bold cyan]")
    console.print()

    # Answer Panel
    console.print(Panel(
        Markdown(ans.direct_answer),
        title="[bold green]Rekomendasi Arsitektur & Penjelasan[/bold green]",
        border_style="green",
        padding=(1, 2)
    ))
    console.print()

    # Citations Table
    if ans.referenced_sections:
        table = Table(title="📑 Bagian & File Dokumentasi yang Dirujuk", show_header=True, header_style="bold magenta", expand=True)
        table.add_column("File", width=22, style="bold cyan")
        table.add_column("Bab / Header Breadcrumb", width=35, style="yellow")
        table.add_column("Relevansi", width=12, justify="center")
        table.add_column("Cuplikan Konten", style="dim")

        for c in ans.referenced_sections:
            table.add_row(c.file_name, c.header_breadcrumb, f"[bold green]{c.relevance_pct}[/bold green]", c.snippet)

        console.print(table)
        console.print()

    # Follow-up questions
    if ans.suggested_follow_up_questions:
        q_list = "\n".join([f"- 💡 {fq}" for fq in ans.suggested_follow_up_questions])
        console.print(Panel(Markdown(q_list), title="[bold yellow]Saran Pertanyaan Lanjutan[/bold yellow]", border_style="yellow"))
        console.print()

def main():
    parser = argparse.ArgumentParser(description="Technical Documentation Q&A Engine CLI")
    parser.add_argument("-d", "--docs-dir", help="Path ke folder dokumentasi (default: sample_docs)")
    parser.add_argument("-q", "--question", help="Pertanyaan teknis langsung")
    parser.add_argument("--reindex", action="store_true", help="Paksa pembuatan ulang vector embeddings")
    parser.add_argument("--list-sections", action="store_true", help="Tampilkan semua bab dokumentasi yang terindeks")
    parser.add_argument("-k", "--top-k", type=int, default=3, help="Jumlah sections rujukan (default: 3)")
    parser.add_argument("-m", "--model", default="gemini-2.5-flash", help="Model Gemini (default: gemini-2.5-flash)")

    args = parser.parse_args()

    base_dir = Path(args.docs_dir) if args.docs_dir else Path(__file__).parent / "sample_docs"
    if not base_dir.exists():
        console.print(f"[bold red]Error:[/bold red] Folder '{base_dir}' tidak ditemukan!")
        sys.exit(1)

    with console.status(f"[bold green]Memuat dan mengindeks dokumentasi di '{base_dir.name}'...[/bold green]", spinner="dots"):
        engine = TechnicalDocsEngine(base_dir)
        if args.reindex:
            engine.load_or_index_docs(force_reindex=True)

    if args.list_sections:
        table = Table(title=f"📚 Bab Dokumentasi Terindeks ({len(engine.chunks)} Bagian)", show_header=True, header_style="bold cyan", expand=True)
        table.add_column("ID", width=6, justify="center")
        table.add_column("File", width=22, style="yellow")
        table.add_column("Hierarki Header (Breadcrumb)", style="bold white")
        table.add_column("Panjang Karakter", width=16, justify="right")

        for ch in engine.chunks:
            table.add_row(f"#{ch.chunk_id}", ch.file_name, ch.header_breadcrumb, f"{ch.char_count} char")

        console.print(table)
        return

    if args.question:
        with console.status("[bold green]Mencari rujukan bab & menyusun jawaban arsitektur...[/bold green]", spinner="dots"):
            ans = engine.ask_technical_question(args.question, top_k=args.top_k, model_name=args.model)
        display_answer(args.question, ans)
        return

    # Interactive REPL
    console.print(Panel.fit(
        "[bold cyan]📚 Technical Documentation & Codebase Q&A (Day 10)[/bold cyan]\n"
        f"[dim]Folder dokumentasi: {base_dir.name} ({len(engine.chunks)} sections terindeks)[/dim]\n"
        "[yellow]Tanyakan arsitektur sistem, spesifikasi API, strategi database, atau konfigurasi deployment.[/yellow]\n"
        "[dim]Ketik 'exit' untuk keluar, atau 'list' untuk melihat semua bab.[/dim]",
        border_style="cyan"
    ))

    while True:
        try:
            console.print("[bold yellow]Tanya Docs > [/bold yellow]", end="")
            user_q = input().strip()

            if not user_q:
                continue
            if user_q.lower() in ["exit", "quit", "q"]:
                console.print("[yellow]Sampai jumpa![/yellow]")
                break
            if user_q.lower() == "list":
                for ch in engine.chunks:
                    console.print(f"• [cyan]{ch.file_name}[/cyan] ➔ {ch.header_breadcrumb}")
                continue

            with console.status("[bold green]Menganalisis dokumentasi...[/bold green]", spinner="dots"):
                ans = engine.ask_technical_question(user_q, top_k=args.top_k, model_name=args.model)
            display_answer(user_q, ans)

        except KeyboardInterrupt:
            console.print("\n[yellow]Sesi dihentikan.[/yellow]")
            break
        except Exception as e:
            console.print(f"[bold red]Error:[/bold red] {e}\n")

if __name__ == "__main__":
    main()
