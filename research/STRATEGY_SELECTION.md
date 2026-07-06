# Strategy Selection — Six-Angle Deep Research Synthesis

*Compiled 2026-07-06 from six parallel deep-research runs (plus nine banked sub-studies) aimed at
one question: **which trading strategy should Polly actually run?** Builds on the verified
`PRE_MVP3_RESEARCH.md` / `MVP3_DESIGN.md` and the mvp1/mvp2 negative results. Where this document
contradicts the earlier research, this document supersedes it — the two material supersessions are
flagged ⚠️ OVERTURNED below.*

**Sourcing:** load-bearing numbers are byte-fetched from primary sources (arXiv PDFs parsed
locally, docs.polymarket.com, live gamma-API pulls dated 2026-07-06, exchange Solidity source)
unless flagged `[snippet]`. Full per-angle source lists in §9.

---

## 0. The answer

> **Run a two-core portfolio: (1) a mid-horizon calibration harvest (buy 65–90¢ favourites,
> 5–35 days to settlement, politics + geopolitics, maker-first) as the directional core, and
> (2) rewards-harvesting passive market-making in mid-tail reward pools as the flow core —
> with the dumb-money/toxicity flow index as an overlay (filter + confirmation), not a
> standalone strategy. Kill the automated news-latency play. Park sports fair-value taker
> trading. Expected blended net return on a $25–100k book: ~10–30%/yr against a ~7–11%/yr
> hurdle, with a fat left tail that the sizing rules below exist to contain.**

Why this shape: every "be fast" edge examined (news reaction, in-play sports, copy/consensus,
internal arb) is either bot-saturated (3.6s median arb persistence; ~9M fills/day), structurally
blocked (matching delays protect makers from takers), or — decisively — **negative after real
execution costs by its own supporting evidence**. Every surviving edge is a "be the house / be
patient" edge: collect subsidies, warehouse binary risk the crowd re-creates, and avoid being
anyone's exit liquidity.

---

## 1. The hurdle rate (what any strategy must clear)

- Capital on Polymarket is **fully collateralized, zero leverage, zero yield**: pUSD pays holders
  nothing (Polymarket keeps the ~T-bill float yield on ~$500M); "Holding Rewards" pay 3.25%
  annualized on only ~19 curated long-dated markets — ~50bp *below* the 3-mo T-bill (3.76%,
  Jul 2026).
- The market itself reveals the hurdle: **Gebele & Matthes 2026** (arXiv 2605.31431, byte-fetched)
  measure an **annualized settlement wedge of ~3.1–6.9%** — near-certain contracts trade below fair
  value by exactly the lockup discount. Prices are *discounted probabilities*.
- Platform risk adds a premium: UMA/resolution integrity (~0.3–0.7%/yr expected loss budget, >5%
  single-event tail), pUSD admin-pause + USDC depeg passthrough, geo-restriction expansion
  (~14 → 40+ jurisdictions), operational/custody (two real incidents: Dec 2025 Magic-auth drains,
  May 2026 internal-key compromise — both operational, never a contract exploit).

**Required net return ≈ 7–11%/yr on deployed capital.** Anything below that is worse than T-bills
once platform risk is priced. Two corollaries: (a) all 1-month-plus near-certainties (93–97¢) are
*correctly priced* — their "cheapness" IS the wedge; (b) capital turnover matters as much as
per-trade edge — rank trades by **growth per unit time**, not per bet (G&M's rule: haircut every
edge by `r_q·τ`).

---

## 2. Core strategy #1 — Mid-horizon calibration harvest (highest-conviction directional edge)

**⚠️ Reframed from the pre-MVP3 version.** The Polymarket-specific calibration slopes
(Le 2026, arXiv 2602.19520, Table 15, byte-fetched) are much weaker than the headline
cross-platform numbers the earlier research quoted:

| Domain × horizon (Polymarket) | Slope b | Implication |
|---|---|---|
| Politics 2d–1wk | 1.98 | strongest bin — but 2024-election-contaminated, halve it |
| Politics 1wk–1mo | **1.68** | **the core trade** |
| Politics 1mo+ | **1.086** | ≈ inside the settlement wedge → **dead** |
| Sports 1mo+ | 1.32 | marginal, maker-only (3% fee) |
| Crypto 1mo+ | 1.06 | dead (7% fee) |

