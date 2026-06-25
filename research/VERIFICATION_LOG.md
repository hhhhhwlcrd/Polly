# Pre-MVP3 Research — Verification Log

*Re-run 2026-06-25 with a working sandbox egress allowlist (`research/sandbox-allowlist.txt`).
Five parallel research subagents (one per pillar) re-fetched the primary sources behind every
previously-flagged claim and adversarially tried to refute each. This log records the outcome of
each flagged claim, the primary-source URL, the confirmed value, and any correction (old → new).*

## How to read the status column
- ✅ **verified** — confirmed against the primary source (byte-fetched) or, where the publisher
  blocked automated fetch, against ≥2 independent reproductions / strong secondary sources.
- ✏️ **corrected** — the claim was wrong or imprecise; the corrected value is given.
- ⚠️ **unverified / downgraded** — no primary source located; downgraded to inference/speculation.
- ⛔ **still-blocked** — primary host refused automated fetch this session (origin anti-bot, **not**
  an egress-policy block — see "Still-blocked hosts" at the bottom).

## Fetch-environment finding (important)
The egress allowlist is in force, but several **publishers return origin-level anti-bot 403s** to
the headless fetcher regardless of the allowlist: `papers.ssrn.com`/`ssrn.com`, `davidhbailey.com`,
`researchgate.net`, `semanticscholar.org`, and (intermittently this session) `en.wikipedia.org`,
many `.edu` PDF hosts, `dl.acm.org`, `dspace.mit.edu`, `sciencedirect.com`/`onlinelibrary.wiley.com`
abstract pages, and several vendor doc hosts (`go.chainalysis.com`, `docs.nansen.ai`,
`api-guide.intel.arkm.com`, `docs.dune.com`, `docs.goldsky.com`, `docs.polygon.technology`,
`blog.gdeltproject.org`, `site.api.espn.com`). What **did** byte-fetch cleanly: `arxiv.org/pdf/*`
and `/abs/*`, `ideas.repec.org`, `docs.polymarket.com`, `polygonscan.com`/`etherscan.io`,
`help.polymarket.com`, `polymarket.com/accuracy`, `the-odds-api.com`, `goldsky.com`, `tardis.dev`,
and reference-implementation code on `github.com` raw. Where a primary PDF was anti-bot-blocked,
subagents downloaded the arXiv PDF and extracted text locally (true byte-verification) or
cross-confirmed across ≥2 independent reproductions; those cases are marked accordingly.

---

## Pillar A — Insider / informed-trading detection

