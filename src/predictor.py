"""Utilities for simple future prediction using linear regression."""

from __future__ import annotations

from typing import Any

import numpy as np
import pandas as pd
from sklearn.linear_model import LinearRegression

from src.utils import choose_default_columns, detect_column_types, is_identifier_like


class PredictionError(Exception):
    """Raised when prediction inputs are invalid or unusable."""


def _build_unavailable(reason: str) -> dict[str, Any]:
    """Return a consistent unavailable-prediction payload."""
    return {
        "available": False,
        "reason": reason,
        "method": "Linear Regression",
        "historical_points": 0,
        "prediction_basis": None,
        "predicted_value": None,
        "next_label": None,
        "direction": None,
        "r2_score": None,
        "historical_data": pd.DataFrame(),
    }


def _fit_linear_regression(x_values: np.ndarray, y_values: np.ndarray) -> tuple[LinearRegression, float]:
    """Fit a simple linear regression model and return the model and fit score."""
    model = LinearRegression()
    model.fit(x_values, y_values)
    r2_score = float(model.score(x_values, y_values))
    return model, r2_score


def _predict_from_dates(
    dataframe: pd.DataFrame,
    target_column: str,
    date_column: str,
    periods_ahead: int,
) -> dict[str, Any]:
    """Predict the next value when a real date column is available."""
    trend_frame = dataframe[[date_column, target_column]].dropna().copy()
    if trend_frame.empty:
        return _build_unavailable("The selected date and target columns do not contain usable values.")

    trend_frame = (
        trend_frame.groupby(date_column)[target_column]
        .agg(total_value="sum", average_value="mean", record_count="count")
        .reset_index()
        .sort_values(date_column)
    )

    if len(trend_frame) < 3:
        return _build_unavailable("At least 3 dated points are needed for prediction.")

    day_offsets = (trend_frame[date_column] - trend_frame[date_column].min()).dt.days.astype(float)
    x_values = day_offsets.to_numpy().reshape(-1, 1)
    y_values = trend_frame["total_value"].to_numpy(dtype=float)

    model, r2_score = _fit_linear_regression(x_values, y_values)

    unique_offsets = sorted(day_offsets.unique().tolist())
    if len(unique_offsets) >= 2:
        steps = [curr - prev for prev, curr in zip(unique_offsets, unique_offsets[1:]) if curr - prev > 0]
        step_size = float(np.median(steps)) if steps else 1.0
    else:
        step_size = 1.0

    next_offset = float(day_offsets.iloc[-1] + step_size * periods_ahead)
    predicted_value = float(model.predict(np.array([[next_offset]]))[0])
    next_date = trend_frame[date_column].max() + pd.to_timedelta(step_size * periods_ahead, unit="D")

    last_observed = y_values[-1]
    if predicted_value > last_observed:
        direction = "growth"
    elif predicted_value < last_observed:
        direction = "decline"
    else:
        direction = "stable"

    return {
        "available": True,
        "reason": None,
        "method": "Linear Regression",
        "historical_points": int(len(trend_frame)),
        "prediction_basis": "date",
        "predicted_value": round(predicted_value, 2),
        "next_label": next_date.strftime("%Y-%m-%d"),
        "direction": direction,
        "r2_score": round(r2_score, 3),
        "historical_data": trend_frame,
    }


def _predict_from_sequence(
    dataframe: pd.DataFrame,
    target_column: str,
    periods_ahead: int,
) -> dict[str, Any]:
    """Predict the next value using row order when no date column is available."""
    series = dataframe[target_column].dropna().astype(float).reset_index(drop=True)
    if len(series) < 3:
        return _build_unavailable("At least 3 numeric values are needed for prediction.")

    x_values = np.arange(len(series), dtype=float).reshape(-1, 1)
    y_values = series.to_numpy(dtype=float)
    model, r2_score = _fit_linear_regression(x_values, y_values)

    next_index = float(len(series) - 1 + periods_ahead)
    predicted_value = float(model.predict(np.array([[next_index]]))[0])
    historical_data = pd.DataFrame(
        {
            "period": np.arange(1, len(series) + 1),
            target_column: series,
        }
    )

    last_observed = y_values[-1]
    if predicted_value > last_observed:
        direction = "growth"
    elif predicted_value < last_observed:
        direction = "decline"
    else:
        direction = "stable"

    return {
        "available": True,
        "reason": None,
        "method": "Linear Regression",
        "historical_points": int(len(series)),
        "prediction_basis": "sequence",
        "predicted_value": round(predicted_value, 2),
        "next_label": f"Period {int(next_index + 1)}",
        "direction": direction,
        "r2_score": round(r2_score, 3),
        "historical_data": historical_data,
    }


def predict_trend(
    dataframe: pd.DataFrame,
    target_column: str | None = None,
    date_column: str | None = None,
    periods_ahead: int = 1,
) -> dict[str, Any]:
    """Predict a future value from the cleaned dataset when the structure is suitable."""
    if dataframe.empty:
        raise PredictionError("The cleaned dataset is empty and cannot be used for prediction.")
    if periods_ahead < 1:
        raise PredictionError("periods_ahead must be at least 1.")

    column_types = detect_column_types(dataframe)
    defaults = choose_default_columns(dataframe)

    if target_column not in column_types["numeric"]:
        target_column = defaults["target_column"]
    if date_column not in column_types["date"]:
        date_column = defaults["date_column"]

    if not target_column:
        return _build_unavailable("No suitable numeric target column is available for prediction.")
    if is_identifier_like(target_column):
        return _build_unavailable(
            f"The column '{target_column}' looks like an identifier, so prediction is skipped to avoid misleading results."
        )

    if date_column:
        return _predict_from_dates(dataframe, target_column, date_column, periods_ahead)

    return _predict_from_sequence(dataframe, target_column, periods_ahead)
