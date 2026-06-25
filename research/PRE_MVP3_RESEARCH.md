# Pre-MVP3 Research Synthesis

*Compiled 2026-06-25 from a 14-agent deep-research fan-out across insider detection, pricing/
mispricing, fair value, microstructure, on-chain data, forward-testing, and signal actionability.*
*Re-verified 2026-06-25 with a working sandbox egress allowlist: a 5-pillar parallel re-fetch
resolved the confidence flags below against primary sources. See **`VERIFICATION_LOG.md`** for the
per-claim outcome (verified / corrected / still-unverified) with primary URLs and old→new values.*

> **Sourcing status (updated after the verification pass):** the academic formulas (PSR, MinTRL,
> DSR, Lo SE, OFI R², Kalshi passthrough) and the Polymarket on-chain facts (v2 contracts, fee
> model, UMA liveness) have now been **byte-verified** against primary sources (arXiv PDFs,
> `docs.polymarket.com`, Polygonscan, reference-implementation code) — annotated **[VERIFIED]**
> inline. A minority of claims remain **snippet-confirmed** because the publisher returns origin
> anti-bot 403s (SSRN, ResearchGate, davidhbailey.com, Yale Insights, several `.edu`/news hosts) —
> annotated **[SNIPPET]**; these were cross-checked across ≥2 independent results. Corrected numbers
> are annotated **[CORRECTED]** and the refuted FLB-reversal claim is marked **[REFUTED]**. The
> still-blocked hosts are listed at the end of `VERIFICATION_LOG.md`; none were routed around.

---

## 0. The strategic conclusion (read this first)

The single most important finding cuts across every angle and **redirects MVP3's whole thesis**:

> **Detecting informed/insider activity is easy; *capturing* it is the hard part — and following
> it is a losing race.** Once a sharp/insider trade prints, its *permanent* price impact (Kyle
> 1985) is incorporated within seconds, the public WebSocket reveals trade direction only ~59% of
> the time ([VERIFIED] Dubach 2026, arXiv 2604.24366 — panel mean 0.615, CI [0.58,0.65]), MEV/HFT
> bots fill in milliseconds, and Polymarket charges a **category-based taker fee on a `p(1−p)`
> curve** ([VERIFIED] `docs.polymarket.com/trading/fees`) that taxes aggressive takers while
> rebating makers. The insider's fill **is** the signal, so a follower captures only the decayed
> residual minus fees and slippage.

The two **defensible** edges the literature actually supports are therefore:

1. **Be the fast actor in the multi-minute *news-incorporation* window** — prices update only
   ~0.64-for-one to a benchmark probability change, leaving multi-minute drift ([VERIFIED] Kalshi
   study, arXiv 2606.07811 — passthrough 0.63–0.64). The race is automation vs. slow humans, not
   copying a confirmed fill.
2. **Fade the identifiable *unskilled* cohort.** Yale/LBS analysis of 1.72M Polymarket accounts
   ($13.76B volume) finds **~3% of traders drive nearly all price discovery and accuracy**, and the
   unskilled majority's losses flow to them ([SNIPPET, cross-checked] Gómez-Cram, Guo, Jensen &
   Kung, LBS/Yale, Apr 2026: ~3.14% skilled, capturing >30% of gains; only ~12% of top raw-profit
   winners clear a 10,000-simulation skill bar; ~60% of "lucky" winners regress out-of-sample).
   Unlike the sharp-following signal (thin, front-run, half-hidden in alt-accounts), the dumb-money
   signal is **large, persistent, and not self-erasing**.

Plus two structural, capacity-limited edges: **mispricing/fair-value deviations** and **passive
market-making** (zero maker fees + rebates; makers profit as counterparty to biased flow).

So insider detection in MVP3 is best used **defensively** (flag toxic/insider flow to *avoid*
being its counterparty, and to *fade markets the dumb money is wrong about*) rather than as a
copy signal.

