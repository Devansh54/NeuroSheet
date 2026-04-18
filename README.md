# NeuroSheet AI

NeuroSheet AI is a Python-based project that will transform multiple Excel files into meaningful insights, visual analytics, and future predictions through an interactive dashboard.

## Phase 1 Status

This repository is currently initialized with the project foundation only.
No feature implementation has been added yet.

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

The project will assume the following:

- Input files will be `.xlsx` Excel files
- Files should represent the same type of dataset
- Same columns across files are preferred
- Small column differences are acceptable during merge
- At least one numeric column should exist for meaningful analysis
- A date column is optional
- Column names may vary in spacing/case and will be standardized later
- Source file name tracking will be preserved during merge

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

## Module List

- `app.py`: Streamlit dashboard entry point
- `src/data_loader.py`: Excel loading and merging
- `src/data_cleaner.py`: cleaning and standardization
- `src/analyzer.py`: summary calculations and grouping
- `src/insights.py`: human-readable insight generation
- `src/predictor.py`: prediction logic
- `src/utils.py`: shared helper functions

## Git Workflow

- Stable branch: `main`
- Phase 1 to Phase 5 working branch: `feature/phase1-phase5-backend`
- Phase 6 to Phase 10 working branch: `feature/phase6-phase10-frontend`
- Merge tested work into `main`
- Use clear commit names such as `feat:` `chore:` and `docs:`

## Phase Split

### Phase 1 to Phase 5

- Project foundation
- Data pipeline
- Data cleaning
- Analysis engine
- Insight engine

### Phase 6 to Phase 10

- Prediction module
- Dashboard UI/UX
- Visualizations
- Export/reporting
- Testing and polish

## Setup Notes

The repository structure is initialized now so development can begin in later phases.
Actual implementation will be added after the foundation phase.
