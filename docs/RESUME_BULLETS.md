# Resume bullets for this project

Pick one or two, and adjust the numbers after your first successful run:

- Built an automated disease-surveillance pipeline in Python that pulls live
  CDC data (NHSN hospital admissions, RESP-NET hospitalization rates, PLACES
  county chronic-disease prevalence), validates it with data-quality checks,
  and loads it into DuckDB/Parquet on a daily GitHub Actions schedule.
- Developed an interactive Streamlit + Plotly dashboard tracking COVID-19,
  influenza, and RSV admissions across all US states and chronic-disease
  prevalence across 3,000+ counties, with trend, state-comparison, and
  age-group views.
- Engineered a paginated Socrata API client with retry/backoff, schema
  normalization, and long-format reshaping of weekly surveillance data,
  replacing manual spreadsheet pulls with a fully reproducible pipeline.

## How to talk about it in one line

"I built a free, end-to-end healthcare analytics project that automatically
refreshes real CDC disease data every day and serves it in a dashboard —
the same extract, transform, load, and visualization workflow I use at work."
