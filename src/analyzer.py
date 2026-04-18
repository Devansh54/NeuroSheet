"""Utilities for summary analysis and grouping."""

from __future__ import annotations

from typing import Any

import pandas as pd

from src.utils import choose_default_columns, detect_column_types


class DataAnalysisError(Exception):
    """Raised when analysis cannot be performed on the cleaned dataset."""


def _summarize_numeric_columns(dataframe: pd.DataFrame, numeric_columns: list[str]) -> dict[str, dict[str, float]]:
    """Build high-level statistics for each numeric column."""
    overview: dict[str, dict[str, float]] = {}
    for column in numeric_columns:
        overview[column] = {
            "sum": float(dataframe[column].sum()),
            "mean": float(dataframe[column].mean()),
            "min": float(dataframe[column].min()),
            "max": float(dataframe[column].max()),
            "count": float(dataframe[column].count()),
        }
    return overview


def _build_grouped_summary(
    dataframe: pd.DataFrame,
    group_column: str | None,
    target_column: str | None,
) -> pd.DataFrame:
    """Create grouped counts and optional numeric aggregates."""
    if not group_column or group_column not in dataframe.columns:
        return pd.DataFrame()

    if target_column and target_column in dataframe.columns and pd.api.types.is_numeric_dtype(dataframe[target_column]):
        grouped = (
            dataframe.groupby(group_column, dropna=False)[target_column]
            .agg(record_count="count", total_value="sum", average_value="mean")
            .sort_values(by=["total_value", "record_count"], ascending=[False, False])
            .reset_index()
        )
        return grouped.head(10)

    grouped = (
        dataframe.groupby(group_column, dropna=False)
        .size()
        .reset_index(name="record_count")
        .sort_values(by="record_count", ascending=False)
        .head(10)
    )
    return grouped


def _build_trend_summary(
    dataframe: pd.DataFrame,
    date_column: str | None,
    target_column: str | None,
) -> pd.DataFrame:
    """Create a date-based trend summary when a date column exists."""
    if not date_column or date_column not in dataframe.columns:
        return pd.DataFrame()

    trend_source = dataframe.dropna(subset=[date_column]).copy()
    if trend_source.empty:
        return pd.DataFrame()

    if target_column and target_column in trend_source.columns and pd.api.types.is_numeric_dtype(trend_source[target_column]):
        trend = (
            trend_source.groupby(date_column)[target_column]
            .agg(total_value="sum", average_value="mean", record_count="count")
            .reset_index()
            .sort_values(date_column)
        )
        return trend

    trend = (
        trend_source.groupby(date_column)
        .size()
        .reset_index(name="record_count")
        .sort_values(date_column)
    )
    return trend


def _build_top_record(dataframe: pd.DataFrame, target_column: str | None) -> dict[str, Any] | None:
    """Return the row with the highest target value when possible."""
    if not target_column or target_column not in dataframe.columns:
        return None
    if not pd.api.types.is_numeric_dtype(dataframe[target_column]):
        return None
    if dataframe[target_column].dropna().empty:
        return None

    top_index = dataframe[target_column].idxmax()
    return dataframe.loc[top_index].to_dict()


def analyze_dataframe(
    dataframe: pd.DataFrame,
    target_column: str | None = None,
    group_column: str | None = None,
    date_column: str | None = None,
) -> dict[str, Any]:
    """Analyze cleaned data and return summary-ready outputs."""
    if dataframe.empty:
        raise DataAnalysisError("The cleaned dataset is empty and cannot be analyzed.")

    column_types = detect_column_types(dataframe)
    defaults = choose_default_columns(dataframe)

    if target_column not in column_types["numeric"]:
        target_column = defaults["target_column"]
    if group_column not in dataframe.columns:
        group_column = defaults["group_column"]
    if date_column not in column_types["date"]:
        date_column = defaults["date_column"]

    numeric_overview = _summarize_numeric_columns(dataframe, column_types["numeric"])
    grouped_summary = _build_grouped_summary(dataframe, group_column, target_column)
    trend_summary = _build_trend_summary(dataframe, date_column, target_column)
    top_record = _build_top_record(dataframe, target_column)

    summary_metrics = {
        "row_count": int(len(dataframe)),
        "column_count": int(len(dataframe.columns)),
        "numeric_column_count": int(len(column_types["numeric"])),
        "categorical_column_count": int(len(column_types["categorical"])),
        "date_column_count": int(len(column_types["date"])),
        "target_column": target_column,
        "group_column": group_column,
        "date_column": date_column,
        "missing_value_count": int(dataframe.isna().sum().sum()),
    }

    if target_column and target_column in numeric_overview:
        summary_metrics["target_total"] = numeric_overview[target_column]["sum"]
        summary_metrics["target_average"] = numeric_overview[target_column]["mean"]

    return {
        "summary_metrics": summary_metrics,
        "column_types": column_types,
        "numeric_overview": numeric_overview,
        "grouped_summary": grouped_summary,
        "trend_summary": trend_summary,
        "top_record": top_record,
        "selected_columns": {
            "target_column": target_column,
            "group_column": group_column,
            "date_column": date_column,
        },
    }
