# Phase 6: Evals — measuring whether the library actually helps

The library's purpose is a measurable lift for weaker models on this repo. This phase produces
the measurement instrument and runs the first reading. Without it, a plausible-looking library
and a working library are indistinguishable — and plausible-looking is the default failure.

## Probes (mined in Phase 1, finalized here)

`.claude/skills/.skill-library/probes.md` holds 5–10 probes. Finalize each to this schema:

```
### P<n>: <task statement as a user would type it>
- entry point: <file or subsystem>
- success checkpoint: <observable: command + expected output | file state | test that passes>
- expected primary skill: <name>
- source: <ledger ID / commit that makes this a real, representative task>
```

Probe quality rules:
- Every probe is a REAL task shape from this repo's history (a merged fix, a small feature, a
  CI failure) — not an invented quiz question.
- Checkpoints are observable by command, never "the code looks right".
- At least one probe exercises a decision gate (change-control, validation) — those are where
  weaker models fail silently.
- Probes must NOT be answerable from the README alone; otherwise they measure nothing.

`probes.md` lives outside any skill directory ON PURPOSE: it must never load into consumer
sessions or add a trigger description.

## Cold-context run (this build, done by the builder)

Already partially done as review gate R6. Complete the set here: fresh subagent, repo +
library, one probe at a time, ≥2 probes total (more if gates R3/R6 forced skill rewrites).
Record per probe in the final report:

| probe | skill loaded (right one?) | checkpoint reached? | steps followed literally vs improvised | turns |

Any probe where the subagent succeeded by IGNORING the library is a red flag: the library is
inert for that task type — revisit its trigger or content before calling the build done.

## A/B protocol (for the operator, with the actual target models)

The builder's subagents approximate a consumer. The real measurement uses the operator's
target models (e.g., Opus, Sonnet) on their real harness. Ship these instructions verbatim in
the final report:

1. **B arm (with library):** in the repo, run your target model on each probe as a fresh
   session: paste the probe task statement, let it work, record: success (checkpoint reached
   y/n), number of turns, wrong/failed commands run, whether the expected skill loaded.
2. **A arm (without):** temporarily disable the library — rename the directory:
   `.claude/skills` → `.claude/skills.off` (PowerShell: `Rename-Item .claude/skills skills.off`;
   bash: `mv .claude/skills .claude/skills.off`). Re-run the same probes, fresh sessions, same
   model. Rename back afterwards.
3. **Compare per probe:** success rate, turns-to-checkpoint, wrong-command count. The library
   earns its context cost when B beats A on success or cuts turns/wrong-commands materially on
   the SAME model. B ≈ A everywhere → the library is decoration for this repo; use the results
   to find which skills never loaded (trigger problem) or loaded but didn't change behavior
   (content problem).
4. Re-run the same probe set after every refresh — it doubles as a regression suite for the
   library itself.

## Interpreting failures (route, don't gloss)

| Symptom | Diagnosis | Route |
|---|---|---|
| expected skill never loaded | trigger/description failure | authoring.md description contract + R3 |
| skill loaded, model still failed | content failure: missing branch, wrong observation, judgment call left open | authoring.md procedure style + R6 |
| model succeeded ignoring skills | probe too easy OR skill redundant | replace probe; reconsider skill admission |
| model followed skill into an error | factual failure — a claim survived review wrongly | R2 on that skill, then fix |

Eval failures during this phase are BUILD failures: fix and re-run the affected gate. Only
gloss-free results go in the final report.
