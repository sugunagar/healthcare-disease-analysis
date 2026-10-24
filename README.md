# Real-Time Healthcare Disease Analysis
A free, fully automated disease-surveillance project, a nightly ETL pipeline pulls
live public-health data from the CDC, cleans and validates it, loads it into
DuckDB/Parquet, and serves it in an interactive Streamlit dashboard.

**Cost: $0.** Every data source is a free public API with no key required.
Hosting is free too: GitHub Actions (public repo) for the pipeline and
Streamlit Community Cloud for the dashboard.
## Live Demo

Try the dashboard here: https://healthcare-disease-analysis-bysuguna.streamlit.app/

<img width="1200" height="800" alt="dashboard-screenshot" src="https://github.com/user-attachments/assets/d9eeb758-96ec-4165-87b5-040415c378c5" />



## What it tracks

| Dataset | Source | Update cadence | What it answers |
| --- | --- | --- | --- |
| Weekly Hospital Respiratory Admissions (NHSN) | CDC Socrata `vdzy-6i9v` | Weekly | How many new COVID-19, influenza, and RSV admissions per state, per week? |
| RESP-NET Hospitalization Rates | CDC Socrata `kvib-3txy` | Weekly | Which age groups are being hospitalized, and by which virus? |
| PLACES Chronic Disease Prevalence | CDC Socrata `cwsq-ngmh` | Annual release | Which counties have the highest diabetes, asthma, COPD, obesity, and stroke prevalence? |

## Project structure

```
healthcare-disease-analysis/
├── config.yaml                  # datasets, filters, measures — change here, not in code
├── pipeline/
│   ├── extract.py               # Socrata API client with pagination + retries
│   ├── transform.py             # cleaning, typing, derived metrics
│   ├── load.py                  # DuckDB load, Parquet export, data-quality report
│   └── run_pipeline.py          # orchestrator: extract -> transform -> load
├── dashboard/
│   ├── app.py                   # Streamlit dashboard (4 tabs)
│   └── data_loader.py           # reads processed Parquet, cached
├── data/                        # created by the pipeline (gitignored except summaries)
├── .github/workflows/daily-refresh.yml   # runs the pipeline every morning, free
├── docs/
│   ├── RESUME_BULLETS.md
│   └── INTERVIEW_TALKING_POINTS.md
└── requirements.txt
```

## Run it locally

```bash
python -m venv .venv && source .venv/bin/activate   # recommended, keeps deps isolated
pip install -r requirements.txt
python pipeline/run_pipeline.py        # pulls live CDC data -> data/processed/
streamlit run dashboard/app.py          # open the dashboard in your browser
```

## Automation (free)

- **GitHub Actions** (`.github/workflows/daily-refresh.yml`) runs the pipeline
  every day at 08:00 UTC and commits the refreshed Parquet files + a
  `data/processed/last_updated.json` freshness stamp.
- **Streamlit Community Cloud** redeploys automatically on every push, so the
  dashboard always shows the latest successful pipeline run.
- Locally, the same command works on any scheduler (`cron`, Task Scheduler):
  `0 8 * * * cd /path/to/project && python pipeline/run_pipeline.py`

## Data-quality checks

Every run writes `data/processed/dq_report.json` with row counts, date ranges,
null rates, and duplicate counts per table. The pipeline exits non-zero if a
source returns zero rows or a required column is missing — so a silent failure
can never ship stale data as "fresh".

## Skills this project demonstrates

Python, SQL (DuckDB), REST APIs, ETL/ELT, data cleaning, data-quality
validation, scheduling/automation, dashboarding (Streamlit + Plotly), and
GitHub Actions CI/CD — all on real, messy, real-world public-health data.

## Data notes & limitations

- CDC data is provisional and revised retroactively; week-over-week numbers can
  change as hospitals report late. The dashboard shows the data-as-of date on
  every tab.
- NHSN jurisdiction codes are US state abbreviations; national figures are the
  sum across states, computed in the pipeline.
- PLACES values are age-adjusted prevalence percentages from the latest release
  year present in the source.
- This is an analytics portfolio project, not medical advice and not a clinical
  tool.
