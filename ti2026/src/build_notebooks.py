"""Generate the ti2026 analysis notebooks (plain-JSON .ipynb, no nbformat dep).

Run:  python src/build_notebooks.py   (from ti2026/)
"""
from __future__ import annotations

import json
from pathlib import Path

NB_DIR = Path(__file__).resolve().parent.parent / "notebooks"


def nb(cells):
    return {
        "cells": cells,
        "metadata": {
            "kernelspec": {"display_name": "Python 3", "language": "python", "name": "python3"},
            "language_info": {"name": "python", "version": "3.11"},
        },
        "nbformat": 4,
        "nbformat_minor": 5,
    }


def md(src):
    return {"cell_type": "markdown", "metadata": {}, "source": src.splitlines(keepends=True)}


def code(src):
    return {
        "cell_type": "code",
        "execution_count": None,
        "metadata": {},
        "outputs": [],
        "source": src.splitlines(keepends=True),
    }


SETUP = """\
import sys, pathlib
ROOT = pathlib.Path.cwd().parent if pathlib.Path.cwd().name == 'notebooks' else pathlib.Path.cwd()
sys.path.insert(0, str(ROOT))
import pandas as pd, numpy as np
pd.set_option('display.max_columns', 60); pd.set_option('display.width', 160)
DATA = ROOT / 'data'
"""

# ----------------------------------------------------------------- 01
nb01 = nb(
    [
        md(
            "# 01 — Data collection: 2025-26 tier-1 pro season from OpenDota\n"
            "\n"
            "Downloads detailed stats for every match of the tier-1 circuit since TI 2025\n"
            "(leagues matched by name pattern — see `src/collect_data.py:TIER1_PATTERNS`).\n"
            "\n"
            "**Requirements:** network access to `api.opendota.com` (keyless ≈60 req/min;\n"
            "set `OPENDOTA_API_KEY` to go faster). First full pull ≈ 30–90 min; everything\n"
            "is disk-cached under `data/cache/`, so re-runs are instant and offline-safe.\n"
            "If this sandbox blocks OpenDota, run this notebook locally once — the other\n"
            "notebooks only need the parquet files it produces."
        ),
        code(SETUP),
        code(
            "# Pull (or refresh) the season. Tune --since / --max-matches as needed.\n"
            "from src.collect_data import main as collect\n"
            "import sys\n"
            "sys.argv = ['collect', '--since', '2025-09-01']\n"
            "try:\n"
            "    collect()\n"
            "except Exception as e:\n"
            "    print(f'Collection failed ({e}).\\nFalling back to any existing parquet in data/.')"
        ),
        code(
            "matches = pd.read_parquet(DATA / 'matches.parquet')\n"
            "players = pd.read_parquet(DATA / 'match_players.parquet')\n"
            "picks   = pd.read_parquet(DATA / 'picks_bans.parquet')\n"
            "print(f'{len(matches):,} matches | {len(players):,} player rows | {len(picks):,} draft rows')\n"
            "matches['date'] = pd.to_datetime(matches.start_time, unit='s')\n"
            "matches.groupby('league_name').agg(n=('match_id','size'), first=('date','min'), last=('date','max')).sort_values('last')"
        ),
        code(
            "# Sanity: patch coverage and parsed-replay coverage (gold_adv present)\n"
            "print(matches.patch.value_counts().sort_index())\n"
            "print(f\"parsed replays: {matches.gold_adv_10.notna().mean():.0%}\")\n"
            "matches.sample(3)"
        ),
    ]
)

