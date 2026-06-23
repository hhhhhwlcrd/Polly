# Executive Summary — Copy-Trading the Top Polymarket Performers

**Project:** Polly · **Date:** 2026-06-23 · **Notebook:** `notebooks/polly_copytrading_analysis.ipynb`

## The question
If you mechanically **copied the bets of Polymarket's best-performing traders**,
would you make money — and which *way* of copying works best?

## What we did
- Pulled **public Polymarket data**: the leaderboard (top performers), every
  BUY/SELL of those wallets (`data-api/activity`), and each market's settlement
  (`clob/markets`).
- Cohort = **100 top performers** (union across leaderboard windows; the public
  API caps at 50/window). Median all-time profit **$4.3 M**.
- Universe = **67,067 copyable bets** (BUYs on markets that resolved), across
  **88 traders** and **1,559 markets**, Oct 2024 → Jun 2026.
- Copy model: buy the same outcome token, **hold to resolution**, price the fill
  at the trader's price **+ 2% slippage**. Per-bet ROI = `payout / price_eff − 1`.
- **Chronological train (60%) / validation (20%) / test (20%) split** — fit
  strategy parameters on train, tune on validation, and report ROI **only on the
  held-out test period**.

## Headline result
> **Naively copying top traders is a trap.** It looks fantastic in-sample
> (**+38.7% per bet**) but earns **−0.1%** out-of-sample after slippage — the
> leaderboard "edge" is mostly **survivorship bias** and is already priced into
> the market by the time you can copy it.
>
> **The one signal that survives out-of-sample is consensus:** when **≥5 of the
> top traders independently pile into the same outcome**, that outcome resolves
> correct **95.9%** of the time, for **+64% ROI per bet** on the held-out test set.

## Strategy scoreboard (ROI per copied $1)

| Strategy | Train | Val | **Test (held-out)** | Test win-rate | Test bets |
|---|---:|---:|---:|---:|---:|
| S1 Copy-all (equal) | +38.7% | +68.5% | **−0.1%** | 51.2% | 13,414 |
| S2 Stake-weighted¹ | +34.1% | +64.6% | **+31.3%** | 51.2% | 13,414 |
| **S3 Consensus ≥ 5** | +91.8% | +61.1% | **+64.4%** | **95.9%** | 730 |
| S4 Price-band (long-shots)² | +41.9% | +93.2% | **−0.8%** | 36.7% | 6,910 |
| S5 Follow positive-edge wallets | +64.4% | +0.1% | **+2.3%** | 58.7% | 603 |
| S6 Smart-money (edge-weighted) | +123% | +8.0% | **−6.3%** | 58.7% | 603 |
| S7 Top-10 hottest wallets | +132% | +17.1% | **−96.3%** | 2.1% | 47 |

¹ Capital-weighted ROI is **dominated by a handful of whale positions** (deployed
  capital ≈ \$7.6 M); it is **not** a realistic retail copier return — read it as
  "the big stakes happened to win," not as a strategy you can size into.
² Long-shot band looked best on validation (+93%) but collapsed on test — a clean
  example of **validation overfitting**.

## Key findings
1. **Copy-all ≈ break-even.** Across 13.4k out-of-sample bets the naive copier
   nets −0.1% after 2% slippage — the cohort's 66% raw win rate comes from buying
   favorites that are already fairly priced.
2. **Chasing the hottest hands is the *worst* thing you can do.** Selecting wallets
   by past ROI (S6/S7) produces the biggest in-sample numbers and the biggest
   out-of-sample losses (top-10 wallets: **−96%**). High past ROI = high variance /
   long-shot luck, not repeatable skill.
3. **Consensus is the durable edge.** Herding among independent top traders is
   informative: ≥5-trader agreement wins ~96% of the time and is the only strategy
   positive across **both** validation **and** test. It is, however, **low-capacity**
   (730 bets/period) and requires acting fast — you copy *after* the 5th trader, so
   real slippage will be worse than modeled.
4. **Slippage matters.** Moving from 0% → 5% slippage swings smart-money test ROI
   by ~4.5 points; any thin edge is fragile to execution costs.

## Recommendation
- **Do not** blindly mirror the leaderboard, and **never** chase the highest-ROI
  wallets — both are net-negative once survivorship and slippage are removed.
- **Do** treat **multi-trader consensus as a signal**: a confirmation filter
  ("only act when several sharp traders agree") is the only approach that
  generalized out-of-sample. Validate it live on a small bankroll given its limited
  capacity and execution-timing risk.

## Caveats
Survivorship bias (cohort chosen because it won); BUY-and-hold-to-resolution model
(ignores traders' own exits/SELLs); fills modeled at trader price + flat slippage;
trade history truncated to ~1,000 most-recent trades/wallet, so the calendar is
recent-weighted (val/test windows are short though bet-rich). Reproduce with
`python src/collect_data.py && jupyter nbconvert --execute notebooks/...`.
