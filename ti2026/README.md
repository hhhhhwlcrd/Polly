# ti2026 — Dota 2 / The International 2026: data, game-stats, model, markets

Ad-hoc analysis in the Polly fair-value methodology (`../research/STRATEGY_SELECTION.md`):
download the pro match tape, profile players and teams from **game statistics**, model
P(champion), and price the live Polymarket TI books — including the three **derivative**
markets (Radiant/Dire, longest game, most-banned hero) where match data actually beats a
thin retail book.

Live analysis: **`../research/TI2026_MARKET_ANALYSIS.md`** (Aug 14 2026, TI in progress).

## Layout
```
src/opendota.py         rate-limited, disk-cached OpenDota client (keyless OK)
src/collect_data.py     tier-1 season -> data/*.parquet
                        (matches incl. timelines/objectives/teamfights, players, drafts)
src/features.py         player / team / draft summary tables
src/game_stats.py       *** timing curves, laning, objectives, teamfights, pace,
                        lead-conversion, side splits, opponent adjustment
src/draft.py            *** ban tables, contest rate, hero winrates, team draft
                        signatures, player hero pools, patch meta-shift
src/derivatives.py      *** pricing models for the three TI stat markets
src/model.py            Elo core + logistic stack + TI bracket Monte Carlo + Shin de-vig
src/polymarket.py       *** live gamma/CLOB reader for all four TI books
src/build_notebooks.py  regenerates the notebooks below
notebooks/
  01_data_collection.ipynb          download detailed stats for tournament games
  02_player_performance.ipynb       skill / economics / hero pool per player
  03_team_model.ipynb               multi-parameter model + TI simulation -> P(champion)
  04_team_state.ipynb               form, momentum, patch splits, roster overlay
  05_undervalued_vs_polymarket.ipynb winner market vs model vs de-vigged books
  06_draft_and_meta.ipynb           *** bans, contest rates, draft styles, meta shift
  07_game_stats_deep_dive.ipynb     *** team style profiles, timing curves, opp-adjusted
  08_derivative_markets.ipynb       *** price Radiant/Dire, longest game, most banned
  09_live_ti_tracker.ipynb          *** daily refresh loop during the tournament
```
`***` = added/rebuilt in the Aug 2026 game-stats pass.

## Run order
```bash
pip install -r requirements.txt
jupyter lab notebooks/     # 01 -> 06/07 -> 03 -> 08 -> 09 (daily)
```

## What each layer measures

**Game stats (07).** Every team gets a *style vector*: where its economy curve sits at
minutes 10–40 (tempo vs scaling, via `scaling_slope`), lane strength by role, first-tower
and roshan control, gold swing per teamfight, kills/minute, and how reliably it converts a
+3k lead or overturns a −3k deficit. `opponent_adjust()` residualises any metric against
opponent Elo so a soft schedule doesn't masquerade as strength.

**Draft (06).** Contest rate — (picks + bans) / games — is the honest meta measure; a hero
at 1.0 is removed from the board every game. Team draft signatures separate wide,
unpredictable pools from narrow comfort-hero teams. `meta_shift()` diffs hero priority
across a patch boundary, which is what invalidates pre-patch form.

**Derivative pricing (08).** Beta-binomial for Radiant/Dire (with a sensitivity grid,
because the answer is dominated by the assumed true rate), max-of-N with empirical **and**
GPD tail models for longest game (empirical cannot exceed its sample max — use GPD when the
buckets sit near it), and Dirichlet-multinomial forward simulation for most-banned hero.

## Data access
Notebook 01 needs `api.opendota.com` (keyless ≈60 req/min, keyed 300/min via
`OPENDOTA_API_KEY`; first pull 30–90 min, then fully disk-cached in `data/cache/`).
**This repo's sandbox blocks OpenDota/STRATZ/Liquipedia/datdota/Dotabuff entirely** — run 01
in your own environment; notebooks 02–08 work offline from the parquet files. The Polymarket
gamma/CLOB API used by 05/08/09 is publicly reachable and keyless.

Parsed-replay fields (timelines, objectives, teamfights, lane roles) exist only where
`parsed == True`; notebook 07 prints coverage first because every game-stats feature depends
on it.

## Known caveats
- Team renames are unaddressed in the Polymarket resolution text: **Iron Wing = 1w/1win,
  BoomBoys = BetBoom, TEAM VISION = PARIVISION, HULIGANI = L1ga**. Map names carefully.
- Fee flag on the TI books is `sports_fees_v2`; read the effective rate from the market's
  fee fields before any taker order. Makers pay zero and earn rebates.
- Several TI books carry **placeholder asks (0.94–0.97) and no bids**. A "mid" with no bid
  is not a price — `polymarket.book_table()` surfaces bid/ask separately for this reason.
- Valve ships balance patches close to and sometimes during TI (TI 2026 runs on 7.41e,
  released Jul 30). Re-run 06/07 after any patch and widen the model's uncertainty.
