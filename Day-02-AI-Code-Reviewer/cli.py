"""
Day 02 - AI Code Reviewer & Refactor Assistant (CLI Version)
Menjalankan audit kode langsung dari terminal dengan Rich syntax highlighting dan laporan isu terstruktur.
"""

import sys
import argparse
from pathlib import Path
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.syntax import Syntax
from rich.markdown import Markdown

# Pastikan modul reviewer terbaca
sys.path.append(str(Path(__file__).parent))
from reviewer import review_code, CodeReviewResult

console = Console()

SEVERITY_COLORS = {
    "Critical": "bold red",
    "High": "red",
    "Medium": "yellow",
    "Low": "blue",
    "Info": "cyan"
}

CATEGORY_ICONS = {
    "Security": "🔒 Security",
    "Bug": "🐛 Bug",
    "Performance": "⚡ Performance",
    "Code Smell": "🦨 Code Smell",
    "Style / Best Practice": "🎨 Style"
}

def display_review(result: CodeReviewResult, show_refactor: bool = True):
    console.print()
    console.rule("[bold cyan]🛡️ HASIL AUDIT & CODE REVIEW AI[/bold cyan]")
    console.print()

    # Score Gauge
    score_color = "green" if result.quality_score >= 8 else "yellow" if result.quality_score >= 5 else "red"
    score_text = f"[{score_color} bold]{result.quality_score} / 10[/{score_color} bold]"

    # Summary Panel
    summary_md = f"""**Bahasa Terdeteksi:** `{result.language}` | **Skor Kualitas:** {score_text}
    
**Ringkasan Eksekutif:**
{result.executive_summary}
"""
    if result.time_complexity_before and result.time_complexity_after:
        summary_md += f"\n**Kompleksitas Waktu:** `{result.time_complexity_before}` ➔ `{result.time_complexity_after}`"

    console.print(Panel(Markdown(summary_md), title="[bold green]📋 Ringkasan Analisis[/bold green]", border_style="green"))
    console.print()

    # Issues Table
    if result.issues:
        table = Table(show_header=True, header_style="bold magenta", expand=True)
        table.add_column("Level", width=12)
        table.add_column("Kategori", width=18)
        table.add_column("Baris", width=10)
        table.add_column("Masalah & Rekomendasi Solusi", style="white")

        for issue in result.issues:
            sev_color = SEVERITY_COLORS.get(issue.severity, "white")
            sev_badge = f"[{sev_color}]{issue.severity}[/{sev_color}]"
            cat_badge = CATEGORY_ICONS.get(issue.category, issue.category)
            line_str = issue.line_number or "-"
            
            detail_str = f"[bold]{issue.title}[/bold]\n[dim]{issue.description}[/dim]\n💡 [green]{issue.suggestion}[/green]"
            table.add_row(sev_badge, cat_badge, line_str, detail_str)

        console.print(table)
        console.print()
    else:
        console.print(Panel("[bold green]🎉 Luar biasa! Tidak ditemukan masalah kritis pada kode ini.[/bold green]", border_style="green"))
        console.print()

    # Changes summary
    if result.explanation_of_changes:
        changes_md = "\n".join([f"- {change}" for change in result.explanation_of_changes])
        console.print(Panel(Markdown(changes_md), title="[bold yellow]🔄 Poin Perubahan Refactoring[/bold yellow]", border_style="yellow"))
        console.print()

    # Show refactored code
    if show_refactor and result.refactored_code:
        console.rule("[bold green]🚀 KODE SETELAH DIREFAKTOR[/bold green]")
        lang_syntax = result.language.lower()
        if "python" in lang_syntax:
            lang_syntax = "python"
        elif "javascript" in lang_syntax or "js" in lang_syntax:
            lang_syntax = "javascript"
        elif "typescript" in lang_syntax or "ts" in lang_syntax:
            lang_syntax = "typescript"
        elif "go" in lang_syntax:
            lang_syntax = "go"
        else:
            lang_syntax = "python"

        syntax = Syntax(result.refactored_code, lang_syntax, theme="monokai", line_numbers=True)
        console.print(syntax)
        console.print()

def main():
    parser = argparse.ArgumentParser(description="AI Code Reviewer & Refactor Assistant CLI")
    parser.add_argument("-f", "--file", help="Path ke file kode sumber yang ingin diaudit")
    parser.add_argument("-t", "--text", help="Snippet kode langsung")
    parser.add_argument("-o", "--output", help="Path file untuk menyimpan kode hasil refaktor")
    parser.add_argument("--focus", default="General (All)", choices=["General (All)", "Security Focus", "Performance Focus", "Clean Code/Refactor"], help="Fokus utama audit")
    parser.add_argument("-m", "--model", default="gemini-2.5-flash", help="Nama model Gemini (default: gemini-2.5-flash)")
    
    args = parser.parse_args()

    content = ""
    lang_hint = None
    if args.file:
        file_path = Path(args.file)
        if not file_path.exists():
            console.print(f"[bold red]Error:[/bold red] File '{args.file}' tidak ditemukan!")
            sys.exit(1)
        content = file_path.read_text(encoding="utf-8")
        lang_hint = file_path.suffix.lstrip(".")
    elif args.text:
        content = args.text
    else:
        console.print(Panel.fit(
            "[bold cyan]🛡️ AI Code Reviewer & Refactor Assistant (Day 02)[/bold cyan]\n"
            "[dim]Tempel snippet kode Anda di bawah ini, lalu tekan Ctrl+Z (Windows) atau Ctrl+D (Mac/Linux) lalu Enter:[/dim]",
            border_style="cyan"
        ))
        try:
            content = sys.stdin.read()
        except KeyboardInterrupt:
            console.print("\n[yellow]Operasi dibatalkan.[/yellow]")
            sys.exit(0)

    if not content.strip():
        console.print("[bold red]Kode input kosong. Tidak ada yang direview.[/bold red]")
        sys.exit(1)

    with console.status("[bold green]Sedang melakukan audit kode mendalam dengan Gemini AI...[/bold green]", spinner="dots"):
        try:
            result = review_code(
                code_content=content,
                language_hint=lang_hint,
                focus=args.focus,
                model_name=args.model
            )
            display_review(result)

            if args.output:
                out_path = Path(args.output)
                out_path.write_text(result.refactored_code, encoding="utf-8")
                console.print(f"[bold green]✓[/bold green] Kode refaktor berhasil disimpan ke: [cyan]{out_path.resolve()}[/cyan]\n")

        except Exception as e:
            console.print(f"\n[bold red]Gagal melakukan review:[/bold red] {e}")
            sys.exit(1)

if __name__ == "__main__":
    main()
