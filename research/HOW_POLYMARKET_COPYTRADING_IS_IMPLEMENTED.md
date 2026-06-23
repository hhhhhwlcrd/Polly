# How Polymarket Copy-Trading Is Generally Implemented

*Deep-research synthesis, compiled 2026-06-23. Every load-bearing claim carries a source.
Vendor latency/accuracy/volume figures are flagged as marketing unless tied to an
authoritative source (docs.polymarket.com, GitHub code, PolygonScan, Dune, Nansen).*

> ⚠️ **Version warning that dominates this whole topic:** Polymarket cut over to **CLOB
> v2 / new exchange contracts / pUSD collateral on April 28, 2026**, with **no backward
> compatibility**. Contract addresses, the signed-order struct, the EIP-712 domain
> (`"1"`→`"2"`), and the fee model all changed. Treat any tutorial or repo written before
> ~May 2026 as partially stale, and resolve contract addresses/ABIs at runtime.
> Sources: https://docs.polymarket.com/v2-migration ·
> https://help.polymarket.com/en/articles/14762452-polymarket-exchange-upgrade-april-28-2026

---

## TL;DR

There are **three layers** to the ecosystem:

1. **DIY open-source bots** — almost all converge on one architecture:
   *poll `data-api/activity` for a target wallet every 1–2s → place a FOK market order via
   `py-clob-client`/`clob-client` through a proxy wallet.* Sizing is mostly naive.
2. **Productized services** — a few Telegram/web bots genuinely **auto-execute**
   (PolyGun, PolyCop, Polycopy Premium); the larger half of the ecosystem is **alerts /
   analytics only** despite "copy" branding.
3. **The data substrate** everyone shares — the **public, keyless** Polymarket leaderboard
   API + on-chain Polygon data (reconstructable PnL), plus Dune/Nansen labeling.

