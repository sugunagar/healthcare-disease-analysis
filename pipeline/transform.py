"""Transform layer: cleaning, typing, and derived metrics.

Each function is pure (DataFrame in -> DataFrame out) so it can be unit-tested
without touching the network.
"""
import pandas as pd


def _to_numeric(df: pd.DataFrame, cols: list[str]) -> pd.DataFrame:
    for col in cols:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")
    return df


def transform_nhsn(df: pd.DataFrame, cfg: dict) -> pd.DataFrame:
    """Long-format admissions: one row per state x week x disease."""
    if df.empty:
        return df
    rate_cols = list(cfg["diseases"].values())
    count_cols = list(cfg["count_columns"].values())
    df = _to_numeric(df.copy(), rate_cols + count_cols)
    df["weekendingdate"] = pd.to_datetime(df["weekendingdate"], errors="coerce")
    df = df.dropna(subset=["weekendingdate", "jurisdiction"])

    long_frames = []
    for disease, rate_col in cfg["diseases"].items():
        count_col = cfg["count_columns"][disease]
        part = df[["jurisdiction", "weekendingdate", rate_col, count_col]].copy()
        part.columns = ["state", "week_ending", "admissions_per_100k", "admissions"]
        part["disease"] = disease
        long_frames.append(part)
    out = pd.concat(long_frames, ignore_index=True)
    out = out.dropna(subset=["admissions_per_100k"])
    # National total per week x disease (sum across states).
    national = (out.groupby(["week_ending", "disease"], as_index=False)
                  .agg(admissions=("admissions", "sum")))
    national["state"] = "US"
    national["admissions_per_100k"] = None  # rates do not sum; keep counts only
    out = pd.concat([out, national], ignore_index=True)
    return out.sort_values(["disease", "state", "week_ending"])


def transform_respnet(df: pd.DataFrame, cfg: dict) -> pd.DataFrame:
    """Hospitalization rates by virus network, age group, and week."""
    if df.empty:
        return df
    df = df.copy()
    df["estimate"] = pd.to_numeric(df["estimate"], errors="coerce")
    df["date"] = pd.to_datetime(df["date"], errors="coerce")
    df = df.dropna(subset=["date", "estimate"])
    if "surveillance_network" in df.columns and cfg.get("networks"):
        df = df[df["surveillance_network"].isin(cfg["networks"])]
    # Keep the headline series only: national, all races/sexes, weekly,
    # age-adjusted rates — the demographic breakdowns stay in the raw source.
    # Age groups are kept (the dashboard compares them); everything else is
    # pinned to the headline series: national, all races/sexes, weekly rates.
    canonical = [("race", "All"), ("sex", "All"), ("state", "Overall"),
                 ("data_type", "Weekly Rate")]
    for col, label in canonical:
        if col in df.columns and label in set(df[col].unique()):
            df = df[df[col] == label]
    return df.sort_values(["surveillance_network", "date"])


def transform_places(df: pd.DataFrame, cfg: dict) -> pd.DataFrame:
    """Chronic-disease prevalence by county, latest release year only.

    The source is census-tract level, so tracts are rolled up to counties
    with a population-weighted mean — county prevalence is not a simple
    average of tract percentages.
    """
    if df.empty:
        return df
    df = df.copy()
    df["data_value"] = pd.to_numeric(df["data_value"], errors="coerce")
    df = df.dropna(subset=["data_value", "countyname", "measureid"])
    if "year" in df.columns:
        latest_year = df["year"].max()
        df = df[df["year"] == latest_year]
    if cfg.get("value_type") and "data_value_type" in df.columns:
        typed = df[df["data_value_type"] == cfg["value_type"]]
        if not typed.empty:
            df = typed
    df["disease"] = df["measureid"].map(cfg["measures"]).fillna(df["measure"])
    df = df.rename(columns={"statedesc": "state", "countyname": "county",
                            "data_value": "prevalence_pct"})
    keys = ["state", "stateabbr", "county", "countyfips", "measureid",
            "disease", "year"]
    if "totalpopulation" in df.columns:
        df["totalpopulation"] = pd.to_numeric(df["totalpopulation"],
                                              errors="coerce").fillna(0)
        df["weighted"] = df["prevalence_pct"] * df["totalpopulation"]
        agg = (df.groupby(keys, as_index=False)
                 .agg(prevalence_pct=("weighted", "sum"),
                      totalpopulation=("totalpopulation", "sum")))
        agg["prevalence_pct"] = agg["prevalence_pct"] / agg["totalpopulation"]
        out = agg.drop(columns=["totalpopulation"])
    else:
        out = df.groupby(keys, as_index=False)["prevalence_pct"].mean()
    return out.sort_values(["disease", "prevalence_pct"],
                           ascending=[True, False])
