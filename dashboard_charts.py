"""
Dashboard chart generation module.
Creates Plotly visualizations from extracted employee productivity metrics.
"""

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from typing import Optional, Dict


def chart_employee_completion_rate(metrics_df: pd.DataFrame):
    """Bar chart: Employee completion rates."""
    fig = px.bar(
        metrics_df,
        x="employee_name",
        y="completion_rate",
        title="📊 Task Completion Rate by Employee",
        labels={"completion_rate": "Completion Rate (%)", "employee_name": "Employee"},
        color="completion_rate",
        color_continuous_scale="RdYlGn",
        range_color=[0, 100],
        text="completion_rate"
    )
    fig.update_traces(texttemplate='%{text:.1f}%', textposition='outside')
    fig.update_layout(height=400, showlegend=False, hovermode="x unified")
    return fig


def chart_tasks_completed(metrics_df: pd.DataFrame):
    """Grouped bar chart: Total tasks vs completed tasks."""
    data_plot = metrics_df[["employee_name", "completed_tasks", "overdue_tasks"]].copy()
    
    fig = go.Figure(data=[
        go.Bar(x=data_plot["employee_name"], y=data_plot["completed_tasks"], 
               name="Completed", marker_color="green", text=data_plot["completed_tasks"], textposition='auto'),
        go.Bar(x=data_plot["employee_name"], y=data_plot["overdue_tasks"], 
               name="Overdue", marker_color="red", text=data_plot["overdue_tasks"], textposition='auto')
    ])
    fig.update_layout(
        title="✅ Task Status Distribution",
        xaxis_title="Employee",
        yaxis_title="Task Count",
        barmode="stack",
        height=400,
        hovermode="x unified"
    )
    return fig


def chart_total_hours_worked(metrics_df: pd.DataFrame):
    """Bar chart: Total hours worked per employee."""
    fig = px.bar(
        metrics_df,
        x="employee_name",
        y="total_time_taken_hours",
        title="⏱️ Total Hours Worked per Employee",
        labels={"total_time_taken_hours": "Total Hours", "employee_name": "Employee"},
        color="total_time_taken_hours",
        color_continuous_scale="Blues",
        text="total_time_taken_hours"
    )
    fig.update_traces(texttemplate='%{text:.2f}h', textposition='outside')
    fig.update_layout(height=400, showlegend=False, hovermode="x unified")
    return fig


def chart_productivity_ratio(metrics_df: pd.DataFrame):
    """Pie chart: Employees by productivity ratio (only those with activity data)."""
    df_with_activity = metrics_df[metrics_df["total_activity_hours"] > 0].copy()
    
    if len(df_with_activity) == 0:
        return None
    
    fig = px.pie(
        df_with_activity,
        values="total_activity_hours",
        names="employee_name",
        title="🎯 Active Hours Distribution",
        labels={"total_activity_hours": "Active Hours"}
    )
    fig.update_layout(height=400)
    return fig


def chart_productive_vs_nonproductive(metrics_df: pd.DataFrame):
    """Grouped bar chart: Productive vs nonproductive hours."""
    df_with_activity = metrics_df[metrics_df["total_activity_hours"] > 0].copy()
    
    if len(df_with_activity) == 0:
        return None
    
    fig = go.Figure(data=[
        go.Bar(x=df_with_activity["employee_name"], y=df_with_activity["productive_hours"], 
               name="Productive", marker_color="lightgreen"),
        go.Bar(x=df_with_activity["employee_name"], y=df_with_activity["nonproductive_hours"], 
               name="Non-Productive", marker_color="lightcoral")
    ])
    fig.update_layout(
        title="📈 Productive vs Non-Productive Hours",
        xaxis_title="Employee",
        yaxis_title="Hours",
        barmode="stack",
        height=400,
        hovermode="x unified"
    )
    return fig


def chart_avg_time_per_task(metrics_df: pd.DataFrame):
    """Bar chart: Average time per task (efficiency metric)."""
    fig = px.bar(
        metrics_df,
        x="employee_name",
        y="avg_time_per_task",
        title="⚡ Average Time per Task",
        labels={"avg_time_per_task": "Avg Hours", "employee_name": "Employee"},
        color="avg_time_per_task",
        color_continuous_scale="Viridis",
        text="avg_time_per_task"
    )
    fig.update_traces(texttemplate='%{text:.2f}h', textposition='outside')
    fig.update_layout(height=400, showlegend=False, hovermode="x unified")
    return fig


def chart_productivity_scatter(metrics_df: pd.DataFrame):
    """Scatter plot: Completion rate vs productivity ratio."""
    df_with_activity = metrics_df[metrics_df["total_activity_hours"] > 0].copy()
    
    if len(df_with_activity) == 0:
        # Show all employees on X-axis, but note missing activity data
        fig = px.scatter(
            metrics_df,
            x="completion_rate",
            y="total_time_taken_hours",
            title="📊 Completion Rate vs Hours Worked",
            labels={"completion_rate": "Completion Rate (%)", "total_time_taken_hours": "Total Hours"},
            hover_data=["employee_name", "completed_tasks"],
            color_discrete_sequence=["#3b82f6"],
            size=[10] * len(metrics_df)
        )
    else:
        fig = px.scatter(
            df_with_activity,
            x="completion_rate",
            y="productivity_ratio",
            title="🎯 Completion Rate vs Productivity Ratio",
            labels={"completion_rate": "Completion Rate (%)", "productivity_ratio": "Productivity Ratio (%)"},
            hover_data=["employee_name", "total_tasks", "productive_hours"],
            color="total_time_taken_hours",
            color_continuous_scale="Viridis",
            size=[15] * len(df_with_activity),
            range_x=[0, 105],
            range_y=[0, 105]
        )
    
    fig.update_layout(height=400, hovermode="closest")
    return fig


def chart_completion_rate_distribution(metrics_df: pd.DataFrame):
    """Histogram: Distribution of completion rates."""
    fig = px.histogram(
        metrics_df,
        x="completion_rate",
        nbins=5,
        title="📉 Completion Rate Distribution",
        labels={"completion_rate": "Completion Rate (%)"},
        color_discrete_sequence=["#3b82f6"]
    )
    fig.update_layout(height=400, showlegend=False)
    return fig


def create_summary_cards(summary: dict) -> dict:
    """Prepare summary statistics for UI display."""
    return {
        "Total Employees": summary["total_employees"],
        "Avg Completion Rate": f"{summary['avg_completion_rate']:.1f}%",
        "Top Performer": summary["top_performer"],
        "Highest Completion": f"{summary['highest_completion_rate']:.1f}%",
        "Total Tasks": summary["total_tasks"],
        "Completed Tasks": summary["total_completed_tasks"],
        "Total Hours Tracked": f"{summary['total_hours_tracked']:.1f}h",
    }
