"""
Day 07 - Interactive Prompt Engineering Playground (Streamlit Web App)
Antarmuka Web Interaktif untuk eksplorasi prompt engineering, parameter tuning,
A/B testing perbandingan prompt, optimasi prompt otomatis, dan export kode Python.
"""

import os
import sys
import json
from pathlib import Path
import streamlit as st

# Pastikan modul internal terbaca
sys.path.append(str(Path(__file__).parent))
from engine import (
    run_prompt_inference,
    optimize_prompt,
    extract_variables_from_template,
    generate_python_snippet,
    ExecutionResult,
    PromptOptimizationResult
)

PRESETS_FILE = Path(__file__).parent / "presets.json"

st.set_page_config(
    page_title="Prompt Engineering Playground | Day 07",
    page_icon="🧪",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom Styling
st.markdown("""
<style>
    .metric-box {
        background-color: #f8f9fa;
        border-radius: 8px;
        padding: 12px;
        border: 1px solid #e0e0e0;
        text-align: center;
    }
    .prompt-box {
        background-color: #f1f8e9;
        border-left: 5px solid #558b2f;
        padding: 15px;
        border-radius: 8px;
        margin-bottom: 12px;
    }
    .var-badge {
        background-color: #e0f2f1;
        color: #004d40;
        padding: 2px 8px;
        border-radius: 12px;
        font-size: 0.8rem;
        font-family: monospace;
    }
</style>
""", unsafe_allow_html=True)

def load_presets():
    if PRESETS_FILE.exists():
        return json.loads(PRESETS_FILE.read_text(encoding="utf-8"))
    return []

# Sidebar
with st.sidebar:
    st.title("⚙️ Hyperparameters")
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

    temp_val = st.slider(
        "Temperature",
        min_value=0.0,
        max_value=2.0,
        value=0.7,
        step=0.05,
        help="0.0 = Paling deterministik & faktual, 1.0+ = Lebih kreatif & bervariasi"
    )

    top_p_val = st.slider(
        "Top-P (Nucleus Sampling)",
        min_value=0.0,
        max_value=1.0,
        value=0.95,
        step=0.05,
        help="Probabilitas kumulatif pemotongan token"
    )

    max_tokens_val = st.slider(
        "Max Output Tokens",
        min_value=100,
        max_value=4096,
        value=1024,
        step=64
    )

    st.divider()
    st.markdown("### 📌 Tentang Proyek")
    st.markdown("""
    **Day 07 dari 30 Days of AI Challenge**
    - Dynamic Variable Templating `{{var}}`
    - A/B Side-by-Side Prompt Comparison
    - Automated AI Prompt Optimizer
    - Python Code Snippet Generator
    """)

# Main Content
st.title("🧪 AI Prompt Engineering Playground & Studio")
st.markdown("Eksperimen parameter LLM, uji variabel dinamis, bandingkan A/B prompt, dan optimalkan instruksi prompt Anda.")

tab_sandbox, tab_ab_test, tab_optimizer, tab_library = st.tabs([
    "🎛️ Prompt Sandbox & Variables",
    "⚔️ A/B Prompt Comparator",
    "🚀 AI Prompt Optimizer",
    "📚 Template Library"
])

# ----------------- TAB 1: PROMPT SANDBOX -----------------
with tab_sandbox:
    col_sb1, col_sb2 = st.columns([1, 1], gap="large")

    with col_sb1:
        st.subheader("📥 Prompt Configuration")

        presets = load_presets()
        preset_names = ["-- Pilih Template Siap Pakai --"] + [p["name"] for p in presets]
        selected_preset = st.selectbox("Load Preset:", preset_names)

        default_sys = ""
        default_user = "Jelaskan konsep {{konsep}} kepada anak umur {{umur}} tahun menggunakan analogi sederhana."
        
        if selected_preset != "-- Pilih Template Siap Pakai --":
            p_data = next(p for p in presets if p["name"] == selected_preset)
            default_sys = p_data.get("system_instruction", "")
            default_user = p_data.get("prompt_template", "")

        system_instruction = st.text_area(
            "System Instruction (Persona & Role):",
            value=default_sys,
            height=100,
            placeholder="Kamu adalah asisten AI ahli di bidang..."
        )

        user_prompt_template = st.text_area(
            "User Prompt Template (Gunakan {{nama_variabel}} untuk dynamic input):",
            value=default_user,
            height=180
        )

        # Dynamic variable inputs
        detected_vars = extract_variables_from_template(user_prompt_template)
        var_values = {}
        if detected_vars:
            st.markdown("##### 🧩 Variabel Dinamis Terdeteksi:")
            cols_vars = st.columns(min(len(detected_vars), 3))
            for i, var_name in enumerate(detected_vars):
                c = cols_vars[i % len(cols_vars)]
                var_values[var_name] = c.text_input(f"`{{{{{var_name}}}}}`", value=f"contoh {var_name}", key=f"var_{var_name}")

        run_btn = st.button("🚀 Jalankan Prompt", type="primary", use_container_width=True)

    with col_sb2:
        st.subheader("📊 Model Output & Metrics")

        if run_btn:
            if not user_prompt_template.strip():
                st.warning("Prompt tidak boleh kosong!")
            elif not os.getenv("GEMINI_API_KEY"):
                st.error("🔑 API Key belum diatur! Masukkan GEMINI_API_KEY di sidebar atau file .env")
            else:
                with st.spinner("🤖 Mengirim prompt ke Gemini AI..."):
                    try:
                        res: ExecutionResult = run_prompt_inference(
                            prompt_template=user_prompt_template,
                            variables=var_values,
                            system_instruction=system_instruction,
                            model_name=model_option,
                            temperature=temp_val,
                            top_p=top_p_val,
                            max_output_tokens=max_tokens_val
                        )
                        st.session_state["sandbox_result"] = res
                        st.session_state["current_vars"] = var_values
                        st.session_state["current_sys"] = system_instruction
                        st.session_state["current_user"] = user_prompt_template
                    except Exception as e:
                        st.error(f"Error eksekusi prompt: {e}")

        if "sandbox_result" in st.session_state:
            res: ExecutionResult = st.session_state["sandbox_result"]
            m = res.metrics

            # Metrics Row
            m1, m2, m3, m4 = st.columns(4)
            m1.metric("Latency", f"{m.latency_ms:.0f} ms")
            m2.metric("Panjang Output", f"{m.output_word_count} kata")
            m3.metric("Temperature", f"{m.temperature}")
            m4.metric("Model", m.model_used)

            st.markdown("### Respon Model:")
            st.markdown(res.output_text)

            # Code generator expander
            with st.expander("🐍 Lihat Kode Python SDK Siap Pakai"):
                snippet = generate_python_snippet(
                    prompt_template=st.session_state.get("current_user", user_prompt_template),
                    system_instruction=st.session_state.get("current_sys", system_instruction),
                    variables=st.session_state.get("current_vars", var_values),
                    temperature=temp_val,
                    top_p=top_p_val,
                    model_name=model_option
                )
                st.code(snippet, language="python")
        else:
            st.info("👈 Sesuaikan prompt di sebelah kiri lalu klik **'Jalankan Prompt'**.")

# ----------------- TAB 2: A/B TESTING -----------------
with tab_ab_test:
    st.subheader("⚔️ A/B Prompt Comparator (Battle Mode)")
    st.markdown("Bandingkan dua variasi prompt yang berbeda pada konteks/input yang sama secara bersamaan.")

    col_ab_input = st.text_input("Input Data Uji Bersama ({{input_data}}):", value="Bagaimana cara kerja Docker Container?")

    col_a, col_b = st.columns(2, gap="large")

    with col_a:
        st.markdown("### 🅰️ Variasi Prompt A")
        sys_a = st.text_area("System Instruction A:", value="Kamu adalah asisten teknis yang ringkas.", height=80, key="sys_a")
        prompt_a = st.text_area("User Prompt A:", value="Jelaskan dalam 2 poin singkat: {{input_data}}", height=100, key="prompt_a")
        temp_a = st.slider("Temperature A", 0.0, 1.5, 0.2, key="temp_a")

    with col_b:
        st.markdown("### 🅱️ Variasi Prompt B")
        sys_b = st.text_area("System Instruction B:", value="Kamu adalah edukator yang menggunakan analogi rumah dan apartemen.", height=80, key="sys_b")
        prompt_b = st.text_area("User Prompt B:", value="Jelaskan konsep ini dengan analogi kehidupan sehari-hari: {{input_data}}", height=100, key="prompt_b")
        temp_b = st.slider("Temperature B", 0.0, 1.5, 0.8, key="temp_b")

    if st.button("⚡ Jalankan A/B Test Bersamaan", type="primary", use_container_width=True):
        if not os.getenv("GEMINI_API_KEY"):
            st.error("🔑 API Key belum diatur!")
        else:
            with st.spinner("🤖 Menjalankan evaluasi A/B testing..."):
                try:
                    res_a = run_prompt_inference(
                        prompt_template=prompt_a,
                        variables={"input_data": col_ab_input},
                        system_instruction=sys_a,
                        model_name=model_option,
                        temperature=temp_a
                    )
                    res_b = run_prompt_inference(
                        prompt_template=prompt_b,
                        variables={"input_data": col_ab_input},
                        system_instruction=sys_b,
                        model_name=model_option,
                        temperature=temp_b
                    )

                    st.divider()
                    col_res_a, col_res_b = st.columns(2, gap="large")

                    with col_res_a:
                        st.success(f"**Output A** (⏱️ {res_a.metrics.latency_ms:.0f} ms | {res_a.metrics.output_word_count} kata)")
                        st.markdown(res_a.output_text)

                    with col_res_b:
                        st.info(f"**Output B** (⏱️ {res_b.metrics.latency_ms:.0f} ms | {res_b.metrics.output_word_count} kata)")
                        st.markdown(res_b.output_text)

                except Exception as e:
                    st.error(f"Error A/B testing: {e}")

# ----------------- TAB 3: AI PROMPT OPTIMIZER -----------------
with tab_optimizer:
    st.subheader("🚀 AI Prompt Optimizer & Refiner")
    st.markdown("Masukkan draft prompt biasa, dan biarkan AI Prompt Engineering Specialist mendesain ulang dengan teknik terbaik (Role, Context, Delimiters, & Output constraints).")

    raw_input_prompt = st.text_area(
        "Masukkan Draft Prompt Anda:",
        value="Buatkan artikel tentang AI untuk pemula",
        height=120
    )
    opt_goal = st.text_input("Tujuan Khusus (Opsional):", value="Lebih terstruktur, aplikatif, dan menyertakan contoh nyata")

    if st.button("✨ Optimalkan Prompt Saya", type="primary", use_container_width=True):
        if not os.getenv("GEMINI_API_KEY"):
            st.error("🔑 API Key belum diatur!")
        else:
            with st.spinner("🤖 Menganalisis & menyempurnakan struktur prompt..."):
                try:
                    opt_res: PromptOptimizationResult = optimize_prompt(
                        raw_prompt=raw_input_prompt,
                        goal=opt_goal,
                        model_name=model_option
                    )

                    st.success("🎉 Prompt berhasil dioptimalkan!")
                    
                    st.markdown("### 🛡️ System Instruction Baru:")
                    st.code(opt_res.optimized_system_instruction)

                    st.markdown("### 📝 User Prompt Baru:")
                    st.code(opt_res.optimized_user_prompt)

                    st.markdown("### 💡 Poin-Poin Peningkatan:")
                    for imp in opt_res.key_improvements:
                        st.markdown(f"- {imp}")

                    st.caption(f"Rekomendasi Temperature: `{opt_res.recommended_temperature}`")

                except Exception as e:
                    st.error(f"Error optimasi: {e}")

# ----------------- TAB 4: TEMPLATE LIBRARY -----------------
with tab_library:
    st.subheader("📚 Curated Prompt Template Library")
    presets = load_presets()

    for p in presets:
        with st.expander(f"📌 {p['name']} — {p['description']}", expanded=True):
            if p.get("system_instruction"):
                st.markdown(f"**System:** `{p['system_instruction']}`")
            st.code(p["prompt_template"])
            st.caption(f"Default Temperature: `{p.get('temperature', 0.7)}` | Top-P: `{p.get('top_p', 0.95)}`")
