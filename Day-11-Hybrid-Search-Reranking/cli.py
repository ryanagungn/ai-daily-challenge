"""
Day 11 - Hybrid Search & Re-ranking (CLI Version)
Mencari dokumen dengan BM25 leksikal + Dense Vector + RRF Fusion dan Cross-Encoder Re-ranking via terminal.
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
from hybrid_engine import HybridSearchEngine, RankedItem, ReRankedItem

console = Console()

def display_hybrid_table(query: str, items: list[RankedItem]):
    console.print()
    console.rule(f"[bold cyan]🔀 HASIL HYBRID SEARCH (BM25 + Dense Vector + RRF): '{query}'[/bold cyan]")
    console.print()

    table = Table(show_header=True, header_style="bold magenta", expand=True)
    table.add_column("Rank", width=6, justify="center")
    table.add_column("RRF Score", width=12, justify="center", style="bold green")
    table.add_column("BM25 Rank", width=12, justify="center", style="yellow")
    table.add_column("Dense Rank", width=12, justify="center", style="cyan")
    table.add_column("Judul & Cuplikan", style="white")

    for idx, it in enumerate(items, 1):
        bm25_str = f"#{it.bm25_rank} ({it.bm25_score})" if it.bm25_rank else "-"
        dense_str = f"#{it.dense_rank} ({it.dense_score*100:.1f}%)" if it.dense_rank else "-"
        content_preview = it.content[:140] + "..." if len(it.content) > 140 else it.content

        detail = f"[bold]{it.title}[/bold] [dim]({it.category})[/dim]\n[dim]{content_preview}[/dim]"
        table.add_row(f"#{idx}", f"{it.rrf_score:.4f}", bm25_str, dense_str, detail)

    console.print(table)
    console.print()

def display_reranked_table(query: str, reranked_items: list[ReRankedItem]):
    console.print()
    console.rule("[bold green]🎯 HASIL RE-RANKING CROSS-ENCODER (GEMINI AI)[/bold green]")
    console.print()

    table = Table(show_header=True, header_style="bold green", expand=True)
    table.add_column("Rank", width=6, justify="center")
    table.add_column("Relevansi", width=12, justify="center")
    table.add_column("Judul & Kategori", width=32, style="bold cyan")
    table.add_column("Alasan Relevansi (LLM Reasoning)", style="white")

    for idx, it in enumerate(reranked_items, 1):
        score_color = "bold green" if it.relevance_score >= 80 else "bold yellow" if it.relevance_score >= 50 else "red"
        score_badge = f"[{score_color}]{it.relevance_score}/100[/{score_color}]"

        title_str = f"{it.title}\n[dim]({it.category})[/dim]"
        table.add_row(f"#{idx}", score_badge, title_str, it.reasoning)

    console.print(table)
    console.print()

def main():
    parser = argparse.ArgumentParser(description="Hybrid Search with BM25 & Dense Vectors CLI")
    parser.add_argument("-q", "--query", help="Kueri pencarian (misal: 'ERR_REDIS_CONN_TIMEOUT' atau 'proteksi xss cookie')")
    parser.add_argument("-k", "--top-k", type=int, default=4, help="Jumlah hasil teratas (default: 4)")
    parser.add_argument("--bm25-weight", type=float, default=0.5, help="Bobot BM25 (default: 0.5)")
    parser.add_argument("--dense-weight", type=float, default=0.5, help="Bobot Dense Vector (default: 0.5)")
    parser.add_argument("--rerank", action="store_true", help="Jalankan LLM Cross-Encoder Re-ranking pada kandidat")
    parser.add_argument("-m", "--model", default="gemini-2.5-flash", help="Model Gemini untuk Re-ranking")

    args = parser.parse_args()

    engine = HybridSearchEngine()

    query_str = args.query
    if not query_str:
        console.print(Panel.fit(
            "[bold cyan]🔀 Hybrid Search Engine CLI (Day 11)[/bold cyan]\n"
            "[dim]Pencarian gabungan BM25 (Kata Kunci Eksak) + Dense Vector (Makna Semantik) + RRF Fusion.[/dim]\n"
            "[yellow]Contoh uji: 'ERR_REDIS_CONN_TIMEOUT', 'mencegah pencurian session token', 'CVE-2024-38856'[/yellow]",
            border_style="cyan"
        ))
        try:
            query_str = input("Kueri Pencarian > ").strip()
        except KeyboardInterrupt:
            sys.exit(0)

    if not query_str:
        console.print("[bold red]Kueri pencarian tidak boleh kosong.[/bold red]")
        sys.exit(1)

    with console.status("[bold green]Menjalankan BM25 + Dense Vector Search + RRF Fusion...[/bold green]", spinner="dots"):
        hybrid_results = engine.hybrid_search_rrf(
            query=query_str,
            top_k=args.top_k,
            bm25_weight=args.bm25_weight,
            dense_weight=args.dense_weight
        )

    display_hybrid_table(query_str, hybrid_results)

    if args.rerank and hybrid_results:
        with console.status("[bold green]Menjalankan Cross-Encoder Re-ranking dengan Gemini AI...[/bold green]", spinner="dots"):
            reranked = engine.rerank_with_llm(query=query_str, candidates=hybrid_results, model_name=args.model)
        display_reranked_table(query_str, reranked)

if __name__ == "__main__":
    main()
