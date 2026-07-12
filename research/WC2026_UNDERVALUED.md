# WC-2026 Winner Market — Undervaluation Scan (snapshot 2026-07-07 ~10:30 UTC; updated Jul 7 ~18:00, Jul 10 ~12:30 & ~21:45 UTC — LIVE POSITION)

*Three-agent live research: (1) Polymarket market state via gamma/CLOB APIs, (2) sharp-book
fair value with Shin de-vig, (3) model/Elo fair value + platform-bias adjustments — applying the
Strategy-B3 methodology from `STRATEGY_SELECTION.md`. This is a point-in-time analysis: two R16
matches (Argentina–Egypt, Switzerland–Colombia) play the evening of Jul 7 and invalidate part of
the table; the Spain thesis dies at Spain–Belgium kickoff Jul 10.*

## The answer

**Most undervalued: Spain at 18.05¢ (PM mid).** It is the only alive team cheap versus the
de-vigged sharp-book benchmark by more than the cost hurdle — Shin-de-vigged FanDuel/consensus
fair ≈ **21.3–21.5%** → gap **−3.3pp**, and the independent Elo bracket convolution puts Spain at
**28%** (highest of all teams). Best estimate of true value after discounting for the caveats
below: **~20–21%**, i.e. ≈ **+2–3pp (+11–17% relative)** over the 18.05¢ price.

**But it is a modest, partially-rational edge, not a slam dunk** — three honest strikes:
1. **Opta's simulator says 13%** and Kalshi trades 18.6 (≈ PM) — two of four benchmarks call PM fair.
2. **Real fitness/bracket reasons for cheapness:** Lamine Yamal is on managed minutes after a
   hamstring issue, and Spain's half contains France (likely SF) — the hardest remaining path.
3. **Platform bias does NOT help here:** at ~12 days to resolution the verified classic FLB says
   sub-50¢ outcomes are, if anything, slightly *overpriced* (the sports short-horizon slope is
   ~0.90–1.10 ≈ calibrated; the recalibration direction at 18¢ is neutral-to-negative). The
   pre-MVP3 "favourites underpriced" result is about high-priced binaries, not 18¢ outcomes in a
   10-way field.
Also: Pinnacle was unobtainable (403), so the book benchmark leans on FanDuel's post-R16 list;
recreational books shade winners after wins, which could explain ~1pp of the gap.

**The clearest OVERvalued side is Argentina at 18.45¢** — rich vs Shin-de-vigged books (+1.9pp,
fair ≈ 16.5–16.6%), rich vs Opta (16.3), rich vs Kalshi (16.9); PM also prices Argentina-to-final
37.5 vs books' ~34.5. Only the Elo convolution disagrees (26%, but inflated by tonight's 84%
advance vs Egypt — a known Bradley-Terry confound). Pattern is consistent with a Messi retail
premium. Norway 5.8¢ is marginally rich (+0.9–1.6pp; Haaland flow). Everything else is inside the
noise/cost band; the neg-risk book sums to 0.9935, so there is no structural discount to harvest.

## Update log — 2026-07-07 ~18:00 UTC re-pull (post Argentina–Egypt)

