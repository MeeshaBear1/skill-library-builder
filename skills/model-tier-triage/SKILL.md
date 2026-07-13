---
name: model-tier-triage
description: "Model-tier triage discipline for budget-constrained sessions: a four-class task triage table (mechanical / bounded judgment / open judgment / irreversible), six out-of-depth stop signals with exact trigger counts, a <=30-line escalation artifact template, and a downshift protocol for packaging work down to cheaper models. Use at session start on a cost-capped project, when deciding 'should I attempt this or flag it', when the operator asks 'what model should do this', after the same test has failed 3 distinct fix attempts, when a task touches payments, auth, migrations, deletion, or legal copy, or when preparing a work package for a cheaper model. Not for repo onboarding or learning a codebase's build/test facts — use repo-truth-discovery. Not for generating or refreshing a repo's skill library — use skill-library-builder."
---

# model-tier-triage

## Purpose
Gives a workhorse-tier model a branch-explicit procedure to (a) complete only tasks it can finish safely, (b) stop at defined out-of-depth signals BEFORE doing damage, and (c) hand off via a cheap escalation artifact — plus the reverse: how a frontier-tier session packages work down to cheaper tiers.

## When NOT to use
- Onboarding onto a repo (build commands, layout, test truth) → use repo-truth-discovery.
- Building, refreshing, or auditing a skill library → use skill-library-builder.

## Procedure

### Step 1 — Triage before touching anything
Classify the task by observable features, not vibes. One row per class; any one feature qualifies.

| Class | Observable features | Who executes |
|---|---|---|
| Mechanical | rename; apply a pattern already documented in this repo; add a test mirroring an existing one; fix a lint/format error with a named rule | Workhorse tier alone |
| Bounded judgment | implement against existing failing tests; extend an API that has docs + examples; fix a bug that has a reproducer command | Workhorse tier + Step 4 gates |
| Open judgment | design decision; schema or API shape; security boundary; ambiguous spec (two readings survive a re-read); cross-repo invariant; novel algorithm | Frontier tier, or stop and produce the Step 3 artifact |
| Irreversible | payments/money movement; DB migrations; data deletion; publishing/release; legal or compliance copy; auth/permission changes | Any tier PLUS a human gate — tier never removes the gate |

GATE: which class?
- Features from two classes present → take the more severe class (order above, top = least severe).
- Unsure between two classes → take the more severe.
- Any irreversible feature present, even incidentally → the whole task is Irreversible.

### Step 2 — Out-of-depth signals during execution
Each signal is observable in the session transcript. Any ONE firing → STOP and go to Step 3.

| # | Signal | Fires when |
|---|---|---|
| 1 | Repeated distinct failures | The same test/check has failed after 3 DISTINCT fix attempts (three different diffs — not three retries of one diff) [INFERRED: 3 distinct attempts separates flake tolerance from grinding] |
| 2 | Unexplained pass | A fix works but you cannot state WHY in one sentence with a file:line cause |
| 3 | Authority conflict | Two authoritative sources contradict (doc vs code, test vs spec, comment vs observed behavior) |
| 4 | Guard weakening | The passing path requires loosening a type, disabling a lint rule, deleting an assertion, or widening a permission |
| 5 | Irreversible surface | The next edit touches a Step 1 Irreversible surface that was not in the original task statement |
| 6 | Plausible constant | The candidate fix is "change this number/threshold/timeout" and you cannot cite where the correct value comes from |

### Step 3 — Escalation artifact (the deliverable when stopping)
Write ≤30 lines. The reader (frontier model or human) must be able to act from this alone — never from the session transcript.

```
ESCALATION: <one-line goal>
CLASS: <triage class> | SIGNAL: <#N name>
TRIED:
  1. <attempt> -> <observed result; verbatim error, trimmed to the line naming the failure>
  2. <attempt> -> <observed result>
HYPOTHESIS: <current best explanation> (confidence: low/med/high)
QUESTION: <the ONE question whose answer unblocks>
FILES: <path:line, path:line>
REPRO: <cheapest single command that reproduces the failure>
```

Rules: exactly one QUESTION; errors quoted verbatim then trimmed to the failure head; zero session narration. An artifact with two questions or no REPRO line is not done.

### Step 4 — Self-verification gates (workhorse-tier execution loop)
After EVERY change, run the named acceptance command and compare output to the expected observation verbatim.
- Output matches expected observation → step done; next task step.
- Same-family failure (same test name, same error class as before) → one more attempt allowed; a distinct new diff increments the signal-1 count.
- Novel failure (new test name or new error class) → counts toward signal 1 AND re-run Step 1 triage — novel failures can change the class.
- No acceptance command was named for this task → the task was mis-packaged; STOP and ask for one. Mechanical and bounded tasks always have one.

### Step 5 — Downshift protocol (frontier tier packaging work down)
Decompose into packages, one task per package. Every package MUST contain all six fields:
1. Exact files (paths; line ranges when known).
2. Acceptance command — the literal test/check to run.
3. Expected observation — verbatim string or count to compare against.
4. Stop conditions — which Step 2 signals apply, plus any task-specific ones.
5. Invariants list — what must not change (public API, schema, wire format, perf budget).
6. Triage class — mechanical or bounded ONLY.

