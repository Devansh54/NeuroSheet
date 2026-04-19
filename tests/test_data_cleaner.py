import pandas as pd

from src.data_cleaner import clean_dataframe


def test_clean_dataframe_standardizes_and_fills_values() -> None:
    dataframe = pd.DataFrame(
        {
            " Sales Amount ": ["100", None, "300"],
            "Region": [" North ", None, "South"],
            "Join Date": ["2024-01-01", "2024-01-02", None],
        }
    )

    result = clean_dataframe(dataframe)
    cleaned = result["data"]

    assert list(cleaned.columns) == ["sales_amount", "region", "join_date"]
    assert cleaned["sales_amount"].tolist() == [100.0, 200.0, 300.0]
    assert cleaned["region"].tolist() == ["North", "Unknown", "South"]
    assert str(cleaned["join_date"].iloc[2].date()) == "2024-01-02"


def test_clean_dataframe_removes_duplicates() -> None:
    dataframe = pd.DataFrame(
        {
            "Sales": [10, 10, 20],
            "Region": ["East", "East", "West"],
        }
    )

    result = clean_dataframe(dataframe)

    assert result["summary"]["duplicate_rows_removed"] == 1
    assert len(result["data"]) == 2


def test_clean_dataframe_handles_colliding_standardized_column_names() -> None:
    dataframe = pd.DataFrame(
        [
            ["2024-01-01", "2024-02-01", "2024-03-01", "North"],
            ["2024-01-02", "2024-02-02", "2024-03-02", "South"],
        ],
        columns=["Join Date", "Join-Date", "Join Date", "Region"],
    )

    result = clean_dataframe(dataframe)
    cleaned = result["data"]

    assert list(cleaned.columns) == ["join_date", "join_date_2", "join_date_3", "region"]
    assert str(cleaned["join_date"].iloc[0].date()) == "2024-01-01"
    assert str(cleaned["join_date_2"].iloc[0].date()) == "2024-02-01"
    assert str(cleaned["join_date_3"].iloc[0].date()) == "2024-03-01"
    assert result["summary"]["renamed_columns"]["Join Date"] == "join_date"
    assert result["summary"]["renamed_columns"]["Join Date [2]"] == "join_date_3"
