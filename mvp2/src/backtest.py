"""
mvp2 orchestration: turn a copy strategy into a sized, walk-forward-evaluated,
compounding-bankroll backtest.

Pipeline per strategy:
  select entries  ->  realistic fill (latency + fees)  ->  estimate win prob p
  ->  fractional-Kelly sizing on a compounding bankroll  ->  walk-forward metrics.

Strategies:
  copy_all        copy every cohort BUY (sized by population base-rate p)
  follow_skill    copy only empirical-Bayes top-skill wallets (p = shrunk win rate)
  consensus       copy the N-th distinct-buyer trigger (p = calibrated by buyer count)
"""
from __future__ import annotations
from pathlib import Path
import numpy as np
import pandas as pd

import fills, signals, bankroll, evaluation as ev

MVP1 = Path(__file__).resolve().parents[2] / "mvp1" / "data"


# --- shared event timing ----------------------------------------------------
def resolution_proxy() -> dict:
    """Resolution time per market ≈ last observed trade on it (data-driven, since
    API end_dates are unreliable for these markets)."""
    t = pd.read_parquet(MVP1 / "trades.parquet")
    t["conditionId"] = t["conditionId"].astype(str)
    return t.groupby("conditionId")["timestamp"].max().to_dict()


def base_buys(delta_s: float) -> pd.DataFrame:
    """All copyable BUYs with realistic fill at latency `delta_s`, fees, and times."""
    b = fills.load_buys()
    b = fills.reconstruct_fill(b, delta_s=delta_s)
    b = fills.price_after_fees(b)
    b = b[b["fillable"]].copy()
    rp = resolution_proxy()
    b["entry_ts"] = b["timestamp"] + delta_s
    b["resolve_ts"] = b["conditionId"].map(rp).astype(float)
    b = b[b["resolve_ts"] > b["entry_ts"]].copy()
    return b.sort_values("entry_ts").reset_index(drop=True)


# --- win-probability estimators (fit on train) ------------------------------
# Win prob is calibrated PRICE-conditionally on train: edge exists only where
# copied bets beat the market price. Then we SHRINK that estimate toward the
# market price (the efficient prior): p_hat = price + shrink*(p_cal - price).
# Survivorship lives on the cohort axis (we picked the 100 winners), so the raw
# calibrated edge is inflated; shrinkage is the research-prescribed antidote to
# overestimated-p overbetting. shrink=1 trusts the cohort fully, shrink=0 trusts
# only the market (Kelly -> 0). DEFAULT 0.5.
DEFAULT_SHRINK = 0.5


def _shrink(p_cal, price, shrink):
    p_cal, price = np.asarray(p_cal, float), np.asarray(price, float)
    return np.clip(price + shrink * (p_cal - price), 0.0, 1.0)


def attach_winprob_copyall(train, test, shrink=DEFAULT_SHRINK):
    f, _ = signals.calibrate_by_price(train)
    out = test.copy()
    out["win_prob"] = _shrink(f(out["fill_price"]), out["fill_price"], shrink)
    return out


def attach_winprob_skill(train, test, min_bets=10, top_frac=0.5, shrink=DEFAULT_SHRINK):
    skill = signals.wallet_skill(train, min_bets=min_bets)
    keep = skill.head(max(1, int(len(skill) * top_frac)))
    sub_train = train[train["proxyWallet"].isin(keep["proxyWallet"])]
    f, _ = signals.calibrate_by_price(sub_train)   # price-calibrated on skilled subset
    out = test[test["proxyWallet"].isin(set(keep["proxyWallet"]))].copy()
    out["win_prob"] = _shrink(f(out["fill_price"]), out["fill_price"], shrink)
    return out


def attach_winprob_consensus(train, test, n_followers, fallback, shrink=DEFAULT_SHRINK):
    # consensus signal = distinct-buyer count; calibrate its win rate on train
    table = signals.calibrate_consensus(train)
    ent = signals.consensus_entries(test, n_followers).copy()
    buyers = signals.final_buyer_counts(test)
    ent["buyers"] = buyers.loc[ent.index].values
    p_cal = ent["buyers"].apply(lambda k: signals.consensus_winprob(k, table, fallback))
    ent["win_prob"] = _shrink(p_cal.to_numpy(), ent["fill_price"].to_numpy(), shrink)
    return ent


# --- run one strategy across walk-forward folds, chaining the bankroll ------
def run_strategy(buys, build_test_events, *, n_folds=4, embargo_h=24.0,
                 kelly_frac=0.25, bankroll0=10_000.0, **sim_kw):
    """Returns stitched equity curve + ledger + aggregate metrics.

    Params are re-fit on each fold's train; the bankroll is carried across folds
    so daily/monthly/yearly compounding is realistic."""
    folds = ev.walk_forward_folds(buys, n_folds=n_folds, embargo_h=embargo_h)
    equity_parts, ledgers, bk = [], [], bankroll0
    for train, test in folds:
        events = build_test_events(train, test)
        events = events.dropna(subset=["win_prob", "cost_per_share",
                                       "entry_ts", "resolve_ts"])
        if len(events) == 0:
            continue
        res = bankroll.simulate(events, bankroll0=bk, kelly_frac=kelly_frac, **sim_kw)
        equity_parts.append(res["equity"]); ledgers.append(res["ledger"])
        bk = res["bankroll_final"]
    if not equity_parts:
        return None
    equity = pd.concat(equity_parts).sort_values("timestamp").reset_index(drop=True)
    ledger = pd.concat(ledgers, ignore_index=True) if ledgers else pd.DataFrame()
    m = ev.equity_metrics(equity, bankroll0)
    m.update(ev.trade_metrics(ledger))
    daily = equity.set_index("datetime")["equity"].resample("1D").last().ffill()
    m["deflated_sharpe"] = ev.deflated_sharpe(daily.pct_change().dropna().values,
                                              n_trials=12)
    m["bankroll_final"] = bk
    return {"equity": equity, "ledger": ledger, "metrics": m, "n_folds": len(folds)}
