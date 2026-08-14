# TI 2026 — Live Market Analysis & Game-Stats Framework

*Snapshot 2026-08-14 ~09:15 UTC. The International 2026 (TI15) is **in progress**: Shanghai,
Swiss Bo3 group stage Aug 13–16, Main Event Aug 20–23, $2,919,406 prize pool, patch **7.41e**
(released Jul 30, two weeks pre-event). Supersedes `TI2026_UNDERVALUED.md` for all pricing.
Analysis pipeline: `ti2026/` (see §6).*

---

## 0. What changed since the July scan

| | July 7 (pre-tournament) | August 14 (live) |
|---|---|---|
| Winner-market volume | **$4,237** (a shell) | **$1,048,766** ($125k/24h) |
| Sum of mids | 1.93 (unpriceable) | **1.089** (tradeable book) |
| Spreads | 8–38¢ | 1–7¢ on the top names |
| Derivative markets | none | **three live** (Radiant/Dire, longest game, most-banned hero) |

The July call was **TEAM VISION at 12¢** as the top maker bid. VISION now trades **31.5¢** and
leads the Swiss at 3–0 — that ladder rung is +162% if it filled. The others: Yandex .14→.165
(+18%), Falcons .10→.11 (+10%), Aurora .07→**.0195 (−72%)**. Net across the four-rung ladder,
VISION carried the sleeve. Logged plainly: Aurora was a losing rung.

---

## 1. Current winner market (Aug 14, 09:15 UTC)

| Team | Mid | Bid/Ask | Swiss | Note |
|---|---|---|---|---|
| **TEAM VISION** (PARIVISION) | **.315** | .31/.32 | **3–0** (8–2) | EWC 2026 champions; beat Falcons & BoomBoys |
| Team Spirit | .185 | .15/.22 | 2–0 (4–0) | wide 7¢ spread |
| Team Yandex | .165 | .15/.18 | 1–1 | |
| BoomBoys (BetBoom) | .135 | .13/.14 | 2–1 | EWC runner-up |
| Team Falcons | .11 | .10/.12 | 1–1 | defending champions |
| Team Liquid | .09 | .06/.12 | 2–0 (4–1) | **widest spread in the book** |
| Aurora | .0195 · 1w/Iron Wing .018 · LGD .0155 · Xtreme .0105 · Resilience .0105 | | | |
| Nigma .0065 · Vici .0045 · GamerLegion .003 · HULIGANI .0005 · OG .0005 | | | 0–2: OG, Resilience, Xtreme, HULIGANI | |

Sum of mids **1.089** — an 8.9% overround, normal for a live book. **Name decoding** (Valve's
bookmaker-debranding sweep): Iron Wing = 1w/1win · BoomBoys = BetBoom · TEAM VISION = PARIVISION ·
HULIGANI = L1ga Team. All 16 Polymarket entries reconcile; there is no 17th team.

**Read:** the winner book is now *efficient enough* that it is no longer the interesting market.
VISION at 31.5¢ after 3–0 is defensible (Swiss leader, EWC champion, top-3 direct berth in sight);
Liquid at 2–0 with a .06/.12 spread is the only structural anomaly, and it is a spread artifact,
not a valuation claim. **The edge has migrated to the derivative books.**

---

## 2. The three derivative markets — where the edge now is

These resolve on *public statistics*, not on a team's fate. A match-data model competes against a
thin retail book instead of against sharps. All three are priced below with the new
`ti2026/src/derivatives.py` models.

### A. "Will Radiant or Dire have the higher win rate?" — market: Radiant .705 / Dire .305 / Neither .06

**Verdict: Dire looks cheap, but the evidence conflicts — size small or stand down.**

| Prior p (Radiant) | Source | Model P(Radiant) | P(Dire) |
|---|---|---|---|
| 0.451 | TI14 (research pass B) | 0.184 | **0.783** |
| 0.459 | EWC 2026, 157 games, same patch family | 0.219 | 0.745 |
| 0.491 | 2026 tier-1 pooled (Wallachia+DreamLeague+EWC, 338 games) | 0.403 | 0.544 |
| **0.508** | **TI14 (research pass A)** | **0.535** | 0.419 |
| 0.520 | TI13 (123 games) | 0.607 | 0.352 |
| 0.530 | ≈ market-implied breakeven | 0.710 | 0.244 |

⚠️ **The two independent research passes disagree on TI14's Radiant rate: 45.1% vs 50.83%.**
That single unresolved number swings P(Radiant) from 0.18 to 0.54. Neither could be byte-verified
(every stats host is egress-blocked). Honest band: **p ∈ [0.47, 0.53] → P(Radiant) ∈ [0.25, 0.73]**,
central ≈ 0.50 vs the market's 0.705.

