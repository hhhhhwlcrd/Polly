# MVP3 Research — Verification Log

*Primary-source verification pass, 2026-07-01. Five parallel agents + direct `curl` checks
re-examined every load-bearing claim in `PRE_MVP3_RESEARCH.md` / `MVP3_DESIGN.md` against the
actual papers, contracts, and docs — replacing the original search-snippet basis.*

## How this pass was done (and its limits)
- **`curl` with a browser User-Agent is the reliable fetch path**; the `WebFetch` tool is
  rejected (403) by most publishers' bot protection even when the host is allowlisted. arXiv,
  `davidhbailey.com` (apex), `docs.polymarket.com`, `polygonscan.com`, `fortune.com`,
  `cointelegraph.com`, `ideas.repec.org`, `raw.githubusercontent.com` were reachable and fetched.
- **Still blocked this session** (egress-policy 403 / host bot-challenge, *not* routed around):
  `papers.ssrn.com`, `nber.org`, `academic.oup.com`, `onlinelibrary.wiley.com`, `sciencedirect.com`,
  `journals.uchicago.edu`, `en.wikipedia.org`, `corpgov.law.harvard.edu`, `justice.gov`,
  `cnbc.com`, and several `www.`-subdomain author mirrors. Claims resting only on these are marked
  **UNVERIFIED (blocked)** — most were corroborated via citing papers or the source's own abstract,
  but not the primary PDF.
- Verdicts: **VERIFIED** (confirmed against primary), **CORRECTED** (primary contradicts the doc),
  **UNVERIFIED** (primary unreachable).

## Headline outcome
The **forward-test statistics formulas** (PSR, MinTRL, Deflated Sharpe, Lo SE, Kelly) — the ones
that go into code — are **VERIFIED exactly** against the authors' reference code. The **on-chain
technical facts** (all contract addresses, fee formula/rates, `OrderFilled` semantics, WS fields)
are **VERIFIED** against docs + PolygonScan. The **Polymarket-empirical** claims (arbitrage total,
frozen liquidity, Dubach 59%, cross-venue, Kyle λ, news passthrough) are **VERIFIED** on arXiv.
The corrections are concentrated in **transcription/attribution errors** in the insider and
mispricing pillars — several specific figures were misattributed or mislabeled. **None of the
strategic conclusions change.**

---

## Corrections that must propagate into the docs

| Doc claim (original) | Correction | Source |
|---|---|---|
| Polymarket has a **"reversed" favorite-longshot bias (low-prob overpriced)**; cite "Reichenbach & Walther / Le 2026" | **Classic FLB direction** — Le 2026 finds longshots overpriced / favorites underpriced / compression toward 50% (Politics slope **1.31**). "Reversed" label is wrong; author is **Le**, not Reichenbach & Walther. (Microstructure literature is genuinely mixed by category, but the dominant Polymarket pattern is classic + compression.) | arXiv 2602.19520 |
| Arbitrage split "~$10.6M single-market / ~$29M rebalancing" | **Labels swapped**: single-market *rebalancing* ≈ **$10.6M**; cross-market *combinatorial* ≈ **$29.0M**. Total **$39.59M** ✓ | arXiv 2508.03474 |
| "~15-share avg capacity; 62–78% fail on execution" (attributed to the arbitrage paper) | **Misattributed** — the **14.8-share / 76.9%** figures are from the **NBA in-game** paper (2605.00864), not the aggregate arbitrage paper. "62–78% fail" has **no basis** in either. | arXiv 2605.00864 |
| "~50% open-to-close reversal in pre-game lines (**Moskowitz**)" | **Misattributed** → Lou, Polk & Skouras, "A Tug of War" (JFE 2019). The ~50% magnitude is **unconfirmed**. | — |
| Sybil "GNN/GAT models report **95–100%** on chain/tree patterns" | **Not in the cited paper** — arXiv 2505.09313 is a **LightGBM subgraph model**, all metrics **>0.9** on 193,701 addresses. The 95–100%/97-95% figures are misattributed. | arXiv 2505.09313 |
| Insider thresholds include "**whale ≥$5k / mega ≥$25k**" | **Not in the deployed detector** (pselamy repo) — it has fresh-wallet ($1k), a $10k large-trade bonus, and 2%/5% size anomaly. Drop the whale/mega tiers. | github pselamy/polymarket-insider-tracker |
| Lee-Ready "EMO 83.7%" | **81.05%** (Ellis-Michaely-O'Hara 2000, Nasdaq). 83.7% was a different-venue mis-cite. Odders-White 72.8% ✓ | JFQA 35:529-551 |
| Proxy↔EOA "CREATE2 salt = keccak256(owner)" | True for legacy Safe/Magic factories, but the **current Deposit Wallet Factory** (`0x0000…Cc07`) uses `salt=keccak256(abi.encode(factory, walletId))` with beacon/UUPS clones. Use the documented `deriveDepositWalletAddress()`. | docs.polymarket.com/trading/deposit-wallets |
| Polygon "reorgs reach 32+ blocks" | Not an official bound; sprintLength 64→**16**. Rely on **milestone finality (2–5s)** as the collector's safety signal, not a fixed block depth. | polygon.technology / docs.polygon.technology |
| Magdon-Ismail drawdown ref PII `S0378437104004327` | **Wrong PII** (Physica A). Correct citation: *On the Maximum Drawdown of a Brownian Motion*, J. Appl. Probability 41 (2004) 147–161. Substantive claim (E[maxDD] ∝ √T zero-drift) is TRUE. | — |
| Meulbroek "~40–50% of the takeover **premium** pre-announcement" | Meulbroek's "almost half" is of the **runup**, not the premium (that's Keown-Pinkerton/Schwert). 3%/insider-day ✓ | Meulbroek 1992, JF 47(5) |

