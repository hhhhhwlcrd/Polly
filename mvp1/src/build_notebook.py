"""Generate notebooks/polly_copytrading_analysis.ipynb from cell definitions."""
import json, sys
from pathlib import Path

cells = []
def md(txt):  cells.append(("markdown", txt))
def code(txt): cells.append(("code", txt))

# ===========================================================================
md(r"""# Polly — Copy-Trading the Top 100 Polymarket Performers

**Question:** If you mechanically copied the bets of Polymarket's best-performing
traders, would you make money — and which *way* of copying works best?

This notebook builds an end-to-end analytics pipeline on **public Polymarket data**:

1. **Find available stats for the top ~100 performers** (leaderboard PnL/volume).
2. **Define multiple copy-trading strategies** (different ways of mirroring bets).
3. **Split the trade timeline into train / validation / test** by date,
   fit each strategy's parameters on train/val, and **report ROI on a held-out
   test period** that the strategies never saw.

### Data sources (all public, unauthenticated)
| Source | Endpoint | What it gives |
|---|---|---|
| Leaderboard | `lb-api.polymarket.com/{profit,volume}` | top performers (caps at 50/window) |
| Activity | `data-api.polymarket.com/activity` | every BUY/SELL with price, size, time |
| Resolution | `clob.polymarket.com/markets/<id>` | which outcome won (settlement) |

Raw data was pulled by `src/collect_data.py` into `../data/`.

### The copy model (one formula)
A *copyable bet* = a **BUY** by a top performer on a market that later **resolved**.
A copier buys the same outcome token and **holds to resolution**. Spending \$1 at
price `p` buys `1/p` shares; winning shares settle at \$1, losers at \$0:

$$\text{ROI}_{\text{bet}} = \frac{\text{payout}}{p_{\text{eff}}} - 1,\quad
  \text{payout}\in\{0,1\},\quad p_{\text{eff}} = \min(p\,(1+\text{slippage}),\,0.99)$$

This prices favorites and long-shots consistently and needs only the trader's
execution price plus the market's settlement. Strategies differ only in **which**
bets they copy and **how much** weight they place on each.

> **Key assumptions / caveats** (revisited in the conclusion): we model BUY-and-hold
> to resolution (we ignore the trader's later SELLs/exits); fills happen at the
> trader's price plus a slippage haircut; and the cohort is selected *because* it
> performed well — **survivorship bias** is exactly why the train/val/**test** split
> matters.""")

code("""import sys; sys.path.insert(0, '../src')
import numpy as np, pandas as pd
import matplotlib.pyplot as plt, seaborn as sns
import backtest as bt
sns.set_theme(style="whitegrid"); plt.rcParams['figure.dpi']=110
pd.set_option('display.float_format', lambda x: f'{x:,.4f}')
print('modules loaded')""")

# --- Section 1: cohort -----------------------------------------------------
md(r"""## 1 · The top-100 performer cohort

Polymarket's public leaderboard returns at most **50 wallets per window**, so we
build the cohort as the **union of top performers across several windows**
(all-time / 30d / 7d / 1d profit, plus volume) and keep the 100 highest-ranked
unique wallets. For each we record all-time **profit** and **volume** where the
API exposes them.""")

code("""traders, trades, res = bt.load_raw()
print(f"cohort wallets: {len(traders)} | raw trades: {len(trades):,} | markets w/ resolution: {len(res):,}")
display(traders.head(10)[['cohort_rank','name','profit_all','volume_all','lb_sources']])""")

code("""fig, ax = plt.subplots(1, 2, figsize=(12,4))
traders['profit_all'].dropna().div(1e6).plot(kind='hist', bins=30, ax=ax[0], color='seagreen')
ax[0].set(title='All-time profit (top performers)', xlabel='Profit ($M)')
traders['volume_all'].dropna().div(1e6).plot(kind='hist', bins=30, ax=ax[1], color='steelblue')
ax[1].set(title='All-time volume (top performers)', xlabel='Volume ($M)')
plt.tight_layout(); plt.show()
print('Median all-time profit: $%.2fM' % (traders['profit_all'].median()/1e6))""")

