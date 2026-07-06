# MVP3 Design — Always-On Data Collection + Multi-Strategy Forward Test

*Design blueprint, 2026-06-25. Grounded in `PRE_MVP3_RESEARCH.md`,
`HOW_POLYMARKET_COPYTRADING_IS_IMPLEMENTED.md`, and `MVP2_RESEARCH_SYNTHESIS.md`. Builds on the
mvp1/mvp2 verdict: leaderboard copying is not a robust edge — the durable asset is the
data + methodology.*
*Updated 2026-06-25 after the primary-source verification pass (see `VERIFICATION_LOG.md`). The
design is unchanged in shape; the edits below fold in corrected facts: the v2 `OrderFilled` is a
distinct event (dual decoder), UMA fast-path liveness is 2h, FiveThirtyEight is dead as an anchor,
Polymarket spreads are measured in bps, and the favorite-longshot bias is **classic, not reversed**.*

## Thesis

MVP3 stops trying to *copy* winners (a losing race after latency/fees/survivorship) and instead:
1. **Captures the full information set** Polymarket exposes, continuously and point-in-time, so the
   data supports *every* strategy below without re-collection.
2. **Derives signals that don't self-erase:** on-chain insider/toxicity flags, mispricing vs.
   fair value, and dumb-money fade — used to *price* and *position*, not to chase fills.
3. **Proves itself by forward paper-trading** evaluated at 1 / 2 / 6 months with anytime-valid
   statistics — the only design that escapes the cohort-survivorship bias that contaminated mvp1/2.

---

## Part 1 — The always-on data collection system (`mvp3/collector/`)

Build this first; it is the deliverable that makes everything else possible. Fix the **market
universe at t0** (snapshot every live + upcoming market) so the forward test is survivorship-free.

### 1.1 What to capture (six streams, all bitemporal: valid-time + ingest-time)

| Stream | Source | Cadence | Why |
|---|---|---|---|
| **Order books (L2)** | CLOB market WebSocket `book`+`price_change`+`tick_size_change` | event-driven | micro-price, spread/depth, realistic fills; **REST L2 backfill is gone — must capture live** |
| **Trades (tape)** | on-chain `OrderFilled` (**v1 + v2 use DISTINCT event signatures — dual decoder**; v2 also emits `FeeCharged`) + Data API `/trades` | per block / poll | execution-truth price & size; **attribute per-fill on `maker`** (taker = Exchange contract when sweeping) |
| **Last-trade/midpoint** | WS `last_trade_price`, CLOB `/midpoint`,`/spread` | event-driven | fast price reference |
| **On-chain flows** | Polygon logs: CTF `TransferSingle/Batch`, USDC.e+pUSD `Transfer`, proxy-factory `ProxyCreation` | per block (+~30-block reorg buffer) | funding graph, wallet age, holdings |
| **Resolutions** | UMA CTF Adapter events + CLOB market `winner` | per event | settlement ground truth + event timestamps (**fast path finalizes after 2h liveness; 48h only on DVM escalation**) |
| **Off-chain anchors** | GDELT DOC 2.0 (news), The Odds API (de-vig, 500 credits/mo free), ESPN JSON (sports) | 1–15 min | fair value + event-study runup; store `seendate` as an interval. **FiveThirtyEight is shut down (Mar 2025) — dropped; no free raw-poll replacement** |

Plus **market metadata** (Gamma): slug↔conditionId↔clobTokenIds, category (fee rate), neg_risk,
tick size, min order size, end date.

### 1.2 Architecture
```
 WS/RPC/REST collectors ──▶ raw immutable log (append-only Parquet on object store, partitioned
   (one process per stream)        by date + conditionId; Zstd; dedup-by-id, last-write-wins)
            │                              │
            │                              ▼
            │                     bitemporal store (DuckDB over Parquet for research;
            │                     optional TimescaleDB/ClickHouse for live queries)
            ▼                              │
   point-in-time API  ◀────────────────────┘   ("as-of(t)" queries only — the leakage firewall)
            │
            ▼
   feature builders → signals → paper-trading engine (Part 3)
```
- **Two-layer firewall:** the raw log records *everything*; the decision layer may only call
  `as_of(t)` (records with valid-time ≤ t and ingest-time ≤ t). This is the standard look-ahead
  defense and the thing mvp1/mvp2 lacked.
