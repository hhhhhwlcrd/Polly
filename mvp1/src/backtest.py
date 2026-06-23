"""
Polly — copy-trading backtest engine.

Core idea
---------
A *copyable bet* is a BUY trade by a top-performer on a market that later
resolved.  A copier who mirrors that bet buys the same outcome token and
holds it to resolution.  Spending $1 at price p buys 1/p shares; each
winning share settles at $1, losing shares at $0.  So the per-dollar return
of one copied bet is::

    roi = payout / entry_price_eff - 1            payout in {0, 1}
    entry_price_eff = min(price * (1 + slippage), PRICE_CAP)

This single formula prices favorites and long-shots consistently and needs
nothing but the trader's execution price plus the market's settlement.

Everything downstream (strategies, train/val/test) just decides *which* bets
to copy and *how much* weight to put on each.
"""
from __future__ import annotations
from pathlib import Path
import numpy as np
import pandas as pd

DATA = Path(__file__).resolve().parent.parent / "data"
PRICE_CAP = 0.99      # cannot effectively buy a share for more than ~$0.99
PRICE_FLOOR = 0.01


# --------------------------------------------------------------------------
# Loading & assembly
# --------------------------------------------------------------------------
def load_raw():
    traders = pd.read_csv(DATA / "traders.csv")
    trades = pd.read_parquet(DATA / "trades.parquet")
    res = pd.read_parquet(DATA / "resolutions.parquet")
    return traders, trades, res


def build_bets(slippage: float = 0.0) -> pd.DataFrame:
    """Return the per-bet copyable dataset (one row per BUY on a resolved market)."""
    traders, trades, res = load_raw()

    # winning token + payout lookup per (conditionId)
    res = res.dropna(subset=["conditionId"])
    win_map = res.set_index("conditionId")["winning_token"].to_dict()
    closed_map = res.set_index("conditionId")["closed"].to_dict()

    df = trades.copy()
    df = df[df["side"] == "BUY"].copy()
    df["conditionId"] = df["conditionId"].astype(str)
    df["asset"] = df["asset"].astype(str)

    df["closed"] = df["conditionId"].map(closed_map)
    df["winning_token"] = df["conditionId"].map(win_map)
    # keep only resolved markets with a known winner
    df = df[(df["closed"] == True) & df["winning_token"].notna()].copy()

    df["payout"] = (df["asset"] == df["winning_token"].astype(str)).astype(float)
    df["datetime"] = pd.to_datetime(df["timestamp"], unit="s", utc=True)
    df["date"] = df["datetime"].dt.date

    df = apply_pricing(df, slippage)

    # attach cohort rank / labels (drop overlapping cols from activity first)
    tr = traders[["proxyWallet", "cohort_rank", "name", "profit_all",
                  "volume_all"]].copy()
    tr["proxyWallet"] = tr["proxyWallet"].str.lower()
    df = df.drop(columns=[c for c in ["name", "pseudonym"] if c in df.columns])
    df = df.merge(tr, on="proxyWallet", how="left")

    df = df.sort_values("timestamp").reset_index(drop=True)
    return df


def apply_pricing(df: pd.DataFrame, slippage: float) -> pd.DataFrame:
    df = df.copy()
    df["entry_price"] = df["price"].clip(PRICE_FLOOR, PRICE_CAP)
    df["entry_price_eff"] = (df["price"] * (1 + slippage)).clip(PRICE_FLOOR, PRICE_CAP)
    df["roi"] = df["payout"] / df["entry_price_eff"] - 1.0
    return df


# --------------------------------------------------------------------------
# Chronological split
# --------------------------------------------------------------------------
def date_split(df, train=0.6, val=0.2):
    """Chronological split by trade time — no look-ahead leakage."""
    df = df.sort_values("timestamp")
    n = len(df)
    i_tr, i_val = int(n * train), int(n * (train + val))
    splits = {
        "train": df.iloc[:i_tr].copy(),
        "val": df.iloc[i_tr:i_val].copy(),
        "test": df.iloc[i_val:].copy(),
    }
    return splits


def split_ranges(splits):
    rows = []
    for name, d in splits.items():
        rows.append({"split": name, "n_bets": len(d),
                     "start": d["datetime"].min(), "end": d["datetime"].max(),
                     "n_markets": d["conditionId"].nunique(),
                     "n_traders": d["proxyWallet"].nunique()})
    return pd.DataFrame(rows)


# --------------------------------------------------------------------------
# Portfolio evaluation
# --------------------------------------------------------------------------
def evaluate(bets: pd.DataFrame, weight: pd.Series | None = None) -> dict:
    """Weighted ROI / P&L of copying a set of bets. weight ~ capital per bet."""
    if len(bets) == 0:
        return {"n_bets": 0, "roi": np.nan, "win_rate": np.nan,
                "total_pnl": np.nan, "capital": np.nan, "avg_price": np.nan}
    w = np.ones(len(bets)) if weight is None else np.asarray(weight, dtype=float)
    w = np.where(np.isfinite(w) & (w > 0), w, 0.0)
    if w.sum() == 0:
        w = np.ones(len(bets))
    cap = w.sum()
    pnl = float((w * bets["roi"].values).sum())
    return {
        "n_bets": int(len(bets)),
        "roi": pnl / cap,                       # return on deployed capital
        "win_rate": float(bets["payout"].mean()),
        "total_pnl": pnl,
        "capital": float(cap),
        "avg_price": float(bets["entry_price_eff"].mean()),
    }


def equity_curve(bets: pd.DataFrame, weight=None):
    """Cumulative P&L over time for a $1-per-unit-weight copier."""
    b = bets.sort_values("timestamp")
    w = np.ones(len(b)) if weight is None else np.asarray(weight, float)[b.index.argsort()]
    cum = np.cumsum(w * b["roi"].values)
    return b["datetime"].values, cum


# --------------------------------------------------------------------------
# Strategies — each maps a bets frame -> (filtered bets, weights)
# Params fitted on train/val are passed in explicitly.
# --------------------------------------------------------------------------
def s_copy_all(bets):
    return bets, np.ones(len(bets))


def s_stake_weighted(bets):
    w = bets["usdcSize"].clip(lower=0).fillna(0).values
    return bets, w


def s_follow_topk(bets, good_wallets):
    sub = bets[bets["proxyWallet"].isin(good_wallets)]
    return sub, np.ones(len(sub))


def s_price_band(bets, lo, hi):
    sub = bets[(bets["entry_price"] >= lo) & (bets["entry_price"] <= hi)]
    return sub, np.ones(len(sub))


def s_consensus(bets, min_followers):
    """Copy a (market, outcome-token) only if >= N cohort traders bought it."""
    k = bets.groupby(["conditionId", "asset"])["proxyWallet"].transform("nunique")
    sub = bets[k >= min_followers]
    return sub, np.ones(len(sub))


def s_smart_money(bets, good_wallets, wallet_weight):
    """Follow positive-edge wallets, weighting by their train-period edge."""
    sub = bets[bets["proxyWallet"].isin(good_wallets)].copy()
    w = sub["proxyWallet"].map(wallet_weight).fillna(0).values
    return sub, w


# --------------------------------------------------------------------------
# Helpers to fit params from a (train) frame
# --------------------------------------------------------------------------
def wallet_edge(train_bets: pd.DataFrame, min_bets=15) -> pd.DataFrame:
    g = train_bets.groupby("proxyWallet").agg(
        n=("roi", "size"), edge=("roi", "mean"), win=("payout", "mean"),
        name=("name", "first")).reset_index()
    return g[g["n"] >= min_bets].sort_values("edge", ascending=False)
