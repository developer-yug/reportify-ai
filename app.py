import streamlit as st
import pandas as pd

from task_data import format_task_data
from llm_prompt import generate_summary
from email_utils import send_email
from utils.excel_generator import create_excel_report


st.title("📊 AI Task Productivity Analyzer")
st.write("Upload task allocation & workfolio CSV files to generate daily productivity report.")

task_file = st.file_uploader("📥 Upload Task Allocation CSV", type=["csv"])
work_file = st.file_uploader("📥 Upload Workfolio CSV", type=["csv"])

email_to = st.text_input("📧 Send To (optional)")
email_cc = st.text_input("📨 CC Emails (comma-separated, optional)")

if st.button("Generate Summary"):
    if not task_file or not work_file:
        st.error("⚠️ Please upload both CSV files first.")
        st.stop()

    # Read CSVs
    task_df = pd.read_csv(task_file)
    work_df = pd.read_csv(work_file)

    # Convert to text
    task_text = format_task_data(task_df)
    work_text = work_df.to_string(index=False)

    st.info("🧠 Generating AI summary... please wait.")
    try:
        summary = generate_summary(task_text, work_text)
    except Exception as e:
        st.error(f"AI Error: {e}")
        st.stop()

    st.success("✅ Summary generated successfully!")
    st.text_area("📄 AI Summary Output", summary, height=300)

    # Generate Excel attachment
    excel_path = create_excel_report(task_df, work_df)

    # Email sending
    if email_to:
        cc_list = [email.strip() for email in email_cc.split(",")] if email_cc else []

        try:
            send_email(
                subject="Daily Productivity Summary",
                body=summary,
                receiver_email=email_to,
                cc_emails=cc_list,
                attachment_path=excel_path
            )
            st.success(f"📧 Email sent to {email_to} with CC: {', '.join(cc_list)}")

        except Exception as e:
            st.error(f"Email sending failed: {e}")
