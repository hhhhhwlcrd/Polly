# mvp2 Research Synthesis & Design Blueprint

*Deep-research output across 6 foundational angles + 3 implementation angles, compiled
2026-06-23. Companion to `HOW_POLYMARKET_COPYTRADING_IS_IMPLEMENTED.md` (the implementation
detail) and `mvp1/reports/DEEP_RESEARCH_PROMPT_v2.md` (the brief).*

> **Sourcing caveat carried from the research:** the session's egress proxy returned HTTP 403
> on direct PDF fetches for most scholarly hosts, so academic claims were verified via search
> indexing and cross-checked across ≥2 independent sources. Canonical URLs are given; byte-check
> primary PDFs before quoting verbatim.

---

## Diagnosis: how much of mvp1 was real?

| mvp1 result | Verdict after research | Why |
|---|---|---|
| Copy-all +38.7% train → **−0.1% test** | **Real (the honest number).** | Survivorship + price already incorporates the move; matches social-trading null results. |
| Top-10 hottest wallets **−96%** | **Real & expected.** | Winner's curse / regression to the mean; ranking by raw extreme ROI selects luck. Shrinkage would fix the *selection*, not make it profitable. |
| Consensus ≥5 **+64% / 96% win** | **Largely an artifact; treat as unproven.** | Priced at the leader's fill with flat 2% slippage and **zero latency**; you act *after* the Nth trader. Independent live consensus bot got **−2.47% ROI**. Kyle/HFT theory + 13F evidence say fast informed-flow alpha decays before it's copyable. |

**Bottom line:** mvp2's job is to find out whether *any* version of the consensus signal
survives **realistic fills, latency, and fees** — and to size it so that a thin edge isn't
destroyed by variance.

---

## A. Realistic information flow & evaluation

- **Late copiers capture little of fast informed flow.** Kyle (1985): private information is
  bled into price continuously, fully impounded by close; a copier seeing executed flow is
  structurally behind. NYSE information share ~92.7% concentrated in the lead venue (Hasbrouck
  1995); HFTs trade *with* the permanent component, capturing it first (Brogaard-Hendershott-
  Riordan 2014). 13F-copying alpha collapses for high-turnover flow but can survive for
  slow/fundamental positions (Di Mascio "Alpha Decay"; Quantpedia alpha-cloning).
  → **mvp2 hypothesis:** copy edge, if any, lives in *slower* markets (longer time-to-resolve),
  not minutes-to-resolution sports/crypto.
  Sources: https://people.duke.edu/~qc2/BA532/1985%20EMA%20Kyle.pdf ·
  https://onlinelibrary.wiley.com/doi/abs/10.1111/j.1540-6261.1995.tb04054.x ·
  https://papers.ssrn.com/sol3/papers.cfm?abstract_id=1928510
- **Signals decay when crowded** ~58% post-publication (McLean & Pontiff 2016, *JF*).
  Public leaderboard wallets are, by definition, crowded.
  https://onlinelibrary.wiley.com/doi/abs/10.1111/jofi.12365
- **Social-trading followers don't beat costs.** Dorfleitner et al. 2018 (*QREF*): no strategy
  earns positive risk-adjusted returns after transaction costs; copy mechanisms *increase*
  risk-taking (Apesteguia et al. 2020, *Management Science*). Sports tipster followers lose
  (−9% to −27%); closing-line value works precisely because value is pre-crowd.
  https://papers.ssrn.com/sol3/papers.cfm?abstract_id=3108422 ·
  https://pubsonline.informs.org/doi/10.1287/mnsc.2019.3508
- **Evaluation must be walk-forward + point-in-time, not a single split.**
  - Walk-forward / rolling-origin: each test point forecast only from prior data (Hyndman
    *FPP3* §5.10; sklearn `TimeSeriesSplit` with `gap`).
    https://otexts.com/fpp3/tscv.html
  - **Purged + embargoed CV** to kill leakage from overlapping outcome windows; **CPCV** for a
    *distribution* of OOS performance (López de Prado, *AFML* 2018).
    https://en.wikipedia.org/wiki/Purged_cross-validation
  - **Deflated Sharpe Ratio** and **PBO/CSCV** to correct for multiple-testing / # of strategy
    trials; **MinBTL** (≈ with 5y data, trying >45 configs almost guarantees a spurious Sharpe=1).
    https://papers.ssrn.com/sol3/papers.cfm?abstract_id=2460551 ·
    https://www.ams.org/notices/201405/rnoti-p458.pdf
  - **Survivorship is quantifiable**: it inflated fund returns ~1.4%/yr (Elton-Gruber-Blake) and
    manufactures spurious persistence (Brown et al. 1992). Select followers point-in-time only.
- **Follower selection must shrink toward the mean.** James-Stein / empirical-Bayes
  (beta-binomial) shrinkage of win rates pulls small-sample leaders hard toward the population —
  the direct antidote to mvp1's "top-10 hottest wallets → −96%" winner's curse.
  http://varianceexplained.org/r/beta_binomial_baseball/ · https://en.wikipedia.org/wiki/Winner's_curse

## B. Bankroll management (the missing half of mvp1)

- **Binary-contract Kelly:** for price `c`, estimated win-prob `p`: **`f* = (p − c)/(1 − c)`**,
  bet only when `p > c`. https://en.wikipedia.org/wiki/Kelly_criterion ·
  https://arxiv.org/abs/2412.14144
- **Use fractional Kelly (¼–½).** Half-Kelly keeps ~75% of growth while ~halving volatility;
  overbetting past ~2× Kelly drives growth negative. Estimation error makes overbetting the
  dominant risk → bet *below* full Kelly. https://www.stat.berkeley.edu/~aldous/157/Papers/Good_Bad_Kelly.pdf
