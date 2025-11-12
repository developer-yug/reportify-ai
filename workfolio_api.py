import pandas as pd
import os

def load_workfolio_data(csv_path="data/workfolio_active_hours.csv"):
    if os.path.exists(csv_path):
        return pd.read_csv(csv_path)
    else:
        print("No CSV found, please verify Workfolio API access.")
        return pd.DataFrame()