> **Verification verdict (2026-06-25 re-fetch):** the strategic conclusion is **unchanged** — every
> load-bearing pillar of it (insider's-fill-is-the-signal; ~59% feed-direction; ~0.64 news
> passthrough; ~3% skilled traders; subsidized market-making; capacity-bound arbitrage) **survived**
> primary-source verification. The corrections were to *numbers and citations*, not to the thesis.
> The one genuine reversal — the favorite-longshot bias is **classic, not reversed** — actually
> *reinforces* the long-horizon-mispricing edge (it is the same compression-toward-50% phenomenon),
> so it strengthens rather than weakens the fair-value strategy. See `VERIFICATION_LOG.md`.

---

## 1. Pillar A — Predicting insider / informed trading from on-chain data

**It happens, it's real, and it's prosecutable.** Documented cases: the DOJ-charged US soldier
([VERIFIED] MSgt Gannon Ken Van Dyke, justice.gov) who bet ~$33k across ~13 bets → ~$410k on the
Maduro capture using classified info; Israeli indictments for Iran-strike timing bets; Bubblemaps'
9-wallet cluster, **98% win rate over 80+ bets, $2.4M**, on US-military markets ([VERIFIED via
CBS/60 Minutes + Bloomberg] — [CORRECTED] the wallets were *created days before* the event, with
four "just days before"; the earlier "<24h" funding detail is not supported); the Columbia finding
that **~25% of Polymarket volume is wash trading** (≈45% of *sports* volume — [VERIFIED]
business.columbia.edu). The election whale "Théo" ([VERIFIED] 11 wallets, **>$85M** — revised up
from the earlier ~$48M; Polymarket "found no evidence of manipulation") was a **false positive** —
research-driven, not an insider — which is the central design warning.

