# Pre-MVP3 — Executive Summary

*2026-07-01. Distills the pre-MVP3 research (`PRE_MVP3_RESEARCH.md`), its verification
(`VERIFICATION_LOG.md`), and the build plan (`MVP3_DESIGN.md`). All figures below are
primary-source verified unless marked "(unverified — host blocked)".*

## The question
After mvp1/mvp2 showed that **copying Polymarket's top traders is not a robust edge**
(survivorship + a few windfall windows; fails Deflated-Sharpe significance), MVP3 asks: can
**on-chain data** be used to (a) predict insider/informed trading and (b) evaluate mispricing —
and combined into strategies with a real forward test?

## The one finding that redirects everything
**Detecting informed/insider flow is easy; *capturing* it is a losing race.** Once a sharp/insider
trade prints, its permanent price impact lands within seconds (Kyle), the public feed reveals trade
direction only **~59% of the time** (verified, Dubach 2026), bots fill in milliseconds, and
Polymarket's taker fee was built to tax latency arbitrage. **The insider's fill *is* the signal** —
so following it captures only the decayed residual minus fees.

**Therefore MVP3 pivots from "follow winners" to four defensible edges:**
1. **Fade the unskilled cohort.** ~3% of traders drive price discovery; the unskilled majority's
   losses fund them (Yale/LBS). This signal is large, persistent, and — unlike sharp-following —
   **does not self-erase when observed**.
2. **Passive market-making.** Structurally subsidized: **zero maker fee + 20–25% rebates + a
   quadratic near-mid liquidity-reward score** (all verified from Polymarket docs). Edge comes from
   inventory/terminal-risk control, *not* spread capture (Palumbo: passive LP ≈ underwriting).
3. **Mispricing / fair value.** De-vig external odds (Shin) and poll ensembles, bet deviations —
   strongest for sports and long-horizon politics (compression toward 50%).
4. **News-latency.** The one genuine "be fast" window: prices update only **~0.64-for-one** to a
   benchmark probability change, leaving multi-minute drift (verified).

**Insider detection is used *defensively*** — a toxicity filter so the market-maker avoids being the
counterparty to informed flow, and a confirmation signal for fades — never as a copy trigger.

## What the two research pillars established (verified)

**Insider prediction from on-chain data is feasible and evidenced.** Real prosecuted cases (DOJ
soldier: **$33,034 → $409,881** on the Maduro raid; Bubblemaps 9-wallet cluster **98% win / $2.4M**
on military markets). The Mitts-Ofir screen flagged **~$143M** anomalous profit across **210k**
wallet-market pairs. The engineerable on-chain signatures: fresh wallet (age<48h, nonce≤5, >$1k) +
shared-CEX-deposit funding cluster + narrow-focus concentration + last-minute taking + anomalous win
rate; Sybil clustering via funding + gas-provision graph (LightGBM detector, all metrics >0.9). But
**wash trading is ~25% of volume** (Columbia) and the Théo whale was a false positive — so composite,
multi-signal scoring is mandatory.

**Mispricing is real but capacity-bound.** ~**$40M** ($39.59M verified) of internal arbitrage in one
year (**$10.6M single-market rebalancing + $29M cross-market combinatorial**), but per-op ~100 bps,
sub-minute (Kyle λ fell **0.518→0.01**), retail-scale (NBA study: 76.9% capped at ~14.8 shares).
Cross-venue deviations of **2–4%** persist for structural (not informational) reasons. Fair value:
markets beat polls **74%** long-horizon (MAE 1.33pp), 538-type models roughly tie the market (Brier
0.1084 vs 0.1091), Shin is the best de-vig.

## The build (MVP3)
1. **Always-on bitemporal collector first** — six streams (L2 books, on-chain `OrderFilled` trades,
   flows/funding graph, resolutions, off-chain anchors, metadata), point-in-time firewall, universe
   fixed at t0 (survivorship-free), v2 dual-indexing. This is the durable asset.
2. **Strategies in robustness order:** market-making → mispricing/arb → fade-dumb-money →
   news-latency → insider-as-toxicity-filter. Hard hazard to code around: the **post-event
   "frozen-liquidity" window** (NBA spreads → 7,532 bps, 81% of apparent arbs unexecutable).
3. **Forward paper-test at 1 / 2 / 6 months** with **anytime-valid statistics** (e-values /
   confidence sequences for honest monthly peeking), reporting **win rate first** (stabilizes fast),
   Sharpe/drawdown as provisional, and a **Deflated Sharpe + MinTRL** (formulas verified exactly).

## Verification status (honesty note)
A primary-source pass ran on 2026-07-01 via `curl` (the reliable path; `WebFetch` is bot-blocked).
**Verified against primaries:** all forward-test formulas, all on-chain addresses/fees/events, and
the Polymarket-empirical figures. **Corrected:** 10 attribution/label/figure errors (e.g. Polymarket
FLB is *classic* not "reversed"; arbitrage split labels were swapped; capacity figures belonged to
the NBA paper; "Moskowitz reversal" → Lou-Polk-Skouras; Sybil ML percentages and whale/mega tiers
were misattributed). **Still unverified (blocked hosts):** Mitts-Ofir 69.9% win rate, Page-Clemen
4.7–10.9pp, FLB dollar magnitudes, ensemble ~40% — none load-bearing. **No strategic conclusion
changed.** Full audit: [`VERIFICATION_LOG.md`](VERIFICATION_LOG.md).
