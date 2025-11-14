import os
import json
import streamlit as st
import pandas as pd
from task_data import format_task_data
from llm_prompt import generate_summary
from email_utils import save_summary_json, parse_summary_json, send_emails
from productivity_analyzer import load_and_merge_data, extract_employee_metrics, get_productivity_summary
from dashboard_charts import (
    chart_employee_completion_rate,
    chart_tasks_completed,
    chart_total_hours_worked,
    chart_productivity_ratio,
    chart_productive_vs_nonproductive,
    chart_avg_time_per_task,
    chart_productivity_scatter,
    chart_completion_rate_distribution,
    create_summary_cards,
)

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

# --- Check if we have existing files ---
os.makedirs("data", exist_ok=True)
task_csv_path = os.path.join("data", "task_allocation.csv")
work_csv_path = os.path.join("data", "workfolio_active_hours.csv")

task_df = None
workfolio_df = None
use_existing_files = os.path.exists(task_csv_path) and os.path.exists(work_csv_path)

# --- Upload Section ---
st.markdown("<h3>📂 Upload Your Data Files</h3>", unsafe_allow_html=True)

if use_existing_files:
    st.info("📂 Using existing data files from disk. Upload new files to replace them.")

col1, col2 = st.columns(2)
with col1:
    uploaded_task_file = st.file_uploader("🗂️ Task Allocation File", type=["csv", "xlsx"], key="task")
with col2:
    uploaded_workfolio_file = st.file_uploader("💻 Workfolio Activity File", type=["csv", "xlsx"], key="workfolio")

# --- Load Data (CSV or Excel) ---
def load_uploaded_file(file):
    if file.name.endswith(".csv"):
        return pd.read_csv(file)
    elif file.name.endswith(".xlsx"):
        return pd.read_excel(file)
    else:
        raise ValueError("Unsupported file format. Please upload a CSV or Excel file.")

# If files were uploaded, load and save them
if uploaded_task_file is not None and uploaded_workfolio_file is not None:
    try:
        task_df = load_uploaded_file(uploaded_task_file)
        workfolio_df = load_uploaded_file(uploaded_workfolio_file)
        
        # Save uploaded files as CSV
        task_df.to_csv(task_csv_path, index=False)
        
        # Only save workfolio file if it has the correct columns (Activity Duration or Status)
        has_activity_duration = any("duration" in c.lower() for c in workfolio_df.columns)
        has_status = any("status" in c.lower() for c in workfolio_df.columns)
        
        if has_activity_duration and has_status:
            # This looks like the correct workfolio file
            workfolio_df.to_csv(work_csv_path, index=False)
            st.info(f"🔁 Uploaded files saved as CSV:\n`{task_csv_path}`\n`{work_csv_path}`")
        else:
            # Workfolio file doesn't have expected columns - keep existing file if it exists
            if os.path.exists(work_csv_path):
                st.warning(f"⚠️ Workfolio file doesn't have expected columns. Using previously saved workfolio data.")
            else:
                # Create a minimal workfolio file with dummy data
                st.warning(f"⚠️ Workfolio file missing expected columns. Using sample data for dashboard.")
                sample_workfolio = pd.DataFrame({
                    "Employee": [f"Emp {i}" for i in range(1, 7)],
                    "App/Site Name": ["Sample App"] * 6,
                    "Status": ["Productive"] * 6,
                    "Activity Duration": ["1h 00m"] * 6
                })
                sample_workfolio.to_csv(work_csv_path, index=False)
    except Exception as e:
        st.error(f"❌ Failed to read uploaded files: {e}")
        st.stop()

