# TI 2026 Main Event — Statistical Analysis & Bet Recommendation

*Snapshot 2026-08-19 ~10:35 UTC. Main Event Aug 20–23, Shanghai. Winner book: $1,698,029 volume,
$133k/24h. Model: `ti2026/src/bracket8.py` (8-team double-elim Monte Carlo). Supersedes the
Aug-14 pricing in `TI2026_MARKET_ANALYSIS.md`.*

---

## 0. The answer in one paragraph

**The winner market is now efficiently priced, and at the ask there is no bet with a reliable
edge.** TEAM VISION at 42¢ is correctly the favourite — my balanced model says 40.8% against a
39.3% de-vigged market, i.e. the book has it right to within noise. The clearest *mispricings*
are all on the sell side (Team Spirit and 1w Team are too expensive in every scenario I ran), and
you cannot easily sell in this book. **If you want a winner bet, VISION is the honest pick and
you are paying only ~1–2pp of vig for it. If you want +EV, don't cross the ask — the vig at the
ask is 13.3%, and the genuinely mispriced market right now is the "longest game" book, not the
winner book.**

---

## 1. Where the tournament stands

The Swiss stage finished Aug 16. **All eight survivors start in the UPPER bracket** — there is no
pre-seeded lower bracket, so price differences are *pure strength judgments* with no structural
handicap to net out. 14 series, all Bo3 except a Bo5 grand final with no upper-bracket advantage.

**Quarterfinals, Thu Aug 20** (the three direct qualifiers chose their opponents):

| Match | Model P(advance) |
|---|---|
| 1w Team vs **Team Spirit** | 42.5% / **57.5%** |
| **TEAM VISION** vs BoomBoys | **72.3%** / 27.7% |
| **Team Liquid** vs Team Yandex | **55.4%** / 44.6% |
| Nigma Galaxy vs **Team Falcons** | 38.5% / **61.5%** |

VISION used the #1 seed's pick to draw **BoomBoys — the weakest survivor (2–3 Swiss)**. That is a
real, earned advantage and it is already in the prices.

**Final Swiss form:**

| Team | Series | Games | Game WR | Read |
|---|---|---|---|---|
| TEAM VISION | 4–0 | 8–2 | **80%** | Only undefeated team; beat Falcons, Spirit, BoomBoys |
| Nigma Galaxy | 4–1 | 8–2 | **80%** | Four straight 2–0s — but vs OG (1–4), LGD, Vici (2–3); one real scalp (Spirit) |
| Team Liquid | 4–1 | 9–5 | 64% | Grindy; three of four wins went 3 games |
| Team Spirit | 3–2 | n/p | n/p | 3–0 start, then **0–2 to VISION and 0–2 to Nigma back-to-back** |
| 1w Team | 3–2 | n/p | n/p | Beat Nigma and Falcons; lost to BoomBoys, Liquid |
| Team Falcons | 3–2 | 8–7 | **53%** | Worst game rate of the survivors; every series went 3 |
| BoomBoys | 2–3 | n/p | n/p | Worst survivor record |
| Team Yandex | 2–3 | n/p | n/p | Wins only over HULIGANI (0–4) and Resilience |

---

## 2. The model

Structure validated first: with eight identical teams the simulator returns 12.5% each — the
bracket is symmetric, as it should be. (For contrast, a *pre-seeded* 4-UB/4-LB bracket is worth
21.8% vs 3.2% per seat — a 6.9x edge. That asymmetry does **not** apply here.)

Ratings are the honest problem: five Bo3 series is ~10–14 games, and a game win rate from 10
games carries a ±13pp standard error. So rather than assert one rating set, I ran three, varying
only how much weight the Swiss stage gets against pre-TI evidence (season titles, EWC 2026,
GosuGamers Elo):

**P(champion), model vs Shin-de-vigged market:**

| Team | S1 prior-heavy | S2 balanced | S3 form-heavy | Market |
|---|---|---|---|---|
| TEAM VISION | 30.3 | **40.8** | 53.5 | **39.3** |
| Team Spirit | 11.3 | 9.3 | 6.4 | 12.6 |
| Team Liquid | 10.9 | 13.0 | 14.7 | 12.1 |
| Team Falcons | 14.8 | 12.4 | 8.6 | 10.2 |
| Team Yandex | 14.1 | 8.4 | 3.2 | 7.5 |
| 1w Team | 5.8 | 4.8 | 3.1 | 6.6 |
| BoomBoys | 10.0 | 6.9 | 3.6 | 5.8 |
| Nigma Galaxy | 2.8 | 4.4 | 6.9 | 5.8 |

The market sits almost exactly on the **balanced** scenario. That is a strong sign of an
efficient book: it is neither over-reacting to Swiss form nor ignoring it.

---

## 3. Why almost every edge dies at the ask

| | Sum |
|---|---|
| Best bids | 1.007 |
| Mids | 1.070 |
| **Asks** | **1.133** |

Spreads are 1–2¢ on 6–13¢ contracts — **8–25% of the contract price**. Buying at the ask means
paying a 13.3% vig, which swamps every edge in the table above.

**Edge vs the ask, net of the taker fee (percentage points):**

