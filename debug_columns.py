#!/usr/bin/env python3
import pandas as pd
from productivity_analyzer import load_and_merge_data

# Debug: Check what columns exist after load_and_merge_data
task_df, workfolio_df = load_and_merge_data('data/task_allocation.csv', 'data/workfolio_active_hours.csv')

print("Workfolio columns:")
print(workfolio_df.columns.tolist())
print("\nSearching for 'duration':")
candidates = [c for c in workfolio_df.columns if "duration" in c.lower()]
print(f"Found: {candidates}")

# Check the actual column name
activity_duration_col = next((c for c in workfolio_df.columns if "duration" in c.lower()), "Activity Duration")
print(f"\nSelected column: '{activity_duration_col}'")
print(f"Column exists: {activity_duration_col in workfolio_df.columns}")

if activity_duration_col in workfolio_df.columns:
    print(f"Sample values: {workfolio_df[activity_duration_col].head().tolist()}")
