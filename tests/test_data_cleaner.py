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
