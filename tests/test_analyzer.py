import pandas as pd

from src.analyzer import analyze_dataframe


def test_analyze_dataframe_builds_group_and_trend_summaries() -> None:
    dataframe = pd.DataFrame(
        {
            "date": pd.to_datetime(["2024-01-01", "2024-01-01", "2024-02-01", "2024-02-01"]),
            "region": ["North", "South", "North", "South"],
            "sales": [100, 200, 150, 250],
        }
    )

    result = analyze_dataframe(dataframe, target_column="sales", group_column="region", date_column="date")

    assert result["summary_metrics"]["target_column"] == "sales"
    assert not result["grouped_summary"].empty
    assert not result["trend_summary"].empty
    assert result["summary_metrics"]["target_total"] == 700.0


def test_analyze_dataframe_handles_categorical_only_grouping() -> None:
    dataframe = pd.DataFrame({"region": ["North", "North", "South"], "status": ["Open", "Closed", "Open"]})

    result = analyze_dataframe(dataframe, group_column="region")

    assert result["summary_metrics"]["group_column"] == "region"
    assert "record_count" in result["grouped_summary"].columns


def test_analyze_dataframe_picks_first_meaningful_numeric_target_without_keyword_match() -> None:
    dataframe = pd.DataFrame(
        {
            "region": ["North", "South", "North"],
            "units": [10, 15, 20],
            "is_active": [True, False, True],
        }
    )

    result = analyze_dataframe(dataframe)

    assert result["summary_metrics"]["target_column"] == "units"
    assert result["summary_metrics"]["numeric_column_count"] == 1
    assert result["summary_metrics"]["target_total"] == 45.0