- **Drawdown law:** under fraction `f` of full Kelly, P(ever fall to fraction `a`) ≈ `a^(1/f)`.
  Full Kelly → 50% chance of ever halving; half-Kelly → ~25%; quarter-Kelly → ~6%.
- **Correlated/simultaneous bets:** the multivariate optimum is **`f* = C⁻¹(μ − r)`** (≡
  Markowitz tangency). **Naive per-bet Kelly over-bets** when bets share an event; positive
  correlation shrinks each stake, two perfectly-correlated bets ≈ one bet. Even *independent*
  simultaneous bets need joint sizing (≈ 1/√n of standalone Kelly each). This is *the* fix for
  copying many wallets into the same market. Whitrow 2007 (*JRSS-C*);
  https://doi.org/10.1111/j.1467-9876.2007.00581.x
- **Calibration feeds Kelly.** Grade the win-prob with **Brier score** + reliability diagram;
  overestimated `p` ⇒ overbet ⇒ negative growth. So mvp2 must *calibrate* "≥N traders agree" into
  an empirical win-probability, not assume it. https://doi.org/10.1175/1520-0493(1950)078%3C0001:VOFEIT%3E2.0.CO;2
- **Hard caps regardless of Kelly:** ~1–2% unit, ≤2–3% per position, ~5–7% aggregate exposure;
  volatility targeting / leverage caps as quant analogues.

## C. Metrics mvp2 must report (daily / monthly / yearly ROI + risk)

- **Compound, don't average.** Per-bet arithmetic ROI overstates bankroll growth by the
  volatility drag `R_geo ≈ R_arith − σ²/2`. Report **geometric** growth on a compounding
  bankroll. https://www.kitces.com/blog/volatility-drag-variance-drain-mean-arithmetic-vs-geometric-average-investment-returns/
- **Return:** CAGR = (End/Start)^(1/years) − 1; daily→annual `(1+r)^252−1`, monthly `(1+r)^12−1`;
  report **time-weighted** daily/monthly/yearly. Keep **yield = profit/total-staked** separately
  from **ROI = profit/bankroll**.
- **Risk-adjusted:** Sharpe (annualize ×√N, but √N invalid under autocorrelation — Lo 2002),
  Sortino (downside deviation vs MAR), Calmar = CAGR/|MaxDD|.
- **Drawdown:** max drawdown from the equity high-water mark, time-under-water, Ulcer Index.
- **Trade-level:** win rate, profit factor, expectancy, turnover, avg holding period, exposure.
- **Capacity:** edge decays as size grows vs book depth; square-root impact law
  `I(Q) ≈ Y·σ·√(Q/V)`; cap orders to a fraction of available depth.

---

## mvp2 design blueprint (build-from-scratch in `mvp2/`)

**Data plan.** Reuse mvp1's collectors, add: per-market **`/book`** snapshots (for walk-the-book
fills) and **`/prices-history`** (for price *at* and *after* each leader trade); record
per-market **tick size, min size, neg-risk flag, category fee**. Detect via `/activity` polling
first (`maker`-attributed `OrderFilled` `eth_subscribe` as a later latency upgrade).

**Latency-aware point-in-time fill model (the core fix).** For each leader BUY at time `t`,
price the copier's fill at `t+Δ` (Δ ≈ 5–30s) by **walking the order book as it stood at `t+Δ`**,
then subtract the **category taker fee**. ROI per bet = settlement − that realistic cost. Sweep Δ.

**Evaluation protocol.** Walk-forward with **purged + embargoed** folds (embargo ≥ max
time-to-resolution); select **followers point-in-time** with **empirical-Bayes shrunk** win
rates; tune all hyperparameters under **CPCV** and report **Deflated Sharpe / PBO**, respecting
**MinBTL** (cap the number of configs tried).

**Bankroll module.** Calibrate the consensus signal → win-prob `p` (Brier-scored); size with
**fractional (¼–½) Kelly `f*=(p−c)/(1−c)`**, **joint across simultaneous correlated bets**
(`C⁻¹`, with per-event exposure caps), hard caps (≤2–3% position, ≤5–7% aggregate); simulate a
**compounding bankroll** and report CAGR + daily/monthly/yearly TWR, Sharpe/Sortino/Calmar, max
drawdown/time-under-water, plus a **capacity** estimate from book depth.

**Prioritized testable hypotheses (each with a success criterion):**
1. **H1 — Realistic fills kill most of the consensus edge.** After latency-Δ walk-the-book fills
   + taker fees, OOS consensus ROI drops from +64% toward the live-bot −2.5%. *Success:* quantify
   the surviving edge with a confidence interval; pass only if Deflated-Sharpe-significant.
2. **H2 — Edge concentrates in slow markets.** Consensus net edge is higher for long
   time-to-resolution markets than for <24h sports/crypto. *Success:* monotone edge-vs-horizon.
3. **H3 — Shrinkage beats raw ranking.** Empirical-Bayes follower selection OOS-dominates
   top-K-by-raw-ROI (which lost 96%). *Success:* higher OOS CAGR, lower drawdown.
4. **H4 — Fractional-Kelly + correlation-aware sizing improves risk-adjusted return** vs
   $1/bet and vs naive per-bet Kelly. *Success:* higher Calmar, `a^(1/f)`-consistent drawdowns.
5. **H5 — Capacity is small.** Net edge decays to ≤0 beyond some bankroll relative to book depth.
   *Success:* an explicit capacity-vs-ROI curve.

**Risks/unknowns:** no published WS/RPC latency SLA (measure live); v2 ABI/fee specifics must be
pulled at runtime; `/prices-history` is known to return empty for resolved markets (may need
on-chain reconstruction); leaderboard caps at 50/window (cohort = union, as in mvp1).