---

## Full verification table

### Forward-test statistics (all fetched from davidhbailey.com apex + arXiv + Thorp PDF)
| Claim | Verdict | Confirmed |
|---|---|---|
| PSR = Φ[(SR−SR*)·√(n−1)/√(1−skew·SR+((kurt−1)/4)·SR²)] | **VERIFIED** | Exact, vs authors' code (App. A.3); use *full* kurtosis (Normal=3) |
| MinTRL = 1+[1−skew·SR+((kurt−1)/4)SR²]·[Z_α/(SR−SR*)]² | **VERIFIED** | Exact, incl. leading `1+` |
| DSR benchmark SR0 = (1−γ)Z⁻¹[1−1/N]+γZ⁻¹[1−1/(N·e)] | **VERIFIED** | Exact, vs code Snippet 1; γ=Euler-Mascheroni |
| Lo (2002) SR SE ≈ √((1+SR²/2)/T) | **VERIFIED** | Exact (skew=0,kurt=3 case of PSR denom) |
| Harvey-Liu-Zhu t>3.0 factor hurdle | **VERIFIED** | 9 of ~300 factors survive |
| Harvey-Liu Sharpe haircut (separate paper, nonlinear) | **VERIFIED** | JPM "Backtesting" 2015; not a flat 50% |
| e-process supermartingale → optional stopping valid; confidence sequences | **VERIFIED** | arXiv 2210.01948, 1810.08240 |
| Wald SPRT bounds A≈(1−β)/α, B≈β/(1−α) | **UNVERIFIED (blocked)** | Wikipedia blocked; textbook-standard |
| Binary Kelly f*=(p−c)/(1−c); drawdown P(drop to a)≈a^(1/f) | **VERIFIED** | Thorp: exact primitive a^(2m/s²); a^(1/f) is the fractional-Kelly approx |

### On-chain / architecture (docs.polymarket.com + PolygonScan, via curl)
| Claim | Verdict |
|---|---|
| CTF Exchange v2 `0xE111…996B`, Neg-Risk v2 `0xe222…0F59`, pUSD `0xC011…2DFB`, v1 `0x4bFb…982E`, CTF `0x4D97…6045`, Safe factory `0xaacF…541b`, Magic factory `0xaB45…4052`, UMA adapter `0x6A9D…4F74` | **VERIFIED** (every address matches docs + PolygonScan tag) |
| `OrderFilled` 8 fields; `maker`=funder/proxy (not relayer); assetId==0=collateral side | **VERIFIED** |
| Taker fee `= C·rate·p·(1−p)`, makers=0, rates (bps) Crypto7/Sports3/Politics·Finance·Tech·Mentions4/Econ·Culture·Weather·Other5/Geopolitics0 | **VERIFIED** |
| UMA liveness 2h default (48h = post-dispute DVM, distinct phase) | **VERIFIED (discrepancy resolved)** |
| Proxy CREATE2 salt | **CORRECTED** (deposit-wallet factory differs — see above) |
| Polygon reorg "32+ blocks" | **CORRECTED** (use 2–5s milestone finality) |
| `/prices-history` empty for resolved markets | **UNVERIFIED by docs** (but empirically observed `[]` during mvp1/mvp2 collection — treat as true, confirm live) |
| Market WS `book`/`price_change` fields | **VERIFIED** |

