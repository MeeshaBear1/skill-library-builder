# Express smoke test — A/B results

**Run: 2026-07-10 · express@ba00676 · single trial.** These are real measured
runs, not estimates. Read the honest verdict at the bottom before citing them.

## Method (what was actually done)

Three arms, same probes, fresh isolated sub-sessions, no repo files modified:

- **A — weak model, library OFF** (Sonnet 4.6, told not to read `.claude/skills/`)
- **B — weak model, library ON** (Sonnet 4.6, told to read the relevant SKILL.md first)
- **Ceiling — frontier model, library OFF** (Opus 4.8)

Only the **3 non-mutating probes** ran (P1 run-suite, P2 verify-regression,
P7 locate-routing). The mutating / change-control probes were **not** run: P3 and
P6 name `express-change-control` (unauthored in this 3-skill smoke test), and P4
edits files (needs an isolated worktree per arm). **`turns` = harness tool-call
count** for that sub-session. "Library ON" here is a *proxy* — the sub-agent was
instructed to read the skills, which is more generous than Claude Code's
trigger-based auto-load.

## Scorecard

| Probe | Expected skill | A: weak/OFF | B: weak/ON | Ceiling: frontier/OFF |
| --- | --- | --- | --- | --- |
| P1 — run the test suite | express-test-and-validate | ✓ · 2 turns · 0 wrong | ✓ · 7 turns · 0 wrong · read skill | ✓ · 1 turn · 0 wrong |
| P2 — verify #4893 regression | express-debugging-playbook | ✓ · 1 turn · 0 wrong | ✓ · 6 turns · 0 wrong · read skill | ✓ · 2 turns · 0 wrong |
| P7 — locate routing (trick) | express-architecture-contract | ✓ · 4 turns · 0 wrong | ✓ · 4 turns · 0 wrong · read skill | ✓ · 1 turn · 0 wrong |

Every arm **succeeded** on every probe with **zero wrong commands**. In the B arm
the sub-agent read the expected skill each time. On P7 (the trick — routing lives
in the external `router` package, not `lib/`) **all three arms** correctly named
the `router` dependency and none patched `lib/`; the B arm additionally surfaced
the skill's "fix is upstream" gate.

## Honest verdict — INCONCLUSIVE on the headline claim

- **These 3 probes are too easy to show library lift.** The weak model already
  matched the frontier model on success unaided, so B ≈ A on the outcome — and the
  library arm *cost more* turns (reading the skill is overhead when the model would
  have got there anyway). That is precisely the protocol's "B ≈ A → the library is
  decoration *for these tasks*" signal, and it is a real finding: a verified library
  earns its context cost only where the task exceeds the base model, not everywhere.
- **The claim this repo makes — "a verified library lets a weaker model approach
  frontier" — is NOT tested by this run.** It would show (if anywhere) on the
  change-control probes (P3/P6) and the edit probes (P4), where a naive model
  silently does the wrong safe-looking thing. Those need (a) authoring
  `express-change-control` and (b) per-arm worktree isolation. Until then, treat the
  headline as unproven, not proven.
- **Single trial.** express@ba00676 has a documented flaky test; re-run any flipped
  cell before trusting it. No cell flipped here (all clean passes).

**Next to make this conclusive:** author `express-change-control`, then run P3/P4/P6
in isolated worktrees across the same three arms — those are the probes designed to
separate "the model knew anyway" from "the library kept it from a confident mistake."
