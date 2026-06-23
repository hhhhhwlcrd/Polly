# Research

Deep-research outputs feeding **mvp2**. Findings were gathered by fanning out parallel
search agents across 9 angles, cross-verifying each load-bearing claim against ≥2 sources.

| File | What it covers |
|---|---|
| [`HOW_POLYMARKET_COPYTRADING_IS_IMPLEMENTED.md`](HOW_POLYMARKET_COPYTRADING_IS_IMPLEMENTED.md) | How copy-trading is built in practice: the canonical DIY bot architecture (poll `/activity` → FOK order via `py-clob-client`), notable open-source repos, the commercial/tracker ecosystem (auto-execute vs alerts, custody), and the technical detection/execution/fill reference. Includes the April-2026 CLOB v2 migration and a confirmed key-stealer malware warning. |
| [`MVP2_RESEARCH_SYNTHESIS.md`](MVP2_RESEARCH_SYNTHESIS.md) | Academic + methodological grounding and the mvp2 design blueprint: late-copier/alpha-decay evidence, walk-forward + purged CV + Deflated Sharpe/PBO, empirical-Bayes follower selection, binary/fractional/correlated Kelly, the metrics suite, and 5 prioritized testable hypotheses. |

**Headline takeaway:** the public *tracking* infrastructure is solid, but the *copy edge* is
thin, crowded, and taxed (nonzero taker fees explicitly target latency arbitrage). An
independent live ¼-Kelly+consensus bot got **−2.47% ROI in 10 days**, corroborating mvp1's
out-of-sample collapse. mvp2's priority is a **latency-aware, walk-the-book, fee-inclusive**
fill model plus **fractional-Kelly bankroll management**, evaluated walk-forward.
