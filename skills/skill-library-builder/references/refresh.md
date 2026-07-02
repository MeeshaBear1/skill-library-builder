# Lifecycle: manifest, refresh, only:<skill>, audit

A one-shot library rots. A stale skill in authoritative runbook voice misleads a weaker model
MORE than no skill — it inverts the library's purpose. The manifest makes staleness detectable
and regeneration surgical.

## Manifest

`.claude/skills/.skill-library/manifest.json`, written during Phase 4 (as each skill is
authored — never reconstructed later):

```json
{
  "builderVersion": 2,
  "generatedAt": "2026-07-02",
  "headSha": "<git rev-parse HEAD at generation>",
  "scope": ".",
  "excludes": ["vendor/**"],
  "skills": {
    "<skill-name>": {
      "sources": ["src/billing/", "package.json", ".github/workflows/ci.yml"],
      "generatedAt": "2026-07-02",
      "headSha": "<sha>",
      "fileHash": "<git hash-object .claude/skills/<name>/SKILL.md>",
      "referenceFiles": ["references/incidents.md"]
    }
  },
  "probes": ".claude/skills/.skill-library/probes.md"
}
```

`sources` = the files/dirs whose change invalidates this skill. Choose them at authoring time
from the ledger citations — every `[VERIFIED: file:...]` source belongs in the list.
`fileHash` uses `git hash-object <file>` (portable, no extra tooling) — recompute and update
after any gate-driven fix in Phase 5.

## refresh mode

0. No manifest found → tell the user; offer `init` instead. Never guess provenance.
1. Read the manifest. Run `git rev-parse HEAD`; if equal to `headSha`, report "no drift" and
   stop (still run step 5's hand-edit check — edits happen without commits too).
2. Drift set: `git diff --name-only <manifest headSha>..HEAD`, filtered by scope/excludes.
3. Affected skills = manifest skills whose `sources` intersect the drift set (prefix match
   for directories).
4. Orphan check: any skill whose sources were DELETED in the drift set → do not regenerate on
   momentum. Present to the user: subsystem gone → propose deleting the skill; subsystem
   moved → remap sources and regenerate.
5. Hand-edit check, per affected skill (and per unaffected skill, cheaply): recompute
   `git hash-object` on the skill files; mismatch vs manifest `fileHash` = a human edited it.
   NEVER silently overwrite a hand-edited skill: diff manifest-era content vs current, present
   the conflict, and merge the human's changes into the regenerated version explicitly
   (their content wins where the repo doesn't contradict it).
6. Regenerate ONLY affected skills: re-run the pipeline scoped to them — targeted census on
   their sources (census.md procedure, restricted), re-author (authoring.md, all contracts
   apply), then gates R1, R2, R4, R5 on the touched skills; R3 (trigger matrix) only if any
   description changed. Update each regenerated skill's manifest entry.
7. Report: drifted files → affected skills table, orphans flagged, hand-edit conflicts and
   resolutions, gate results, new headSha. Recommend re-running the probe set (evals.md) as
   the library's regression suite.

## only:<skill-name> mode

Force-regenerate one skill regardless of drift: steps 5–7 of refresh, restricted to that
skill. Use when a skill is known-wrong. If its name is not in the manifest → offer init-style
authoring of a single new skill (admission test still applies — taxonomy.md).

## audit mode (read-only; writes nothing)

The month-2 health check, cheap enough to run monthly or in CI:

1. Manifest exists? Every manifest skill directory still present? Every `.claude/skills/*/`
   directory represented in the manifest? Mismatches → report.
2. R1 mechanical lint over every skill (review.md) — catches hand edits that broke format.
3. Staleness: drift set vs each skill's sources (steps 2–3 above) → "stale" list with the
   drifting files named.
4. Sample re-verification: for each stale skill, run its re-verification one-liners
   (Tier 1–2 only) and diff against recorded observations.
5. Hand-edit inventory via fileHash comparison.
6. Report: healthy / stale (with drift evidence) / broken (lint failures) / orphaned /
   hand-edited — plus the single recommended action for each (usually `refresh`).

Audit changes NOTHING — it is safe to run unattended and is the mode to schedule.

## Month-2 ritual (put this in the final report, verbatim)

> Monthly, or after any large merge: run the skill-library-builder in `audit` mode. If it
> reports stale skills, run `refresh`. After refresh, re-run the probe set with your target
> model. Total cost: minutes. Skipping it converts your library from an asset into a
> liability at whatever speed your repo changes.