# --- Section 2: copyable bets ---------------------------------------------
md(r"""## 2 · Building the copyable-bets dataset

We restrict trades to **BUYs on markets that resolved with a known winner**, join
each trade's outcome token to the market's settlement, and compute the per-bet ROI
(here at a baseline **2% slippage**). This is the universe every strategy draws from.""")

code("""SLIPPAGE = 0.02
bets = bt.build_bets(slippage=SLIPPAGE)
print(f"copyable bets: {len(bets):,} | traders represented: {bets['proxyWallet'].nunique()} "
      f"| resolved markets: {bets['conditionId'].nunique()}")
print(f"overall win rate: {bets['payout'].mean():.1%}")
print(f"NAIVE copy-all ROI (all data, in-sample): {bets['roi'].mean():+.2%}  <-- inflated, see split")
display(bets[['datetime','name','title','outcome','entry_price','payout','roi']].head())""")

code("""fig, ax = plt.subplots(1, 3, figsize=(15,4))
bets['entry_price'].plot(kind='hist', bins=40, ax=ax[0], color='slateblue')
ax[0].set(title='Entry price distribution', xlabel='price (implied prob)')
bets.groupby(bets['datetime'].dt.to_period('M').astype(str)).size().plot(kind='bar', ax=ax[1], color='darkorange')
ax[1].set(title='Copyable bets per month', xlabel='', ylabel='# bets')
# ROI by price bucket
bets['pb'] = pd.cut(bets['entry_price'], [0,.2,.4,.6,.8,1.0])
bets.groupby('pb', observed=True)['roi'].mean().plot(kind='bar', ax=ax[2], color='teal')
ax[2].set(title='Mean ROI by entry-price bucket', xlabel='price bucket', ylabel='ROI')
ax[2].axhline(0, color='k', lw=.8)
plt.tight_layout(); plt.show()""")

# --- Section 3: split ------------------------------------------------------
md(r"""## 3 · Train / validation / test split (chronological)

We sort **all bets by execution time** and cut 60% / 20% / 20%. The split is
strictly time-ordered, so no future information leaks into earlier periods. Because
trading volume is heavily concentrated in recent weeks, the calendar windows for
val/test are short but each still contains thousands of bets — strong statistical
power for a genuine **out-of-sample** test of "does the copy edge persist forward?".""")

code("""splits = bt.date_split(bets, train=0.6, val=0.2)
display(bt.split_ranges(splits))
train, val, test = splits['train'], splits['val'], splits['test']""")

# --- Section 4: strategies -------------------------------------------------
md(r"""## 4 · Copy-trading strategies

Seven ways to copy the cohort. Parameters (which wallets, thresholds, bands) are
**fit on train, tuned on validation, and only then scored on test**.

| # | Strategy | Idea |
|---|---|---|
| S1 | **Copy-all (equal)** | mirror every bet, \$1 each — the naive baseline |
| S2 | **Stake-weighted** | size each copy ∝ the trader's own USDC stake |
| S3 | **Consensus ≥ N** | only copy a market/outcome ≥ N cohort members bought |
| S4 | **Price band** | only copy bets whose entry price ∈ [lo, hi] |
| S5 | **Follow positive-edge wallets** | copy only wallets profitable *in train* |
| S6 | **Smart-money (edge-weighted)** | follow positive-edge wallets, weight by train edge |
| S7 | **Top-K wallets** | follow the K best wallets by train ROI |

All tunable parameters are selected by **maximising validation ROI**.""")

