"""
Day 05 - Multimodal Vision Receipt & Invoice Extractor (CLI Version)
Mengekstrak data struk & invoice langsung dari terminal dengan format visual tabel Rich.
"""

import sys
import argparse
import pandas as pd
from pathlib import Path
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.markdown import Markdown

# Pastikan modul internal terbaca
sys.path.append(str(Path(__file__).parent))
from extractor import extract_receipt_data, ReceiptData

console = Console()

def format_currency(val: float, currency: str) -> str:
    if currency == "IDR":
        return f"Rp {val:,.0f}"
    return f"{currency} {val:,.2f}"

def display_receipt_data(data: ReceiptData, image_path: Path):
    console.print()
    console.rule("[bold cyan]🧾 HASIL EKSTRAKSI STRUK & INVOICE MULTIMODAL AI[/bold cyan]")
    console.print()

    curr = data.currency

    # 1. Header Info Panel
    info_md = f"""**Merchant:** [bold]{data.merchant_name}[/bold]
- **Alamat:** {data.merchant_address or '-'}
- **No. Invoice / Struk:** `{data.invoice_number or '-'}`
- **Waktu Transaksi:** `{data.transaction_date or '-'}` {data.transaction_time or ''}
- **Kategori:** `[yellow]{data.category}[/yellow]` | **Metode Bayar:** `[green]{data.payment_method or '-'}[/green]` | **Status:** `[bold green]{data.payment_status}[/bold green]`
"""
    console.print(Panel(Markdown(info_md), title="[bold green]🏪 Informasi Transaksi[/bold green]", border_style="green"))
    console.print()

    # 2. Line Items Table
    table = Table(title="🛒 Rincian Item Belanjaan", show_header=True, header_style="bold magenta", expand=True)
    table.add_column("No", width=5, justify="center")
    table.add_column("Nama Item", style="white")
    table.add_column("Kuantitas", width=12, justify="right")
    table.add_column("Harga Satuan", width=18, justify="right")
    table.add_column("Total Harga", width=20, justify="right", style="bold cyan")

    for idx, item in enumerate(data.items, 1):
        table.add_row(
            str(idx),
            item.item_name,
            f"{item.quantity:g}",
            format_currency(item.unit_price, curr),
            format_currency(item.total_price, curr)
        )

    console.print(table)
    console.print()

    # 3. Financial Breakdown Table
    fin_table = Table(show_header=False, expand=False, box=None)
    fin_table.add_column("Label", style="dim", width=25)
    fin_table.add_column("Nilai", justify="right", style="bold")

    fin_table.add_row("Subtotal", format_currency(data.subtotal, curr))
    if data.tax_amount > 0:
        fin_table.add_row("Pajak (PPN / PB1)", format_currency(data.tax_amount, curr))
    if data.service_charge > 0:
        fin_table.add_row("Biaya Layanan (Service)", format_currency(data.service_charge, curr))
    if data.discount_amount > 0:
        fin_table.add_row("Diskon / Potongan", f"- {format_currency(data.discount_amount, curr)}")
    fin_table.add_row("[bold]GRAND TOTAL[/bold]", f"[bold green]{format_currency(data.total_amount, curr)}[/bold green]")

    console.print(Panel(fin_table, title="[bold yellow]💰 Rekapitulasi Pembayaran[/bold yellow]", border_style="yellow"))
    console.print()

    if data.math_verification_notes:
        console.print(f"[dim]ℹ️ Catatan Verifikasi: {data.math_verification_notes}[/dim]\n")

def main():
    parser = argparse.ArgumentParser(description="Multimodal Vision Receipt & Invoice Extractor CLI")
    parser.add_argument("-i", "--image", help="Path ke file gambar struk/invoice (.png, .jpg, .jpeg, .webp)")
    parser.add_argument("--json-out", help="Path untuk menyimpan hasil ekstraksi dalam format JSON")
    parser.add_argument("--csv-out", help="Path untuk menyimpan daftar item dalam format CSV")
    parser.add_argument("-m", "--model", default="gemini-2.5-flash", help="Model Gemini (default: gemini-2.5-flash)")

    args = parser.parse_args()

    # Default ke sample image jika tidak ada argumen
    img_path = None
    if args.image:
        img_path = Path(args.image)
    else:
        sample_path = Path(__file__).parent / "sample_coffee_receipt.png"
        if sample_path.exists():
            console.print(f"[yellow]Tidak ada file gambar yang dispesifikasikan. Menggunakan sample default:[/yellow] [cyan]{sample_path.name}[/cyan]")
            img_path = sample_path
        else:
            console.print("[bold red]Error:[/bold red] Silakan berikan path gambar dengan argumen `-i / --image <path>`")
            sys.exit(1)

    if not img_path.exists():
        console.print(f"[bold red]Error:[/bold red] File gambar '{img_path}' tidak ditemukan!")
        sys.exit(1)

    with console.status(f"[bold green]Menganalisis gambar struk dengan Gemini Vision AI...[/bold green]", spinner="dots"):
        try:
            result = extract_receipt_data(img_path, model_name=args.model)
        except Exception as e:
            console.print(f"[bold red]Gagal mengekstrak struk:[/bold red] {e}")
            sys.exit(1)

    display_receipt_data(result, img_path)

    # Export jika diminta
    if args.json_out:
        Path(args.json_out).write_text(result.model_dump_json(indent=2), encoding="utf-8")
        console.print(f"[bold green]✓[/bold green] JSON disimpan ke: [cyan]{args.json_out}[/cyan]")

    if args.csv_out:
        df = pd.DataFrame([item.model_dump() for item in result.items])
        df.to_csv(args.csv_out, index=False)
        console.print(f"[bold green]✓[/bold green] CSV line items disimpan ke: [cyan]{args.csv_out}[/cyan]")

if __name__ == "__main__":
    main()
