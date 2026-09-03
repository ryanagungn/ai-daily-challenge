"""
Day 07 - Interactive Prompt Engineering Playground (CLI Version)
Eksperimen prompt, uji parameter temperature/top_p, dan optimasi prompt langsung dari terminal.
"""

import sys
import json
import argparse
from pathlib import Path
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.syntax import Syntax
from rich.markdown import Markdown
from rich.prompt import Prompt

# Pastikan modul internal terbaca
sys.path.append(str(Path(__file__).parent))
from engine import (
    run_prompt_inference,
    optimize_prompt,
    extract_variables_from_template,
    generate_python_snippet,
    ExecutionResult
)

console = Console()
PRESETS_FILE = Path(__file__).parent / "presets.json"

def load_presets():
    if PRESETS_FILE.exists():
        return json.loads(PRESETS_FILE.read_text(encoding="utf-8"))
    return []

def display_presets_table():
    presets = load_presets()
    table = Table(title="📚 Preset Template Prompt", show_header=True, header_style="bold magenta", expand=True)
    table.add_column("ID", style="cyan", width=24)
    table.add_column("Nama Template", style="bold white", width=35)
    table.add_column("Deskripsi", style="dim")

    for p in presets:
        table.add_row(p["id"], p["name"], p["description"])

    console.print(table)
    console.print()

def display_result(result: ExecutionResult):
    console.print()
    console.rule("[bold green]✨ HASIL GENERASI MODEL[/bold green]")
    console.print()

    # Output text
    console.print(Panel(
        Markdown(result.output_text),
        title="[bold green]Response AI[/bold green]",
        border_style="green",
        padding=(1, 2)
    ))
    console.print()

    # Metrics table
    m = result.metrics
    table = Table(show_header=True, header_style="bold cyan", box=None)
    table.add_column("Model", style="white")
    table.add_column("Latency", style="yellow")
    table.add_column("Output Size", style="cyan")
    table.add_column("Temperature", style="magenta")
    table.add_column("Top-P", style="blue")

    table.add_row(
        m.model_used,
        f"{m.latency_ms:.0f} ms",
        f"{m.output_word_count} kata ({m.output_char_count} char)",
        str(m.temperature),
        str(m.top_p)
    )
    console.print(table)
    console.print()

def main():
    parser = argparse.ArgumentParser(description="AI Prompt Engineering Playground CLI")
    parser.add_argument("-p", "--prompt", help="Teks prompt (dapat menggunakan pola {{variabel}})")
    parser.add_argument("-s", "--system", help="System instruction")
    parser.add_argument("--preset", help="Gunakan ID preset dari library")
    parser.add_argument("--list-presets", action="store_true", help="Tampilkan daftar preset yang tersedia")
    parser.add_argument("--optimize", help="Optimasi prompt mentah menggunakan AI Prompt Engineering specialist")
    parser.add_argument("-t", "--temperature", type=float, default=0.7, help="Nilai temperature (0.0 - 2.0, default: 0.7)")
    parser.add_argument("--top-p", type=float, default=0.95, help="Nilai top-p (default: 0.95)")
    parser.add_argument("-m", "--model", default="gemini-2.5-flash", help="Model Gemini (default: gemini-2.5-flash)")
    parser.add_argument("--export-code", action="store_true", help="Tampilkan snippet kode Python untuk prompt ini")

    args = parser.parse_args()

    if args.list_presets:
        display_presets_table()
        return

    # Mode 1: AI Prompt Optimizer
    if args.optimize:
        console.print(f"[bold cyan]🔍 Sedang mengoptimalkan prompt Anda...[/bold cyan]")
        opt_res = optimize_prompt(args.optimize, model_name=args.model)
        
        console.print()
        console.rule("[bold yellow]🚀 HASIL OPTIMASI PROMPT[/bold yellow]")
        console.print(Panel(opt_res.optimized_system_instruction, title="[bold green]System Instruction Baru[/bold green]", border_style="green"))
        console.print(Panel(opt_res.optimized_user_prompt, title="[bold cyan]User Prompt Baru[/bold cyan]", border_style="cyan"))
        
        impr_md = "\n".join([f"- {imp}" for imp in opt_res.key_improvements])
        console.print(Panel(Markdown(impr_md), title="[bold yellow]Poin Peningkatan[/bold yellow]", border_style="yellow"))
        console.print(f"Rekomendasi Temperature: [bold magenta]{opt_res.recommended_temperature}[/bold magenta]\n")
        return

    prompt_template = args.prompt
    system_inst = args.system
    variables = {}
    temp = args.temperature
    top_p = args.top_p

    # Mode 2: Preset loader
    if args.preset:
        presets = load_presets()
        matched = next((p for p in presets if p["id"] == args.preset), None)
        if not matched:
            console.print(f"[bold red]Error:[/bold red] Preset '{args.preset}' tidak ditemukan!")
            display_presets_table()
            sys.exit(1)
        
        prompt_template = matched["prompt_template"]
        system_inst = matched.get("system_instruction")
        variables = matched.get("variables", {})
        temp = matched.get("temperature", temp)
        top_p = matched.get("top_p", top_p)
        console.print(f"[bold green]✓ Loaded Preset:[/bold green] {matched['name']}\n")

    # Mode 3: Interactive REPL jika tidak ada argumen
    if not prompt_template:
        console.print(Panel.fit(
            "[bold cyan]🧪 Interactive Prompt Engineering Playground (Day 07)[/bold cyan]\n"
            "[dim]Eksperimen prompt engineering, template variabel, dan evaluasi respons model.[/dim]\n"
            "[yellow]Tip: Gunakan flag '--list-presets' atau '--preset <id>' untuk template siap pakai.[/yellow]",
            border_style="cyan"
        ))
        prompt_template = Prompt.ask("Masukkan Prompt Template (gunakan {{var}} jika ada variabel)")

    # Deteksi variabel jika belum terisi
    var_keys = extract_variables_from_template(prompt_template)
    for k in var_keys:
        if k not in variables:
            val = Prompt.ask(f"Isi nilai untuk variabel '[bold cyan]{k}[/bold cyan]'")
            variables[k] = val

    if args.export_code:
        code_str = generate_python_snippet(
            prompt_template=prompt_template,
            system_instruction=system_inst,
            variables=variables,
            temperature=temp,
            top_p=top_p,
            model_name=args.model
        )
        console.print(Panel(Syntax(code_str, "python", theme="monokai", line_numbers=True), title="🐍 Python Code Snippet", border_style="cyan"))
        return

    with console.status("[bold green]Mengirim prompt ke Gemini AI...[/bold green]", spinner="dots"):
        try:
            res = run_prompt_inference(
                prompt_template=prompt_template,
                variables=variables,
                system_instruction=system_inst,
                model_name=args.model,
                temperature=temp,
                top_p=top_p
            )
            display_result(res)
        except Exception as e:
            console.print(f"[bold red]Gagal mengeksekusi prompt:[/bold red] {e}")

if __name__ == "__main__":
    main()