**The recurring on-chain signatures (engineer these as features):**
- **Wallet freshness:** age < 48h, nonce ≤ 5, first trade > $1k (deployed-detector thresholds).
- **Funding-source clustering:** trace USDC/pUSD `Transfer` edges backward to a shared CEX deposit
  address (how Chainalysis tied Théo's 11 wallets). Use the **EVM deposit-address/sweep heuristic**
  (Victor FC 2020; `etherclust`), **not** Bitcoin co-spend. Stop traversal at known service clusters.
- **Concentration / narrow focus:** single-theme betting; large bets in low-probability outcomes
  (>2% of 24h volume or >5% of book depth); niche markets (<$50k/day).
- **Last-minute one-sided taking:** % of size in the 1–10 min before resolution.
- **Anomalous win rate:** p-value of observed win rate vs. chance (flag p<0.001 / >80%).
- **Sybil clusters:** funding-graph + **gas-provision sub-graph** (first-gas edges), Louvain/K-Core
  community detection + behavioral co-movement (the Arkham/Bubblemaps/Nansen/Trusta production
  method). ([CORRECTED] the earlier "GNN/GAT report 95–100% on chain/tree Sybil patterns" claim is
  **unsupported** — the cited SybilGAT paper, arXiv 2409.08631, is a *social-network* method
  reporting AUC ≈ 0.58–0.86, not blockchain chain/tree accuracy. Treat GNN Sybil detection as
  promising-but-unproven for our setting; rely on the funding/gas-graph + behavioral heuristics,
  which are the actual production methods.)

**Methods that transfer from TradFi (on-chain *improves* on them — trade direction & identity are
observable, eliminating trade-classification error):**
- **Event-study runup / CAR** (Meulbroek 1992): abnormal pre-event drift; on Polymarket, abnormal
  implied-probability move before the news `seendate`, attributable to *specific wallets*.
- **PIN** (Easley et al. 1996): order-imbalance MLE for probability of informed trading.
- **VPIN** (Easley-López de Prado-O'Hara 2012): volume-bucketed signed-flow toxicity — real-time
  "is this flow informed?" alarm. (Its flash-crash *predictive* claim is contested — Andersen-
  Bondarenko — so treat as a toxicity gauge, not a forecaster.)

**The flagship purpose-built source:** **Mitts & Ofir (2026), "From Iran to Taylor Swift"**
([VERIFIED, snippet — SSRN 6426778 anti-bot-blocked; confirmed via the Harvard corpgov mirror +
multiple outlets]) — a composite statistical screen over **>210,000** Polymarket wallet-market
pairs (range Feb 2024–Feb 2026) flagging a **69.9% win rate / ~$143M anomalous profit**, combining
**bet-size anomaly + profitability + pre-event timing + directional concentration**. The flagged
cohort's win rate exceeds a permutation null by **>60 standard deviations** — a strong, quotable
robustness figure. **Polysights** raised $1.5M to productize exactly this; **Chainalysis** now
partners with Polymarket on it.

**Hard limits:** attribution dead-ends at CEX deposit addresses and mixers; vendor labels
misattribute ("Ghost Clusters," USENIX 2025); composite multi-signal scoring is mandatory to avoid
Théo-style false positives. Tooling: Arkham API (`/intelligence/address_enriched`, `entity_predictions`,
`clusterIds`; transfers throttled — [SNIPPET] ~20 rps standard / 1 rps heavy endpoints, **not
byte-verified**), Nansen (Smart Money + Prediction-Markets category; [SNIPPET] free-plan calls cost
10× credits, **not byte-verified**), Dune `labels.addresses`, and the free **Chainalysis sanctions
oracle** ([VERIFIED] `isSanctioned(address)→bool`, same address on Polygon/Ethereum/BNB:
`0x40C57923924B5c5c5455c48D93317139ADDaC8fb`).

---

## 2. Pillar B — Evaluating pricing / mispricing from on-chain data

**Calibration:** Polymarket is broadly well-calibrated near resolution ([VERIFIED] self-reported
Brier **0.0627** at polymarket.com/accuracy; independent 0.06–0.18) but **systematically compressed
toward 50% at long horizons** — [CORRECTED] a 70¢ politics contract **one month out** implies a true
**~75%** (slope-dependent; ~83% only at a steeper calibration slope). [CORRECTED CITATION] Page &
Clemen, *The Economic Journal* 2013, 123(568):491–513 (**not** Management Science); the sharpest
numeric anchor is now **Le 2026, arXiv 2602.19520**, which documents the effect on Polymarket at
scale. **Domain-specific:** sports well-calibrated at 0–48h; politics chronically underconfident.
[REFUTED] The earlier "**reversed** favorite-longshot bias on Polymarket (low-prob overpriced)"
claim is **wrong** — Le 2026 finds the **classic** FLB, *same direction as racetracks*: favourites
underpriced, longshots overpriced, worsening with horizon. This is internally consistent with the
long-horizon compression toward 50% (favourites pulled down, longshots pulled up). An FLB tilt is
therefore principled in the **standard** direction; it still must be platform-calibrated.

**Internal arbitrage (strongest, but capacity-bound):** ~**$40M** extracted Apr 1 2024–Apr 1 2025
([VERIFIED] arXiv 2508.03474), mostly single-market **YES+NO < $1** and neg-risk multi-outcome
**YES-sum ≠ 1**. But per-opportunity it's small ([CORRECTED, re-attributed to arXiv 2605.00864 —
Polymarket NBA] median **101.01 bps**), short-lived (median duration **3.6s single / 16s
combinatorial** — [CORRECTED] the earlier "half-life <1 min as λ fell 0.52→0.01" is **not in either
paper**; remove it), and **liquidity-capped** (**76.9%** of combinatorial opportunities constrained
to an average executable size of just **14.8 shares**). Only **7 valid in-game arbs** were found
across 75M+ snapshots.

**Cross-venue:** [DOWNGRADED — unverified] the earlier "~6% of events cross-listed; persistent
**2–4% deviations ≥1h**" figures could not be sourced — *neither* arbitrage paper studies
cross-venue/cross-platform arbitrage, and the deviations they do observe last **seconds, not hours**.
Cross-venue arb remains *structurally* plausible (semantic non-fungibility, geo/KYC, USD↔USDC
settlement, UMA-vs-named-source resolution risk) but the magnitudes are now **speculation**, not
evidence; capturable only with funded accounts on both venues; fees decisive everywhere.