Supporting the Dire side: TI's Radiant rate has fallen monotonically (TI12 ~59–61% → TI13 ~52% →
TI14 45–51%); all three 2026 tier-1 events landed 46–52%; the widely-quoted 53.5% is a **public
matchmaking** figure (40k pub games), the wrong reference class. Supporting Radiant: 7.41's map
changes (Radiant safe-lane camp, T2 tower) pushed the advantage back toward Radiant after 7.40
briefly favoured Dire, and at TI14 teams traded first pick for Radiant 67.85% of the time — the
pros behave as if Radiant is worth something.

**"Neither" (exact tie) at 6¢:** model says 3.3–5.3%. Mildly rich; not worth a trade at 6¢.

**Action:** Dire at .305 is the only position with a positive central estimate (+~20pp), but the
TI14 conflict is load-bearing and TI15's own split is unpublished. Treat as a **small,
speculative** maker bid at ≤.30, not a core position. **Resolve the conflict first** by counting
TI15's actual Radiant/Dire split from match data (notebook 07 does this) — after ~60 games the
in-tournament sample starts to dominate the prior.

### B. "Longest single game duration" — buckets 91-95 / 96-100 / 101-105 / 106-110 / 111+

**Verdict: the book is unformed (every bucket 0.01 bid / 0.97 ask, 0.49 placeholder mid) and the
high buckets are badly underpriced.**

Two facts dominate:
1. **A 94:38 game has already been played** — TEAM VISION vs Falcons, Round 2 Game 3, Aug 13
   (reported as the biggest comeback in TI history, ~34.9k gold swing). So the sub-91 outcome is
   already dead and **91-95 is the floor**, not a forecast.
2. **TI15 is running extraordinarily long.** Day 1: **8 of 29 games over 60 minutes (27.6%)**.
   My reconstruction of 21 known game durations gives mean **52.8 min**, median 48.3, 28.6% over
   60 — versus **38.4 min** average at TI13. The 7.41e meta (mega-creep gold/XP nerfs) is slow.

With ~105 games remaining, the question is only *"does any of them beat 95 minutes?"*:

| Duration model | 91-95 | 96-100 | 101-105 | 106-110 | 111+ |
|---|---|---|---|---|---|
| TI15 empirical bootstrap (n=21) | 0.251 | 0.222 | 0.223 | 0.154 | 0.150 |
| Lognormal fit to TI15 | 0.164 | 0.141 | 0.144 | 0.142 | **0.409** |
| Blend with a calmer prior | 0.308 | 0.157 | 0.153 | 0.124 | 0.258 |

**Every bucket is worth far more than 1¢, and no bucket is worth 97¢.** Even the most conservative
model puts 111+ at 15% and 96-100 at 14%. This is the cleanest edge in the three books — but it is
capturable *only* by resting bids (crossing a 0.97 ask is never right).

**Caveat, stated plainly:** the historical counter-argument is real — the last three TIs peaked at
87 / 69 / 77 minutes, and only 2 of 7 Internationals ever produced a >95-minute game. My models
lean heavily on the fat TI15 sample (21–29 games). If Day 1 was an outlier and the meta reverts,
91-95 holds and the high buckets expire worthless. That is why the spread across models above is
wide and why sizing should be small.

### C. "Most banned hero" — market: Treant Protector .63 bid / .94 ask (mid .785); ~100 heroes unpriced

**Verdict: Treant is a far bigger favourite than 63¢ — the strongest signal of the three.**

TI 2026 Day 1 pick/ban (29 games):

| Hero | Bans | Picks | Contest |
|---|---|---|---|
| **Treant Protector** | **28** | 1 (0% WR) | **29/29 = 100%** |
| Lone Druid | 13 | 5 | 62% |
| Puck | 12 | 4 | 55% |
| Shadow Fiend | 11 | 4 | 52% |

The 28+1 = 29 identity independently reproduces the reported Day-1 game count — a strong internal
consistency check. Treant was **nerfed in 7.41e and is still banned out of every game**; he was
banned 135 times at EWC 2026 (98% contest) and Noxville reported a ~24-game consecutive ban streak
in tier-1 play.

Dirichlet-multinomial forward simulation with ~105 games left:

| Prior weight | Treant | Lone Druid | Tie mass |
|---|---|---|---|
| Weak (trust TI15 data) | **0.985** | 0.010 | 0.000 |
| Strong EWC prior | **0.977** | 0.019 | 0.001 |

A 15-ban lead after 29 games, compounding at ~0.97 bans/game vs Lone Druid's ~0.45, is
essentially unassailable: projected finals are ~129 vs ~60. The generic "#1-vs-#2 margins are only
1–14 bans" base rate (true at TI12 and Wallachia S8) **does not apply** when one hero is at 100%
contest and the field is not.

