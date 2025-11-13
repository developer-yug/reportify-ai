from task_data import load_task_allocation, format_task_data
from workfolio_api import load_workfolio_data
from llm_prompt import generate_summary
from email_utils import send_email

def main():
    task_df = load_task_allocation()
    workfolio_df = load_workfolio_data()

    task_text = format_task_data(task_df)
    workfolio_text = workfolio_df.to_string(index=False)

    # summary = generate_summary(task_text, workfolio_text)
    # print("\n=== AI Summary ===\n", summary)
    
summary = """
📊 **Daily Productivity Summary (Test Mode)**

Here is a sample AI-generated summary for testing email delivery:

**Employee Breakdown**
- Emp 1 spent ~3 hours implementing payment integration.
- Emp 2 spent ~2 hours setting up crash analytics and ensuring stability logs.
- Emp 3 spent ~4 hours on UI bug fixing and testing.

**Overall Insights**
- Total productive hours: 9 hrs
- All assigned tasks for the day were executed on schedule.
- No blockers identified.
- System performance remained stable.

(This is a mock summary used only for validating email sending.)
    """

print("\n=== FAKE AI SUMMARY (EMAIL TEST) ===\n", summary)

cc_list = [
    "bg828587@gmail.com",
    "bhushan.n.gayakwad@zohomail.in"
]

send_email("Daily Report", summary, cc_emails=cc_list)

if __name__ == "__main__":
    main()
