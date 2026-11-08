# AGENTS.md: Research Stack

## Goal and scope
Build a reliable research and paper-trading pipeline for Indian equities using existing tools and minimal custom code. This phase qualifies the pipeline, not the profitability or live readiness of any strategy.

Paper only. Never place, enable, or prepare live orders. A future live-trading decision is outside scope and belongs to the user.

## Proposed components
- **OpenAlgo** (`github.com/marketcalls/openalgo`): India-facing data and sandbox layer. Verify current installed-version capabilities; do not assume a feature from a README is available or behaves as expected.
  - Platform, Python library (3.12+) and optional Indicator Skills. Analyzer Mode gives virtual capital on real broker prices. AGPL-3.0.
- **NautilusTrader** (`github.com/nautechsystems/nautilus_trader`): research/backtesting engine. Verify current installed-version behavior for data, execution, fees, and supported integrations.
  - **nautilus-fyers** (`github.com/sunilsala88/nautilus-fyers`): community Fyers adapter (alpha, single maintainer, Python 3.11+). Use it for data only. It has no paper sandbox: never register its execution client, and never test with real orders, even tiny or far-from-market ones. For paper fills use NautilusTrader's sandbox execution client.
- **Broker data API**: **shortlisted providers are Angel One (SmartAPI) and Fyers**. Both offer free API access and free market data per their current public pages (researched 7 Nov 2026). Recheck current terms, access, history limits, rate limits, instrument coverage, and authentication behavior before relying on them. **Fyers tokens expire ~6 AM IST daily; Angel One token behavior to confirm. Fyers has a 100,000 requests/day cap.**
- Do not assume a supported OpenAlgo–Nautilus bridge or an official Indian venue adapter. Community adapters may be incomplete or unstable. **Only Fyers has a NautilusTrader adapter found (`nautilus-fyers`, alpha).**

## Safety and change rules
1. Paper only. Never configure a live execution route or use live-order credentials in a strategy runtime. Use data-only credentials where available; never commit secrets.
2. Before paper execution, identify and verify a technical control that prevents live-order placement. Instructions, labels, or an assumed sandbox mode are not sufficient evidence.
3. Configure existing tools first. Add code only to fill a verified gap; keep integration code in `bridge/`, add a test, and explain why configuration is insufficient.
4. Make small, focused changes. One concern per pull request. Never merge; the user approves every merge.
5. Read the current docs for the installed version before using an API. Do not guess names or behavior.
6. Do not invent or change capital, loss limits, sizing limits, strategy thresholds, or scope decisions owned by the user.
7. Surface errors explicitly. Never silently fall back from paper to live, hide a failed check, or report success when the required evidence is missing.
8. **Handle broker token expiry explicitly.** Fyers tokens expire ~6 AM IST daily; Angel One behavior to confirm. Unattended runs must have a tested re-authentication or safe-stop plan.
   - Fyers: keep the refresh token (valid ~15 days) and PIN in environment variables or a secret store, never in code or the repo; call `FyersAuthenticator.refresh_access_token(refresh_token, pin)` in pre-market job. Interactive login required every ~15 days.
   - OpenAlgo: runs locally at `http://127.0.0.1:5000`, WebSocket proxy on port 8765, requires broker connection and API key from dashboard.
9. **Keep credentials in one place.** Broker tokens and the Fyers PIN live only in environment variables or a secret store, read by OpenAlgo and the Nautilus data client. Strategy and research code gets none. Fyers and Angel One tokens may be order-capable, so assume they are. Keep each tool in its own virtualenv (OpenAlgo needs Python 3.12+, nautilus-fyers 3.11+).

## Data, accounting, and research integrity
1. Document source, extraction time/parameters, timestamps/time zone, exchange calendar, instrument identifiers, symbol changes, adjustment policy, and dataset version.
2. Check duplicates, out-of-order or out-of-session bars, missing values, and unexplained gaps against an explicit expected-data definition.
3. Signals must not use future data. Record the execution timing model; a signal from a bar may act only on the next eligible bar or later, as specified and tested.
4. Use a dated, sourced Indian charges configuration and a documented slippage model. Validate simulated accounting against independent hand calculations before relying on results.
5. Any strategy result must include costs and a double-cost sensitivity case. Do not claim that pipeline qualification establishes strategy performance.
6. Before a strategy-performance backtest, obtain user-approved pass/fail criteria, risk limits, test/holdout periods, leakage controls, and allowed variants. Do not invent numeric thresholds.
7. Log every variant tried. Report failures and negative results honestly; do not tune a strategy until it passes.

## Gate workflow
1. Restate the task and identify its gate. Read relevant docs and project files before changing anything.
2. Complete gates in order: scope/safety; data quality; accounting/timing; paper smoke test; operational safety/recovery. Strategy evaluation is blocked until its protocol is approved.
3. For each gate, record pass/fail/blocked status and evidence. A one-session smoke test proves basic workflow operation only, not strategy quality or unattended readiness.
4. Make the smallest change, run the focused tests/checks, and report actual output and remaining risks.
5. Preserve versions, data/config identifiers, logs, test results, assumptions, and known limitations so the run can be reproduced.
6. Ask the user before changing scope, provider, hosting model, capital, risk limits, or any other user-owned decision.

## When uncertain
State what is unknown and what evidence would resolve it. Stop at the affected gate rather than guessing, bypassing a failed check, or proceeding on an unverified assumption.