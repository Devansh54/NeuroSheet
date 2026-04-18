from pathlib import Path

import pandas as pd
import pytest

from src.data_loader import DataLoadError, load_excel_folder


def test_load_excel_folder_reads_and_tracks_source(tmp_path: Path) -> None:
    first = tmp_path / "sales_a.xlsx"
    second = tmp_path / "sales_b.xlsx"
    pd.DataFrame({"Sales": [100, 200], "Region": ["North", "South"]}).to_excel(first, index=False)
    pd.DataFrame({"Sales": [300], "Region": ["West"]}).to_excel(second, index=False)

    result = load_excel_folder(str(tmp_path))

    assert result["summary"]["files_loaded"] == 2
    assert result["summary"]["total_rows_loaded"] == 3
    assert "source_file" in result["data"].columns
    assert set(result["data"]["source_file"]) == {"sales_a.xlsx", "sales_b.xlsx"}


def test_load_excel_folder_rejects_missing_folder(tmp_path: Path) -> None:
    missing = tmp_path / "missing"
    with pytest.raises(DataLoadError):
        load_excel_folder(str(missing))


def test_load_excel_folder_skips_empty_excel_files(tmp_path: Path) -> None:
    empty = tmp_path / "empty.xlsx"
    valid = tmp_path / "valid.xlsx"
    pd.DataFrame().to_excel(empty, index=False)
    pd.DataFrame({"Sales": [50]}).to_excel(valid, index=False)

    result = load_excel_folder(str(tmp_path))

    assert result["summary"]["files_loaded"] == 1
    assert result["summary"]["skipped_files"][0]["file"] == "empty.xlsx"
