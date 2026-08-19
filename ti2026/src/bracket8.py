"""8-team double-elimination Monte Carlo — the TI Main Event structure.

Standard TI main-event bracket (used TI11-TI14): 4 teams start in the upper
bracket, 4 in the lower bracket. Losing an upper-bracket match drops you into
the lower bracket; losing in the lower bracket eliminates you.

    UB semis  : U1-U2, U3-U4            (losers -> LB round 2)
    UB final  : winners                  (loser -> LB final)
    LB round 1: L1-L2, L3-L4             (losers out)
    LB round 2: LB-R1 winners vs UB-semi losers   (losers out)
    LB round 3: LB-R2 winners             (loser out)
    LB final  : LB-R3 winner vs UB-final loser
    Grand final: UB-final winner vs LB-final winner

The asymmetry is enormous and is the single biggest driver of title odds: an
upper-bracket team needs 3 series wins *with a life to spare*, a lower-bracket
team needs 5 straight wins with none. With eight identical teams this measures
at **P(champion) = 21.8% per UB seat vs 3.2% per LB seat — a 6.9x edge** (the
LB number is just 0.5^5 = 3.1%). Quantify it; never eyeball it.

Strength is expressed as a per-MAP win probability derived from ratings on a
logistic scale; series are converted with the standard binomial.
"""
from __future__ import annotations

from math import comb

import numpy as np
import pandas as pd


def map_prob(r_a: float, r_b: float, scale: float = 400.0) -> float:
    """Per-map win probability from Elo-style ratings."""
    return 1.0 / (1.0 + 10 ** ((r_b - r_a) / scale))


def series_prob(p_map: float, best_of: int) -> float:
    """P(win a BoN series) from a per-map probability (independent maps)."""
    need = best_of // 2 + 1
    return float(sum(comb(best_of, k) * p_map**k * (1 - p_map) ** (best_of - k)
                     for k in range(need, best_of + 1)))


def simulate_main_event(
    ub: list[str],
    lb: list[str],
    ratings: dict[str, float],
    n_sims: int = 100_000,
    rating_sd: float = 0.0,
    bo_ub: int = 3,
    bo_lb: int = 3,
    bo_gf: int = 5,
    seed: int = 21,
) -> pd.DataFrame:
    """P(champion) / P(grand final) / P(top-3) for an 8-team double elim.

    `ub` : the four upper-bracket teams, in bracket order [U1,U2,U3,U4]
           (U1 plays U2, U3 plays U4).
    `lb` : the four lower-bracket teams, in order [L1,L2,L3,L4]
           (L1 plays L2, L3 plays L4).
    `rating_sd` : per-simulation Gaussian noise added to each rating. This is
           the honesty knob — it represents "we do not know true strength this
           precisely" (patch reads, prep, form). 0 = pretend ratings are exact.
    """
    rng = np.random.default_rng(seed)
    teams = list(ub) + list(lb)
    champ = {t: 0 for t in teams}
    gf = {t: 0 for t in teams}
    top3 = {t: 0 for t in teams}

    for _ in range(n_sims):
        r = {t: ratings[t] + (rng.normal(0, rating_sd) if rating_sd else 0.0) for t in teams}

        def play(a: str, b: str, bo: int) -> tuple[str, str]:
            p = series_prob(map_prob(r[a], r[b]), bo)
            return (a, b) if rng.random() < p else (b, a)

        # --- upper bracket
        w1, l1 = play(ub[0], ub[1], bo_ub)
        w2, l2 = play(ub[2], ub[3], bo_ub)
        ubf_w, ubf_l = play(w1, w2, bo_ub)

        # --- lower bracket
        lw1, _ = play(lb[0], lb[1], bo_lb)      # loser eliminated
        lw2, _ = play(lb[2], lb[3], bo_lb)
        lr2a, _ = play(lw1, l2, bo_lb)          # UB losers cross over
        lr2b, _ = play(lw2, l1, bo_lb)
        lr3_w, lr3_l = play(lr2a, lr2b, bo_lb)  # 4th place = lr3_l
        lbf_w, lbf_l = play(lr3_w, ubf_l, bo_lb)  # 3rd place = lbf_l

        # --- grand final
        champion, runner_up = play(ubf_w, lbf_w, bo_gf)

        champ[champion] += 1
        gf[ubf_w] += 1
        gf[lbf_w] += 1
        for t in (champion, runner_up, lbf_l):
            top3[t] += 1

    out = pd.DataFrame({
        "team": teams,
        "start": ["UB"] * 4 + ["LB"] * 4,
        "rating": [ratings[t] for t in teams],
        "p_champion": [champ[t] / n_sims for t in teams],
        "p_grand_final": [gf[t] / n_sims for t in teams],
        "p_top3": [top3[t] / n_sims for t in teams],
    }).sort_values("p_champion", ascending=False).reset_index(drop=True)
    se = np.sqrt(out.p_champion * (1 - out.p_champion) / n_sims)
    out["mc_se"] = se.round(4)
    return out


