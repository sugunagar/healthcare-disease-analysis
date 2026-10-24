"""Extract layer: Socrata (CDC Open Data) API client.

Free, no API key required. Handles pagination, retries with backoff, and
returns a pandas DataFrame per dataset.
"""
import logging
import time

import pandas as pd
import requests

logger = logging.getLogger(__name__)

PAGE_SIZE = 50_000
MAX_RETRIES = 4


def fetch_socrata(base: str, dataset_id: str, where: str | None = None,
                  order: str | None = None, limit: int | None = None) -> pd.DataFrame:
    """Fetch all rows of a Socrata dataset (paginated)."""
    url = f"{base}/{dataset_id}.json"
    frames, offset = [], 0
    session = requests.Session()
    session.headers.update({"User-Agent": "healthcare-disease-analysis/1.0"})

    while True:
        params = {"$limit": PAGE_SIZE, "$offset": offset}
        if where:
            params["$where"] = where
        if order:
            params["$order"] = order
        if limit is not None:
            params["$limit"] = min(PAGE_SIZE, limit - offset)

        last_error = None
        for attempt in range(MAX_RETRIES):
            try:
                resp = session.get(url, params=params, timeout=60)
                resp.raise_for_status()
                rows = resp.json()
                break
            except (requests.RequestException, ValueError) as exc:
                last_error = exc
                wait = 2 ** attempt
                logger.warning("Fetch failed (attempt %s/%s): %s — retrying in %ss",
                               attempt + 1, MAX_RETRIES, exc, wait)
                time.sleep(wait)
        else:
            raise RuntimeError(f"Socrata fetch failed for {dataset_id}: {last_error}")

        if not rows:
            break
        frames.append(pd.DataFrame(rows))
        offset += len(rows)
        logger.info("%s: fetched %s rows so far", dataset_id, offset)
        if limit is not None and offset >= limit:
            break
        if len(rows) < PAGE_SIZE:
            break

    if not frames:
        return pd.DataFrame()
    return pd.concat(frames, ignore_index=True)