| Team | Ask | S1 prior | S2 balanced | S3 form | Worst | Best |
|---|---|---|---|---|---|---|
| TEAM VISION | .42 | −12.4 | −1.9 | **+10.8** | −12.4 | +10.8 |
| Team Yandex | .083 | **+5.6** | −0.1 | −5.3 | −5.3 | +5.6 |
| BoomBoys | .07 | +2.8 | −0.3 | −3.6 | −3.6 | +2.8 |
| Team Falcons | .12 | +2.5 | +0.1 | −3.7 | −3.7 | +2.5 |
| Team Liquid | .14 | −3.5 | −1.4 | +0.3 | −3.5 | +0.3 |
| Nigma Galaxy | .079 | −5.3 | −3.7 | −1.2 | −5.3 | −1.2 |
| 1w Team | .081 | −2.5 | −3.5 | −5.2 | −5.2 | −2.5 |
| Team Spirit | .14 | −3.1 | −5.1 | −8.0 | −8.0 | −3.1 |

**Every single team has a negative worst case.** Only VISION under a form-heavy view (+10.8)
and Yandex under a prior-heavy view (+5.6) offer real edge, and those are bets on a *rating
philosophy*, not on a mispricing.

**Robust findings (same sign in all three scenarios):**
- **Team Spirit is overpriced** (−3.1 to −8.0). Consistent with the crowd-favourite premium this
  project has documented before: big fanbase, EWC-2025 pedigree, but a 0–2/0–2 collapse to
  VISION and Nigma at the end of the Swiss.
- **1w Team is overpriced** (−2.5 to −5.2).
- **Nigma Galaxy is overpriced** (−5.3 to −1.2) — the classic hot-qualifier trap: an 80% game
  rate built largely against OG (1–4), LGD and Vici.

---

## 4. The recommendation

**Primary: if you want a winner bet, buy TEAM VISION — but understand what you are buying.**
At 42¢ you are paying ~1–2pp over fair. That is cheap by betting standards (a sportsbook would
charge 5%+), and VISION is the correct favourite on every piece of evidence: only undefeated
team, best game rate, EWC 2026 champion, DreamLeague S29 champion, #1 pre-TI Elo, beat three of
the seven other survivors head-to-head in the Swiss, and drew the weakest opponent in the QF.
It is **not value**, it is a fairly-priced bet on the best team.

**Do not buy Team Spirit at 14¢, 1w at 8.1¢, or Nigma at 7.9¢** — negative in every scenario.

**Better than any of the above: don't cross the ask.** Maker bids that clear a 3pp edge under
the conservative balanced model:

| Team | Model (balanced) | Bid at or below | Current bid / ask |
|---|---|---|---|
| TEAM VISION | 40.8% | **.378** | .400 / .420 |
| Team Liquid | 13.0% | .100 | .120 / .140 |
| Team Falcons | 12.4% | .094 | .100 / .120 |

A resting VISION bid at .375–.38 converts a −1.9pp taker trade into a +3pp maker trade, costs
zero fees, and earns rebates. It may not fill — that is the trade-off.

**Sizing.** This is one cluster (all eight outcomes resolve off the same tournament), so the
≤15%-of-bankroll cluster cap from `STRATEGY_SELECTION.md` applies to the whole TI book. On the
~$130 you have, that is **~$20 total** across everything TI. A VISION position of $12–15 is the
sensible ceiling.

### The better bet is not in this market

The **longest-game** book is genuinely mispriced. State: group stage complete at 109 games, the
record is still the 94:38 VISION–Falcons game from Day 1, and only ~37 games remain.

| Bucket | Model (range across tail models) | Market |
|---|---|---|
| **91-95 (i.e. the record holds)** | **0.52 – 0.67** | mid .46, **bid .18 / ask .74** |
| 96-100 | 0.11 – 0.14 | ask .66 |
| 101-105 | 0.08 – 0.10 | ask .65 |
| 106-110 | 0.05 – 0.08 | ask .66 |
| 111+ | 0.05 – 0.17 | **bid .21** / ask .66 |

Market mids sum to **1.895** — the book is unformed and the mids are meaningless. Every ask is
unbuyable. The two real plays: a **maker bid on 91-95 at ≤.50** (fair ~0.62), and **buying NO on
111+ at ~.79** (fair NO 0.83–0.95). Both are maker-side in a thin book, which is exactly the
edge profile this project has repeatedly concluded is the durable one.

---

## 4b. PER-TEAM BREAKDOWN (prices refreshed 2026-08-19 15:46 UTC, pre-QF)

Book state: **bid-sum 1.019 · mid-sum 1.068 · ask-sum 1.117**. Spreads tightened through the day
(VISION 2¢→1¢). Nigma drifted down (.0645→.052), Spirit up (.135→.145).