# If no files uploaded, try to load existing files
if task_df is None or workfolio_df is None:
    if use_existing_files:
        try:
            task_df = pd.read_csv(task_csv_path)
            workfolio_df = pd.read_csv(work_csv_path)
            st.success(f"✓ Loaded existing data files from disk")
        except Exception as e:
            st.error(f"❌ Failed to load existing files: {e}")
            st.stop()
    else:
        st.info("📁 Please upload both **Task Allocation** and **Workfolio Activity** files (CSV or Excel).")
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
tab1, tab2, tab3, tab4 = st.tabs(["📋 Task Allocation", "💻 Workfolio Activity", "🧠 AI Summary", "📊 Admin Dashboard"])

with tab1:
    st.markdown("<h3>📋 Task Allocation Data</h3>", unsafe_allow_html=True)
    st.dataframe(task_df, use_container_width=True)

with tab2:
    st.markdown("<h3>💻 Workfolio Activity Data</h3>", unsafe_allow_html=True)
    st.dataframe(workfolio_df, use_container_width=True)

with tab3:
    st.markdown("<h3>🧠 AI Summary Generator</h3>", unsafe_allow_html=True)
    # Prepare both human-readable and raw CSV content for the prompt
    task_text = format_task_data(task_df)
    workfolio_text = workfolio_df.to_string(index=False)
    task_csv_text = task_df.to_csv(index=False)
    workfolio_csv_text = workfolio_df.to_csv(index=False)

    if run_summary:
        with st.spinner("⚙️ Generating AI summary via DeepSeek..."):
            try:
                # Pass CSV content to the summary generator so the model can compute per-employee metrics
                summary = generate_summary(task_csv_text, workfolio_csv_text)
                st.success("✅ AI Summary generated successfully!")

                # Try to parse the returned summary as JSON and save it
                try:
                    summary_dict = parse_summary_json(summary)
                    save_path = save_summary_json(summary)
                    st.markdown("### ✨ Summary Output (parsed JSON)")
                    st.write(summary_dict.get("digest", {}))

                    st.markdown("### ✉️ Generated Emails Preview")
                    for i, em in enumerate(summary_dict.get("emails", [])):
                        name = em.get("employee_name") or em.get("employee_id")
                        st.markdown(f"**{i+1}. {name}**")
                        st.text_input("Subject", value=em.get("email_subject", ""), key=f'subj_{i}')
                        st.text_area("Body", value=em.get("email_body", ""), height=150, key=f'body_{i}')

                    if enable_export:
                        st.download_button(
                            label="💾 Download Summary (.json)",
                            data=json.dumps(summary_dict, indent=2),
                            file_name="daily_summary.json",
                            mime="application/json",
                        )

                    # Send emails if user requests and credentials are set
                    if st.button("📨 Send Emails"):
                        try:
                            # Optionally provide a recipient_map if you have employee->email mapping
                            results = send_emails(summary_dict)
                            st.success("Email send completed")
                            st.json(results)
                        except Exception as e:
                            st.error(f"Failed to send emails: {e}")

                except json.JSONDecodeError:
                    st.markdown("### ✨ Summary Output (raw)")
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

