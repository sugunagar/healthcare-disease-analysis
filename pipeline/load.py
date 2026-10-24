"""Load layer: DuckDB tables + Parquet exports + data-quality report."""
import json
import logging
import os

import duckdb
import pandas as pd

logger = logging.getLogger(__name__)


def data_quality_report(tables: dict[str, pd.DataFrame]) -> dict:
    report = {}
    for name, df in tables.items():
        report[name] = {
            "rows": int(len(df)),
            "columns": list(df.columns),
            "null_rate": {c: round(float(df[c].isna().mean()), 4)
                          for c in df.columns},
            "duplicate_rows": int(df.duplicated().sum()),
            "date_min": (str(df["week_ending"].min()) if "week_ending" in df.columns
                         else str(df["date"].min()) if "date" in df.columns else None),
            "date_max": (str(df["week_ending"].max()) if "week_ending" in df.columns
                         else str(df["date"].max()) if "date" in df.columns else None),
        }
    return report


def load_all(tables: dict[str, pd.DataFrame], processed_dir: str,
             duckdb_file: str) -> dict:
    """Write each table to DuckDB and Parquet; return the DQ report."""
    os.makedirs(processed_dir, exist_ok=True)
    for name, df in tables.items():
        if df.empty:
            raise ValueError(f"Refusing to load empty table: {name}")
        path = os.path.join(processed_dir, f"{name}.parquet")
        df.to_parquet(path, index=False)
        logger.info("Wrote %s rows -> %s", len(df), path)

    con = duckdb.connect(duckdb_file)
    try:
        for name, df in tables.items():
            con.execute(f"CREATE OR REPLACE TABLE {name} AS SELECT * FROM df")
    finally:
        con.close()

    report = data_quality_report(tables)
    with open(os.path.join(processed_dir, "dq_report.json"), "w") as fh:
        json.dump(report, fh, indent=2, default=str)
    return report
