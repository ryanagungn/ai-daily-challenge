"""
Day 13: Local LLM Offline Runner - Streamlit Web UI
Aplikasi web untuk inferensi AI lokal (Ollama / Local Server)
dengan privasi penuh, streaming real-time, dan pengukuran kecepatan tokens/detik.
"""

import time
import streamlit as st
import pandas as pd
from local_engine import LocalLLMEngine, ServerStatus, GenerationMetrics

# 1. Konfigurasi Halaman
st.set_page_config(
    page_title="Day 13 - Local LLM Offline Runner",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 2. Inisialisasi Session State
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

if "server_url" not in st.session_state:
    st.session_state.server_url = "http://localhost:11434"

if "last_metrics" not in st.session_state:
    st.session_state.last_metrics = None

# Custom CSS
st.markdown("""
<style>
    .metric-badge {
        display: inline-block;
        padding: 4px 12px;
        border-radius: 16px;
        background-color: #1E293B;
        color: #38BDF8;
        font-weight: 600;
        font-size: 0.85rem;
        margin-right: 8px;
        border: 1px solid #334155;
    }
    .status-online {
        color: #22C55E;
        font-weight: bold;
    }
    .status-simulated {
        color: #F59E0B;
        font-weight: bold;
    }
    .card-box {
        padding: 16px;
        border-radius: 8px;
        background-color: #0F172A;
        border: 1px solid #1E293B;
        margin-bottom: 12px;
    }
</style>
""", unsafe_allow_html=True)


# 3. Sidebar: Konfigurasi Koneksi & Model
with st.sidebar:
    st.title("🤖 Local LLM Runner")
    st.caption("Day 13 of 30 Days AI Challenge")
    st.divider()

    st.subheader("🔌 Server Connection")
    server_input = st.text_input(
        "Local Server URL",
        value=st.session_state.server_url,
        help="Default Ollama: http://localhost:11434 | LM Studio: http://localhost:1234/v1"
    )

    col_btn1, col_btn2 = st.columns([1, 1])
    with col_btn1:
        refresh_btn = st.button("🔄 Cek Server", use_container_width=True)
    with col_btn2:
        clear_chat_btn = st.button("🗑️ Reset Chat", use_container_width=True)

    if clear_chat_btn:
        st.session_state.chat_history = []
        st.session_state.last_metrics = None
        st.rerun()

    st.session_state.server_url = server_input.strip()
    engine = LocalLLMEngine(base_url=st.session_state.server_url)
    status = engine.check_health()

    # Status Badge
    if status.connected:
        st.success(f"🟢 Terhubung ({status.server_type.upper()})")
    else:
        st.warning("🟡 Mode Simulasi Offline (Daemon Tidak Aktif)")
        st.caption("💡 Jalankan `ollama serve` di terminal untuk menghubungkan model fisik.")

    # Model Selection
    st.subheader("📦 Model Selector")
    model_options = [m.name for m in status.models]
    if not model_options:
        model_options = ["llama3.2:1b (Simulated)"]
    
    selected_model_name = st.selectbox("Pilih Model AI", options=model_options)

    # Tampilkan info model jika ada
    chosen_info = next((m for m in status.models if m.name == selected_model_name), None)
    if chosen_info:
        with st.expander("ℹ️ Spesifikasi Model", expanded=False):
            st.write(f"**Family:** {chosen_info.family}")
            st.write(f"**Parameter:** {chosen_info.parameter_size or '-'}")
            st.write(f"**Kuantisasi:** {chosen_info.quantization_level or '-'}")
            if chosen_info.size_gb > 0:
                st.write(f"**Ukuran Disk:** {chosen_info.size_gb} GB")

    st.divider()
    st.subheader("⚙️ Parameter Inferensi")
    temperature = st.slider("Temperature", 0.0, 1.5, 0.7, 0.05, help="Tingkat kreativitas model")
    force_simulated = st.checkbox("Paksa Mode Simulasi", value=False, help="Gunakan engine simulasi meskipun server aktif")
    system_prompt = st.text_area(
        "System Prompt (Opsional)",
        placeholder="Contoh: Anda adalah asisten AI teknis yang ringkas dan akurat...",
        height=80
    )


# 4. Header Utama
st.title("🤖 Local LLM Offline Runner")
st.markdown(
    "**Inference AI 100% On-Device**: Tanpa Cloud API, Zero Biaya Token, dan Privasi Data Maksimal. "
    "Dilengkapi streaming real-time serta kalkulasi throughput **Tokens Per Second (t/s)**."
)

tab_chat, tab_bench, tab_guide = st.tabs([
    "💬 Chat & Live Streaming",
    "⚡ Benchmark Throughput (Tokens/s)",
    "🛡️ Panduan & Arsitektur Local AI"
])


# ==========================================
# TAB 1: CHAT & LIVE STREAMING
# ==========================================
with tab_chat:
    # Tampilkan prompt cepat jika chat masih kosong
    if not st.session_state.chat_history:
        st.markdown("##### 💡 Coba Pertanyaan Populer:")
        col1, col2, col3 = st.columns(3)
        with col1:
            if st.button("🧠 Jelaskan Arsitektur Transformer", use_container_width=True):
                st.session_state.chat_history.append({"role": "user", "content": "Jelaskan konsep arsitektur Transformer secara ringkas"})
                st.rerun()
        with col2:
            if st.button("🔒 Keuntungan Local AI vs Cloud", use_container_width=True):
                st.session_state.chat_history.append({"role": "user", "content": "Apa saja keuntungan privasi dan biaya menggunakan Local LLM dibanding Cloud AI?"})
                st.rerun()
        with col3:
            if st.button("⚡ Cara Setup Ollama di Laptop", use_container_width=True):
                st.session_state.chat_history.append({"role": "user", "content": "Bagaimana cara setup dan pull model di Ollama?"})
                st.rerun()

    # Render Riwayat Chat
    for msg in st.session_state.chat_history:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])
            if msg.get("metrics"):
                m = msg["metrics"]
                st.caption(
                    f"⚡ **{m['tokens_per_sec']} t/s** | ⏱️ TTFT: **{m['ttft_sec']*1000:.0f}ms** | "
                    f"📦 **{m['eval_tokens']} tokens** | ⏳ **{m['total_duration_sec']}s**"
                )

    # Input Chat
    user_prompt = st.chat_input("Ketik pesan atau pertanyaan untuk model lokal...")
    if user_prompt:
        # Simpan user message
        st.session_state.chat_history.append({"role": "user", "content": user_prompt})
        with st.chat_message("user"):
            st.markdown(user_prompt)

        # Generate respons dengan live streaming
        with st.chat_message("assistant"):
            response_container = st.empty()
            metrics_container = st.empty()
            full_response = ""
            final_metrics: GenerationMetrics = None

            # Stream generator
            stream_gen = engine.stream_chat(
                model=selected_model_name,
                messages=st.session_state.chat_history,
                system_prompt=system_prompt if system_prompt.strip() else None,
                temperature=temperature,
                force_simulated=force_simulated
            )

            for chunk, metrics in stream_gen:
                if chunk:
                    full_response += chunk
                    response_container.markdown(full_response + " ▌")
                if metrics:
                    final_metrics = metrics

            response_container.markdown(full_response)

            if final_metrics:
                m_dict = final_metrics.to_dict()
                metrics_container.caption(
                    f"⚡ **{m_dict['tokens_per_sec']} t/s** | ⏱️ TTFT: **{m_dict['ttft_sec']*1000:.0f}ms** | "
                    f"📦 **{m_dict['eval_tokens']} tokens** | ⏳ **{m_dict['total_duration_sec']}s** | "
                    f"🖥️ Mode: {'Simulated' if m_dict['is_simulated'] else 'Local Hardware'}"
                )
                st.session_state.chat_history.append({
                    "role": "assistant",
                    "content": full_response,
                    "metrics": m_dict
                })
                st.session_state.last_metrics = m_dict
            else:
                st.session_state.chat_history.append({
                    "role": "assistant",
                    "content": full_response
                })