- **Reorg safety:** Polygon reorgs reach 32+ blocks — apply a confirmation buffer before marking
  on-chain events final; idempotent dedup-by-id absorbs Goldsky/Mirror re-emits.
- **v2 dual-indexing (VERIFIED on Polygonscan):** watch **both** exchange generations — v1 CTF Exch
  `0x4bFb41d5B3570DeFd03C39a9A4D8dE6Bd8B8982E` / v1 NegRisk `0xC5d563A36AE78145C45a50134d48A1215220f80a`
  and v2 CTF Exch `0xE111180000d2663C0091e4f400237545B87B996B` / v2 NegRisk
  `0xe2222d279d744050d28e00520010520000310F59` — and **both** collateral tokens (USDC.e
  `0x2791Bca1f2de4661Ed88A30C99A7a9449Aa84174` + pUSD `0xC011a7E12a19f7B1f670d46F03B03f3342E82DFB`);
  CTF `0x4D97DCd97eC945f40cF65F87097ACe5EA0476045` is stable. **The v2 `OrderFilled` is a NEW event**
  (topic0 `0xe92c2272…`; `OrdersMatched` `0x787a2e12…`; fees split into a separate `FeeCharged`
  event) — you **cannot** reuse the v1 decoder/topic0, and v2 fees must be read from `FeeCharged` /
  `getClobMarketInfo`, not the old order `feeRateBps`. Pull the byte-exact v2 ABI from the verified
  source tab before hard-coding. v1-only tooling goes blind after Apr 28 2026.
- **Build vs. reuse:** Goldsky Mirror is the fastest production lake for the on-chain streams;
  `SII-WANGZJ/Polymarket_data` is the closest OSS collector to clone. We still run our **own** WS
  order-book recorder (no other source reconstructs historical L2).
- **Volume:** instrument it — order-book capture across ~2.4k markets is low-to-mid GB/day,
  concentrated in a few hot markets.

### 1.3 Derived feature tables (computed point-in-time, stored alongside)
- **Wallet features:** age, nonce, first-funding source (backward USDC/pUSD trace, stop at service
  clusters), funding-cluster id (deposit-address + gas-provision sub-graph), realized win rate /
  PnL (empirical-Bayes shrunk), skill label.
- **Market microstructure:** micro-price, spread, depth profile, OFI/OBI (from **on-chain** signed
  trades — the public feed is only ~59% direction-accurate), realized vol, time-to-resolution.
- **Insider/toxicity score** (composite, see Strategy E): fresh-wallet + funding-cluster +
  concentration + last-minute + anomalous-win-rate, with VPIN as a secondary toxicity gauge.
- **Fair value:** de-vigged external probability (Shin for sports odds; poll ensemble for politics),
  market-vs-fair deviation, long-horizon compression-corrected probability.

---

## Part 2 — The strategy set (ship in robustness order, not glamour order)

Each strategy is a pure function of the point-in-time feature store → desired position; sizing is
the mvp2 fractional-Kelly + caps engine (reused). Ordered most → least structurally robust.

### A. Passive market-making (most structurally robust)
- **Why:** Polymarket *subsidizes* makers (VERIFIED, `docs.polymarket.com`) — **makers are never
  charged fees + a 20% (crypto) / 25% (other-category) share of taker fees is rebated to makers +
  quadratic near-mid liquidity rewards** (`S = ((v−s)/v)²·b`, single-sided quotes ÷ c=3). Taker fee
  itself is category-based on a `p(1−p)` curve (`fee = C × feeRate × p × (1−p)`; feeRate: crypto
  0.07, sports 0.03, finance/politics/mentions/tech 0.04, econ/culture/weather/other 0.05,
  geopolitics 0). Maker>taker return structure (Betfair) + biased taker flow.
- **How:** Avellaneda-Stoikov / Guéant-Lehalle-Fernandez-Tapia inventory-skewed quoting; reservation
  price skews with inventory and time-to-resolution; quote near mid to max liquidity-reward score.
