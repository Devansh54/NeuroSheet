"""Shared helpers for NeuroSheet data processing."""

from __future__ import annotations

from typing import Any

import pandas as pd


TARGET_KEYWORDS = (
    "sales",
    "revenue",
    "amount",
    "profit",
    "price",
    "total",
    "count",
    "number",
)

GROUP_KEYWORDS = (
    "category",
    "region",
    "country",
    "state",
    "council",
    "grade",
    "status",
    "type",
    "employer",
)

DATE_KEYWORDS = ("date", "day", "month", "year", "time")
IDENTIFIER_KEYWORDS = ("id", "number", "customer_number", "member_customer_number")


def detect_column_types(dataframe: pd.DataFrame) -> dict[str, list[str]]:
    """Detect numeric, date, and categorical columns from a dataframe."""
    numeric_columns = [
        column
        for column in dataframe.columns
        if pd.api.types.is_numeric_dtype(dataframe[column])
        and not pd.api.types.is_bool_dtype(dataframe[column])
    ]
    date_columns = [
        column for column in dataframe.columns if pd.api.types.is_datetime64_any_dtype(dataframe[column])
    ]
    categorical_columns = [
        column
        for column in dataframe.columns
        if column not in numeric_columns and column not in date_columns
    ]
    return {
        "numeric": numeric_columns,
        "date": date_columns,
        "categorical": categorical_columns,
    }


def _pick_by_keywords(columns: list[str], keywords: tuple[str, ...]) -> str | None:
    """Pick the first column containing a preferred keyword."""
    lowered = [(column, column.lower()) for column in columns]
    for keyword in keywords:
        for original, lowered_name in lowered:
            if keyword in lowered_name:
                return original
    return None


def choose_default_columns(dataframe: pd.DataFrame) -> dict[str, str | None]:
    """Choose sensible default columns for analysis."""
    column_types = detect_column_types(dataframe)

    numeric_candidates = [
        column
        for column in column_types["numeric"]
        if column != "source_file"
        and dataframe[column].nunique(dropna=True) > 1
        and not is_identifier_like(column)
    ]
    categorical_candidates = [
        column
        for column in column_types["categorical"]
        if column != "source_file" and dataframe[column].nunique(dropna=True) > 1
    ]

    target_column = _pick_by_keywords(numeric_candidates, TARGET_KEYWORDS)
    if not target_column and numeric_candidates:
        target_column = numeric_candidates[0]

    group_column = _pick_by_keywords(categorical_candidates, GROUP_KEYWORDS)
    if not group_column and categorical_candidates:
        group_column = categorical_candidates[0]

    date_column = _pick_by_keywords(column_types["date"], DATE_KEYWORDS)
    if not date_column and column_types["date"]:
        date_column = column_types["date"][0]

    return {
        "target_column": target_column,
        "group_column": group_column,
        "date_column": date_column,
    }


def format_value(value: Any) -> str:
    """Format values for readable console or UI output."""
    if value is None:
        return "N/A"
    if isinstance(value, float):
        if pd.isna(value):
            return "N/A"
        return f"{value:,.2f}"
    if isinstance(value, int):
        return f"{value:,}"
    if isinstance(value, pd.Timestamp):
        return value.strftime("%Y-%m-%d")
    return str(value)


def is_identifier_like(column_name: str | None) -> bool:
    """Identify columns that behave more like record identifiers than measures."""
    if not column_name:
        return False
    lowered = column_name.lower()
    return any(keyword in lowered for keyword in IDENTIFIER_KEYWORDS)
