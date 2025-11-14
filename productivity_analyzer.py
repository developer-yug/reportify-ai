"""
Core productivity analysis module.
Processes task allocation and workfolio activity data to extract employee productivity metrics.
"""

import pandas as pd
from typing import Dict, List, Tuple
import re


def parse_time_to_hours(time_str: str) -> float:
    """Convert time strings (hh:mm:ss or Xh Ym format) to hours as float."""
    if pd.isna(time_str) or not isinstance(time_str, str):
        return 0.0

    time_str = str(time_str).strip()

    # Pattern: "hh:mm:ss"
    if re.match(r"^\d{1,2}:\d{2}:\d{2}$", time_str):
        parts = time_str.split(":")
        h, m, s = int(parts[0]), int(parts[1]), int(parts[2])
        return h + m / 60 + s / 3600

    # Pattern: "Xh Ym" (e.g., "2h 30m")
    match = re.match(r"(\d+)\s*h\s+(\d+)\s*m", time_str)
    if match:
        h, m = int(match.group(1)), int(match.group(2))
        return h + m / 60

    # Single hour pattern: "Xh"
    match = re.match(r"(\d+)\s*h", time_str)
    if match:
        return float(match.group(1))

    # Single minute pattern: "Xm"
    match = re.match(r"(\d+)\s*m", time_str)
    if match:
        return int(match.group(1)) / 60

    return 0.0


def load_and_merge_data(task_csv_path: str, workfolio_csv_path: str) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """Load and prepare both CSVs. Return (task_df, workfolio_df) with normalized columns."""
    # Load task allocation
    task_df = pd.read_csv(task_csv_path)
    
    # Load workfolio activity
    workfolio_df = pd.read_csv(workfolio_csv_path)
    
    # Normalize task data
    task_df.columns = task_df.columns.str.strip()
    
    # Normalize workfolio data
    workfolio_df.columns = workfolio_df.columns.str.strip()
    
    return task_df, workfolio_df


def extract_employee_metrics(task_df: pd.DataFrame, workfolio_df: pd.DataFrame) -> pd.DataFrame:
    """
    Extract and aggregate productivity metrics per employee.
    
    Returns a DataFrame with columns:
    - employee_id
    - employee_name
    - total_tasks
    - completed_tasks
    - overdue_tasks
    - completion_rate (%)
    - total_time_taken_hours
    - avg_time_per_task_hours
    - productive_hours (from workfolio)
    - nonproductive_hours (from workfolio)
    - total_activity_hours
    - productivity_ratio (%)
    """
    
    # === Task Analysis ===
    # Find the employee ID column (handles variations in naming)
    emp_id_col = next((c for c in task_df.columns if "emp" in c.lower() and "id" in c.lower()), "Employee Id")
    emp_name_col = next((c for c in task_df.columns if "emp" in c.lower() and "name" in c.lower()), "Employee Name")
    task_status_col = next((c for c in task_df.columns if "status" in c.lower()), "Task Status (Overdue/Done)")
    time_taken_col = next((c for c in task_df.columns if "time" in c.lower() and "taken" in c.lower()), "Time Taken (hh:mm:ss)")
    
    # Convert time strings to hours
    task_df["time_hours"] = task_df[time_taken_col].apply(parse_time_to_hours)
    
    # Group by employee
    task_agg = task_df.groupby([emp_id_col, emp_name_col]).agg({
        "time_hours": ["sum", "mean", "count"],
        task_status_col: lambda x: (x.str.lower().str.contains("done", na=False)).sum()
    }).reset_index()
    
    task_agg.columns = ["employee_id", "employee_name", "total_time_taken_hours", "avg_time_per_task", 
                        "total_tasks", "completed_tasks"]
    
    # Calculate metrics
    task_agg["overdue_tasks"] = task_agg["total_tasks"] - task_agg["completed_tasks"]
    task_agg["completion_rate"] = (task_agg["completed_tasks"] / task_agg["total_tasks"] * 100).round(2)
    
    # === Workfolio Analysis ===
    # Check if workfolio has the required Activity Duration column
    has_activity_duration = any("duration" in c.lower() for c in workfolio_df.columns)
    
    if not has_activity_duration:
        # Workfolio data is missing or invalid - create empty workfolio aggregation
        # This handles cases where wrong file was uploaded
        workfolio_agg = pd.DataFrame({
            "employee_id": task_agg["employee_id"].unique(),
            "total_activity_hours": 0,
            "productive_hours": 0,
            "nonproductive_hours": 0,
            "productivity_ratio": 0
        })
    else:
        # Map employee names from workfolio to task data
        # The workfolio has "Emp 1", "Emp 2", etc. — try to map by sequence or by name similarity
        emp_mapping = _map_employees(task_df, workfolio_df, emp_name_col)
        
        # Find the employee column in workfolio
        workfolio_emp_col = next((c for c in workfolio_df.columns if "emp" in c.lower()), "Employee")
        
        workfolio_df["mapped_employee_id"] = workfolio_df[workfolio_emp_col].map(emp_mapping).fillna(-999)
        
        # Find the status column
        activity_status_col = next((c for c in workfolio_df.columns if "status" in c.lower()), "Status")
        activity_duration_col = next((c for c in workfolio_df.columns if "duration" in c.lower()), "Activity Duration")
        
        # Convert activity duration to hours
        workfolio_df["activity_hours"] = workfolio_df[activity_duration_col].apply(parse_time_to_hours)
        
        # Split by productive/nonproductive
        workfolio_df["is_productive"] = workfolio_df[activity_status_col].str.lower().str.contains("productive", na=False)
        
        # Group by employee
        workfolio_agg = workfolio_df[workfolio_df["mapped_employee_id"] > -999].groupby("mapped_employee_id").agg({
            "activity_hours": "sum",
            "is_productive": lambda x: x.sum()
        }).reset_index()
        
        workfolio_agg.columns = ["employee_id", "total_activity_hours", "productive_hours"]
        workfolio_agg["nonproductive_hours"] = (workfolio_agg["total_activity_hours"] - workfolio_agg["productive_hours"]).round(2)
        workfolio_agg["productivity_ratio"] = (workfolio_agg["productive_hours"] / workfolio_agg["total_activity_hours"] * 100).round(2)
    
    # Merge task and workfolio metrics
    result = task_agg.merge(workfolio_agg, on="employee_id", how="left")
    
    # Fill missing workfolio data with 0
    result[["total_activity_hours", "productive_hours", "nonproductive_hours", "productivity_ratio"]] = \
        result[["total_activity_hours", "productive_hours", "nonproductive_hours", "productivity_ratio"]].fillna(0)
    
    # Round numeric columns
    result["total_time_taken_hours"] = result["total_time_taken_hours"].round(2)
    result["avg_time_per_task"] = result["avg_time_per_task"].round(2)
    
    return result.sort_values("completion_rate", ascending=False)


