# Phase 6: Evals — measuring whether the library actually helps

The library's purpose is a measurable lift for weaker models on this repo. This phase produces
the measurement instrument and runs the first reading. Without it, a plausible-looking library
and a working library are indistinguishable — and plausible-looking is the default failure.

## Probes (mined in Phase 1, expected skill assigned at the Phase 3 checkpoint, finalized here)

`.claude/skills/.skill-library/probes.md` holds 5–10 probes. By now each already carries its
`expected primary skill` (assigned from the ownership map in Phase 3 and used by gate R3).
Finalize each to this schema:

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

Probe-design lessons (measured, from the two A/B runs of 2026-07-10/12 — an INCONCLUSIVE
smoke test followed by a conclusive 64-trial eval):
- **Target knowledge gaps, not reasoning.** A weak model reasons adequately; it fails on
  repo facts and house discipline it cannot derive. Any probe a capable model answers
  unaided from general knowledge measures nothing — that is exactly how the first run went
  INCONCLUSIVE (B ≈ A everywhere, library pure overhead).
- **Grade fabrication and variance, not just success/fail.** Repeat the same probe N times:
  hard-fabrication rate (specific numbers/claims with no source) and answer variance across
  identical runs separated the arms decisively when success-rate could not.
- **Library soft-present, never mandated.** Have the library on disk and say nothing about
  it. A "read the skill first" arm measures neither trigger fidelity nor real uplift — and
  overstates the library's day-to-day value.
- **Include one adversarial-pressure variant.** Demand the wrong-but-easy behavior ("file it
  today", "just confirm it passes") and grade whether the model disclosed limits instead of
  complying. Disclosure-under-pressure was the strongest observed separator between arms.
- **Firing is not uplift — probe conflict-resolution, not discovery.** A skill can open 10/10
  on-trigger and still not improve the OUTPUT. Measure it with a *poisoned-doc* probe: plant
  ONE stale command in the README (real command lives only in the manifest) and grade whether
  the model ships the stale one. Measured (2026-07-12, output-quality A/B): the model opened
  the manifest 11/11 in BOTH the skill and no-skill arms, yet 30–70% still shipped the poisoned
  README command — **reading the authoritative source ≠ preferring it on conflict.** The skill
  gave only a directional, non-significant lift (7/10 vs 3/10 correct, Fisher p ≈ 0.18); its
  win, when it came, was explicit doc-vs-manifest flagging. Lesson for content: teach the skill
  to prefer the manifest over prose on conflict, not merely to open it — and don't count an
  "opened the right file" transcript signal as success; grade the answer. **The fix, then the
  regression:** the skill was taught "a command is a claim — verify vs the manifest, prefer it
  on conflict", and the same probe re-run at 30/arm went **26/30 (patched skill) vs 10/30 (no
  skill), Fisher p ≈ 5e-5** — the bar cleared, 12/13 skill trials debunking the decoy in the
  new rule's own words. That is this phase's whole point: the eval diagnosed a content gap, the
  fix closed it, the re-run proved it. Prose that just fires gave p ≈ 0.18; prose that resolves
  the conflict gave p ≈ 5e-5.

- **Bury the fence at real-world depth — a both-arms ceiling is a fixture bug, not a
  verdict.** Measured (2026-07-13, planted Chesterton's-fence A/B for a history-archaeology
  skill): with the guard's justification visible in a commit SUBJECT line, both arms hit
  10/10 (Fisher p = 1.0) — the unaided model already runs `git log --oneline`, so the probe
  measured baseline behavior. Re-planted at the depth where such reasons actually hide
  (commit body only, blame owned by a later cosmetic commit, natural deletion pressure in
  the ask), the unaided arm deleted the load-bearing guard 7/10 and cited the real reason
  0/10, while the skill arm kept 10/10 and cited 10/10 (primary p ≈ 0.0031, citation
  p ≈ 1.1e-5). Publish the ceiling run as its pre-registered negative, then fix the FIXTURE
  in a v2 — never quietly re-roll it. Corollary: grade *grounded* success separately from
  lucky success — the shallow run's "keeps" included plausible guesses that never touched
  history (fabricated intent that happened to land right).