| Team | Bid | Ask | Spread | as % of price | Shin fair | QF win% | Top-4% | Model prior / bal / form | Edge @ ask |
|---|---|---|---|---|---|---|---|---|---|
| **TEAM VISION** | .400 | .410 | .010 | 2% | 38.9 | **72.3** | **78.4** | 30.4 / **40.8** / 53.4 | −1.0 |
| **Team Spirit** | .140 | .150 | .010 | 7% | 13.6 | 57.5 | 49.0 | 11.2 / 9.3 / 6.5 | **−6.1** |
| **Team Liquid** | .120 | .140 | .020 | 15% | 12.2 | 55.4 | 56.7 | 11.0 / 13.0 / 14.7 | −1.4 |
| **Team Falcons** | .100 | .120 | .020 | 18% | 10.2 | 61.5 | 55.6 | 14.7 / 12.5 / 8.6 | **+0.2** |
| **Team Yandex** | .082 | .085 | .003 | 4% | 7.6 | 44.6 | 46.8 | 14.0 / 8.4 / 3.3 | −0.3 |
| **1w Team** | .067 | .088 | .021 | 27% | 7.1 | 42.5 | 36.7 | 5.8 / 4.8 / 3.1 | **−4.3** |
| **BoomBoys** | .060 | .070 | .010 | 15% | 5.8 | 27.7 | 40.4 | 10.0 / 6.9 / 3.6 | −0.3 |
| **Nigma Galaxy** | .050 | .054 | .004 | 8% | 4.6 | 38.5 | 36.4 | 2.8 / 4.4 / 6.9 | −1.2 |

### Team profiles

**TEAM VISION (PARIVISION) — .400/.410 · fair ~40.8%**
Swiss **4–0, 8–2 games (80%)** — the only undefeated team. Head-to-head vs survivors: **3–0**
(Falcons 2–1 incl. the 94-min game, Spirit 2–0, BoomBoys). Credentials: EWC 2026 champion,
DreamLeague S29 champion, #1 pre-TI Elo, coached by Puppey. Used the #1 seed to pick **BoomBoys**
— the weakest survivor — giving a 72.3% QF and a 78.4% top-4. *The correct favourite; priced
right, not cheap.*

**Team Spirit — .140/.150 · fair ~9.3% → the clearest overpricing**
Swiss **3–2**. Opened 3–0, then **0–2 to VISION and 0–2 to Nigma back-to-back**, then needed
three games to beat Resilience (2–3 team) in the elimination round. H2H vs survivors **1–2**.
Pedigree is real (EWC 2025 champion, Yatoro/Collapse) and that is what the market is paying for —
the crowd-favourite premium this project has documented before. Negative in **all three**
scenarios (−3.1 to −8.0). Also drew the toughest QF of the top seeds (1w, 57.5%).

**Team Liquid — .120/.140 · fair ~13.0%**
Swiss **4–1, 9–5 games (64%)**. Grindy: three of four wins went the distance. H2H **2–1** (beat
Yandex, beat 1w; lost to Spirit 1–2). BLAST Slam VI champion. The one team that looks mildly
*better* the more weight you give recent form (11.0 → 13.0 → 14.7 across scenarios). Note the
2¢ spread is 15% of the price — maker-only.

**Team Falcons — .100/.120 · fair ~12.5% → the only non-negative edge at the ask**
Swiss **3–2, 8–7 games (53%)** — the worst game rate among survivors; every series went three.
H2H **0–2** (lost to VISION and 1w). But: **defending TI champions**, longest-tenured roster in
the field, and they did *exactly this* last year — scraped the TI14 group stage and won the
title. Prior-heavy 14.7% vs form-heavy 8.6% is the widest philosophical split in the field.

**Team Yandex — .082/.085 · fair ~8.4%**
Swiss **2–3**; wins only over HULIGANI (0–4) and Resilience, plus a 2–1 elimination-round win
over LGD. Blew a lead in a reverse sweep to Aurora. Yet **#2 pre-TI Elo with three season titles**
(DreamLeague S27, Wallachia S7, BLAST Slam VII). The biggest prior-vs-form gap on the board:
14.0% if you trust the season, 3.3% if you trust the Swiss.

**1w Team (ex-Tundra/1win) — .067/.088 · fair ~4.8% → second-clearest overpricing**
Swiss **3–2**, top elimination-round seed. H2H **2–2** (beat Nigma 2–0 and Falcons 2–1; lost to
BoomBoys and Liquid). Four titles pre-patch-7.41, then a slump plus an org sale. Negative in all
three scenarios (−2.5 to −5.2). The **27% spread** (.067/.088) is the widest in the book — a
taker here pays enormously.

**BoomBoys (BetBoom) — .060/.070 · fair ~6.9%**
Swiss **2–3**, the worst record of any survivor, and drew the worst possible QF (VISION, 27.7%).
Offsetting: EWC 2026 runner-up and Wallachia S8 champion, and they reversed a 0–2 Swiss loss to
Aurora into a 2–0 elimination-round win 24h later. Prior-heavy 10.0% vs form-heavy 3.6%.

**Nigma Galaxy — .050/.054 · fair ~4.4% → the hot-qualifier trap**
Swiss **4–1, 8–2 games (80%)** — tied with VISION for the best game rate, four straight 2–0s.
But the schedule was weak: OG (1–4), LGD, Vici (2–3), with **one real scalp (Spirit 2–0)**. They
also opened 0–2 to 1w. Pre-tournament they were the weakest team in the field at 1.7¢. Negative
in all three scenarios; the market has already re-rated them from 1.7¢ to 5.2¢ and the drift is
now *down* (.0645 → .052 today).

## 5. Scorecard — including the call I got wrong