# ==========================================
# TAB 2: BENCHMARK THROUGHPUT (TOKENS/S)
# ==========================================
with tab_bench:
    st.subheader("⚡ Pengujian Kecepatan & Latensi Model")
    st.markdown(
        "Jalankan uji beban standar untuk mengukur **Throughput generasi (Tokens Per Second)** dan "
        "**Time to First Token (TTFT)** pada perangkat keras Anda saat ini."
    )

    bench_prompt = st.text_area(
        "Benchmark Test Prompt",
        value="Jelaskan konsep Kuantisasi 4-bit (GGUF Q4_K_M) pada model AI lokal dan pengaruhnya terhadap konsumsi VRAM dalam 2 paragraf padat.",
        height=100
    )

    if st.button("🚀 Mulai Uji Benchmark", type="primary"):
        with st.spinner(f"Menjalankan benchmark inferensi pada '{selected_model_name}'..."):
            res = engine.run_benchmark(
                model=selected_model_name,
                benchmark_prompt=bench_prompt,
                system_prompt=system_prompt if system_prompt.strip() else None
            )

        m = res["metrics"]
        st.success("✅ Benchmark Selesai!")

        # 4 Metric Cards
        col_m1, col_m2, col_m3, col_m4 = st.columns(4)
        with col_m1:
            st.metric("⚡ Throughput", f"{m['tokens_per_sec']} t/s", delta="Generasi Kecepatan")
        with col_m2:
            st.metric("⏱️ TTFT (Latensi Awal)", f"{m['ttft_sec']*1000:.0f} ms", delta="- Responsiveness")
        with col_m3:
            st.metric("📦 Output Tokens", f"{m['eval_tokens']} tok", delta="Panjang Respons")
        with col_m4:
            st.metric("⏳ Total Waktu", f"{m['total_duration_sec']} s", delta="Wall Clock Time")

        st.divider()

        # Preview output & benchmark analysis
        st.markdown("##### 📝 Preview Keluaran Benchmark:")
        st.info(res["output_preview"])

        # Klasifikasi Kecepatan
        tps = m["tokens_per_sec"]
        if tps >= 50:
            rating = "🚀 **Sangat Cepat (Blazing Fast)**: Setara GPU modern (RTX 40-series atau Apple M-series Max/Pro)."
        elif tps >= 25:
            rating = "⚡ **Cepat & Responsif**: Nyaman untuk percakapan real-time tanpa jeda menunggu."
        elif tps >= 10:
            rating = "⏳ **Standar / CPU-Bound**: Tipikal CPU laptop tanpa akselerasi CUDA VRAM."
        else:
            rating = "🐢 **Lambat**: Model terlalu besar untuk kapasitas RAM/VRAM yang tersedia."

        st.markdown(f"**Analisis Performa:** {rating}")


