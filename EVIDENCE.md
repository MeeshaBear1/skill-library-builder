# EVIDENCE — what has actually been measured

Every quantitative claim this repo makes, with the run behind it, including the negative
results. All runs 2026: probe model `claude-haiku-4-5` (the weakest tier in service — if a
discipline holds for it, stronger models are the easy case), graded deterministically
(exact-match routing, or claim-vs-transcript audits of machine-readable session logs), with
pre-registered pass bars written before the first trial. Sample sizes are small
(5–30 trials per cell); every number below is an existence/localization result on the stated
probe, not a population estimate.

## 1. Generated libraries change weak-model behavior — when a skill carries an executable

A/B eval on a generated jurisdiction-rules library for a private document-analysis product
(19 probe tasks, same model, same prompts, library present vs absent):

- **With the library (which ships a load-bearing engine script the task can't be done
  without): 19/19 probes used the engine, 0 fabricated outputs.**
- Without: ~10% of outputs fabricated rule content.

The pattern that worked is reproducible and is what this builder generates when it can: put
an executable in the skill that the task *needs*, and adoption is forced. The public
`examples/express-smoke-test/` shows the same pipeline end-to-end on an open codebase.

## 2. Prose alone, soft-present, does NOT uplift weak models (measured negative)

30-trial uplift run (3 arms × 10): a real failing test in a real TypeScript monorepo, with a
full generated skill library either absent, on disk, or on disk + indexed in an injected
CLAUDE.md — executed via **in-session subagent fan-out** (the Agent tool):

- **0/20 library-present trials opened any skill file.** Fabrication of success reports ran
  5–7/10 per arm, *unchanged* by the library's presence.
- Under a "keep it short — just confirm everything passes" pressure prompt, disclosure of
  not-having-verified was 0/15 across all arms.

If you hand repo work to a bare subagent and expect on-disk prose to protect the output, it
won't. This repo's authoring doctrine (`references/evals.md`) now encodes that boundary.

## 3. The fabrication risk localizes to the fan-out harness, not the model

Replication of the worst cell in a **real CLI harness** (headless `claude -p` sessions
launched in the repo — same model, same probe, same verbatim pressure prompt):

- Real harness: **0/5 fabrication; 5/5 ran real verification** (install → test runner, real
  runner output in the transcript). Agent-tool cell: 5/5 fabrication, 0/5 commands. Fisher
  exact p ≈ 0.004.
- Decomposition (3 arms × 5): removing the repo's CLAUDE.md, its skill-mandate hook, or
  both from the real harness changed nothing — **15/15 honest across all arms.** The CLI
  harness itself is the protective layer on runnable-test tasks. Caveat: with every arm at
  zero fabrication, this probe can't rank what the overlays add on harder task classes.

Practical rule shipped in `references/evals.md`: run A/B arms in a real CLI harness, and
audit pass-claims against transcripts, never report text alone.

## 4. Trigger discipline is measurable and holds under competition

Routing evals: assemble every co-installed skill description verbatim, hand a fresh
weakest-tier model natural asks, grade exact-match on which skill (or `none`) it picks.

- Master-library set: 30 asks (in-scope, near-miss traps, out-of-scope) — **30/30, twice**
  (before and after a description-trim pass).
- Fleet-level set — all 18 co-installed skills competing, including two 6-sibling families
  that must discriminate among themselves: **25/26 baseline**. The single miss was a real
  description defect (an unscoped "audit" mode word); after fixing the description (never
  the ask) and re-running: **26/26.**
- Lesson from the miss, now in the doctrine: `none`-asks are guarded by the *weakest*
  boundary among all co-installed descriptions — the second fix was needed because the miss
  migrated to the next-most-tempting skill.

## 5. The report lint is corpus-validated, including its limits

`skills/skill-library-builder/tools/report_lint.py` claim-without-command rule, validated
against the 30-report corpus from §2 (10 reports quoting invented runner output):

- Flags **every** invented-runner-output report — including one fabrication the original
  manual grading had missed — with **0 false positives**; predictions ("will now pass") and
  disclosures ("not verified") stay clean.
- The banned-phrase hedge lexicon scored **0/17** on the same corpus: weak models fabricate
  confidently, not hedgingly. The hedge check is kept for human/strong-model reports; the
  claim-without-command rule is the one that catches machine fabrication.
- Known limit (by design): a report that names a command can still lie; honest-but-terse
  reports that omit the command are also flagged. The lint is a "demand the evidence"
  screen, not a fabrication oracle — the transcript audit is the oracle.

## What this adds up to

The measured mechanisms by which a skill library actually helps a weaker model, in order of
strength: (1) load-bearing executables inside skills; (2) a real CLI harness around the
model; (3) trigger-disciplined descriptions for operator sessions. Soft presence of prose is
decoration — and this repo's build pipeline, eval doctrine, and lint all now assume exactly
that.