**Fair value from external anchors:** markets beat polls ~74% long-horizon (election-eve MAE
~1.33pts — [VERIFIED, snippet] Berg-Nelson-Rietz 2008, *Int. J. Forecasting* 25(2)); **538-type
models roughly tie the market** ([VERIFIED direction] Sethi et al. CI'25 — no model beat the market
on the headline 2024 contract; the exact Brier 0.108 vs 0.109 is snippet-only); **Shin's method**
([VERIFIED] Shin 1992/1993, *Economic Journal*) is the best de-vig of sportsbook odds → fair
probability (beats basic normalization in 217/412 book-competition pairs); **equal-weight
market+model ensembles** beat both ~40% of days ([UNSOURCED] flag); superforecasters beat markets
15–30% on Brier ([VERIFIED] Good Judgment / Tetlock). → A fair-value engine that de-vigs/ensembles
external probabilities and bets deviations is principled, especially for sports (de-vig consensus
odds) and politics (poll aggregators + long-horizon compression correction).

**Statistical dynamics:** roughly a martingale for *anticipated* news, but violated predictably —
**~0.64 news passthrough with multi-minute drift** ([VERIFIED] arXiv 2606.07811, passthrough
0.63–0.64; underreaction → tradable), **overreaction to *surprises*** ([VERIFIED] Choi & Hui 2014,
JEBO), ~50% open-to-close reversal in pre-game lines ([VERIFIED] Moskowitz 2021, *J. Finance*
76(6):3153 — reversal coefficient −0.50; note this is overreaction-reversal specifically, not
generic "negative HF autocorrelation"). Volatility *rises* into resolution (non-stationary).

---

## 3. Microstructure (supports mispricing + market-making)

- **OFI predicts short-term moves** ([VERIFIED] Cont, Kukanov & Stoikov, arXiv **1011.6402** — avg
  **R²=65%** for order-flow imbalance vs **32%** for trade imbalance, ~48 of 50 stocks ≥50% R²;
  *not* the "44/50" earlier cited, and the earlier arXiv id 1011.4087 was an unrelated physics
  paper). The edge **decays in seconds** (autocorrelations vanish after ~10s) → best used as a
  **maker/queue-positioning** signal, not taker arbitrage (the maker>taker framing is reasoned
  inference, not a stated result of the paper).
- **Stoikov micro-price** ([VERIFIED] Stoikov 2018, *Quant. Finance* 18(12):1959 — `P_micro = M +
  g(I,S)`, a martingale "fair price") is the best short-horizon fair value.
- **Critical Polymarket caveat:** [VERIFIED] public-feed trade direction matches on-chain ground
  truth only **~59%** of the time (Dubach 2026, arXiv 2604.24366 — panel mean 0.615, CI [0.58,0.65];
  vs ~80% Lee-Ready on Nasdaq), and the effective half-spread flips sign on **50–67%** of markets
  (67%/50% across two 7-day windows) — **signed-flow signals MUST be built from on-chain data**, not
  the WebSocket.
- Depth ≈ uniform grid (not top-of-book) [VERIFIED] (depth-concentration 0.137 vs 0.10 uniform
  benchmark). [CORRECTED] Spreads are quoted in **bps, not "2–5¢"** — ~**400 bps** in the central
  [0.4,0.6] range, **1,300–1,800 bps** below 0.10 (Dubach). The earlier "**~3.5× more volume to move
  price than Kalshi**" figure is **not in the source — unverified**. **Maker > taker** return
  structure ([snippet] Betfair, Whelan) + Polymarket's [VERIFIED] **zero maker fees + 20% (crypto) /
  25% (other) rebates + quadratic near-mid liquidity rewards** (`S = ((v−s)/v)²·b`, single-sided
  ÷ c=3) make passive market-making the most structurally robust candidate.
- Abnormal trade size predicts resolution, strengthening near resolution ([VERIFIED] Kyle 1985,
  *Econometrica* 53:1315 — single λ permanent-impact parameter) → ties microstructure back to
  insider detection.

---

## 4. On-chain & off-chain data (the substrate)

