import pandas as pd

def load_task_allocation(csv_path="data/task_allocation.csv"):
    return pd.read_csv(csv_path)

def format_task_data(df):
    return df.to_string(index=False)
