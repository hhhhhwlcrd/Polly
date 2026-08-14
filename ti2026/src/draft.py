"""Draft, ban and hero-meta analysis for pro Dota 2 (ti2026).

Consumes the `picks_bans` parquet (one row per draft action) plus match and
player tables. Produces:

  ban_table        — most-banned heroes with first-phase share
  contest_table    — contest rate = (picks + bans) / games, the real measure
                     of how the meta values a hero
  team_draft_style — per-team hero diversity, comfort concentration, and
                     first-phase ban tendencies
  player_hero_pool — per-player pool breadth / depth and signature heroes
  meta_shift       — hero priority delta between two patches (what the
                     pre-TI patch changed), the single biggest form-invalidator

The ban table is also the input to `derivatives.most_banned_hero_market`,
which prices the Polymarket "Most Banned Hero at TI 2026" book.
"""
from __future__ import annotations

import numpy as np
import pandas as pd

# Captains Mode 7.3x+ : 14 bans per game (7 per side) across three phases.
BANS_PER_GAME = 14
FIRST_PHASE_ORDERS = {0, 1, 2, 3}  # opening bans carry the highest priority signal


def _hero_names(heroes: pd.DataFrame | None) -> dict:
    if heroes is None or not len(heroes):
        return {}
    col = "localized_name" if "localized_name" in heroes.columns else "name"
    return dict(zip(heroes["id"], heroes[col]))


def ban_table(picks_bans: pd.DataFrame, heroes: pd.DataFrame | None = None,
              matches: pd.DataFrame | None = None) -> pd.DataFrame:
    """Ban counts per hero, with first-phase share and per-game rate."""
    pb = picks_bans.copy()
    bans = pb[pb["is_pick"] == False]  # noqa: E712
    n_games = pb["match_id"].nunique() or 1
    g = bans.groupby("hero_id")
    out = pd.DataFrame({
        "bans": g.size(),
        "first_phase_bans": g["order"].apply(lambda s: s.isin(FIRST_PHASE_ORDERS).sum()),
        "mean_ban_order": g["order"].mean(),
    }).reset_index()
    out["ban_rate"] = out["bans"] / n_games
    out["first_phase_share"] = out["first_phase_bans"] / out["bans"].clip(lower=1)
    names = _hero_names(heroes)
    if names:
        out["hero"] = out["hero_id"].map(names)
    return out.sort_values("bans", ascending=False).reset_index(drop=True)


def contest_table(picks_bans: pd.DataFrame, heroes: pd.DataFrame | None = None) -> pd.DataFrame:
    """Contest rate = (picks + bans) / games. 1.0 means the hero is taken
    off the board every single game — the true 'meta tyrant' signal."""
    pb = picks_bans.copy()
    n_games = pb["match_id"].nunique() or 1
    g = pb.groupby("hero_id")
    out = pd.DataFrame({
        "picks": g["is_pick"].sum(),
        "actions": g.size(),
    }).reset_index()
    out["bans"] = out["actions"] - out["picks"]
    out["contest_rate"] = out["actions"] / n_games
    out["pick_ban_ratio"] = out["picks"] / out["actions"].clip(lower=1)
    names = _hero_names(heroes)
    if names:
        out["hero"] = out["hero_id"].map(names)
    return out.sort_values("contest_rate", ascending=False).reset_index(drop=True)


def hero_winrates(picks_bans: pd.DataFrame, matches: pd.DataFrame,
                  heroes: pd.DataFrame | None = None, min_picks: int = 5) -> pd.DataFrame:
    """Win rate of each *picked* hero (draft-side attribution, no player data)."""
    picks = picks_bans[picks_bans["is_pick"] == True].merge(  # noqa: E712
        matches[["match_id", "radiant_win"]], on="match_id", how="inner")
    # picks_bans.team: 0 = radiant, 1 = dire
    picks["won"] = np.where(picks["team"] == 0, picks["radiant_win"], ~picks["radiant_win"].astype(bool))
    g = picks.groupby("hero_id")
    out = pd.DataFrame({"picks": g.size(), "winrate": g["won"].mean()}).reset_index()
    names = _hero_names(heroes)
    if names:
        out["hero"] = out["hero_id"].map(names)
    return out[out["picks"] >= min_picks].sort_values("winrate", ascending=False)