code("""# --- Fit wallet-level edge on TRAIN only -------------------------------
edge = bt.wallet_edge(train, min_bets=20)
print(f"wallets with >=20 train bets: {len(edge)}")
display(edge.head(10)[['name','n','edge','win']])
good_wallets = edge[edge['edge'] > 0]['proxyWallet'].tolist()
wallet_w = dict(zip(edge['proxyWallet'], edge['edge'].clip(lower=0)))
print(f"positive-edge wallets carried forward: {len(good_wallets)}")""")

code("""# --- Tune scalar hyper-parameters on VALIDATION ------------------------
def roi_of(fn_bets, fn_w):  # tiny helper
    return bt.evaluate(fn_bets, fn_w)['roi']

# Consensus N
cons = {N: roi_of(*bt.s_consensus(val, N)) for N in (2,3,5,8)}
best_N = max(cons, key=cons.get)
# Price band
bands = {(.5,.95):None,(.05,.5):None,(.3,.7):None,(.6,.9):None,(.05,.95):None}
band_roi = {b: roi_of(*bt.s_price_band(val,*b)) for b in bands}
best_band = max(band_roi, key=band_roi.get)
# Top-K
topk_by_edge = edge['proxyWallet'].tolist()
ks = {}
for K in (5,10,20,30):
    sub,w = bt.s_follow_topk(val, topk_by_edge[:K]); ks[K]=bt.evaluate(sub,w)['roi']
best_K = max(ks, key=ks.get)
print('Consensus ROI by N (val):', {k:round(v,4) for k,v in cons.items()}, '-> N*=',best_N)
print('Price-band ROI (val):', {k:round(v,4) for k,v in band_roi.items()}, '-> band*=',best_band)
print('Top-K ROI by K (val):', {k:round(v,4) for k,v in ks.items()}, '-> K*=',best_K)""")

# --- Section 5: evaluate ---------------------------------------------------
md(r"""## 5 · Evaluation across train / val / **test**

For each strategy we report ROI (return on deployed capital), win rate, number of
bets, and total P&L assuming \$1 of capital per unit weight. Watch the gap between
**train** (in-sample, survivorship-inflated) and **test** (held-out) — that gap is
the whole point.""")

code("""def run(strategy_fn, frame):
    sub, w = strategy_fn(frame)
    return bt.evaluate(sub, w)

strategies = {
  'S1 copy-all':       lambda f: bt.s_copy_all(f),
  'S2 stake-weighted': lambda f: bt.s_stake_weighted(f),
  'S3 consensus>=%d'%best_N: lambda f: bt.s_consensus(f, best_N),
  'S4 price-band %s'%str(best_band): lambda f: bt.s_price_band(f, *best_band),
  'S5 follow +edge':   lambda f: bt.s_follow_topk(f, good_wallets),
  'S6 smart-money':    lambda f: bt.s_smart_money(f, good_wallets, wallet_w),
  'S7 top-%d wallets'%best_K: lambda f: bt.s_follow_topk(f, topk_by_edge[:best_K]),
}

rows=[]
for name, fn in strategies.items():
    for split_name, frame in [('train',train),('val',val),('test',test)]:
        r = run(fn, frame); r['strategy']=name; r['split']=split_name; rows.append(r)
results = pd.DataFrame(rows)
pivot = results.pivot(index='strategy', columns='split', values='roi')[['train','val','test']]
print('=== ROI by strategy and split ==='); display(pivot.style.format('{:+.2%}'))
print('\\n=== TEST-period detail (held-out) ===')
display(results[results.split=='test'].set_index('strategy')[['n_bets','win_rate','roi','total_pnl','avg_price']])""")

code("""# Bar chart: test ROI by strategy
tt = results[results.split=='test'].set_index('strategy')['roi'].sort_values()
fig, ax = plt.subplots(figsize=(9,4.5))
colors=['crimson' if v<0 else 'seagreen' for v in tt.values]
tt.plot(kind='barh', color=colors, ax=ax)
ax.axvline(0,color='k',lw=1); ax.set(title='Out-of-sample (TEST) ROI per copied $1', xlabel='ROI')
for i,v in enumerate(tt.values): ax.text(v, i, f' {v:+.2%}', va='center')
plt.tight_layout(); plt.show()""")

