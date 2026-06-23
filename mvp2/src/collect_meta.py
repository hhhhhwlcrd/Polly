"""
mvp2 supplementary collection: per-market metadata needed for *realistic* copying.

mvp1 already gathered trades + resolutions. For mvp2 we additionally need, per market:
  - fee category  -> taker fee = size * feeRate * p * (1-p)  (makers pay 0)
  - neg_risk flag -> a token-for-token copier can misread neg-risk convert/arb
  - tags / slug   -> human context

Historical order books and price history are NOT retrievable for resolved markets
(`/prices-history` returns []), so the realistic-fill model reconstructs the
post-latency price from our own dense trade tape (see src/fills.py) rather than
from book snapshots. This collector only adds the fee/neg-risk metadata.
"""
from __future__ import annotations
import time
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed

import requests
import pandas as pd

MVP1 = Path(__file__).resolve().parents[2] / "mvp1" / "data"
OUT = Path(__file__).resolve().parents[1] / "data"
OUT.mkdir(exist_ok=True)
CLOB = "https://clob.polymarket.com/markets"

session = requests.Session()
session.headers.update({"User-Agent": "polly-mvp2/1.0"})

# Polymarket taker fee rate by category (fraction; makers pay 0).
# fee = shares * feeRate * p * (1-p). Source: docs.polymarket.com/trading/fees (early 2026).
FEE_BY_CATEGORY = {
    "Crypto": 0.07, "Sports": 0.03, "Politics": 0.04, "Finance": 0.04,
    "Tech": 0.04, "Mentions": 0.04, "Economics": 0.05, "Culture": 0.05,
    "Weather": 0.05, "Geopolitics": 0.0, "Other": 0.05,
}
# Map common CLOB tags -> our fee category bucket.
TAG_TO_CAT = {
    "crypto": "Crypto", "bitcoin": "Crypto", "ethereum": "Crypto",
    "sports": "Sports", "nba": "Sports", "nfl": "Sports", "soccer": "Sports",
    "epl": "Sports", "mlb": "Sports", "ufc": "Sports", "tennis": "Sports",
    "politics": "Politics", "elections": "Politics", "us election": "Politics",
    "geopolitics": "Geopolitics", "war": "Geopolitics",
    "economics": "Economics", "fed": "Economics", "inflation": "Economics",
    "finance": "Finance", "stocks": "Finance",
    "tech": "Tech", "ai": "Tech",
    "pop culture": "Culture", "entertainment": "Culture", "movies": "Culture",
    "weather": "Weather",
}


def categorize(tags) -> str:
    if not tags:
        return "Other"
    low = [str(t).lower() for t in tags]
    for t in low:
        if t in TAG_TO_CAT:
            return TAG_TO_CAT[t]
    # loose contains-match
    for t in low:
        for key, cat in TAG_TO_CAT.items():
            if key in t:
                return cat
    return "Other"


def _get(url, tries=4):
    for i in range(tries):
        try:
            r = session.get(url, timeout=30)
            if r.status_code == 200:
                return r.json()
            if r.status_code in (429, 500, 502, 503):
                time.sleep(1.2 * (i + 1)); continue
            return None
        except requests.RequestException:
            time.sleep(1.2 * (i + 1))
    return None


def fetch_meta(cid: str) -> dict | None:
    m = _get(f"{CLOB}/{cid}")
    if not m:
        return None
    tags = m.get("tags") or []
    cat = categorize(tags)
    return {"conditionId": cid, "neg_risk": bool(m.get("neg_risk")),
            "category": cat, "fee_rate": FEE_BY_CATEGORY.get(cat, 0.05),
            "slug": m.get("market_slug"),
            "min_tick": m.get("minimum_tick_size"),
            "min_order_size": m.get("minimum_order_size")}


def main():
    trades = pd.read_parquet(MVP1 / "trades.parquet")
    res = pd.read_parquet(MVP1 / "resolutions.parquet")
    res = res.dropna(subset=["conditionId"])
    closed = set(res.loc[res["closed"] == True, "conditionId"])
    buys = trades[(trades["side"] == "BUY")]
    cids = sorted(set(buys["conditionId"].astype(str)) & set(map(str, closed)))
    print(f"markets needing meta: {len(cids)}", flush=True)

    rows = []
    with ThreadPoolExecutor(max_workers=12) as ex:
        futs = {ex.submit(fetch_meta, c): c for c in cids}
        for i, f in enumerate(as_completed(futs), 1):
            r = f.result()
            if r:
                rows.append(r)
            if i % 200 == 0:
                print(f"  {i}/{len(cids)}", flush=True)
    df = pd.DataFrame(rows)
    df.to_parquet(OUT / "market_meta.parquet", index=False)
    print("category counts:\n", df["category"].value_counts().to_string(), flush=True)
    print(f"neg_risk markets: {int(df['neg_risk'].sum())}/{len(df)}", flush=True)
    print("DONE", flush=True)


if __name__ == "__main__":
    main()