def team_draft_style(picks_bans: pd.DataFrame, matches: pd.DataFrame,
                     teams: pd.DataFrame | None = None) -> pd.DataFrame:
    """Per-team draft signature: hero diversity, concentration, ban discipline."""
    pb = picks_bans.merge(
        matches[["match_id", "radiant_team_id", "dire_team_id"]], on="match_id", how="inner")
    pb["team_id"] = np.where(pb["team"] == 0, pb["radiant_team_id"], pb["dire_team_id"])
    pb = pb.dropna(subset=["team_id"])

    picks = pb[pb["is_pick"] == True]  # noqa: E712
    bans = pb[pb["is_pick"] == False]  # noqa: E712

    gp = picks.groupby("team_id")["hero_id"]
    style = pd.DataFrame({
        "unique_picked": gp.nunique(),
        "total_picks": gp.size(),
        # HHI: low = wide, unpredictable pool; high = few comfort heroes
        "pick_hhi": gp.apply(lambda s: float(((s.value_counts() / len(s)) ** 2).sum())),
    })
    gb = bans.groupby("team_id")["hero_id"]
    style["unique_banned"] = gb.nunique()
    style["ban_hhi"] = gb.apply(lambda s: float(((s.value_counts() / len(s)) ** 2).sum()))
    style["pool_per_game"] = style["unique_picked"] / (style["total_picks"] / 5).clip(lower=1)
    style = style.reset_index()
    if teams is not None and len(teams):
        style = style.merge(teams[["team_id", "name"]], on="team_id", how="left")
    return style.sort_values("unique_picked", ascending=False)


def player_hero_pool(match_players: pd.DataFrame, heroes: pd.DataFrame | None = None,
                     min_games: int = 8) -> pd.DataFrame:
    """Per-player pool breadth, concentration and signature heroes."""
    mp = match_players[match_players["account_id"].notna()].copy()
    g = mp.groupby(["account_id", "name"], dropna=False)
    out = pd.DataFrame({
        "games": g.size(),
        "winrate": g["win"].mean(),
        "pool": g["hero_id"].nunique(),
        "hero_hhi": g["hero_id"].apply(lambda s: float(((s.value_counts() / len(s)) ** 2).sum())),
    }).reset_index()
    out["pool_per_game"] = out["pool"] / out["games"]
    names = _hero_names(heroes)
    sig = (mp.groupby(["account_id", "hero_id"]).size().rename("n").reset_index()
             .sort_values("n", ascending=False).groupby("account_id").head(3))
    if names:
        sig["hero"] = sig["hero_id"].map(names)
        top = sig.groupby("account_id")["hero"].apply(lambda s: ", ".join(map(str, s)))
        out = out.merge(top.rename("signature"), on="account_id", how="left")
    return out[out["games"] >= min_games].sort_values("games", ascending=False)


def meta_shift(picks_bans: pd.DataFrame, matches: pd.DataFrame,
               patch_a: int, patch_b: int, heroes: pd.DataFrame | None = None,
               top_n: int = 20) -> pd.DataFrame:
    """Change in hero contest rate between two patches.

    Use this the moment a pre-TI patch lands: heroes whose contest rate jumps
    are the new meta, and every pre-patch team profile built on the old meta
    is correspondingly stale (widen your model's uncertainty).
    """
    pb = picks_bans.merge(matches[["match_id", "patch"]], on="match_id", how="inner")
    frames = {}
    for tag, patch in (("a", patch_a), ("b", patch_b)):
        sub = pb[pb["patch"] == patch]
        n = sub["match_id"].nunique() or 1
        frames[tag] = (sub.groupby("hero_id").size() / n).rename(f"contest_{tag}")
    out = pd.concat(frames.values(), axis=1).fillna(0.0).reset_index()
    out["delta"] = out[f"contest_b"] - out[f"contest_a"]
    names = _hero_names(heroes)
    if names:
        out["hero"] = out["hero_id"].map(names)
    return pd.concat([out.nlargest(top_n, "delta"), out.nsmallest(top_n, "delta")])
