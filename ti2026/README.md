# ti2026 — Dota 2 The International 2026: data, model, undervaluation

Ad-hoc analysis in the Polly fair-value methodology (`../research/STRATEGY_SELECTION.md`):
download the 2025-26 tier-1 pro season, profile players and teams, model P(champion)
for TI 2026 (Shanghai, Aug 13–23, 16 teams), and compare against Polymarket's
TI-winner market. Research companion: `../research/TI2026_UNDERVALUED.md`.

## Layout
```
src/opendota.py         rate-limited, disk-cached OpenDota client (keyless OK)
src/collect_data.py     tier-1 season -> data/*.parquet (matches, players, drafts)
src/features.py         player / team / draft feature tables
src/model.py            Elo core + logistic stack + TI bracket Monte Carlo + Shin de-vig
src/build_notebooks.py  regenerates the notebooks below
notebooks/
  01_data_collection.ipynb           download detailed stats for tournament games
  02_player_performance.ipynb        skill / economics / hero pool per player
  03_team_model.ipynb                multi-parameter model + TI simulation -> P(champion)
  04_team_state.ipynb                current form, momentum, patch splits, roster overlay
  05_undervalued_vs_polymarket.ipynb live Polymarket vs model vs Shin-de-vigged books
```

## Run order
```bash
pip install -r requirements.txt
jupyter lab notebooks/            # run 01 -> 02/04 -> 03 -> 05
```
Notebook 01 needs `api.opendota.com` (keyless ≈60 req/min; `OPENDOTA_API_KEY` to go
faster; first full pull 30–90 min, then fully disk-cached under `data/cache/`).
**This repo's sandbox blocks OpenDota/STRATZ/Liquipedia/datdota entirely** — run 01
in your own environment; notebooks 02–05 work offline from the parquet files.
The Polymarket gamma API used by notebook 05 is publicly reachable and keyless.

## Known caveats (from the 5-agent research pass, see research doc)
- The Polymarket TI-2026 winner book is **thin and half-formed** (created Jun 29;
  ~$4.2k lifetime volume; some outcomes have no bid) — use bids/asks, never mids,
  and treat the tighter Esports World Cup 2026 winner market as the form anchor.
- Fee flag on the market is `sports_fees_v2` — verify the effective rate from the
  market's fee fields before computing hurdles.
- Valve ships a pre-TI patch most years: re-run 03/04 after it drops and after the
  Esports World Cup concludes; `elo_sigma` in the simulation exists precisely for
  this two-month uncertainty.
- Team renames (BetBoom→BoomBoys, ex-Tundra/1win→"1w Team") are unaddressed in the
  Polymarket resolution text — map names carefully in notebook 05.
