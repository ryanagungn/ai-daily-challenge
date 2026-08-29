"""
Day 03 - Natural Language to SQL (CLI Version)
Menjalankan query database dengan bahasa sehari-hari langsung dari terminal.
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
from database import init_database, get_schema_description
from sql_engine import query_database_with_nl, SQLGenerationResult

console = Console()

def display_schema():
    console.print()
    console.rule("[bold cyan]🗄️ SKEMA DATABASE E-COMMERCE (SQLite)[/bold cyan]")
    schema_text = get_schema_description()
    console.print(Syntax(schema_text, "sql", theme="monokai", line_numbers=False))
    console.print()

def display_query_result(res: dict):
    console.print()
    console.rule("[bold cyan]🎯 HASIL QUERY DATABASE[/bold cyan]")
    console.print()

    meta: SQLGenerationResult = res["result_meta"]

    # 1. SQL Code
    console.print(Panel(
        Syntax(meta.sql_query, "sql", theme="monokai", line_numbers=True),
        title="[bold green]⚡ Generated SQL (SQLite)[/bold green]",
        border_style="green"
    ))
    console.print()

    # 2. Status & Error Handling
    if not res["success"]:
        console.print(Panel(f"[bold red]Error:[/bold red] {res['error']}", border_style="red"))
        return

    # 3. Data Table
    table = Table(
        title=f"📊 Hasil Query ({res['row_count']} baris | ⏱️ {res['execution_time_ms']} ms)",
        show_header=True,
        header_style="bold magenta",
        expand=True
    )

    for col in res["columns"]:
        table.add_column(str(col), style="cyan")

    for row in res["rows"]:
        formatted_values = []
        for col in res["columns"]:
            val = row.get(col, "")
            # Format mata uang jika angka besar
            if isinstance(val, (int, float)) and val > 10000 and "id" not in col.lower() and "quantity" not in col.lower():
                formatted_values.append(f"Rp {val:,.0f}")
            else:
                formatted_values.append(str(val))
        table.add_row(*formatted_values)

    console.print(table)
    console.print()

    # 4. Explanation & Insights
    expl_md = f"""### 💡 Penjelasan Logika Query:
{meta.explanation}

### 📈 Insight Bisnis:
{meta.business_insights}

*Tabel yang digunakan: {', '.join([f'`{t}`' for t in meta.tables_used])} | Rekomendasi Grafik: `{meta.chart_recommendation}`*
"""
    console.print(Panel(Markdown(expl_md), title="[bold yellow]🧠 Analisis AI[/bold yellow]", border_style="yellow"))
    console.print()

def main():
    parser = argparse.ArgumentParser(description="Natural Language to SQL Query Runner CLI")
    parser.add_argument("-q", "--question", help="Pertanyaan dalam bahasa manusia (misal: 'Siapa 5 pelanggan belanja terbanyak?')")
    parser.add_argument("--schema", action="store_true", help="Tampilkan skema database yang tersedia")
    parser.add_argument("-m", "--model", default="gemini-2.5-flash", help="Nama model Gemini (default: gemini-2.5-flash)")
    
    args = parser.parse_args()

    # Pastikan DB siap
    init_database()

    if args.schema:
        display_schema()
        return

    if args.question:
        with console.status(f"[bold green]Menerjemahkan pertanyaan & menjalankan SQL...[/bold green]", spinner="dots"):
            res = query_database_with_nl(args.question, model_name=args.model)
        display_query_result(res)
        return

    # Interactive REPL mode
    console.print(Panel.fit(
        "[bold cyan]🗄️ Natural Language to SQL CLI (Day 03)[/bold cyan]\n"
        "[dim]Tanyakan apa saja seputar data penjualan, produk, pelanggan, atau kategori e-commerce.\n"
        "Ketik 'schema' untuk melihat tabel, atau 'exit' untuk keluar.[/dim]",
        border_style="cyan"
    ))

    while True:
        try:
            console.print("[bold yellow]Tanya Data > [/bold yellow]", end="")
            user_input = input().strip()

            if not user_input:
                continue
            if user_input.lower() in ["exit", "quit", "q"]:
                console.print("[yellow]Sampai jumpa![/yellow]")
                break
            if user_input.lower() == "schema":
                display_schema()
                continue

            with console.status(f"[bold green]Memproses query AI...[/bold green]", spinner="dots"):
                res = query_database_with_nl(user_input, model_name=args.model)
            display_query_result(res)

        except KeyboardInterrupt:
            console.print("\n[yellow]Operasi dihentikan.[/yellow]")
            break
        except Exception as e:
            console.print(f"[bold red]Terjadi kesalahan:[/bold red] {e}")

if __name__ == "__main__":
    main()
