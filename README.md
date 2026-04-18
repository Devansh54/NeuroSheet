# NeuroSheet AI

NeuroSheet AI is a Python-based project that transforms Excel files into cleaned datasets, summary analysis, human-readable insights, and safe future predictions through a modular workflow that will later power a Streamlit dashboard.

## Current Progress

- Phase 1 complete: project foundation
- Phase 2 complete: multi-file Excel loading pipeline
- Phase 3 complete: data cleaning and standardization
- Phase 4 complete: analysis engine
- Phase 5 complete: human-readable insight generation
- Phase 6 complete: linear regression prediction module
- Phase 7 onward: pending

## Implemented Features

### 1. Data Loading

- Reads `.xlsx` files from the `data/` folder
- Merges multiple files into one dataframe
- Skips invalid or empty Excel files when possible
- Preserves source file names in a `source_file` column
- Returns a load summary with file counts and detected columns

### 2. Data Cleaning

- Removes fully empty rows
- Standardizes column names into lowercase snake_case
- Trims text fields
- Normalizes blank-like values
- Converts numeric-looking text into numeric columns
- Converts likely date columns into datetime
- Removes duplicate rows
- Fills missing values with safe defaults
- Returns a cleaning summary

### 3. Analysis Engine

- Detects numeric, categorical, and date columns
- Chooses sensible default target/group/date columns
- Builds numeric summaries
- Creates grouped summaries
- Creates trend summaries when date data exists
- Identifies the top record for meaningful numeric targets

### 4. Insight Generation

- Produces plain-English insights from analysis output
- Works on numeric, categorical, and mixed datasets
- Avoids misleading insights for identifier-like numeric columns
- Highlights data quality issues such as many `Unknown` values

### 5. Prediction Module

- Uses linear regression for forecasting
- Supports date-based prediction when a date column exists
- Supports sequence-based prediction when no date column exists
- Refuses prediction when the target is unsuitable
- Blocks misleading prediction on identifier-like columns such as member IDs

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

## Current Sample Data

The project currently uses this sample workbook:

- [Members Employer Information.xlsx](C:\Users\Hp\Downloads\NeuroSheet\data\Members%20Employer%20Information.xlsx)

This file is useful for testing cleaning, grouping, and insight generation. It is not ideal for forecasting because the detected numeric field is an identifier-like member number, so prediction is intentionally skipped.

## Dependencies

Install the current dependencies with:

```bash
pip install -r requirements.txt
```

Current dependencies:

- `pandas`
- `openpyxl`
- `scikit-learn`

## How To Run The Current Backend Pipeline

Start Python from the project folder:

```bash
python
```

Then run:

```python
from src.data_loader import load_excel_folder
from src.data_cleaner import clean_dataframe
from src.analyzer import analyze_dataframe
from src.insights import generate_insights
from src.predictor import predict_trend

load_result = load_excel_folder("data")
clean_result = clean_dataframe(load_result["data"])
analysis = analyze_dataframe(clean_result["data"])
insights = generate_insights(clean_result["data"], analysis)
prediction = predict_trend(
    clean_result["data"],
    analysis["selected_columns"]["target_column"],
    analysis["selected_columns"]["date_column"],
)

print(load_result["summary"])
print(clean_result["summary"])
print(analysis["summary_metrics"])
print(insights)
print(prediction)
```

## Expected Result With Current Sample File

With the current member dataset, you should see:

- successful loading and cleaning
- grouped analysis on a useful categorical column such as `region`
- human-readable insights about dataset structure and dominant groups
- prediction skipped with a safe message because `member_customer_number` is treated as an identifier

## Testing Notes

The backend has already been verified against:

- the real member workbook in `data/`
- numeric/date-rich synthetic datasets
- text-only datasets
- too-few-data prediction cases
- identifier-like numeric columns

## Next Planned Work

The next phase is Phase 7:

- Streamlit dashboard UI
- user interaction flow
- data preview
- summary display
- chart integration
- premium frontend styling