**On-chain (Polygon):** [VERIFIED, Polygonscan] ConditionalTokens ERC-1155
`0x4D97DCd97eC945f40cF65F87097ACe5EA0476045` (stable; `TransferSingle/Batch` = holdings, no price);
**CTF Exchange `OrderFilled`** = the trade tape (price = collateral/token ratio; `makerAssetId==0`
side = BUY). **Attribute on `OrderFilled.maker` (the source of funds), never the relayer `tx.from`**
— [VERIFIED] when a taker order sweeps multiple makers, `taker` is the **Exchange contract**, so
per-fill attribution must use each `OrderFilled.maker`. Proxy↔EOA is **CREATE2-deterministic** (Safe
`getOwners()` or forward index). [VERIFIED] UMA resolution **undisputed liveness = 2 hours (7200s)**
on the fast path (the **48h** figure is the UMA **DVM voting** phase, which occurs *only* after a
second dispute — so do not wait 48h by default); a price move *before* the proposal tx is itself a
runup signal.

> ⚠️ **April 28 2026 v2 migration is load-bearing** ([VERIFIED] `docs.polymarket.com/v2-migration`,
> `/resources/contracts`, Polygonscan): new exchange addresses (v2 CTF Exch
> `0xE111180000d2663C0091e4f400237545B87B996B`, v2 NegRisk Exch
> `0xe2222d279d744050d28e00520010520000310F59`), collateral **USDC.e
> (`0x2791Bca1f2de4661Ed88A30C99A7a9449Aa84174`) → pUSD
> (`0xC011a7E12a19f7B1f670d46F03B03f3342E82DFB`)**, **assembly-emitted events with a NEW topic0**,
> a restructured order struct (nonce/expiration/feeRateBps removed; `timestamp`/`metadata`/`builder`
> added; EIP-712 domain version 1→2), and **match-time fees**.
>
> **[CORRECTED — critical for the collector] v1 and v2 do NOT share the `OrderFilled` signature.**
> v2 `OrderFilled` topic0 = `0xe92c22722d9c284034b6c9f5aaec018edb3e593c0e084900b6b9d390a1182a0b`,
> `OrdersMatched` topic0 = `0x787a2e12f4a55b658b8f573c32432ee11a5e8b51677d1e1e937aaf6a0bb5776e`, and
> v2 emits a **separate `FeeCharged` event** (fees are no longer a field on the signed order). v1
> `OrderFilled(bytes32 orderHash, address maker, address taker, uint256 makerAssetId, uint256
> takerAssetId, uint256 makerAmountFilled, uint256 takerAmountFilled, uint256 fee)` is distinct. A
> **dual decoder is mandatory** — index **both** generations + **both** collateral tokens; v1-only
> tooling silently goes blind after that date. (Pull the byte-exact v2 ABI from the verified
> Polygonscan source tab before hard-coding the decoder; the v2 param list here is inferred from the
> event index + assembly-emit pattern.)

**APIs:** [VERIFIED] Data API (`/positions`,`/trades`,`/activity`,`/holders`,`/value` — public, any
wallet) is the real-time backbone; Gamma for metadata/ID mapping; CLOB `/book`,`/prices-history`,
`/midpoint`,`/spread` + market WebSocket (`book`/`price_change`/`last_trade_price`/`tick_size_change`)
for order-book capture; Goldsky subgraphs / Mirror and Dune
(`polymarket_polygon.market_trades`/`positions`) for historical joins. Rate limits: CLOB market data
**1,500/10s/endpoint** (use WS for continuous capture), Data API **1,000/10s**, Goldsky **~50/10s**.
[CORRECTED] The "REST L2 backfill is gone" fact is real but applies to **`/orderbook-history`**
(stopped emitting new snapshots ~**Feb 20 2026**, per nautilus_trader #3635), not `/prices-history`;
the "`/prices-history` empty for resolved markets" detail is **unverified**. Either way the
operational conclusion holds: **historical order books must come from YOUR captured WebSocket
stream.**

**Off-chain anchors (free/cheap):** [VERIFIED] GDELT DOC 2.0 (free, ~15-min, treat `seendate` as an
interval), The Odds API (de-vig consensus from 40+ books; **free tier = 500 *credits*/mo**, not 500
requests), ESPN hidden JSON (free sports ground truth). [CORRECTED — DEAD ANCHOR] **FiveThirtyEight
shut down 2025-03-05; its live poll CSVs are gone** (the `polls` dir last updated 2024-09-13) — do
**not** architect any anchor on 538 feeds. There is no equivalent free, machine-readable raw-poll
feed; for politics, lean on The Odds API / market-implied + manual poll-aggregator ingestion.
Normalize all to UTC; record each source's timestamp *semantics*.

**Storage/architecture:** **bitemporal** (valid-time + transaction-time) for leakage-free as-of
queries; Parquet+DuckDB cold archive / ClickHouse for scans / TimescaleDB for one-Postgres live+hist;
[CORRECTED] **Polygon's max reorg depth is ~32 blocks** (post-PIP-5, down from 128; "32" is the
ceiling, not a floor) → use a ~30-block (~1 min) confirmation buffer + idempotent dedup-by-id;
Goldsky Mirror is the most production-ready off-the-shelf lake; `SII-WANGZJ/Polymarket_data` (~1.1B
records, ~107GB incremental Parquet) is the closest OSS reference collector.