def simulate_ti15(
    qf: list[tuple[str, str]],
    ratings: dict[str, float],
    n_sims: int = 200_000,
    rating_sd: float = 0.0,
    bo: int = 3,
    bo_gf: int = 5,
    seed: int = 23,
) -> pd.DataFrame:
    """TI-2026 Main Event: 8-team double elim where ALL EIGHT start in the UB.

    Confirmed structure (Aug 20-23): four UB quarter-finals; QF losers form LB
    round 1; 14 series total; everything Bo3 except a Bo5 grand final with no
    upper-bracket advantage.

        UBQF1..4 -> UBSF1 (W1 v W2), UBSF2 (W3 v W4) -> UBF -> GF
        LB R1: L1 v L2, L3 v L4
        LB R2: LB-R1 winners v UBSF losers (cross-seeded to opposite half)
        LB SF -> LB Final (v UBF loser) -> GF

    Because every team starts level, price differences here are *pure strength
    judgments* — unlike a pre-seeded bracket, there is no structural handicap
    to net out. `rating_sd` injects per-sim rating noise for honest CIs.
    """
    rng = np.random.default_rng(seed)
    teams = [t for pair in qf for t in pair]
    champ = {t: 0 for t in teams}
    gf_app = {t: 0 for t in teams}
    top3 = {t: 0 for t in teams}
    top4 = {t: 0 for t in teams}

    for _ in range(n_sims):
        r = {t: ratings[t] + (rng.normal(0, rating_sd) if rating_sd else 0.0) for t in teams}

        def play(a: str, b: str, n: int = bo) -> tuple[str, str]:
            p = series_prob(map_prob(r[a], r[b]), n)
            return (a, b) if rng.random() < p else (b, a)

        # upper bracket
        w1, l1 = play(*qf[0]); w2, l2 = play(*qf[1])
        w3, l3 = play(*qf[2]); w4, l4 = play(*qf[3])
        sw1, sl1 = play(w1, w2)          # UB SF1 (top half)
        sw2, sl2 = play(w3, w4)          # UB SF2 (bottom half)
        ubf_w, ubf_l = play(sw1, sw2)

        # lower bracket
        lb1a, _ = play(l1, l2)           # losers eliminated (7th-8th)
        lb1b, _ = play(l3, l4)
        lb2a, _ = play(lb1a, sl2)        # cross-seed: opposite half's UBSF loser
        lb2b, _ = play(lb1b, sl1)
        lbsf_w, lbsf_l = play(lb2a, lb2b)   # loser = 4th
        lbf_w, lbf_l = play(lbsf_w, ubf_l)  # loser = 3rd

        champion, runner_up = play(ubf_w, lbf_w, bo_gf)
        champ[champion] += 1
        gf_app[ubf_w] += 1; gf_app[lbf_w] += 1
        for t in (champion, runner_up, lbf_l):
            top3[t] += 1
        for t in (champion, runner_up, lbf_l, lbsf_l):
            top4[t] += 1

    out = pd.DataFrame({
        "team": teams,
        "rating": [ratings[t] for t in teams],
        "p_champion": [champ[t] / n_sims for t in teams],
        "p_grand_final": [gf_app[t] / n_sims for t in teams],
        "p_top3": [top3[t] / n_sims for t in teams],
        "p_top4": [top4[t] / n_sims for t in teams],
    }).sort_values("p_champion", ascending=False).reset_index(drop=True)
    out["mc_se"] = np.sqrt(out.p_champion * (1 - out.p_champion) / n_sims).round(4)
    return out


def bracket_advantage(ratings_equal: float = 1500.0, n_sims: int = 60_000) -> pd.DataFrame:
    """How much is an upper-bracket start worth, all else equal?

    Runs the bracket with eight identical teams: any difference in P(champion)
    between UB and LB seats is pure structural advantage.
    """
    teams = [f"T{i}" for i in range(8)]
    r = {t: ratings_equal for t in teams}
    return simulate_main_event(teams[:4], teams[4:], r, n_sims=n_sims)


def implied_ratings_from_prices(prices: dict[str, float], ub: list[str], lb: list[str],
                                scale: float = 400.0, iters: int = 400,
                                lr: float = 60.0, n_sims: int = 20_000) -> dict[str, float]:
    """Fit ratings so the simulated P(champion) reproduces the market prices.

    Lets you read the *market's implied strength ordering* net of bracket
    position — i.e. does the book actually think VISION is the best team, or
    just the best-seeded one? Crude gradient matching; good enough to rank.
    """
    teams = list(ub) + list(lb)
    tot = sum(prices.values())
    target = {t: prices[t] / tot for t in teams}
    r = {t: 1500.0 for t in teams}
    for i in range(iters):
        sim = simulate_main_event(ub, lb, r, n_sims=n_sims, seed=1000 + i)
        cur = dict(zip(sim.team, sim.p_champion))
        for t in teams:
            err = target[t] - cur.get(t, 0.0)
            r[t] += lr * err * 10
        mean = np.mean(list(r.values()))
        r = {t: v - mean + 1500.0 for t, v in r.items()}
    return r