**Radiant/Dire: my Aug-14 call was wrong.** I wrote that Dire at 30.5¢ looked cheap on a central
estimate of ~0.50, flagging that the two research passes conflicted on TI14's radiant rate and
that the position should be small pending resolution. The group stage resolved it against me:
TI15 came in at **54% Radiant**, giving Radiant a 59–50 lead with only ~37 games left. Radiant
now trades .9475 and my model agrees (0.88–0.96). Anyone who took the Dire side is down ~2/3.
The guardrail worked — "size small, resolve the conflict first" — but the directional call was
a miss, and the lesson is that the pub-vs-pro reference-class argument I leaned on was weaker
than the tournament's own sample.

**Most-banned Treant: right, and the market has caught up.** I priced it ~0.95 when it traded
.63 bid. Treant finished the group stage **101 bans + 8 picks = 100% contested across all 109
games**. It now trades .90 bid / .99 ask — fairly priced, no edge left. The edge existed for
about five days.

**TEAM VISION at 12¢ (July): +242%** at the current 41¢. The Aurora rung of that same ladder
went to zero. Both are in the ledger.

---

## 6. Honest limits

Every tournament fact here is **search-snippet-derived** — Liquipedia, OpenDota, Stratz, Dotabuff
and most esports press are egress-blocked from this environment. Cross-checks that survived:
Day-1 series reconstruct to exactly 29 games; Treant's 28+1 also sums to 29; the Swiss format
arithmetic closes exactly (1×4-0, 2×4-1, 5×3-2, 5×2-3, 2×1-4, 1×0-4). Not verified: game records
for 11 of 16 teams, the exact lower-bracket cross-seeding rule (TI convention assumed), and
whether the grand final carries any upper-bracket advantage (no source states it either way; TI
never has). The ratings driving the model are my judgment calls on public evidence, which is why
§2 gives three scenarios instead of one number.

---

## 7. $100 allocation — worked calculation (2026-08-19, pre-QF)

**Critical precondition: at the ASK nothing is +EV** (VISION −0.5%, Yandex −2.0% per dollar).
Both legs are only positive as **maker orders resting at the current bid**. Fair values below are
the equal-weight blend of the three rating scenarios (VISION 41.5%, Yandex 8.6%).

**Sleeve 1 — $50 on VISION + Yandex, split proportional to EV/dollar**

| Leg | EV/$ @ bid | Stake | Order | Shares | Pays if it wins |
|---|---|---|---|---|---|
| VISION | +3.8% | **$23.08** | maker buy @ **0.400** | 57.7 | $57.70 |
| Yandex | +4.5% | **$26.92** | maker buy @ **0.082** | 328.3 | $328.30 |

Staked $50 · **EV +$2.10 (+4.2%)** · P(one of them wins) 50.1%

**Sleeve 2 — $50 into a genuinely independent +EV outcome**
Longest-game market: buy **NO on "111+" at 0.86** (the 111+ YES bid is .14 against a model fair
of ~.10). 58.1 shares. Fair NO ≈ 0.90 → **EV +$2.12 net of the taker fee (+4.2%), win prob ~90%.**
This is the only takeable (non-maker) edge left on the board and it is near-independent of who
lifts the Aegis.

**Combined $100 distribution**

| Scenario | Prob | Net P&L |
|---|---|---|
| another team wins + no 111+ game | 44.9% | −$41.86 |
| VISION + no 111+ game | 37.4% | +$15.84 |
| Yandex + no 111+ game | 7.7% | +$286.43 |
| another team + 111+ game | 5.0% | −$100.00 |
| VISION + 111+ game | 4.2% | −$42.30 |
| Yandex + 111+ game | 0.9% | +$228.29 |

**Total EV +$4.42 (+4.4%) · P(finish ahead) 45.9%**

### Two honest warnings

1. **This is ~4.5x Kelly.** Log-optimal sizing on these edges is ~$22 total across five legs
   (EV +$1.77, P(profit) 81.8%), not $100. You are deliberately overbetting for a bigger swing.
2. **"Proportional to EV" is a longshot trap in a mutually-exclusive book.** Spreading the second
   $50 across Falcons/BoomBoys/Liquid raises EV to +$13.38 but drops P(profit) to 40.2% — because
   EV/dollar peaks on longshots, it under-funds VISION, so the *most likely* winner (42%) leaves
   you down $80. Higher EV, worse odds of finishing ahead. Choose consciously.

**Fill risk:** QFs start Aug 20 02:00 UTC. Both maker bids sit at the current best bid and may
not fill. Crossing to the ask instead costs ~0.5% (VISION) / ~2.0% (Yandex) — cheap certainty if
you want the position on before the games.

---

## 8. Quarterfinal-day allocation (2026-08-19 16:03 UTC, QFs start Aug 20 02:00 UTC)

**Per-match markets exist and are far better priced than the winner book:** ~1% vig and 1¢
spreads, versus 13% at the outright. They are also internally coherent — game-winner, match-winner,
BO3 handicap and O/U-2.5-games all reconcile to within 1–2pp of each other.

| Match | Market (match winner) | Model (balanced) | Verdict |
|---|---|---|---|
| Iron Wing vs **Team Spirit** | .535 / .465 | .425 / **.575** | model likes Spirit +10.5pp |
| **TEAM VISION** vs BoomBoys | .735 / .265 | .723 / .277 | agree — no bet |
| **Team Liquid** vs Team Yandex | .545 / .455 | .554 / .446 | agree — no bet |
| **Nigma Galaxy** vs Falcons | .335 / .665 | **.385** / .615 | model likes Nigma +4.5pp |

