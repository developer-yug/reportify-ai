import pandas as pd

def create_excel_report(task_df, work_df):
    output_path = "daily_report.xlsx"

    with pd.ExcelWriter(output_path, engine="openpyxl") as writer:
        task_df.to_excel(writer, sheet_name="Task Allocation", index=False)
        work_df.to_excel(writer, sheet_name="Workfolio Hours", index=False)

    return output_path