# ----------------------------------------------------------------- 02
nb02 = nb(
    [
        md(
            "# 02 — Player performance: skill, economics, hero pool\n"
            "\n"
            "Per-player profile over the tier-1 season: win rate, KDA, GPM/XPM (economy),\n"
            "lane efficiency, teamfight participation, vision, and hero-pool breadth\n"
            "(`hero_pool`, plus HHI concentration — low HHI = wide comfort pool).\n"
            "Roles are inferred from within-team economy rank (1=carry … 5=hard support)."
        ),
        code(SETUP),
        code(
            "from src.features import player_features\n"
            "matches = pd.read_parquet(DATA / 'matches.parquet')\n"
            "mp = pd.read_parquet(DATA / 'match_players.parquet')\n"
            "pf = player_features(mp, matches, min_games=8)\n"
            "print(f'{len(pf)} players with >=8 tier-1 games')\n"
            "pf.head(10)"
        ),
        code(
            "# Top players by role: economy vs impact\n"
            "for role in ['carry','mid','offlane','soft_support','hard_support']:\n"
            "    top = pf[pf.primary_role==role].nlargest(8,'winrate')\n"
            "    print(f'\\n== {role} (top-8 by winrate) ==')\n"
            "    print(top[['name','games','winrate','gpm_mean','xpm_mean','kda_mean','hero_pool','hero_hhi']].to_string(index=False))"
        ),
        code(
            "# Hero-pool breadth vs winrate — is versatility rewarded this season?\n"
            "import matplotlib.pyplot as plt\n"
            "fig, ax = plt.subplots(1, 2, figsize=(12,4))\n"
            "core = pf[pf.primary_role.isin(['carry','mid','offlane'])]\n"
            "ax[0].scatter(core.hero_pool_per_game, core.winrate, alpha=.5)\n"
            "ax[0].set(xlabel='unique heroes per game', ylabel='winrate', title='Cores: hero-pool breadth vs winrate')\n"
            "ax[1].scatter(pf.gpm_mean, pf.kda_mean, c=(pf.winrate>0.55), alpha=.5)\n"
            "ax[1].set(xlabel='GPM', ylabel='KDA', title='Economy vs impact (dark = winrate>55%)')\n"
            "plt.tight_layout()"
        ),
        code(
            "# Per-team player table (join rosters as-of the season)\n"
            "team_of = mp.dropna(subset=['team_id']).groupby('account_id').team_id.agg(lambda s: s.mode().iat[0])\n"
            "pf2 = pf.merge(team_of.rename('team_id'), on='account_id', how='left')\n"
            "teams = pd.read_parquet(DATA / 'teams.parquet')[['team_id','name']].rename(columns={'name':'team'})\n"
            "pf2.merge(teams, on='team_id').sort_values(['team','gpm_mean'], ascending=[True,False]).head(30)"
        ),
    ]
)

# ----------------------------------------------------------------- 03
nb03 = nb(
    [
        md(
            "# 03 — Multi-parameter team model + TI simulation\n"
            "\n"
            "1. **Elo core** on the game tape (idle-decay as roster-churn proxy) with a\n"
            "   walk-forward Brier/log-loss check against the 50% baseline.\n"
            "2. **Feature layer**: lane-phase strength (gold@10), comeback/throw rates,\n"
            "   draft diversity, side bias — a logistic stack when sklearn is present.\n"
            "3. **Bracket Monte Carlo** of a TI-like group→double-elim format with Elo\n"
            "   noise (`elo_sigma≈60`) to model the two-month gap to the main event.\n"
            "Output: `data/model_pchamp.parquet` — P(champion) per team with CIs."
        ),
        code(SETUP),
        code(
            "from src.model import fit_elo, evaluate, simulate_ti\n"
            "from src.features import team_features, draft_features\n"
            "matches = pd.read_parquet(DATA / 'matches.parquet')\n"
            "elo, hist = fit_elo(matches)\n"
            "print('holdout eval:', evaluate(hist))\n"
            "teams_meta = pd.read_parquet(DATA / 'teams.parquet')[['team_id','name']]\n"
            "elo_named = elo.rename_axis('team_id').reset_index().merge(teams_meta, on='team_id')\n"
            "elo_named.nlargest(20, 'elo')"
        ),
        code(
            "# Feature layer + optional logistic stacking over Elo\n"
            "tf = team_features(pd.read_parquet(DATA / 'match_players.parquet'), matches)\n"
            "df_feats = draft_features(pd.read_parquet(DATA / 'picks_bans.parquet'), matches)\n"
            "team_table = (elo_named.merge(tf, on='team_id', how='left')\n"
            "                       .merge(df_feats, on='team_id', how='left'))\n"
            "try:\n"
            "    from sklearn.linear_model import LogisticRegression\n"
            "    m = matches.dropna(subset=['radiant_team_id','dire_team_id']).sort_values('start_time')\n"
            "    j = (m.merge(team_table.add_prefix('r_'), left_on='radiant_team_id', right_on='r_team_id')\n"
            "          .merge(team_table.add_prefix('d_'), left_on='dire_team_id', right_on='d_team_id'))\n"
            "    X = pd.DataFrame({\n"
            "        'elo_gap': j.r_elo - j.d_elo,\n"
            "        'gold10_gap': (j.r_gold10_mean - j.d_gold10_mean).fillna(0),\n"
            "        'comeback_gap': (j.r_comeback_rate - j.d_comeback_rate).fillna(0),\n"
            "        'draft_div_gap': (j.d_draft_hhi - j.r_draft_hhi).fillna(0),\n"
            "    })\n"
            "    y = j.radiant_win.astype(int)\n"
            "    cut = int(len(X)*0.75)\n"
            "    lr = LogisticRegression().fit(X[:cut], y[:cut])\n"
            "    p = lr.predict_proba(X[cut:])[:,1]\n"
            "    print('stacked holdout Brier:', float(((p - y[cut:])**2).mean()))\n"
            "    print(dict(zip(X.columns, lr.coef_[0].round(4))))\n"
            "except ImportError:\n"
            "    print('sklearn not installed - using pure Elo')"
        ),
        code(
            "# TI simulation: EDIT this list to the final TI-2026 participant set.\n"
            "TI_TEAMS = None  # e.g. ['Team Spirit','Team Liquid','Gaimin Gladiators', ...]\n"
            "pool = elo_named.nlargest(16, 'elo') if TI_TEAMS is None else \\\n"
            "       elo_named[elo_named.name.isin(TI_TEAMS)]\n"
            "sim = simulate_ti(list(pool.name), dict(zip(pool.name, pool.elo)), n_sims=20000)\n"
            "sim.to_parquet(DATA / 'model_pchamp.parquet')\n"
            "sim"
        ),
        md(
            "**Reading the output:** `elo_sigma=60` injects ~2 months of patch/roster\n"
            "uncertainty; the random group draw widens CIs further. Treat `p_champion`\n"
            "as a *band* (see ci95 columns), not a point estimate — and re-run after\n"
            "every tier-1 event and after the pre-TI patch drops."
        ),
    ]
)