---

## 5. Forward-test methodology (the 1 / 2 / 6-month evaluation)

**Why forward > historical:** fixing the universe at t0 kills survivorship (the bias that wrecked
mvp1/mvp2 on the cohort axis); point-in-time decisions kill look-ahead. **Limits:** paper trading
can't model own market impact ([VERIFIED] square-root law: impact ∝ √Q, `≈ Y·σ·√(Q/V)`, Y=O(1);
Kyle-Obizhaeva), reflexivity, or true slippage — a known ceiling on credibility. (The "522× paper
vs −49.5% live" practitioner figure is **unsourced — treat as illustrative/apocryphal**.)

**Statistical power — the sobering math:** required sample scales as **1/SR²** [VERIFIED]. **PSR /
MinTRL / DSR** (Bailey & López de Prado) — formulas now **byte-verified** against the reference
implementation; use these exact forms:
- `PSR(SR*) = Φ[ (SR_hat − SR*)·√(T−1) / √(1 − γ3·SR_hat + ((γ4−1)/4)·SR_hat²) ]` (γ3 = skew, γ4 =
  raw kurtosis).
- `MinTRL = 1 + [1 − γ3·SR_hat + ((γ4−1)/4)·SR_hat²]·(Z_α/(SR_hat − SR*))²` — grows as the edge
  approaches benchmark and with negative skew / fat tails.
- `DSR = PSR(SR*)` evaluated at `SR* = √Var[SR]·[(1−γ)·Φ⁻¹(1−1/N) + γ·Φ⁻¹(1−1/(N·e))]`, γ=0.5772
  (Euler-Mascheroni), N = independent trials.

**Metric stability differs sharply:** **win rate** (binomial SE √(p(1−p)/n)) stabilizes fastest
(~100 trades → ~5pp [VERIFIED: √(0.25/100)=0.05]); **Sharpe** converges slowly ([VERIFIED] Lo 2002
SE = √((1+SR²/2)/T), arXiv 1808.04233); **max drawdown is biased and *grows* with window length**
([VERIFIED] Magdon-Ismail et al. 2004 — E[MaxDD] grows log(T)/√T/linear with drift sign) — not
comparable across horizons. → **A 1–2 month window can bound win rate but cannot distinguish a true
Sharpe or worst-case drawdown from noise.** Report hit rate first; treat early Sharpe/DD as
provisional.

**Peeking without inflation:** [CORRECTED] monthly looks at α=0.05 inflate Type-I error to **~0.14
at 5 looks and ~0.19 at 10 looks** (Armitage 1969 — the earlier "~0.19 at 5 looks" conflated the two).
Use **group-sequential alpha-spending (O'Brien-Fleming)** for pre-registered 1/2/6-mo looks, or
better, **e-values / confidence sequences** ([VERIFIED] Ramdas-Grünwald-Vovk-Shafer, arXiv
2210.01948 — valid at *any* stopping time, optional stopping/continuation for any reason — exactly
what monthly monitoring needs). Track **N configurations tried** and report a **Deflated Sharpe**,
not a raw one ([VERIFIED] Harvey-Liu-Zhu 2016, RFS 29(1):5–68: t-stat hurdle > 3.0, not 2.0).

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
