import streamlit as st
import pandas as pd
from task_data import format_task_data
from llm_prompt import generate_summary

# --- Page Setup ---
st.set_page_config(page_title="Workfolio AI Summary", layout="wide")

# --- 🌈 Custom CSS: Fixed Gradient Background + Readable Foreground ---
st.markdown("""
    <style>
    /* 🌈 App background */
    .stApp {
        background: rgba(100, 100, 100, 0.1);
        font-family: 'Poppins', sans-serif;
        color: #1e293b;
    }

    /* Header */
    .main-header {
        text-align: center;
        color: #1e293b;
        padding: 2rem 0;
        margin-bottom: 2rem;
    }
    .main-header h1 {
        font-size: 2.4rem;
        font-weight: 700;
        margin-bottom: 0.3rem;
        background: linear-gradient(90deg, #2563eb, #9333ea);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }
    .main-header p {
        font-size: 1.1rem;
        color: #334155;
    }

    /* Card Containers */
    .glass-card {
        background: rgba(255, 255, 255, 0.8);
        backdrop-filter: blur(12px);
        border-radius: 20px;
        padding: 2rem;
        box-shadow: 0 8px 24px rgba(0,0,0,0.1);
        margin-bottom: 2rem;
        transition: transform 0.2s ease;
    }
    .glass-card:hover {
        transform: translateY(-3px);
    }

    /* Buttons */
    .stButton>button {
        border-radius: 10px !important;
        height: 3rem;
        background: linear-gradient(90deg, #2563eb, #9333ea) !important;
        color: white !important;
        font-weight: 600 !important;
        font-size: 1rem !important;
        border: none !important;
        box-shadow: 0 4px 10px rgba(0,0,0,0.15);
        transition: all 0.3s ease-in-out;
    }
    .stButton>button:hover {
        background: linear-gradient(90deg, #1d4ed8, #7e22ce) !important;
        transform: scale(1.03);
    }

    /* Tabs */
    div[data-baseweb="tab-list"] {
        justify-content: center;
        background: rgba(0, 0, 0, 0.5);
        border-radius: 12px;
        backdrop-filter: blur(8px);
        padding: 0.5rem;
    }

    /* Data Tables */
    [data-testid="stDataFrame"] {
        background: rgba(255,255,255,0.95) !important;
        border-radius: 12px !important;
    }

    /* Summary box */
    .summary-box {
        background: white;
        border-left: 6px solid #2563eb;
        border-radius: 12px;
        padding: 1.5rem;
        margin-top: 1rem;
        font-size: 1rem;
        line-height: 1.6;
        color: #1e293b;
        box-shadow: 0 3px 12px rgba(0,0,0,0.1);
    }

    /* Misc */
    textarea {
        border-radius: 10px !important;
    }

    
    </style>
""", unsafe_allow_html=True)

# --- Header ---
st.markdown("""
    <div class="main-header">
        <h1>📊 Workfolio AI Productivity Summary</h1>
        <p>Upload your task and Workfolio activity CSVs to generate a detailed AI-powered daily summary.</p>
    </div>
""", unsafe_allow_html=True)

# --- Upload Section ---
st.markdown("<h3 style='color: white;'>📂 Upload Your Data Files</h3>", unsafe_allow_html=True)


col1, col2 = st.columns(2)
with col1:
    uploaded_task_file = st.file_uploader("🗂️ Task Allocation CSV", type=["csv"], key="task")
with col2:
    uploaded_workfolio_file = st.file_uploader("💻 Workfolio Activity CSV", type=["csv"], key="workfolio")
st.markdown('</div>', unsafe_allow_html=True)

# --- Wait for Files ---
if uploaded_task_file is None or uploaded_workfolio_file is None:
    st.info("📁 Please upload both **Task Allocation** and **Workfolio Activity** CSV files to continue.")
    st.stop()

# --- Load Data ---
try:
    task_df = pd.read_csv(uploaded_task_file)
    workfolio_df = pd.read_csv(uploaded_workfolio_file)
except Exception as e:
    st.error(f"❌ Failed to read uploaded CSVs: {e}")
    st.stop()

# --- Control Section ---

col1, col2, col3 = st.columns([1, 1, 1])
with col1:
    reload_data = st.button("🔄 Reload Data")
with col2:
    run_summary = st.button("⚡ Generate AI Summary")
with col3:
    enable_export = st.checkbox("💾 Enable Export (.txt)", value=False)
st.markdown('</div>', unsafe_allow_html=True)

if reload_data:
    st.experimental_rerun()

# --- Tabs ---
tab1, tab2, tab3 = st.tabs(["📋 Task Allocation", "💻 Workfolio Activity", "🧠 AI Summary"])

with tab1:
    st.markdown("<h3 style='color:white;'>📋 Task Allocation Data</h3>", unsafe_allow_html=True)

    st.dataframe(task_df, use_container_width=True)

with tab2:
    st.markdown("<h3 style='color:white;'>💻 Workfolio Activity Data</h3>", unsafe_allow_html=True)
    st.dataframe(workfolio_df, use_container_width=True)

with tab3:
    st.markdown("<h3 style='color:white;'>🧠 AI Summary Generator</h3>", unsafe_allow_html=True)

    task_text = format_task_data(task_df)
    workfolio_text = workfolio_df.to_string(index=False)

    if run_summary:
        with st.spinner("⚙️ Generating AI summary via DeepSeek..."):
            try:
                summary = generate_summary(task_text, workfolio_text)
                st.success("✅ AI Summary generated successfully!")
                st.markdown("### ✨ Summary Output")
                st.markdown(f"<div class='summary-box'>{summary}</div>", unsafe_allow_html=True)

                if enable_export:
                    st.download_button(
                        label="💾 Download Summary (.txt)",
                        data=summary,
                        file_name="daily_summary.txt",
                        mime="text/plain",
                    )
            except Exception as e:
                st.error(f"❌ Failed to generate summary: {e}")
    else:
        st.info("Press **Generate AI Summary** to run the model.")
