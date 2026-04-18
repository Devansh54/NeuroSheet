# NeuroSheet AI

NeuroSheet AI is a Python-based project that will transform multiple Excel files into meaningful insights, visual analytics, and future predictions through an interactive dashboard.

## Current Status

- Phase 1 complete: project foundation finalized
- Phase 2 complete: multi-file Excel data pipeline implemented
- Phase 3 onward: pending

## Finalized Project Scope

The complete project will include:

- Multi-file Excel reading
- Data merge and cleaning
- Summary analysis
- Human-readable insight generation
- Future prediction using linear regression
- Streamlit dashboard
- Visual charts
- Exportable outputs

## Expected Excel Format

The project currently assumes:

- Input files are `.xlsx` Excel files
- Files should represent the same type of dataset
- Same columns across files are preferred
- Small column differences are allowed during merge
- At least one numeric column should exist for meaningful analysis later
- A date column is optional
- Column names may vary in spacing/case and will be standardized in Phase 3
- The pipeline adds a `source_file` column automatically

## Frozen Project Structure

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

## Phase 2 Features Implemented

- Reads all `.xlsx` files from a folder
- Skips temporary Excel lock files like `~$file.xlsx`
- Validates missing folder and empty folder cases
- Skips broken or empty files while continuing with valid ones
- Merges all valid files into one raw dataframe
- Preserves the source file name in a `source_file` column
- Returns a load summary with file counts, skipped files, row totals, and detected columns
- Includes a second loader for uploaded files to support later Streamlit integration

## How To Test Phase 2

### 1. Create sample test files

Put 2 or more `.xlsx` files inside the `data/` folder.
Example columns:

- `Date`
- `Category`
- `Product`
- `Sales`

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Run a quick manual test in Python

```bash
python
```

Then run:

```python
from src.data_loader import load_excel_folder

result = load_excel_folder("data")
print(result["summary"])
print(result["data"].head())
```

### 4. Test these cases

- valid folder with 2 or more `.xlsx` files
- folder path that does not exist
- folder with no `.xlsx` files
- one valid file plus one empty/broken file
- files with slightly different columns

### 5. Expected success result

You should get:

- one merged dataframe
- a `source_file` column
- summary containing files found, files loaded, skipped files, total rows loaded, detected columns

## Merge Workflow From Now On

You asked to work directly on `main` from now on.
Recommended flow for each phase:

1. Implement the phase on `main`
2. Test the phase locally
3. Commit changes clearly
4. Push `main` to GitHub
5. Start the next phase on the same branch

## Current Commit Direction

Phase 2 should use a commit message like:

```text
feat: add multi-file excel loading pipeline
```
