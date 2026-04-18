"""Utilities for reading and combining multiple Excel files."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import pandas as pd

SUPPORTED_EXTENSIONS = {".xlsx"}


class DataLoadError(Exception):
    """Raised when Excel files cannot be loaded into a usable dataset."""


def _read_excel_file(file_source: Any, file_name: str) -> pd.DataFrame:
    """Read one Excel file and attach its source name to each row."""
    dataframe = pd.read_excel(file_source, engine="openpyxl")
    if dataframe.empty:
        raise ValueError("File is empty.")

    loaded = dataframe.copy()
    loaded["source_file"] = file_name
    return loaded


def _build_summary(
    combined_dataframe: pd.DataFrame,
    files_found: int,
    files_loaded: list[str],
    skipped_files: list[dict[str, str]],
) -> dict[str, Any]:
    """Create a small summary describing the load operation."""
    return {
        "files_found": files_found,
        "files_loaded": len(files_loaded),
        "loaded_file_names": files_loaded,
        "skipped_files": skipped_files,
        "total_rows_loaded": int(len(combined_dataframe)),
        "detected_columns": combined_dataframe.columns.tolist(),
    }


def load_excel_folder(folder_path: str) -> dict[str, Any]:
    """Load all supported Excel files from a folder and merge them."""
    folder = Path(folder_path).expanduser()
    if not folder.exists():
        raise DataLoadError(f"Folder not found: {folder_path}")
    if not folder.is_dir():
        raise DataLoadError(f"Expected a folder path but got: {folder_path}")

    excel_files = sorted(
        file_path
        for file_path in folder.iterdir()
        if file_path.is_file()
        and file_path.suffix.lower() in SUPPORTED_EXTENSIONS
        and not file_path.name.startswith("~$")
    )

    if not excel_files:
        raise DataLoadError("No .xlsx files were found in the selected folder.")

    loaded_frames: list[pd.DataFrame] = []
    loaded_file_names: list[str] = []
    skipped_files: list[dict[str, str]] = []

    for excel_file in excel_files:
        try:
            dataframe = _read_excel_file(excel_file, excel_file.name)
            loaded_frames.append(dataframe)
            loaded_file_names.append(excel_file.name)
        except Exception as error:
            skipped_files.append({"file": excel_file.name, "reason": str(error)})

    if not loaded_frames:
        raise DataLoadError("All Excel files were skipped. No usable data could be loaded.")

    combined_dataframe = pd.concat(loaded_frames, ignore_index=True, sort=False)
    summary = _build_summary(
        combined_dataframe=combined_dataframe,
        files_found=len(excel_files),
        files_loaded=loaded_file_names,
        skipped_files=skipped_files,
    )

    return {
        "data": combined_dataframe,
        "summary": summary,
    }


def load_uploaded_excel_files(uploaded_files: list[Any]) -> dict[str, Any]:
    """Load multiple uploaded Excel files and merge them."""
    if not uploaded_files:
        raise DataLoadError("No uploaded Excel files were provided.")

    loaded_frames: list[pd.DataFrame] = []
    loaded_file_names: list[str] = []
    skipped_files: list[dict[str, str]] = []

    for uploaded_file in uploaded_files:
        try:
            uploaded_file.seek(0)
            dataframe = _read_excel_file(uploaded_file, uploaded_file.name)
            loaded_frames.append(dataframe)
            loaded_file_names.append(uploaded_file.name)
        except Exception as error:
            skipped_files.append(
                {"file": getattr(uploaded_file, "name", "uploaded_file"), "reason": str(error)}
            )

    if not loaded_frames:
        raise DataLoadError("All uploaded Excel files were skipped. No usable data could be loaded.")

    combined_dataframe = pd.concat(loaded_frames, ignore_index=True, sort=False)
    summary = _build_summary(
        combined_dataframe=combined_dataframe,
        files_found=len(uploaded_files),
        files_loaded=loaded_file_names,
        skipped_files=skipped_files,
    )

    return {
        "data": combined_dataframe,
        "summary": summary,
    }
