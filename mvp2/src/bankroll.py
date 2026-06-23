"""
mvp2 bankroll management — the half mvp1 was missing.

mvp1 staked $1 on every bet (no capital dynamics). mvp2 sizes each copy with
fractional Kelly on a calibrated win probability, caps per-position and aggregate
exposure, handles the correlation of bets that share an event, and simulates a
*compounding* bankroll so we can report real daily / monthly / yearly returns.

Binary-contract Kelly (price c, est. win prob p):   f* = (p - c) / (1 - c),  p>c
Fractional Kelly (kelly_frac in {0.25, 0.5}) controls the growth/drawdown trade:
the probability of ever drawing down to fraction a of bankroll is ~ a^(1/kelly_frac).
"""
from __future__ import annotations
import numpy as np
import pandas as pd


def kelly_binary(p: np.ndarray, c: np.ndarray) -> np.ndarray:
    """Optimal full-Kelly fraction for a $0/$1 contract bought at price c."""
    p, c = np.asarray(p, float), np.asarray(c, float)
    f = (p - c) / np.clip(1 - c, 1e-6, None)
    return np.clip(f, 0.0, 1.0)


def simulate(events: pd.DataFrame, *, bankroll0: float = 10_000.0,
             kelly_frac: float = 0.25, cap_per_bet: float = 0.03,
             cap_aggregate: float = 0.30, cap_per_event: float = 0.10) -> dict:
    """Event-driven compounding simulation.

    `events` needs columns: entry_ts, resolve_ts, cost_per_share, payout(0/1),
    win_prob (estimated p), conditionId (for per-event exposure caps).

    Returns equity curve (daily) + per-bet ledger. Sizing is fractional Kelly on
    available (un-committed) bankroll, clipped by per-bet / per-event / aggregate
    exposure caps. Correlated bets (same conditionId) share `cap_per_event`.
    """
    ev = events.dropna(subset=["entry_ts", "resolve_ts", "cost_per_share"]).copy()
    ev = ev.sort_values("entry_ts").reset_index(drop=True)

    # build a chronological event queue: (+1) entries and (-1) resolutions
    entries = [(r.entry_ts, 0, i) for i, r in ev.iterrows()]
    exits = [(r.resolve_ts, 1, i) for i, r in ev.iterrows()]
    queue = sorted(entries + exits, key=lambda x: (x[0], x[1]))

    bankroll = bankroll0                 # cash available
    committed = 0.0                      # capital locked in open positions
    event_exposure: dict[str, float] = {}   # conditionId -> locked $
    ledger = {i: None for i in range(len(ev))}
    curve = []   # (timestamp, equity)

    for ts, kind, i in queue:
        row = ev.iloc[i]
        if kind == 0:  # ENTRY — size and (maybe) place the bet
            equity = bankroll + committed
            p, c = float(row["win_prob"]), float(row["cost_per_share"])
            f = kelly_frac * kelly_binary(p, c)
            stake = f * bankroll                       # fraction of *available* cash
            stake = min(stake, cap_per_bet * equity)   # per-bet cap
            cid = row["conditionId"]
            room_event = cap_per_event * equity - event_exposure.get(cid, 0.0)
            room_agg = cap_aggregate * equity - committed
            stake = max(0.0, min(stake, room_event, room_agg, bankroll))
            if stake <= 0:
                ledger[i] = {"stake": 0.0, "pnl": 0.0, "placed": False}
                continue
            bankroll -= stake
            committed += stake
            event_exposure[cid] = event_exposure.get(cid, 0.0) + stake
            ledger[i] = {"stake": stake, "entry_ts": ts, "placed": True,
                         "cost_per_share": c, "payout": float(row["payout"]),
                         "conditionId": cid}
        else:          # EXIT — settle at resolution
            li = ledger[i]
            if not li or not li.get("placed"):
                continue
            shares = li["stake"] / li["cost_per_share"]
            payout_value = shares * li["payout"]       # $1/share if won, else $0
            pnl = payout_value - li["stake"]
            bankroll += li["stake"] + pnl
            committed -= li["stake"]
            event_exposure[li["conditionId"]] = max(
                0.0, event_exposure.get(li["conditionId"], 0.0) - li["stake"])
            li["pnl"] = pnl
            li["resolve_ts"] = ts
        curve.append((ts, bankroll + committed))

    led = pd.DataFrame([v for v in ledger.values() if v and v.get("placed")])
    eq = pd.DataFrame(curve, columns=["timestamp", "equity"])
    eq["datetime"] = pd.to_datetime(eq["timestamp"], unit="s", utc=True)
    return {"equity": eq, "ledger": led, "bankroll0": bankroll0,
            "bankroll_final": bankroll + committed}
