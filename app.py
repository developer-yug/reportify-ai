# app.py
import streamlit as st
import pandas as pd
from io import StringIO
import os

# Import your existing functions (adjust import paths if needed)
# from task_data import load_task_allocation, format_task_data
# from workfolio_api import load_workfolio_data
# from llm_prompt import generate_summary

# For demo/test fallback if your modules aren't available, these small stubs let the app run.
def load_task_allocation():
    # replace with: return load_task_allocation()
    return pd.DataFrame([
        {"user_email": "alice@example.com", "task_id": "T1", "task_title": "Payment integration", "allocated_minutes": 180},
        {"user_email": "bob@example.com", "task_id": "T2", "task_title": "Crash analytics", "allocated_minutes": 120},
    ])

def load_workfolio_data():
    # replace with: return load_workfolio_data()
    return pd.DataFrame([
        {"user_email": "alice@example.com", "active_minutes": 150, "productive_minutes": 150},
        {"user_email": "bob@example.com", "active_minutes": 105, "productive_minutes": 105},
    ])

def format_task_data(df: pd.DataFrame) -> str:
    # replace with your real formatter
    return df.to_string(index=False)

def generate_summary(task_text: str, workfolio_text: str) -> str:
    # replace with your real API call function (or import it)
    # This stub simulates a response.
    return f"Simulated summary for:\n\nTASKS:\n{task_text}\n\nWORKFOLIO:\n{workfolio_text}"

# Streamlit layout
st.set_page_config(page_title="Workfolio AI Summary", layout="wide")
st.title("Workfolio — Daily Productivity Summary (Streamlit UI)")

with st.sidebar:
    st.header("Controls")
    refresh_btn = st.button("Reload data")
    run_btn = st.button("Generate AI Summary")
    st.markdown("---")
    st.write("Environment / Keys")
    st.write("DEEPSEEK_API_KEY set in environment or Streamlit secrets.")
    show_raw_api = st.checkbox("Show raw API call (for debugging)", value=False)
    st.markdown("---")
    st.write("Export")
    export_txt = st.checkbox("Enable export (.txt)")

# Load Data (cached to avoid repeated IO)
@st.cache_data(ttl=300)
def load_all():
    task_df = load_task_allocation()
    workfolio_df = load_workfolio_data()
    return task_df, workfolio_df

if refresh_btn:
    # clear cache then reload
    st.cache_data.clear()
    st.experimental_rerun()

task_df, workfolio_df = load_all()

tab1, tab2 = st.tabs(["Data Preview", "AI Summary"])

with tab1:
    st.subheader("Task Allocation")
    st.dataframe(task_df, use_container_width=True)

    st.subheader("Workfolio Activity")
    st.dataframe(workfolio_df, use_container_width=True)

    st.subheader("Manual upload (optional)")
    uploaded_tasks = st.file_uploader("Upload task allocation CSV", type=["csv"])
    uploaded_workfolio = st.file_uploader("Upload workfolio CSV", type=["csv"])

    if uploaded_tasks is not None:
        try:
            task_df = pd.read_csv(uploaded_tasks)
            st.success("Loaded task allocation from upload.")
            st.dataframe(task_df, use_container_width=True)
        except Exception as e:
            st.error(f"Failed to parse tasks CSV: {e}")

    if uploaded_workfolio is not None:
        try:
            workfolio_df = pd.read_csv(uploaded_workfolio)
            st.success("Loaded workfolio data from upload.")
            st.dataframe(workfolio_df, use_container_width=True)
        except Exception as e:
            st.error(f"Failed to parse workfolio CSV: {e}")

with tab2:
    st.subheader("Summary Controls")
    options_col, result_col = st.columns([1, 3])

    with options_col:
        model = st.selectbox("LLM / API (local stub or remote)", ["local-stub", "deepseek-chat"])
        show_inputs = st.checkbox("Show prompt inputs", value=False)
        if model == "deepseek-chat":
            # prefer use of Streamlit secrets; fallback to env
            api_key = st.secrets.get("DEEPSEEK_API_KEY") or os.getenv("DEEPSEEK_API_KEY")
            if not api_key:
                st.warning("DEEPSEEK_API_KEY not found in Streamlit secrets or environment variables.")
            else:
                st.success("DEEPSEEK_API_KEY loaded")

    with result_col:
        st.write("Summary output will appear here.")

    # Prepare texts to send to LLM
    task_text = format_task_data(task_df)
    workfolio_text = workfolio_df.to_string(index=False)

    if show_inputs:
        st.markdown("**Prepared inputs**")
        st.text_area("Task input", task_text, height=150)
        st.text_area("Workfolio input", workfolio_text, height=150)

    # Run the model and show output
    if run_btn:
        with st.spinner("Generating AI summary..."):
            try:
                # If you have a real generate_summary that calls an API, use it here.
                # Example: summary = generate_summary(task_text, workfolio_text)
                summary = generate_summary(task_text, workfolio_text)

                st.markdown("### AI Summary")
                st.code(summary, language=None)

                # small copy button (Streamlit 1.19+)
                st.button("Copy summary to clipboard", on_click=None)  # browsers handle copying via JS; you can add custom JS if needed

                if export_txt:
                    # create a txt download
                    st.download_button("Download summary (.txt)", data=summary, file_name="daily_summary.txt", mime="text/plain")
                # optionally show the raw API payload/response
                if show_raw_api:
                    st.markdown("#### Raw inputs passed to LLM")
                    st.json({
                        "task_text_length": len(task_text),
                        "workfolio_text_length": len(workfolio_text),
                        "model": model
                    })
            except Exception as e:
                st.error(f"Failed to generate summary: {e}")
    else:
        st.info("Press 'Generate AI Summary' in the sidebar to run the model.")
