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

## Skills
- Skills live in `.github/skills/`. Use `grill-with-docs` before any new design, `to-spec` then `to-tickets` then `implement` for building, `tdd` inside every implementation, `code-review` before every PR, `pr` for PR bodies.
- Before touching execution, data clients, indicators, the cost model or gate evidence, run `styx-guardrails`.
- Before using any library API, run `source-driven-development`. Label anything unverified `UNVERIFIED`.
- Quality-bar numbers (coverage and similar) can use the defaults from `constraint-driven-development`. Trading numbers (capital, sizing, loss limits, thresholds, horizon, universe, pass criteria) are never defaulted. Ask Surya.
- Every indicator or signal needs a test that removing future bars does not change past values.
- Use `doubt-driven-development` only when Surya asks, or on changes to the no-live-orders boundary.

## Agent skills

### Issue tracker

GitHub Issues (uses `gh` CLI). See `docs/agents/issue-tracker.md`.

### Domain docs

Single-context (`GLOSSARY.md` + `docs/adr/` at repo root). See `docs/agents/domain.md`.
