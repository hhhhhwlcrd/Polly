"""Collect the 2025-26 tier-1 pro-Dota season from OpenDota into parquet files.

Outputs (ti2026/data/):
  leagues.parquet        one row per selected league
  matches.parquet        one row per match (result, duration, sides, league, patch)
  match_players.parquet  ten rows per match (per-player performance)
  picks_bans.parquet     draft rows per match
  teams.parquet          team metadata + OpenDota rating

Run:  python -m src.collect_data [--since 2025-09-01] [--max-matches N]
Volume: a tier-1 season is roughly 1,500-3,000 matches; at the keyless ~1.1s/call
budget the detailed pull takes 30-90 min on first run (then fully cached).
"""
from __future__ import annotations

import argparse
import datetime as dt
import re
import sys
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from src.opendota import DATA_DIR, OpenDota, OpenDotaError

# Name patterns for the 2025-26 tier-1 circuit. Extend as events are announced.
# Verified league ids (fallback if name matching misses; source: dotabuff slugs)
KNOWN_LEAGUE_IDS = {
    18324: "The International 2025",
    18988: "DreamLeague Season 27",
    19269: "DreamLeague Season 28",
    19696: "DreamLeague Season 29",
    19435: "PGL Wallachia Season 7",
}

TIER1_PATTERNS = [
    r"The International",
    r"DreamLeague Season \d+",
    r"ESL One",
    r"BLAST Slam",
    r"PGL Wallachia",
    r"FISSURE (Universe|Playground)",
    r"Esports World Cup",
    r"Games of the Future",
    r"1win Series",  # keep loose: filter later by prize/teams if noisy
]


def select_leagues(od: OpenDota, since: dt.date) -> pd.DataFrame:
    leagues = pd.DataFrame(od.leagues())
    pat = re.compile("|".join(TIER1_PATTERNS), re.IGNORECASE)
    sel = leagues[leagues["name"].fillna("").str.contains(pat)]
    # OpenDota /leagues has no dates; filter by matches later. Premium tier only.
    if "tier" in sel.columns:
        sel = sel[sel["tier"].isin(["premium", "professional"])]
    return sel.reset_index(drop=True)


def flatten_match(m: dict) -> tuple[dict, list[dict], list[dict]]:
    row = {
        "match_id": m["match_id"],
        "league_id": (m.get("league") or {}).get("leagueid") or m.get("leagueid"),
        "league_name": (m.get("league") or {}).get("name"),
        "start_time": m.get("start_time"),
        "duration": m.get("duration"),
        "radiant_team_id": m.get("radiant_team_id"),
        "dire_team_id": m.get("dire_team_id"),
        "radiant_name": (m.get("radiant_team") or {}).get("name"),
        "dire_name": (m.get("dire_team") or {}).get("name"),
        "radiant_win": m.get("radiant_win"),
        "radiant_score": m.get("radiant_score"),
        "dire_score": m.get("dire_score"),
        "patch": m.get("patch"),
        "series_id": m.get("series_id"),
        "series_type": m.get("series_type"),  # 0=BO1 1=BO3 2=BO5
        "first_blood_time": m.get("first_blood_time"),
    }
    # 10-min gold advantage if the replay was parsed
    adv = m.get("radiant_gold_adv") or []
    row["gold_adv_10"] = adv[10] if len(adv) > 10 else None
    row["gold_adv_20"] = adv[20] if len(adv) > 20 else None

    players = []
    for p in m.get("players", []):
        players.append(
            {
                "match_id": m["match_id"],
                "account_id": p.get("account_id"),
                "name": p.get("name") or p.get("personaname"),
                "team_id": row["radiant_team_id"] if p.get("isRadiant") else row["dire_team_id"],
                "is_radiant": p.get("isRadiant"),
                "win": p.get("win"),
                "hero_id": p.get("hero_id"),
                "lane": p.get("lane"),  # 1 safe, 2 mid, 3 off, 4 jungle (parsed only)
                "lane_role": p.get("lane_role"),  # 1 carry, 2 mid, 3 off, 4 support
                "lane_efficiency": p.get("lane_efficiency"),
                "kills": p.get("kills"),
                "deaths": p.get("deaths"),
                "assists": p.get("assists"),
                "gold_per_min": p.get("gold_per_min"),
                "xp_per_min": p.get("xp_per_min"),
                "last_hits": p.get("last_hits"),
                "denies": p.get("denies"),
                "hero_damage": p.get("hero_damage"),
                "tower_damage": p.get("tower_damage"),
                "hero_healing": p.get("hero_healing"),
                "net_worth": p.get("net_worth"),
                "obs_placed": p.get("obs_placed"),
                "sen_placed": p.get("sen_placed"),
                "stuns": p.get("stuns"),
                "teamfight_participation": p.get("teamfight_participation"),
            }
        )
    picks = [
        {
            "match_id": m["match_id"],
            "is_pick": pb.get("is_pick"),
            "hero_id": pb.get("hero_id"),
            "team": pb.get("team"),  # 0 radiant, 1 dire
            "order": pb.get("order"),
        }
        for pb in (m.get("picks_bans") or [])
    ]
    return row, players, picks


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--since", default="2025-09-01")
    ap.add_argument("--max-matches", type=int, default=None)
    args = ap.parse_args()
    since_ts = int(dt.datetime.fromisoformat(args.since).timestamp())

    od = OpenDota()
    DATA_DIR.mkdir(parents=True, exist_ok=True)

    leagues = select_leagues(od, dt.date.fromisoformat(args.since))
    print(f"Selected {len(leagues)} candidate tier-1 leagues")

    match_ids: list[int] = []
    league_rows = []
    for _, lg in leagues.iterrows():
        try:
            ms = od.league_matches(int(lg["leagueid"]))
        except OpenDotaError as e:
            print(f"  ! league {lg['name']}: {e}")
            continue
        recent = [m for m in ms if (m.get("start_time") or 0) >= since_ts]
        if recent:
            league_rows.append({**lg.to_dict(), "n_matches": len(recent)})
            match_ids += [m["match_id"] for m in recent]
            print(f"  {lg['name']}: {len(recent)} matches")
    match_ids = sorted(set(match_ids), reverse=True)
    if args.max_matches:
        match_ids = match_ids[: args.max_matches]
    print(f"Total unique matches to fetch: {len(match_ids)}")

    rows, prows, pbrows, failed = [], [], [], []
    for i, mid in enumerate(match_ids, 1):
        try:
            m = od.match(mid)
        except OpenDotaError as e:
            failed.append(mid)
            print(f"  ! match {mid}: {e}")
            if len(failed) > 25:
                print("Too many failures - aborting (partial data is cached).")
                break
            continue
        r, ps, pbs = flatten_match(m)
        rows.append(r)
        prows += ps
        pbrows += pbs
        if i % 100 == 0:
            print(f"  {i}/{len(match_ids)} matches")

    pd.DataFrame(league_rows).to_parquet(DATA_DIR / "leagues.parquet")
    pd.DataFrame(rows).to_parquet(DATA_DIR / "matches.parquet")
    pd.DataFrame(prows).to_parquet(DATA_DIR / "match_players.parquet")
    pd.DataFrame(pbrows).to_parquet(DATA_DIR / "picks_bans.parquet")
    try:
        pd.DataFrame(od.teams()).to_parquet(DATA_DIR / "teams.parquet")
    except OpenDotaError as e:
        print(f"! teams pull failed: {e}")
    print(
        f"Done: {len(rows)} matches, {len(prows)} player rows, "
        f"{len(pbrows)} draft rows, {len(failed)} failures."
    )


if __name__ == "__main__":
    main()
