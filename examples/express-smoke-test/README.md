# Example output: expressjs/express smoke test (2026-07-02)

Real, unedited output of skill-library-builder run against a fresh `--depth 300` clone of
[expressjs/express](https://github.com/expressjs/express) by an agent with no prior context,
in unattended mode (`approve=auto`), scoped to 3 skills for the smoke test.

What the pipeline did on its own:

- **Classification**: application/library (rule 3) — monorepo and data/notebook rules
  correctly rejected first.
- **Admission test killed 5 of 10 candidates** (config-and-flags: 0 config variables found;
  failure-archaeology: only 2 documented incidents, folded into debugging-playbook;
  run-and-operate: README-level evidence only; release/domain-reference: no evidence) —
  the anti-padding rule working as designed on a small-core repo.
- **Field discovery**: the very first full `npm test` on Windows hit a real flaky failure
  ("should 404 when URL too long", 2000ms timeout) that passed in isolation and on re-run —
  it became trap T1 and the worked example in the debugging playbook, with all three runs'
  captured output quoted.
- **History mining**: the reverted CVE-2024-51999 security patch surfaced as trap T5
  ("do not trust a 'sec:' commit is live"), quoted from `git log`, with the unexplained
  revert explicitly marked `[INFERRED]` for re-verification.
- **Verification stats**: 12 of 13 published commands executed with captured output; 1
  tagged `[UNVERIFIED-CMD]` with reason; 43 `[VERIFIED]` / 1 `[INFERRED]` markers across the
  3 skills. Lint gate R1 caught one unmarked claim; it was fixed from ledger evidence.

Files here are the generated `SKILL.md`s (flattened: `<name>.SKILL.md`) plus the probe set.
In a real run they live at `<repo>/.claude/skills/<name>/SKILL.md`, and all approved skills
(5 here) would be authored, followed by gates R2–R6 and the eval phase.