The recurring, evidence-backed lesson: **the tracking half rests on solid public
infrastructure; the execution half rests on vendor trust and a thin, decaying edge.** The
one rigorous open-source live test (¼-Kelly + consensus + EV gate) was archived after 10
days at **9.5% win rate / −2.47% ROI — "no edge once wallets are widely tracked."**
(https://github.com/005Jan/Polymarket-smart-money-tracker)

---

## 1. The canonical DIY architecture (what the open-source bots actually do)

```
loop every 1–2s:
  GET data-api.polymarket.com/activity?user=<TARGET_PROXY>&limit=N
    → keep type=="TRADE", dedup by transactionHash, drop trades older than threshold
    → parse: asset (ERC-1155 token_id), outcome (YES/NO), side (BUY/SELL), price∈[0,1], size
    → decide size (fixed $, % of leader, or % of bankroll)
    → create_market_order(MarketOrderArgs(token_id, amount, side, order_type=FOK))
    → post_order(...)   # signed EIP-712, funder = your proxy wallet
```

- **Detection is HTTP polling of the Data API**, *not* on-chain log watching, in essentially
  every working repo. The leader's fills surface in `/activity` keyed by `proxyWallet`; bots
  dedup by `transactionHash`. Confirmed in code (e.g. `gnanam1990/tracker.py` polls every 2s,
  dedups via an LRU of tx-hash MD5s).
  https://github.com/gnanam1990/polymarket-copy-bot ·
  https://docs.polymarket.com/api-reference/core/get-user-activity
- **The CLOB market WebSocket is used for prices/order-status, not for primary trade
  attribution** — its `last_trade_price`/`book` events are **anonymous** (no trader address),
  and the `/ws/user` channel only shows *your own* orders. Useful as a fast "something
  happened" nudge, not to know *who* traded.
  https://docs.polymarket.com/developers/CLOB/websocket/wss-overview
- **On-chain log watching and subgraphs are largely absent from the open repos** despite being
  the lower-latency attribution path (see §3). One outlier uses Playwright/Selenium browser
  automation (slower). https://github.com/unitmargaretaustin/Polymarket-copy-trading-bot
- **Execution goes through the proxy wallet**: the bot signs with the controlling EOA but sets
  `funder` = the Gnosis-Safe/Magic proxy that actually holds USDC and positions, with a
  `signature_type` (0 EOA / 1 Magic-email / 2 browser-proxy). Orders are typically **FOK**
  (fill-or-kill) so you never get stranded partials.
  https://github.com/Polymarket/py-clob-client

### Open-source repos worth reading (ranked by learnability)
| Repo | Lang | Notable for |
|---|---|---|
| [gnanam1990/polymarket-copy-bot](https://github.com/gnanam1990/polymarket-copy-bot) | Python | Cleanest detection loop; ROI/price-band filters; **live trading is a stub** (paper only) |
| [defi-ape/polymarket-copy-trading-bot](https://github.com/defi-ape/polymarket-copy-trading-bot) | TS | Cleanest execution via `@polymarket/clob-client`; handles buy/sell/merge; **naive 1:1 sizing** |
| [shmlkv/polymarket-copy-trading-bot](https://github.com/shmlkv/polymarket-copy-trading-bot) | TS (~48★) | **Best sizing**: percentage / fixed / adaptive + tiered multipliers, scaled by your vs leader capital |
| [005Jan/Polymarket-smart-money-tracker](https://github.com/005Jan/Polymarket-smart-money-tracker) | Python | **Best methodology + honest negative result** (see TL;DR). ¼-Kelly, ≥2-wallet consensus, TP/SL, >15%-move EV gate |
| [Drakkar-Software/OctoBot-Prediction-Market](https://github.com/Drakkar-Software/OctoBot-Prediction-Market) | Python (~93★) | Only one backed by an established project; copy-trade is **WIP** |

### Position sizing in practice (mostly naive)
- **Fixed $ per trade** — most common (e.g. $10). 
- **1:1 raw mirror + balance check** — the naivest, common in TS forks.
- **Proportional to leader size / % of leader balance** — shmlkv, kebbozzo.
- **¼-Kelly with consensus + EV gating** — only `005Jan`. Everything else ignores edge/variance.

### Pitfalls the authors themselves call out
- **Being too late / price already moved** — "100ms vs 5s often decides whether you get the
  same price"; only `005Jan` guards it (rejects entries >15% past the leader's price) — and that
  guard is *why* it found negative ROI: public wallets make you exit liquidity.
- **Partial fills** → use FOK. **Slippage** → cents-cap + liquidity filter. **Rate limits** →
  Data API general bucket ~1,000/10s. **Near-resolution markets** → filter by time-to-resolve.
- **Infra latency**: the CLOB runs in AWS **eu-west-2 (London)** — EU colocation cuts RTT.
  https://www.quicknode.com/guides/defi/polymarket-copy-trading-bot

### ⚠️ Supply-chain danger (confirmed, active)
The niche is full of **keyword-stuffed sales-funnel repos** (real code "DM on Telegram",
inflated stars/forks) and at least one **actively malicious family**: the verified
`dev-protocol` GitHub org was hijacked to host `polymarket-copytrading-bot-sport` (+20 variants)
whose typosquatted npm deps **steal wallet private keys and open an SSH backdoor**. Audit
`package.json`/deps before installing anything; star counts are not signal.
https://www.stepsecurity.io/blog/malicious-polymarket-bot-hides-in-hijacked-dev-protocol-github-org-and-steals-wallet-keys

---

## 2. The productized ecosystem (auto-execute vs alerts, and custody)

| Product | Mode | Custody model | Fee |
|---|---|---|---|
| **PolyGun** (`@polygunsniperbot`) | **Auto-executes** copy+sniper | Per-user smart wallet, key in Telegram session | ~1%/tx, gas sponsored |
| **PolyCop** (`@PolyCop_BOT`) | **Auto-executes** copy+sniper+TP/SL | Non-custodial Polygon wallet, key in session | ~0.5%/filled trade |
| **Polycopy Premium** (`polycopy.app`) | **Auto-executes** ("Auto Copy") | Hosted automation, "your keys/capital are yours" | $30/mo + 1% taker/0.5% maker |
| **PolyTrack / PolymarketFlow / PolyMonit / Polynyx / Alphascope** | **Alerts / analytics only** | Read-only (often no wallet connect) | Freemium (~$10–$50/mo) |

**The core distinction you asked about:** only a handful *auto-execute*; most "copy" tools are
**whale alerts**. Custody splits into (a) **read-only trackers** (no key risk) and (b)
**Telegram auto-executors** whose "key never leaves your session" is an **unverifiable vendor
claim** — and this exact space has a documented history of key-stealing malware
(https://www.cryptopolitan.com/polymarket-copy-traders-warned/). A safer documented pattern is
**ERC-20 spending-approval / revocable allowance** rather than handing over a key
(https://www.polycopytrade.net/blog/non-custodial-copy-trading-polymarket.php).

**Trader selection** is universal across products: the **official leaderboard API** +
on-chain-reconstructed PnL, layered with proprietary "scores" (PolyCop "AI wallet scoring",
Polycopy "Copy Score" by category/price-range, PolymarketFlow "Smart Money Score", Polynyx
arbitrage-bot filtering). https://docs.polymarket.com/api-reference/core/get-trader-leaderboard-rankings

**Treat every performance number as marketing** — e.g. PolyTrack "73% accuracy" (for an
unlaunched feature), PolySmart.io "94% accuracy / <2s", PolyCop "0–1 block execution". None
are independently verified.

**On-chain analytics substrate (verifiable):** because Polymarket settles in USDC on Polygon,
any trader's PnL is reconstructable from `/activity` + ERC-1155 transfers. Community
**Dune** dashboards (e.g. `dune.com/defioasis/polymarket-pnl`) and **Nansen's prediction-market
API** (https://docs.nansen.ai/api/prediction-market) do exactly this, resolving the **proxy/Safe
address back to the user** — the central technical problem (see §3).

---

## 3. Technical detection & execution reference

### 3.1 Detecting a *specific* wallet, four ways
| Approach | Attributes to a wallet? | Latency | Notes |
|---|---|---|---|
| **(a) Poll `/activity?user=<addr>`** | **Yes** (direct) | poll interval + indexer lag | Simplest correct method; dedup by `transactionHash` |
| **(b) CLOB market WS `last_trade_price`** | **No** (anonymous) | lowest (push) | Fast "a trade happened" nudge only |
| **(c) Polygon `OrderFilled` logs** | **Yes** (`maker`/`taker`) | block time ~2s + RPC; `eth_subscribe` push | Most authoritative; must handle multi-match where `taker` = exchange contract → **attribute on `maker`** |
| **(d) Goldsky / subgraph** | **Yes** (`maker`) | indexer lag (seconds+) | Best for research/backfill, weakest for latency |

Sources: https://docs.polymarket.com/api-reference/core/get-user-activity ·
https://docs.polymarket.com/developers/CLOB/websocket/wss-overview ·
https://github.com/Polymarket/ctf-exchange · https://goldsky.com/chains/polymarket

### 3.2 `OrderFilled` event & proxy routing
```solidity
event OrderFilled(
  bytes32 indexed orderHash, address indexed maker, address indexed taker,
  uint256 makerAssetId, uint256 takerAssetId,
  uint256 makerAmountFilled, uint256 takerAmountFilled, uint256 fee);
```
- `maker`/`taker` are the **proxy wallet** addresses (not EOAs). `assetId == 0` means USDC
  collateral; non-zero = ERC-1155 outcome token. In >2-order matches `taker` may be the
  **NegRisk exchange contract**, so attribute on `maker`.
  https://raw.githubusercontent.com/Polymarket/ctf-exchange/main/src/exchange/interfaces/ITrading.sol
- ⚠️ V2 redesigned the order struct and didn't publish a clean `OrderFilled` ABI diff —
  **pull the live ABI** from the v2 exchange (`0xE111180000d2663C0091e4f400237545B87B996B`) for
  post-cutover blocks; neg-risk v2 = `0xe2222d279d744050d28e00520010520000310F59`.
  https://docs.polymarket.com/v2-migration

### 3.3 Order execution (`py-clob-client`)
- **Market (take liquidity now):** `create_market_order(MarketOrderArgs(token_id, amount,
  side, order_type=OrderType.FOK))` → `post_order(...)`. For BUY, `amount` is **USDC**; for
  SELL, **shares**. The order `price` acts as a **worst-price (slippage) cap**, not a target.
- **Limit:** `create_order(OrderArgs(token_id, price, size, side))` → `post_order(..., GTC)`.
- Auth: EOA key → L1 EIP-712 sig → `/auth/api-key` → L2 HMAC creds. ⚠️ V2 → use
  `py-clob-client-v2` / `@polymarket/clob-client-v2`; v1-signed orders are rejected.
  https://docs.polymarket.com/trading/orders/create · https://github.com/Polymarket/py-clob-client

### 3.4 Modeling realistic fills — **walk the book**
Don't assume the last/quoted price. `GET /book` returns `bids`/`asks` as `{price,size}` levels;
accumulate levels until cumulative size ≥ your order, take the **volume-weighted average**.
Documented example: a 7,000-contract buy at quoted ask 0.530 actually fills **~0.5356**. The SDK
exposes `calculate_market_price()` to estimate this before sizing.
https://docs.polymarket.com/trading/orderbook ·
https://www.polymarketdata.co/blog/polymarket-slippage-l2-order-book-guide

### 3.5 Costs & gotchas that change copy economics
- **Taker fees are now nonzero & category-based**, `fee = C·feeRate·p·(1−p)` (peaks at p=0.5);
  reported taker rates ≈ Crypto 0.07 / Sports 0.03 / Politics·Finance·Tech 0.04 / others 0.05;
  **makers pay 0**. A copier taking liquidity pays the full taker fee **on every mirror**, and
  the fee was explicitly introduced to **curb latency arbitrage** — i.e., to tax exactly what a
  copy bot does. ⚠️ V2 moves fees to match-time (`getClobMarketInfo()`).
  https://docs.polymarket.com/trading/fees
- **Tick size** per-market (0.1/0.01/0.001/0.0001) and **changes dynamically near extremes**
  (>0.96, <0.04); **min order size** is per-market — read both from `/book`, don't hardcode.
- **Neg-risk markets** route through a **separate exchange contract** and must be flagged
  (`neg_risk:true`) or orders are rejected; "buy NO on X" is fungible with "buy YES on all
  others," so a naive token-for-token copier can misread an arbitrage/convert as a directional
  bet. https://docs.polymarket.com/advanced/neg-risk
- **Observation latency, end-to-end:** ~2s Polygon block + indexer/poll → **~3–8s** for
  `/activity` polling; sub-second for on-chain `eth_subscribe`. Polygon finality ~2–5s,
  reorg depth ≤2.

---

## 4. What this means for building Polly mvp2

1. **Copy economics are adversarial by design.** Nonzero taker fees explicitly target latency
   arbitrage; you pay them every mirror, enter 3–8s late, and walk a book that already moved.
   Any backtest that prices fills at the leader's price (like mvp1) is optimistic.
2. **Independent confirmation of mvp1's finding.** A live ¼-Kelly+consensus bot got −2.47% ROI /
   9.5% win rate in 10 days — "no edge once wallets are widely tracked." Out-of-sample realism
   is the whole game.
3. **Detection design choice:** `/activity` polling is the simplest correct method and what to
   build first; `eth_subscribe` on `OrderFilled` (attribute on `maker`) is the latency upgrade.
4. **Fill realism is mandatory:** model fills by **walking the live `/book`** + taker fee +
   latency-Δ, not the leader's price. This is the single biggest fix over mvp1.
5. **Security posture:** never run untrusted repos with a funded key; prefer a fresh proxy with
   a capped balance; audit dependencies (active key-stealer malware in this exact niche).
