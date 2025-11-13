import streamlit as st
import pandas as pd
from task_data import format_task_data
from llm_prompt import generate_summary

# --- Page Setup ---
st.set_page_config(page_title="Workfolio AI Summary", layout="wide")

# --- 🌈 Custom CSS ---
st.markdown("""
    <style>
    .stApp {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        font-family: 'Poppins', sans-serif;
        color: white;
    }
    .main-header {
        text-align: center;
        padding: 2rem 0;
        margin-bottom: 2rem;
    }
    .main-header h1 {
        font-size: 2.4rem;
        font-weight: 700;
        margin-bottom: 0.3rem;
        background: linear-gradient(90deg, #f9fafb, #c7d2fe);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }
    .main-header p {
        font-size: 1.1rem;
        color: #e2e8f0;
    }
    .stButton>button {
        border-radius: 10px !important;
        height: 3rem;
        background: linear-gradient(90deg, #38bdf8, #3b82f6) !important;
        color: white !important;
        font-weight: 600 !important;
        font-size: 1rem !important;
        border: none !important;
        box-shadow: 0 4px 10px rgba(0,0,0,0.15);
        transition: all 0.3s ease-in-out;
    }
    .stButton>button:hover {
        background: linear-gradient(90deg, #0284c7, #1d4ed8) !important;
        transform: scale(1.03);
    }
    h3 {
        color: white !important;
    }
    [data-testid="stDataFrame"] {
        background: rgba(255,255,255,0.9) !important;
        border-radius: 12px !important;
    }
    .summary-box {
        background: white;
        border-left: 6px solid #3b82f6;
        border-radius: 12px;
        padding: 1.5rem;
        margin-top: 1rem;
        font-size: 1rem;
        line-height: 1.6;
        color: #1e293b;
        box-shadow: 0 3px 12px rgba(0,0,0,0.1);
    }
    </style>
""", unsafe_allow_html=True)

# --- Header ---
st.markdown("""
    <div class="main-header">
        <h1>📊 Workfolio AI Productivity Summary</h1>
        <p>Upload your task and Workfolio activity data (CSV or Excel) to generate an AI-powered daily summary.</p>
    </div>
""", unsafe_allow_html=True)

# --- Upload Section ---
st.markdown("<h3>📂 Upload Your Data Files</h3>", unsafe_allow_html=True)
col1, col2 = st.columns(2)
with col1:
    uploaded_task_file = st.file_uploader("🗂️ Task Allocation File", type=["csv", "xlsx"], key="task")
with col2:
    uploaded_workfolio_file = st.file_uploader("💻 Workfolio Activity File", type=["csv", "xlsx"], key="workfolio")

# --- Wait for Files ---
if uploaded_task_file is None or uploaded_workfolio_file is None:
    st.info("📁 Please upload both **Task Allocation** and **Workfolio Activity** files (CSV or Excel).")
    st.stop()

# --- Load Data (CSV or Excel) ---
def load_uploaded_file(file):
    if file.name.endswith(".csv"):
        return pd.read_csv(file)
    elif file.name.endswith(".xlsx"):
        return pd.read_excel(file)
    else:
        raise ValueError("Unsupported file format. Please upload a CSV or Excel file.")

try:
    task_df = load_uploaded_file(uploaded_task_file)
    workfolio_df = load_uploaded_file(uploaded_workfolio_file)
except Exception as e:
    st.error(f"❌ Failed to read uploaded files: {e}")
    st.stop()

# --- Control Buttons ---
col1, col2, col3 = st.columns([1, 1, 1])
with col1:
    reload_data = st.button("🔄 Reload Data")
with col2:
    run_summary = st.button("⚡ Generate AI Summary")
with col3:
    enable_export = st.checkbox("💾 Enable Export (.txt)", value=False)

if reload_data:
    st.experimental_rerun()

# --- Tabs ---
tab1, tab2, tab3 = st.tabs(["📋 Task Allocation", "💻 Workfolio Activity", "🧠 AI Summary"])

with tab1:
    st.markdown("<h3>📋 Task Allocation Data</h3>", unsafe_allow_html=True)
    st.dataframe(task_df, use_container_width=True)

with tab2:
    st.markdown("<h3>💻 Workfolio Activity Data</h3>", unsafe_allow_html=True)
    st.dataframe(workfolio_df, use_container_width=True)

with tab3:
    st.markdown("<h3>🧠 AI Summary Generator</h3>", unsafe_allow_html=True)
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
