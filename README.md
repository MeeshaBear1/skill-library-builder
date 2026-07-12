# skill-library-builder

A Claude Code skill that turns a real repository into a **project-specific skill library**:
verified runbooks, architecture contracts, debugging playbooks, and change-control skills
written into the repo's `.claude/skills/`.

**Why:** frontier models re-derive a repo's operating knowledge every session; weaker/cheaper
models often can't. A disciplined, *verified* skill library carries that knowledge —
architecture invariants, real commands with real observed output, known traps, decision gates —
so that Opus- and Sonnet-class agents perform closer to frontier level on the repos you care
about. This is the leverage point: skills can't upgrade a model's reasoning, but they can
delete most of the judgment calls where weaker models lose.

## What makes this different from "generate docs"

- **Nothing unexecuted gets published.** Every command in a generated skill was either run
  (with its real output captured and quoted) or is explicitly tagged `[UNVERIFIED-CMD: reason]`.
- **Every load-bearing claim carries a marker** — `[VERIFIED: file:line]`,
  `[VERIFIED: cmd @ date]`, or `[INFERRED: basis]`. Review greps for them.
- **Review is not self-review.** Factual verification, trigger-discrimination, and the
  cold-context usability run happen in fresh subagent context against the actual repo.
- **Skill count is an output, not a target.** An admission test decides what ships; a repo
  that doesn't warrant a library gets told so.
- **Descriptions are engineered, then tested.** A trigger-matrix gate proves each realistic
  task routes to exactly one skill — because the description is the only thing that decides
  whether knowledge ever reaches the model.
- **It measures itself.** Task probes mined from the repo's real history, a cold-context probe
  run at build time, and an A/B protocol (library present vs renamed away) you run with your
  actual target model. Every quantitative claim this repo makes — including the negative
  results — is in [EVIDENCE.md](EVIDENCE.md), with the run behind it.
- **Reports get linted, not trusted.** `skills/skill-library-builder/tools/report_lint.py`
  mechanically screens agent completion reports: success asserted with no reproduction
  command anywhere is a finding (corpus-validated against real fabricated reports — see
  EVIDENCE.md §5).
- **It doesn't rot silently.** Per-skill provenance (HEAD SHA + sources consulted), a manifest,
  and `refresh` / `audit` modes that detect drift via `git diff`, regenerate only affected
  skills, and never clobber hand-edited ones.
- **It's safe to point at private repos.** Redaction rules + a blocking secrets scan; repo
  prose is treated as evidence, never as instructions (prompt-injection laundering defense);
  read-only outside `.claude/skills/`; three-tier command execution policy.

## What's in this repo — two tiers

**Tier 1 — the generator.** `skill-library-builder` is a pipeline you point at a repo; it
discovers, verifies, and writes that repo's own skill library. Its output is project-specific
and stays in the target repo.

**Tier 2 — standalone companion skills**, included here and usable by anyone directly:

- **`repo-truth-discovery`** — a branch-explicit recon procedure for finding where a repo's
  truth actually lives before touching code: README trust test, doc-of-record sweep
  (DECISIONS.md, PROGRESS.md, `.planning/`), pivot/squash history probes, an empty-repo
  protocol (check the remote before you scaffold), and a supersession check. Distilled from
  a survey of 84 real repos where trusting the README was the #1 cheap-model failure.
- **`model-tier-triage`** — the economics skill: a four-class task-triage table, six
  out-of-depth stop signals with exact trigger counts, a ≤30-line escalation artifact so the
  expensive model answers one crisp question instead of un-burying a mess, and a downshift
  protocol for packaging work for cheaper models. Built for the world where frontier-tier
  tokens are the scarce resource and workhorse models do the daily driving.

There is a third tier this repo deliberately does NOT contain: your own private fleet skills
(cross-repo family maps, business-specific convention contracts). The builder and the two
companions are the public halves; knowledge specific to your repos belongs in your own
`~/.claude/skills`, generated with the tools above.

## Install

All three are personal skills (available in every repo you open):

```powershell
# PowerShell (idempotent: creates the skills dir if missing, replaces any prior install)
New-Item -ItemType Directory -Force "$env:USERPROFILE\.claude\skills" | Out-Null
foreach ($s in 'skill-library-builder','repo-truth-discovery','model-tier-triage') {
  if (Test-Path "$env:USERPROFILE\.claude\skills\$s") { Remove-Item -Recurse -Force "$env:USERPROFILE\.claude\skills\$s" }
  Copy-Item -Recurse "skills/$s" "$env:USERPROFILE\.claude\skills\$s"
}
```

```bash
# bash/zsh (idempotent)
mkdir -p ~/.claude/skills
for s in skill-library-builder repo-truth-discovery model-tier-triage; do
  rm -rf ~/.claude/skills/$s && cp -r skills/$s ~/.claude/skills/$s
done
```

The libraries it *generates* are project skills, written to the target repo's
`.claude/skills/` — commit them so your whole team (and every agent session) gets them.

## Use

In Claude Code, inside the target repository:

- `Build a skill library for this repo` → init mode (census → map → taxonomy checkpoint →
  verified authoring → six review gates → eval probes → report)
- `Refresh the skill library` → regenerates only skills whose sources changed since generation
- `Rebuild the acme-debugging-playbook skill` → `only:<name>` mode
- `Audit the skill library` → read-only health check (stale/broken/orphaned/hand-edited)
- Add `run unattended` to skip the taxonomy checkpoint (`approve=auto`)

Works best when run by a strong model (the builder does discovery, verification, and
authoring); the *output* is optimized for consumption by weaker models.

## Layout

```
skills/
├── skill-library-builder/   Tier 1: the generator
│   ├── SKILL.md             orchestrator: iron rules, phase pipeline, exit gates
│   └── references/
│       ├── census.md        tool-based discovery, evidence ledger, system map
│       ├── taxonomy.md      repo classification, admission test, operator checkpoint
│       ├── authoring.md     format/description contracts, branch-explicit style,
│       │                    evidence markers, execution policy, redaction
│       ├── review.md        six gates: lint, factual, triggers, consistency, secrets, cold-run
│       ├── evals.md         probe mining, cold-context run, A/B measurement protocol
│       └── refresh.md       manifest, drift detection, refresh / only / audit modes
├── repo-truth-discovery/    Tier 2: standalone recon procedure
│   └── SKILL.md
└── model-tier-triage/       Tier 2: standalone tier-economics discipline
    └── SKILL.md
```

## Example output

[examples/express-smoke-test/](examples/express-smoke-test/) — real, unedited skills the
builder generated against a fresh clone of expressjs/express, including a debugging playbook
whose traps came from captured flaky-test output and quoted revert history (a reverted CVE
patch, correctly flagged `[INFERRED]` where the repo records no cause).

## Provenance

Built 2026-07-02. Design derived from an original spec ("Repository Skill Library Builder")
hardened through: a 6-agent adversarial critique panel on the spec (41 findings → DESIGN.md),
a 29-agent adversarial review of the built files (23 confirmed defects, all fixed), and a
live smoke test against expressjs/express (15 friction items, all fixed — including two
would-be-fatal ones: silent empty-Glob-on-dot-directories misreads and the unattended
dependency-install deadlock).

The Tier-2 companion skills were added the same day: authored from an 84-repo portfolio
survey (patterns generalized, all private content stripped), then passed through the same
gate stack — fresh-context factual verification (every quoted command output reproduced,
one wrong git error message caught and fixed), a 10-probe trigger-discrimination matrix
(10/10 routed correctly), banned-verb lint, and a blocking secrets + privacy scan
(zero hits).