# ----------------------------------------------------------------- 04
nb04 = nb(
    [
        md(
            "# 04 — Current team state: form, momentum, stability\n"
            "\n"
            "Trailing-window form vs season baseline, activity gaps (rust), patch splits,\n"
            "and a manual roster-news overlay (fill from Liquipedia/research — roster\n"
            "changes are the #1 model blind spot)."
        ),
        code(SETUP),
        code(
            "matches = pd.read_parquet(DATA / 'matches.parquet')\n"
            "teams = pd.read_parquet(DATA / 'teams.parquet')[['team_id','name']]\n"
            "m = matches.dropna(subset=['radiant_team_id','dire_team_id']).copy()\n"
            "now = m.start_time.max()\n"
            "long = pd.concat([\n"
            "    m.assign(team_id=m.radiant_team_id, win=m.radiant_win),\n"
            "    m.assign(team_id=m.dire_team_id, win=~m.radiant_win.astype(bool)),\n"
            "])\n"
            "def wr(days):\n"
            "    w = long[long.start_time >= now - days*86400]\n"
            "    return w.groupby('team_id').win.agg(['mean','size']).rename(\n"
            "        columns={'mean': f'wr_{days}d', 'size': f'n_{days}d'})\n"
            "form = wr(30).join(wr(60), how='outer').join(wr(180), how='outer')\n"
            "form = form.join(long.groupby('team_id').start_time.max().rename('last_game'))\n"
            "form['days_idle'] = (now - form.last_game) / 86400\n"
            "form = form.reset_index().merge(teams, on='team_id')\n"
            "form['momentum'] = form.wr_30d - form.wr_180d   # + = improving\n"
            "form.sort_values('wr_60d', ascending=False).head(20)"
        ),
        code(
            "# Patch adaptability: winrate on the current patch vs previous\n"
            "cur = m.patch.max()\n"
            "split = pd.concat([\n"
            "    long[long.patch==cur].groupby('team_id').win.mean().rename('wr_cur_patch'),\n"
            "    long[long.patch==cur-1].groupby('team_id').win.mean().rename('wr_prev_patch'),\n"
            "], axis=1).reset_index().merge(teams, on='team_id')\n"
            "split['patch_delta'] = split.wr_cur_patch - split.wr_prev_patch\n"
            "split.dropna().sort_values('patch_delta', ascending=False).head(15)"
        ),
        code(
            "# Manual overlay: roster changes / standins / red flags since TI qualifiers.\n"
            "# Fill from research (research/TI2026_UNDERVALUED.md) and Liquipedia.\n"
            "ROSTER_NOTES = {\n"
            "    # 'Team Spirit': 'stable since TI25; no changes',\n"
            "    # 'Tundra Esports': 'new pos5 May 2026 - cohesion risk',\n"
            "}\n"
            "state = form.sort_values('wr_60d', ascending=False).head(16).copy()\n"
            "state['roster_note'] = state.name.map(ROSTER_NOTES).fillna('(fill me)')\n"
            "state[['name','wr_30d','n_30d','wr_60d','n_60d','momentum','days_idle','roster_note']]"
        ),
    ]
)

