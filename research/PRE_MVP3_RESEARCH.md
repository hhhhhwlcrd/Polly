# Pre-MVP3 Research Synthesis

*Compiled 2026-06-25 from a 14-agent deep-research fan-out across insider detection, pricing/
mispricing, fair value, microstructure, on-chain data, forward-testing, and signal actionability.*

> **VERIFICATION STATUS (updated 2026-07-01):** a primary-source verification pass has now run
> (see [`VERIFICATION_LOG.md`](VERIFICATION_LOG.md)). The forward-test formulas (PSR/MinTRL/DSR/
> Kelly), all on-chain addresses/fees/events, and the Polymarket-empirical figures (arbitrage,
> frozen liquidity, Dubach 59%, Kyle λ, news passthrough) are now **primary-verified**. Ten
> attribution/label/figure errors were **corrected** — the corrected values are inlined below and
> tabulated in the log. Items still resting on blocked hosts (Mitts-Ofir 69.9%, Page-Clemen
> 4.7–10.9pp, FLB dollar magnitudes, ensemble ~40%) are flagged inline. **No strategic conclusion
> changed.** The original text was built from search snippets while WebFetch was 403-blocked.

---

## 0. The strategic conclusion (read this first)

The single most important finding cuts across every angle and **redirects MVP3's whole thesis**:

> **Detecting informed/insider activity is easy; *capturing* it is the hard part — and following
> it is a losing race.** Once a sharp/insider trade prints, its *permanent* price impact (Kyle
> 1985) is incorporated within seconds, the public WebSocket reveals trade direction only ~59% of
> the time (Dubach 2026, arXiv 2604.24366), MEV/HFT bots fill in milliseconds, and Polymarket's
> new dynamic taker fee was introduced *specifically to tax latency arbitrage*. The insider's fill
> **is** the signal, so a follower captures only the decayed residual minus fees and slippage.

The two **defensible** edges the literature actually supports are therefore:

1. **Be the fast actor in the multi-minute *news-incorporation* window** — prices update only
   ~0.64-for-one to a benchmark probability change, leaving multi-minute drift (Kalshi study,
   arXiv 2606.07811). The race is automation vs. slow humans, not copying a confirmed fill.
2. **Fade the identifiable *unskilled* cohort.** Yale/LBS analysis of 1.72M Polymarket accounts
   ($13.76B volume) finds **~3% of traders drive nearly all price discovery and accuracy**, and the
   unskilled majority's losses flow to them. Unlike the sharp-following signal (thin, front-run,
   half-hidden in alt-accounts), the dumb-money signal is **large, persistent, and not
   self-erasing**.

Plus two structural, capacity-limited edges: **mispricing/fair-value deviations** and **passive
market-making** (zero maker fees + rebates; makers profit as counterparty to biased flow).

So insider detection in MVP3 is best used **defensively** (flag toxic/insider flow to *avoid*
being its counterparty, and to *fade markets the dumb money is wrong about*) rather than as a
copy signal.

---

## 1. Pillar A — Predicting insider / informed trading from on-chain data

**It happens, it's real, and it's prosecutable.** Documented cases: the DOJ-charged US soldier who
bet ~$33k → ~$410k on the Maduro capture using classified info; Israeli indictments for Iran-strike
timing bets; Bubblemaps' 9-wallet cluster, **98% win rate over 80+ bets, $2.4M**, on US-military
markets with wallets funded <24h before events; the Columbia finding that **~25% of Polymarket
volume is wash trading** (≈45% of *sports* volume). The election whale "Théo" (11 wallets, ~$85M)
was a **false positive** — research-driven, not an insider — which is the central design warning.

**The recurring on-chain signatures (engineer these as features):**
- **Wallet freshness:** age < 48h, nonce ≤ 5, first trade > $1k (deployed-detector thresholds;
  `pselamy/polymarket-insider-tracker`. *[corrected: no "$5k whale/$25k mega" tiers exist in that
  detector — only fresh-wallet $1k, a $10k large-trade bonus, and the 2%/5% size anomaly below.]*)
