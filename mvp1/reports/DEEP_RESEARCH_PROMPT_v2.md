# Deep Research Prompt — Designing a Better Copy-Trading System (Polly v2)

> Paste this into a deep-research harness. It is self-contained: it carries the
> v1 method and results, the two failure modes to fix, and the exact deliverable
> expected. The objective is **not a literature survey for its own sake** — it is
> a concrete, evidence-backed redesign that produces **better, more honest v2
> results** than v1.

---

## Role
You are a quantitative researcher specializing in prediction markets, market
microstructure, and bankroll/risk management. Research rigorously, cite primary
sources (academic papers, exchange/API docs, reputable practitioner write-ups),
and distinguish **established results** from **speculation**. Every recommendation
must be implementable against Polymarket's public APIs and end in a concrete v2
design.

## Background — what v1 did
"Polly v1" tested whether copying Polymarket's top performers is profitable.

- **Cohort:** top ~100 performers from the public leaderboard (union across
  profit/volume windows). Median all-time profit ≈ $4.3M.
- **Data:** 94k trades (price, size, side, timestamp) via `data-api/activity`;
  market settlement via `clob/markets`. 67,067 "copyable bets" = BUYs on markets
  that resolved.
- **Copy model:** buy the same outcome token, **hold to resolution**, fill at the
  trader's execution price **+ flat 2% slippage**. Per-bet
  `ROI = payout/(price·(1+slippage)) − 1`, payout ∈ {0,1}.
- **Validation:** chronological train/val/test (60/20/20) by trade time; params
  fit on train, tuned on val, scored on held-out test.
- **Sizing:** essentially **$1 per bet** (equal weight), plus one stake-weighted
  variant.

### v1 key results (held-out test, after 2% slippage)
| Strategy | Train ROI | **Test ROI** | Test win-rate | Test bets |
|---|---:|---:|---:|---:|
| Copy-all (naive) | +38.7% | **−0.1%** | 51% | 13,414 |
| Top-10 hottest wallets | +132% | **−96%** | 2% | 47 |
| **Consensus ≥5 traders** | +92% | **+64%** | **96%** | 730 |

**v1 takeaways:** naive copying is break-even out-of-sample (survivorship +
already-priced-in); chasing the highest-ROI wallets overfits catastrophically;
only **multi-trader consensus** generalized.

---

## The two failure modes v2 must fix

### A. The data/information-flow environment is not realistic
v1's backtest gives the copier information and prices it could never actually
obtain in real time. Specifically:

1. **Look-ahead / point-in-time correctness.** The copier "knew" the trader's
   exact fill price and that the market resolved. A live bot only knows trades up
   to *now*, observes them with latency, and must decide *before* resolution.
2. **Latency & price impact.** A sharp trader's BUY moves the price; by the time a
   bot detects it (on-chain confirmation + API polling delay) and submits an
   order, the available price is worse. The **consensus** result is the most
   exposed: you only act *after* the 5th trader, i.e. you are systematically late
   and buying into a move.
3. **Flat 2% slippage is a fiction.** Real fill cost depends on order-book depth,
   size, market liquidity, and tick size — and differs across favorites vs
   long-shots and liquid vs thin markets.
4. **Survivorship/selection bias in the cohort.** Followers were chosen because
   they had already won. A live bot must select whom to follow using **only past
   information**, point-in-time.
5. **Exit modeling.** v1 ignored that traders SELL/exit before resolution; "hold
   to resolution" may misstate both the signal and the achievable return.

### B. There is no bankroll / money management
v1 sized every bet at $1 (or proportional to a whale's stake, which produced a
meaningless capital-weighted number). It has **no capital dynamics**:

1. No position sizing by **edge/confidence** (Kelly / fractional Kelly).
2. No **compounding** or path-dependent equity; ROI-per-bet hides drawdown and
   ruin risk.
3. No handling of **bet correlation** — many copied bets on the same market/event
   are not independent; naive diversification math is wrong.
4. No **exposure limits, liquidity caps, drawdown stops, or bankroll constraints**.

---

## Research objectives & questions

### Objective 1 — A point-in-time, latency-aware simulation environment
Research and recommend, with sources:
- **Event-time backtesting** best practices to eliminate look-ahead in
  copy/signal-following systems; how to construct strictly point-in-time features
  and a walk-forward (rolling/expanding) evaluation that beats a single 60/20/20
  split. What pitfalls cause inflated backtests in copy-trading specifically?