So the harvest is **not** "buy long-horizon favourites" — long-horizon politics favourites earn
roughly the wedge (no alpha). The bias that *exceeds* the wedge by an order of magnitude lives at
**65–90¢ × 5–35 days to settlement**: slope-implied +8–14¢ per trade against a wedge of ~0.3¢ and
fees of 0–0.6% (politics 4% category rate ≈ 0.51¢/share at 85¢; geopolitics 0%).

**The trade:** buy the favourite side (YES or NO — "selling a longshot" is the same trade via the
complement) at 65–90¢, 5–35 days to settlement, maker-first (zero fee + rebate, never cross >1.5¢
of spread), hold to fee-free redemption, recycle capital 6–10×/yr.

**Expected net: ~8–25%/yr on deployed capital at $10–100k**, after a deliberate ×0.5 haircut on
measured slopes (2024-cycle sample concentration), −1–2%/yr adverse selection on maker fills,
−0.5%/yr UMA/wording loss budget, ~70% deployment. Decays toward T-bill+5% at $500k (you become
the marginal buyer of the whole band; ~30–80 qualifying markets exist at a time, ~$5–25k
absorbable each).

**Risk shape: short vol.** 20 independent positions at true p≈0.8 ⇒ ~3% chance of a −20–25%
drawdown *before* correlation; politics clusters resolve together. Hence the hard rules:
≥20 positions, ≤5%/market, **≤15% per resolution cluster** (same election / decision / war),
≤40%/category, 20–30% cash buffer, and a strict **UMA screen** (skip subjective wording —
"agree to", "deal", "substantially" — single-source or map-based criteria; the March 2025
Ukraine-minerals whale-forced resolution with no refunds is the canonical trap, and disputes
concentrate in exactly the fee-free geopolitics wording the strategy prefers).

**Kill-risks:** (1) the measured slope is partly one correlated 2024-cycle draw — a
longshots-win cycle turns the year into a drawdown; (2) UMA integrity; (3) post-publication
crowding (wedges and spreads already compressed post-2024; Le 2026 and G&M publish the recipe).

---

## 3. Core strategy #2 — Rewards-harvesting market-making (the flow core)

**Verdict: marginally viable as a subsidy business, not as spread capture.** The best microstructure
evidence (Dubach, arXiv 2604.24366, byte-fetched) shows the **median maker's gross spread edge on
liquid markets is statistically zero** (median effective half-spread −0.0003 pp; median
adverse-selection component 0.0). Whatever a maker nets comes from **liquidity rewards + rebates −
episodic jump losses**. It is a short-straddle you must keep switching off.

- **Live pool data (gamma API, 2026-07-06):** 159 of the top-500 markets carry rewards totaling
  ~$23k/day (median pool $35/day; 17 markets ≥$500/day). The big pools (elections, Fed, majors)
  are owned by professionals (Jump, Wintermute, equity-aligned; top 1% of maker addresses = 84.1%
  of maker volume, Gini 0.97). **The independent's niche is the $50–500/day mid-tail.**
- **Precedents:** poly-maker ($10k → ~$200/day in the 2024 reward-rich era, killed when pools were
  cut); a 2026 replication netted ~zero; a pro deploying $300k/NFL Sunday makes $60–80k/mo pricing
  off Pinnacle and warns newcomers off.
- **The right model** (arXiv 2510.15205, byte-fetched): Avellaneda-Stoikov **in logit space**
  (bound disappears; sigmoid Jacobian auto-compresses spreads near 0/1), inventory skew shrinking
  with time-to-resolution — and jump risk handled **outside** the quoting formula by mandatory
  quote-pulling: before any scheduled catalyst, on ≥2-tick/30s moves or 3-level sweeps, never
  alive within 24h of market end. The 7,532-bps post-event spreads are the fossil record of makers
  who didn't pull.
