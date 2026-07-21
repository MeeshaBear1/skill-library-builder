# Mode: improve — observed-job harness improvement

Adapted from the improve-harness loop in lopopolo/harness-engineering (playbooks/improve-harness.md,
adopted 2026-07-21). Use this mode when a REAL job stumbled — an agent run on this repo failed,
looped, needed human rescue, or produced work that was rejected — and the suspected cause is a gap
in the skill library (missing skill, stale claim, bad trigger, unresolved judgment call). This mode
improves exactly one skill-shaped gap in response to exactly one observed trajectory. It is not a
broad audit (use `audit`) and not staleness maintenance (use `refresh`).

All Iron rules from SKILL.md apply. Additional rule for this mode: **never make a comparative claim
("the library is better now") without the paired rerun in step 5.** A change without a fresh rerun
is recorded as `unproven`, not as an improvement.

## The loop

> baseline → earliest gap → smallest owning intervention → native verification → fresh rerun →
> retain, revise, or remove

Run it once per invocation. One job, one gap, one intervention. If the baseline reveals several
gaps, record the others in the report and fix only the earliest one — the one the trajectory hit
first — because later failures may be downstream of it.

## Step 0: Record the job contract

Before touching anything, write `.claude/skills/.skill-library/improve/<date>-<slug>/contract.md`:

```text
Target repo and revision (git SHA):
Fixed worker (model + agent config the job ran under):
Representative job (the user request, verbatim or faithfully summarized):
Accepted outcome (what "done" meant to the requester):
Evidence that proves the outcome (command, test, artifact — must be observable):
Authority envelope (what this improvement run may read/write; skills dir + build dir only):
Budget and stop conditions (max time/attempts before stopping and reporting):
Suspected harness gap (one sentence — which skill, or which absence):
```

If you cannot fill "Evidence that proves the outcome" with something observable, stop: the job is
not bounded enough for this loop. Narrow it with the user first.

## Step 1: Observe the baseline

Prefer the existing failed trajectory (transcript, PR review comments, correction notes) over a
fresh run — it is free and it already happened. Run the job fresh only when it is safe, cheap, and
authorized. Record observable evidence, not a vibe summary:

- Was the outcome accepted? Which proof did the worker produce?
- Which skills triggered? Which SHOULD have triggered and did not (trigger-description gap)?
- Which claim inside a triggered skill was wrong, stale, or unresolved (content gap)?
- Where did a human relay facts the library should have carried?
- Retries, abandoned paths, avoidable review cycles.

Classify the gap before intervening: **missing capability** vs **poor discovery** (skill exists,
trigger missed) vs **missing fact** vs **worker limitation** (no skill fixes it — record and stop;
route to model-tier-triage territory instead of authoring around a model ceiling).

## Step 2: Smallest owning intervention

Fix the earliest gap with the smallest change that OWNS it:

- Trigger miss → edit the description frontmatter only.
- Wrong/stale claim → re-verify against the repo (authoring.md evidence rules) and correct it.
- Missing fact → add it to the existing owning skill; create a new skill only if it passes the
  taxonomy admission test.
- Judgment call the skill punts on → resolve it with a verified rule, or name it explicitly as
  operator-decision — never leave "investigate appropriately".

Show diffs and get confirmation per Iron rule 7. Update the manifest entry (refresh.md) — sources,
hashes, generatedAt — for every skill touched.

## Step 3: Native verification

Verify the changed claims the same way authoring.md requires: execute the commands, capture real
output. A claim fixed without execution keeps its `[UNVERIFIED-CMD]`/`[INFERRED]` marker.

## Step 4: Fresh rerun

Rerun the SAME representative job from the contract, cold-context, ideally on the same weaker
model the library targets. Judge it only against "Accepted outcome" + "Evidence" from the
contract. Do not widen the job, weaken the acceptance, or grade your own summary as proof.

## Step 5: Retain, revise, or remove

- Rerun closed the job → **retain**. Record before/after evidence in the report.
- Rerun improved but did not close → **revise**: either loop once more within budget, or stop and
  report the next earliest gap.
- Rerun unchanged or worse → **remove** (revert the intervention) and record the negative result —
  a reverted wrong guess is a success of the loop, not a failure.

## Report

Deliver: the contract; baseline evidence; gap classification; the diff; verification output;
rerun outcome (retain/revise/remove/unproven); and any additional gaps observed but not fixed.
Write it to the improve dir alongside contract.md. If the repo has a golden/eval harness, note
whether this job should become a new probe or golden so the gap stays closed.
