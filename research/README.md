# Research

Deep-research outputs feeding **mvp2**. Findings were gathered by fanning out parallel
search agents across 9 angles, cross-verifying each load-bearing claim against ≥2 sources.

| File | What it covers |
|---|---|
| [`HOW_POLYMARKET_COPYTRADING_IS_IMPLEMENTED.md`](HOW_POLYMARKET_COPYTRADING_IS_IMPLEMENTED.md) | How copy-trading is built in practice: the canonical DIY bot architecture (poll `/activity` → FOK order via `py-clob-client`), notable open-source repos, the commercial/tracker ecosystem (auto-execute vs alerts, custody), and the technical detection/execution/fill reference. Includes the April-2026 CLOB v2 migration and a confirmed key-stealer malware warning. |
| [`MVP2_RESEARCH_SYNTHESIS.md`](MVP2_RESEARCH_SYNTHESIS.md) | Academic + methodological grounding and the mvp2 design blueprint: late-copier/alpha-decay evidence, walk-forward + purged CV + Deflated Sharpe/PBO, empirical-Bayes follower selection, binary/fractional/correlated Kelly, the metrics suite, and 5 prioritized testable hypotheses. |
| [`PRE_MVP3_RESEARCH.md`](PRE_MVP3_RESEARCH.md) | Pre-MVP3 synthesis from a 14-agent fan-out: on-chain insider/informed-trading detection (signatures, methods, tooling, Mitts-Ofir screen), mispricing/fair-value evaluation, microstructure, on-chain & off-chain data sources, and forward-test methodology. Leads with the strategic pivot: following sharps loses; **fade dumb money + market-make + mispricing + be-fast-on-news** win. |
| [`MVP3_DESIGN.md`](MVP3_DESIGN.md) | The MVP3 blueprint: an always-on bitemporal data-collection system (six streams, point-in-time firewall, v2 dual-indexing), a 5-strategy set ordered by robustness (market-making → arb/mispricing → fade-dumb-money → news-latency → insider used defensively), and a forward paper-trading harness evaluated at 1/2/6 months with anytime-valid statistics. |
| [`PRE_MVP3_EXECUTIVE_SUMMARY.md`](PRE_MVP3_EXECUTIVE_SUMMARY.md) | One-page executive summary of the verified pre-MVP3 findings, the strategic pivot, and the build plan. |
| [`VERIFICATION_LOG.md`](VERIFICATION_LOG.md) | Primary-source verification pass (2026-07-01): per-claim verdicts (verified / corrected / blocked), the 10 corrections applied to the docs, and the still-blocked hosts. Forward-test formulas + on-chain facts + Polymarket-empirical figures verified; no strategic conclusion changed. |
| [`sandbox-allowlist.txt`](sandbox-allowlist.txt) | Egress domains the research needs (the ones the proxy 403-blocked). |

**Headline takeaway:** the public *tracking* infrastructure is solid, but the *copy edge* is
thin, crowded, and taxed (nonzero taker fees explicitly target latency arbitrage). An
independent live ¼-Kelly+consensus bot got **−2.47% ROI in 10 days**, corroborating mvp1's
out-of-sample collapse. mvp2's priority is a **latency-aware, walk-the-book, fee-inclusive**
fill model plus **fractional-Kelly bankroll management**, evaluated walk-forward.
