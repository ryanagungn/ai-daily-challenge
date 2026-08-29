"""
Day 03 - Natural Language to SQL (Streamlit Web App)
Antarmuka Web Interaktif untuk eksplorasi database dengan bahasa alami, visualisasi otomatis, dan eksekusi SQL.
"""

import os
import sys
import json
import sqlite3
import pandas as pd
from pathlib import Path
import streamlit as st

# Pastikan modul internal terbaca
sys.path.append(str(Path(__file__).parent))
from database import init_database, get_connection, execute_query, get_schema_description
from sql_engine import generate_sql_from_natural_language, validate_sql_safety, SQLGenerationResult

# Inisialisasi Database
init_database()

st.set_page_config(
    page_title="Text to SQL Analytics | Day 03",
    page_icon="🗄️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom Styling
st.markdown("""
<style>
    .metric-badge {
        background-color: #e8f5e9;
        color: #2e7d32;
        padding: 4px 10px;
        border-radius: 8px;
        font-weight: bold;
    }
    .insight-card {
        background-color: #f8f9fa;
        border-left: 5px solid #0288d1;
        padding: 15px;
        border-radius: 8px;
        margin-top: 10px;
    }
</style>
""", unsafe_allow_html=True)

# Preset Questions
PRESET_QUESTIONS = [
    "Siapa 5 pelanggan dengan total nilai belanja tertinggi?",
    "Berapa total pendapatan penjualan untuk setiap kategori produk?",
    "Tampilkan produk dengan sisa stok kurang dari 30 unit beserta kategorinya",
    "Berapa jumlah pesanan dan total nilai transaksi berdasarkan metode pembayaran?",
    "Tampilkan daftar pesanan yang statusnya 'completed' dari kota Jakarta",
    "Apa produk paling laris berdasarkan total kuantitas terjual?"
]

# Sidebar
with st.sidebar:
    st.title("⚙️ Pengaturan AI & DB")
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
    st.subheader("🗄️ Penjelajah Skema Database")
    
    conn = get_connection()
    tables = ["categories", "products", "customers", "orders", "order_items"]
    selected_table = st.selectbox("Pilih Tabel untuk Preview Data", tables)
    
    df_preview = pd.read_sql_query(f"SELECT * FROM {selected_table} LIMIT 5", conn)
    st.dataframe(df_preview, use_container_width=True, hide_index=True)
    conn.close()

    with st.expander("📄 DDL Skema Lengkap"):
        st.code(get_schema_description(), language="sql")

    st.divider()
    st.markdown("### 📌 Tentang Proyek")
    st.markdown("""
    **Day 03 dari 30 Days of AI Challenge**
    - Natural Language to SQL (Text2SQL)
    - Query Safety & Injection Prevention
    - Automated Data Visualization
    - Business Intelligence & Insights
    """)

# Main Content
st.title("🗄️ AI Natural Language to SQL Analytics")
st.markdown("Eksplorasi data penjualan dan insight bisnis e-commerce cukup dengan mengetik pertanyaan dalam bahasa manusia.")

# Preset buttons
st.markdown("##### 💡 Contoh Pertanyaan Cepat:")
cols_presets = st.columns(3)
for idx, q in enumerate(PRESET_QUESTIONS):
    col = cols_presets[idx % 3]
    if col.button(f"📌 {q}", key=f"btn_preset_{idx}", use_container_width=True):
        st.session_state["user_question"] = q

# Input Query
user_question = st.text_input(
    "Ajukan pertanyaan tentang data e-commerce:",
    value=st.session_state.get("user_question", "Siapa 5 pelanggan dengan total nilai belanja tertinggi?"),
    placeholder="Ketik pertanyaan analitik di sini..."
)

col_run1, col_run2 = st.columns([1, 4])
with col_run1:
    run_btn = st.button("🚀 Buat & Jalankan SQL", type="primary", use_container_width=True)

if run_btn or "last_sql_result" in st.session_state:
    if run_btn:
        if not user_question.strip():
            st.warning("Silakan masukkan pertanyaan terlebih dahulu!")
        elif not os.getenv("GEMINI_API_KEY"):
            st.error("🔑 API Key belum diatur! Masukkan GEMINI_API_KEY di sidebar atau file .env")
        else:
            with st.spinner("🤖 Menerjemahkan pertanyaan ke SQL SQLite dengan Gemini AI..."):
                try:
                    sql_res: SQLGenerationResult = generate_sql_from_natural_language(
                        user_question, model_name=model_option
                    )
                    st.session_state["last_sql_result"] = sql_res
                    st.session_state["edited_sql"] = sql_res.sql_query
                except Exception as e:
                    st.error(f"Gagal generate SQL: {e}")

    if "last_sql_result" in st.session_state:
        sql_res: SQLGenerationResult = st.session_state["last_sql_result"]

        st.divider()
        col_sql, col_data = st.columns([1, 1], gap="large")

        with col_sql:
            st.subheader("⚡ Generated SQL Query")
            
            # Interactive SQL Editor
            edited_sql = st.text_area(
                "SQL Query (dapat diedit manual):",
                value=st.session_state.get("edited_sql", sql_res.sql_query),
                height=160
            )

            col_sub1, col_sub2 = st.columns(2)
            with col_sub1:
                rerun_sql = st.button("🔄 Eksekusi Ulang SQL", use_container_width=True)
            with col_sub2:
                is_safe, _ = validate_sql_safety(edited_sql)
                if is_safe:
                    st.success("🛡️ Query Safe (Read-Only)")
                else:
                    st.error("⚠️ Query Unsafe / Destructive")

            # Explanation & Insights Card
            st.markdown(f"""
            <div class="insight-card">
                <h4>🧠 Penjelasan Logika Query:</h4>
                <p>{sql_res.explanation}</p>
                <hr style="margin: 8px 0;">
                <h4>📈 Insight Bisnis:</h4>
                <p>{sql_res.business_insights}</p>
            </div>
            """, unsafe_allow_html=True)

        with col_data:
            st.subheader("📊 Hasil Query Database")
            
            try:
                columns, rows, elapsed_ms = execute_query(edited_sql)
                
                # Metrics
                m1, m2, m3 = st.columns(3)
                m1.metric("Total Baris", f"{len(rows)} data")
                m2.metric("Waktu Eksekusi", f"{elapsed_ms:.2f} ms")
                m3.metric("Tabel Digunakan", ", ".join(sql_res.tables_used) if sql_res.tables_used else "SQLite")

                if rows:
                    df_result = pd.DataFrame(rows)
                    
                    # Display Table & Chart Tabs
                    tab_table, tab_chart, tab_json = st.tabs(["📋 Tabel Data", "📈 Visualisasi Grafik", "💻 Raw JSON"])
                    
                    with tab_table:
                        st.dataframe(df_result, use_container_width=True, hide_index=True)
                        
                        # Download CSV
                        csv = df_result.to_csv(index=False).encode('utf-8')
                        st.download_button(
                            "📥 Download CSV",
                            csv,
                            "query_results.csv",
                            "text/csv",
                            use_container_width=True
                        )

                    with tab_chart:
                        # Auto Chart rendering
                        x_col = sql_res.x_axis_column if sql_res.x_axis_column in df_result.columns else df_result.columns[0]
                        numeric_cols = df_result.select_dtypes(include=['float64', 'int64', 'float', 'int']).columns.tolist()
                        
                        if numeric_cols:
                            y_col = sql_res.y_axis_column if (sql_res.y_axis_column in numeric_cols) else numeric_cols[0]
                            st.caption(f"Visualisasi Otomatis: `{x_col}` vs `{y_col}`")
                            
                            chart_type = sql_res.chart_recommendation
                            if chart_type in ["bar_chart", "pie_chart"] or len(df_result) <= 15:
                                chart_df = df_result.set_index(x_col)[[y_col]]
                                st.bar_chart(chart_df)
                            elif chart_type == "line_chart":
                                chart_df = df_result.set_index(x_col)[[y_col]]
                                st.line_chart(chart_df)
                            else:
                                chart_df = df_result.set_index(x_col)[[y_col]]
                                st.area_chart(chart_df)
                        else:
                            st.info("Visualisasi grafik hanya tersedia jika query mengembalikan kolom angka numerik.")

                    with tab_json:
                        st.json(rows)

                else:
                    st.info("Query berhasil dijalankan, namun tidak ada data yang cocok dengan kriteria.")

            except Exception as e:
                st.error(f"Gagal mengeksekusi SQL: {e}")