# ----------------------------------------------------------------- 05
nb05 = nb(
    [
        md(
            "# 05 — Undervalued teams vs Polymarket TI-2026 odds\n"
            "\n"
            "Combines: model P(champion) (nb 03) + Shin-de-vigged bookmaker consensus +\n"
            "live Polymarket prices (gamma API) → deviation table with the cost hurdle.\n"
            "\n"
            "Bias checklist applied (see `research/STRATEGY_SELECTION.md`):\n"
            "- **FLB**: at 1mo+ horizon longshots are systematically *overpriced* —\n"
            "  cheap-looking 3–8¢ teams are usually correctly cheap.\n"
            "- **Settlement wedge**: ~2 months lockup ≈ 0.6–0.8% — subtract from any edge.\n"
            "- **Fees**: check the market's `feeType`; sports 3% ⇒ peak ~0.75% taker, 0 maker.\n"
            "- **TI base rate**: pre-tournament favourites have historically won TI rarely —\n"
            "  wide CIs are honest, not a bug."
        ),
        code(SETUP),
        code(
            "import requests\n"
            "# Find the TI-2026 winner market on Polymarket (edit slug if needed)\n"
            "CANDIDATE_SLUGS = ['dota-2-the-international-champions', 'dota-2-the-international-2026']\n"
            "ev = None\n"
            "for slug in CANDIDATE_SLUGS:\n"
            "    r = requests.get('https://gamma-api.polymarket.com/events', params={'slug': slug}, timeout=30).json()\n"
            "    if r:\n"
            "        ev = r[0]; break\n"
            "assert ev, 'TI winner event not found - update CANDIDATE_SLUGS'\n"
            "rows = []\n"
            "import json as _json\n"
            "for mk in ev['markets']:\n"
            "    if mk.get('closed'): continue\n"
            "    prices = _json.loads(mk.get('outcomePrices','[]') or '[]')\n"
            "    rows.append({'team': mk['groupItemTitle'] if 'groupItemTitle' in mk else mk['question'],\n"
            "                 'pm_price': float(prices[0]) if prices else None,\n"
            "                 'volume': float(mk.get('volume') or 0),\n"
            "                 'spread': mk.get('spread')})\n"
            "pm = pd.DataFrame(rows).sort_values('pm_price', ascending=False)\n"
            "print(ev['title'], '| feeType:', ev.get('feeType') or (ev['markets'][0].get('feeType')), '| sum of mids:', pm.pm_price.sum().round(4))\n"
            "pm"
        ),
        code(
            "# Bookmaker consensus (EDIT: paste current decimal odds, e.g. from Pinnacle/GG.bet)\n"
            "BOOK_ODDS = {\n"
            "    # 'Team Spirit': 3.5, 'Team Liquid': 6.0, 'Xtreme Gaming': 7.0, ...\n"
            "}\n"
            "from src.model import shin_devig\n"
            "books = shin_devig(BOOK_ODDS) if BOOK_ODDS else None\n"
            "books"
        ),
        code(
            "model = pd.read_parquet(DATA / 'model_pchamp.parquet')\n"
            "t = pm.merge(model.rename(columns={'p_champion':'model_p'}), on='team', how='left')\n"
            "if books is not None:\n"
            "    t = t.merge(books[['team','shin_devig']], on='team', how='left')\n"
            "HOLD_MONTHS = 2.0        # to TI final\n"
            "WEDGE = 0.0376 * HOLD_MONTHS/12   # lockup opportunity cost\n"
            "t['fee'] = 0.03 * t.pm_price * (1 - t.pm_price)   # verify feeType first!\n"
            "t['fair'] = t[['model_p','shin_devig']].mean(axis=1, skipna=True) if books is not None else t.model_p\n"
            "t['edge'] = t.fair - t.pm_price\n"
            "t['edge_net_taker'] = t.edge - t.fee - t.pm_price*WEDGE - (t.spread.fillna(0.01)/2)\n"
            "t['edge_net_maker'] = t.edge - t.pm_price*WEDGE\n"
            "und = t.sort_values('edge_net_maker', ascending=False)\n"
            "und[['team','pm_price','model_p','shin_devig','fair','edge','edge_net_taker','edge_net_maker']].round(4) if books is not None else \\\n"
            "und[['team','pm_price','model_p','fair','edge','edge_net_taker','edge_net_maker']].round(4)"
        ),
        md(
            "**Decision rule** (per `STRATEGY_SELECTION.md`): a team is genuinely\n"
            "undervalued only if `edge_net_maker` is positive **and** the model and the\n"
            "de-vigged books *agree* on the direction (consistency test). One-source\n"
            "edges — especially on sub-10¢ longshots — are presumed to be FLB noise.\n"
            "Enter maker-only, between matches, cluster-capped."
        ),
    ]
)

for name, obj in {
    "01_data_collection.ipynb": nb01,
    "02_player_performance.ipynb": nb02,
    "03_team_model.ipynb": nb03,
    "04_team_state.ipynb": nb04,
    "05_undervalued_vs_polymarket.ipynb": nb05,
}.items():
    NB_DIR.mkdir(parents=True, exist_ok=True)
    (NB_DIR / name).write_text(json.dumps(obj, indent=1))
    print(f"wrote notebooks/{name}")
