#!/usr/bin/env python3
"""
Test that the analyzer handles invalid/missing workfolio data gracefully.
"""
from productivity_analyzer import load_and_merge_data, extract_employee_metrics
import pandas as pd

print("Testing graceful handling of invalid workfolio data...")

# Load task data normally
task_df = pd.read_csv('data/task_allocation.csv')

# Create invalid workfolio data (task data instead of activity data)
invalid_workfolio_df = pd.read_csv('data/task_allocation.csv')  # This has wrong columns

print(f"\nInvalid workfolio columns: {invalid_workfolio_df.columns.tolist()}")

try:
    metrics = extract_employee_metrics(task_df, invalid_workfolio_df)
    print("✓ Successfully handled invalid workfolio data")
    print(f"✓ Extracted metrics for {len(metrics)} employees")
    print(f"✓ Productivity ratio (should be 0): {metrics['productivity_ratio'].unique()}")
except Exception as e:
    print(f"✗ Failed: {e}")
    import traceback
    traceback.print_exc()