def _map_employees(task_df: pd.DataFrame, workfolio_df: pd.DataFrame, emp_name_col: str) -> Dict[str, int]:
    """Map workfolio 'Emp N' labels to task employee IDs by name similarity or sequence."""
    emp_id_col = next((c for c in task_df.columns if "emp" in c.lower() and "id" in c.lower()), "Employee Id")
    
    task_names = task_df[emp_name_col].unique()
    
    # Find the employee column in workfolio (could be "Employee", "employee", etc.)
    emp_col = next((c for c in workfolio_df.columns if "emp" in c.lower()), None)
    if emp_col is None:
        return {}
    
    workfolio_names = workfolio_df[emp_col].unique()
    
    mapping = {}
    for wf_name in workfolio_names:
        # Convert to string to safely call .lower()
        wf_name_str = str(wf_name).strip()
        
        # Try direct substring match
        for task_name in task_names:
            task_name_str = str(task_name).strip()
            if task_name_str.lower() in wf_name_str.lower() or wf_name_str.lower() in task_name_str.lower():
                emp_id = task_df[task_df[emp_name_col] == task_name][emp_id_col].iloc[0]
                mapping[wf_name] = emp_id
                break
        
        # If no match, assume sequential mapping (Emp 1 -> first employee, etc.)
        if wf_name not in mapping:
            try:
                emp_num = int(re.search(r"\d+", wf_name_str).group())
                emp_ids = sorted(task_df[emp_id_col].unique())
                if emp_num <= len(emp_ids):
                    mapping[wf_name] = emp_ids[emp_num - 1]
            except (ValueError, IndexError, AttributeError, TypeError):
                pass
    
    return mapping


def get_productivity_summary(metrics_df: pd.DataFrame) -> Dict:
    """Generate summary statistics from metrics."""
    return {
        "total_employees": len(metrics_df),
        "avg_completion_rate": metrics_df["completion_rate"].mean(),
        "avg_productivity_ratio": metrics_df["productivity_ratio"].mean(),
        "top_performer": metrics_df.loc[metrics_df["completion_rate"].idxmax()]["employee_name"],
        "highest_completion_rate": metrics_df["completion_rate"].max(),
        "lowest_completion_rate": metrics_df["completion_rate"].min(),
        "total_tasks": metrics_df["total_tasks"].sum(),
        "total_completed_tasks": metrics_df["completed_tasks"].sum(),
        "total_hours_tracked": metrics_df["total_time_taken_hours"].sum(),
        "avg_hours_per_employee": (metrics_df["total_time_taken_hours"].sum() / len(metrics_df)).round(2),
    }