- **Critical risk controls:** passive LP is *underwriting*, not spread capture (Palumbo) — cap
  terminal/resolution exposure, skew hard on inventory, and **pull quotes around event conclusion**
  (post-event/pre-oracle "frozen liquidity": VERIFIED arXiv 2605.00864 — NBA post-game median spread
  hit **7,532.65 bps** and **30/37 (81.1%)** of theoretical arbs were strictly post-game/
  unexecutable). Avoid one-sided toxic flow (use the toxicity score).

### B. Mispricing / arbitrage (structural, capacity-limited)
- **B1 single-market:** YES+NO < $1 → buy the pair; (VERIFIED arXiv 2605.00864) capacity is tiny —
  76.9% of opportunities constrained to ~**14.8 shares**, median yield ~**101 bps**, median duration
  **3.6s** → must be fast and is self-limiting. **B2 neg-risk:** multi-outcome YES-sum ≠ 1 via
  NegRiskAdapter convert.
- **B3 fair-value deviation:** bet when market price deviates from de-vigged/ensembled external fair
  value beyond a threshold — strongest for **sports** (de-vig consensus odds, Shin) and **long-horizon
  politics** (poll ensemble + compression correction: VERIFIED, a 70¢ politics contract **one month
  out ≈ ~75% true**, slope-dependent). **Direction note (CORRECTED):** Polymarket exhibits the
  **classic** favorite-longshot bias (favourites underpriced, longshots overpriced) — same direction
  as racetracks, *not* reversed — which is the same compression-toward-50% effect; tilt the standard
  way, platform-calibrated.
- **Caveat:** log capacity honestly; observed deviations clear in **seconds**, and cross-venue
  magnitudes are now **unverified speculation** (neither arbitrage paper studied cross-venue) — do
  not size on them; most stale arbs are unexecutable frozen liquidity.

### C. Fade-the-dumb-money (large, persistent, non-self-erasing)
- **Why:** ~3% of traders drive price discovery; the unskilled majority's losses fund them
  (Yale/LBS). Unlike sharp-following, this signal doesn't evaporate when observed.
- **How:** identify persistently-unskilled wallets point-in-time (EB-shrunk negative edge); when
  aggregate dumb-money flow pushes a market away from fair value (Strategy B3), **take the other
  side**. Pairs naturally with market-making (be the counterparty to biased flow).

### D. News-latency (automation race in the one genuine window)
> ⚠️ **OVERTURNED 2026-07-06** — see `STRATEGY_SELECTION.md` §5: the anchor paper's own executable
> test (arXiv 2606.07811 App. B) is negative after costs at every threshold; Polymarket matching
> delays hand the speed edge to makers; the fee-free geopolitics niche is documented insider
> territory. Demoted to a ~$100 shadow-mode measurement pilot; do not build for capital.
- **Why:** prices update only ~0.64-for-one to a benchmark probability change → multi-minute drift;
  the edge is reacting to *news* faster than slow humans, not copying confirmed fills.
- **How:** GDELT/RSS/odds/ESPN event detector → map to affected market → take direction before the
  ~multi-minute incorporation completes. Beware surprise-overreaction (fade extreme jumps).
- **Honesty flag:** this is the closest to a "fast" race; expect MEV/HFT competition and model
  latency explicitly. Likely thin; validate hard in the forward test.

### E. Insider/toxicity detection — used DEFENSIVELY
- **Not a copy signal** (the insider's fill *is* the signal; following loses). Two uses:
  (1) **Toxicity filter** for Strategy A — widen/pull quotes when composite insider score is high so
  MM isn't the counterparty to informed flow; (2) **fade confirmation** — a fresh-funded
  narrow-focus cluster piling into a market the dumb money also holds strengthens a fade.
- **Composite score** (avoid Théo-style false positives — single signals are insufficient):
  fresh-wallet (age<48h, nonce≤5, >$1k) + shared-CEX-funding cluster + concentration (>2% 24h vol)
  + last-minute taking + anomalous win-rate (p<0.001). Calibrate against the Mitts-Ofir screen.

---

## Part 3 — Forward-test harness & 1/2/6-month evaluation (`mvp3/forwardtest/`)

The point of the whole project: an out-of-sample, survivorship-free, leakage-free live evaluation.

### 3.1 Harness
- **Paper-trade in real time:** each strategy emits intended orders against the **live** book; the
  engine simulates fills by **walking the recorded L2** (not mid) with a latency-Δ, charging the
  exact category taker fee (or crediting maker rebate). Reference designs: ABIDES / NautilusTrader
  (research-live parity).
- **Log three things separately:** (a) intended trade + the point-in-time book at decision time,
  (b) simulated fill, (c) — if a tiny real-capital sleeve is run — the actual `user`-WS fill as
  ground truth. This lets us re-run *all* strategies over the same recorded data later.
- **Known ceiling:** paper trading can't model own market impact or reflexivity — state this; if any
  edge survives, confirm with a small real-capital sleeve.

### 3.2 Evaluation cadence without peeking inflation
- **Pre-register** the 1 / 2 / 6-month looks. Monthly peeking at α=0.05 inflates Type-I error
  (CORRECTED: ~0.14 at 5 looks, ~0.19 at 10 looks — Armitage), so either use **group-sequential
  O'Brien-Fleming alpha-spending**, or preferably **e-values / confidence sequences** (VERIFIED
  anytime-valid, arXiv 2210.01948 — correct at *any* stopping time).
