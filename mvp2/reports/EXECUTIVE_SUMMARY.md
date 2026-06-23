# Executive Summary — Polly mvp2: Realistic, Bankroll-Managed Copy-Trading

**Project:** Polly mvp2 · **Date:** 2026-06-23 · **Notebook:** `mvp2/notebooks/polly_mvp2_analysis.ipynb`

## What mvp2 set out to fix
mvp1 showed naive copying of the top-100 Polymarket leaderboard is ≈ break-even out-of-sample.
It had two flaws: (1) fills were priced at the **leader's own price** with flat 2% slippage and
**zero latency**; (2) **no bankroll management** (\$1 flat bets). mvp2 rebuilds the system with a
**latency-aware, fee-inclusive fill model**, **price-calibrated + shrunk win probabilities**,
**fractional-Kelly sizing on a compounding bankroll**, **purged walk-forward** validation, and a
**Deflated Sharpe Ratio** multiple-testing guard — all grounded in `../../research/`.

## Headline
> A realistic, bankroll-managed, walk-forward, multiple-testing-corrected pipeline finds that
> **mechanically copying the public top-100 leaderboard is not a robust, capacity-bearing edge.**
> The apparent profits are **survivorship + a few windfall windows**: they **fail Deflated-Sharpe
> significance**, are **unstable and negative in the most recent window**, and the only
> borderline-significant signal (multi-trader consensus) has **almost no out-of-sample capacity**.
> This converges with mvp1's out-of-sample collapse and the independent live copy-bot's −2.47%.

## Five findings

**1. Fill mechanics are *not* the main problem (a surprise).** On the same bet set, realistic
latency + category fees moved full-sample per-bet ROI only from **+39.6% → +39.4%** (Δ=30s; ~0.2 pt).
In this dense trade tape the next-trade price shortly after a leader's BUY is rarely much worse, and
taker fees are ~0.7%/share. *(Caveat: this data-driven proxy may understate true adverse selection;
real latency is ~3–8s with on-chain confirmation.)*

**2. The real killer is out-of-sample instability.** Realistic per-bet ROI by walk-forward test fold
swings **−15%, +136%, +60%, +2%, −15%** — the **most recent fold is −15.2%**. A handful of windfall
windows (correlated markets resolving favorably) dominate; forward, it trends to zero/negative, exactly
like mvp1's −0.1% test.

**3. Survivorship lives on the cohort axis, so nominal returns are an upper bound.** The price-bucket
calibration shows cohort win rates sitting **far above the market price** (the fingerprint of selecting
the 100 winners); test Brier ≈ 0.268 (near coin-flip). A time-based walk-forward cannot remove a bias
that isn't temporal — which is why we shrink probabilities toward the market and trust the Deflated
Sharpe over the nominal P&L.

**4. Statistical significance: mostly absent.** (¼-Kelly, shrink 0.5, walk-forward)

| Strategy | OOS bets | Total ROI | Max DD | Sharpe | Win | **Deflated Sharpe** |
|---|---:|---:|---:|---:|---:|---:|
| copy-all | 826 | +1,348% | −54% | 4.8 | 0.60 | **0.60** ✗ |
| follow-skill (EB) | 191 | +313% | −53% | 6.5 | 0.62 | **0.20** ✗ |
| **consensus ≥3** | 35 | +113% | −3% | 9.9 | 0.74 | **0.91** ~ |
| consensus ≥5 | 6 | +25% | 0% | 5.7 | 0.83 | **0.19** ✗ |

Only **consensus ≥3** approaches significance (DSR 0.91, <0.95 threshold) with a tiny drawdown — but
**35 out-of-sample bets is no capacity**. Copy-all and follow-skill, despite huge nominal returns, are
**not significant**: the returns are noise + survivorship.

**5. Edge concentrates in *slower* markets (H2 confirmed).** Realistic per-bet ROI: **Politics +84.6%
(89% win)** vs fast-resolving **Sports +28.9% (62% win)**; Crypto +31%. Consistent with the
microstructure research — fast informed-flow alpha decays before a copier can act, so what little
survives favours longer-horizon markets.

## Risk management
Fractional Kelly behaves as theory predicts (`P(drop to a) ≈ a^(1/f)`): smaller fractions trade growth
for safety. But the cautionary result is that on a **survivorship-inflated win probability, even
¼-Kelly draws down −54% on copy-all** — a live demonstration of the research warning that overestimated
`p` causes ruinous overbetting. Sizing discipline (shrink-to-market `p`, fractional Kelly, 3%/10%/30%
caps) is **necessary but cannot manufacture an edge that isn't there.**

## Recommendation
Do **not** deploy capital to mechanical leaderboard copying. If pursued at all: restrict to **slower
markets** (politics/long-dated) and **multi-trader consensus**, size with **shrunk-probability
fractional Kelly + hard caps**, and treat it as a **low-capacity experiment validated live on a small
bankroll** — not a scalable strategy. The robust, reusable output of this project is the *methodology*:
realistic fills, calibrated+shrunk probabilities, fractional-Kelly bankroll, purged walk-forward, and
Deflated-Sharpe significance testing.

## Caveats
Cohort survivorship (no historical point-in-time leaderboard available); data-driven fill proxy may
understate adverse selection; trade history truncated to ~1,000 recent trades/wallet (recent-weighted
calendar → short walk-forward windows); resolution time proxied by last observed trade; `prices-history`
is empty for resolved markets. Reproduce: `python src/collect_meta.py && python src/build_notebook.py &&
jupyter nbconvert --execute notebooks/polly_mvp2_analysis.ipynb`.