**Action:** fair ≈ 0.95+; the 0.94 ask offers almost nothing, but **a resting bid anywhere from
.70 to .85 is strong value** if a seller crosses. The risk that justifies a haircut: an emergency
balance patch mid-tournament (Valve has done this) or a sudden meta solution to Treant.

---

## 3. Consolidated action table

| Market | Position | Model fair | Book | Action |
|---|---|---|---|---|
| Most banned: **Treant** | buy | **~0.95** | .63 bid / .94 ask | **Maker bid .70–.85.** Do not cross .94 |
| Longest game: **111+** | buy | 0.15–0.41 | 0.01 bid / 0.97 ask | Maker bid .10–.15 |
| Longest game: **96-100 / 101-105** | buy | ~0.14–0.22 each | 0.01 / 0.97 | Maker bid .08–.12 each |
| Radiant/Dire: **Dire** | buy | ~0.42–0.78 (central ~0.50) | .30 bid / .31 ask | Small maker bid ≤.30; resolve the TI14 conflict first |
| Radiant/Dire: **Neither** | avoid | 0.033–0.053 | .06 | mildly rich, 6¢ — skip |
| Winner market | no action | — | sum 1.089 | efficient enough; VISION 31.5¢ defensible at 3–0 |

**Cluster discipline:** all four positions resolve off the same tournament and correlate (a long,
grindy meta simultaneously drives long games, Treant's value as a defensive ban, and side balance).
Treat the entire TI book as **one cluster ≤15% of bankroll**, per `STRATEGY_SELECTION.md`.

**Execution:** maker orders only — every one of these books has a placeholder ask (0.94–0.97) that
is never worth crossing. Cancel resting bids before a team's elimination series. Re-price daily
with notebook 09 as games accumulate; the in-tournament sample overtakes the priors quickly.

---

## 4. What would change these calls

- **Radiant/Dire:** count TI15's actual split. After ~60 games the tournament sample dominates.
  If TI15 is running Radiant-heavy, the Dire bid is wrong and should be pulled.
- **Longest game:** every day without a >95-minute game raises 91-95. The Main Event (Aug 20–23,
  Bo3/Bo5 elimination) is where marathon games cluster historically.
- **Most banned:** only a balance patch or a hard meta counter to Treant matters.
- **All:** a mid-tournament patch invalidates every prior simultaneously.

---

## 5. Evidence quality — read before sizing

**Nothing in this document is byte-verified.** Every Dota data host (liquipedia, opendota, stratz,
datdota, dotabuff, spectral, dota2protracker) plus the esports press (gosugamers, dotesports,
win.gg, hotspawn, cyberscore, egamersworld) is **egress-blocked in this sandbox**. All tournament
and historical figures are search-snippet-derived across two independent research passes.

Mitigations applied: (a) two arithmetic cross-checks that would be very unlikely to survive
fabrication — Day-1 series reconstruction sums to exactly 29 games, and Treant's 28 bans + 1 pick
also sums to exactly 29; (b) explicit flagging of the one place the passes disagree (TI14
Radiant rate); (c) model outputs quoted as ranges across priors rather than point estimates.

**The fix:** run `ti2026/notebooks/01` in an environment with OpenDota access. Every number here
becomes directly computable — TI15's radiant split, the real duration distribution, exact ban
counts — and the models switch from snippet priors to measured data.

---

## 6. The analysis framework (`ti2026/`) — now with game-stats

Rebuilt this pass. New modules:

| Module | What it adds |
|---|---|
| `src/game_stats.py` | Economy timing curves (gold/xp adv at 10/15/20/25/30/40), lane strength by role, objective control (first tower, roshan, barracks pace), teamfight economics, pace & lead-conversion (close/comeback rates), radiant/dire splits, and **opponent adjustment** (residualise any metric against opponent Elo — the anti-soft-schedule guard) |
| `src/draft.py` | Ban tables, **contest rate** (picks+bans per game — the real meta measure), hero win rates, team draft signatures (pool breadth/HHI), player hero pools, and **meta-shift across a patch boundary** |
| `src/derivatives.py` | The three market models: Beta-binomial Radiant/Dire with a sensitivity grid, max-of-N longest-game with **empirical *and* GPD tail** models, Dirichlet-multinomial most-banned-hero, plus `compare_to_book()` for net-of-fee edges |
| `src/polymarket.py` | Live gamma/CLOB reader for all four TI books, with explicit "no bid = unpriced, not a mid" handling |
| `src/collect_data.py` | Now stores full **timelines, objectives and teamfights** (not just two gold snapshots), plus a `parsed` flag |

New notebooks: **06** draft & meta · **07** game-stats deep dive (style profiles, timing-curve
plots, opponent-adjusted metrics) · **08** derivative-market pricing · **09** live TI tracker
(daily refresh loop). All nine notebooks syntax-check clean.
