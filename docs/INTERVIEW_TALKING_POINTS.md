# Interview talking points

## Why this project
Healthcare data is messy, provisional, and constantly revised — a realistic
test of ETL and dashboard skills. I wanted a project that proves I can work
with live data, not a one-time Kaggle download.

## Architecture
1. **Extract** — a Socrata API client paginates CDC datasets and retries with
   exponential backoff, so transient API failures do not break the run.
2. **Transform** — weekly admissions are reshaped from wide to long format
   (one row per state x week x disease), types are enforced, and a national
   aggregate is computed by summing states.
3. **Load** — DuckDB tables plus Parquet exports, with a data-quality report
   (row counts, null rates, duplicates, date ranges) on every run.
4. **Serve** — a Streamlit dashboard reads the Parquet files; GitHub Actions
   refreshes the data daily and Streamlit Cloud redeploys on push.

## Decisions worth mentioning
- **CDC Socrata instead of paid APIs**: free, no key, and the same data
  hospitals and researchers use — but it requires handling provisional
  revisions and late reporting, which I surface with a data-as-of stamp.
- **Parquet + DuckDB**: columnar storage keeps the dashboard fast even with
  hundreds of thousands of rows, and DuckDB lets me run SQL analytics over
  the same files.
- **Fail-loud pipeline**: the run exits non-zero on empty results, so a
  broken source can never silently ship stale data as fresh.

## If asked "what would you improve?"
- Add anomaly alerts (e.g., a state whose admissions jump 50% week over week).
- Add a forecast tab (simple time-series model) for the next 4 weeks.
- Cache the dashboard data in Streamlit so repeat visits load instantly.
