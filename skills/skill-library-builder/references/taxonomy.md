# Phase 3: Taxonomy — which skills to build

The skill count is an OUTPUT of the admission test, never a target. Padding a library is worse
than a small library: every extra skill's description is permanently loaded into every session
in the repo, dilutes the weaker model's trigger discrimination, and — when the evidence is
thin — can only be filled by invention, which Iron rules 3–4 forbid.

## Admission test (every candidate must pass ALL THREE)

1. **Trigger moment**: name a concrete coding-session moment when this skill's description
   would fire (a task type, an error string, a file being edited). If you cannot script the
   moment, the skill will never load — drop it.
2. **Evidence floor**: the system map holds ≥5 verified facts/commands/traps for this skill
   that a model would NOT get from reading the README once. Below the floor → merge into a
   sibling.
3. **Failure it prevents**: articulate the specific mistake a weaker model makes WITHOUT this
   skill (wrong command, missed gate, re-introduced bug). If you can't, it's documentation,
   not operating knowledge — drop it.

## Sizing bands (sanity check, not quota)

| Repo class | Typical yield |
|---|---|
| trivial / docs-only | 0 (warrant gate already stopped you) or 1 onboarding skill |
| small single-purpose (< ~10k LOC) | 3–6 |
| typical app/library | 6–12 |
| monorepo / multi-service | 10–20, only with per-unit justification |

Landing far outside the band means re-check the admission test — usually over-splitting
(merge siblings) or under-discovery (one more census pass on the thin area).

## Candidate catalog — with inclusion criteria

Default candidates (build when criteria met):

| Candidate | Include only if |
|---|---|
| `<p>-architecture-contract` | map has real invariants/ownership rules (almost always) |
| `<p>-build-and-env` | repo builds/installs; commands verified in Phase 4 |
| `<p>-test-and-validate` | tests or CI exist. If NEITHER exists: state that absence as a VERIFIED fact inside build-and-env, give a manual smoke procedure labeled [INFERRED], and recommend (never silently create) a harness — do not ship a hollow validation skill |
| `<p>-change-control` | repo has real gates: blocking CI checks, CODEOWNERS, hooks, review rules. A solo repo with no gates gets a note in architecture-contract instead |
| `<p>-run-and-operate` | something runs: service, CLI, app; startup verified |
| `<p>-debugging-playbook` | map's Risks section has ≥3 sourced traps/failure patterns. Absorbs failure-archaeology by default |
| `<p>-failure-archaeology` | SPLIT from debugging-playbook only when ≥3 distinct documented incidents exist with explanatory commit bodies or linked issues — quoted, not narrated |
| `<p>-config-and-flags` | non-trivial config surface (≥8 meaningful variables/flags) |
| `<p>-release-and-versioning` | repo publishes/releases and the process is discoverable |
| `<domain>-reference` | dense domain jargon/invariants that code alone doesn't explain |

Data/notebook repos — replace the app-shaped middle rows with:

| Candidate | Include only if |
|---|---|
| `<p>-data-and-provenance` | datasets with locations, versions, or licensing constraints |
| `<p>-environment-and-kernels` | env/kernel setup is non-obvious (conda, CUDA, kernels) |
| `<p>-pipeline-run-order` | notebooks/stages have a required execution order |

NOT default — include only when the repo's actual day-to-day work includes the activity, with
map evidence: `docs-and-writing`, `research-methodology`, `proof-and-analysis-toolkit`,
`<hardest-problem>-campaign`. Never include: `external-positioning` (marketing knowledge has
no trigger surface in a coding session).

`<p>` = project slug: lowercase, `[a-z0-9-]` only, sanitize (`My_App.Core` → `my-app-core`),
and keep full skill names ≤64 chars — truncate the slug, not the topic.

## Monorepo decomposition

Two-tier structure — never one grab-bag skill spanning 12 services:

- **Repo-level skills**: architecture-contract, change-control — things true everywhere.
- **Per-unit depth**: inside repo-level skills, one reference file per unit
  (`references/<unit>.md`) loaded on demand; OR separate `<unit>-<topic>` skills when units
  diverge strongly (different languages/build systems). Prefer reference files until a unit
  needs ≥3 skills of its own.
- Record the chosen scope per skill in the manifest so refresh can target it.

Scoped runs (`scope` ≠ repo root): classify and size against the scope unit, not the whole
repo; name skills `<unit>-<topic>` (unit slug, sanitized); record the scope in each manifest
entry. A later run on a different scope adds skills alongside — the trigger matrix (gate R3)
must still be run across ALL units' descriptions together.

## Canonical ownership map

Before authoring, assign every knowledge area to EXACTLY ONE skill — write the assignment
into the taxonomy proposal. A fact, command, or trap lives in one skill only; siblings
cross-reference it ("for the fix procedure, load `<p>-debugging-playbook` — covers X") and
never restate it. This is what keeps a later edit from stranding a stale copy. Overlap found
in Phase 5's consistency gate is a taxonomy failure — fix the assignment, not just the text.

## Operator checkpoint (exit gate)

Present a proposal table before authoring anything:

| # | Skill name | One-line scope | Primary evidence (ledger IDs) | Est. size |

Plus: resolved skills root path, the canonical ownership map, anything dropped by the
admission test and why.

At this checkpoint, also write the ANSWER KEY for later gates: assign every probe in
`.claude/skills/.skill-library/probes.md` its `expected primary skill: <name>` from the
canonical ownership map. Review gate R3 and the Phase 6 evals score against this field — it
must exist before authoring begins.

Wait for confirmation. If `approve=auto` was set: log the proposal to state.json
(`proposal` field) and proceed — but still deliver the table in the final report.
This checkpoint costs one message and prevents the most expensive failure in the pipeline:
authoring 10 deep skills from a misread of what the repo is.
