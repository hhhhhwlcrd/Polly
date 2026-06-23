# Polly — Copy-Trading Analytics for Polymarket

Research into whether (and how) you can profitably copy Polymarket's best traders.

## Repository layout
| Folder | Status | What it is |
|---|---|---|
| [`mvp1/`](mvp1/) | ✅ complete | First analysis: top-100 cohort, 7 copy strategies, train/val/test ROI. See [`mvp1/README.md`](mvp1/README.md) and [`mvp1/reports/EXECUTIVE_SUMMARY.md`](mvp1/reports/EXECUTIVE_SUMMARY.md). |
| `mvp2/` | 🔜 upcoming | Rebuilt from the ground up around realistic, real-time bot information flow and proper bankroll management. |

## The story so far
**mvp1** found that naively copying top performers is ~break-even out-of-sample,
chasing the hottest wallets loses badly, and only **multi-trader consensus**
generalized (≈96% win rate). But mvp1 has two known weaknesses:

1. **Unrealistic information flow** — it priced fills at the trader's own price and
   "knew" resolutions; a real bot trades with latency, price impact, and only
   point-in-time data.
2. **No bankroll management** — every bet was $1; no position sizing, compounding,
   correlation handling, or risk controls.

**mvp2** is being designed to fix both, driven by the deep-research report in
`research/` and the brief in
[`mvp1/reports/DEEP_RESEARCH_PROMPT_v2.md`](mvp1/reports/DEEP_RESEARCH_PROMPT_v2.md).
