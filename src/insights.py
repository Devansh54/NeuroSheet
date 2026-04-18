"""Utilities for generating human-readable insights from analysis results."""

from __future__ import annotations

from typing import Any

import pandas as pd

from src.utils import format_value, is_identifier_like


def _pretty_name(column_name: str | None) -> str:
    """Convert a snake_case column name into readable text."""
    if not column_name:
        return "value"
    return column_name.replace("_", " ")


def _summarize_dataset_shape(analysis_results: dict[str, Any]) -> str:
    """Create a high-level overview of the cleaned dataset."""
    metrics = analysis_results["summary_metrics"]
    return (
        f"The cleaned dataset contains {format_value(metrics['row_count'])} rows and "
        f"{format_value(metrics['column_count'])} columns, including "
        f"{format_value(metrics['numeric_column_count'])} numeric, "
        f"{format_value(metrics['categorical_column_count'])} categorical, and "
        f"{format_value(metrics['date_column_count'])} date columns."
    )


def _summarize_target_metrics(analysis_results: dict[str, Any]) -> str | None:
    """Describe the main numeric target when it is meaningful."""
    metrics = analysis_results["summary_metrics"]
    target_column = metrics.get("target_column")
    if not target_column or is_identifier_like(target_column):
        return None

    target_total = metrics.get("target_total")
    target_average = metrics.get("target_average")
    if target_total is None or target_average is None:
        return None

    return (
        f"The total {_pretty_name(target_column)} is {format_value(target_total)}, "
        f"with an average of {format_value(target_average)} per record."
    )


def _summarize_grouping(analysis_results: dict[str, Any]) -> str | None:
    """Describe the leading group from the grouped summary."""
    grouped_summary = analysis_results["grouped_summary"]
    group_column = analysis_results["selected_columns"].get("group_column")
    target_column = analysis_results["selected_columns"].get("target_column")

    if grouped_summary.empty or not group_column:
        return None

    top_group = grouped_summary.iloc[0]
    if "total_value" in grouped_summary.columns and target_column and not is_identifier_like(target_column):
        return (
            f"The strongest {_pretty_name(group_column)} is {top_group[group_column]} with "
            f"a total {_pretty_name(target_column)} of {format_value(top_group['total_value'])} "
            f"across {format_value(int(top_group['record_count']))} records."
        )

    return (
        f"The most common {_pretty_name(group_column)} is {top_group[group_column]} with "
        f"{format_value(int(top_group['record_count']))} records."
    )


def _summarize_distribution(analysis_results: dict[str, Any]) -> str | None:
    """Add an insight about spread or category imbalance."""
    grouped_summary = analysis_results["grouped_summary"]
    group_column = analysis_results["selected_columns"].get("group_column")
    target_column = analysis_results["selected_columns"].get("target_column")

    if grouped_summary.empty or len(grouped_summary) < 2 or not group_column:
        return None

    top_group = grouped_summary.iloc[0]
    bottom_group = grouped_summary.iloc[-1]

    if "total_value" in grouped_summary.columns and target_column and not is_identifier_like(target_column):
        return (
            f"There is a visible gap between {_pretty_name(group_column)} groups: "
            f"{top_group[group_column]} leads with {format_value(top_group['total_value'])}, "
            f"while {bottom_group[group_column]} is at {format_value(bottom_group['total_value'])}."
        )

    return (
        f"The {_pretty_name(group_column)} distribution is uneven: "
        f"{top_group[group_column]} appears most often, while {bottom_group[group_column]} appears least often "
        f"within the top grouped results."
    )


def _summarize_trend(analysis_results: dict[str, Any]) -> str | None:
    """Describe the overall trend direction when date data exists."""
    trend_summary = analysis_results["trend_summary"]
    date_column = analysis_results["selected_columns"].get("date_column")
    target_column = analysis_results["selected_columns"].get("target_column")

    if trend_summary.empty or len(trend_summary) < 2 or not date_column:
        return None

    if "total_value" in trend_summary.columns and target_column and not is_identifier_like(target_column):
        first_value = trend_summary["total_value"].iloc[0]
        last_value = trend_summary["total_value"].iloc[-1]
        if last_value > first_value:
            direction = "increasing"
        elif last_value < first_value:
            direction = "decreasing"
        else:
            direction = "stable"

        return (
            f"The {_pretty_name(target_column)} trend over {_pretty_name(date_column)} appears {direction}, "
            f"moving from {format_value(first_value)} to {format_value(last_value)}."
        )

    first_value = trend_summary["record_count"].iloc[0]
    last_value = trend_summary["record_count"].iloc[-1]
    if last_value > first_value:
        direction = "increasing"
    elif last_value < first_value:
        direction = "decreasing"
    else:
        direction = "stable"

    return (
        f"The record volume over {_pretty_name(date_column)} appears {direction}, "
        f"changing from {format_value(int(first_value))} to {format_value(int(last_value))}."
    )


def _summarize_quality_flags(dataframe: pd.DataFrame) -> str | None:
    """Highlight remaining signs of sparse or fallback-filled data."""
    unknown_columns: list[tuple[str, int]] = []
    for column in dataframe.columns:
        if pd.api.types.is_object_dtype(dataframe[column]) or pd.api.types.is_string_dtype(dataframe[column]):
            unknown_count = int((dataframe[column] == "Unknown").sum())
            if unknown_count > 0:
                unknown_columns.append((column, unknown_count))

    if not unknown_columns:
        return None

    column_name, count = max(unknown_columns, key=lambda item: item[1])
    return (
        f"Some fields were incomplete in the source data. "
        f"The column {_pretty_name(column_name)} still contains {format_value(count)} fallback values marked as Unknown."
    )


def _summarize_top_record(analysis_results: dict[str, Any]) -> str | None:
    """Describe the top row when a true numeric target exists."""
    target_column = analysis_results["selected_columns"].get("target_column")
    top_record = analysis_results.get("top_record")
    group_column = analysis_results["selected_columns"].get("group_column")

    if not top_record or not target_column or is_identifier_like(target_column):
        return None

    group_text = ""
    if group_column and group_column in top_record:
        group_text = f" in {_pretty_name(group_column)} {top_record[group_column]}"

    return (
        f"The single highest {_pretty_name(target_column)} value is {format_value(top_record[target_column])}{group_text}."
    )


def generate_insights(dataframe: pd.DataFrame, analysis_results: dict[str, Any]) -> list[str]:
    """Generate simple human-readable insights from analysis outputs."""
    insights: list[str] = []

    builders = [
        lambda: _summarize_dataset_shape(analysis_results),
        lambda: _summarize_target_metrics(analysis_results),
        lambda: _summarize_grouping(analysis_results),
        lambda: _summarize_distribution(analysis_results),
        lambda: _summarize_trend(analysis_results),
        lambda: _summarize_top_record(analysis_results),
        lambda: _summarize_quality_flags(dataframe),
    ]

    for build_insight in builders:
        insight = build_insight()
        if insight and insight not in insights:
            insights.append(insight)

    if not insights:
        insights.append("The dataset is ready for review, but there is not enough structured variation yet to generate strong insights.")

    return insights