code("""# Equity curves on the TEST period for the most interesting strategies
fig, ax = plt.subplots(figsize=(11,5))
for name in ['S1 copy-all','S5 follow +edge','S6 smart-money', 'S3 consensus>=%d'%best_N]:
    sub, w = strategies[name](test)
    if len(sub)==0: continue
    sub2 = sub.sort_values('timestamp')
    ww = np.asarray(w,float)[np.argsort(sub['timestamp'].values)]
    ax.plot(pd.to_datetime(sub2['datetime']), np.cumsum(ww*sub2['roi'].values), label=name)
ax.axhline(0,color='k',lw=.8); ax.legend(); ax.set(title='Cumulative P&L on TEST period',
       ylabel='cumulative profit ($, $1/bet-weight)', xlabel='date')
plt.tight_layout(); plt.show()""")

# --- Section 6: slippage sensitivity ---------------------------------------
md(r"""## 6 · Sensitivity to slippage

Copiers never get the trader's exact fill. We re-price the **test** bets at
0% / 1% / 2% / 5% slippage and recompute ROI — this is the difference between a
paper edge and a tradeable one.""")

code("""sens=[]
for s in (0.0, 0.01, 0.02, 0.05):
    bb = bt.build_bets(slippage=s)
    sp = bt.date_split(bb, 0.6, 0.2); te = sp['test']
    for name, fn in [('S1 copy-all', lambda f: bt.s_copy_all(f)),
                     ('S5 follow +edge', lambda f: bt.s_follow_topk(f, good_wallets)),
                     ('S6 smart-money', lambda f: bt.s_smart_money(f, good_wallets, wallet_w))]:
        r = run(fn, te); sens.append({'slippage':f'{s:.0%}','strategy':name,'test_roi':r['roi']})
sens = pd.DataFrame(sens).pivot(index='strategy', columns='slippage', values='test_roi')
display(sens.style.format('{:+.2%}'))""")

# --- Section 7: conclusions -------------------------------------------------
md(r"""## 7 · What we learned

Quantitative conclusions are auto-generated below from the run; see
`reports/EXECUTIVE_SUMMARY.md` for the written write-up.""")

code("""ca = pivot.loc['S1 copy-all']
best_test = results[results.split=='test'].set_index('strategy')['roi'].idxmax()
best_roi  = results[results.split=='test'].set_index('strategy')['roi'].max()
print('AUTO-GENERATED FINDINGS')
print('-'*60)
print(f'1. Naive copy-all: train {ca.train:+.1%} -> test {ca.test:+.1%} '
      f'({\"edge collapses out-of-sample\" if ca.test < 0.02 else \"edge persists\"})')
print(f'2. Best out-of-sample strategy: {best_test} at {best_roi:+.2%} ROI/bet')
print(f'3. Cohort raw win rate: {bets[\"payout\"].mean():.1%} (favorite-heavy book)')
print(f'4. Slippage 0%->5% moves smart-money test ROI by '
      f'{(sens.loc[\"S6 smart-money\"][\"0%\"]-sens.loc[\"S6 smart-money\"][\"5%\"]):.2%}')""")

# ===========================================================================
nb = {
  "cells": [
    {"cell_type": t, "metadata": {}, "source": s.splitlines(keepends=True)} |
    ({"outputs": [], "execution_count": None} if t == "code" else {})
    for (t, s) in cells
  ],
  "metadata": {"kernelspec": {"display_name": "Python 3", "language": "python",
               "name": "python3"}, "language_info": {"name": "python"}},
  "nbformat": 4, "nbformat_minor": 5,
}
out = Path(__file__).resolve().parent.parent / "notebooks" / "polly_copytrading_analysis.ipynb"
out.write_text(json.dumps(nb, indent=1))
print("wrote", out, "with", len(cells), "cells")