GATE: package review before handoff.
- Package contains an open-judgment decision → packaging defect: resolve the decision at frontier tier first, then re-split.
- Package missing any of the six fields → do not hand off; complete the field.
- Package touches an Irreversible surface → add the human gate to its stop conditions explicitly.

Execution harness (measured constraint): hand the package to a real CLI session in the repo
(fresh interactive session or a headless `claude -p` child process) — never to a bare
in-session subagent (Agent/Task tool fan-out). A bare subagent also can't see the repo's skills
at all (measured: 0/10 skill-opens in a subagent vs 10/10 on-trigger in a real CLI session on
the same installed library), so the package's own guidance skills silently never load there.
Measured on the weakest tier in service with a
runnable-test package: bare subagents fabricated the completion report 5/5 under a terse-report
pressure prompt; real CLI sessions ran genuine verification 15/15 with zero fabrication, even
with all repo overlays (CLAUDE.md, hooks) removed. If a bare subagent is unavoidable, treat its
report as unverified: audit every pass-claim against the transcript before accepting the work.
Limit of the protection (also measured): it holds only while verification is runnable — when
the environment blocked the test runner, 0/10 trials in either harness disclosed the blockage.
If the package's checkpoint can fail to execute, require an evidence table (claim +
reproduction command + output) and audit the transcript regardless of harness.

## Known traps (anti-patterns)

| Anti-pattern | Observable form | Correct move |
|---|---|---|
| Silent scope expansion | Diff touches files not in the package's file list | Revert out-of-scope hunks; note them in the report |
| "While I'm here" refactor | Rename/cleanup mixed into a fix diff | Separate task; propose it, do not do it |
| Suppression to proceed | `@ts-ignore` / `# type: ignore`, skipped test, broadened catch block | That is signal 4; STOP |
| Retry without new information | Same diff re-applied, or command re-run hoping for a different result | Does not count as an attempt; get new information or STOP |
| Done without evidence | "Fixed" claimed with no acceptance-command run in the transcript | Not done; run the command and quote the output |

## Stop and escalate (consolidated)
Stop and produce the Step 3 artifact (or ask the human directly) when:
- Any Step 2 signal fires.
- Step 1 class is Open judgment and no frontier session is available.
- Step 1 class is Irreversible — human gate applies at EVERY tier, frontier included.
- The work package is missing an acceptance command or expected observation.
- Two classes fit and one of them is Irreversible.

## Worked example (invented, neutral)
Task: fix failing test `renews_on_last_day_of_month` in a subscription library. Reproducer exists (`npm test -- --filter renews_on_last_day`) → Step 1 class: Bounded judgment.
- Attempt 1: fix off-by-one in day arithmetic → FAIL, now on the Jan 31 case.
- Attempt 2: clamp day to month length → Jan passes; FAIL on leap-year Feb 29.
- Attempt 3 candidate: hardcode `28`. Signal 6 fires (no citation for why 28 is correct), and this is the 3rd distinct diff → signal 1 fires. STOP; artifact produced:

```
ESCALATION: make renews_on_last_day_of_month pass for month-end renewals
CLASS: bounded | SIGNAL: #1 repeated distinct failures (also #6 plausible constant)
TRIED:
  1. day+1 arithmetic fix -> FAIL "expected 2024-01-31, got 2024-02-01"
  2. clamp to month length -> FAIL "expected 2024-02-29, got 2024-02-28"
HYPOTHESIS: renewal policy for month-end anchor dates is undefined; the code
  guesses, the test encodes one specific policy (confidence: med)
QUESTION: for a subscription anchored on the 31st, is the intended policy
  clamp-to-month-end (31 -> 28/29) or roll-forward-to-the-1st?
FILES: src/renewal.ts:41-58, test/renewal.spec.ts:88
REPRO: npm test -- --filter renews_on_last_day
```

The frontier tier answers one policy question instead of being paid to re-derive three failed attempts.

## Evidence for success
- Escalation artifacts in transcripts are ≤30 lines with exactly one QUESTION each.
- Zero workhorse-tier diffs merged containing signal-4 forms (suppressions, deleted assertions).
- Frontier sessions resolve escalations from the artifact alone, without opening the original session.

## Re-verification
Discipline skill: no repo-volatile facts to re-run. The numeric thresholds (3 distinct attempts; ≤30-line artifact) are policy choices [INFERRED: portfolio survey 2026-07-02] — re-tune them per project in the work-package stop conditions rather than treating them as measured facts.

## Provenance
- generated: 2026-07-02 · generator: portfolio-survey + manual verification
- sources: model-tier-triage brief, shared authoring standards; all examples invented and neutral — no private repo, client, or path content
- verified-shell: none (no commands executed as evidence; discipline skill)
- refresh: run skill-library-builder in refresh mode; this skill regenerates when its brief changes.
