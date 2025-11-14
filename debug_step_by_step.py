#!/usr/bin/env python3
import pandas as pd
from productivity_analyzer import load_and_merge_data, parse_time_to_hours, _map_employees

# Debug: Manual step through extract_employee_metrics
task_df, workfolio_df = load_and_merge_data('data/task_allocation.csv', 'data/workfolio_activity.csv')

print("Initial workfolio_df columns:", workfolio_df.columns.tolist())

# Step 1: Find employee column
emp_id_col = next((c for c in task_df.columns if "emp" in c.lower() and "id" in c.lower()), "Employee Id")
emp_name_col = next((c for c in task_df.columns if "emp" in c.lower() and "name" in c.lower()), "Employee Name")
print(f"emp_id_col: {emp_id_col}, emp_name_col: {emp_name_col}")

# Step 2: Do mapping
emp_mapping = _map_employees(task_df, workfolio_df, emp_name_col)
print(f"emp_mapping: {emp_mapping}")

# Step 3: Add mapped_employee_id column
workfolio_emp_col = next((c for c in workfolio_df.columns if "emp" in c.lower()), "Employee")
print(f"workfolio_emp_col: {workfolio_emp_col}")

workfolio_df["mapped_employee_id"] = workfolio_df[workfolio_emp_col].map(emp_mapping).fillna(-999)
print("After adding mapped_employee_id, columns:", workfolio_df.columns.tolist())

# Step 4: Find duration column
print("\nAll columns in workfolio_df:")
for c in workfolio_df.columns:
    print(f"  '{c}'")

candidates = [c for c in workfolio_df.columns if "duration" in c.lower()]
print(f"\nDuration candidates: {candidates}")

activity_duration_col = next((c for c in workfolio_df.columns if "duration" in c.lower()), "Activity Duration")
print(f"activity_duration_col selected: '{activity_duration_col}'")
print(f"Exists in workfolio_df.columns: {activity_duration_col in workfolio_df.columns}")
