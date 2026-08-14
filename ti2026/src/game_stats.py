"""Deep game-statistics features for pro Dota 2 matches (ti2026).

Consumes the parquet tables written by src.collect_data (which now stores
timelines, objectives and teamfights) and produces per-team *style* profiles:

  economy timing   — gold/xp advantage at minutes 10/15/20/25/30/40
  laning           — per-lane win rates and lane-efficiency by role
  objectives       — first-tower/roshan control, tower & barracks pace
  teamfighting     — fight frequency, participation, net gold swing per fight
  pace & closing   — kills/min, duration profile, comeback/throw conversion
  side             — radiant vs dire split (feeds the Radiant/Dire derivative)

Everything is opponent-agnostic by default; call `opponent_adjust()` to
regress a metric against opposition strength (Elo) so that a team farming
weak opponents is not mistaken for a strong one.
"""
from __future__ import annotations

import numpy as np
import pandas as pd

KEY_MINUTES = (10, 15, 20, 25, 30, 40)

# OpenDota objective `type` strings
OBJ_TOWER = "CHAT_MESSAGE_TOWER_KILL"
OBJ_ROSHAN = "CHAT_MESSAGE_ROSHAN_KILL"
OBJ_FIRSTBLOOD = "CHAT_MESSAGE_FIRSTBLOOD"
OBJ_BARRACKS = "CHAT_MESSAGE_BARRACKS_KILL"
OBJ_AEGIS = "CHAT_MESSAGE_AEGIS"


# ---------------------------------------------------------------- helpers
def to_team_long(matches: pd.DataFrame) -> pd.DataFrame:
    """One row per (match, team) with the match viewed from that team's side."""
    m = matches.dropna(subset=["radiant_team_id", "dire_team_id"]).copy()
    m["radiant_win"] = m["radiant_win"].astype(bool)
    rad = m.assign(
        team_id=m.radiant_team_id, opp_id=m.dire_team_id,
        is_radiant=True, win=m.radiant_win, sign=1,
    )
    dire = m.assign(
        team_id=m.dire_team_id, opp_id=m.radiant_team_id,
        is_radiant=False, win=~m.radiant_win, sign=-1,
    )
    return pd.concat([rad, dire], ignore_index=True)


def _series_from_timeline(col: pd.Series, minute: int) -> pd.Series:
    """Element `minute` of a per-minute array column, NaN when the game was
    shorter or the replay was never parsed."""
    return col.map(
        lambda a: (a[minute] if isinstance(a, (list, np.ndarray)) and len(a) > minute else np.nan)
    )


# ---------------------------------------------------------------- economy
def timing_features(matches: pd.DataFrame) -> pd.DataFrame:
    """Mean gold/xp advantage per team at each key minute → timing profile.

    Positive `gold_adv_20` means the team is typically ahead by 20 minutes
    (tempo/early team); teams with a negative early number but a positive
    late number are scaling/late-game teams.
    """
    long = to_team_long(matches)
    out = {}
    for mnt in KEY_MINUTES:
        gcol, xcol = f"gold_adv_{mnt}", f"xp_adv_{mnt}"
        if gcol not in long.columns:  # rebuild from raw timeline if present
            if "radiant_gold_adv" in long.columns:
                long[gcol] = _series_from_timeline(long["radiant_gold_adv"], mnt) * long["sign"]
            else:
                continue
        else:
            long[gcol] = long[gcol] * long["sign"]
        if xcol in long.columns:
            long[xcol] = long[xcol] * long["sign"]
        elif "radiant_xp_adv" in long.columns:
            long[xcol] = _series_from_timeline(long["radiant_xp_adv"], mnt) * long["sign"]
        out[gcol] = long.groupby("team_id")[gcol].mean()
        if xcol in long.columns:
            out[xcol] = long.groupby("team_id")[xcol].mean()

    df = pd.DataFrame(out)
    if {"gold_adv_10", "gold_adv_30"} <= set(df.columns):
        # >0 → the team grows its lead as the game goes (scaling drafts)
        df["scaling_slope"] = (df["gold_adv_30"] - df["gold_adv_10"]) / 20.0
    return df.reset_index().rename(columns={"index": "team_id"})