- **Parameters:** 8–15 markets, pools $50–500/day, mid 0.15–0.85, >21 days to resolution, quote at
  ~0.4–0.6× the max-reward spread, inventory cap 5% of bankroll per market (worst-case-loss
  terms), ≤50–60% of bankroll deployed, split/merge to fund two-sided pairs with ~$1, sweep pUSD
  weekly. **Exclude crypto** (measured *negative* effective spread — flow prices through the mid)
  and in-play sports.
- **Expected: ~0–3%/month on deployed capital (central 1–2%)**, fat left tail — one un-pulled
  ladder through a news jump erases 2–6 weeks of income. Below $10k not worth the infra.

**Kill-risks:** (1) jump/insider sweeps if quote-pulling ever fails (the modal failure); (2)
reward-pool cuts — the profit is platform subsidy and has been cut before; (3) professional
crowd-out extending into the mid-tail.

---

## 4. Overlay — Fade-the-dumb-money (filter + confirmation, not standalone)

**Verdict: implementable ex-ante, but its value is as an overlay on the two cores.** The evidence
base is now strong:

- **Anti-skill persists.** LBS/Yale (SSRN 6617059, snippet-corroborated): 6.4% of 1.72M accounts
  are *statistically significant losers*; skill classification persists 44% out-of-sample and
  **anti-skill 51%** (vs ~10% for mutual funds). Taiwan day-trading (byte-verified abstract):
  the non-elite mass reliably loses −28.9 bps/day after fees, ex-ante identifiable by prior rank.
- **The fade regime applies here.** Cross-domain review: fading the public clears costs only when
  (i) the bias signal is at an extreme, (ii) commission <2–3%, (iii) the market is thin/immature,
  (iv) no informed flow is already arbing it. Prediction markets resolve to terminal value — no
  equity-style inventory-drift channel — and Polymarket fees are 0–0.75% effective, so conditions
  (i)–(ii) hold; (iii)–(iv) bind (Kyle's λ fell ÷50 into the 2024 election as markets matured).
- **Best ex-ante features (evidence-ranked):** turnover/overtrading; prior PnL shrunk toward the
  *negative* population prior (84% of wallets lose); **longshot-band concentration** (the 0–0.30
  band has negative realized returns on Polymarket — the longshot donors are identifiable);
  disposition effect (conditioned); chasing/deposit-cadence markers.
- **Engineering (byte-verified from exchange source):** the v2 `OrderFilled` event carries
  explicit `side`, `tokenId`, and `builder` fields; the aggressor wallet is directly recoverable
  (the `taker` field of maker-side fills; `OrdersMatched.takerOrderMaker`); MINT/MERGE matches
  require normalizing NO-fills to YES-equivalents before netting. The ~59% direction-accuracy
  problem applies to *WebSocket book-delta inference*, not on-chain events. **No open-source
  market-level dumb-flow index exists — this signal is greenfield.**

**How to use it:** (a) **toxicity filter for the MM core** — widen/pull when skilled-cohort flow
arrives (skilled net buying moves outcomes ~8bp per 1pp; lucky flow predicts nothing); (b)
**confirmation for the harvest core** — prefer favourites whose cheapness coincides with
identified dumb-flow on the longshot side; (c) fade-the-herd standalone only at documented
extremes (Intrade-Romney-whale-style episodes). Per-wallet precision is statistically hard
(~1,100 bets to detect a 3pp edge) — the signal is *aggregate flow of the classified cohort*.

---

## 5. Killed / parked strategies (and why)

### ⚠️ OVERTURNED: automated news-latency (pre-MVP3 "defensible edge #1") — KILLED
The anchor paper (arXiv 2606.07811, byte-fetched and fully parsed) contradicts the use we planned:
its "4.6-pt net drift" is net of *benchmark changes*, **not costs**, and its own Appendix B runs
exactly our trade — **executable returns are negative at every gap threshold** (−1.20% to −0.36%
buying at ask; positive only at unattainable midpoints). "The predictable midpoint drift is
largely absorbed by trading costs." Add: Polymarket's matching delays (250ms crypto/finance,
configured in-play sports delays, uncancellable during the window) exist precisely to hand the
speed edge to makers; the fee-free geopolitics niche is documented insider territory ($1.2M
pre-strike wallets — a news bot buys *after* informed money and risks being its exit); the only
feeds fast enough cost more than the strategy's optimistic gross at small scale (X Pro $5k+/mo,
closed to new signups).
**Survivor:** a ~$100, 4–6-week **shadow-mode pilot** (zero trades) that measures our end-to-end
latency vs the market's incorporation curve on ≥30 live geopolitics events — which would also be
the first Polymarket underreaction measurement (genuinely novel). Go-criteria in the DR5 report;
if it fails, strategy D is permanently dead.

