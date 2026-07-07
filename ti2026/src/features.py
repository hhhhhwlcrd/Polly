"""Feature engineering shared by the ti2026 notebooks.

All functions take the parquet frames produced by src.collect_data and return
tidy per-player / per-team feature tables. Kept dependency-light (pandas+numpy).
"""
from __future__ import annotations

import numpy as np
import pandas as pd

CORE_ROLES = {1: "carry", 2: "mid", 3: "offlane", 4: "soft_support", 5: "hard_support"}


def infer_role(g: pd.DataFrame) -> pd.Series:
    """Rough position inference: rank by GPM within team-match (1=carry...5=hs).

    lane_role covers laning only; economy rank is the standard proxy for
    position 1-5. Good enough for aggregate skill/econ profiling.
    """
    r = g.groupby(["match_id", "team_id"])["gold_per_min"].rank(
        ascending=False, method="first"
    )
    return r.map(lambda x: CORE_ROLES.get(int(x), "unknown"))


def player_features(mp: pd.DataFrame, matches: pd.DataFrame, min_games: int = 8) -> pd.DataFrame:
    df = mp.merge(
        matches[["match_id", "start_time", "duration", "patch"]], on="match_id"
    )
    df = df[df["account_id"].notna()].copy()
    df["role"] = infer_role(df)
    df["kda"] = (df["kills"] + df["assists"]) / df["deaths"].clip(lower=1)
    df["gpm_share"] = df["gold_per_min"] / df.groupby(["match_id", "team_id"])[
        "gold_per_min"
    ].transform("sum")

    g = df.groupby(["account_id", "name"], dropna=False)
    out = pd.DataFrame(
        {
            "games": g.size(),
            "winrate": g["win"].mean(),
            "primary_role": g["role"].agg(lambda s: s.mode().iat[0] if len(s.mode()) else "unknown"),
            "gpm_mean": g["gold_per_min"].mean(),
            "xpm_mean": g["xp_per_min"].mean(),
            "kda_mean": g["kda"].mean(),
            "lane_eff_mean": g["lane_efficiency"].mean(),
            "gpm_share_mean": g["gpm_share"].mean(),
            "tf_participation": g["teamfight_participation"].mean(),
            "obs_per_game": g["obs_placed"].mean(),
            # hero pool: breadth and concentration
            "hero_pool": g["hero_id"].nunique(),
            "hero_hhi": g["hero_id"].agg(
                lambda s: float(((s.value_counts() / len(s)) ** 2).sum())
            ),
        }
    ).reset_index()
    out["hero_pool_per_game"] = out["hero_pool"] / out["games"]
    return out[out["games"] >= min_games].sort_values("games", ascending=False)


def team_features(mp: pd.DataFrame, matches: pd.DataFrame, min_games: int = 10) -> pd.DataFrame:
    m = matches.dropna(subset=["radiant_team_id", "dire_team_id"]).copy()
    long = pd.concat(
        [
            m.assign(team_id=m.radiant_team_id, opp_id=m.dire_team_id,
                     win=m.radiant_win, is_radiant=True,
                     gold10=m.gold_adv_10, gold20=m.gold_adv_20),
            m.assign(team_id=m.dire_team_id, opp_id=m.radiant_team_id,
                     win=~m.radiant_win.astype(bool), is_radiant=False,
                     gold10=-m.gold_adv_10, gold20=-m.gold_adv_20),
        ]
    )
    long["behind_at_20"] = long["gold20"] < -3000
    long["comeback_win"] = long["behind_at_20"] & long["win"].astype(bool)
    long["ahead_at_20"] = long["gold20"] > 3000
    long["throw_loss"] = long["ahead_at_20"] & ~long["win"].astype(bool)

    g = long.groupby("team_id")
    out = pd.DataFrame(
        {
            "games": g.size(),
            "winrate": g["win"].mean(),
            "radiant_share": g["is_radiant"].mean(),
            "avg_duration": g["duration"].mean(),
            "gold10_mean": g["gold10"].mean(),          # lane-phase strength
            "gold20_mean": g["gold20"].mean(),
            "comeback_rate": g["comeback_win"].sum() / g["behind_at_20"].sum(),
            "throw_rate": g["throw_loss"].sum() / g["ahead_at_20"].sum(),
            "last_played": g["start_time"].max(),
        }
    ).reset_index()

    # draft diversity from picks
    return out[out["games"] >= min_games]


def draft_features(pb: pd.DataFrame, matches: pd.DataFrame) -> pd.DataFrame:
    picks = pb[pb["is_pick"] == True].merge(  # noqa: E712
        matches[["match_id", "radiant_team_id", "dire_team_id"]], on="match_id"
    )
    picks["team_id"] = np.where(
        picks["team"] == 0, picks["radiant_team_id"], picks["dire_team_id"]
    )
    g = picks.groupby("team_id")["hero_id"]
    return pd.DataFrame(
        {
            "picked_heroes": g.nunique(),
            "picks": g.size(),
            "draft_hhi": g.agg(lambda s: float(((s.value_counts() / len(s)) ** 2).sum())),
        }
    ).reset_index()
