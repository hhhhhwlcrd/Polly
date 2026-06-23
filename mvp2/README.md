# Polly mvp2 — Realistic, Bankroll-Managed Copy-Trading

A ground-up rebuild of mvp1 that fixes its two known flaws — **unrealistic information flow**
and **no bankroll management** — using the deep-research findings in [`../research/`](../research/).

**Verdict:** with realistic fills, calibrated+shrunk win probabilities, fractional-Kelly sizing,
purged walk-forward validation, and a Deflated-Sharpe significance test, mechanically copying the
public top-100 leaderboard is **not a robust, capacity-bearing edge** — apparent profits are
survivorship + windfall windows, fail significance, and fade out-of-sample. Full write-up:
[`reports/EXECUTIVE_SUMMARY.md`](reports/EXECUTIVE_SUMMARY.md).

## What changed vs mvp1
| Area | mvp1 | mvp2 |
|---|---|---|
| Fill price | leader's price + flat 2% | next real trade at `t+Δ` (latency-aware) + category taker fee |
| Win prob | implicit | price-calibrated on train, **shrunk toward market price** (efficient prior) |
| Sizing | \$1 flat | **fractional-Kelly** `f*=(p−c)/(1−c)`, compounding bankroll, 3%/10%/30% caps |
| Validation | one 60/20/20 split | **purged walk-forward** + **Deflated Sharpe** (multiple-testing guard) |
| Reporting | per-bet ROI | daily/monthly/yearly returns, Sharpe/Sortino/Calmar, max drawdown |

## Layout
```
src/collect_meta.py   # adds per-market fee category + neg_risk to mvp1's data
src/fills.py          # latency-aware, fee-inclusive realistic fill model
src/signals.py        # consensus trigger (point-in-time), empirical-Bayes follower skill, price calibration
src/bankroll.py       # binary/fractional Kelly + correlation-capped compounding bankroll simulator
src/evaluation.py     # purged walk-forward folds + metrics suite + Deflated Sharpe
src/backtest.py       # orchestration: strategy -> realistic fills -> sizing -> walk-forward metrics
src/build_notebook.py # generates the analysis notebook
notebooks/polly_mvp2_analysis.ipynb   # executed analysis + plots
reports/              # EXECUTIVE_SUMMARY.md + strategy_summary.csv + per_fold_roi.csv
data/market_meta.parquet              # fee category / neg_risk per market
```
Reuses mvp1's `trades.parquet` / `resolutions.parquet` / `traders.csv` directly.

## Reproduce
```bash
pip install -r ../mvp1/requirements.txt scipy
python src/collect_meta.py
python src/build_notebook.py
jupyter nbconvert --to notebook --execute --inplace notebooks/polly_mvp2_analysis.ipynb
```