**Argentina 3–2 Egypt** — from 0–2 down (79'/83'/90+' comeback; Messi missed a first-half
penalty; [FIFA match centre](https://www.fifa.com/en/match-centre/match/17/285023/289288/400021528),
[ESPN](https://www.espn.com/soccer/match/_/gameId/760509/egypt-argentina),
[NPR](https://www.npr.org/2026/07/07/nx-s1-5884872/2026-world-cup-fifa-argentina-egypt-round-of-16)).
Argentina advance to QF4 vs tonight's Switzerland–Colombia winner (still pending at pull time;
PM prices Colombia 2.85¢ vs Switzerland 1.15¢ on the winner board).

Live PM moves (winner market, $87.9M 24h, sum of active mids 0.9915 — book still fair-sum):

| Team | 10:30 → 18:00 | Read |
|---|---|---|
| **Argentina** | 18.45 → **17.45** (−1.0, on $12.9M 24h) | **Fell despite winning.** A fairly-priced team clears an 84%-priced match and gains ~+1pp; falling −1pp instead = pre-match price was ~2pp too rich (our "sell" verdict) *and* the market derated the near-loss performance. **The rich-vs-fair status is now UNKNOWN**: mechanically conditioning stale pre-match book fairs on advancing gives ~19–19.5%, but fresh book odds will have cut Argentina's final-win conditional after that display. **Do not short at 17.45 without a fresh de-vig.** |
| **Spain** | 18.05 → **18.75** (+0.7, no match played) | The undervaluation gap **narrowed to ~+1.5–2.5pp** vs the 20–21% fair estimate. Thesis intact but thinner; entry discipline matters more now (see execution plan). |
| England | 14.45 → 15.25 | drift up; still fair vs 14.7–17 range |
| France | 33.05 → 32.75 | unchanged-fair |

## POSITION LEDGER & NEXT STEPS (Jul 10, 21:45 UTC)

**T0 EXECUTED:** bought **303 Spain YES @ 16.5¢ = $50.00** (maker fill, pre-QF).
**Spain beat Belgium 2–1 in regulation** (Merino 88' — [ESPN](https://www.espn.com/soccer/match/_/gameId/760511/belgium-spain),
[CNN](https://www.cnn.com/2026/07/10/sport/live-news/spain-belgium-world-cup-score)) → **semifinal vs France, Jul 14**.

Mark-to-market at 21:45 UTC: Spain bid 21.1¢ → position worth **$63.93 (+27.9%)**. Board:
France 37.65, Spain 21.15, Argentina 17.65, England 14.85; remaining reserve **$18.50**.

**T1 decision (per plan):**
- 21.15¢ is **below the 26¢ sell-half trigger → HOLD all 303 shares.** No sell.
- The stale-board conditional math suggests Spain may still be 2–4pp cheap, but conditioning a
  Jul-8 board double-counts once both SF opponents advance — a **fresh live-book check decides
  the reserve**: if any sharp book quotes Spain to win the WC at **+310 or shorter** (Shin-fair
  ≥ ~23%), add the $18.5 as a maker bid ≤21.5¢; if **+330 or longer**, hold the reserve in cash.
- **Next checkpoints:** (1) *pre-SF, Jul 13–14:* if Spain trades ≥26¢ before kickoff, sell half
  (~152 sh) as maker — locks ≥$39.5 against the $50 cost, letting the rest ride the France game
  free; below 26¢, hold through the SF (position either dies or roughly doubles). (2) *post-SF:*
  win → T2 rules (hold to final only if ≥2pp cheap vs final-match de-vig, else sell into the
  pre-final peak); loss → sleeve ends ≈ −$50 +$18.5 reserve intact; no revenge redeploy.
- Standing rules unchanged: maker orders only, nothing in-play, reserve deploys only on a
  verified ≥2pp gap.

## PRE-SF CHECKPOINT — 2026-07-12 07:10 UTC: **SELL SPAIN, ROTATE TO ARGENTINA**

Semis set: **France–Spain (Tue Jul 14, Dallas)**, **England–Argentina (Wed Jul 15, Atlanta)**;
Argentina beat Switzerland 3–1 ([ESPN](https://www.espn.com/soccer/match/_/gameId/760513/switzerland-argentina)).
Fresh post-QF book board ([FOX](https://www.foxsports.com/stories/soccer/world-cup-2026-champion-odds)):
France +155, Argentina +300, Spain +330, England +350 (overround 9.7%, Shin z=0.032). SF
moneyline de-vig: France 56.3 / Spain 43.7.

| Team | PM (07:09 UTC) | Shin fair | PM − fair | Verdict |
|---|---|---|---|---|
| France | .3925 | .364 | **+2.8pp** | rich on PM |
| England | .2095 | .200 | +1.0pp | fair-to-rich |
| **Spain (held)** | .1995 | .210 | **−1.0pp** | **edge converged** — inside the 2pp/cost band |
| **Argentina** | .1915 | .227 | **−3.5pp** | **new undervalued signal.** The Messi premium fully inverted: books rank Argentina 2nd; PM ranks them 4th, below England. (Correction: the QF was a 3–1 **extra-time** win, not a rout — mild fatigue caveat, but the +300 was posted post-match and prices it) |

**Actions (recommended, per the plan's own edge rules):**
1. **SELL all 303 Spain as maker at ~19.9–20.0¢** → ≈ $60.30, **locking +$10.30 (+20.6%)**.
   Rationale: the entry thesis is complete — the 3.4pp dislocation we bought at 16.5 has closed
   (+1.0pp residual is inside costs); holding through France is a ~43.7% coin flip with no edge.
   *(Documented alternative for a lottery preference: hold through the SF — position dies or
   ~doubles; not the process play.)*
2. **Rotate $40 into Argentina: maker bid ≤19.2¢ (~208 shares)** — reserve $18.5 + ~$21.5 of
   proceeds. The −3.5pp gap exceeds the 2pp threshold on a fresh same-day board (grade B:
   single-source FOX consensus, partially corroborated by the SF moneylines). Order must rest
   **before Wed's England–Argentina kickoff**; cancel at kickoff−1h if unfilled.
3. Keep **~$39 cash** for the final checkpoint (T2, Jul 16–18): re-run the de-vig after both
   SFs; sell Argentina into strength if it reprices ≥26–27¢ post-SF win; if Argentina loses,
   sleeve still ends green (≈ $39 cash + dust vs $68.5 start… i.e. ≈ −$1.5 net) — the Spain
   profit funds the Argentina risk.

Sleeve state if both orders execute: ≈ $79 gross value vs $68.5 deposited (+15% realized+cash
before the Argentina bet resolves).

### Refresh — Jul 12, 12:07 UTC (final pre-SF numbers)
Board: France 38.85, **England 21.85 (rising)**, **Spain 20.05 (bid .200 — the exit fills
here)**, **Argentina 18.95 (falling, $7.6M 24h)**. No Argentina team news (Messi played the QF
and assisted — [Al Jazeera](https://www.aljazeera.com/sports/2026/7/12/argentina-defeat-switzerland-to-set-up-england-semifinal-at-world-cup-2026));
the England-up/Argentina-down drift on their own SF pairing is flow, not information, and it
**widens the Argentina gap to −3.75pp** while England is now +1.9pp rich — the same
retail-vs-books divergence, sharper. Updated orders: **sell 303 Spain @ .200 = $60.60
(+$10.60, +21.2%)**; **Argentina maker bid .190 (~210 shares ≈ $40)**; England–Argentina
kicks off Wed Jul 15 ~19:00 ET — cancel unfilled bids at kickoff−1h. If Argentina keeps
drifting to ≤18¢ with no news, do NOT chase beyond the $40 — the cluster cap holds.

## Update log — 2026-07-10 12:31 UTC re-pull: **T0 TRIGGERED on Spain** [executed & exited — see checkpoint above]

Bracket state: **France beat Morocco** (QF1) and **Switzerland beat Colombia** (R16) → QF4 =
Argentina–Switzerland (Jul 12). **Spain–Belgium kicks off today ~19:00 UTC** — this is the
T0 decision window (~6h at pull time). England–Norway is tomorrow (Jul 11).

PM winner board (12:31 UTC, $31.7M 24h, mids sum 0.9895): France 38.55¢, Argentina 18.25¢,
**Spain 16.45¢**, England 15.85¢, Norway 5.85¢, Belgium 2.15¢, Switzerland 1.85¢.

**Fresh de-vig** (freshest same-vintage book board, Jul 8 pre-QF: France +180, Spain +360,
Argentina +400, England +460, Norway +1400, Belgium +3000, Switzerland +3300 —
[bookies.com](https://bookies.com/uk/news/world-cup-winner-odds-2026-usa-canada-mexico-8-july-france-favourites-over-argentina-spain-england),
[ESPN](https://www.espn.com/espn/betting/story/_/id/48386952/espn-soccer-futbol-world-cup-betting-odds-championship-groups);
overround 11.7%, Shin z=0.0176):

| Team | PM | Shin fair | PM − fair | Verdict |
|---|---|---|---|---|
| **Spain** | .1645 | **.199** | **−3.4pp** | **UNDERVALUED — T0 triggers.** Fell 18.75→16.45 *without playing* and with **no negative news** — Yamal is fit and starting ([ESPN](https://www.espn.com/soccer/story/_/id/49314604/lamine-yamal-spain-luis-de-la-fuente-excited-belgium), [khelnow](https://khelnow.com/football/will-lamine-yamal-play-spain-vs-belgium-fifa-world-cup-2026)); Spain unbeaten, zero goals conceded. The drop looks like flow rotating to France post-QF1. |
| Argentina | .1825 | .182 | +0.0pp | **Richness fully unwound — now exactly fair.** Short stays suspended. |
| England | .1585 | .162 | −0.3pp | fair |
| France | .3855 | .332* | +5.3pp* | ***Vintage-ambiguous***: the book board predates France's QF win; naive conditional fair ≈ .33/.752 ≈ .44 would make PM ~5pp *cheap*. Unresolvable without fresh post-QF book odds — no action. |
| Norway / Belgium / Switzerland | .0585/.0215/.0185 | .055/.023/.021 | ±0.3pp | fair (longshot zone — leave) |

**T0 action (per the $300 plan):** the Spain gap (−3.4pp on the freshest board; still ~−2pp even
if live books have drifted Spain to +400) exceeds the ≥2pp threshold → **place the $120 maker bid
at 16.4–16.5¢ before ~18:00 UTC** (stop quoting an hour before kickoff; never in-play). Caveat
honestly logged: the Spain book quote is ~2 days old — if a live book shows Spain ≥ +430, the
gap is inside costs and T0 lapses to no-trade. Next checkpoint: T1 after Spain–Belgium resolves.

## Consolidated fair-value table (10:30 UTC, before the Jul 7 evening matches)

| Team | PM mid | Kalshi | Shin de-vig (books) | Opta | Elo convolution | Verdict |
|---|---|---|---|---|---|---|
| France | 33.05¢ | 33.2 | 33.3–33.7 | 31 | 23.4 | fair (Elo low, outvoted) |
| **Argentina** | 18.45¢ | 16.9 | 16.5–16.6 | ~16.3 | 26.4* | **rich +1.9pp — sell side** |
| **Spain** | 18.05¢ | 18.6 | **21.3–21.5** | 13 | **28.0** | **cheap −2–3pp — the pick** |
| England | 14.45¢ | 14.1 | 14.7–15.0 | 17 | 10.5 | fair (models disagree, market between) |
| Norway | 5.80¢ | — | 4.3–4.9 | 7 | 4.9 | marginally rich |
| Colombia | 3.35¢ | — | 3.0–3.4 | 3.4 | 1.7 | fair; repriced tonight |
| Morocco | 2.75¢ | — | 2.4 | 3.2–4 | 2.0 | fair |
| Belgium | 2.25¢ | — | 2.7 | 1.6 | 2.5 | inside costs |
| Switzerland | 0.95¢ | — | 0.7–0.8 | small | 0.6 | fair; plays tonight |
| Egypt | 0.25¢ | — | 0.08–0.35 | small | 0.1 | de-vig-ambiguous; no |

\* Elo Argentina inflated by the not-yet-played 84% Egypt advance probability.

Costs at these prices: taker fee `C·0.03·p(1−p)` ≈ 0.37–0.66¢ on the four contenders + 0.05¢
half-spread (books are 1-tick, $1.4–6.8M gamma liquidity per outcome); maker ≈ 0. Only Spain (buy)
and Argentina (sell) clear the taker hurdle; both clear the maker hurdle comfortably.

## If trading it (per the STRATEGY_SELECTION rules)

- **Structure:** long Spain YES via maker limit ≤18.0¢ (never cross >1 tick), optionally paired
  with short Argentina (buy Argentina NO / sell YES as maker) — the pair is internally consistent
  (PM ranks Argentina above Spain; every book ranks Spain well above Argentina) and hedges some
  tournament-level flow.
- **Timing:** enter only between matches (frozen-liquidity rule) — i.e., after tonight's R16
  games settle and before **Spain–Belgium kickoff Jul 10**, which is the thesis expiry.
- **Sizing:** this is one resolution cluster — the ≤15%/cluster cap applies to the combined pair;
  the ~+2–3pp edge at 18¢ with binary risk sizes to roughly 1–3% of book under ¼-Kelly with the
  ×0.5 evidence haircut.
- **Not tradeable:** every "cheap-looking" longshot (Morocco vs Opta, Norway) — the FLB regime
  says sub-15¢ names are the systematically overpriced zone, and Elo agrees.

## Execution plan — ACTIONABLE $70 REVISION (Jul 10; supersedes the $300 sizing below)

**World Cup budget: $70 (currently USDT on Binance). The TI sleeve is budgeted separately —
see `TI2026_UNDERVALUED.md` §5 (its $300 maker-bid ladder remains operative).**

### Funding path: Binance → Polymarket (~$1–1.5 total cost, ~10–15 min)
1. **Binance Convert: USDT → USDC** (fee-free, instant). Rationale: native USDC avoids the
   auto-swap spread that Polymarket's bridge charges on USDT deposits.
2. **Withdraw USDC on the *Polygon* network** to your Polymarket deposit address (Polymarket →
   Deposit → Transfer Crypto → USDC → Polygon; addresses are per-network — copy the Polygon/EVM
   one). Binance's Polygon-USDC withdrawal fee is ~$1 (check the live fee in the UI). Min deposit
   $2; arrival ~5–10 min; auto-converts to pUSD 1:1.
3. Fallback (one step fewer, slightly worse rate): withdraw **USDT on Polygon** directly —
   Polymarket accepts it (min $2) and auto-swaps to pUSD with a small embedded spread.
4. **Checks before sending $70 in one shot** (a $2 test costs $1 in fees — not worth it at this
   size, so triple-check instead): network = Polygon, address = the one Polymarket shows for
   Polygon/EVM, token = USDC. Wrong-network sends are unrecoverable. Also confirm the platform's
   ToS/geo-eligibility for your jurisdiction before funding.

### $70 World Cup allocation (lands ≈ $68.5 after deposit fees)
| Tranche | Size | Action |
|---|---|---|
| **T0 — Spain (live, triggered)** | **$50** | Maker bid 16.4–16.5¢ (~303 shares) **before ~18:00 UTC today**; cancel if unfilled at kickoff−1h |
| **T1 reserve** | **$18.5** | Post Spain–Belgium: add only if Spain still ≥2pp cheap on a fresh de-vig; or redeploy on a new ≥2pp gap among survivors; else hold |

T1/T2 rules (post Spain–Belgium): win + gap closed (≥26¢) → **sell half as maker** (locks
~+60% on ~$25); win + still ≥2pp cheap → add the $18.5; loss → sleeve is down $50, **stop** —
redeploy the reserve into the SFs only on a fresh ≥2pp verified gap. Pre-final (T2): hold to the
final only if still ≥2pp cheap vs the final-match de-vig, else sell everything as maker into the
pre-final liquidity peak. Honesty at this scale: WC-sleeve EV is roughly **+$6–8 if the Spain
edge is real**; deposit friction alone is ~2% of the bankroll — the value of running this at $70
is process practice (funding, maker execution, checkpoint discipline) as much as the P&L.

## [superseded] Execution plan — $300 sleeve (2–3 re-evaluations before the final)

Style: **trade the reprice, don't marry the final** — held to resolution, a ~20%-fair position
loses ~80% of the time; buying cheap before a gate and selling into strength after it clears
keeps the EV with far less variance. Maker orders only (0 fee + rebate; taker ≈0.45¢ + spread);
never order during a live match; no order without a fresh de-vig showing ≥2pp of edge.

| Checkpoint | Condition → action | Size |
|---|---|---|
| **T0 — before Spain–Belgium (Jul 10)** | Re-run de-vig. If Spain ≤ fair − 2pp (i.e. ≲18.5–19.0 vs fair ≥20.5): maker bid | **$120** |
| T0 optional | Argentina leg **suspended** post-Egypt (see update log) — re-enable only if fresh de-vig shows ≥1.5pp rich | ($45) |
| **T1 — Jul 11–13, Spain won QF** | Re-run. Still ≥2pp cheap → add **$90**. Gap closed (price ~26–30¢) → **sell half as maker** (+45–60% on tranche) | +$90 / −½ |
| T1 — Spain lost QF | Tranche dead (−$120 max). No revenge bets: deploy the remaining $180 only on a new ≥2pp verified gap among survivors; else hold cash | $0 default |
| **T2 — Jul 16–18, pre-final** | Hold to the final only if still ≥2pp cheap vs the final-match de-vig; otherwise sell everything as maker into the pre-final liquidity peak | exit |

Caps: ≤$150 exposure through any single match; max loss $300 by construction. Honest EV:
+$25–35 on the sleeve if the Spain edge is real; the post-Egypt narrowing (gap now ~1.5–2.5pp)
means T0 may legitimately produce **no trade** — that is the system working, not failing.

## Data quality

Byte-fetched/live: Polymarket gamma + CLOB (prices, books, history, fees: sports_fees_v2 3%
taker / 25% maker rebate, tick 0.001, neg-risk, $4.02B event volume); Kalshi page; own Shin
solver (z=0.0146–0.0160 by bisection on FanDuel 12.6% / consensus 11.6% overrounds); own Elo
convolution (exact bracket enumeration; no home teams left; P(advance)=logistic expectancy,
penalties 50/50). Snippet-tier: all bookmaker odds (FanDuel post-Jul-6 primary; stale BetMGM/
bet365 quotes excluded), Opta figures (theanalyst.com 403), Elo ratings (eloratings.net blocked;
footballratings.org snapshot), injury news. **Pinnacle missing entirely** — the single biggest
caveat on the Spain number.
