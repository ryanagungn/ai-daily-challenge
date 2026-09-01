"""
Day 05 - Multimodal Vision Receipt & Invoice Extractor (Streamlit Web App)
Antarmuka Web Interaktif untuk audit struk belanja, ekstraksi line-items, dan rekonsiliasi keuangan.
"""

import os
import sys
import json
import pandas as pd
from pathlib import Path
from PIL import Image
import streamlit as st

# Pastikan modul internal terbaca
sys.path.append(str(Path(__file__).parent))
from extractor import extract_receipt_data, ReceiptData

st.set_page_config(
    page_title="AI Receipt & Invoice Extractor | Day 05",
    page_icon="🧾",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom Styling
st.markdown("""
<style>
    .merchant-card {
        background-color: #f8f9fa;
        border-radius: 12px;
        padding: 18px;
        border-left: 5px solid #2e7d32;
        margin-bottom: 15px;
    }
    .badge-cat {
        background-color: #e8f5e9;
        color: #1b5e20;
        padding: 4px 12px;
        border-radius: 16px;
        font-weight: bold;
        font-size: 0.85rem;
    }
</style>
""", unsafe_allow_html=True)

# Helper currency format
def format_curr(val: float, curr: str) -> str:
    if curr == "IDR":
        return f"Rp {val:,.0f}"
    return f"{curr} {val:,.2f}"

# Sidebar
with st.sidebar:
    st.title("⚙️ Pengaturan Vision AI")
    api_key_input = st.text_input(
        "Gemini API Key",
        value=os.getenv("GEMINI_API_KEY", ""),
        type="password",
        help="Dapatkan API key gratis di aistudio.google.com"
    )
    if api_key_input:
        os.environ["GEMINI_API_KEY"] = api_key_input

    model_option = st.selectbox(
        "Pilih Model Gemini",
        options=["gemini-2.5-flash", "gemini-2.5-pro"],
        index=0
    )

    st.divider()
    st.markdown("### 📌 Tentang Proyek")
    st.markdown("""
    **Day 05 dari 30 Days of AI Challenge**
    - Multimodal Vision Understanding
    - Automated Table & Line Item Extraction
    - Financial Math Reconciliation
    - Export to Accounting Formats (CSV/JSON)
    """)

# Main Content
st.title("🧾 AI Receipt & Invoice Data Extractor")
st.markdown("Unggah foto struk belanja, invoice restoran, atau kuitansi untuk mengekstrak data item, subtotal, dan pajak secara otomatis.")

col_left, col_right = st.columns([1, 1], gap="large")

with col_left:
    st.subheader("📸 Input Gambar Struk")
    
    input_mode = st.radio(
        "Pilih Sumber Gambar:",
        ["📁 Upload File Gambar", "📷 Ambil Foto dari Kamera", "📄 Gunakan Sample Demo (Struk Kopi)"],
        horizontal=True
    )

    image_to_process = None

    if input_mode == "📁 Upload File Gambar":
        uploaded_file = st.file_uploader("Upload Foto Struk (.png, .jpg, .jpeg, .webp)", type=["png", "jpg", "jpeg", "webp"])
        if uploaded_file is not None:
            image_to_process = Image.open(uploaded_file)
            st.image(image_to_process, caption="Gambar yang diunggah", use_container_width=True)

    elif input_mode == "📷 Ambil Foto dari Kamera":
        camera_image = st.camera_input("Ambil foto struk fisik Anda:")
        if camera_image is not None:
            image_to_process = Image.open(camera_image)

    elif input_mode == "📄 Gunakan Sample Demo (Struk Kopi)":
        sample_path = Path(__file__).parent / "sample_coffee_receipt.png"
        if sample_path.exists():
            image_to_process = Image.open(sample_path)
            st.image(image_to_process, caption="Sample Struk Kopi Kenangan Senja", use_container_width=True)
        else:
            st.warning("Sample image belum di-generate.")

    process_btn = st.button("🚀 Ekstrak Data dari Struk", type="primary", use_container_width=True)

with col_right:
    st.subheader("📊 Data Terstruktur Hasil Ekstraksi")

    if process_btn:
        if image_to_process is None:
            st.warning("Silakan sediakan gambar struk terlebih dahulu!")
        elif not os.getenv("GEMINI_API_KEY"):
            st.error("🔑 API Key belum diatur! Masukkan GEMINI_API_KEY di sidebar atau file .env")
        else:
            with st.spinner("🤖 Menganalisis gambar dan mengekstrak tabel struk dengan Gemini Vision..."):
                try:
                    result_data: ReceiptData = extract_receipt_data(image_to_process, model_name=model_option)
                    st.session_state["receipt_result"] = result_data
                except Exception as e:
                    st.error(f"Gagal mengekstrak struk: {e}")

    if "receipt_result" in st.session_state:
        res: ReceiptData = st.session_state["receipt_result"]
        curr = res.currency

        # Merchant Information Card
        st.markdown(f"""
        <div class="merchant-card">
            <span class="badge-cat">{res.category}</span>
            <h3 style="margin: 8px 0 4px 0; color: #1b5e20;">{res.merchant_name}</h3>
            <p style="margin: 0; color: #555; font-size: 0.9rem;">📍 {res.merchant_address or 'Alamat tidak tertera'}</p>
            <p style="margin: 0; color: #555; font-size: 0.9rem;">🧾 No. Invoice: <code>{res.invoice_number or '-'}</code> | 📅 {res.transaction_date or '-'} {res.transaction_time or ''}</p>
            <p style="margin: 4px 0 0 0; color: #2e7d32; font-weight: bold;">💳 Metode: {res.payment_method or '-'} ({res.payment_status})</p>
        </div>
        """, unsafe_allow_html=True)

        # Metrics Row
        m1, m2, m3, m4 = st.columns(4)
        m1.metric("Subtotal", format_curr(res.subtotal, curr))
        m2.metric("Pajak / PB1", format_curr(res.tax_amount, curr))
        m3.metric("Diskon", f"-{format_curr(res.discount_amount, curr)}" if res.discount_amount > 0 else "Rp 0")
        m4.metric("Grand Total", format_curr(res.total_amount, curr))

        # Tabs for Items, Math verification, Export, JSON
        tab_items, tab_export, tab_json = st.tabs([
            f"🛒 Line Items ({len(res.items)} produk)",
            "📥 Export Data",
            "💻 Raw JSON"
        ])

        with tab_items:
            if res.items:
                df_items = pd.DataFrame([{
                    "Nama Item": it.item_name,
                    "Kuantitas": f"{it.quantity:g}",
                    "Harga Satuan": format_curr(it.unit_price, curr),
                    "Total Harga": format_curr(it.total_price, curr)
                } for it in res.items])
                
                st.dataframe(df_items, use_container_width=True, hide_index=True)
            else:
                st.info("Tidak ada line items yang terdeteksi.")

            if res.math_verification_notes:
                st.caption(f"ℹ️ Verifikasi Matematis: {res.math_verification_notes}")

        with tab_export:
            st.markdown("### Export untuk Laporan Keuangan:")
            col_ex1, col_ex2 = st.columns(2)
            
            with col_ex1:
                # CSV Export of items
                df_raw = pd.DataFrame([it.model_dump() for it in res.items])
                st.download_button(
                    "📥 Download Items (CSV)",
                    data=df_raw.to_csv(index=False).encode('utf-8'),
                    file_name=f"receipt_{res.invoice_number or 'items'}.csv",
                    mime="text/csv",
                    use_container_width=True
                )

            with col_ex2:
                # Full JSON Export
                st.download_button(
                    "💾 Download Full Receipt (JSON)",
                    data=res.model_dump_json(indent=2),
                    file_name=f"receipt_{res.invoice_number or 'data'}.json",
                    mime="application/json",
                    use_container_width=True
                )

        with tab_json:
            st.json(res.model_dump())
    else:
        st.info("👈 Pilih atau unggah gambar struk di sebelah kiri, lalu klik **'Ekstrak Data dari Struk'**.")
