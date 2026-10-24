"""Dashboard data access: reads the processed Parquet files the pipeline writes."""
import json
import os

import pandas as pd

PROCESSED = os.path.join(os.path.dirname(os.path.dirname(
    os.path.abspath(__file__))), "data", "processed")


def load_table(name: str) -> pd.DataFrame:
    path = os.path.join(PROCESSED, f"{name}.parquet")
    if not os.path.exists(path):
        return pd.DataFrame()
    df = pd.read_parquet(path)
    for col in ("week_ending", "date"):
        if col in df.columns:
            df[col] = pd.to_datetime(df[col])
    return df


def last_updated() -> dict:
    path = os.path.join(PROCESSED, "last_updated.json")
    if os.path.exists(path):
        with open(path) as fh:
            return json.load(fh)
    return {}
