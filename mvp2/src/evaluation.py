"""
mvp2 evaluation — walk-forward splits + the full performance-metrics suite.

Replaces mvp1's single 60/20/20 split with expanding-window walk-forward folds,
*purged* so a training bet must resolve before the test window starts (no leakage
from overlapping outcome windows; an embargo gap is applied). Metrics are computed
on the compounding-bankroll equity curve and reported daily / monthly / yearly,
plus a Deflated-Sharpe guard against multiple-testing inflation.
"""
from __future__ import annotations
import numpy as np
import pandas as pd
from scipy import stats


# --- Walk-forward, purged ---------------------------------------------------
def walk_forward_folds(df: pd.DataFrame, n_folds: int = 4, embargo_h: float = 24.0):
    """Expanding-window folds over entry time, purging train bets whose resolution
    leaks into the test window. Yields (train_df, test_df) per fold."""
    d = df.sort_values("entry_ts").reset_index(drop=True)
    edges = np.quantile(d["entry_ts"], np.linspace(0.4, 1.0, n_folds + 1))
    embargo = embargo_h * 3600
    folds = []
    for k in range(n_folds):
        te_lo, te_hi = edges[k], edges[k + 1]
        test = d[(d["entry_ts"] >= te_lo) & (d["entry_ts"] < te_hi)]
        # train = everything entered before the test window AND resolved before it
        train = d[(d["entry_ts"] < te_lo) & (d["resolve_ts"] < te_lo - embargo)]
        if len(test) and len(train):
            folds.append((train.copy(), test.copy()))
    return folds


# --- Equity-curve / return metrics ------------------------------------------
def _daily_equity(eq: pd.DataFrame) -> pd.Series:
    s = eq.set_index("datetime")["equity"].sort_index()
    return s.resample("1D").last().ffill()


def equity_metrics(eq: pd.DataFrame, bankroll0: float) -> dict:
    if len(eq) < 2:
        return {k: np.nan for k in ("cagr", "roi_total", "sharpe", "sortino",
                "calmar", "max_drawdown", "ret_daily", "ret_monthly", "ret_yearly",
                "vol_annual", "days")}
    daily = _daily_equity(eq)
    rets = daily.pct_change().dropna()
    days = (daily.index[-1] - daily.index[0]).days or 1
    years = days / 365.25
    total = daily.iloc[-1] / bankroll0 - 1.0
    # CAGR is unstable when the calendar window is only days; cap the annualization
    # exponent so a 2-week test doesn't report astronomical "annualized" figures.
    years_eff = max(years, 30 / 365.25)   # treat <1mo windows as ~1 month for CAGR
    cagr = (max(daily.iloc[-1] / bankroll0, 1e-9)) ** (1 / years_eff) - 1.0
    mu, sd = rets.mean(), rets.std(ddof=1)
    downside = rets[rets < 0].std(ddof=1)
    sharpe = (mu / sd * np.sqrt(365)) if sd > 0 else np.nan
    sortino = (mu / downside * np.sqrt(365)) if downside and downside > 0 else np.nan
    run_max = daily.cummax()
    dd = daily / run_max - 1.0
    max_dd = dd.min()
    calmar = (cagr / abs(max_dd)) if max_dd < 0 else np.nan
    return {
        "cagr": cagr, "roi_total": total,
        "ret_daily": (1 + total) ** (1 / max(days, 1)) - 1,
        "ret_monthly": (1 + cagr) ** (1 / 12) - 1,
        "ret_yearly": cagr,
        "vol_annual": sd * np.sqrt(365) if sd > 0 else np.nan,
        "sharpe": sharpe, "sortino": sortino, "calmar": calmar,
        "max_drawdown": max_dd, "days": days,
    }


def trade_metrics(ledger: pd.DataFrame) -> dict:
    if ledger is None or len(ledger) == 0:
        return {"n_bets": 0, "win_rate": np.nan, "profit_factor": np.nan,
                "expectancy": np.nan, "avg_stake": np.nan}
    wins = ledger["pnl"] > 0
    gross_win = ledger.loc[ledger["pnl"] > 0, "pnl"].sum()
    gross_loss = -ledger.loc[ledger["pnl"] < 0, "pnl"].sum()
    return {
        "n_bets": int(len(ledger)),
        "win_rate": float(wins.mean()),
        "profit_factor": float(gross_win / gross_loss) if gross_loss > 0 else np.inf,
        "expectancy": float(ledger["pnl"].mean()),
        "avg_stake": float(ledger["stake"].mean()),
    }


# --- Multiple-testing guard -------------------------------------------------
def deflated_sharpe(daily_rets: np.ndarray, n_trials: int) -> float:
    """Probabilistic/Deflated Sharpe: P(true SR>0) after deflating for n_trials,
    return non-normality and sample length (Bailey & Lopez de Prado 2014)."""
    r = np.asarray(daily_rets, float)
    r = r[np.isfinite(r)]
    n = len(r)
    if n < 10 or r.std(ddof=1) == 0:
        return np.nan
    sr = r.mean() / r.std(ddof=1)                       # per-period SR
    sk, ku = stats.skew(r), stats.kurtosis(r, fisher=False)
    # expected max SR under n_trials independent null strategies
    emc = 0.5772156649
    z = stats.norm.ppf(1 - 1.0 / max(n_trials, 2))
    z2 = stats.norm.ppf(1 - 1.0 / max(n_trials, 2) * np.e ** -1)
    sr0 = np.sqrt(1.0 / (n - 1)) * ((1 - emc) * z + emc * z2)   # deflation benchmark
    denom = np.sqrt(1 - sk * sr + (ku - 1) / 4 * sr ** 2)
    if denom <= 0:
        return np.nan
    return float(stats.norm.cdf((sr - sr0) * np.sqrt(n - 1) / denom))