### Polymarket-empirical (arXiv, via curl)
| Claim | Verdict |
|---|---|
| Internal arbitrage total **$39.59M** (~$40M), Apr2024–Apr2025 | **VERIFIED** (split labels corrected above) |
| Cross-venue ~6% cross-listed, 2–4% persistent deviations | **VERIFIED** |
| Kyle λ **0.518→0.01**, arb half-life hours→<1 min | **VERIFIED exactly** |
| NBA: 7 single-market (median 3.6s), 290 combinatorial (median 101 bps), 76.9% capped at 14.8 shares, post-game spread 7,532 bps, 81.1% stale | **VERIFIED** |
| Dubach: feed↔on-chain direction ~59% (mean 0.615); half-spread sign-flip 67%/50%; uniform-geometric depth; longshot premium | **VERIFIED** |
| News underreaction ~**0.64**-for-one passthrough + multi-minute drift | **VERIFIED exactly** |
| GasTrace MEV 96.73% acc / 95.71% F1 | **VERIFIED verbatim** |

### Insider cases & detection
| Claim | Verdict |
|---|---|
| DOJ soldier Maduro bet **$33,034 → $409,881** | **VERIFIED** (indictment figure) |
| Bubblemaps 9-wallet, 98% win, $2.4M military | **VERIFIED** |
| Columbia wash trading 25% avg (~60% peak Dec 2024, 45% sports) | **VERIFIED** (note: Dubach's own wash median 1% — don't cite both as agreeing) |
| Mitts-Ofir: 210k wallet-market pairs, $143M anomalous profit | **VERIFIED** (via two citing arXiv papers) |
| Mitts-Ofir: 69.9% flagged win rate | **UNVERIFIED (blocked)** — abstract text only (SSRN/corpgov blocked) |
| Detector fresh-wallet (age<48h, nonce≤5, >$1k) + size anomaly (2%/5%) | **VERIFIED** (whale/mega tiers CORRECTED — not present) |
| Meulbroek 3%/insider-day; PIN/VPIN definitions; VPIN Andersen-Bondarenko critique | **VERIFIED** (Meulbroek "premium" wording corrected) |

### Mispricing / fair value
| Claim | Verdict |
|---|---|
| Favorite-longshot bias exists; magnitude | **CORRECTED/PARTIAL** — SW net returns favorites ~−5.5%, extreme longshots ~−61%; the "$0.85/$0.63, $0.50→$0.35" figures don't match SW and are unconfirmed |
| Polymarket FLB direction | **CORRECTED** — classic (not reversed); Le 2026 |
| Page-Clemen long-horizon 4.7–10.9pp | **UNVERIFIED (blocked)** — qualitative claim (bias grows with horizon) holds |
| Berg-Nelson-Rietz: markets beat polls 74%, eve MAE 1.33pp | **VERIFIED** |
| 538≈market Brier 0.1084 vs 0.1091 | **VERIFIED exactly** (k5cents repo) |
| Shin de-vig most accurate | **VERIFIED (qualitative)** |
| Market+model ensemble beats both ~40% of days | **UNVERIFIED** — core ensemble result holds; exact 40% unconfirmed |

---

## Net assessment
- **Safe to build on:** all forward-test formulas, all on-chain addresses/fees/events, the
  Polymarket-empirical arbitrage/microstructure/news figures, and the headline insider cases.
- **Fix before quoting:** the 10 corrections table above (attribution/label/figure errors).
- **Do not rely on until re-fetched:** Mitts-Ofir 69.9%, Page-Clemen 4.7–10.9pp, FLB dollar
  magnitudes, ensemble ~40%, SPRT bounds — all blocked-host casualties, none load-bearing for the
  MVP3 design.
- **Strategic conclusions unchanged:** following informed/insider flow still loses; fade-dumb-money
  + market-making + mispricing + news-latency remain the defensible edges; forward paper-testing at
  1/2/6 months with anytime-valid stats remains the evaluation plan.