**$50 across today's games — only two sides clear a 2% hurdle:**

| Bet | Order | Stake | Shares | Raw EV/$ | Confidence |
|---|---|---|---|---|---|
| **Team Spirit** to beat Iron Wing | buy @ .47 | **$25.65** | 54.6 | +20.8% | **low (0.40)** |
| **Nigma Galaxy** to beat Falcons | buy @ .34 | **$24.35** | 71.6 | +11.3% | medium (0.70) |

Split is proportional to *confidence-adjusted* EV (+8.3% vs +7.9%), which lands near 50/50.
**Do not bet VISION/BoomBoys or Liquid/Yandex** — model and market agree within 1–2pp, so those
stakes are pure vig.

**The Spirit caveat, stated plainly.** Spirit's and Iron Wing's Swiss *game* records were never
published, so I assumed a 0.52 game win rate for both and the model's Spirit edge comes almost
entirely from the pre-TI prior (EWC-2025 pedigree). Against that: Spirit's two Swiss losses were
both **0–2 sweeps** (to VISION and Nigma) while Iron Wing's were competitive 1–2s, and Iron Wing
beat both Nigma and the defending champions. The market siding with Iron Wing is defensible; hence
the 0.40 haircut. If you want only one bet today, take **Nigma**.

**Note this resolves an apparent contradiction with §4.** Spirit is simultaneously *overpriced in
the winner market* (.145 vs fair .090) and *underpriced in the match market* (.47 vs fair .575).
The market implies Spirit's title chance **conditional on beating Iron Wing** is .136/.465 = 29.2%,
second only to VISION; my model says 16.2%. Buying Spirit for the match while not owning Spirit
for the title is the coherent pair, not a contradiction.

**$50 on the best stats bet across all TI markets — only one is takeable:**

| Market | Price | Model fair | EV/$ | Status |
|---|---|---|---|---|
| **Longest game: NO on "111+"** | **.86** | **0.90** | **+4.2%** | **takeable, ~90% win** |
| Radiant/Dire: Radiant | .96 | 0.92–0.955 | −2.2% | converged since Aug 14 |
| Most banned: Treant | .989 | ~0.99 | +0.1% | converged (was .63 five days ago) |
| Longest game: 91-95 | ask .68 | 0.52–0.67 | −9.8% | ask sits above fair |
| Shallowest pool: HULIGANI | ask .995 | 0.93–0.97 | −4.5% | ask above fair |

$50 → 58.1 shares, **EV +$2.12**. The two new hero-pool markets are unformed (widest-pool mids sum
to 1.40, bids to 0.17) and I lack the per-team unique-hero counts to price them — flagged, not
guessed. Structural note for later: "widest pool" mechanically favours whoever plays the most
games, which is a deep **lower-bracket** run (6 series) rather than the upper-bracket champion (4);
and **LGD at .0545 is already eliminated** and cannot add heroes, so it should be near zero.

**Combined $100: EV ≈ +$11 on the model's raw numbers, ≈ +$6 after the confidence haircuts.**
Still ~4x Kelly on these edges — same overbetting caveat as §7.

---

## 9. Conservative $100 Yandex allocation (QF day)

