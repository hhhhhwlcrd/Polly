# MVP3 Design — Always-On Data Collection + Multi-Strategy Forward Test

*Design blueprint, 2026-06-25. Grounded in `PRE_MVP3_RESEARCH.md`,
`HOW_POLYMARKET_COPYTRADING_IS_IMPLEMENTED.md`, and `MVP2_RESEARCH_SYNTHESIS.md`. Builds on the
mvp1/mvp2 verdict: leaderboard copying is not a robust edge — the durable asset is the
data + methodology.*

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
| **Trades (tape)** | on-chain `OrderFilled` (CTF Exchange v1+v2) + Data API `/trades` | per block / poll | execution-truth price & size; **attribute on `maker`** |
| **Last-trade/midpoint** | WS `last_trade_price`, CLOB `/midpoint`,`/spread` | event-driven | fast price reference |
| **On-chain flows** | Polygon logs: CTF `TransferSingle/Batch`, USDC.e+pUSD `Transfer`, proxy-factory `ProxyCreation` | per block (+reorg buffer) | funding graph, wallet age, holdings |
| **Resolutions** | UMA CTF Adapter events + CLOB market `winner` | per event | settlement ground truth + event timestamps |
| **Off-chain anchors** | GDELT DOC 2.0 (news), The Odds API (de-vig), ESPN JSON (sports), 538 CSVs (polls) | 1–15 min | fair value + event-study runup; store `seendate` as an interval |

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
- **Reorg safety:** treat **Polygon milestone finality (~2–5s)** as the signal for marking on-chain
  events final (verified — sprintLength was cut 64→16 to shrink reorgs; there is no official fixed
  "32-block" bound, so don't hardcode one). Idempotent dedup-by-id absorbs Goldsky/Mirror re-emits.
- **v2 dual-indexing:** watch **both** exchange generations (`0x4bFb…`/`0xC5d5…` v1 and
  `0xE111…996B`/`0xe222…0F59` v2) and **both** collateral tokens (USDC.e + pUSD `0xC011…2DFB`);
  CTF `0x4D97…6045` is stable. v1-only tooling goes blind after Apr 28 2026.
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
- **Why:** Polymarket *subsidizes* makers — **zero maker fee + 20–25% taker-fee rebate + quadratic
  near-mid liquidity rewards**. Maker>taker return structure (Betfair) + biased taker flow.
- **How:** Avellaneda-Stoikov / Guéant-Lehalle-Fernandez-Tapia inventory-skewed quoting; reservation
  price skews with inventory and time-to-resolution; quote near mid to max liquidity-reward score.
- **Critical risk controls:** passive LP is *underwriting*, not spread capture (Palumbo) — cap
  terminal/resolution exposure, skew hard on inventory, and **pull quotes around event conclusion**
  (post-event/pre-oracle "frozen liquidity": NBA spreads hit ~7,532 bps; ~81% of apparent arbs are
  unexecutable). Avoid one-sided toxic flow (use the toxicity score).

### B. Mispricing / arbitrage (structural, capacity-limited)
- **B1 single-market:** YES+NO < $1 → buy the pair; capacity ~15 shares, half-life <1 min → must be
  fast and is self-limiting. **B2 neg-risk:** multi-outcome YES-sum ≠ 1 via NegRiskAdapter convert.
- **B3 fair-value deviation:** bet when market price deviates from de-vigged/ensembled external fair
  value beyond a threshold — strongest for **sports** (de-vig consensus odds, Shin) and **long-horizon
  politics** (poll ensemble + compression correction: a 70¢ week-out politics contract ≈ 83% true).
- **Caveat:** log capacity honestly; most cross-venue/stale arbs are unexecutable frozen liquidity.

### C. Fade-the-dumb-money (large, persistent, non-self-erasing)
- **Why:** ~3% of traders drive price discovery; the unskilled majority's losses fund them
  (Yale/LBS). Unlike sharp-following, this signal doesn't evaporate when observed.
- **How:** identify persistently-unskilled wallets point-in-time (EB-shrunk negative edge); when
  aggregate dumb-money flow pushes a market away from fair value (Strategy B3), **take the other
  side**. Pairs naturally with market-making (be the counterparty to biased flow).

### D. News-latency (automation race in the one genuine window)
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
  (~0.19 at 5 looks), so either use **group-sequential O'Brien-Fleming alpha-spending**, or
  preferably **e-values / confidence sequences** (anytime-valid — correct at *any* stopping time).
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
Live Goldsky project-id/v2 manifest coverage; deployed UMA liveness (2h vs 48h); `book.hash` algo
(read `py-clob-client`); exact v2 `OrderFilled` ABI (pull from the verified contract); 538 CSV
continuity; Arkham/Nansen pricing at our query volume. Treat all single-source magnitudes in the
research as directional, not as plug-in parameters.
