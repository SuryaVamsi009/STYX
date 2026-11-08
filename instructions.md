# STYX: Systematic Trader's Yield eXtractor

Implementation instructions. Owner: Surya. Written 8 Nov 2026. Read this file first; it is the single entry point for people and agents working on STYX.

## 1. What STYX is

STYX is a research and paper-trading pipeline for Indian equities. It reuses existing tools instead of writing a trading engine:

- **OpenAlgo** (`marketcalls/openalgo`): India-facing layer with broker plugins, history store (Historify) and Analyzer Mode (virtual capital on real prices).
- **NautilusTrader** (`nautechsystems/nautilus_trader`) with **nautilus-fyers** (`sunilsala88/nautilus-fyers`, alpha) for backtesting. nautilus-fyers supplies Fyers data only.
- **Free broker data**: Angel One SmartAPI or Fyers. Recheck current terms before relying on either.
- **A small research loop** (section 6) that records every research claim before the outcome, grades it mechanically, and scores it against baselines.

STYX is not a live-trading system. Nothing in this file authorises a real order. Passing the pipeline gates shows only that data, accounting and the paper workflow behave as tested. It does not show that any strategy has an edge.

## 2. Non-negotiable rules

1. **Paper only.** Never place, enable or prepare a live order. A live-trading decision is outside this project and belongs to Surya.
2. **Prove the boundary, do not assume it.** Fyers and Angel One tokens are likely order-capable, so "data-only credentials" may not exist. The control is that no execution client for a real broker is ever registered, and Gate 0 and Gate 3 must test that. A flag such as `LIVE_ORDERS=False`, an instruction or a UI label is not a control. Never test with "tiny" or far-from-market real orders.
3. **Minimise code.** Configure existing tools first. New code only fills a verified gap, lives in `bridge/` or `research/`, has a test, and comes with a short note on why configuration was not enough.
4. **Verify before relying.** Read the docs for the installed versions. Do not guess API names, broker terms or sandbox behaviour. Anything unverified is labelled `UNVERIFIED`.
5. **Credentials in one place.** Broker tokens and the Fyers PIN live only in environment variables or a secret store, read by OpenAlgo and the Nautilus data client. Strategy and research code gets none. Never commit secrets and never log them.
6. **Costs always.** Every result includes a dated, sourced Indian charges model and slippage, and a double-cost check.
7. **Surya owns risk.** Do not invent or change capital, sizing, loss limits, thresholds, horizon or universe. Ask.
8. **Evidence is reproducible.** Record versions, data identifiers, config, logs and outcomes for every gate.
9. **Forward data only.** An LLM has read the past, so only calls registered before their outcome count as evidence.
10. **Small, reviewable changes.** One concern per pull request. Agents never merge; Surya approves every merge.

## 3. Repository layout

```
styx/
├── vendor/                      # cloned upstream repos, gitignored
│   ├── openalgo/
│   └── nautilus-fyers/
├── .venv-openalgo/              # Python 3.12, gitignored
├── .venv-nautilus/              # Python 3.12, gitignored
├── bridge/                      # integration code (the only custom code besides research/)
│   ├── openalgo_nautilus.py     # Historify -> Nautilus catalog
│   └── cost_model.py            # Indian charges + Nautilus FeeModel
├── research/                    # the research loop (section 6)
│   ├── snapshots/               # daily scan JSON
│   ├── calls.py  grader.py  scoreboard.py
│   ├── playbook/                # regime profiles computed from history
│   └── protocols/               # written protocols for approval
├── strategies/                  # strategy code, no broker credentials
├── config/                      # no secrets
├── data/                        # catalog and datasets, gitignored
├── evidence/                    # gate_<n>.json inputs and results, no secrets
├── scripts/gate_check.py        # evidence -> PASS / FAIL / BLOCKED
├── tests/
├── AGENTS.md                    # section 8 of this file
└── instructions.md              # this file
```

Two virtualenvs on purpose: OpenAlgo and its library need Python 3.12+, nautilus-fyers needs 3.11+, and NautilusTrader pins its own dependencies.

## 4. Setup