### Sports fair-value taker trading — PARKED
Pre-game major-league prices already track de-vigged sharp books to ~0.5–1.5¢ (professionals price
Polymarket *off Pinnacle* directly); the NBA study found zero pre-game arb and seconds-long
in-play scraps capped at ~15 shares; Moskowitz's byte-verified conclusion — documented sports
mispricings "fail to overcome transactions costs" — generalizes. De-vig method choice (Shin vs
multiplicative differs 90–190bp at p≥0.85) exceeds the residual edge, so even measurement is
fragile. Sports exposure belongs in the MM core (maker side, subsidized), not directional.
Cross-venue "3–8% divergence" claims are vendor-blog noise inside Polymarket's own spread.

### Leaderboard/consensus copying — remains KILLED (mvp1/mvp2, unchanged)
Nothing in the six angles rehabilitates it; the LBS/Yale skill-persistence result (44%) is about
*self-computed on-chain cohorts*, not the public leaderboard, and feeds the overlay instead.

---

## 6. Portfolio blueprint ($50k reference book)

| Sleeve | Allocation | Expected net | Infra prerequisite |
|---|---|---|---|
| Calibration harvest (core #1) | 40–50% | 8–25%/yr | collector + UMA screen + cluster tagging |
| Rewards MM (core #2) | 25–35% | 0–3%/mo on deployed | WS book feed, <1s cancel, quote-puller, on-chain fill attribution |
| Cash / redeploy buffer | 20–30% | T-bill (off-platform) | — |
| News-latency shadow pilot | $0 traded (~$100 infra) | dataset only | collector WS capture |

- **Sizing:** fractional Kelly (¼) with the mvp2 engine, extended by the risk-constrained-Kelly
  bound (Busseti-Ryu-Boyd: choose λ = log β / log α; e.g. λ=6.46 caps P(30% drawdown) at 10%) and
  the Grossman-Zhou dynamic rule (shrink exposure toward zero as the floor nears).
- **Cluster caps are the unit of risk**, not markets: ≤15% per resolution cluster across BOTH
  sleeves (an election night hits harvest positions and MM inventory together).
- **Kill-switches (pre-registered, anytime-valid):** retire a sleeve on e-value evidence of
  negative edge; hard stop at −15% book drawdown in 30 days; MM sleeve halts on any
  catalyst-exposure incident (quote alive within 5 min of a scheduled event).
- **Opsec (non-negotiable):** fresh proxy wallet, capped on-platform balance, no third-party bot
  code with a funded key (documented key-stealer malware in this exact niche), weekly pUSD sweep,
  browser-wallet (not email-login) custody so the Safe is EOA-owned.
- **Order of operations:** the MVP3 collector remains the first build — both cores and the overlay
  consume it. Then: harvest paper-pilot (8–12 weeks, criteria in DR3 report) and MM live pilot
  ($10–15k, 2 weeks, criteria in DR1 report) in parallel; overlay ships when the wallet-skill
  table has enough history; 1/2/6-month forward evaluation per MVP3_DESIGN §3 unchanged.

---

## 7. What changed vs the pre-MVP3 research (supersessions & corrections)

1. **⚠️ News-incorporation edge OVERTURNED at executable level** (was "defensible edge #1") — see §5.
2. **Long-horizon politics harvest dead; harvest moved to 5–35 days.** Polymarket politics 1mo+
   slope is 1.086 (not the 1.32 domain average, and far from Kalshi's 1.73); the "70¢ a month out
   ≈ 75%" example is Kalshi-weighted. Near-certainty cheapness is the settlement wedge (48–88% of
   the gradient explained), not alpha.
3. **The dynamic-fee framing resolves cleanly:** fees tax takers on a p(1−p) curve and *fund* the
   maker side — the platform's economics actively pay the two core strategies.
4. **Engineering corrections** (fold into MVP3_DESIGN when building): v2 `OrderFilled` ABI now
   source-verified (explicit `side`/`tokenId`/`builder`); aggressor directly recoverable (three
   ways); the ~59% direction problem is WS-inference-only; **Goldsky subgraphs are stale post-v2**
   (index v1 only) — use Envio HyperSync / `warproxxx/poly_data` for backfill; MINT/MERGE fills
   need YES-normalization; wash-trading is median 1% per market (22% upper tail) — the "25%" was a
   platform-wide average dominated by the tail.
5. **Wallet-skill persistence quantified** (44%/51%) — upgrades fade-the-dumb-money from thesis to
   implementable overlay, while the ~1,100-bet detection floor demotes it from standalone.

Strategic conclusion of `PRE_MVP3_RESEARCH.md` otherwise intact: detection ≠ capture; the durable
edges are structural (subsidies, warehousing bias) not informational races.

---

## 8. Honest uncertainties

- The harvest's core slope rests on one published study whose strongest bins are 2024-cycle
  concentrated; the ×0.5 haircut is judgment, not measurement. The paper pilot exists to replace
  it with our own forward number.
- MM return range (0–3%/mo) extrapolates from three anecdotes + live pool math, not a distribution.
- LBS/Yale persistence figures are news-snippet-verified (SSRN anti-bot blocked the PDF); the 51%
  anti-skill figure is single-sourced.
- Tax treatment (§1256 vs ordinary vs gambling) is unresolved and could materially change MM's
  high-turnover after-tax economics.
- All capacity estimates are point-in-time (Jul 2026); reward pools and spreads are
  platform-discretionary.

## 9. Source appendix (by research angle)

- **DR1 MM viability:** arXiv 2510.15205 (logit-space AS, PDF parsed); arXiv 2604.24366 (Dubach,
  effective-spread/adverse-selection decomposition); live gamma-api.polymarket.com pool pull
  (2026-07-06); news.polymarket.com poly-maker + Meet-Your-Market-Maker profiles;
  docs.polymarket.com/market-makers/*; CFTC MM-program filing `[snippet]`; Jump/Wintermute
  coverage `[snippet]`.
- **DR2 sports fair value:** arXiv 2605.00864 (NBA arb, parsed); arXiv 2604.24366; Moskowitz JF
  2021 (PDF parsed); Kaunitz arXiv 1710.02824; Štrumbelj 2014 + own Shin/power solver
  computations; Levitt 2004; fee docs (byte-fetched); Odds-API docs.
- **DR3 calibration harvest:** arXiv 2602.19520 (Le, PDF parsed incl. Table 15); arXiv 2605.31431
  (Gebele & Matthes, PDF parsed); docs/help.polymarket.com (fees, pUSD, Holding Rewards);
  UMA-dispute coverage `[snippet]`.
- **DR4 fade-dumb-money:** SSRN 6617059 `[snippet, multi-outlet]`; arXiv 2606.04217 (band returns,
  parsed); arXiv 2605.02287; Barber-Odean corpus; BLLO 2014 (RePEc); Levitt-Miles; Rothschild &
  Sethi 2016; Gandhi & Serrano-Padial 2015; ctf-exchange / ctf-exchange-v2 Solidity source (read
  directly); Boehmer et al. + arXiv 2403.17095 replication.
- **DR5 news latency:** arXiv 2606.07811 (PDF fully parsed incl. Appendix B Table 11);
  docs.polymarket.com/concepts/order-lifecycle (matching delays); feed pricing (X API, GDELT,
  wires) `[snippet]`; Croxson & Reade; insider-wallet coverage `[snippet]`.
- **DR6 portfolio/platform:** arXiv 1603.06183 (risk-constrained Kelly, parsed); arXiv 1206.2305
  (Grossman-Zhou); Thorp 2006 (parsed); arXiv 2605.31431; docs.polymarket.com (pUSD, CTF, neg-risk
  convert); arXiv 2604.15674 (dispute counts, fetched); CFTC/QCX filings `[snippet]`;
  Intrade/PredictIt/Kalshi precedents `[snippet]`.
