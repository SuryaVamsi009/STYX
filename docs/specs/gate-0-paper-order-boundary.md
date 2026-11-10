# Gate 0: Paper-order boundary

**Status:** Design approved; execution **BLOCKED** pending installed-version documentation and runtime evidence.

## Goal

Prove the selected Gate 0 configuration does not register or invoke a real-broker order path, records its one test order as virtual, and creates no new order in the broker's own order book. This is a bounded claim about the tested configuration, not a guarantee about every external path or future change.

## Approved scope

- Provider: Angel One or Fyers, whichever is connected in OpenAlgo. Recorded in evidence/gate_0.json when Part A runs. Until then it is NOT_SET.
- Route: OpenAlgo Analyzer Mode.
- Environment: Surya's own machine.
- Instrument: NSE `RELIANCE`, cash equity.
- Test order: one virtual market Buy, one share, product MIS.
- Test-only capital: ₹1,00,000 (1 lakh) at 1× (no leverage); no F&O. This is not planning capital and cannot produce strategy evidence.
- ₹2,000 was the first approved test capital. OpenAlgo's sandbox only allows ₹1L, ₹5L, ₹10L, ₹25L, ₹50L or ₹1Cr, so Surya approved ₹1,00,000, the smallest allowed value, on 10 Nov 2026. Patching OpenAlgo to allow ₹2,000 was rejected, because Gate 0 must test the unmodified installed version.
- The research universe is unchanged.

Analyzer Mode isolation, current provider terms, and the installed-version order-book visibility behavior are **UNVERIFIED**. Do not infer safety from the mode label or guess API names.

## Part A — any time

1. Install/configure the selected existing tools and read the installed-version OpenAlgo documentation and the connected broker's documentation. Establish how Analyzer Mode handles orders and how a read-only broker order-book check is performed. If isolation or read visibility cannot be established, Part A is **BLOCKED**.
2. Record the OpenAlgo and relevant tool versions, selected provider/instrument/environment, Analyzer Mode state, ₹1,00,000 (1 lakh) capital and 1× leverage setting. Do not record credentials.
3. Search all STYX-owned source and configuration for direct broker-order call sites. Separately audit the installed OpenAlgo version's active execution registration and routing path. Prove no real-broker execution path is registered or invoked; unused vendor implementation code alone is not evidence that a path is active.
4. Confirm the configured route is in Analyzer Mode before any order. Do not submit the test order unless all Part A isolation checks pass.

## Part B — regular NSE cash-equity session only

Part B runs only during a regular NSE cash-equity session verified against an authoritative current exchange calendar. Outside that session, including holidays and special/extended sessions, Part B is **BLOCKED as expected**, not failed.

1. Require a quiet order-activity window on the same connected broker account used by the configured data path, from the baseline through the post-test snapshot. If that cannot be guaranteed, Part B is **BLOCKED**.
2. Take a timestamped, read-only broker order-book baseline. Use the app or a documented read-only API; do not guess an API name or log credentials.
3. Use the installed-version documented funds requirement for the specified one-share order, including applicable charges. If the requirement is unknown or exceeds ₹1,00,000 (1 lakh), do not submit; request Surya's approval before increasing the test amount. Never change quantity or leverage automatically.
4. After Part A passes and the funds check fits, submit exactly the approved virtual order: one market Buy of one NSE `RELIANCE` cash-equity share, product MIS, at 1×. No live order may be placed, enabled, or prepared.
5. After the documented order-book visibility interval, take a timestamped, read-only snapshot of that broker's order book. A new broker-side order is a Gate 0 **FAIL** and stops the test. If the read is unavailable or visibility is uncertain, Part B is **BLOCKED**.
6. Confirm the order is recorded as virtual in Analyzer Mode and the route-specific guard/test shows no real-broker order path was registered or invoked.

## Provider notes

- **Fyers:** the access token expires around 6 AM IST every day, so Surya logs in again through OpenAlgo each trading morning before Part A or Part B. Confirm the exact expiry in the installed-version docs. The sign-in is OAuth-style through Fyers' own page, using the app's App ID and secret.
- **Angel One:** OpenAlgo's Angel login takes the client code, PIN and a TOTP. Session length is UNVERIFIED until checked in the installed-version docs.
- Both brokers' tokens are order-capable. The boundary proof does not depend on which broker is chosen.
- Switching provider after a Gate 0 run requires a new Gate 0 run and new evidence.

## Gate result

- **PASS:** All Part A checks pass; Part B runs in the qualifying session; the order is recorded virtually; the broker order book shows no new order; and all evidence is complete.
- **FAIL:** A real-broker order path is registered or invoked, an order is not recorded virtually, or a new broker-side order appears during the quiet test window. Stop the test; do not attempt another order.
- **BLOCKED:** Required version-matched docs, mode/route evidence, funds requirement, read-only order-book visibility, quiet account window, or qualifying session is unavailable or ambiguous. Do not fall back to another route.

Before Gate 3 or any research or strategy run, reset Analyzer Mode capital to Surya-approved planning capital. Gate 0 results are not strategy evidence.

## Evidence

Record the scope, versions, configuration/mode state, route audit, test-only capital and leverage, documented funds requirement, order result, timestamped broker order-book snapshots, guard/test output, status, and blockers in `evidence/gate_0.json`. Identify any broker account only with a redacted reference; never include credentials. Record actual outputs and keep unperformed checks as `NOT_RUN` or `UNVERIFIED`, not as passing.

## Current blockers

- No local OpenAlgo installation or installed-version documentation is available; Analyzer Mode isolation is **UNVERIFIED**.
- Part A and Part B have not been run.
