"""Orchestrator: extract -> transform -> load for all three CDC datasets.

Usage:  python pipeline/run_pipeline.py
Exits non-zero if any source returns zero rows, so a broken source can never
silently ship stale data as fresh.
"""
import json
import logging
import os
import sys
from datetime import date

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import yaml

from pipeline.extract import fetch_socrata
from pipeline.load import load_all
from pipeline.transform import (transform_nhsn, transform_places,
                                transform_respnet)

logging.basicConfig(level=logging.INFO,
                    format="%(asctime)s %(levelname)s %(message)s")
logger = logging.getLogger(__name__)

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def main() -> None:
    with open(os.path.join(ROOT, "config.yaml")) as fh:
        cfg = yaml.safe_load(fh)
    base = cfg["socrata_base"]
    paths = cfg["paths"]
    processed_dir = os.path.join(ROOT, paths["processed_dir"])
    duckdb_file = os.path.join(ROOT, paths["duckdb_file"])

    tables = {}

    # 1. NHSN weekly respiratory admissions (COVID / flu / RSV by state).
    nhsn = cfg["datasets"]["nhsn_admissions"]
    raw = fetch_socrata(
        base, nhsn["id"],
        where=f"weekendingdate >= '{nhsn['min_date']}'",
        order="weekendingdate DESC")
    tables["nhsn_admissions"] = transform_nhsn(raw, nhsn)

    # 2. RESP-NET hospitalization rates by virus network and age group.
    resp = cfg["datasets"]["respnet_rates"]
    raw = fetch_socrata(base, resp["id"], order="date DESC")
    tables["respnet_rates"] = transform_respnet(raw, resp)

    # 3. PLACES chronic disease prevalence by county.
    places = cfg["datasets"]["places_chronic"]
    measures = ", ".join(f"'{m}'" for m in places["measures"])
    raw = fetch_socrata(
        base, places["id"],
        where=f"measureid in({measures})")
    tables["places_chronic"] = transform_places(raw, places)

    for name, df in tables.items():
        if df.empty:
            logger.error("Empty table after transform: %s — aborting", name)
            sys.exit(1)
        logger.info("%s: %s rows", name, len(df))

    report = load_all(tables, processed_dir, duckdb_file)
    with open(os.path.join(processed_dir, "last_updated.json"), "w") as fh:
        json.dump({"last_run": str(date.today()),
                   "tables": {k: v["rows"] for k, v in report.items()}},
                  fh, indent=2)
    logger.info("Pipeline complete. DQ report: %s", report)


if __name__ == "__main__":
    main()