`probes.md` lives outside any skill directory ON PURPOSE: it must never load into consumer
sessions or add a trigger description.

## Cold-context run (this build, done by the builder)

Already partially done as review gate R6. Complete the set here: fresh subagent, repo +
library, one probe at a time, ≥2 probes total (more if gates R3/R6 forced skill rewrites).

If subagents are unavailable in this session: attempt the probes yourself under the
fresh-inputs constraint (skills + repo only; the ledger and your authoring memory are
off-limits), label every result "self-run, not cold-context" in the final report, and state
that the operator A/B protocol below is the authoritative measurement in that case.

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

**Harness boundary (measured; do not skip this):** run both arms in a REAL CLI harness — a
fresh interactive session or a headless `claude -p` child process launched in the repo — never
via in-session subagent fan-out (the Agent/Task tool). The harness difference swamps the
library effect: in our runs, the same weak model on the same probe fabricated success reports
5/5 as a bare in-session subagent and 0/15 in headless CLI sessions, with the library constant.
An A/B run through bare subagents measures the fan-out harness, not your library. Worse, the
bare-subagent harness does not even surface your skills to the child: in a real CLI harness on
a repo with an installed library, a soft-present (un-indexed) skill was spontaneously invoked
on a trigger-matching ask 10/10 and 0/10 on a non-matching ask, whereas the same class of
library soft-present in bare subagents opened 0/20 — so an A/B through subagents measures an
*invisible* library, not a decorative one. Corollary
for grading any arm: never trust the report text alone — audit pass-claims against the
transcript (was the named command actually run, is the runner output real?), or mechanically
pre-screen reports with `tools/report_lint.py` (claim-without-command rule) and audit what it
flags.

Boundary of the boundary (also measured): the harness protects only while verification is
RUNNABLE. On a blocked-verification variant of the same probe (test-runner dependency
sabotaged), 0/10 trials in either harness disclosed the blockage under a keep-it-short
prompt — the honest trials were exactly the ones that repaired the environment and really
ran. If a probe's checkpoint can be blocked, grade disclosure explicitly and require the
`--completion` evidence table, which flags a report that cannot name its reproduction.

**Discarding a flaky trial: outcome-blind exclusion only.** Real A/B trials die of
environment problems (checkout fails, dependency install times out, the harness itself is
killed). The tempting mistake is to re-roll "the trials that obviously broke" — which in
practice means re-rolling failures, silently inflating whichever arm you re-rolled. The
rule: a trial may be excluded ONLY on evidence that is independent of the model's output —
gathered before the model ran (checkout, setup, environment sanity) or about the harness
itself (killed by a signal). Never exclude on the answer's quality, and never exclude
"because it failed"; a timeout is a behavioral outcome (a model can hang), not an
environment fault. Every exclusion carries a receipt (which rule, what evidence) in the
report, and ambiguity resolves toward INCLUSION. A passing trial with invalidated
environment evidence is excluded just the same — that is what keeps the exclusion honest.

## Interpreting failures (route, don't gloss)

| Symptom | Diagnosis | Route |
|---|---|---|
| expected skill never loaded | trigger/description failure | authoring.md description contract + R3 |
| skill loaded, model still failed | content failure: missing branch, wrong observation, judgment call left open | authoring.md procedure style + R6 |
| model succeeded ignoring skills | probe too easy OR skill redundant | replace probe; reconsider skill admission |
| model followed skill into an error | factual failure — a claim survived review wrongly | R2 on that skill, then fix |

Eval failures during this phase are BUILD failures: fix and re-run the affected gate — under
review.md's fix protocol (R1 + R2 delta on the changed text; a final R5 re-run before Phase 7
whenever content changed after R5 first passed). Only gloss-free results go in the final
report.
