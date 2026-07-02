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
  actual target model.
- **It doesn't rot silently.** Per-skill provenance (HEAD SHA + sources consulted), a manifest,
  and `refresh` / `audit` modes that detect drift via `git diff`, regenerate only affected
  skills, and never clobber hand-edited ones.
- **It's safe to point at private repos.** Redaction rules + a blocking secrets scan; repo
  prose is treated as evidence, never as instructions (prompt-injection laundering defense);
  read-only outside `.claude/skills/`; three-tier command execution policy.

## Install

The builder is a personal skill (available in every repo you open):

```powershell
# PowerShell
Copy-Item -Recurse skills/skill-library-builder "$env:USERPROFILE\.claude\skills\skill-library-builder"
```

```bash
# bash/zsh
cp -r skills/skill-library-builder ~/.claude/skills/skill-library-builder
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
skills/skill-library-builder/
├── SKILL.md                 orchestrator: iron rules, phase pipeline, exit gates
└── references/
    ├── census.md            tool-based discovery, evidence ledger, system map
    ├── taxonomy.md          repo classification, admission test, operator checkpoint
    ├── authoring.md         format/description contracts, branch-explicit style,
    │                        evidence markers, execution policy, redaction
    ├── review.md            six gates: lint, factual, triggers, consistency, secrets, cold-run
    ├── evals.md             probe mining, cold-context run, A/B measurement protocol
    └── refresh.md           manifest, drift detection, refresh / only / audit modes
```

## Provenance

Built 2026-07-02. Design derived from an original spec ("Repository Skill Library Builder")
hardened through a 6-agent adversarial critique panel — 41 findings, all addressed or
consciously rejected in [DESIGN.md](DESIGN.md).
