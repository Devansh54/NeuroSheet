"""Utilities for cleaning merged Excel data."""

from __future__ import annotations

import re
from typing import Any

import pandas as pd


class DataCleaningError(Exception):
    """Raised when the merged dataset cannot be cleaned safely."""


def _standardize_column_name(column_name: Any) -> str:
    """Convert a raw column label into lowercase snake_case."""
    normalized = re.sub(r"[^a-zA-Z0-9]+", "_", str(column_name).strip().lower())
    normalized = re.sub(r"_+", "_", normalized).strip("_")
    return normalized or "unnamed_column"


def _rename_columns(dataframe: pd.DataFrame) -> tuple[pd.DataFrame, dict[str, str]]:
    """Rename columns into a standard format."""
    rename_map: dict[str, str] = {}
    renamed_columns: list[str] = []
    original_name_counts: dict[str, int] = {}
    standardized_name_counts: dict[str, int] = {}

    for column in dataframe.columns:
        original_label = str(column)
        original_count = original_name_counts.get(original_label, 0) + 1
        original_name_counts[original_label] = original_count

        base_name = _standardize_column_name(column)
        standardized_count = standardized_name_counts.get(base_name, 0) + 1
        standardized_name_counts[base_name] = standardized_count
        resolved_name = base_name if standardized_count == 1 else f"{base_name}_{standardized_count}"

        summary_key = original_label if original_count == 1 else f"{original_label} [{original_count}]"
        rename_map[summary_key] = resolved_name
        renamed_columns.append(resolved_name)

    renamed = dataframe.copy()
    renamed.columns = renamed_columns
    return renamed, rename_map


def _normalize_text_columns(dataframe: pd.DataFrame) -> pd.DataFrame:
    """Strip whitespace and normalize blank-like values for text columns."""
    normalized = dataframe.copy()
    for column in normalized.select_dtypes(include=["object", "string"]).columns:
        normalized[column] = normalized[column].astype("string").str.strip()
        normalized[column] = normalized[column].replace({"": pd.NA, "nan": pd.NA, "None": pd.NA})
    return normalized


def _convert_numeric_columns(dataframe: pd.DataFrame) -> tuple[pd.DataFrame, list[str]]:
    """Convert object columns to numeric when most values look numeric."""
    converted = dataframe.copy()
    converted_columns: list[str] = []

    for column in converted.columns:
        is_text_like = pd.api.types.is_object_dtype(converted[column]) or pd.api.types.is_string_dtype(
            converted[column]
        )
        if column == "source_file" or not is_text_like:
            continue

        cleaned_text = (
            converted[column]
            .astype("string")
            .str.replace(",", "", regex=False)
            .str.replace("$", "", regex=False)
            .str.replace("%", "", regex=False)
            .str.strip()
        )
        numeric_series = pd.to_numeric(cleaned_text, errors="coerce")
        non_null_count = converted[column].notna().sum()
        if non_null_count == 0:
            continue

        success_ratio = numeric_series.notna().sum() / non_null_count
        if success_ratio >= 0.8:
            converted[column] = numeric_series
            converted_columns.append(column)

    return converted, converted_columns


def _convert_date_columns(dataframe: pd.DataFrame) -> tuple[pd.DataFrame, list[str]]:
    """Convert likely date columns into pandas datetime values."""
    converted = dataframe.copy()
    converted_columns: list[str] = []

    for column in converted.columns:
        is_text_like = pd.api.types.is_object_dtype(converted[column]) or pd.api.types.is_string_dtype(
            converted[column]
        )
        if not is_text_like:
            continue
        if "date" not in column and "day" not in column and "month" not in column:
            continue

        parsed = pd.to_datetime(converted[column], errors="coerce")
        non_null_count = converted[column].notna().sum()
        if non_null_count == 0:
            continue

        success_ratio = parsed.notna().sum() / non_null_count
        if success_ratio >= 0.6:
            converted[column] = parsed
            converted_columns.append(column)

    return converted, converted_columns


def _fill_missing_values(dataframe: pd.DataFrame) -> tuple[pd.DataFrame, dict[str, str]]:
    """Fill missing values with beginner-friendly defaults."""
    filled = dataframe.copy()
    fill_actions: dict[str, str] = {}

    for column in filled.columns:
        if not filled[column].isna().any():
            continue

        if pd.api.types.is_numeric_dtype(filled[column]):
            median_value = filled[column].median()
            fallback = 0 if pd.isna(median_value) else median_value
            filled[column] = filled[column].fillna(fallback)
            fill_actions[column] = f"Filled numeric nulls with median value {fallback}."
        elif pd.api.types.is_datetime64_any_dtype(filled[column]):
            filled[column] = filled[column].ffill().bfill()
            fill_actions[column] = "Filled date nulls using nearest available dates."
        else:
            filled[column] = filled[column].fillna("Unknown")
            fill_actions[column] = 'Filled text nulls with "Unknown".'

    return filled, fill_actions


def clean_dataframe(dataframe: pd.DataFrame) -> dict[str, Any]:
    """Clean a merged dataframe and return the cleaned output plus a summary."""
    if dataframe.empty:
        raise DataCleaningError("The merged dataset is empty and cannot be cleaned.")

    working = dataframe.copy()
    initial_shape = working.shape

    working.dropna(how="all", inplace=True)
    rows_after_empty_drop = len(working)

    working, renamed_columns = _rename_columns(working)
    working = _normalize_text_columns(working)
    working, numeric_columns = _convert_numeric_columns(working)
    working, date_columns = _convert_date_columns(working)

    duplicate_rows_removed = int(working.duplicated().sum())
    working.drop_duplicates(inplace=True)

    missing_before_fill = int(working.isna().sum().sum())
    working, fill_actions = _fill_missing_values(working)
    missing_after_fill = int(working.isna().sum().sum())

    cleaned = working.reset_index(drop=True)
    summary = {
        "initial_rows": int(initial_shape[0]),
        "initial_columns": int(initial_shape[1]),
        "rows_after_empty_row_removal": int(rows_after_empty_drop),
        "final_rows": int(cleaned.shape[0]),
        "final_columns": int(cleaned.shape[1]),
        "duplicate_rows_removed": duplicate_rows_removed,
        "missing_values_before_fill": missing_before_fill,
        "missing_values_after_fill": missing_after_fill,
        "renamed_columns": renamed_columns,
        "numeric_columns_converted": numeric_columns,
        "date_columns_converted": date_columns,
        "fill_actions": fill_actions,
    }

    return {
        "data": cleaned,
        "summary": summary,
    }
