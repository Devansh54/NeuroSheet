from pathlib import Path

import pandas as pd

from src.exporter import export_results


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
