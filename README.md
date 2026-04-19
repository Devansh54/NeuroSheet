# NeuroSheet

NeuroSheet is a Python-based Excel analysis system that loads one or more Excel workbooks, cleans and standardizes the merged dataset, generates summary analysis and plain-English insights, produces simple forecasting when the data supports it, and presents the full workflow through an interactive Streamlit dashboard.

This project is built as a Python mini project with a strong focus on practical data processing, readable output, and a polished presentation layer.

## Project Objective

The objective of NeuroSheet is to simplify spreadsheet-based analysis for users who work with raw Excel files but may not have advanced technical or analytics expertise. The project is designed to take scattered workbook data, clean it into a consistent structure, extract useful summaries, generate readable insights, support simple forecasting, and present the full result in a professional dashboard that is easy to demonstrate and evaluate.

## What It Does

- Loads one or more `.xlsx` files from a folder or file upload
- Merges multiple workbooks into one dataset
- Tracks the origin of each row using a `source_file` column
- Standardizes raw column names into lowercase snake_case
- Converts likely numeric and date-like fields automatically
- Removes duplicate rows and fills missing values safely
- Detects useful default columns for analysis, grouping, and forecasting
- Generates summary metrics such as totals, averages, minimums, maximums, and counts
- Builds grouped analysis for columns such as region, category, type, or similar fields
- Generates plain-English insights from the cleaned dataset
- Runs linear-regression-based prediction when the dataset has enough usable structure
- Visualizes comparison, share, and trend patterns in the dashboard
- Exports cleaned data and a text report

## Key Features

### Data Ingestion

- Folder-based Excel loading
- Multi-file upload support in the dashboard
- Invalid or empty file handling
- Source file tracking

### Data Cleaning

- Column renaming and normalization
- Text cleanup and blank-value normalization
- Numeric conversion for columns that are mostly numeric
- Date conversion for columns that behave like dates
- Duplicate removal
- Missing-value filling with beginner-friendly defaults

### Analysis Engine

- Dataset size and schema summary
- Numeric column statistics
- Grouped breakdowns
- Top-record detection
- Timeline summary when a usable date column exists

### Insight Engine

- Human-readable dataset summary
- Group-wise insight generation
- Distribution and imbalance observations
- Trend commentary
- Data quality warnings for incomplete fields

### Prediction Module

- Linear regression forecasting with date-based prediction when a valid date column exists
- Sequential fallback prediction when date data is not available but a usable numeric series exists
- Safe unavailable-state messaging when forecasting would be misleading

### Dashboard

- Streamlit-based interactive interface
- Folder, Upload, and Showcase input modes
- Dark and light theme support
- Premium black-and-gold visual style
- Responsive cards, tables, and chart sections
- Export and download actions from the dashboard

## Project Structure

```text
NeuroSheet/
|-- app.py
|-- requirements.txt
|-- README.md
|-- .gitignore
|-- data/
|-- demo_assets/
|-- outputs/
|-- tests/
`-- src/
    |-- __init__.py
    |-- analyzer.py
    |-- data_cleaner.py
    |-- data_loader.py
    |-- exporter.py
    |-- insights.py
    |-- predictor.py
    `-- utils.py
```

## Core Modules

### `src/data_loader.py`

Responsible for reading Excel files from a local folder or dashboard uploads, validating them, skipping unusable files, merging valid files, and generating a load summary.

### `src/data_cleaner.py`

Responsible for cleaning the merged dataset by standardizing columns, normalizing text, converting numeric and date-like columns, removing duplicates, filling missing values, and producing a cleaning summary.

### `src/analyzer.py`

Responsible for summary analysis including row and column counts, numeric overview, grouped aggregation, timeline summaries, and top-record detection.

### `src/insights.py`

Responsible for turning raw analysis output into simple, readable insight statements suitable for dashboard display and project demonstration.

### `src/predictor.py`

Responsible for running linear-regression-based forecasting when the dataset contains enough structured information.

### `src/exporter.py`

Responsible for exporting the cleaned dataset to CSV and generating a plain-text report in the `outputs/` folder.

### `app.py`

Responsible for the Streamlit dashboard, input workflow, data preview, metrics display, visuals, insight section, prediction panel, and export actions.

