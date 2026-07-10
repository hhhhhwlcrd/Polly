# TI 2026 (Dota 2) Winner Market — Undervaluation Scan (snapshot 2026-07-07 ~13:30 UTC; updated ~17:45 UTC)

*Five-agent live research applying the Strategy-B3 methodology (`STRATEGY_SELECTION.md`):
(1) Polymarket/tournament state via gamma+CLOB APIs, (2) bookmaker benchmark + Shin de-vig,
(3) team strength & form, (4) data-API spec (feeds `../ti2026/` notebooks), (5) modeling methods
& esports-market biases. Companion pipeline: **`ti2026/`** (OpenDota collector, player/team
features, Elo+Monte-Carlo model, Polymarket comparison notebook).*

## 0. Read this first — the market is a shell, and that IS the finding

The Polymarket market ("The International 2026: Winner", created Jun 29, neg-risk, 16 teams,
resolves via Dotabuff by Sep 6) has traded **$4,237 lifetime** ($45 in 24h). Spreads are 8–38¢,
two outcomes have **no bid at all**, the sum of mids is **1.92** (vs 1.00 fair) and the sum of
best bids is **0.686**. Displayed "odds" are market-maker placeholder quotes, not consensus.
Meanwhile **no bookmaker has posted TI 2026 outrights yet** (Pinnacle: "markets currently not
open"; books historically appear 3–5 weeks out, after the Esports World Cup). Consequences:

1. **At displayed mids, NOTHING is undervalued** — the whole book sums to 192%; every mid is at
   or above any defensible fair value. The two "cheapest-looking" verdicts in mid-space (LGD 22¢,
   HULIGANI/Resilience 19¢) are pure no-bid artifacts (real bids: 3¢ / none / none).
2. **The undervaluation lives on the bid side**: best bids sum to 0.686, i.e. resting buyers are
   collectively offering 31% less than a fair book. The actionable edge is *posting maker bids
   below fair value* in a market with no informed flow yet — exactly the thin/immature-market
   condition (iii) from the fade-rule in `STRATEGY_SELECTION.md`.
3. This is a **relative-value table**, therefore: fair-value bands are synthesized from the season
   evidence + the one live (partial, C-grade) EWC bookmaker list + the TI-history prior — not from
   a de-viggable TI book, because none exists. Confidence is correspondingly wide.

## 0b. Update log — 2026-07-07 ~17:45 UTC re-pull (EWC day 1 in progress)

TI winner book: **zero new trades** ($4,237 lifetime unchanged; 24h volume still the single $45
Xtreme print). Quote-side moves only, and they *tightened toward our fair bands*:
- **TEAM VISION best bid .09 → .11** (mid .16 → .17) — the bid side is converging on our 13–17%
  band floor; the recommended resting-bid level moves up accordingly (see §6 ladder).
- Team Spirit bid .07 → .08 (mid .115 → .12); Yandex bid .12 → .11 (mid .230 → .225). Everything
  else unchanged; sum of mids 1.93 — still a shell book.

EWC winner market (form anchor, $82.6k vol, $47k in 24h — this one is live and trading): Yandex
.21, PARIVISION .16, Falcons .15, **Aurora .10 → .11**, Spirit .095, BetBoom .095, 1W .0585,
**LGD .0375 → .044**, **Liquid .0525 → .041** (day-1 drift; group matches were in progress at
pull time — treat as noise until Liquipedia standings post). No day-1 upsets large enough to move
the TI fair bands yet.

## 1. Fair-value synthesis (before comparing to Polymarket)

Inputs: 2025-26 tier-1 results map (Yandex 3 titles + 2 finals since Dec; VISION #1 GosuGamers
Elo + DL S29 title; Tundra/1w 4 titles pre-patch-7.41 then 4 straight poor events; Falcons
reigning TI champs, longest-tenured roster, flat 2026), EWC bookmaker top-6 (VISION 20%raw,
Yandex 20, Aurora 14.3, Falcons 14.3, Spirit 9.1, Liquid 7.7 — single-source, ~10–20% vig,
24-team field), and the TI calibration prior (favourite won only ~4 of 14 TIs — though the last
three winners were favourite-tier; cap any favourite ≤ ~20% two months out with a pre-TI patch
pending; Glicko-RD logic says widen everything).

| Team | Fair band | Basis |
|---|---|---|
| Team Yandex | **16–20%** | form team of 2026 (3 titles); EWC co-favourite |
| TEAM VISION | **13–17%** | #1 Elo, DL S29 champs, Puppey; pos-5 new (~1 mo) |
| Team Falcons | **11–14%** | reigning champs, 2.5-yr roster, TI pedigree; flat form |
| BetBoom (BoomBoys) | 7–10% | Wallachia S8 champs, stable 2026 |
| Aurora | 7–10% | 3 finals in 2026, no title ("bridesmaid" profile) |
| Team Spirit | 6–9% | pedigree + volatility; pos-5 swapped May; crowd-favourite premium risk |
| Team Liquid | 5–7% | Slam VI title; steady tier-1.5 |
| 1w Team (ex-Tundra) | 4–7% | highest variance: 4 titles pre-7.41, slump since + org sale |
| Xtreme Gaming | 3–5% | TI25 runner-up but declining; Shanghai home soil |
| LGD (ex-HEROIC) | 3–5% | Slam VII finalists, long cohesion; unproven vs elite EEU |
| OG | 1.5–3% | rebuilt SEA roster; the "OG magic" is narrative, not data |
| Nigma Galaxy | 1–2% | qualifier team; big fanbase = retail-premium risk |
| HULIGANI | 1–2% | open-qualifier Cinderella; beat NAVI/VP once |
| Team Resilience | 1–2% | CN qualifier tier |
| GamerLegion | 1–2% | NA's lone slot |
| Vici Gaming | 0.5–1.5% | weakest CN qualifier |

## 2. The undervaluation table vs current Polymarket quotes

`Δmid` = fair-band midpoint − PM mid (positive = undervalued at displayed odds).
`Buy@ask?` = does buying at the current ask clear fair value + costs (sports-fee schedule
`sports_fees_v2`, ~0.75% max effective + spread)? `Maker bid` = a defensible resting-bid level.

| Team | PM bid/ask (mid) | Fair band | Δmid | Buy@ask? | Verdict & action |
|---|---|---|---|---|---|
| **TEAM VISION** | .09/.23 (.160) | 13–17% | **−1pp ≈ fair** | No (.23 > fair) | **Closest to genuinely cheap** at mid; strongest Δ vs EWC book (−11pp Shin-normalized). Post maker bids .10–.12 |
| **Team Falcons** | .08/.20 (.140) | 11–14% | −1.5pp ≈ fair | No | Champion pedigree at a fair mid; bid .09–.11 |
| **Aurora** | .06/.14 (.100) | 7–10% | −1.5pp ≈ fair | No | Fair-ish; bid .07–.08 |
| **Team Yandex** | .12/.34 (.230) | 16–20% | −5pp rich | No (.34 absurd) | Favourite, but mid already above fair; bid .13–.15 only |
| BetBoom/BoomBoys | .07/.17 (.120) | 7–10% | −3.5pp rich | No | bid ≤.08 |
| Team Spirit | .07/.16 (.115) | 6–9% | −4pp rich | No | Crowd-premium candidate — do not chase |
| Team Liquid | .05/.16 (.105) | 5–7% | −4.5pp rich | No | bid ≤.06 |
| 1w Team | .06/.13 (.095) | 4–7% | −4pp rich | No | Patch-lottery ticket; bid ≤.05 if at all |
| Xtreme Gaming | .02/.12 (.070) | 3–5% | −3pp rich | No | Home-soil narrative will attract flow; bid ≤.04 |
| LGD Gaming | .03/.41 (.220) | 3–5% | **−18pp artifact** | Never | Mid is a no-bid illusion; nothing to buy, nothing to short (no bids) |
| HULIGANI / Resilience | —/.38 (.19) | 1–2% | −17pp artifact | Never | Same artifact |
| Nigma / OG / GamerLegion | asks .079–.149 | 1–3% | rich | No | Classic FLB zone + fan premium (Nigma) — asks are 3–7× fair |
| Vici Gaming | .009/.019 (.014) | 0.5–1.5% | ≈ fair | Marginal | The only ask *inside* a fair band's upper edge — and still no edge net of variance |

**Bottom line:** according to current Polymarket odds, **no team is undervalued at executable
(ask) prices, and only TEAM VISION / Falcons / Aurora are even fair at displayed mids** — the
book as a whole is 92% overpriced at mids and 31% underbid at bids. The correct trade today is
not "buy the undervalued team" but **be the market**: post maker bids at the levels above (they
sit at or below the bottom of each fair band), collect the thin-book premium, and let impatient
flow cross to you. If forced to name the single most undervalued team in the displayed odds:
**TEAM VISION at a 16.0¢ mid vs a 13–17% fair band with the largest normalized gap vs the only
live bookmaker list** — followed by Falcons (14.0¢ vs 11–14%) and Aurora (10.0¢ vs 7–10%).

## 3. Bias checklist applied (why the table looks like this)

- **FLB (verified, this repo):** at 1mo+ horizons longshots are systematically overpriced —
  every sub-10¢ ask here (Nigma .149, OG .085, GamerLegion .079) is 3–7× the fair band. TI's
  "Cinderella wins" lore (OG TI8, Spirit TI10, Tundra TI11) is real but already over-monetized:
  retail over-bets underdogs ≤28% implied (Sweeney et al.).
- **Crowd-favourite premium (byte-verified at TI 2025):** Nigma did more Polymarket volume than
  Spirit/Liquid/Tundra despite being far weaker — expect Spirit/Nigma/OG asks to stay rich.
- **Favourite cap:** pre-event favourites won ~4/14 TIs; with a pre-TI patch pending (7.42
  expected; 1w's and Xtreme's form already flipped once on 7.41) no team deserves >20% today.
- **Settlement wedge:** ~7 weeks to resolution ≈ 0.5% — minor, but it means resting bids should
  sit ~½–1¢ below target fair, not at it.
- **Fee flag:** the market carries `sports_fees_v2` with makerBaseFee=takerBaseFee=1000 raw
  units — the effective taker rate needs empirical confirmation before any taker order (the
  notebooks read it from the market's fee fields; makers earn rebates either way).

## 4. Invalidation schedule & re-run plan

1. **EWC 2026 (Paris, Jul 7–19 — started today):** 13 of 16 TI teams present; a deep
   Yandex/VISION/Falcons run moves everything 3–8pp. Re-run `ti2026/notebooks/03→05` after.
2. **Bookmaker TI outrights post ~late July** (Pinnacle/GG.bet): the moment a full Shin de-vig
   becomes possible — that is when this table upgrades from relative-value to true deviation.
3. **Games of the Future (Astana, Jul 31–Aug 5)** — last form signal, 8 days before TI.
4. **The pre-TI patch (7.42/7.41e):** biggest single model risk; widen all bands on release
   (the `elo_sigma` knob in `ti2026/src/model.py` exists for exactly this).
5. Polymarket book formation: at $4k volume, one $500 order moves everything; recheck before
   quoting.

> **Budget note (Jul 10, corrected):** the $70 budget applies to the **World Cup sleeve only**
> (see `WC2026_UNDERVALUED.md`, which also carries the Binance→Polymarket funding path). This
> TI plan's $300 sizing below remains operative as written.

## 5. Execution plan — $300 sleeve (re-evaluate every 1–2 weeks + in-tournament)

The book is a shell, so the sleeve is deployed as a **maker-bid ladder**, not purchases. Fills
only happen when someone crosses down to us — we either buy below fair or don't trade at all.
Never cross an ask; nothing in the sub-10¢ FLB zone.

**Phase 1 — now (post day-1 update): GTC maker bids, ~$150 notional if all fill**

| Team | Bid level | Shares | Cost if filled | vs fair band |
|---|---|---|---|---|
| TEAM VISION | **.12** (best bid now .11) | ~415 | $49.8 | floor of 13–17% |
| Team Falcons | **.10** (best bid .08) | 400 | $40.0 | floor of 11–14% |
| Team Yandex | **.14** (best bid .11) | ~285 | $39.9 | below 16–20% |
| Aurora | **.07** (best bid .06) | 300 | $21.0 | floor of 7–10% |

Standing rules: **cancel a team's bid before its EWC elimination/decider matches** (a fill during
a live loss is pure adverse selection — the main way this ladder loses); refresh levels at each
weekly re-eval; a fill immediately followed by bad news gets re-checked against the new fair band,
not averaged down.

**Phase 2 — ~Jul 20–28 ($100 reserve):** EWC concludes Jul 19 and bookmakers historically post TI
outrights in this window. Run `ti2026/notebooks/05` with real book odds → true Shin de-vig. Buy
(maker) anything ≥2pp below Shin-fair net of costs; **sell any filled Phase-1 leg that has gone
≥2pp rich** as the book tightens — monetizing book formation without tournament risk.

**Phase 3 — during TI, Aug 13–23 ($50 reserve):** the documented dip-buy — a top-3-fair team with
a bad Swiss start that survives to playoffs gets oversold (TI25: Falcons went 2–3 in Swiss, price
crashed, won the title through the upper bracket). Maker bids between series only.

Expectations, honestly: EV on the sleeve is small in dollars (+$20–50 if the bands are right);
most bids may never fill; a filled leg still loses ~85% of the time if held to resolution —
the sell-into-strength rules in Phases 2–3 are where edge converts to realized P&L.

## 6. Sources & data quality

Polymarket gamma/CLOB pulled live 13:22–13:30 UTC (event id 649201; A-grade). Tournament facts
(Shanghai Aug 13–23; Swiss Aug 13–16 → 8-team main event Aug 20–23; 7 invites + 9 qualifier
winners; renames BetBoom→BoomBoys, ex-Tundra→1w) cross-checked ≥2 snippets (B-grade; Liquipedia/
OpenDota/datdota/STRATZ egress-blocked in this sandbox — full list in the doc bodies). EWC odds:
single snippet, book unnamed (C-grade). Season results/rosters: GosuGamers/Forbes/esports.gg
snippets, mutually consistent. Modeling priors: TrueSkill2 PDF (byte-verified — Halo-based,
correction applied), OpenDota/datdota rating parameters read from production source code,
TI 2025 Polymarket volumes byte-pulled ($1.62M, 78% on the two finalists).