**What a Yandex bet actually is:** a bet on the *prior-heavy* worldview — that season pedigree
(#2 pre-TI Elo, three titles: DreamLeague S27, Wallachia S7, BLAST Slam VII) outweighs a 2–3
Swiss whose only wins came against HULIGANI (0–4) and Team Resilience. Every Yandex expression is
**+EV only under that view**:

| Bet | Ask | Fair (equal-wt) | EV/$ | Range across scenarios |
|---|---|---|---|---|
| **Yandex +1.5 games** (wins ≥1) | .72 | .703 | −3.2% | −13.7% … **+6.1%** |
| Yandex match winner | .46 | .438 | −6.4% | −28.3% … **+13.6%** |
| Yandex Game 1 winner | .47 | .458 | −4.2% | −18.7% … +9.1% |
| Yandex to win TI (outright) | .085 | .086 | −1.9% | −63.9% … +62.0% |

The **+1.5 handicap is the least-bad and by far the lowest-variance vehicle** (~70% win rate), so
it carries the core of a conservative structure.

**The allocation**

| Stake | Bet | Order | Shares |
|---|---|---|---|
| **$40** | Yandex **+1.5 games** (wins ≥1 game) | buy @ **.72** | 55.6 |
| **$20** | Yandex **match winner** | buy @ **.46** | 43.5 |
| **$25** | **NO on "111+"** (longest game) | buy @ **.86** | 29.1 |
| **$15** | cash, unstaked | — | — |

The NO-111+ leg is the only genuinely +EV bet on the board (+4.2%, ~90% win, uncorrelated with
Yandex) and it exists here to offset the vig you pay on the Yandex legs.

**Outcome distribution**

| Scenario | Prob | Net P&L |
|---|---|---|
| Yandex 2–0 or 2–1, no 111+ game | 39.4% | **+$43.10** |
| Yandex loses 1–2, no 111+ game | 23.9% | −$0.37 |
| Yandex swept 0–2, no 111+ game | 26.7% | −$55.93 |
| Yandex wins, 111+ game happens | 4.4% | +$14.03 |
| Yandex loses 1–2, 111+ game | 2.7% | −$29.44 |
| Yandex swept 0–2, 111+ game | 3.0% | −$85.00 |

**EV −$0.72 · P(ahead) 43.8% · P(flat or better) 67.7% · worst case −$85** (the $15 cash is never
at risk). By worldview: **prior-heavy +$6.96 · balanced +$0.15 · form-heavy −$9.27.**

**The design property that makes this conservative:** if Yandex wins *even one game* — 70.3% of the
time — the handicap leg carries you to roughly break-even (−$0.37). You only take a real loss on a
0–2 sweep. Compare a naive $100 straight on the match winner: 43.8% to win $117, 56.2% to lose the
lot, EV −$6.40.

**If you want more upside instead:** swap $10 of the handicap into the outright at .085 (11.8x
payoff). That raises the ceiling a lot and the variance with it — it is the opposite of this
structure's intent.

---

## 10. POSITION LOG — filled 2026-08-19 (QF day)

| Filled | Bet | Price | Shares | Pays if it hits |
|---|---|---|---|---|
| **$40** | Yandex **+1.5 games** | .72 | 55.56 | $55.56 |
| **$20** | Yandex **match winner** | .46 | 43.48 | $43.48 |
| **$5** | **NO on "111+"** | .86 | 5.81 | $5.81 |
| $35 | cash, unstaked | | | |

Deployed $65 of $100 (the NO-111+ leg came in at $5 rather than the recommended $25).

| Scenario | Prob | Net P&L |
|---|---|---|
| Yandex 2–0 or 2–1, no 111+ game | 39.4% | **+$39.85** |
| Yandex loses 1–2, no 111+ game | 23.9% | −$3.63 |
| Yandex swept 0–2, no 111+ game | 26.7% | −$59.19 |
| Yandex wins, 111+ happens | 4.4% | +$34.03 |
| Yandex loses 1–2, 111+ happens | 2.7% | −$9.44 |
| Yandex swept 0–2, 111+ happens | 3.0% | −$65.00 |

**EV −$1.65 · P(ahead) 43.8% · worst case −$65** (vs −$85 on the full-size version — the smaller
NO leg and larger cash pile cut the tail).
By worldview: **prior-heavy +$6.03 · balanced −$0.78 · form-heavy −$10.20.**

**Effect of under-sizing the NO-111+ leg.** It was the only +EV component, so trimming it $25→$5
moved portfolio EV from −$0.72 to −$1.65 and, more importantly, weakened the cushion: the
"Yandex loses 1–2" outcome went from −$0.37 (a scratch) to −$3.63. The structure still works —
a competitive 1–2 defeat costs under $4 — but the break-even property is thinner.

**Optional top-up:** adding $20 to NO-111+ at .86 (23.3 shares) is +$0.85 EV on its own and
restores the cushion, since it pays in ~90% of states. Purely optional; the $35 cash is also a
perfectly good place to leave it.

**Live prices at fill time** (Liquid–Yandex, unchanged from the analysis): Match Winner
Liquid .545 / Yandex .455 · Game 1 .535/.465 · Handicap Liquid −1.5 .285 / Yandex +1.5 .715 ·
O/U 2.5 games .495/.505. Quarterfinals begin Aug 20 02:00 UTC.

---

## 11. RESULT + EVALUATION (2026-08-20 13:06 UTC)

### The bet won — Yandex beat Liquid 2–0

| Leg | Stake | Price | Shares | Result | Return |
|---|---|---|---|---|---|
| Yandex +1.5 games | $40 | .72 | 55.56 | ✅ won | **$55.56** |
| Yandex match winner | $20 | .46 | 43.48 | ✅ won | **$43.48** |
| NO on "111+" | $5 | .86 | 5.81 | pending | — |

**$60 staked → $99.04 returned = +$39.04 (+65%).** The 2–0 sweep was the best branch: it hit the
39.4% cell of the outcome table (+$39.85 projected vs +$39.04 actual, the difference being the
unresolved NO-111+ leg).

**Process note, not a victory lap:** the model rated this bet at **−1.65 EV** on the equal-weight
view and only +$6.03 under prior-heavy. It won because the prior-heavy thesis — Yandex's season
pedigree over a weak Swiss — was the correct read, which is exactly what a 2–0 over a 4–1 Swiss
team demonstrates. One result does not validate a −EV entry; it validates *the worldview*, and the
model has now been updated for it (Yandex 1514 → 1535).

### Quarterfinal scoreboard vs the model

| Match | Model favourite | Result | Model call |
|---|---|---|---|
| Iron Wing vs Spirit | **Spirit .575** (market had IW) | **Spirit won** | ✅ the flagged low-confidence edge landed |
| VISION vs BoomBoys | VISION .723 | VISION won 2–0 | ✅ |
| Liquid vs Yandex | Liquid .554 | **Yandex won 2–0** | ❌ model favoured Liquid |
| Nigma vs Falcons | Falcons .615 | **still pending** | — |

### Yandex's next step: UB semifinal vs the Nigma/Falcons winner

That QF has not been played yet, so the opponent is undetermined (market: Falcons 63.5%).

| Opponent | Yandex wins UB semi | Yandex champion | Yandex reaches GF |
|---|---|---|---|
| Falcons (63.5% likely) | **50.3%** | 15.3% | 40.5% |
| Nigma (36.5%) | **61.8%** | 17.3% | 47.0% |
| **Blended** | **~54%** | **16.0%** | **42.9%** |

### Post-QF board (updated ratings: VISION 1634, Yandex 1535, Falcons 1534, Spirit 1527)

| Team | Model champ% | Reach GF% | Market% | Edge |
|---|---|---|---|---|
| TEAM VISION | 53.0 | 73.6 | 39.0 | **+14.0** |
| **Team Yandex** | **16.0** | **42.9** | **12.8** | **+3.3** |
| Team Spirit | 12.3 | 29.6 | 15.5 | −3.2 |
| Team Falcons | 10.4 | 28.2 | 11.5 | −1.1 |
| Nigma / Liquid / BoomBoys / 1w | 3.0 / 2.4 / 1.7 / 1.1 | | 4.9 / 4.5 / 4.0 / 2.5 | all negative |

**On the VISION +14pp:** the market barely moved VISION (.393 → .390) despite it clearing a 73.5%
quarterfinal. Conditional on advancing it "should" be near .535. Either the book is slow or it is
pricing a hard remaining path (Spirit in the UB semi). Treat with caution — this is where my model
is most aggressive — and note the **8¢ spread (.35/.43)** eats a third of the edge at the ask.

### Sizing on a $32 bank

Kelly on the Yandex outright (model 16.0% vs .135 ask) is ~2.9% of bank = **$0.92**; quarter-Kelly
is $0.23. Any stake you actually feel is already a multiple of that.

**Best execution advice: wait for the UB-semifinal match market.** Per-match books ran **~1% vig
with 1¢ spreads** versus **~5.6% at the outright ask** — five times cheaper to express the same
view, and it will list before the semifinal. If you want exposure now, Yandex outright at **.135**
is +15.9% EV/$ on the model; **$5–8 of the $32** is a defensible size, leaving the rest for the
cheaper match market.

---

## 12. UB SEMIFINAL STATS REFRESH (2026-08-20 13:13 UTC)

**Bracket state:** Spirit, VISION, Yandex through to the UB semis. **Nigma vs Falcons is still
unplayed** (Falcons .645), so Yandex's semifinal opponent remains undetermined.

### The new market: Team Spirit vs TEAM VISION (UB semi, Bo3, Aug 21)
Freshly listed, only **$944 volume** — VISION **.65 bid / .68 ask**, Spirit .32/.35.

| Scenario | Rating gap | VISION per game | VISION Bo3 | EV/$ @ .68 |
|---|---|---|---|---|
| prior-heavy | 74 | .605 | .655 | −4.6% |
| balanced | 107 | .649 | .717 | **+4.5%** |
| form-heavy | 151 | .705 | .790 | **+15.2%** |
| **equal-weight** | | | **.721** | **+5.0%** |

**VISION at .68 is a modest buy** — positive in two of three worldviews, +5.0% blended. **Spirit at
.35 is a clear avoid at −22.1%.** Caveat: the book is one day old with $944 traded and a 3¢ spread,
so treat the quote as soft.

### Full remaining-tournament projection

| Team | prior | balanced | form | **model** | market | edge |
|---|---|---|---|---|---|---|
| TEAM VISION | 41.4 | 52.5 | 65.3 | **53.1** | 41.0 | **+12.1** |
| Team Yandex | 24.1 | 15.8 | 7.7 | **15.9** | 13.2 | **+2.7** |
| Team Spirit | 14.9 | 12.6 | 8.9 | 12.1 | 15.5 | −3.4 |
| Team Falcons | 11.8 | 10.8 | 8.7 | 10.5 | 11.5 | −1.0 |
| Nigma Galaxy | 1.8 | 2.9 | 4.7 | 3.2 | 4.9 | −1.7 |
| Team Liquid | 2.1 | 2.5 | 3.0 | 2.5 | 7.0 | **−4.5** |
| BoomBoys | 2.5 | 1.8 | 0.9 | 1.7 | 4.2 | −2.4 |
| 1w Team | 1.3 | 1.1 | 0.9 | 1.1 | 2.5 | −1.5 |

**The VISION gap persists and is now the story of this book.** The outright has barely moved
(.393 → .390 → .410) across two rounds in which VISION cleared a 73.5% quarterfinal, while the
model — positive in *all three* scenarios now (41.4 / 52.5 / 65.3) — says 53.1%. Two readings:
either the outright is genuinely slow to reprice survivors, or it is discounting a hard remaining
path. Note the outright's **4¢ spread (.39/.43)** eats a third of the edge, whereas the match
market prices the same view at ~3¢ on a 68¢ contract.

**Yandex (+2.7pp) remains mildly cheap** and is the one holding that is *up* on both the model and
the market since the QF (model 8.4% → 15.9%; market 8.2¢ → 13.2¢).

**Liquid at 7.0¢ is the clearest sell** (model 2.5%): it lost its QF and now needs a five-series
lower-bracket run, which the market appears not to have fully discounted.

### Where the value sits now, ranked
1. **VISION UB-semi @ .68** — +5.0% EV, cleanest execution (match books ≈1% vig vs 5.6% outright).
2. **VISION outright @ .43** — bigger nominal edge (+12.1pp) but a 4¢ spread and the model's most
   aggressive corner; size smaller than the headline suggests.
3. **Yandex outright @ .144** — +2.7pp, consistent with the position already held.
4. Avoid: Spirit .35 (semi), Liquid .09, BoomBoys .05, 1w .031 — all negative in every scenario.

---

## 13. EXECUTION TABLE — $34 Yandex plan (built 2026-08-20 15:33 UTC)

Live at build time: **Yandex .113 bid / .145 ask** (mid .129) · Falcons .12/.14 · Nigma .03/.042
(their QF is still swinging — Nigma bounced .017 → .036) · VISION .40/.43.

Model fair values: **Yandex unconditional .149** · **if it wins the semi .252** · **if it loses .046**.
The semi vs Falcons is a coin flip (1535 vs 1534, P(win) 50.2%).

| # | Date / trigger | Link | Bet & direction | Acceptable price | Size |
|---|---|---|---|---|---|
| **1** | **NOW** (before the semi) | [TI 2026 Winner](https://polymarket.com/event/the-international-2026-winner-20260629212545745) | **BUY Team Yandex** — resting **maker bid**, do not cross | **≤ .130** (fair .149). Never pay the .145 ask | **$12** (~92 sh @ .13) |
| **2** | When the **Yandex vs Falcons semi market lists** (after their QF resolves; slug will look like `dota2-ty-flc-2026-08-2x`) | search "dota2" on Polymarket, or [event list](https://polymarket.com/markets/esports) | **BUY Yandex — Match Winner**. Better execution than the outright: match books run ~1% vig vs the outright's 3¢ spread | **≤ .52** (coin-flip fair .50; anything ≤ .52 is fine) | Use this **instead of** row 1 if it lists before you fill — same $12, not additional |
| **3** | **Yandex LOSES the semi** → drops to lower bracket | [TI 2026 Winner](https://polymarket.com/event/the-international-2026-winner-20260629212545745) | **BUY Team Yandex** (the dip) | **≤ .040 only** (fair .046). **If it holds ≥ .050, do not buy** | **$22** (550 sh @ .04) |
| **4** | **Yandex WINS the semi** → into the UB final | [TI 2026 Winner](https://polymarket.com/event/the-international-2026-winner-20260629212545745) | **BUY Team Yandex** — only on a *non*-overshoot | **≤ .235** (fair .252). If it gaps to **.28+, sit out** and consider trimming row 1 into the spike | **$10** max, keep $12 dry |
| **5** | **Any time** | [TI 2026 Winner](https://polymarket.com/event/the-international-2026-winner-20260629212545745) | **DO NOT BUY** Spirit, Liquid, BoomBoys, 1w | — | $0 — negative in every scenario |
| **6** | **Hold** — no action | [Longest Single Game](https://polymarket.com/event/the-international-2026-longest-single-game-duration-20260617185055630) | Existing **NO on "111+"** (5.81 sh @ .86) — let it settle | Book is unformed (bid .01 / ask .69); marks are meaningless. **Do not trade it** | hold |

**Rules that bind all rows:** maker orders only where possible; never place an order while a series
is live; and rows 3 and 4 are **mutually exclusive** — exactly one fires. Total at risk before the
semi result is **$12 of $34**.

**Why row 1 is capped at .130:** at the .145 ask the model's edge is ~0.4pp — inside the noise.
At .130 it is +15%; at the .113 bid it is +32%. The whole edge here is in *not crossing the spread*.

---

## 14. UPDATE 2026-08-20 16:27 UTC — Yandex becomes +EV at the ask

**The Nigma–Falcons QF is live at 1–1 with game 3 deciding** ($6.8M traded; Falcons .605 / Nigma
.395). Yandex's semifinal opponent is therefore still unresolved, and the outright has not priced
that optionality:

| Yandex's semi opponent | P | Yandex champion (model) |
|---|---|---|
| Falcons (live .605) | 60.5% | **15.1%** |
| Nigma (live .395) | 39.5% | **17.3%** |
| **Blended fair** | | **.160** |

Market: **.112 bid / .144 ask.**

| Entry | EV/$ |
|---|---|
| at the .144 **ask** | **+8.5%** |
| at a .130 maker bid | +23.0% |
| at the .112 bid | +42.8% |

**The key property: .144 sits below the fair value of *both* branches** (.151 if Falcons advances,
.173 if Nigma does). So buying now is +EV regardless of how game 3 ends — a rare robust entry, and
the reason to act before the QF resolves rather than after. Once Falcons advances (the likelier
branch) the edge compresses from +8.5% to about +5%.

**Revised row 1:** buy Yandex at **≤ .148** (was ≤ .130). Crossing the .144 ask is now justified;
a resting bid at .130 is still better if it fills. Rows 2–6 of the table in §13 are unchanged.

**Rest of the board at the ask** (blended model): VISION 52.9% vs .430 = **+21.4%** (still the
model's most aggressive corner — treat with the caution noted in §12); everything else is deeply
negative: Spirit −28.8%, Falcons −24.7%, Nigma −49.2%, Liquid −68.4%, BoomBoys −68.1%, 1w −72.9%.

*Sizing reminder: Kelly on this edge is ~$0.64 of a $34 bank. The $12 in row 1 is a deliberate
overbet, as every stake in this log has been.*
