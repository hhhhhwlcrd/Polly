# Polly — Polymarket Copy-Trading Analytics

Can you make money by copying Polymarket's best traders? This project pulls public
Polymarket data, builds several copy-trading strategies, evaluates them with a
proper **train / validation / test** date split, and reports out-of-sample ROI.

**TL;DR:** Naive copying is ~break-even out-of-sample; chasing the hottest wallets
loses badly; **multi-trader consensus** is the only signal that generalizes
(≈96% win rate, +64% ROI/bet on held-out test). Full write-up:
[`reports/EXECUTIVE_SUMMARY.md`](reports/EXECUTIVE_SUMMARY.md).

## Layout
```
src/collect_data.py     # pull leaderboard + trade history + market resolutions -> data/
src/backtest.py         # copyable-bets dataset, date split, strategies, ROI engine
src/build_notebook.py   # generates the analysis notebook
notebooks/polly_copytrading_analysis.ipynb   # executed analysis + plots
reports/EXECUTIVE_SUMMARY.md                 # results write-up
data/                   # traders.csv, trades.parquet, resolutions.parquet
```

## Reproduce
```bash
pip install -r requirements.txt
python src/collect_data.py                       # ~minutes; writes data/
python src/build_notebook.py                      # regenerate notebook
jupyter nbconvert --to notebook --execute --inplace \
    notebooks/polly_copytrading_analysis.ipynb    # run it
```

## Data sources (public, unauthenticated)
- `lb-api.polymarket.com/{profit,volume}` — leaderboards (max 50/window)
- `data-api.polymarket.com/activity` — per-wallet trade history
- `clob.polymarket.com/markets/<conditionId>` — market settlement / winner

## Method in one line
A *copyable bet* is a BUY by a top performer on a market that resolved; a copier
buys the same token and holds to settlement, so per-bet
`ROI = payout / (price·(1+slippage)) − 1`. Strategies differ only in which bets
they copy and how they weight them; parameters are fit on train, tuned on
validation, and scored on a held-out test period.
