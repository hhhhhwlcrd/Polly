"""Pricing models for TI-2026 *derivative* (game-statistic) markets.

These are the markets where a match-data pipeline actually creates edge: the
outcome is a public statistic, not a team's fate, so a decent model of the
data-generating process beats a thin retail book. Three models here, one per
live Polymarket book:

  A. radiant_dire_market      "Will Radiant or Dire have the higher win rate"
  B. longest_game_market      "Longest single game duration" (minute buckets)
  C. most_banned_hero_market  "Most banned hero"

Each takes *tournament state so far* plus a prior calibrated on historical /
current-patch data, propagates parameter uncertainty (Beta / bootstrap /
Dirichlet), and returns probabilities directly comparable to the book.

Everything is deliberately explicit about its assumptions: the honest failure
mode of these markets is a confident model built on the wrong N.
"""
from __future__ import annotations

import numpy as np
import pandas as pd


# ============================================================ A. Radiant/Dire
def radiant_dire_market(
    games_played: int = 0,
    radiant_wins_so_far: int = 0,
    games_remaining: int = 180,
    prior_p: float = 0.53,
    prior_strength: float = 200.0,
    n_sims: int = 200_000,
    seed: int = 11,
) -> dict:
    """P(Radiant total > Dire total), P(Dire > Radiant), P(exact tie).

    Model: the per-game radiant win probability p is uncertain, given a
    Beta(prior_p·k, (1−prior_p)·k) prior updated by the games already played
    at this tournament. Remaining games are Binomial(n_remaining, p).

    `prior_p` should be the *current-patch professional* radiant win rate
    (compute it from the match tape: game_stats.pace_features → radiant_winrate,
    or a league-wide count), NOT a pub number and NOT a stale patch.
    `prior_strength` is how many pseudo-games of confidence that prior carries;
    200 ≈ "a season of tier-1 data, but the patch could differ".

    Returns probabilities plus the implied fair prices and the posterior mean p.
    """
    rng = np.random.default_rng(seed)
    a = prior_p * prior_strength + radiant_wins_so_far
    b = (1 - prior_p) * prior_strength + (games_played - radiant_wins_so_far)
    p = rng.beta(a, b, size=n_sims)
    future_rad = rng.binomial(games_remaining, p)
    total_rad = radiant_wins_so_far + future_rad
    total_games = games_played + games_remaining
    total_dire = total_games - total_rad

    p_rad = float((total_rad > total_dire).mean())
    p_dire = float((total_dire > total_rad).mean())
    p_tie = float((total_rad == total_dire).mean())
    return {
        "p_radiant": p_rad,
        "p_dire": p_dire,
        "p_tie": p_tie,
        "posterior_p_mean": float(p.mean()),
        "posterior_p_sd": float(p.std()),
        "total_games_assumed": total_games,
        "fair_prices": {"Radiant": round(p_rad, 4), "Dire": round(p_dire, 4),
                        "Neither": round(p_tie, 4)},
    }


def radiant_dire_sensitivity(
    grid_p=(0.50, 0.51, 0.52, 0.53, 0.54, 0.55),
    grid_n=(120, 150, 180, 220),
    **kw,
) -> pd.DataFrame:
    """P(Radiant) across plausible (true p, total games) — the honesty table.

    The market's price maps to a *combination* of p and N, so quoting a single
    number without this grid overstates precision.
    """
    rows = []
    for p in grid_p:
        for n in grid_n:
            r = radiant_dire_market(games_remaining=n, prior_p=p,
                                    prior_strength=1e6, n_sims=40_000, **kw)
            rows.append({"true_p": p, "n_games": n, "p_radiant": round(r["p_radiant"], 3)})
    return pd.DataFrame(rows).pivot(index="true_p", columns="n_games", values="p_radiant")


