"""
mvp2 signals & follower selection.

Two lessons from the research drive this module:
  1. mvp1's "consensus" (>=N top traders on the same outcome) was the only signal
     that generalised — but it was measured with hindsight and a zero-latency fill.
     Here the consensus *trigger* is point-in-time: the copier can only act on the
     Nth distinct cohort BUY, and enters at that trade's time (+ latency, in fills).
  2. mvp1's "follow the top-K by raw ROI" lost 96% out-of-sample — the winner's
     curse. The fix is empirical-Bayes (beta-binomial) shrinkage of each wallet's
     win rate toward the population mean, so small-sample "hot" wallets are pulled
     back hard (James-Stein / Efron-Morris).
"""
from __future__ import annotations
import numpy as np
import pandas as pd


# --- Empirical-Bayes follower skill -----------------------------------------
def fit_beta_prior(wins: np.ndarray, n: np.ndarray):
    """Method-of-moments beta prior from per-wallet (wins, n) win-rate samples."""
    rates = wins / np.maximum(n, 1)
    w = n / n.sum()
    m = np.average(rates, weights=w)                 # prior mean
    v = np.average((rates - m) ** 2, weights=w)      # spread of wallet skill
    v = max(v, 1e-6)
    strength = max(m * (1 - m) / v - 1, 1.0)         # prior pseudo-count
    return m * strength, (1 - m) * strength          # alpha0, beta0


def wallet_skill(train_buys: pd.DataFrame, min_bets: int = 10) -> pd.DataFrame:
    """Shrunk win-rate per wallet using a beta-binomial empirical-Bayes prior."""
    g = train_buys.groupby("proxyWallet").agg(
        n=("payout", "size"), wins=("payout", "sum"),
        raw_roi=("roi", "mean"), name=("name", "first")).reset_index()
    a0, b0 = fit_beta_prior(g["wins"].to_numpy(), g["n"].to_numpy())
    g["shrunk_winrate"] = (g["wins"] + a0) / (g["n"] + a0 + b0)
    g["raw_winrate"] = g["wins"] / g["n"]
    g.attrs["prior"] = (a0, b0)
    return g[g["n"] >= min_bets].sort_values("shrunk_winrate", ascending=False)


# --- Consensus trigger (point-in-time) --------------------------------------
def consensus_entries(buys: pd.DataFrame, n_followers: int) -> pd.DataFrame:
    """Return one entry row per (market, token) at the moment the N-th *distinct*
    cohort wallet has bought it — the earliest a copier could act on consensus.

    No look-ahead: distinct-wallet count is accumulated in time order; the trigger
    is the N-th new wallet's trade, and downstream we fill at that time (+latency).
    """
    df = buys.sort_values("timestamp")
    keep_idx = []
    for (_, _), g in df.groupby(["conditionId", "asset"], sort=False):
        seen, trigger = set(), None
        for idx, w in zip(g.index, g["proxyWallet"].to_numpy()):
            seen.add(w)
            if len(seen) >= n_followers:
                trigger = idx
                break
        if trigger is not None:
            keep_idx.append(trigger)
    out = df.loc[keep_idx].copy()
    out["n_consensus"] = n_followers
    return out


def final_buyer_counts(buys: pd.DataFrame) -> pd.Series:
    """Total distinct cohort buyers per (market, token) — for calibration buckets."""
    return buys.groupby(["conditionId", "asset"])["proxyWallet"].transform("nunique")


# --- Calibration ------------------------------------------------------------
def brier_score(p: np.ndarray, outcome: np.ndarray) -> float:
    return float(np.mean((np.asarray(p) - np.asarray(outcome)) ** 2))


def calibrate_by_price(train: pd.DataFrame, n_buckets: int = 10):
    """Fit empirical win rate by entry-price bucket on TRAIN, return p(price).

    This is the honest edge test: a copy strategy is only +EV where copied bets at
    a given price win *more often than the price implies*. If the calibrated win
    rate ≈ price, Kelly sizing yields ~0 and the strategy correctly does nothing.
    """
    d = train.dropna(subset=["fill_price", "payout"])
    if len(d) < n_buckets * 5:
        base = d["payout"].mean() if len(d) else 0.5
        return (lambda price: np.full_like(np.asarray(price, float), base)), {}
    try:
        q = pd.qcut(d["fill_price"], n_buckets, duplicates="drop")
    except ValueError:
        q = pd.cut(d["fill_price"], n_buckets)
    tab = d.groupby(q, observed=True).agg(
        lo=("fill_price", "min"), hi=("fill_price", "max"),
        p=("payout", "mean")).reset_index(drop=True)
    centers = ((tab["lo"] + tab["hi"]) / 2).to_numpy()
    probs = tab["p"].to_numpy()

    def f(price):
        return np.interp(np.asarray(price, float), centers, probs,
                         left=probs[0], right=probs[-1])
    return f, tab.to_dict("records")


def calibrate_consensus(train_buys: pd.DataFrame) -> dict:
    """Map distinct-buyer count -> empirical win probability (point-in-time prior)."""
    df = train_buys.copy()
    df["buyers"] = final_buyer_counts(df)
    # collapse to one row per (market, token): did that token win?
    per = df.groupby(["conditionId", "asset"]).agg(
        buyers=("buyers", "first"), win=("payout", "first")).reset_index()
    table = per.groupby("buyers")["win"].mean().to_dict()
    return table


def consensus_winprob(n_buyers, table: dict, fallback: float) -> float:
    if n_buyers in table:
        return table[n_buyers]
    # use the highest available bucket <= n_buyers, else fallback
    keys = sorted(k for k in table if k <= n_buyers)
    return table[keys[-1]] if keys else fallback