## Technology Stack

- Python
- Pandas
- NumPy
- Scikit-learn
- OpenPyXL
- Streamlit
- Altair
- Pytest

## Expected Input

NeuroSheet works best when:

- input files are `.xlsx` workbooks
- files represent the same type of business or operational dataset
- columns are mostly similar across files
- at least one meaningful numeric column exists for stronger analysis
- a date column exists if timeline analysis and forecasting are required

The project can still operate with imperfect files, but richer structure produces better insights and more complete output.

## How To Run Locally

### 1. Install dependencies

```bash
pip install -r requirements.txt
```

### 2. Start the dashboard

```bash
streamlit run app.py
```

### 3. Use the workflow

1. Select `Folder`, `Upload`, or `Showcase` mode.
2. Provide Excel files or use the built-in showcase dataset.
3. Click `Analyze Data`.
4. Review the cleaned dataset, metrics, charts, insights, and prediction output.
5. Download the cleaned CSV or generated report.

## Dashboard Workflow

### Folder Mode

Use a folder that contains one or more `.xlsx` files. The project loads all valid Excel files in that folder and merges them.

### Upload Mode

Upload one or more Excel files directly into the dashboard for quick testing without changing the local data folder.

### Showcase Mode

Use showcase mode during demo or viva when you need to clearly demonstrate:

- grouped analysis
- timeline summary
- charts and trends
- forecasting behavior with a valid numeric target

This mode is useful because some real-world datasets may not contain the structure needed to show every feature clearly.

## Demo Screenshots

Add final screenshots here before submission or deployment sharing.

Suggested captures:

1. Hero section and input workflow
2. Processing summary, dataset preview, and executive metrics
3. Charts, insights, prediction, and export sections

Suggested captions:

- `Dashboard home with workbook ingestion workflow`
- `Cleaned dataset review with metrics and grouped analysis`
- `Visual analytics, forecasting, and export output`

## Output Produced

NeuroSheet can produce:

- a cleaned merged dataset
- summary metrics
- grouped analysis tables
- trend summaries
- plain-English insight statements
- prediction output with method, next label, predicted value, direction, and fit score
- downloadable CSV export
- downloadable text report

## Export Behavior

Two export paths are supported:

- Browser download from the dashboard
- File save into the local `outputs/` folder

For local use, both are valid. For deployed Streamlit apps, browser download should be treated as the main export path because server-side files are not guaranteed to persist permanently across sessions.

## Testing

The project includes automated tests for the core pipeline:

- data loading
- data cleaning
- analysis
- prediction
- export

Run the test suite with:

```bash
pytest -q
```

## Current Limitations

- Only `.xlsx` files are supported
- Forecasting depends on the presence of a meaningful numeric field
- Date-based trend analysis depends on a valid date column
- Forecast output is intentionally simple and uses linear regression only
- The project includes backend test coverage, but not automated browser-level UI testing

## Submission Notes

For project submission or viva, present NeuroSheet as:

**a Python-based Excel intelligence system with an interactive dashboard for analysis, insights, visualization, forecasting, and export**

That framing keeps the project centered on Python data processing and analysis rather than presenting it as only a UI exercise.

## Future Scope

Possible future improvements for NeuroSheet include:

- support for `.csv` and additional spreadsheet formats
- smarter column-matching across files with inconsistent schemas
- advanced forecasting models beyond linear regression
- user-controlled target, group, and date column selection for deeper analysis
- downloadable PDF or presentation-style reports
- authentication and persistent project history for multi-user scenarios
- automated UI testing for full dashboard validation

## Deployment

This project can be deployed using Streamlit Community Cloud.

Recommended deployment setup:

1. Push the final project to GitHub.
2. Open Streamlit Community Cloud.
3. Create a new app from the GitHub repository.
4. Select the main branch.
5. Use `app.py` as the entrypoint.
6. Deploy and verify the dashboard using Folder, Upload, and Showcase modes.

## Final Readiness Checklist

- `requirements.txt` is complete
- README matches the implemented project
- test suite passes
- dashboard runs locally
- exports work
- showcase mode demonstrates the full capability set
- real dataset and demo assets are kept separate for clarity
