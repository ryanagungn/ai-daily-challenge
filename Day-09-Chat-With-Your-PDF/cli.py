"""
Day 09 - Chat with Your PDF (CLI Version)
Tanya jawab interaktif dengan dokumen PDF melalui terminal dengan rujukan sitasi chunk.
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
from rag_engine import PDFRAGSession, RAGAnswer

console = Console()

def display_answer(q: str, answer: RAGAnswer):
    console.print()
    console.rule("[bold cyan]🤖 JAWABAN RAG BERDASARKAN DOKUMEN[/bold cyan]")
    console.print()

    # Answer panel
    conf_color = "green" if answer.confidence_rating == "High" else "yellow" if answer.confidence_rating == "Medium" else "red"
    title_meta = f"[bold green]Jawaban AI[/bold green] (Keyakinan: [{conf_color}]{answer.confidence_rating}[/{conf_color}])"

    console.print(Panel(
        Markdown(answer.answer),
        title=title_meta,
        border_style="green",
        padding=(1, 2)
    ))
    console.print()

    # Citations table
    if answer.citations:
        table = Table(title="📑 Rujukan Sitasi Konteks (Grounding)", show_header=True, header_style="bold magenta", expand=True)
        table.add_column("Chunk", width=8, justify="center")
        table.add_column("Halaman", width=10, justify="center")
        table.add_column("Relevansi", width=12, justify="center")
        table.add_column("Cuplikan Konteks", style="dim")

        for c in answer.citations:
            rel_pct = f"{c.similarity_score * 100:.1f}%"
            table.add_row(f"#{c.chunk_id}", f"Hal {c.page_number}", f"[cyan]{rel_pct}[/cyan]", c.snippet)

        console.print(table)
        console.print()

def main():
    parser = argparse.ArgumentParser(description="Chat with Your PDF CLI (RAG)")
    parser.add_argument("-f", "--file", help="Path ke file PDF atau TXT")
    parser.add_argument("-q", "--question", help="Pertanyaan langsung")
    parser.add_argument("-k", "--top-k", type=int, default=3, help="Jumlah chunk relevan yang diambil (default: 3)")
    parser.add_argument("-m", "--model", default="gemini-2.5-flash", help="Model Gemini (default: gemini-2.5-flash)")

    args = parser.parse_args()

    # Default ke sample PDF jika ada
    doc_path = None
    if args.file:
        doc_path = Path(args.file)
    else:
        sample_pdf = Path(__file__).parent / "sample_ai_playbook.pdf"
        if sample_pdf.exists():
            console.print(f"[yellow]Tidak ada file dokumen yang dispesifikasikan. Menggunakan sample default:[/yellow] [cyan]{sample_pdf.name}[/cyan]\n")
            doc_path = sample_pdf
        else:
            console.print("[bold red]Error:[/bold red] Silakan berikan path dokumen dengan `-f <file.pdf>`")
            sys.exit(1)

    if not doc_path.exists():
        console.print(f"[bold red]Error:[/bold red] File '{doc_path}' tidak ditemukan!")
        sys.exit(1)

    session = PDFRAGSession(chunk_size=550, chunk_overlap=80)

    with console.status(f"[bold green]Memecah teks ({doc_path.name}) & meng-embed vektor dengan Gemini...[/bold green]", spinner="dots"):
        try:
            total_chunks = session.load_and_index_document(doc_path, doc_name=doc_path.name)
            console.print(f"[bold green]✓ Dokumen berhasil diindeks:[/bold green] [cyan]{total_chunks}[/cyan] chunks siap ditanyakan.\n")
        except Exception as e:
            console.print(f"[bold red]Gagal membaca dokumen:[/bold red] {e}")
            sys.exit(1)

    # Mode 1 Pertanyaan
    if args.question:
        with console.status("[bold green]Mencari konteks & menghasilkan jawaban...[/bold green]", spinner="dots"):
            ans = session.ask(args.question, top_k=args.top_k, model_name=args.model)
        display_answer(args.question, ans)
        return

    # Mode Interaktif Chat REPL
    console.print(Panel.fit(
        f"[bold cyan]💬 Chat with Your PDF (Day 09)[/bold cyan]\n"
        f"[white]Dokumen aktif:[/white] [yellow]{doc_path.name}[/yellow]\n"
        "[dim]Ketik pertanyaan Anda tentang isi dokumen (atau 'exit' untuk keluar):[/dim]",
        border_style="cyan"
    ))

    while True:
        try:
            console.print("[bold yellow]Tanya PDF > [/bold yellow]", end="")
            user_q = input().strip()

            if not user_q:
                continue
            if user_q.lower() in ["exit", "quit", "q"]:
                console.print("[yellow]Sampai jumpa![/yellow]")
                break

            with console.status("[bold green]Mencari rujukan dokumen & menjawab...[/bold green]", spinner="dots"):
                ans = session.ask(user_q, top_k=args.top_k, model_name=args.model)
            display_answer(user_q, ans)

        except KeyboardInterrupt:
            console.print("\n[yellow]Sesi dihentikan.[/yellow]")
            break
        except Exception as e:
            console.print(f"[bold red]Error:[/bold red] {e}\n")

if __name__ == "__main__":
    main()