with tab4:
    st.markdown("<h3>📊 Admin Productivity Dashboard</h3>", unsafe_allow_html=True)
    st.markdown("**Real-time analytics and employee productivity insights**")

    # Load and process productivity data
    try:
        task_csv_path = os.path.join("data", "task_allocation.csv")
        work_csv_path = os.path.join("data", "workfolio_active_hours.csv")
        
        # Load and merge data
        task_df_data, workfolio_df_data = load_and_merge_data(task_csv_path, work_csv_path)
        
        # Extract metrics
        metrics_df = extract_employee_metrics(task_df_data, workfolio_df_data)
        summary = get_productivity_summary(metrics_df)
        
        # Display summary cards
        st.markdown("### 📈 Summary Metrics")
        summary_cards = create_summary_cards(summary)
        
        col_summary = st.columns(len(summary_cards))
        for idx, (key, value) in enumerate(summary_cards.items()):
            with col_summary[idx]:
                st.metric(label=key, value=value)
        
        # Dashboard controls
        st.markdown("---")
        st.markdown("### 🎯 Analytics & Visualizations")
        
        show_completion = st.checkbox("Show Completion Metrics", value=True)
        show_hours = st.checkbox("Show Hours Metrics", value=True)
        show_activity = st.checkbox("Show Activity Metrics", value=True)
        show_individual = st.checkbox("Show Individual Employee Analysis", value=True)
        
        # Row 1: Completion metrics
        if show_completion:
            st.markdown("#### Task Completion Analysis")
            col1, col2 = st.columns(2)
            
            with col1:
                fig1 = chart_employee_completion_rate(metrics_df)
                st.plotly_chart(fig1, use_container_width=True)
            
            with col2:
                fig2 = chart_tasks_completed(metrics_df)
                st.plotly_chart(fig2, use_container_width=True)
            
            col3, col4 = st.columns(2)
            with col3:
                fig3 = chart_completion_rate_distribution(metrics_df)
                st.plotly_chart(fig3, use_container_width=True)
            
            with col4:
                fig4 = chart_avg_time_per_task(metrics_df)
                st.plotly_chart(fig4, use_container_width=True)
        
        # Row 2: Hours and efficiency
        if show_hours:
            st.markdown("#### Time & Efficiency Analysis")
            col5, col6 = st.columns(2)
            
            with col5:
                fig5 = chart_total_hours_worked(metrics_df)
                st.plotly_chart(fig5, use_container_width=True)
            
            with col6:
                fig6 = chart_productivity_scatter(metrics_df)
                st.plotly_chart(fig6, use_container_width=True)
        
        # Row 3: Activity metrics
        if show_activity:
            st.markdown("#### Activity & Productivity Analysis")
            col7, col8 = st.columns(2)
            
            with col7:
                fig7 = chart_productivity_ratio(metrics_df)
                if fig7:
                    st.plotly_chart(fig7, use_container_width=True)
                else:
                    st.info("No workfolio activity data available for some employees.")
            
            with col8:
                fig8 = chart_productive_vs_nonproductive(metrics_df)
                if fig8:
                    st.plotly_chart(fig8, use_container_width=True)
                else:
                    st.info("No workfolio activity data available.")
        
        # Individual employee analysis
        if show_individual:
            st.markdown("#### 👥 Individual Employee Insights")
            
            employees = sorted(metrics_df["employee_name"].unique())
            selected_emp = st.selectbox("Select Employee", employees, key="emp_select")
            
            if selected_emp:
                emp_data = metrics_df[metrics_df["employee_name"] == selected_emp].iloc[0]
                
                st.markdown(f"**Employee: {selected_emp}**")
                
                col_emp1, col_emp2, col_emp3, col_emp4 = st.columns(4)
                with col_emp1:
                    st.metric(label="Tasks Completed", value=int(emp_data["completed_tasks"]), 
                             delta=f"of {int(emp_data['total_tasks'])}")
                
                with col_emp2:
                    st.metric(label="Completion Rate", value=f"{emp_data['completion_rate']:.1f}%")
                
                with col_emp3:
                    st.metric(label="Total Hours", value=f"{emp_data['total_time_taken_hours']:.2f}h")
                
                with col_emp4:
                    prod_ratio = emp_data["productivity_ratio"] if emp_data["total_activity_hours"] > 0 else 0
                    st.metric(label="Productivity Ratio", value=f"{prod_ratio:.1f}%")
                
                # Detailed breakdown
                st.markdown("**Task Details:**")
                emp_tasks = task_df_data[task_df_data["Employee Id"] == emp_data["employee_id"]].copy()
                if len(emp_tasks) > 0:
                    st.dataframe(emp_tasks[[c for c in emp_tasks.columns if c not in ["Employee Id"]]], 
                                use_container_width=True, hide_index=True)
    
    except Exception as e:
        st.error(f"❌ Failed to load dashboard: {e}")
        import traceback
        st.info(traceback.format_exc())
