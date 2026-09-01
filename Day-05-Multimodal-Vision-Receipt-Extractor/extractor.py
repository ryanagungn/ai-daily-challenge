"""
Day 05 - Multimodal Vision Receipt & Invoice Extractor Core Module
Mengekstrak data terstruktur (line items, total, pajak, tanggal, merchant)
dari foto struk belanja, invoice, atau kuitansi menggunakan Gemini 2.5 Flash Vision.
"""

import os
import json
from pathlib import Path
from typing import List, Literal, Optional, Union
from pydantic import BaseModel, Field
from PIL import Image
from dotenv import load_dotenv

load_dotenv()

class ReceiptItem(BaseModel):
    item_name: str = Field(description="Nama produk atau layanan yang dibeli")
    quantity: float = Field(description="Jumlah kuantitas item yang dibeli")
    unit_price: float = Field(description="Harga per satuan unit")
    total_price: float = Field(description="Total harga untuk item ini (quantity * unit_price)")

class ReceiptData(BaseModel):
    merchant_name: str = Field(description="Nama toko, restoran, atau perusahaan penerbit invoice")
    merchant_address: Optional[str] = Field(default=None, description="Alamat lengkap merchant jika tertera")
    merchant_phone: Optional[str] = Field(default=None, description="Nomor telepon merchant jika tertera")
    tax_id_npwp: Optional[str] = Field(default=None, description="Nomor Pokok Wajib Pajak (NPWP) atau Tax ID jika ada")
    
    invoice_number: Optional[str] = Field(default=None, description="Nomor struk, faktur, atau receipt ID")
    transaction_date: Optional[str] = Field(default=None, description="Tanggal transaksi dalam format YYYY-MM-DD")
    transaction_time: Optional[str] = Field(default=None, description="Waktu transaksi jika ada (misal: 14:25)")
    
    currency: str = Field(description="Kode mata uang (misal: 'IDR', 'USD', 'EUR', 'SGD')")
    category: Literal[
        "Food & Beverage",
        "Electronics & Gadget",
        "Office & Stationery",
        "Transportation & Fuel",
        "Groceries & Supermarket",
        "Healthcare & Pharmacy",
        "Utilities & Bills",
        "Fashion & Apparel",
        "Other"
    ] = Field(description="Kategori pengeluaran transaksi")
    
    items: List[ReceiptItem] = Field(description="Daftar item belanjaan yang tertera di struk")
    
    subtotal: float = Field(description="Nilai subtotal sebelum pajak dan diskon")
    tax_amount: float = Field(default=0.0, description="Nilai total pajak (PPN, PB1, Service Tax, dll)")
    service_charge: float = Field(default=0.0, description="Biaya layanan restoran / service charge jika ada")
    discount_amount: float = Field(default=0.0, description="Nilai potongan harga atau diskon promo")
    total_amount: float = Field(description="Grand total akhir yang dibayarkan")
    
    payment_method: Optional[str] = Field(default=None, description="Metode pembayaran (misal: QRIS, Cash, Credit Card, GoPay)")
    payment_status: Literal["PAID", "UNPAID", "PENDING"] = Field(default="PAID", description="Status pembayaran")
    
    math_verification_notes: Optional[str] = Field(
        default=None,
        description="Catatan verifikasi perhitungan matematika (apakah subtotal + pajak - diskon == total_amount)"
    )

def get_gemini_client():
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise ValueError("GEMINI_API_KEY tidak ditemukan! Pastikan sudah menyetelnya di file .env")
    
    try:
        from google import genai
        return genai.Client(api_key=api_key)
    except ImportError:
        raise ImportError("Package 'google-genai' belum terpasang. Jalankan: pip install google-genai")

def extract_receipt_data(
    image_input: Union[str, Path, Image.Image],
    model_name: str = "gemini-2.5-flash"
) -> ReceiptData:
    """
    Mengekstrak data dari gambar struk/invoice menggunakan Gemini Vision API dengan structured output.
    """
    client = get_gemini_client()

    if isinstance(image_input, (str, Path)):
        img_path = Path(image_input)
        if not img_path.exists():
            raise FileNotFoundError(f"File gambar tidak ditemukan: {img_path}")
        image = Image.open(img_path)
    elif isinstance(image_input, Image.Image):
        image = image_input
    else:
        raise TypeError("image_input harus berupa file path atau objek PIL.Image")

    prompt = """
    Kamu adalah Sistem OCR & Ekstraksi Data Keuangan / Invoice AI tingkat enterprise.
    Tugasmu adalah membaca gambar struk / faktur / kuitansi ini dengan sangat teliti dan akurat.

    Instruksi Khusus:
    1. Ekstrak nama merchant, nomor invoice, tanggal, dan waktu secara presisi.
    2. Identifikasi setiap item belanjaan, jumlah kuantitas (quantity), harga satuan (unit_price), dan total harga baris (total_price).
    3. Ekstrak Subtotal, Pajak (PPN/PB1), Service Charge, Diskon, dan Grand Total.
    4. Format semua angka keuangan sebagai nilai numerik (float) murni tanpa simbol mata uang atau pemisah ribuan.
    5. Verifikasi perhitungan matematika: Pastikan hubungan (Subtotal + Pajak + Service - Diskon) konsisten dengan Total Akhir. Berikan catatan jika ada ketidakcocokan.
    6. Tentukan kategori pengeluaran yang paling sesuai.
    """

    response = client.models.generate_content(
        model=model_name,
        contents=[image, prompt],
        config={
            "response_mime_type": "application/json",
            "response_schema": ReceiptData,
            "temperature": 0.1,
        },
    )

    parsed_dict = json.loads(response.text)
    return ReceiptData(**parsed_dict)
