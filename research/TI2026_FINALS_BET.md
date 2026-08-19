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
