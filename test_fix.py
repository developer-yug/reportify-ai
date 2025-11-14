#!/usr/bin/env python3
from productivity_analyzer import load_and_merge_data, extract_employee_metrics

# Test the fixed code
try:
    task_df, workfolio_df = load_and_merge_data('data/task_allocation.csv', 'data/workfolio_active_hours.csv')
    metrics = extract_employee_metrics(task_df, workfolio_df)
    print("✓ Dashboard data loaded successfully")
    print(f"✓ Metrics shape: {metrics.shape}")
    print(f"✓ Employees: {metrics['employee_name'].tolist()}")
    print("\nMetrics columns:")
    print(metrics.columns.tolist())
    print("\nFix SUCCESSFUL - ready to test in Streamlit!")
except Exception as e:
    print(f"✗ Error: {e}")
    import traceback
    traceback.print_exc()