| # | Flagged claim | Status | Primary source | Confirmed value | Old → New |
|---|---|---|---|---|---|
| A1 | Mitts & Ofir 2026 "From Iran to Taylor Swift" — screen thresholds, win-rate, $ profit, # pairs | ✅ (snippets; SSRN ⛔) | SSRN 6426778; mirror corpgov.law.harvard.edu | **69.9% win rate**, **~$143M** aggregate anomalous profit, **>210,000** wallet-market pairs; composite = bet-size anomaly + profitability + pre-event timing + directional concentration; win rate **>60 SD** above a permutation null; range **Feb 2024–Feb 2026** | All three draft figures confirmed (no change); added the >60-SD robustness stat |
| A2 | PIN (Easley-Kiefer-O'Hara-Paperman 1996) = order-imbalance MLE | ✅ | J. Finance 51:1405 (Wiley); frds.io | `PIN = αμ / (αμ + 2ε)`; α,δ,μ,ε via MLE on independent-Poisson buy/sell flow | — |
| A3 | VPIN (Easley-LdP-O'Hara 2012, RFS) toxicity; flash-crash claim contested | ✅ | RFS 25:1457; critique Andersen & Bondarenko, J. Fin. Markets 2014 | Volume-bucketed signed-flow toxicity; flash-crash *predictive* claim refuted (VPIN peaked **after**, not before, the crash) | — |
| A4 | Meulbroek 1992 event-study runup | ✅ | J. Finance 47:1661 (Wiley/RePEc) | Insider-day abnormal move ≈ **40–50%** of the later public-announcement reaction | — |
| A5 | Bubblemaps 9-wallet US-military cluster: 98% / 80+ bets / $2.4M / funded <24h | ✏️ | CBS/60 Minutes; Bloomberg graphics; Decrypt | 9 accounts, **98%** over **80+** bets, **$2.4M** — confirmed | "funded <24h before events" → accounts **created "days prior"** (4 "just days before"); soften the <24h detail |
| A6 | DOJ-charged soldier, ~$33k→~$410k, Maduro, classified info | ✅ | justice.gov press release; CNBC | MSgt **Gannon Ken Van Dyke**; ~**$33,000** across ~13 bets → ~**$410,000** | — |
| A7 | Columbia: ~25% of volume wash-traded (~45% of sports) | ✅ | business.columbia.edu; CoinDesk; Bloomberg | **~25%** total; **45%** sports, 17% elections, 12% politics, 3% crypto; peaked ~60% Dec 2024 | — |
| A8 | Théo whale: 11 wallets, ~$85M, research false-positive | ✅ | Bloomberg; Chainalysis | **11** clustered accounts; **>$85M** (revised up from ~$48M); Polymarket found "no evidence of manipulation" | $48M → $85M (figure was revised upward post-election) |
| A9 | Deposit-address/sweep clustering = Victor 2020 (not BTC co-spend) | ✅ | Springer FC 2020 (10.1007/978-3-030-51280-4_33); dblp | Ethereum deposit-address heuristic clustered **17.9%** of active EOAs | — |
| A10 | GNN/GAT Sybil detection "95–100% on chain/tree patterns" | ✏️/⚠️ | arXiv 2409.08631 (SybilGAT) | SybilGAT is a **social-network** method reporting **AUC ≈ 0.58–0.86**, not 95–100% accuracy, and tests no chain/tree topology | **Claim unsupported — drop or re-anchor.** The 95–100% number does not trace to a blockchain-Sybil source |
| A11 | Chainalysis sanctions oracle (Polygon `0x40C5…c8fb`, `isSanctioned`) | ✅ | etherscan address; chainalysis docs; 0xsequence/chainalysis source | Address **0x40C57923924B5c5c5455c48D93317139ADDaC8fb** (same on Ethereum/Polygon/BNB); method **`isSanctioned(address)→bool`** | — |
| A12 | Arkham (20/1 rps) & Nansen (credits) API specifics | ⚠️ | intel.arkm.com docs (⛔); docs.nansen.ai (⛔) | Snippet-level only: Arkham ~20 rps standard / 1 rps heavy; Nansen free-plan calls cost 10× credits | Not byte-verified — flag before hard-coding |

## Pillar B — Mispricing / fair-value

| # | Flagged claim | Status | Primary source | Confirmed value | Old → New |
|---|---|---|---|---|---|
| B1 | Page & Clemen — long-horizon compression; "70¢ week-out → ~83% true" | ✏️ | **The Economic Journal** 2013, 123(568):491–513 (NOT Management Science); Le 2026 arXiv 2602.19520 | Direction confirmed (favourites underpriced, longshots overpriced, worsening with horizon). Magnitude is slope-dependent: at the headline slope, **70¢ one month out ≈ ~75% true** (~83% only at a steeper slope) | Journal corrected; example softened "week-out → 83%" → **"one month out → ~75%"** |
| B2 | Polymarket Brier ~0.06 (self-reported); independent 0.06–0.18 | ✅ | polymarket.com/accuracy | Self-reported **0.0627**; independent estimates ~0.057–0.18 (segment-dependent) | — |
| B3 | Favorite-longshot bias **REVERSED** on Polymarket (longshots overpriced) | ⛔ **REFUTED** | Le 2026, arXiv 2602.19520 | Polymarket shows the **classic** FLB, **same direction** as racetracks: favourites underpriced, longshots overpriced | **"Reversed" → NOT reversed.** Load-bearing correction |
| B4 | $40M internal arb; ~100bps/opp, half-life<1min (λ 0.52→0.01), ~15-share cap, 62–78% fail | ✏️ | $40M: arXiv 2508.03474. Per-opp: **arXiv 2605.00864** (NBA) | $40M (Apr 1 2024–Apr 1 2025) ✅. Per-opp: median **101.01 bps**; **76.9%** constrained to avg **14.8 shares**; median duration **3.6s single / 16s combinatorial** | Per-opp numbers re-attributed to 2605.00864; "~100bps"→101.01, "~15 shares"→14.8, "62–78% fail"→76.9% constrained. **"half-life<1min / λ 0.52→0.01" NOT in either paper — remove** |
| B5 | Cross-venue: ~6% cross-listed; 2–4% deviations ≥1h | ⚠️ | (none located) | Neither arb paper studies cross-venue; observed deviations last **seconds**, not hours | **Downgrade to speculation** — no primary support for 6% / 2–4% / ≥1h |
| B6 | Markets beat polls ~74%; election-eve MAE ~1.33 pts | ✅ (snippet) | Berg-Nelson-Rietz 2008, Int. J. Forecasting 25(2); uiowa IEM | **74%** closer than polls; election-eve **MAE 1.33 pts** | — |
| B7 | 538-type models ≈ tie the market (Brier 0.108 vs 0.109) | ✅ dir / ✏️ exact | Sethi et al., CI'25 (dl.acm.org 10.1145/3715928.3737483) | "Roughly tie" confirmed (no model beat the market on the headline 2024 contract); exact 0.108/0.109 **not byte-confirmed** (ACM/MIT ⛔) | Keep direction; flag exact decimals as snippet-only |
| B8 | Shin's method = best de-vig of bookmaker odds | ✅ | Shin 1992/1993, Economic Journal; Štrumbelj 2014 | Shin de-vig beats basic normalization (best in 217/412 book-competition pairs) | — |
| B9 | Equal-weight ensembles beat both ~40% of days; superforecasters beat markets ~30% Brier | ⚠️ | Good Judgment / Tetlock | Superforecaster 15–30% edge documented; **"40% of days" ensemble figure unsourced** | Keep superforecaster claim; flag "40% of days" as unsourced |
| B10 | ~0.64 Kalshi news passthrough (arXiv 2606.07811); overreaction (Choi-Hui); ~50% open-to-close reversal (Moskowitz) | ✅ | arXiv 2606.07811; Choi & Hui 2014 JEBO; Moskowitz 2021 JF 76(6):3153 | id **2606.07811 is real**; passthrough **0.63–0.64**; Moskowitz reversal coefficient **−0.50** (~half reverses) | "negative HF autocorrelation" framing is loose — Moskowitz is overreaction-reversal specifically |

## Pillar C — Microstructure

| # | Flagged claim | Status | Primary source | Confirmed value | Old → New |
|---|---|---|---|---|---|
| C1 | OFI R² & "44 of 50 stocks" (Cont-Kukanov-Stoikov) | ✏️ | **arXiv 1011.6402** (byte-verified PDF) | Avg **R²=65%** (OFI) vs **32%** (trade imbalance); ~**48/50** stocks ≥50% R² | arXiv id 1011.4087 (wrong/unrelated) → **1011.6402**; "44/50" not in paper → headline **"avg R² 65%"** / ~48/50 ≥50% |
| C2 | Stoikov micro-price (mid + imbalance + spread; martingale) | ✅ | Stoikov 2018, Quant. Finance 18(12):1959 (RePEc) | `P_micro = M + g(I,S)`; martingale "fair price"; beats mid & weighted-mid | — |
| C3 | OFI/OBI edge < spread → maker/queue signal, decays in seconds | ⚠️/✅ | arXiv 1011.6402 | Seconds-scale decay confirmed ("autocorrelations … vanish after ~10s"); "maker-not-taker" is reasoned inference, not a stated result | Downgrade framing to inference |
| C4 | Polymarket feed direction ~59% vs on-chain; half-spread flips on 50–67% | ✅ | **arXiv 2604.24366** (Dubach, byte-verified) | Panel mean **0.615**, 95% CI [0.58,0.65]; effective half-spread sign flips on **67%/50%** across two 7-day windows; vs ~80% Lee-Ready on Nasdaq | id 2604.24366 **confirmed resolves**; numbers confirmed |
| C5 | Depth ≈ uniform grid; spreads 2–5¢; ~3.5× Kalshi volume | ✏️ | arXiv 2604.24366 | Uniform-grid depth confirmed (concentration 0.137 vs 0.10 uniform); spreads **~400 bps central, 1,300–1,800 bps below 0.10** | **Spreads are in bps, not "2–5¢"**; **"3.5× Kalshi" not in source — unverified** |
| C6 | Maker > taker returns (Betfair) | ⚠️ | Whelan, karlwhelan.com (snippet) | Directionally supported (positive maker returns laying favourites) | snippet-only, not byte-verified |
| C7 | Maker incentives: 0 maker fee + 20/25% rebate + quadratic near-mid rewards | ✅ | docs.polymarket.com/market-makers/liquidity-rewards; help.polymarket.com | Makers never charged; rebate **20% crypto / 25% other**; reward score **S = ((v−s)/v)²·b**, single-sided ÷ c=3 | — |
| C8 | Frozen liquidity: NBA spread ~7,532 bps; ~81% of arbs unexecutable | ✏️ | **arXiv 2605.00864** (byte-verified) | Post-game median spread **7,532.65 bps**; **30/37 (81.1%)** theoretical arbs strictly post-game/unexecutable; only **7 valid in-game arbs** in 75M+ snapshots | Source 2508.03474 → **2605.00864**; numbers confirmed exact |
| C9 | Kyle 1985 — λ permanent impact; size predicts resolution | ✅ | Econometrica 53:1315 | Single λ price-impact param; constant depth 1/λ; private info fully impounded by end of trading | — |

## Pillar D — Data sources & collector architecture

| # | Flagged claim | Status | Primary source | Confirmed value | Old → New |
|---|---|---|---|---|---|
| D1 | v2 + v1 contract addresses | ✅ | docs.polymarket.com/resources/contracts; Polygonscan (verified) | v2 CTF Exch `0xE111180000d2663C0091e4f400237545B87B996B`; v2 NegRisk Exch `0xe2222d279d744050d28e00520010520000310F59`; NegRisk Adapter `0xd91E80cF2E7be2e162c6513ceD06f1dD0dA35296`; CTF `0x4D97DCd97eC945f40cF65F87097ACe5EA0476045`; pUSD proxy `0xC011a7E12a19f7B1f670d46F03B03f3342E82DFB` (impl `0x6bBCef9f7ef3B6C592c99e0f206a0DE94Ad0925f`); UMA Adapter `0x6A9D222616C90FcA5754cd1333cFD9b7fb6a4F74`; UMA OO `0xCB1822859cEF82Cd2Eb4E6276C7916e692995130`; Proxy Factory `0xaB45c5A4B0c941a2F231C04C3f49182e1A254052`. **v1** CTF Exch `0x4bFb41d5B3570DeFd03C39a9A4D8dE6Bd8B8982E`; v1 NegRisk Exch `0xC5d563A36AE78145C45a50134d48A1215220f80a`; USDC.e `0x2791Bca1f2de4661Ed88A30C99A7a9449Aa84174` | v1 stubs `0x4bFb…`/`0xC5d5…` → full verified addresses; added pUSD impl |
| D2 | v2 OrderFilled / OrdersMatched ABI | ✏️ | Polygonscan v2 event index; ctf-exchange-v2 | **v2 OrderFilled topic0 `0xe92c22722d9c284034b6c9f5aaec018edb3e593c0e084900b6b9d390a1182a0b`**; **OrdersMatched topic0 `0x787a2e12f4a55b658b8f573c32432ee11a5e8b51677d1e1e937aaf6a0bb5776e`**; **separate `FeeCharged` event**; v1 `OrderFilled(bytes32 orderHash, address maker, address taker, uint256 makerAssetId, uint256 takerAssetId, uint256 makerAmountFilled, uint256 takerAmountFilled, uint256 fee)` | **Correction: v1 and v2 do NOT share the OrderFilled signature.** v2 has a new topic0 + splits fees into `FeeCharged` → **dual decoder mandatory.** (Exact v2 param list inferred from event index + assembly-emit; pull byte-for-byte ABI before hard-coding) |
| D3 | UMA liveness 2h vs 48h | ✅ | docs.polymarket.com/developers/resolution/UMA | **Undisputed liveness = 2 hours (7200s)** (fast path); **48h = the DVM voting phase** that occurs only after a second dispute | Resolved: 2h is the proposer liveness; 48h is escalation-only |
| D4 | Fee model (categories, formula, rebates, getClobMarketInfo) | ✅ | docs.polymarket.com/trading/fees | Crypto 7% / Sports 3% / Finance·Politics·Mentions·Tech 4% / Econ·Culture·Weather·Other 5% / **Geopolitics 0**; `fee = C × feeRate × p × (1−p)`; rebate 20% crypto / 25% other; makers never charged; `getClobMarketInfo` → `info.fd = {r:feeRate, e:exponent, to:takerOnly}` | The fee is **category-based with a p(1−p) curve**, not a single "dynamic taker fee"; correct the framing |
| D5 | Data/Gamma/CLOB APIs + WS channels + rate limits | ✅ | docs.polymarket.com/api-reference | Data API `/positions,/trades,/activity,/holders,/value` (1,000/10s); Gamma metadata; CLOB `/book,/prices-history,/midpoint,/spread` (1,500/10s/endpoint); WS `book/price_change/last_trade_price/tick_size_change`; Goldsky 50/10s | — |
| D6 | "/prices-history empty for resolved markets" + "REST L2 backfill gone" | ⚠️/✏️ | nautilus_trader issue #3635 | The L2-backfill loss is real but concerns **`/orderbook-history`** (stopped emitting ~**Feb 20 2026**); "/prices-history empty for resolved markets" is **not in the docs** | Re-attribute to `/orderbook-history`; the operational conclusion (capture L2 live) stands |
| D7 | OrderFilled attribution (price ratio; assetId==0 = buy; attribute on `maker`) | ✅ | docs.polymarket.com/.../onchain-order-info | `makerAssetId==0` ⇒ BUY; `maker` = source of funds; `taker` = Exchange contract when sweeping multiple makers → attribute per-fill on `maker`, never `tx.from` | — |
| D8 | GDELT (free, 15-min), Odds API, ESPN JSON, 538 CSVs | ✅/⛔ | gdeltproject.org; the-odds-api.com; ESPN; github.com/fivethirtyeight/data | GDELT free 15-min; Odds API **500 credits/mo** (credits, not requests); ESPN JSON free/unauth; **FiveThirtyEight SHUT DOWN 2025-03-05 — live poll CSVs gone** | **538 is a dead anchor — remove it**; Odds API "requests" → "credits" |
| D9 | Polygon deep reorgs "32+ blocks" | ✏️ | polygon.technology (PIP-5 / sprint 64→16) | Post-PIP-5 max reorg ≈ **32 blocks** (down from 128); recommend ~30-block (~1 min) confirmation buffer | "32+ (floor)" → **~32 is the ceiling**; buffer ~30 blocks |
| D10 | Goldsky Mirror/subgraphs; Dune tables; tardis.dev; SII-WANGZJ collector | ✅ | goldsky.com; docs.dune.com; tardis.dev; github SII-WANGZJ | All exist as described; Dune `polymarket_polygon.market_trades`/`positions`; SII-WANGZJ ~1.1B records (~107GB Parquet, incremental) | — |

## Pillar E — Forward-test methodology

| # | Flagged claim / formula | Status | Primary source | Confirmed value | Old → New |
|---|---|---|---|---|---|
| E1 | Probabilistic Sharpe Ratio | ✅ | Bailey & LdP (SSRN 1821643 ⛔); ref impl rubenbriones/Probabilistic-Sharpe-Ratio | `PSR(SR*) = Z[ (SR_hat − SR*)·√(T−1) / √(1 − γ3·SR_hat + ((γ4−1)/4)·SR_hat²) ]`, Z=Φ, γ3=skew, γ4=raw kurtosis | Confirmed exactly (√(T−1); −γ3 term; (γ4−1)/4) |
| E2 | Minimum Track Record Length | ✅ | ref impl (byte-verified code) | `MinTRL = 1 + [1 − γ3·SR_hat + ((γ4−1)/4)·SR_hat²]·(Z_α/(SR_hat − SR*))²` | Confirmed; a circulating `(1−skew)/(3·SR)` variant is OCR corruption |
| E3 | Deflated Sharpe Ratio + expected-max | ✅ | Bailey & LdP 2014 (SSRN 2460551 ⛔); marti.ai; Wikipedia | `DSR = PSR(SR*)` at `SR* = √Var[SR]·[(1−γ)·Z⁻¹(1−1/N) + γ·Z⁻¹(1−1/(N·e))]`, γ=0.5772, e=Euler | Confirmed all terms |
| E4 | Required sample ∝ 1/SR² | ✅ | follows from E5/E2 | `T ∝ z²·(1+SR²/2)/SR² ≈ z²/SR²` | — |
| E5 | Lo 2002 Sharpe SE | ✅ | arXiv 1808.04233 (byte-verified) | `SE(SR) = √((1 + SR²/2)/T)` | — |
| E6 | Win-rate binomial SE; ~100 trades → ~5pp | ✅ | arithmetic | `√(0.25/100) = 0.05` = 5.0 pp at p=0.5 | — |
| E7 | Max drawdown biased, grows with T | ✅ | Magdon-Ismail et al. 2004, J. Appl. Prob. 41:147 | E[MaxDD] grows: log(T) (positive drift) / √T (zero) / linear (negative) | — |
| E8 | Multiple-looks Type-I inflation ~0.19 at 5 looks | ✏️ | Armitage 1969 (NJIT .edu lecture table; Lakens) | At α=0.05: 5 looks → **~0.142**; **10 looks → ~0.193** | **"~0.19 at 5 looks" → ~0.14 at 5 looks, ~0.19 at 10 looks** |
| E9 | O'Brien-Fleming alpha-spending | ✅ | O'Brien & Fleming 1979, Biometrics; SAS SEQDESIGN | Group-sequential boundary, very conservative early (spends little α), less stringent later | — |
| E10 | e-values / anytime-valid (valid at any stopping time) | ✅ | arXiv 2210.01948 (Ramdas-Grünwald-Vovk-Shafer, byte-verified) | SAVI "remain valid at all stopping times … optional stopping or continuation for any reason" | — |
| E11 | Harvey-Liu-Zhu t > 3.0 hurdle | ✅ | HLZ 2016, RFS 29(1):5–68 (RePEc byte-verified); NBER w20592 | "a t-statistic greater than 3.0" for a new factor | — |
| E12 | Square-root market-impact law; 522× paper vs −49.5% live | ✅ law / ⚠️ anecdote | ar5iv 1602.03043; Kyle-Obizhaeva | Impact ∝ √Q (`≈ Y·σ·√(Q/V)`, Y=O(1)) confirmed across asset classes | **522×/−49.5% anecdote not sourced — flag as illustrative/apocryphal** |

## Cross-pillar (added this pass)

| # | Claim | Status | Primary source | Confirmed value |
|---|---|---|---|---|
| X1 | Yale/LBS ~3% skilled traders / 1.72M accounts / $13.76B | ✅ (snippets; Yale page ⛔) | Gómez-Cram, Guo, Jensen & Kung (LBS/Yale, Apr 2026); CoinDesk; The Block; Crowdfund Insider | **1.72M accounts, $13.76B volume**; **~3%** (3.14%) drive most price discovery; skilled minority captures **>30%** of gains; only **~12%** of top raw-profit winners clear a 10,000-sim skill bar; ~**60%** of "lucky winners" regress out-of-sample |

---

## Still-blocked hosts (origin anti-bot 403 — report only; not routed around)
`papers.ssrn.com` / `ssrn.com`, `davidhbailey.com`, `researchgate.net`, `semanticscholar.org`,
`corpgov.law.harvard.edu` (rate-limited mid-session), `en.wikipedia.org` (intermittent this session),
`dl.acm.org`, `dspace.mit.edu`, `sciencedirect.com` & `onlinelibrary.wiley.com` & `academic.oup.com`
(abstract pages), `link.springer.com` (auth redirect), `tandfonline.com` (micro-price article),
many `.edu` PDF mirrors (cs.rpi.edu, web.njit.edu, people.duke.edu, berkeley.edu PDFs),
`insights.som.yale.edu`, `business.columbia.edu`, `cbsnews.com`, `bloomberg.com`, `cnbc.com`,
`justice.gov`, `decrypt.co` (all confirmed via search snippets instead),
`go.chainalysis.com`, `docs.nansen.ai`, `api-guide.intel.arkm.com`,
`docs.dune.com`, `docs.goldsky.com`, `docs.polygon.technology`,
`blog.gdeltproject.org` / `www.gdeltproject.org`, `site.api.espn.com` / `espn.com`,
`github.com` HTML (raw/API used instead). These are **origin anti-bot blocks, not egress-policy
denials** — the proxy's `recentRelayFailures` was empty for them. Where blocked, claims were
confirmed via byte-fetched arXiv PDFs, `ideas.repec.org`, reference-implementation code, or ≥2
independent search reproductions, as noted per row.
