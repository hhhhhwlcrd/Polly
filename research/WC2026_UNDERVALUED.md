# WC-2026 Winner Market — Undervaluation Scan (snapshot 2026-07-07 ~10:30 UTC)

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

## Data quality

Byte-fetched/live: Polymarket gamma + CLOB (prices, books, history, fees: sports_fees_v2 3%
taker / 25% maker rebate, tick 0.001, neg-risk, $4.02B event volume); Kalshi page; own Shin
solver (z=0.0146–0.0160 by bisection on FanDuel 12.6% / consensus 11.6% overrounds); own Elo
convolution (exact bracket enumeration; no home teams left; P(advance)=logistic expectancy,
penalties 50/50). Snippet-tier: all bookmaker odds (FanDuel post-Jul-6 primary; stale BetMGM/
bet365 quotes excluded), Opta figures (theanalyst.com 403), Elo ratings (eloratings.net blocked;
footballratings.org snapshot), injury news. **Pinnacle missing entirely** — the single biggest
caveat on the Spain number.