- **Polymarket data for realistic fills:** what does the CLOB API expose
  (order-book depth/`/book`, price history/`/prices-history`, trades, tick size,
  fees, neg-risk markets)? How can we reconstruct the **price actually available
  to a copier at trade-time + a latency Δ**, instead of the trader's fill?
- **Latency budget:** realistic detection latency for a copy bot (on-chain
  confirmation on Polygon, indexer/API polling, order placement). How much does
  price typically move in the seconds/minutes after a sharp trade (information
  content of informed order flow)? Cite microstructure / informed-trading
  literature (e.g., price impact, PIN, Kyle's lambda) and any Polymarket/crypto
  prediction-market empirical studies.
- **Modeling slippage properly:** size-dependent slippage from order-book walking
  vs a flat haircut; how to cap copy size to a fraction of available depth.
- **Point-in-time follower selection:** how to rank/choose whom to copy using only
  trailing data (rolling skill estimates, shrinkage/regularization to avoid the
  v1 "hottest-wallet" overfit), and how to detect *persistent* skill vs luck
  (variance of long-shot bettors). Reference work on performance persistence,
  hot-hand vs regression-to-mean, and shrinkage estimators (e.g., empirical Bayes).

### Objective 2 — Bankroll & risk management for binary prediction markets
Research and recommend, with sources:
- **Kelly criterion for binary contracts** priced in [0,1]: exact formula given an
  edge estimate, and why **fractional Kelly** (½, ¼) is standard in practice given
  parameter uncertainty. How to translate a noisy estimated win-probability into a
  bet fraction without over-betting.
- **Estimating the edge to feed Kelly:** calibrating the consensus signal into a
  probability (e.g., does "≥N traders agree" map to a calibrated win-prob?), and
  calibration metrics (Brier score, reliability curves).
- **Correlated bets:** sizing when many simultaneous bets share a common event;
  approaches like simultaneous/ "Kelly for correlated bets," exposure budgeting,
  and per-event caps. Why treating correlated bets as independent overstates
  diversification and growth.
- **Risk controls:** drawdown limits, risk-of-ruin, volatility/exposure targeting,
  bankroll fraction caps, and liquidity-aware max stake. What metrics should v2
  report beyond ROI — **CAGR on a compounding bankroll, max drawdown, Sharpe/Sortino,
  risk-of-ruin, turnover, and capacity**?
- **Capacity analysis:** given order-book depth, how much capital can the
  consensus strategy actually absorb before its edge decays?

---

## Source priorities
- Academic: prediction-market efficiency & informed trading; favorite–longshot
  bias; Kelly/growth-optimal betting and fractional Kelly; correlated-bet sizing;
  performance persistence / skill-vs-luck; backtest overfitting (e.g., deflated
  Sharpe, walk-forward).
- Polymarket/CLOB official API docs (order book, price history, fees, neg-risk,
  proxy-wallet settlement) and Polygon confirmation characteristics.
- Reputable practitioner sources on crypto/prediction-market copy-trading,
  latency, and MEV/front-running risk on copied flow.
- Treat forums/blogs as leads to verify, not as authority.

## Required deliverable (the point of the research)
Produce a **v2 design blueprint**, not just a literature review:

1. **Diagnosis** — for each v1 result above, state how much of it is likely an
   artifact of unrealistic information flow vs a real edge, with cited reasoning.
   Pay special attention to whether the +64% consensus result survives latency and
   price-impact.
2. **v2 data plan** — exact Polymarket endpoints/fields to add (order book, price
   history, fees), and how to build a **point-in-time, latency-Δ fill model**.
3. **v2 evaluation protocol** — walk-forward scheme, point-in-time follower
   selection, leakage checklist, and the realistic-fill methodology.
4. **v2 bankroll module** — concrete sizing rule (e.g., fractional-Kelly on a
   calibrated consensus probability with per-event exposure caps), risk controls,
   and the full metrics set to report.
5. **Concrete experiments for v2** — a prioritized list of testable hypotheses
   (e.g., "consensus edge net of size-dependent slippage and 30s latency remains
   > X%"), each with the data, method, and success criterion.
6. **Risks & unknowns** — what cannot be resolved from public data and how to
   bound it.

Every claim cited; every recommendation actionable against the existing
`src/collect_data.py` / `src/backtest.py` codebase. Optimize the whole thing for
one outcome: **v2 produces more realistic and more profitable results than v1.**