- **Report in stability order:** **win rate first** (binomial SE √(p(1−p)/n) — stabilizes in ~weeks,
  ~100 trades → ~5pp); **Sharpe provisional** (Lo SE, slow); **max drawdown explicitly provisional**
  (biased, grows with window — not comparable across horizons).
- **Deflate, don't inflate:** track **N strategies/configs tried** and report a **Deflated Sharpe**
  (Harvey-Liu-Zhu hurdle t>3.0). Compute **PSR/MinTRL** to state honestly how long each strategy
  must run to confirm its edge given its Sharpe, skew, kurtosis (edge ≈ benchmark ⇒ MinTRL years).
- **Expected reading at each checkpoint:** 1mo → win-rate confidence intervals + arb hit-rate +
  data-quality/gap report (foreground these). 2mo → per-strategy directional read, still provisional
  Sharpe. 6mo → first defensible risk-adjusted comparison; promote only strategies that clear the
  Deflated-Sharpe / anytime-valid bar.

### 3.3 Success criteria (per strategy)
A strategy graduates to a real-capital sleeve only if, at the 6-month look: anytime-valid p<0.05 (or
e-value>20) on net-of-fee/slippage return, win rate CI excludes the no-edge null, Deflated Sharpe>0,
and observed capacity ≥ a usable bankroll. Otherwise: document and retire (as mvp1/mvp2 did).

---

## Build order & milestones
1. **Collector MVP** (order books + trades + resolutions + metadata, bitemporal, t0 universe fixed) →
   start recording immediately (the clock on the 6-month test starts when capture starts).
2. **On-chain flow + funding-graph + wallet features** (insider/toxicity score, EB skill).
3. **Fair-value engine** (de-vig/ensemble external anchors) + microstructure features (on-chain OFI,
   micro-price).
4. **Paper-trading harness** + strategies A→E behind the point-in-time firewall.
5. **1/2/6-month forward evaluation** with anytime-valid stats; promote/retire.

> Operational note: this container is ephemeral, so the always-on collector must run on persistent
> infrastructure (a small VPS / scheduled job + object storage) for the multi-month window. The repo
> ships the code, schema, and run-book; the months-long capture runs outside the session.

## Open items to verify before/while building (flagged in research)
**Resolved in the 2026-06-25 verification pass** (see `VERIFICATION_LOG.md`): UMA liveness = **2h**
fast path (48h is DVM-only); v2 `OrderFilled`/`OrdersMatched` have **new topic0s** + a separate
`FeeCharged` event (topic0s recorded in the log; still pull the byte-exact param list from the
verified Polygonscan source before hard-coding); 538 CSVs are **dead** (drop them); fee model and
all contract addresses confirmed on Polygonscan.

**Still open:** live Goldsky project-id/v2 manifest coverage; `book.hash` algo (read
`py-clob-client`); Arkham/Nansen pricing at our query volume (vendor docs were anti-bot-blocked —
only snippet-level). Treat all remaining single-source magnitudes in the research as directional,
not as plug-in parameters; in particular the cross-venue arbitrage magnitudes are now **unverified
speculation**, and the GNN/GAT Sybil-accuracy claim was **dropped as unsupported**.
