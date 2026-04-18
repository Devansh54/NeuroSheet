import pandas as pd

from src.predictor import predict_trend


def test_predict_trend_uses_date_based_forecast_when_possible() -> None:
    dataframe = pd.DataFrame(
        {
            "date": pd.to_datetime(["2024-01-01", "2024-02-01", "2024-03-01", "2024-04-01"]),
            "sales": [100, 120, 140, 170],
        }
    )

    result = predict_trend(dataframe, target_column="sales", date_column="date")

    assert result["available"] is True
    assert result["prediction_basis"] == "date"
    assert result["predicted_value"] is not None


def test_predict_trend_blocks_identifier_like_columns() -> None:
    dataframe = pd.DataFrame({"member_customer_number": [1001, 1002, 1003, 1004]})

    result = predict_trend(dataframe, target_column="member_customer_number")

    assert result["available"] is False
    assert "identifier" in result["reason"]
