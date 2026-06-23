"""
mvp2 realistic fill model — the central fix over mvp1.

mvp1 priced a copied bet at the *leader's own* execution price with a flat 2%
slippage and zero latency. That is optimistic: a copier observes the trade only
after ~3-8s (Polygon block + indexer/poll), and the price has often already moved.

Historical order books aren't retrievable for resolved markets, so we reconstruct
the price a copier would actually face at `trigger_ts + delta` directly from our
own dense trade tape: the price of the *next trade that actually happened* on the
same outcome token at-or-after `trigger_ts + delta`. This is a real, data-driven
proxy for "the price available shortly after the leader acted".

On top of that we charge Polymarket's category taker fee (makers pay 0):
    fee_per_share = fee_rate * p * (1 - p)
    cost_per_share = p + fee_per_share = p * (1 + fee_rate * (1 - p))
    roi            = payout / cost_per_share - 1,   payout in {0, 1}
"""
from __future__ import annotations
from pathlib import Path
import numpy as np
import pandas as pd

MVP1 = Path(__file__).resolve().parents[2] / "mvp1" / "data"
META = Path(__file__).resolve().parents[1] / "data" / "market_meta.parquet"
PRICE_FLOOR, PRICE_CAP = 0.01, 0.99
MAX_LOOKAHEAD_S = 6 * 3600   # if no trade within this window after t+delta, no reliable fill


def load_buys() -> pd.DataFrame:
    """Cohort BUYs on resolved markets, with payout, meta, and time-to-resolution."""
    trades = pd.read_parquet(MVP1 / "trades.parquet")
    res = pd.read_parquet(MVP1 / "resolutions.parquet").dropna(subset=["conditionId"])
    traders = pd.read_csv(MVP1 / "traders.csv")

    res["conditionId"] = res["conditionId"].astype(str)
    win = res.set_index("conditionId")["winning_token"].to_dict()
    closed = res.set_index("conditionId")["closed"].to_dict()
    endd = res.set_index("conditionId")["end_date"].to_dict()

    df = trades[trades["side"] == "BUY"].copy()
    df["conditionId"] = df["conditionId"].astype(str)
    df["asset"] = df["asset"].astype(str)
    df["proxyWallet"] = df["proxyWallet"].str.lower()
    df["closed"] = df["conditionId"].map(closed)
    df["winning_token"] = df["conditionId"].map(win)
    df = df[(df["closed"] == True) & df["winning_token"].notna()].copy()
    df["payout"] = (df["asset"] == df["winning_token"].astype(str)).astype(float)
    df["datetime"] = pd.to_datetime(df["timestamp"], unit="s", utc=True)

    # time to resolution (hours) -> H2 slow-vs-fast test
    end_ts = pd.to_datetime(pd.Series(df["conditionId"].map(endd)), utc=True, errors="coerce")
    df["hours_to_resolve"] = (end_ts.values - df["datetime"].values) / np.timedelta64(1, "h")

    # market meta (fee category, neg_risk)
    if META.exists():
        meta = pd.read_parquet(META)
        df = df.merge(meta[["conditionId", "category", "fee_rate", "neg_risk"]],
                      on="conditionId", how="left")
    df["fee_rate"] = df.get("fee_rate", pd.Series(0.05, index=df.index)).fillna(0.05)
    df["category"] = df.get("category", pd.Series("Other", index=df.index)).fillna("Other")
    df["neg_risk"] = df.get("neg_risk", pd.Series(False, index=df.index)).fillna(False)

    tr = traders[["proxyWallet", "cohort_rank", "name"]].copy()
    tr["proxyWallet"] = tr["proxyWallet"].str.lower()
    df = df.drop(columns=[c for c in ["name", "pseudonym"] if c in df.columns])
    df = df.merge(tr, on="proxyWallet", how="left")
    return df.sort_values("timestamp").reset_index(drop=True)


def _asset_price_index(trades: pd.DataFrame):
    """Per-token sorted (timestamp, price) arrays for fast next-trade lookup."""
    idx = {}
    for asset, g in trades.sort_values("timestamp").groupby("asset"):
        idx[asset] = (g["timestamp"].to_numpy(), g["price"].to_numpy())
    return idx


def reconstruct_fill(buys: pd.DataFrame, delta_s: float,
                     all_trades: pd.DataFrame | None = None) -> pd.DataFrame:
    """Add `fill_price` = price of next trade on the same token at/after trigger+delta.

    delta_s = 0 reproduces an (almost) mvp1-style optimistic fill at the leader's
    own next-observable price. Larger delta = more realistic latency.
    """
    if all_trades is None:
        all_trades = buys
    idx = _asset_price_index(all_trades)
    out = buys.copy()
    fill = np.full(len(out), np.nan)
    ts = out["timestamp"].to_numpy()
    assets = out["asset"].to_numpy()
    own = out["price"].to_numpy()
    for i in range(len(out)):
        arr = idx.get(assets[i])
        if arr is None:
            continue
        t_arr, p_arr = arr
        target = ts[i] + delta_s
        j = np.searchsorted(t_arr, target, side="left")
        if j < len(t_arr) and (t_arr[j] - target) <= MAX_LOOKAHEAD_S:
            fill[i] = p_arr[j]
        elif delta_s == 0:
            fill[i] = own[i]   # no later trade; use own price at zero latency
    out["fill_price"] = np.clip(fill, PRICE_FLOOR, PRICE_CAP)
    out["fillable"] = ~np.isnan(fill)
    return out


def price_after_fees(df: pd.DataFrame, price_col: str = "fill_price") -> pd.DataFrame:
    """Cost per share incl. taker fee, and resulting per-bet ROI to resolution."""
    out = df.copy()
    p = out[price_col].clip(PRICE_FLOOR, PRICE_CAP)
    out["fee_per_share"] = out["fee_rate"] * p * (1 - p)
    out["cost_per_share"] = (p + out["fee_per_share"]).clip(PRICE_FLOOR, 0.999)
    out["roi"] = out["payout"] / out["cost_per_share"] - 1.0
    return out
