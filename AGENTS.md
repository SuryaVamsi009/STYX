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