- **Funding-source clustering:** trace USDC/pUSD `Transfer` edges backward to a shared CEX deposit
  address (how Chainalysis tied Théo's 11 wallets). Use the **EVM deposit-address/sweep heuristic**
  (Victor FC 2020; `etherclust`), **not** Bitcoin co-spend. Stop traversal at known service clusters.
- **Concentration / narrow focus:** single-theme betting; large bets in low-probability outcomes
  (>2% of 24h volume or >5% of book depth); niche markets (<$50k/day).
- **Last-minute one-sided taking:** % of size in the 1–10 min before resolution.
- **Anomalous win rate:** p-value of observed win rate vs. chance (flag p<0.001 / >80%).
- **Sybil clusters:** funding-graph + **gas-provision sub-graph** (first-gas edges), Louvain/K-Core
  community detection + behavioral co-movement (the Arkham/Bubblemaps/Nansen/Trusta production
  method). ML detectors work: a LightGBM subgraph model reports all metrics **>0.9** on 193,701
  addresses (arXiv 2505.09313). *[corrected: the earlier "95–100% chain/tree" figures were not in
  that paper.]*

**Methods that transfer from TradFi (on-chain *improves* on them — trade direction & identity are
observable, eliminating trade-classification error):**
- **Event-study runup / CAR** (Meulbroek 1992): abnormal pre-event drift; on Polymarket, abnormal
  implied-probability move before the news `seendate`, attributable to *specific wallets*.
- **PIN** (Easley et al. 1996): order-imbalance MLE for probability of informed trading.
- **VPIN** (Easley-López de Prado-O'Hara 2012): volume-bucketed signed-flow toxicity — real-time
  "is this flow informed?" alarm. (Its flash-crash *predictive* claim is contested — Andersen-
  Bondarenko — so treat as a toxicity gauge, not a forecaster.)

**The flagship purpose-built source:** **Mitts & Ofir (2026), "From Iran to Taylor Swift"** — a
statistical screen over **~210k Polymarket wallet-market pairs** (verified) flagging **~$143M
anomalous profit** (verified via two citing arXiv papers), combining abnormal win rate + abnormal
profit + concentrated timely positioning. *[The **69.9%** flagged win rate is from the SSRN/corpgov
abstract only — SSRN and Harvard corpgov were host-blocked this session, so it is unverified against
the primary PDF.]* **Polysights** raised $1.5M to productize
exactly this; **Chainalysis** now partners with Polymarket on it.

**Hard limits:** attribution dead-ends at CEX deposit addresses and mixers; vendor labels
misattribute ("Ghost Clusters," USENIX 2025); composite multi-signal scoring is mandatory to avoid
Théo-style false positives. Tooling: Arkham API (`/intelligence/address_enriched`, `entity_predictions`,
`clusterIds`; transfers throttled to 1 rps), Nansen (Smart Money + Prediction-Markets category;
~100 credits/label call), Dune `labels.addresses`, and the free **Chainalysis sanctions oracle**
(`isSanctioned`, Polygon `0x40C5…c8fb`).

---

## 2. Pillar B — Evaluating pricing / mispricing from on-chain data

**Calibration:** Polymarket is broadly well-calibrated near resolution (self-reported Brier ~0.06;
independent 0.06–0.18) but **systematically compressed toward 50% at long horizons** — a 70¢
politics contract a week out implies a true ~83% (Page & Clemen 2013; Le 2026). **Domain-specific:**
sports well-calibrated at 0–48h; politics chronically underconfident. **Favorite-longshot bias on
Polymarket runs in the *classic* direction** (longshots overpriced / favorites underpriced,
compression toward 50%; Politics calibration slope **1.31**, Le 2026, arXiv 2602.19520). *[corrected:
the earlier "reversed FLB" label and the "Reichenbach & Walther" attribution were wrong.]* Any FLB
tilt must still be platform- and category-calibrated (Weather/Sports can flip at some horizons).

**Internal arbitrage (strongest, but capacity-bound):** **$39.59M (~$40M)** extracted
Apr2024–Apr2025 (verified) — single-market *rebalancing* ≈ **$10.6M**, cross-market *combinatorial*
≈ **$29.0M** *[corrected: labels were previously swapped]*; mechanisms are **YES+NO < $1** and
neg-risk multi-outcome **YES-sum ≠ 1**. Per-opportunity small (~100 bps), short-lived (half-life
**< 1 min** as Kyle λ fell **0.518→0.01**, verified). **Capacity is retail-scale — but the ~15-share
/ 76.9% figures belong to the NBA in-game study** (arXiv 2605.00864: 76.9% of combinatorial ops
capped at avg 14.8 shares), *not* the aggregate arbitrage paper; there is no "62–78% execution-fail"
figure in the source.

**Cross-venue:** ~6% of events are cross-listed; semantically-equivalent markets show persistent
**2–4% deviations (≥1h)** due to *structural* frictions (semantic non-fungibility, geo/KYC,
USD↔USDC settlement, UMA-vs-named-source resolution risk), not information. Capturable only with
funded accounts on both venues; fees decisive everywhere.

**Fair value from external anchors:** markets beat polls ~74% long-horizon (election-eve MAE
~1.33pts); **538-type models roughly tie the market** (Brier 0.108 vs 0.109); **Shin's method** is
the best de-vig of sportsbook odds → fair probability; **equal-weight market+model ensembles** beat
both ~40% of days; superforecasters beat markets ~30% on Brier. → A fair-value engine that
de-vigs/ensembles external probabilities and bets deviations is principled, especially for sports
(de-vig consensus odds) and politics (poll aggregators + long-horizon compression correction).

**Statistical dynamics:** roughly a martingale for *anticipated* news, but violated predictably —
**~0.64-for-one news passthrough with multi-minute drift** (verified; underreaction → tradable),
**overreaction to *surprises*** (Choi-Hui), open-to-close reversal in pre-game lines (Lou-Polk-Skouras
"A Tug of War," JFE 2019 — *[corrected: previously mis-attributed to Moskowitz; the ~50% magnitude is
unconfirmed]*), negative high-frequency autocorrelation (mean reversion). Volatility *rises* into
resolution (non-stationary).

---

## 3. Microstructure (supports mispricing + market-making)

- **OFI/OBI predict short-term moves but the edge is *smaller than the spread*** → a **maker/queue-
  positioning** signal, not taker arbitrage. Decays in seconds.
- **Stoikov micro-price** (mid adjusted by imbalance+spread) is the best short-horizon fair value.
- **Critical Polymarket caveat:** public-feed trade direction matches on-chain ground truth only
  **~59%** of the time, and the effective half-spread flips sign on 50–67% of markets — **signed-flow
  signals MUST be built from on-chain data**, not the WebSocket.
- Depth ≈ uniform geometric grid (not top-of-book); spreads 2–5¢; ~3.5× more volume to move price
  than Kalshi. **Maker > taker** return structure (Betfair evidence) + Polymarket's **zero maker
  fees + 20–25% rebates** make passive market-making the most structurally robust candidate.
- Abnormal trade size predicts resolution, strengthening near resolution (Kyle) → ties microstructure
  back to insider detection.

---

## 4. On-chain & off-chain data (the substrate)

**On-chain (Polygon):** ConditionalTokens ERC-1155 `0x4D97…6045` (stable; `TransferSingle/Batch` =
holdings, no price); **CTF Exchange `OrderFilled(maker,taker,makerAssetId,takerAssetId,…)`** = the
trade tape (price = collateral/token ratio; `assetId==0` side = buy/sell). **Attribute on
`OrderFilled.maker` (the proxy/funder), never the relayer `tx.from`** (all verified vs docs +
PolygonScan). Proxy↔EOA is **CREATE2-deterministic** — but the derivation differs by factory: legacy
Safe/Magic proxies use `salt=keccak256(owner)` (Safe also resolvable via `getOwners()`), while the
**current Deposit Wallet Factory** (`0x0000…Cc07`) uses `salt=keccak256(abi.encode(factory,
walletId))` with beacon/UUPS clones — use the documented `deriveDepositWalletAddress()`, don't
hardcode the old salt. UMA resolution uses a **2h liveness** default (verified; the 48h figure is the
*separate* post-dispute DVM voting phase); a price move *before* the OO proposal tx is a runup signal.

> ⚠️ **April 28 2026 v2 migration is load-bearing:** new exchange addresses (`0xE111…996B`,
> `0xe222…0F59`), collateral **USDC.e → pUSD** (`0xC011…2DFB`), assembly-emitted events, new order
> struct, **match-time fees**. Index **both** generations + **both** collateral tokens; v1-only
> tooling silently goes blind after that date.

**APIs:** Data API (`/positions`,`/trades`,`/activity`,`/holders`,`/value` — public, any wallet) is
the real-time backbone; Gamma for metadata/ID mapping; CLOB `/book`,`/prices-history` + market
WebSocket (`book`/`price_change`/`last_trade_price`) for order-book capture; Goldsky subgraphs /
Mirror and Dune (`polymarket_polygon.market_trades`/`positions`) for historical joins. Rate limits:
CLOB market data 1,500/10s/endpoint (use WS for continuous capture), Data API 1,000/10s, Goldsky
~50/10s. **`/prices-history` is empty for resolved markets and REST L2 backfill is gone — historical
order books must come from YOUR captured WebSocket stream.**

**Off-chain anchors (free/cheap):** GDELT DOC 2.0 (free, ~15-min, treat `seendate` as an interval),
The Odds API (de-vig consensus), ESPN hidden JSON (free sports ground truth), 538 poll CSVs
(continuity uncertain post-2025). Normalize all to UTC; record each source's timestamp *semantics*.

**Storage/architecture:** **bitemporal** (valid-time + transaction-time) for leakage-free as-of
queries; Parquet+DuckDB cold archive / ClickHouse for scans / TimescaleDB for one-Postgres live+hist;
**Polygon has deep reorgs (32+ blocks)** → confirmation buffer + idempotent dedup-by-id; Goldsky
Mirror is the most production-ready off-the-shelf lake; `SII-WANGZJ/Polymarket_data` (1.1B records,
incremental Parquet) is the closest OSS reference collector.

---

## 5. Forward-test methodology (the 1 / 2 / 6-month evaluation)

**Why forward > historical:** fixing the universe at t0 kills survivorship (the bias that wrecked
mvp1/mvp2 on the cohort axis); point-in-time decisions kill look-ahead. **Limits:** paper trading
can't model own market impact (square-root law), reflexivity, or true slippage — a known ceiling on
credibility. (One practitioner engine: 522× paper vs −49.5% live.)

**Statistical power — the sobering math:** required sample scales as **1/SR²**. **PSR/MinTRL**
(Bailey-López de Prado): MinTRL grows as the edge approaches benchmark and with negative skew / fat
tails. **Metric stability differs sharply:** **win rate** (binomial SE √(p(1−p)/n)) stabilizes
fastest (~100 trades → ~5pp); **Sharpe** converges slowly (Lo 2002 SE ≈ √((1+SR²/2)/T)); **max
drawdown is biased and *grows* with window length** — not comparable across horizons. → **A 1–2
month window can bound win rate but cannot distinguish a true Sharpe or worst-case drawdown from
noise.** Report hit rate first; treat early Sharpe/DD as provisional.

**Peeking without inflation:** monthly looks at α=0.05 inflate Type-I error (~0.19 at 5 looks).
Use **group-sequential alpha-spending (O'Brien-Fleming)** for pre-registered 1/2/6-mo looks, or
better, **e-values / confidence sequences** (anytime-valid; valid at *any* stopping time — exactly
what monthly monitoring needs). Track **N configurations tried** and report a **Deflated Sharpe**,
not a raw one (Harvey-Liu-Zhu: t-stat hurdle > 3.0, not 2.0).

**Harness:** record every intended trade with the **point-in-time book**, simulate fills by
**walking the recorded L2** (not mid), log actual fills from the `user` WS as ground truth. ABIDES /
NautilusTrader (research-live parity) are the reference designs.

---

## 6. What this means for MVP3 (handoff to the design doc)

1. **Build the always-on collector first** (it's the asset that makes everything else possible): full
   order books + trades + on-chain `OrderFilled`/transfers + funding graph + resolutions + off-chain
   anchors, bitemporally, fixing the market universe at t0.
2. **Ship strategies in robustness order**, not glamour order: market-making & mispricing/arb
   (structural) → fade-the-dumb-money (large persistent signal) → news-latency (automation race) →
   insider detection used **defensively** (toxicity filter), not as a copy signal.
3. **Evaluate by forward paper-trading at 1/2/6 months** with anytime-valid statistics, foregrounding
   win rate, deflating the Sharpe, and stating MinTRL honestly.

See **`MVP3_DESIGN.md`** for the concrete data schema, collector architecture, strategy specs, and
forward-test plan.
