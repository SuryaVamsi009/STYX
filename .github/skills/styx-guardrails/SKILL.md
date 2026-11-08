---
name: "styx-guardrails"
description: "Use when changing STYX code that touches execution or data clients, strategies, indicators, the cost model, backtests, or gate evidence."
---

# STYX guardrails

STYX is paper-only research and paper trading for Indian equities. Passing a gate shows the pipeline behaves as tested. It does not show a strategy has an edge. Run this checklist before reporting any change as done, and report real command output.

## 1. Paper-only boundary

Broker tokens (Fyers, Angel One) are likely order-capable, so the control is that no real-broker execution client is ever registered. Flags like `LIVE_ORDERS=False` are not controls.

- Search the change for `FyersLiveExecClientFactory`, any `exec_clients` entry that is not the sandbox client, and any call to a broker order endpoint (`placeorder`, `smartorder`, `basketorder`) outside OpenAlgo Analyzer Mode.
- If the change adds or touches an execution path, a test must prove the only registered execution client is the sandbox one, and that orders land in the sandbox.
- Before any OpenAlgo order call, the code must confirm Analyzer Mode is on, and refuse otherwise.
- Never test with tiny or far-from-market real orders.
- Any hit: stop and report. Do not fix it by adding a flag.

## 2. Credentials

- Tokens and the Fyers PIN come only from environment variables or a secret store.
- Strategy and research code receives no broker credentials.
- Search the diff, config, fixtures and logs for keys, tokens and PINs. Any hit: stop.

## 3. No look-ahead

- Daily bars are stamped at the session close (15:30 IST, stored as UTC). Midnight stamps are a bug.
- A signal on bar t fills at the next bar's open or later, never at bar t.
- Every indicator or signal function needs a truncation test: the output for bars up to t must equal the output computed on data cut at t.

```python
def test_no_lookahead(fn, df, cut):
    full = fn(df)
    part = fn(df.iloc[:cut])
    pd.testing.assert_series_equal(full.iloc[:cut], part, check_names=False)
```

- Warm-up NaNs stay NaN. Do not back-fill.

## 4. Costs

- Results include the Indian charges model (brokerage, STT, exchange, SEBI, stamp duty, GST) plus slippage.
- Every rate carries `as_of` and `source`. Rates without them are UNVERIFIED placeholders. Do not invent or "fix" a rate from memory.
- Report each result at 1x and 2x costs. If it only works at 1x, say so.
- Hand-calculated expected values come from an independent calculation, not from the code under test.

## 5. Numbers Surya owns

Capital, position sizing, loss limits, thresholds, horizon, universe, and pass or fail criteria are never defaulted or tuned by the agent. If one is needed and not set, ask.

## 6. Research loop integrity

- A call is written to the append-only registry before its outcome is known. Edits are rejected.
- Only forward-collected calls count as evidence, because an LLM has read the past.
- Grader: entry at the next bar's open, stop wins a tie, results net of costs.
- An LLM-produced number that is not in the snapshot is rejected.

## 7. Evidence and honesty

- Update `evidence/gate_<n>.json` and run `python scripts/gate_check.py --gate <n>`. Report PASS, FAIL or BLOCKED as printed.
- Never report success when evidence is missing. A missing check is BLOCKED, not passed.
- Label unverified API names, rates and behaviours `UNVERIFIED`, and use the `source-driven-development` skill before relying on them.
- Log every strategy variant tried, including failures. Never tune until something passes.

## 8. Stop and ask when

The boundary test fails or cannot be written, a secret appears, a gate fails, a protocol is missing, or the request would need a live order in any form.