```bash
mkdir styx && cd styx && git init
mkdir -p vendor bridge research/{snapshots,playbook,protocols} strategies config data evidence scripts tests
printf '.env\n*.env\nvendor/\ndata/\n.venv-*/\n' > .gitignore

git clone https://github.com/marketcalls/openalgo.git vendor/openalgo
git clone https://github.com/sunilsala88/nautilus-fyers.git vendor/nautilus-fyers

python3.12 -m venv .venv-openalgo
.venv-openalgo/bin/pip install -r vendor/openalgo/requirements.txt openalgo

python3.12 -m venv .venv-nautilus
.venv-nautilus/bin/pip install -e "vendor/nautilus-fyers[nautilus,live,stream,dev]" pandas duckdb pytest
```

Follow each vendor repo's README for its current run steps; do not rely on this file for them. Copy `scripts/gate_check.py` and the cost model from the fixed Repository Integration Plan (section 4 and section 6 there).

## 5. Build order: the gates

Work in order. Record each gate as **pass**, **fail** or **blocked** with evidence in `evidence/gate_<n>.json`, then run `python scripts/gate_check.py --gate <n>`. A failed gate is fixed and rechecked, or the approach is dropped. Never skip or bypass one.

| Gate | Goal | Done when |
| --- | --- | --- |
| 0. Scope and safety | Choose provider, instruments, environment. Prove the selected paper route has no real-order path. | Scope record names provider, instruments, environment and tool versions. A test proves no real-broker order path is registered or invoked, the selected route records the test order virtually, and the broker's own order book shows no new order. |
| 1. Data path | Prove the chosen source gives usable, reproducible history. | A live quote and a bounded multi-instrument history are loaded. Calendar, timestamps, duplicates, gaps and adjustments are checked and reported. A dataset snapshot id and a quality report are saved. |
| 2. Accounting | Prove simulated accounting matches hand calculation. | A synthetic trade ledger reconciles to a hand calculation within a stated tolerance. Signal-to-fill timing is tested (next bar or later, daily bars stamped at session close). The cost config has `as_of` and `source`. |
| 3. Paper smoke test | One paper route runs a session and produces a reconcilable log. | One route chosen (A or B below), session completed, ledger reconciled, no live order sent or prepared. |
| 4. Operational safety | Failures stop safely. | Token expiry, network loss, stale data, restart and duplicate events are tested. Logs hold no secrets. The boundary still holds after restart. |
| 5. Protocol freeze | Deferred until a strategy is evaluated. | Surya approves a written protocol first (section 7). |
| 6. Evidence review | Preserve and review. | Every gate has its evidence, versions, configs and limitations stored. |

Paper routes for Gate 3. Pick one and test only that:

- **Route B, OpenAlgo Analyzer Mode** (fastest): virtual capital on real broker prices. Set the sandbox capital to Surya's approved planning capital, not the 1 Cr default. Confirm Analyzer Mode is on before any order. Run the validation workflow: market order, limit order away from market, modify, cancel, square-off, reset.
- **Route A, NautilusTrader sandbox execution on Fyers data**: register the Fyers data client and NautilusTrader's sandbox execution client only. Never register `FyersLiveExecClientFactory`. Class and config names are unverified until checked against the installed version.

**Gate 0 Route B exception, approved by Surya:** The single Gate 0 paper-order exercise uses ₹2,000 of Analyzer Mode capital at 1× (no leverage) for one market Buy of one NSE `RELIANCE` cash-equity share, product MIS. This is test-only capital, not planning capital or strategy evidence; no F&O is used. Do not submit the order until Analyzer Mode isolation is verified. Record the capital and leverage in `evidence/gate_0.json`. If the documented funds requirement including applicable charges is unknown or exceeds ₹2,000, stop and request Surya's approval before raising the test amount; never increase leverage or change the quantity automatically. Before Gate 3 or any research or strategy run, reset to Surya-approved planning capital.

## 6. Research loop

After the pipeline gates, STYX adds the loop that decides which ideas deserve a backtest. The full audit and design is on the ATLAS page ("ATLAS Research Process: Audit, Design and Plan"). Summary:

```
Daily scan -> Snapshot JSON -> Research AI -> Call registry
                                                  | graded after the close
                                                  v
Backtest, paper <- Your approval <- Scoreboard <- Grader v2
```

