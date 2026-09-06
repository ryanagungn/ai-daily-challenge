"""
Day 08 - Semantic Search Engine with Vector Embeddings (CLI Version)
Menjalankan pencarian semantik vektor dan komparasi vs keyword search langsung dari terminal.
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
from embeddings_engine import VectorDatabase, SearchResult

console = Console()

def display_search_results(query: str, results: list[SearchResult], mode: str = "Semantic Vector"):
    console.print()
    console.rule(f"[bold cyan]🔍 HASIL PENCARIAN ({mode}): '{query}'[/bold cyan]")
    console.print()

    if not results:
        console.print(Panel("[yellow]Tidak ada dokumen yang memenuhi ambang batas (threshold) kemiripan.[/yellow]", border_style="yellow"))
        return

    table = Table(show_header=True, header_style="bold magenta", expand=True)
    table.add_column("Rank", width=6, justify="center")
    table.add_column("Kemiripan", width=14, justify="center")
    table.add_column("Kategori", width=22, style="cyan")
    table.add_column("Judul & Cuplikan Konten", style="white")

    for idx, r in enumerate(results, 1):
        # Color based on score
        if r.match_type == "Semantic Vector":
            score_color = "bold green" if r.similarity_score >= 0.7 else "bold yellow" if r.similarity_score >= 0.5 else "blue"
            score_badge = f"[{score_color}]{r.similarity_percentage}[/{score_color}]"
        else:
            score_badge = f"[bold cyan]{r.similarity_percentage}[/bold cyan]"

        content_preview = r.content if len(r.content) <= 160 else r.content[:157] + "..."
        detail_str = f"[bold]{r.title}[/bold]\n[dim]{content_preview}[/dim]"

        table.add_row(f"#{idx}", score_badge, r.category, detail_str)

    console.print(table)
    console.print()

def display_all_docs(vdb: VectorDatabase):
    table = Table(title=f"📚 Knowledge Base Database ({len(vdb.documents)} Dokumen Terindeks)", show_header=True, header_style="bold cyan", expand=True)
    table.add_column("ID", width=8, justify="center")
    table.add_column("Kategori", width=22, style="yellow")
    table.add_column("Judul Dokumen", style="bold white")

    for doc in vdb.documents:
        table.add_row(doc["id"], doc["category"], doc["title"])

    console.print(table)
    console.print()

def main():
    parser = argparse.ArgumentParser(description="AI Semantic Search Engine CLI")
    parser.add_argument("-q", "--query", help="Kueri pencarian dalam bahasa manusia (misal: 'cara mencegah kebocoran data cloud')")
    parser.add_argument("-k", "--top-k", type=int, default=3, help="Jumlah hasil teratas (default: 3)")
    parser.add_argument("-t", "--threshold", type=float, default=0.35, help="Ambang batas cosine similarity (0.0 - 1.0, default: 0.35)")
    parser.add_argument("--compare", action="store_true", help="Bandingkan hasil Semantic Search vs Exact Keyword Search")
    parser.add_argument("--list-docs", action="store_true", help="Tampilkan semua dokumen dalam Knowledge Base")
    parser.add_argument("--add-title", help="Judul dokumen baru untuk di-indeks")
    parser.add_argument("--add-category", default="General", help="Kategori dokumen baru")
    parser.add_argument("--add-content", help="Isi konten dokumen baru")

    args = parser.parse_args()

    vdb = VectorDatabase()

    if args.list_docs:
        display_all_docs(vdb)
        return

    if args.add_title and args.add_content:
        with console.status("[bold green]Meng-embed dan menyimpan dokumen baru...[/bold green]", spinner="dots"):
            new_id = vdb.add_document(args.add_title, args.add_category, args.add_content)
        console.print(f"[bold green]✓ Dokumen berhasil diindeks:[/bold green] ID `{new_id}` - '{args.add_title}'\n")
        return

    query_str = args.query
    if not query_str:
        display_all_docs(vdb)
        console.print(Panel.fit(
            "[bold cyan]🔍 AI Semantic Search Engine CLI (Day 08)[/bold cyan]\n"
            "[dim]Ketik pertanyaan/konsep yang ingin Anda cari secara makna (semantik):[/dim]",
            border_style="cyan"
        ))
        try:
            query_str = input("Cari > ").strip()
        except KeyboardInterrupt:
            sys.exit(0)

    if not query_str:
        console.print("[red]Kueri pencarian kosong.[/red]")
        sys.exit(1)

    with console.status("[bold green]Menghitung vector embeddings & cosine similarity...[/bold green]", spinner="dots"):
        semantic_res = vdb.semantic_search(query_str, top_k=args.top_k, threshold=args.threshold)

    display_search_results(query_str, semantic_res, mode="Semantic AI Vector")

    if args.compare:
        keyword_res = vdb.keyword_search(query_str, top_k=args.top_k)
        display_search_results(query_str, keyword_res, mode="Exact Keyword Match")

if __name__ == "__main__":
    main()