# ==========================================
# TAB 3: PANDUAN & ARSITEKTUR LOCAL AI
# ==========================================
with tab_guide:
    st.subheader("🛡️ Mengapa Local AI Menjadi Standar Privasi Modern?")
    
    col_g1, col_g2 = st.columns(2)
    with col_g1:
        st.markdown("""
        ### ⚖️ Perbandingan: Local LLM vs Cloud AI

        | Parameter | Local LLM (Ollama) | Cloud AI (OpenAI/Anthropic) |
        |---|---|---|
        | **Privasi Data** | 🔒 **100% On-Device**, Zero Leakage | ☁️ Ditransmisikan ke server pihak ketiga |
        | **Biaya Operasional** | 🆓 **Rp 0 / Bebas Biaya Token** | 💳 Bayar per 1,000 token input/output |
        | **Ketergantungan Internet** | 📶 **Offline Penuh** (Bisa di hutan/pesawat) | ❌ Wajib koneksi internet stabil |
        | **Regulasi Keamanan** | ✅ Memenuhi syarat GDPR, HIPAA, Perbankan | ⚠️ Butuh Enterprise DPA khusus |
        | **Latensi Jaringan** | ⚡ **0 ms Network Lag** | 🌐 300ms - 1500ms RTT latency |
        """)

    with col_g2:
        st.markdown("""
        ### 📦 Memahami Kuantisasi GGUF & Kebutuhan RAM

        Kuantisasi adalah proses kompresi bobot parameter model dari presisi tinggi (FP16) menjadi presisi lebih ringkas (4-bit atau 8-bit) dengan degradasi akurasi yang hampir tidak terlihat.

        * **Model 1B-3B Parameter (e.g. Llama-3.2 1B, Qwen-2.5 3B)**:
          * RAM Minimal: **4 GB RAM**
          * Cocok untuk: Laptop standar, Raspberry Pi, perangkat edge.
        * **Model 7B-8B Parameter (e.g. Mistral 7B, Llama-3.1 8B)**:
          * RAM Minimal: **8 - 16 GB RAM** (atau 6GB VRAM GPU)
          * Cocok untuk: Coding, penalaran logis, summarization panjang.
        * **Model Reasoning (e.g. DeepSeek-R1 Distill 1.5B/7B)**:
          * Model penalaran dengan Chain-of-Thought mandiri.
        """)

    st.divider()
    st.markdown("""
    ### 💻 Panduan Cepat Menjalankan Ollama:
    
    ```bash
    # 1. Pastikan Ollama daemon aktif
    ollama serve

    # 2. Unduh model ringan dalam sekejap
    ollama pull llama3.2:1b
    ollama pull deepseek-r1:1.5b

    # 3. Verifikasi model yang terpasang
    ollama list
    ```
    """)
