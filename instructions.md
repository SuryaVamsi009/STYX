# STYX Instructions

## Overview
STYX (Systematic Trader's Yield eXtractor) is a research and paper-trading pipeline for Indian equities.

**Core Philosophy**: Build a reliable pipeline using existing open-source tools (OpenAlgo + NautilusTrader), minimizing custom code. This phase qualifies the **pipeline**, not any trading strategy.

## Proposed Stack

| Component | Purpose | Key Details |
|-----------|---------|-------------|
| **OpenAlgo** | India-facing market-data & paper-trading layer | Broker plugins, REST/WebSocket API, Historify (DuckDB), Analyzer Mode (virtual capital on real prices). AGPL-3.0. Python 3.12+ |
| **NautilusTrader** | Research & backtesting engine | Python strategies, Rust/Cython core. Verify installed version behavior |
| **nautilus-fyers** | Fyers data adapter for Nautilus | Alpha, single maintainer, Python 3.11+. **Data only** - no paper sandbox. Use Nautilus sandbox execution client |
| **Broker API** | Market data source | Shortlisted: **Angel One (SmartAPI)** and **Fyers**. Both require demat. Fyers: tokens expire ~6 AM IST daily, 100k req/day cap |

## Project Structure (Planned)
```
STYX/
├── bridge/                # Minimal integration code (only for verified gaps)
├── src/
│   └── styx/              # Main package (if needed)
├── tests/                 # Test suite
├── notebooks/             # Jupyter notebooks for research
├── data/                  # Local data storage
├── config.yaml            # Strategy configuration
├── .env                   # Environment variables (API keys, tokens, PINs)
├── requirements.txt       # Python dependencies
├── README.md
├── instructions.md
└── AGENTS.md              # Agent instructions (from Research Stack Plan)
```

## Gate-Based Plan (Must Complete in Order)

### Gate 0 — Confirm Scope & Safety Boundary
- Confirm provider (Angel One or Fyers), instrument scope (initial: NSE equity cash, intraday), environment
- Verify paper-only boundary with technical control (not just instruction)
- Document tool versions, constraints, known limitations

### Gate 1 — Verify Data Path & Historical Quality
- Retrieve live quote for in-scope instrument
- Load bounded historical sample (multiple instruments, periods, calendar edge cases)
- Check: malformed timestamps, duplicates, gaps, out-of-session bars, symbol changes, adjustment policy
- Save dataset identifier, extraction params, data-quality report

### Gate 2 — Verify Accounting & Simulation Mechanics
- Read version-specific docs for bar ingestion, event timestamps, signal evaluation, order submission, fills, positions, fees
- Construct deterministic synthetic example with known prices/quantities/timestamps
- Hand-calculate: gross P&L, brokerage, STT, exchange charges, SEBI fees, stamp duty, GST, slippage (dated, sourced config)
- Verify signal timing model (no future data access)
- Compare engine output with hand calculation

### Gate 3 — Paper-Workflow Smoke Test
**Select ONE route:**
- **Route A**: NautilusTrader sandbox execution on live Fyers data (via nautilus-fyers). Use `BacktestEngine` for history, `TradingNode` with simulated execution for live data. **Never register Fyers execution client.**
- **Route B**: OpenAlgo Analyzer Mode (virtual capital on real broker prices) with Angel One or Fyers feed. Sandbox config: ₹10Cr default (set to user-approved capital), 5s MTM/pending checks, MIS square-off 15:15 IST

### Gate 4 — Qualify Operational Safety & Recovery
- Test: token expiry (Fyers ~6 AM IST daily, refresh token ~15 days), network interruption, stale data, process restart, duplicate events, storage failure
- Verify safe-stop behavior, no live-order fallback, logs without secrets
- Fyers refresh: `FyersAuthenticator.refresh_access_token(refresh_token, pin)` in pre-market job

### Gate 5 — Freeze Research Protocol (Deferred)
- User must approve written protocol before any strategy backtest
- Defines: hypothesis, universe, timeframe, sizing, risk limits, in-sample/validation/holdout, costs, pass/fail metrics

### Gate 6 — Review & Preserve Evidence
- Preserve: gate status, versions, config, data identifiers, cost config, logs, reconciliation results, limitations
- Review paper operation on agreed schedule

## Safety & Change Rules
1. **Paper only** - Never configure live execution or use live-order credentials in strategy runtime
2. **Verify technical control** preventing live-order placement before paper execution
3. **Configure first** - Add code only for verified gaps; keep in `bridge/` with test and explanation
4. **Small focused changes** - One concern per PR; user approves every merge
5. **Read current docs** for installed version before using any API
6. **User owns risk limits** - Don't invent/change capital, loss limits, sizing, thresholds
7. **Surface errors explicitly** - Never silently fall back from paper to live
8. **Handle token expiry** - Fyers tokens expire ~6 AM IST; refresh token + PIN in env/secret store
9. **Credentials in one place** - Broker tokens/PIN only in env vars or secret store; strategy code gets none

## Data, Accounting & Research Integrity
1. Document: source, extraction time/params, timestamps/TZ, exchange calendar, instrument IDs, symbol changes, adjustment policy, dataset version
2. Check: duplicates, out-of-order/out-of-session bars, missing values, unexplained gaps
3. Signals must not use future data; record execution timing model
4. Use dated, sourced Indian charges config + documented slippage model; validate against hand calculations
5. Strategy results must include costs + double-cost sensitivity case
6. User-approved protocol required before strategy-performance backtest
7. Log every variant tried; report failures honestly

## Setup (When Implementation Begins)
1. Choose provider (Angel One or Fyers) and paper route (A or B)
2. Set up separate virtualenvs: OpenAlgo (Python 3.12+), NautilusTrader (Python 3.11+)
3. Configure `.env` with broker credentials, tokens, PINs (never in code/repo)
4. For Fyers: set up token refresh job (pre-market, using refresh token + PIN)
5. For OpenAlgo: deploy locally, connect broker plugin, enable Analyzer Mode

## Cost Model (Validate in Gate 2)
- Brokerage (broker's current schedule: flat fee capped by %)
- STT (Securities Transaction Tax)
- Exchange transaction charges
- SEBI fees
- Stamp duty (differs for delivery vs intraday)
- GST
- Slippage (documented model + double-cost sensitivity check)

## Decisions Still Needed (User-Owned)
- [ ] Initial data provider: Angel One or Fyers
- [ ] Hosting: user's machine or always-on server
- [ ] First paper route: Route A (Nautilus) or Route B (OpenAlgo)
- [ ] Risk limits: capital, position sizing, loss thresholds
- [ ] First strategy protocol: intentionally not defined in this phase

## Known Risks to Verify
- No ready-made OpenAlgo–Nautilus bridge
- Indian venue integrations for Nautilus are community-maintained
- Broker/API terms can change
- OpenAlgo is AGPL-3.0
- Fyers free-data claim needs reconfirmation
- nautilus-fyers is alpha with single maintainer
- OpenAlgo Analyzer Mode is execution sandbox, not exchange emulator
- Live-order boundary: tokens likely order-capable; not registering execution client is the control
- Daily bar timestamps: stamp at session close, not midnight