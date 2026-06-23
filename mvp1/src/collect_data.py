"""
Polly — Polymarket copy-trading analytics: data collection.

Pulls three things from Polymarket's public APIs and writes them to ./data:

  1. traders.csv        — the "top 100 performing" cohort (union across
                          leaderboard windows, since each window caps at 50).
  2. trades.parquet     — every BUY/SELL trade (TRADE activity) for those
                          wallets, capped per trader for tractability.
  3. resolutions.parquet— per-market settlement (winning token, payout) so we
                          can value a copied bet held to resolution.

All endpoints are public and unauthenticated:
  - lb-api.polymarket.com/{profit,volume}   leaderboards (max 50/window)
  - data-api.polymarket.com/activity        trade history per wallet
  - clob.polymarket.com/markets/<cid>       market resolution (token winner)
"""
from __future__ import annotations
import json, time, sys
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

import requests
import pandas as pd

DATA = Path(__file__).resolve().parent.parent / "data"
DATA.mkdir(exist_ok=True)

LB = "https://lb-api.polymarket.com"
ACT = "https://data-api.polymarket.com/activity"
CLOB = "https://clob.polymarket.com/markets"

# Tunables ------------------------------------------------------------------
TARGET_TRADERS = 100      # size of the top-performer cohort
MAX_TRADES_PER_TRADER = 1000   # most-recent TRADE records per wallet
PAGE = 500                # activity page size
N_WORKERS = 12            # concurrency for trade + resolution fetches

session = requests.Session()
session.headers.update({"User-Agent": "polly-copytrading-research/1.0"})


def _get(url, params=None, tries=4):
    for i in range(tries):
        try:
            r = session.get(url, params=params, timeout=30)
            if r.status_code == 200:
                return r.json()
            if r.status_code in (429, 500, 502, 503):
                time.sleep(1.5 * (i + 1))
                continue
            return None
        except requests.RequestException:
            time.sleep(1.5 * (i + 1))
    return None


# 1. Top-performer cohort ----------------------------------------------------
def build_cohort() -> pd.DataFrame:
    """Union of top performers across profit windows + volume (each capped 50)."""
    rows = {}
    sources = [("profit", "all"), ("profit", "30d"), ("profit", "7d"),
               ("profit", "1d"), ("volume", "all"), ("volume", "30d")]
    for metric, window in sources:
        data = _get(f"{LB}/{metric}", {"window": window, "limit": 50}) or []
        for rank, d in enumerate(data):
            w = d["proxyWallet"].lower()
            r = rows.setdefault(w, {"proxyWallet": w, "name": d.get("name"),
                                    "pseudonym": d.get("pseudonym"),
                                    "profit_all": None, "volume_all": None,
                                    "lb_sources": set()})
            r["lb_sources"].add(f"{metric}:{window}")
            if metric == "profit" and window == "all":
                r["profit_all"] = d["amount"]
            if metric == "volume" and window == "all":
                r["volume_all"] = d["amount"]
            # keep a best-known profit/volume even from non-all windows
            if metric == "profit":
                r["profit_best"] = max(r.get("profit_best", 0) or 0, d["amount"])
            if metric == "volume":
                r["volume_best"] = max(r.get("volume_best", 0) or 0, d["amount"])
        time.sleep(0.2)

    df = pd.DataFrame(rows.values())
    df["lb_sources"] = df["lb_sources"].apply(lambda s: ",".join(sorted(s)))
    # rank cohort: prefer all-time profit, then best-known profit, then volume
    df["rank_key"] = df["profit_all"].fillna(df.get("profit_best")).fillna(0)
    df = df.sort_values("rank_key", ascending=False).head(TARGET_TRADERS)
    df = df.reset_index(drop=True)
    df.insert(0, "cohort_rank", df.index + 1)
    return df


# 2. Trade history -----------------------------------------------------------
def fetch_trades(wallet: str) -> list[dict]:
    out, offset = [], 0
    while offset < MAX_TRADES_PER_TRADER:
        page = _get(ACT, {"user": wallet, "limit": PAGE,
                          "offset": offset, "type": "TRADE"})
        if not page:
            break
        out.extend(page)
        if len(page) < PAGE:
            break
        offset += PAGE
    return out[:MAX_TRADES_PER_TRADER]


# 3. Market resolution -------------------------------------------------------
def fetch_resolution(cid: str) -> dict | None:
    m = _get(f"{CLOB}/{cid}")
    if not m or not m.get("tokens"):
        return None
    rec = {"conditionId": cid, "closed": m.get("closed"),
           "question": m.get("question"), "end_date": m.get("end_date_iso")}
    for t in m["tokens"]:
        rec[f"token_{t['outcome']}"] = t["token_id"]
        # payout per share at settlement: winner -> ~1, loser -> ~0
        rec[f"payout_{t['token_id']}"] = float(t.get("price") or 0)
        if t.get("winner"):
            rec["winning_token"] = t["token_id"]
    return rec


def main():
    print("[1/3] Building top-performer cohort ...", flush=True)
    cohort = build_cohort()
    cohort.to_csv(DATA / "traders.csv", index=False)
    print(f"      cohort size = {len(cohort)} unique wallets", flush=True)

    print("[2/3] Fetching trade history ...", flush=True)
    all_trades = []
    with ThreadPoolExecutor(max_workers=N_WORKERS) as ex:
        futs = {ex.submit(fetch_trades, w): w for w in cohort["proxyWallet"]}
        for i, f in enumerate(as_completed(futs), 1):
            all_trades.extend(f.result())
            if i % 10 == 0:
                print(f"      {i}/{len(futs)} wallets, {len(all_trades)} trades", flush=True)
    trades = pd.DataFrame(all_trades)
    trades["proxyWallet"] = trades["proxyWallet"].str.lower()
    trades.to_parquet(DATA / "trades.parquet", index=False)
    print(f"      total trades = {len(trades)}", flush=True)

    print("[3/3] Fetching market resolutions ...", flush=True)
    cids = sorted(trades["conditionId"].dropna().unique())
    print(f"      unique markets = {len(cids)}", flush=True)
    res = []
    with ThreadPoolExecutor(max_workers=N_WORKERS) as ex:
        futs = {ex.submit(fetch_resolution, c): c for c in cids}
        for i, f in enumerate(as_completed(futs), 1):
            r = f.result()
            if r:
                res.append(r)
            if i % 200 == 0:
                print(f"      {i}/{len(cids)} markets resolved-checked", flush=True)
    pd.DataFrame(res).to_parquet(DATA / "resolutions.parquet", index=False)
    print(f"      resolutions found = {len(res)}", flush=True)
    print("DONE.", flush=True)


if __name__ == "__main__":
    main()
