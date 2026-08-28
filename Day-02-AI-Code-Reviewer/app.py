"""
Day 02 - AI Code Reviewer & Refactor Assistant (Streamlit Web App)
Antarmuka Web Interaktif untuk audit keamanan kode, deteksi bug, dan refactoring otomatis.
"""

import os
import sys
import json
from pathlib import Path
import streamlit as st

# Pastikan path modul reviewer terbaca
sys.path.append(str(Path(__file__).parent))
from reviewer import review_code, CodeReviewResult

st.set_page_config(
    page_title="AI Code Reviewer | Day 02",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom Styling
st.markdown("""
<style>
    .issue-critical { border-left: 5px solid #dc3545; padding: 10px; background-color: #fff5f5; border-radius: 6px; margin-bottom: 8px; }
    .issue-high { border-left: 5px solid #fd7e14; padding: 10px; background-color: #fffaf0; border-radius: 6px; margin-bottom: 8px; }
    .issue-medium { border-left: 5px solid #ffc107; padding: 10px; background-color: #fffdf0; border-radius: 6px; margin-bottom: 8px; }
    .issue-low { border-left: 5px solid #0d6efd; padding: 10px; background-color: #f0f7ff; border-radius: 6px; margin-bottom: 8px; }
    .badge { display: inline-block; padding: 2px 8px; border-radius: 12px; font-size: 0.75rem; font-weight: bold; margin-right: 6px; }
</style>
""", unsafe_allow_html=True)

# Preset Examples
SAMPLE_PYTHON = '''import sqlite3

def get_user_data(user_id, is_admin=[]):
    # Bug 1: Mutable default argument
    # Bug 2: SQL Injection vulnerability
    conn = sqlite3.connect("users.db")
    cursor = conn.cursor()
    
    query = "SELECT * FROM users WHERE id = '" + user_id + "'"
    cursor.execute(query)
    data = cursor.fetchall()
    
    # Bug 3: Connection not closed properly
    return data

def calculate_duplicates(items):
    # Inefficient O(N^2) algorithm
    duplicates = []
    for i in range(len(items)):
        for j in range(i + 1, len(items)):
            if items[i] == items[j] and items[i] not in duplicates:
                duplicates.append(items[i])
    return duplicates
'''

SAMPLE_JS = '''// Sample Insecure & Buggy JavaScript
function processPayment(user, amount) {
    const API_SECRET = "sk_live_98374928374928374"; // Hardcoded Secret
    
    // Insecure eval
    eval("var discount = " + user.discountFormula);
    
    // Floating point precision bug
    let total = amount + 0.1 + 0.2;
    
    fetch('/api/pay', {
        method: 'POST',
        body: JSON.stringify({ user, total, secret: API_SECRET })
    }); // Missing catch / async-await handling
}
'''

# Sidebar
with st.sidebar:
    st.title("⚙️ Pengaturan Reviewer")
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

    focus_option = st.selectbox(
        "Fokus Review",
        options=["General (All)", "Security Focus", "Performance Focus", "Clean Code/Refactor"],
        index=0
    )

    st.divider()
    st.markdown("### 📌 Tentang Proyek")
    st.markdown("""
    **Day 02 dari 30 Days of AI Challenge**
    - Static Code & Security Vulnerability Audit
    - Bug & Performance Bottleneck Detection
    - Full Clean Code Refactoring
    - Complexity Analysis (O-Notation)
    """)

# Main Content
st.title("🛡️ AI Code Reviewer & Refactor Assistant")
st.markdown("Audit keamanan kode, deteksi bug tersembunyi, optimasi performa, dan hasilkan kode bersih siap produksi.")

col1, col2 = st.columns([1, 1], gap="large")

with col1:
    st.subheader("📥 Input Kode Sumber")
    
    col_btn1, col_btn2 = st.columns(2)
    with col_btn1:
        if st.button("📄 Load Contoh Python (Buggy)", use_container_width=True):
            st.session_state["code_input"] = SAMPLE_PYTHON
    with col_btn2:
        if st.button("📄 Load Contoh JS (Insecure)", use_container_width=True):
            st.session_state["code_input"] = SAMPLE_JS

    input_tab1, input_tab2 = st.tabs(["✍️ Editor Kode", "📁 Upload File"])
    
    with input_tab1:
        code_text = st.text_area(
            "Masukkan kode sumber di bawah:",
            value=st.session_state.get("code_input", SAMPLE_PYTHON),
            height=320,
            placeholder="Tempel kode Python, JavaScript, TypeScript, Go, dll..."
        )

    with input_tab2:
        uploaded_file = st.file_uploader("Upload file kode (.py, .js, .ts, .go, .java, .cpp, .php)", type=["py", "js", "ts", "go", "java", "cpp", "php", "sql"])
        if uploaded_file is not None:
            code_text = uploaded_file.read().decode("utf-8")
            st.success(f"File '{uploaded_file.name}' berhasil dimuat!")

    review_btn = st.button("🚀 Mulai Audit & Review Kode", type="primary", use_container_width=True)

with col2:
    st.subheader("📊 Hasil Audit & Refactoring")

    if review_btn:
        if not code_text.strip():
            st.warning("Silakan masukkan kode sumber terlebih dahulu!")
        elif not os.getenv("GEMINI_API_KEY"):
            st.error("🔑 API Key belum diatur! Masukkan GEMINI_API_KEY di sidebar atau file .env")
        else:
            with st.spinner("Sedang menganalisis kode secara mendalam dengan Gemini AI..."):
                try:
                    result: CodeReviewResult = review_code(
                        code_content=code_text,
                        focus=focus_option,
                        model_name=model_option
                    )

                    # Score & Metric row
                    m1, m2, m3 = st.columns(3)
                    score_color = "🟢" if result.quality_score >= 8 else "🟡" if result.quality_score >= 5 else "🔴"
                    m1.metric("Kualitas Kode", f"{score_color} {result.quality_score} / 10")
                    m2.metric("Total Isu Ditemukan", f"{len(result.issues)} isu")
                    m3.metric("Bahasa", result.language)

                    st.info(f"📋 **Ringkasan:** {result.executive_summary}")

                    if result.time_complexity_before and result.time_complexity_after:
                        st.markdown(f"⏱️ **Kompleksitas Waktu:** `{result.time_complexity_before}` ➔ `{result.time_complexity_after}`")

                    # Tabs for results
                    tab_issues, tab_refactor, tab_changes, tab_json = st.tabs([
                        f"🐛 Daftar Isu ({len(result.issues)})",
                        "✨ Kode Refaktor",
                        "🔄 Poin Perubahan",
                        "💻 Raw JSON"
                    ])

                    with tab_issues:
                        if not result.issues:
                            st.success("🎉 Tidak ada masalah kritis yang terdeteksi!")
                        else:
                            for idx, issue in enumerate(result.issues, 1):
                                css_class = f"issue-{issue.severity.lower()}" if issue.severity.lower() in ["critical", "high", "medium", "low"] else "issue-low"
                                line_info = f" ({issue.line_number})" if issue.line_number else ""
                                st.markdown(f"""
                                <div class="{css_class}">
                                    <strong>#{idx} [{issue.severity.upper()}] {issue.category}{line_info}:</strong> {issue.title}<br>
                                    <small style="color: #555;">{issue.description}</small><br>
                                    <span style="color: #2e7d32; font-weight: 500;">💡 Solusi: {issue.suggestion}</span>
                                </div>
                                """, unsafe_allow_html=True)

                    with tab_refactor:
                        lang_code = result.language.lower()
                        if "python" in lang_code:
                            st.code(result.refactored_code, language="python")
                        elif "javascript" in lang_code or "js" in lang_code:
                            st.code(result.refactored_code, language="javascript")
                        elif "typescript" in lang_code or "ts" in lang_code:
                            st.code(result.refactored_code, language="typescript")
                        elif "go" in lang_code:
                            st.code(result.refactored_code, language="go")
                        else:
                            st.code(result.refactored_code)

                        st.download_button(
                            label="📥 Download Refactored Code",
                            data=result.refactored_code,
                            file_name=f"refactored_code.{uploaded_file.name.split('.')[-1] if uploaded_file else 'py'}",
                            mime="text/plain",
                            use_container_width=True
                        )

                    with tab_changes:
                        st.markdown("### Poin-Poin Perbaikan:")
                        for change in result.explanation_of_changes:
                            st.markdown(f"- {change}")

                    with tab_json:
                        st.json(result.model_dump())

                except Exception as e:
                    st.error(f"Terjadi kesalahan saat review: {e}")
    else:
        st.info("👈 Masukkan kode di panel kiri lalu klik tombol **'Mulai Audit & Review Kode'**.")