# ---------------------------------------------------------------- laning
def lane_features(match_players: pd.DataFrame, matches: pd.DataFrame) -> pd.DataFrame:
    """Lane-phase strength per team, split by lane role.

    `lane_efficiency` is OpenDota's parsed laning metric; we also derive a
    head-to-head lane win rate by comparing the two teams' role-matched
    10-minute net worth where the timeline is available.
    """
    mp = match_players.merge(
        matches[["match_id", "radiant_team_id", "dire_team_id", "radiant_win"]],
        on="match_id", how="inner",
    )
    mp = mp[mp["team_id"].notna()].copy()
    mp["role_name"] = mp["lane_role"].map({1: "safe", 2: "mid", 3: "off", 4: "jungle"})

    g = mp.groupby(["team_id", "role_name"])
    tbl = g.agg(
        lane_eff=("lane_efficiency", "mean"),
        gpm=("gold_per_min", "mean"),
        xpm=("xp_per_min", "mean"),
        n=("match_id", "size"),
    ).reset_index()
    wide = tbl.pivot(index="team_id", columns="role_name",
                     values=["lane_eff", "gpm"])
    wide.columns = [f"{a}_{b}" for a, b in wide.columns]
    return wide.reset_index()


# ------------------------------------------------------------ objectives
def objective_features(matches: pd.DataFrame) -> pd.DataFrame:
    """First-tower rate, roshan share, tower/barracks pace from `objectives`.

    `objectives` is a list-of-dicts column (JSON) written by collect_data.
    Radiant is team 2, Dire is team 3 in OpenDota's objective `team` field.
    """
    if "objectives" not in matches.columns:
        return pd.DataFrame(columns=["team_id"])

    rows = []
    for r in matches.dropna(subset=["radiant_team_id", "dire_team_id"]).itertuples():
        objs = r.objectives
        if not isinstance(objs, (list, np.ndarray)) or len(objs) == 0:
            continue
        rad, dire = int(r.radiant_team_id), int(r.dire_team_id)
        acc = {rad: dict(tower=0, rosh=0, rax=0, first_tower=0),
               dire: dict(tower=0, rosh=0, rax=0, first_tower=0)}
        first_tower_seen = False
        first_tower_time = np.nan
        for o in objs:
            typ = o.get("type")
            # objective `team`: 2 = radiant, 3 = dire
            tm = {2: rad, 3: dire}.get(o.get("team"))
            if typ == OBJ_TOWER:
                if tm is None:
                    # tower kills sometimes only carry player_slot
                    ps = o.get("player_slot")
                    tm = rad if (ps is not None and ps < 128) else dire
                acc[tm]["tower"] += 1
                if not first_tower_seen:
                    acc[tm]["first_tower"] = 1
                    first_tower_time = o.get("time", np.nan)
                    first_tower_seen = True
            elif typ == OBJ_ROSHAN:
                ps = o.get("player_slot")
                tm = rad if (ps is not None and ps < 128) else dire
                acc[tm]["rosh"] += 1
            elif typ == OBJ_BARRACKS:
                if tm is not None:
                    acc[tm]["rax"] += 1
        dur_min = max((r.duration or 0) / 60.0, 1e-6)
        for tm, a in acc.items():
            rows.append({
                "team_id": tm, "match_id": r.match_id,
                "towers": a["tower"], "towers_per_min": a["tower"] / dur_min,
                "roshans": a["rosh"], "barracks": a["rax"],
                "first_tower": a["first_tower"], "first_tower_time": first_tower_time,
            })
    if not rows:
        return pd.DataFrame(columns=["team_id"])
    df = pd.DataFrame(rows)
    return df.groupby("team_id").agg(
        towers_pg=("towers", "mean"),
        towers_per_min=("towers_per_min", "mean"),
        roshans_pg=("roshans", "mean"),
        barracks_pg=("barracks", "mean"),
        first_tower_rate=("first_tower", "mean"),
        first_tower_time=("first_tower_time", "mean"),
        n_obj_games=("match_id", "size"),
    ).reset_index()


