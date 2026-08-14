"""Minimal Polymarket gamma/CLOB reader for the ti2026 notebooks.

Public, keyless endpoints only — enough to pull a live book and compare it to
the model. Writing orders is deliberately out of scope for this repo.
"""
from __future__ import annotations

import json

import pandas as pd
import requests

GAMMA = "https://gamma-api.polymarket.com"
CLOB = "https://clob.polymarket.com"

# The four live TI-2026 books (slugs verified 2026-08-14)
TI_SLUGS = {
    "winner": "the-international-2026-winner-20260629212545745",
    "radiant_dire": "the-international-2026-will-radiant-or-dire-have-higher-win-rate-20260811191704245",
    "longest_game": "the-international-2026-longest-single-game-duration-20260617185055630",
    "most_banned": "the-international-2026-most-banned-hero-20260810200955093",
}
PLACEHOLDER_LABELS = set(list("ABCDEFGHIJKLMNOPQR") + ["Other"])


def fetch_event(slug: str, timeout: int = 30) -> dict:
    r = requests.get(f"{GAMMA}/events", params={"slug": slug}, timeout=timeout)
    r.raise_for_status()
    data = r.json()
    if not data:
        raise LookupError(f"no Polymarket event for slug {slug!r}")
    return data[0]


def book_table(slug: str, drop_placeholders: bool = True) -> pd.DataFrame:
    """One row per live outcome: mid, best bid/ask, spread, volume.

    NOTE ON MIDS: in thin books Polymarket's `outcomePrices` can be an
    ask-derived artifact when no bid exists. Rows with `bid is None` should be
    treated as *unpriced*, never as a real mid — several TI books are in that
    state, which is precisely where resting-bid strategies live.
    """
    ev = fetch_event(slug)
    rows = []
    for m in ev["markets"]:
        if m.get("closed") or not m.get("active"):
            continue
        label = m.get("groupItemTitle") or m.get("question")
        if drop_placeholders and label in PLACEHOLDER_LABELS:
            continue
        prices = json.loads(m.get("outcomePrices") or "[]")
        bid, ask = m.get("bestBid"), m.get("bestAsk")
        rows.append({
            "outcome": label,
            "mid": float(prices[0]) if prices else None,
            "bid": float(bid) if bid is not None else None,
            "ask": float(ask) if ask is not None else None,
            "spread": (float(ask) - float(bid)) if (bid is not None and ask is not None) else None,
            "volume": float(m.get("volume") or 0),
            "volume24h": float(m.get("volume24hr") or 0),
            "token_id": (json.loads(m.get("clobTokenIds") or "[]") or [None])[0],
            "fee_type": m.get("feeType"),
        })
    df = pd.DataFrame(rows).sort_values("mid", ascending=False, na_position="last")
    df.attrs["title"] = ev.get("title")
    df.attrs["volume"] = float(ev.get("volume") or 0)
    df.attrs["volume24h"] = float(ev.get("volume24hr") or 0)
    df.attrs["description"] = ev.get("description")
    df.attrs["priced_sum"] = float(df["mid"].dropna().sum())
    df.attrs["bid_sum"] = float(df["bid"].dropna().sum())
    return df


def order_book(token_id: str, timeout: int = 30) -> pd.DataFrame:
    """Full L2 depth for one outcome token (bids/asks with sizes)."""
    r = requests.get(f"{CLOB}/book", params={"token_id": token_id}, timeout=timeout)
    r.raise_for_status()
    b = r.json()
    bids = pd.DataFrame(b.get("bids", [])).assign(side="bid")
    asks = pd.DataFrame(b.get("asks", [])).assign(side="ask")
    out = pd.concat([bids, asks], ignore_index=True)
    if len(out):
        out["price"] = out["price"].astype(float)
        out["size"] = out["size"].astype(float)
    return out


def price_history(token_id: str, interval: str = "1d", fidelity: int = 60) -> pd.DataFrame:
    r = requests.get(f"{CLOB}/prices-history",
                     params={"market": token_id, "interval": interval, "fidelity": fidelity},
                     timeout=30)
    r.raise_for_status()
    h = pd.DataFrame(r.json().get("history", []))
    if len(h):
        h["t"] = pd.to_datetime(h["t"], unit="s")
    return h


def all_ti_books() -> dict[str, pd.DataFrame]:
    return {k: book_table(s) for k, s in TI_SLUGS.items()}
