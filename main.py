from task_data import load_task_allocation, format_task_data
from workfolio_api import load_workfolio_data
from llm_prompt import generate_summary
# from email_utils import send_email

def main():
    task_df = load_task_allocation()
    workfolio_df = load_workfolio_data()

    task_text = format_task_data(task_df)
    workfolio_text = workfolio_df.to_string(index=False)

    summary = generate_summary(task_text, workfolio_text)
    print("\n=== AI Summary ===\n", summary)

    # send_email("Daily Productivity Summary", summary)

if __name__ == "__main__":
    main()