# ========================================================= B. Longest game
def longest_game_market(
    durations_min: np.ndarray | list,
    games_remaining: int,
    buckets: list[tuple[int, int | None]],
    longest_so_far: float = 0.0,
    tail_model: str = "empirical",
    n_sims: int = 100_000,
    seed: int = 12,
) -> pd.DataFrame:
    """Distribution of the tournament's MAXIMUM game duration.

    `durations_min` : a reference sample of pro game lengths, in minutes, from
                      the SAME patch (7.4x) — the right-tail shape is what
                      matters, so use hundreds of games, not dozens.
    `buckets`       : e.g. [(91,95),(96,100),(101,105),(106,110),(111,None)].
    `longest_so_far`: the longest game already played at the tournament; the
                      final max can never be below it.

    Two tail models:
      "empirical"  — bootstrap resample the observed durations (safe, but
                     cannot produce a longer game than history contains)
      "gpd"        — fit a Generalised Pareto tail above the 90th percentile,
                     which *can* extrapolate beyond the sample (use when the
                     buckets sit at/above your sample max)
    """
    d = np.asarray([x for x in durations_min if np.isfinite(x) and x > 0], dtype=float)
    if len(d) < 50:
        raise ValueError(f"need >=50 reference durations, got {len(d)}")
    rng = np.random.default_rng(seed)

    if tail_model == "empirical":
        draws = rng.choice(d, size=(n_sims, games_remaining), replace=True)
        sim_max = draws.max(axis=1)
    elif tail_model == "gpd":
        u = np.quantile(d, 0.90)
        exceed = d[d > u] - u
        # method-of-moments GPD fit
        m, v = exceed.mean(), exceed.var()
        xi = 0.5 * (1 - m**2 / v) if v > 0 else 0.1
        sigma = 0.5 * m * (m**2 / v + 1) if v > 0 else m
        xi = float(np.clip(xi, -0.4, 0.4))
        p_exceed = len(exceed) / len(d)
        body = d[d <= u]
        sim_max = np.empty(n_sims)
        for i in range(n_sims):
            n_tail = rng.binomial(games_remaining, p_exceed)
            best = body[rng.integers(0, len(body), size=games_remaining - n_tail)].max() \
                if games_remaining - n_tail > 0 else 0.0
            if n_tail > 0:
                w = rng.random(n_tail)
                tail = u + (sigma / xi) * ((1 - w) ** (-xi) - 1) if abs(xi) > 1e-6 \
                    else u - sigma * np.log(1 - w)
                best = max(best, float(tail.max()))
            sim_max[i] = best
    else:
        raise ValueError("tail_model must be 'empirical' or 'gpd'")

    sim_max = np.maximum(sim_max, longest_so_far)
    sim_max = np.floor(sim_max)  # market rounds DOWN to the nearest minute

    rows = []
    for lo, hi in buckets:
        if hi is None:
            p = float((sim_max >= lo).mean())
            label = f"{lo}+"
        else:
            p = float(((sim_max >= lo) & (sim_max <= hi)).mean())
            label = f"{lo}-{hi}"
        rows.append({"bucket": label, "p": round(p, 4)})
    below = float((sim_max < buckets[0][0]).mean())
    rows.append({"bucket": f"<{buckets[0][0]} (unlisted/Other)", "p": round(below, 4)})
    out = pd.DataFrame(rows)
    out.attrs["sim_max_mean"] = float(sim_max.mean())
    out.attrs["sim_max_p50"] = float(np.median(sim_max))
    out.attrs["sim_max_p95"] = float(np.quantile(sim_max, 0.95))
    out.attrs["tail_model"] = tail_model
    return out


# ======================================================= C. Most banned hero
def most_banned_hero_market(
    bans_so_far: pd.Series | dict,
    games_played: int,
    games_remaining: int,
    prior_rates: pd.Series | dict | None = None,
    prior_strength: float = 30.0,
    bans_per_game: int = 14,
    n_sims: int = 40_000,
    seed: int = 13,
) -> pd.DataFrame:
    """P(each hero finishes as the single most-banned hero of the tournament).

    Model: each game's 14 ban slots are drawn from a hero-level ban-rate vector
    θ with a Dirichlet posterior — Dirichlet(prior_strength·prior_rates +
    bans_so_far) — then remaining bans are Multinomial. Ties are resolved to
    "no winner" mass and reported separately (the real market resolves ties
    alphabetically, so treat tie mass as a haircut on the leader).

    `bans_so_far`  : hero → ban count at this tournament (from draft.ban_table).
    `prior_rates`  : hero → ban share from recent same-patch tier-1 play. When
                     None, a uniform prior over the observed heroes is used
                     (weak; supply a real prior for anything load-bearing).
    """
    bans = pd.Series(bans_so_far, dtype=float)
    heroes = list(bans.index)
    if prior_rates is not None:
        pr = pd.Series(prior_rates, dtype=float).reindex(heroes).fillna(0.0)
        pr = pr / pr.sum() if pr.sum() > 0 else pd.Series(1.0 / len(heroes), index=heroes)
    else:
        pr = pd.Series(1.0 / len(heroes), index=heroes)

    alpha = prior_strength * pr.to_numpy() + bans.to_numpy()
    rng = np.random.default_rng(seed)
    remaining_bans = int(games_remaining * bans_per_game)

    wins = np.zeros(len(heroes))
    ties = 0
    base = bans.to_numpy()
    B = 2000  # simulate in blocks to bound memory
    done = 0
    while done < n_sims:
        k = min(B, n_sims - done)
        theta = rng.dirichlet(alpha, size=k)
        future = np.array([rng.multinomial(remaining_bans, t) for t in theta])
        total = base[None, :] + future
        mx = total.max(axis=1, keepdims=True)
        is_max = total == mx
        n_max = is_max.sum(axis=1)
        wins += (is_max & (n_max[:, None] == 1)).sum(axis=0)
        ties += int((n_max > 1).sum())
        done += k

    out = pd.DataFrame({
        "hero_id": heroes,
        "bans_so_far": base,
        "p_most_banned": wins / n_sims,
    }).sort_values("p_most_banned", ascending=False).reset_index(drop=True)
    out.attrs["p_tie_any"] = ties / n_sims
    out.attrs["remaining_ban_slots"] = remaining_bans
    return out


# ============================================================ market compare
def compare_to_book(model: pd.DataFrame, book: dict, key: str, p_col: str,
                    fee_rate: float = 0.03, half_spread: float = 0.01) -> pd.DataFrame:
    """Join model probabilities to live Polymarket prices and net out costs.

    `book` : {outcome_label: price}. `key`/`p_col`: model's label/probability
    columns. Taker fee on Polymarket sports-schedule = rate·p·(1−p) per share;
    makers pay zero, so `edge_maker` is the number that matters for a resting
    bid strategy in a thin book.
    """
    df = model.copy()
    df["price"] = df[key].map(book)
    df = df.dropna(subset=["price"])
    df["fee"] = fee_rate * df["price"] * (1 - df["price"])
    df["edge_raw"] = df[p_col] - df["price"]
    df["edge_taker"] = df["edge_raw"] - df["fee"] - half_spread
    df["edge_maker"] = df["edge_raw"]
    return df.sort_values("edge_maker", ascending=False)
