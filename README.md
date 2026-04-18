# NeuroSheet AI

NeuroSheet AI is a Python-based Excel analysis project that converts raw workbooks into a cleaned dataset, summary metrics, readable insights, simple forecasting output, and an interactive dashboard for demonstration.

## Project Snapshot

NeuroSheet is designed to help a user:

- load one or more Excel files
- merge and clean the dataset
- inspect high-level analysis results
- read plain-English findings
- view grouped and trend-oriented summaries
- generate a basic forecast when the data structure supports it
- export the cleaned dataset and a summary report

## Current Implementation Status

- Phase 1 complete: project scope, structure, and workflow finalized
- Phase 2 complete: Excel ingestion and merge pipeline implemented
- Phase 3 complete: cleaning and standardization pipeline implemented
- Phase 4 complete: analysis engine implemented
- Phase 5 complete: human-readable insight generation implemented
- Phase 6 complete: linear regression forecasting module implemented
- Phase 7 complete: interactive Streamlit dashboard implemented
- Phase 8 in progress through UI/chart refinement

## Core Features

- Multi-file Excel loading from folder path or uploads
- Source file tracking through a `source_file` column
- Column normalization and data cleaning
- Duplicate removal and missing-value handling
- Numeric and date-like column detection
- Summary analysis and grouped breakdowns
- Plain-English insight generation
- Forecast readiness and prediction support
- Interactive black-and-gold dashboard with dark and light appearance modes
- CSV and text report download actions

## Expected Input Format

NeuroSheet currently assumes:

- input files are `.xlsx` workbooks
- files represent the same type of dataset
- identical columns are preferred, but minor variation is tolerated
- at least one meaningful numeric business field is needed for strong analysis
- a date column is optional, but recommended for trend analysis and forecasting
- column names may vary in spacing or case and are standardized during cleaning

## Project Structure

```text
NeuroSheet/
|-- app.py
|-- requirements.txt
|-- README.md
|-- .gitignore
|-- data/
|-- outputs/
`-- src/
    |-- __init__.py
    |-- data_loader.py
    |-- data_cleaner.py
    |-- analyzer.py
    |-- insights.py
    |-- predictor.py
    `-- utils.py
```

## Verified Modules

### Data Loading

Implemented in `src/data_loader.py`:

- loads `.xlsx` files from a folder
- supports uploaded files for the dashboard
- skips temporary Excel lock files
- merges valid data into one dataframe
- returns load summary and skipped-file reasons

### Data Cleaning

Implemented in `src/data_cleaner.py`:

- standardizes column names
- normalizes text values
- converts likely numeric and date columns
- removes duplicate rows
- fills missing values with safe defaults
- returns a cleaning summary

### Analysis

Implemented in `src/analyzer.py`:

- row and column counts
- numeric overview
- grouped summary
- top-record detection
- trend summary when date data exists

### Insights

Implemented in `src/insights.py`:

- dataset shape summary
- grouped-result explanation
- trend observation
- data quality flags
- human-readable finding generation

### Forecasting

Implemented in `src/predictor.py`:

- date-based linear regression forecasting
- sequential fallback forecasting
- unavailable-state handling when the dataset is not forecast-ready

### Dashboard

Implemented in `app.py`:

- folder and upload input flow
- dark/light appearance control
- preview tables
- processing summary cards
- grouped and trend visual sections
- findings and forecast panels
- export/download controls

## How To Run

### 1. Install dependencies

```bash
pip install -r requirements.txt
```

### 2. Start the dashboard

```bash
streamlit run app.py
```

### 3. Use the workflow

1. Choose `Folder` mode or `Upload` mode.
2. Provide one or more Excel files.
3. Click `Analyze Data`.
4. Review the cleaned dataset, metrics, findings, and forecast section.
5. Download the cleaned CSV or summary report.

## Manual Backend Check

Open Python and run:

```python
from src.data_loader import load_excel_folder
from src.data_cleaner import clean_dataframe
from src.analyzer import analyze_dataframe
from src.insights import generate_insights
from src.predictor import predict_trend

load_result = load_excel_folder("data")
clean_result = clean_dataframe(load_result["data"])
analysis_result = analyze_dataframe(clean_result["data"])
insight_result = generate_insights(clean_result["data"], analysis_result)
prediction_result = predict_trend(clean_result["data"])

print(load_result["summary"])
print(clean_result["summary"])
print(analysis_result["summary_metrics"])
print(insight_result)
print(prediction_result)
```

## Dashboard Review Checklist

When reviewing the UI, verify the following:

- the page loads without layout breakage
- dark mode and light mode both remain readable
- folder mode works with the `data/` folder
- upload mode accepts `.xlsx` files
- preview tables show toolbar actions
- grouped analysis and trend sections render correctly
- forecast output appears when the dataset supports it, or shows guidance when it does not
- download buttons return the cleaned CSV and text report

## Current Constraints

- only `.xlsx` files are supported
- forecast quality depends entirely on the quality of the input columns
- a dataset without a meaningful numeric business metric will not produce a forecast
- a dataset without a date field will not produce timeline forecasting
- dedicated export/report modules and automated tests are still pending

## Presentation Positioning

For submission or viva, present NeuroSheet as:

**a Python-based Excel intelligence system with an interactive dashboard for analysis, insights, and forecasting**

This keeps the project centered on Python data processing rather than presenting it as only a UI project.