| Step | Build | Done when |
| --- | --- | --- |
| R1. Call registry | `Call` record (id, created_at, origin, symbol, side, entry rule, stop, target, horizon, two-line rationale, snapshot id) appended to an append-only ledger | Calls read back identically and an edit attempt is rejected |
| R2. Scan to JSON | The daily scan writes a snapshot with `source`, `fetched_at`, `status` per field. India VIX comes from an India VIX source. No hard-coded article URLs. | The JSON passes a schema check. Tests run on recorded pages, with no network. |
| R3. Grader v2 | Entry at the next bar's open. Expiry is checked after the bars. If one bar touches both stop and target, the stop counts. Net of costs. | Hand-calculated cases match. Tie, no-fill and timeout cases are tested. |
| R4. Scoreboard | Per origin: calls, hit rate, average net R versus Nifty and random-side baselines, at 1x and 2x costs | It runs end to end on registered calls |
| R5. Research AI v2 | One LLM provider, schema-checked extraction. A number not found in the snapshot is rejected. Word-boundary keyword rules stay as the baseline to beat. | The rejection is tested and no hand-typed market level remains |
| R6. Promotion | Protocol template in `research/protocols/` | One idea goes from scoreboard to an approved protocol |

The scan, grader and scoreboard run on a schedule: the scan registers the day's calls at 9 AM IST and a job after the close grades them.

## 7. Before any strategy backtest (Gate 5)

Do not run a strategy backtest meant to establish performance until Surya approves a written protocol containing:

- Hypothesis, universe, timeframe, signal timing and execution assumptions.
- Position sizing and capital and loss limits, supplied by Surya.
- In-sample, validation and untouched holdout periods, and how leakage is prevented.
- The cost and slippage model with dated sources, and the double-cost check.
- Numeric pass and fail metrics, minimum sample size, and treatment of missing data.
- Which variants are allowed, how each is logged, and when the holdout may be looked at.

Do not invent numeric thresholds. Log every variant tried, report negative results, and never tune until something passes.

## 8. AGENTS.md (copy to the repo root)

```markdown
# AGENTS.md: STYX

Read `instructions.md` first. STYX is paper-only research and paper trading for Indian equities.

## Hard rules
1. Never place, enable or prepare a live order. Never register a real-broker execution client.
2. Never add credentials to code, config, logs or commits. Strategy and research code gets no broker tokens.
3. Do not set or change capital, sizing, loss limits, thresholds, horizon or universe. Ask Surya.
4. Configure existing tools before writing code. New code needs a test and a note on why configuration was not enough.
5. Read the installed version's docs before using an API. Label anything unverified `UNVERIFIED`.
6. One concern per pull request. Tests first. Never merge; Surya approves every merge.
7. The agent that edits the scan does not edit the grader or scoreboard in the same change.
8. Report actual command output. Never report success when evidence is missing, and never silently fall back from paper to live.

## Workflow
Restate the task and name its gate or step. Read docs and files. Make the smallest change. Run the focused tests. Record evidence under `evidence/`. Report results and remaining risks.

## When unsure
State what is unknown and what evidence would settle it. Stop at the affected gate. Do not guess or bypass a failed check.
```

## 9. Definition of done for every pull request

- [ ] One concern, linked to a gate or research step.
- [ ] Test written first, failing before and passing after, with output pasted.
- [ ] No secrets in the diff, config or logs.
- [ ] No real-broker execution client registered; the boundary test still passes.
- [ ] Costs included where a result is reported, with the double-cost case.
- [ ] Evidence file updated and versions recorded.
- [ ] Anything unverified is labelled `UNVERIFIED`.

## 10. Decisions Surya still owes

| Decision | Why it matters |
| --- | --- |
| First data provider: Angel One or Fyers | Fyers has the Nautilus adapter (alpha). Angel One free history covers equity and NFO futures. Both are on OpenAlgo's list. |
| Hosting: own machine or always-on server | Sets how token expiry (Fyers about 6 AM IST daily) and restarts are handled. |
| First paper route: A or B | Gate 3 tests one route only. |
| Planning capital and loss limits | Not set anywhere in this project. Needed for sandbox capital and sizing. |
| Horizon and universe: swing or intraday, which instruments | The scan's picks target 1 to 12 months while the goal is daily income. |
| Pass criteria and minimum sample | Must be written into the protocol before results are looked at. |
| Where the research loop lives | Default assumption: in STYX, with ATLAS left frozen. Confirm. |
| LLM provider and model | One provider, chosen by Surya. |

## 11. Reference docs

- Research Stack Plan and Agent Instructions (the gate plan).
- Repository Integration Plan (code sketches, cost model, gate checker). All code in it is an untested sketch.
- ATLAS Research Process: Audit, Design and Plan (the research loop).
