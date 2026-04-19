from pathlib import Path

import pandas as pd

from src.exporter import build_report_text, export_results


def test_export_results_writes_csv_and_report(tmp_path: Path) -> None:
    dataframe = pd.DataFrame({"date": pd.to_datetime(["2024-01-01"]), "sales": [100]})
    result = export_results(
        cleaned_data=dataframe,
        load_summary={
            "files_found": 1,
            "files_loaded": 1,
            "loaded_file_names": ["demo.xlsx"],
            "skipped_files": [],
            "total_rows_loaded": 1,
            "detected_columns": ["date", "sales"],
        },
        clean_summary={
            "final_rows": 1,
            "duplicate_rows_removed": 0,
            "missing_values_before_fill": 0,
            "missing_values_after_fill": 0,
        },
        analysis_result={
            "summary_metrics": {
                "row_count": 1,
                "column_count": 2,
                "numeric_column_count": 1,
                "date_column_count": 1,
                "target_column": "sales",
                "group_column": None,
                "date_column": "date",
            }
        },
        insights=["Sales remain stable."],
        prediction={"available": False, "reason": "No forecast"},
        output_dir=str(tmp_path),
    )

    assert Path(result["cleaned_data_path"]).exists()
    assert Path(result["report_path"]).exists()


def test_build_report_text_includes_loaded_files_and_confidence_note() -> None:
    report = build_report_text(
        load_summary={
            "files_found": 2,
            "files_loaded": 2,
            "loaded_file_names": ["a.xlsx", "b.xlsx"],
            "skipped_files": [{"file": "bad.xlsx", "reason": "File is empty."}],
            "total_rows_loaded": 8,
        },
        clean_summary={
            "final_rows": 8,
            "duplicate_rows_removed": 1,
            "missing_values_before_fill": 2,
            "missing_values_after_fill": 0,
        },
        analysis_result={
            "summary_metrics": {
                "row_count": 8,
                "column_count": 3,
                "numeric_column_count": 1,
                "date_column_count": 1,
                "target_column": "sales",
                "group_column": "region",
                "date_column": "date",
            }
        },
        insights=["Sales trend is increasing."],
        prediction={
            "available": True,
            "method": "Linear Regression",
            "next_label": "2024-05-01",
            "predicted_value": 210.0,
            "direction": "growth",
            "r2_score": 0.91,
            "confidence_note": "The fitted trend is strong on a time-based model using broader history, so treat this as directional guidance.",
        },
    )

    assert "Loaded file names: a.xlsx, b.xlsx" in report
    assert "Skipped files: 1" in report
    assert "Skipped detail: bad.xlsx -> File is empty." in report
    assert "Confidence note:" in report
