"""
Day 05 - Sample Receipt Image Generator
Menghasilkan gambar struk belanja realistis sintetis menggunakan Pillow untuk testing offline/online.
"""

from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

OUTPUT_DIR = Path(__file__).parent

def create_coffee_receipt():
    width, height = 480, 720
    img = Image.new("RGB", (width, height), color="#fcfaf2")
    draw = ImageDraw.Draw(img)

    # Tambahkan tekstur struk / garis putus-putus
    draw.rectangle([(20, 20), (width - 20, height - 20)], outline="#d1cdc0", width=2)
    
    # Header Struk
    draw.text((width // 2, 50), "KOPI KENANGAN SENJA", fill="#1a1a1a", anchor="mm")
    draw.text((width // 2, 75), "Jl. Sudirman No. 45, Jakarta Selatan", fill="#555555", anchor="mm")
    draw.text((width // 2, 95), "Telp: (021) 555-0199 | NPWP: 01.234.567.8-012.000", fill="#777777", anchor="mm")
    
    draw.line([(30, 120), (width - 30, 120)], fill="#aaaaaa", width=1)
    
    # Metadata
    draw.text((35, 135), "No. Struk: KPS-20240901-889", fill="#333333")
    draw.text((35, 155), "Tanggal  : 01 Sep 2024 14:25 WIB", fill="#333333")
    draw.text((35, 175), "Kasir    : Dimas Pratama", fill="#333333")
    draw.text((35, 195), "Meja     : Takeaway / QRIS", fill="#333333")
    
    draw.line([(30, 225), (width - 30, 225)], fill="#aaaaaa", width=1)
    draw.text((35, 235), "ITEM", fill="#1a1a1a")
    draw.text((width - 35, 235), "TOTAL (IDR)", fill="#1a1a1a", anchor="ra")
    draw.line([(30, 255), (width - 30, 255)], fill="#aaaaaa", width=1)
    
    # Items
    items = [
        ("2x Es Kopi Kenangan Mantan (L)", "2 x 24.000", "48.000"),
        ("1x Earl Grey Tea Latte (R)", "1 x 28.000", "28.000"),
        ("1x Croissant Butter Almond", "1 x 32.000", "32.000"),
        ("2x Toast Cokelat Keju", "2 x 22.000", "44.000"),
    ]
    
    y = 275
    for title, sub, total in items:
        draw.text((35, y), title, fill="#222222")
        draw.text((width - 35, y), total, fill="#222222", anchor="ra")
        y += 20
        draw.text((50, y), sub, fill="#777777")
        y += 35
        
    draw.line([(30, y), (width - 30, y)], fill="#aaaaaa", width=1)
    y += 15
    
    # Totals
    draw.text((35, y), "Subtotal", fill="#444444")
    draw.text((width - 35, y), "152.000", fill="#444444", anchor="ra")
    y += 25
    draw.text((35, y), "PB1 Restoran (10%)", fill="#444444")
    draw.text((width - 35, y), "15.200", fill="#444444", anchor="ra")
    y += 25
    draw.text((35, y), "Diskon Promo QRIS", fill="#2e7d32")
    draw.text((width - 35, y), "-10.000", fill="#2e7d32", anchor="ra")
    y += 30
    
    draw.line([(30, y), (width - 30, y)], fill="#222222", width=2)
    y += 15
    draw.text((35, y), "GRAND TOTAL", fill="#111111")
    draw.text((width - 35, y), "Rp 157.200", fill="#111111", anchor="ra")
    y += 30
    draw.text((35, y), "Metode Bayar: QRIS GO-PAY", fill="#555555")
    draw.text((width - 35, y), "LUNAS", fill="#2e7d32", anchor="ra")
    
    y += 50
    draw.line([(30, y), (width - 30, y)], fill="#aaaaaa", width=1)
    y += 25
    draw.text((width // 2, y), "*** TERIMA KASIH ATAS KUNJUNGAN ANDA ***", fill="#666666", anchor="mm")
    draw.text((width // 2, y + 20), "Wifi: KenanganSenja_Free | Pass: kopi1234", fill="#888888", anchor="mm")

    img_path = OUTPUT_DIR / "sample_coffee_receipt.png"
    img.save(img_path)
    print(f"Sample coffee receipt saved to {img_path}")

if __name__ == "__main__":
    create_coffee_receipt()
