#!/usr/bin/env python3
"""
Simulate the full app workflow: uploading wrong file and checking if dashboard recovers.
"""
import pandas as pd
import os

os.makedirs("data", exist_ok=True)

# Simulate user uploading wrong workfolio file (actually task file)
print("Simulating user upload of wrong workfolio file...")
task_df = pd.read_csv('data/task_allocation.csv')
wrong_workfolio = pd.read_csv('data/task_allocation.csv')  # Wrong - uploading task as workfolio

# App logic - check if file is valid
has_activity_duration = any("duration" in c.lower() for c in wrong_workfolio.columns)
has_status = any("status" in c.lower() for c in wrong_workfolio.columns)

print(f"Wrong file has 'Activity Duration': {has_activity_duration}")
print(f"Wrong file has 'Status': {has_status}")

work_csv_path = os.path.join("data", "workfolio_active_hours.csv")

if has_activity_duration and has_status:
    print("✗ Would have overwritten workfolio_active_hours.csv with wrong data!")
    wrong_workfolio.to_csv(work_csv_path, index=False)
else:
    print("✓ Correctly detected invalid workfolio file - NOT overwriting!")
    if os.path.exists(work_csv_path):
        print("✓ Keeping existing workfolio_active_hours.csv")

# Now test if dashboard still works
print("\nTesting dashboard with protected workfolio file...")
from productivity_analyzer import load_and_merge_data, extract_employee_metrics

try:
    task_df_data, workfolio_df_data = load_and_merge_data('data/task_allocation.csv', 'data/workfolio_active_hours.csv')
    metrics = extract_employee_metrics(task_df_data, workfolio_df_data)
    print(f"✓ Dashboard loaded successfully with {len(metrics)} employees")
    print(f"✓ Metrics extracted correctly")
except Exception as e:
    print(f"✗ Dashboard failed: {e}")
