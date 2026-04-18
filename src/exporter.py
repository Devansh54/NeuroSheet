"""Utilities for exporting cleaned data and analysis reports."""

from __future__ import annotations

from datetime import datetime
from pathlib import Path
from typing import Any

import pandas as pd


class ExportError(Exception):
    """Raised when export artifacts cannot be written safely."""


def _timestamp_slug() -> str:
    """Return a stable timestamp for export file names."""
    return datetime.now().strftime("%Y%m%d_%H%M%S")


def _prepare_export_dataframe(dataframe: pd.DataFrame) -> pd.DataFrame:
    """Convert datetime columns to strings before writing CSV."""
    export_frame = dataframe.copy()
    for column in export_frame.columns:
        if pd.api.types.is_datetime64_any_dtype(export_frame[column]):
            export_frame[column] = export_frame[column].dt.strftime("%Y-%m-%d")
    return export_frame


def build_report_text(
    load_summary: dict[str, Any],
    clean_summary: dict[str, Any],
    analysis_result: dict[str, Any],
    insights: list[str],
    prediction: dict[str, Any],
) -> str:
    """Build a plain-text report from current pipeline outputs."""
    metrics = analysis_result["summary_metrics"]
    lines: list[str] = [
        "NeuroSheet Export Report",
        "",
        "Load Summary",
        f"- Files found: {load_summary['files_found']}",
        f"- Files loaded: {load_summary['files_loaded']}",
        f"- Rows loaded: {load_summary['total_rows_loaded']}",
        "",
        "Cleaning Summary",
        f"- Final rows: {clean_summary['final_rows']}",
        f"- Duplicate rows removed: {clean_summary['duplicate_rows_removed']}",
        f"- Missing values before fill: {clean_summary['missing_values_before_fill']}",
        f"- Missing values after fill: {clean_summary['missing_values_after_fill']}",
        "",
        "Analysis Summary",
        f"- Row count: {metrics['row_count']}",
        f"- Column count: {metrics['column_count']}",
        f"- Numeric columns: {metrics['numeric_column_count']}",
        f"- Date columns: {metrics['date_column_count']}",
        f"- Target column: {metrics.get('target_column') or 'Not identified'}",
        f"- Group column: {metrics.get('group_column') or 'Not identified'}",
        f"- Date column: {metrics.get('date_column') or 'Not identified'}",
        "",
        "Insights",
    ]
    lines.extend(f"- {insight}" for insight in insights)
    lines.extend(["", "Forecast"])
    if prediction["available"]:
        lines.extend(
            [
                f"- Method: {prediction['method']}",
                f"- Next label: {prediction['next_label']}",
                f"- Predicted value: {prediction['predicted_value']}",
                f"- Direction: {prediction['direction']}",
                f"- R2 score: {prediction['r2_score']}",
            ]
        )
    else:
        lines.append(f"- Status: {prediction['reason']}")
    lines.append("")
    return "\n".join(lines)


def export_results(
    cleaned_data: pd.DataFrame,
    load_summary: dict[str, Any],
    clean_summary: dict[str, Any],
    analysis_result: dict[str, Any],
    insights: list[str],
    prediction: dict[str, Any],
    output_dir: str = "outputs",
) -> dict[str, Any]:
    """Write cleaned data and report artifacts to the outputs directory."""
    output_path = Path(output_dir).expanduser()
    try:
        output_path.mkdir(parents=True, exist_ok=True)
    except OSError as error:
        raise ExportError(f"Could not create export directory '{output_dir}': {error}") from error

    stamp = _timestamp_slug()
    csv_path = output_path / f"neurosheet_cleaned_data_{stamp}.csv"
    report_path = output_path / f"neurosheet_report_{stamp}.txt"

    try:
        _prepare_export_dataframe(cleaned_data).to_csv(csv_path, index=False)
        report_path.write_text(
            build_report_text(load_summary, clean_summary, analysis_result, insights, prediction),
            encoding="utf-8",
        )
    except OSError as error:
        raise ExportError(f"Failed to write export files: {error}") from error

    return {
        "status": "success",
        "output_dir": str(output_path.resolve()),
        "cleaned_data_path": str(csv_path.resolve()),
        "report_path": str(report_path.resolve()),
    }
