#!/usr/bin/env python3
"""
Simulate the Admin Dashboard workflow to verify all components work together.
"""
from productivity_analyzer import load_and_merge_data, extract_employee_metrics, get_productivity_summary
from dashboard_charts import create_summary_cards, chart_employee_completion_rate
import os

print("=" * 60)
print("ADMIN DASHBOARD WORKFLOW TEST")
print("=" * 60)

try:
    # Load data (as Admin Dashboard does)
    task_csv_path = os.path.join("data", "task_allocation.csv")
    work_csv_path = os.path.join("data", "workfolio_active_hours.csv")
    
    print(f"\n1. Loading data from:")
    print(f"   - Task: {task_csv_path}")
    print(f"   - Workfolio: {work_csv_path}")
    
    task_df_data, workfolio_df_data = load_and_merge_data(task_csv_path, work_csv_path)
    print(f"   ✓ Loaded {len(task_df_data)} tasks and {len(workfolio_df_data)} workfolio records")
    
    # Extract metrics
    print("\n2. Extracting employee metrics...")
    metrics_df = extract_employee_metrics(task_df_data, workfolio_df_data)
    print(f"   ✓ Extracted metrics for {len(metrics_df)} employees")
    print(f"   ✓ Columns: {metrics_df.columns.tolist()}")
    
    # Generate summary
    print("\n3. Generating summary statistics...")
    summary = get_productivity_summary(metrics_df)
    print(f"   ✓ Summary keys: {list(summary.keys())}")
    
    # Create summary cards
    print("\n4. Creating summary cards...")
    summary_cards = create_summary_cards(summary)
    print(f"   ✓ Created {len(summary_cards)} summary cards")
    for key, value in summary_cards.items():
        print(f"      - {key}: {value}")
    
    # Test one chart
    print("\n5. Creating sample chart (completion rate)...")
    fig = chart_employee_completion_rate(metrics_df)
    print(f"   ✓ Chart created: {type(fig).__name__}")
    
    print("\n" + "=" * 60)
    print("✅ ALL TESTS PASSED - DASHBOARD READY!")
    print("=" * 60)
    
except Exception as e:
    print(f"\n❌ ERROR: {e}")
    import traceback
    traceback.print_exc()
    exit(1)