# ----------------------------------------------------------- teamfights
def teamfight_features(matches: pd.DataFrame) -> pd.DataFrame:
    """Fight frequency and net gold swing per fight, per team."""
    if "teamfights" not in matches.columns:
        return pd.DataFrame(columns=["team_id"])
    rows = []
    for r in matches.dropna(subset=["radiant_team_id", "dire_team_id"]).itertuples():
        tfs = r.teamfights
        if not isinstance(tfs, (list, np.ndarray)) or len(tfs) == 0:
            continue
        rad, dire = int(r.radiant_team_id), int(r.dire_team_id)
        n_fights = len(tfs)
        rad_gold = dire_gold = 0.0
        rad_deaths = dire_deaths = 0
        for tf in tfs:
            for i, p in enumerate(tf.get("players", []) or []):
                gd = p.get("gold_delta") or 0
                dth = p.get("deaths") or 0
                if i < 5:
                    rad_gold += gd
                    rad_deaths += dth
                else:
                    dire_gold += gd
                    dire_deaths += dth
        dur_min = max((r.duration or 0) / 60.0, 1e-6)
        rows += [
            {"team_id": rad, "fights_per_min": n_fights / dur_min,
             "fight_gold_swing": (rad_gold - dire_gold) / n_fights,
             "fight_death_diff": (dire_deaths - rad_deaths) / n_fights},
            {"team_id": dire, "fights_per_min": n_fights / dur_min,
             "fight_gold_swing": (dire_gold - rad_gold) / n_fights,
             "fight_death_diff": (rad_deaths - dire_deaths) / n_fights},
        ]
    if not rows:
        return pd.DataFrame(columns=["team_id"])
    return pd.DataFrame(rows).groupby("team_id").mean().reset_index()


# ------------------------------------------------------ pace / closing
def pace_features(matches: pd.DataFrame) -> pd.DataFrame:
    long = to_team_long(matches)
    long["kills"] = np.where(long.is_radiant, long.radiant_score, long.dire_score)
    long["deaths"] = np.where(long.is_radiant, long.dire_score, long.radiant_score)
    long["dur_min"] = long["duration"] / 60.0
    long["kpm"] = (long.kills + long.deaths) / long.dur_min.clip(lower=1e-6)

    g20 = "gold_adv_20"
    if g20 in long.columns:
        adv = long[g20] * long["sign"]
        long["ahead20"] = adv > 3000
        long["behind20"] = adv < -3000
    else:
        long["ahead20"] = long["behind20"] = False

    g = long.groupby("team_id")
    out = pd.DataFrame({
        "games": g.size(),
        "winrate": g["win"].mean(),
        "avg_duration_min": g["dur_min"].mean(),
        "kills_pg": g["kills"].mean(),
        "combined_kpm": g["kpm"].mean(),
        "radiant_winrate": g.apply(
            lambda d: d.loc[d.is_radiant, "win"].mean() if d.is_radiant.any() else np.nan,
            include_groups=False),
        "dire_winrate": g.apply(
            lambda d: d.loc[~d.is_radiant, "win"].mean() if (~d.is_radiant).any() else np.nan,
            include_groups=False),
    })
    # conversion: do they close leads / come back?
    conv = long.groupby("team_id").apply(
        lambda d: pd.Series({
            "close_rate": d.loc[d.ahead20, "win"].mean() if d.ahead20.any() else np.nan,
            "comeback_rate": d.loc[d.behind20, "win"].mean() if d.behind20.any() else np.nan,
        }), include_groups=False)
    return out.join(conv).reset_index()


# ------------------------------------------------- opponent adjustment
def opponent_adjust(long: pd.DataFrame, metric: str, elo: pd.Series) -> pd.DataFrame:
    """Residualise a per-game metric against opponent Elo.

    Returns per-team mean residual: 'how much better than expected given who
    they played'. Guards against the classic trap of rating a team highly
    because its schedule was soft.
    """
    d = long[["team_id", "opp_id", metric]].dropna().copy()
    d["opp_elo"] = d["opp_id"].map(elo)
    d = d.dropna(subset=["opp_elo"])
    if len(d) < 20:
        return pd.DataFrame(columns=["team_id", f"{metric}_adj"])
    x = d["opp_elo"].to_numpy()
    y = d[metric].to_numpy()
    b, a = np.polyfit(x, y, 1)
    d[f"{metric}_adj"] = y - (a + b * x)
    return d.groupby("team_id")[f"{metric}_adj"].mean().reset_index()


# ------------------------------------------------------------- assembly
def team_style_profile(matches: pd.DataFrame, match_players: pd.DataFrame,
                       teams: pd.DataFrame | None = None) -> pd.DataFrame:
    """Join every block above into one row per team — the model's feature row."""
    parts = [
        pace_features(matches),
        timing_features(matches),
        objective_features(matches),
        teamfight_features(matches),
        lane_features(match_players, matches),
    ]
    out = parts[0]
    for p in parts[1:]:
        if len(p) and "team_id" in p.columns:
            out = out.merge(p, on="team_id", how="left")
    if teams is not None and len(teams):
        out = out.merge(teams[["team_id", "name"]], on="team_id", how="left")
    return out.sort_values("games", ascending=False)
