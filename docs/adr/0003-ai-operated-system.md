# AI-operated system

STYX's primary operator is an AI agent. Humans approve, the AI operates. Design rules:

1. All state is machine-readable files, with a `styx status --json` summary.
2. Every action is a command with an exit code and JSON output.
3. The AI process holds no broker credentials and talks only to OpenAlgo, and every action first confirms Analyzer Mode is on and refuses otherwise.
4. BLOCKED and FAIL mean stop, with a `STOP` file that halts all jobs.
5. Capital, limits, protocols and merges need human-created approval records that the AI cannot write.
6. Every AI action is logged append-only.
7. Results are deterministic and replayable from saved snapshots.
8. The AI has rate and run limits.