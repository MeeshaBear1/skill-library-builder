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
  "generatedAt": "<today's date>",
  "headSha": "<git rev-parse HEAD at generation>",
  "scope": ".",
  "excludes": ["vendor/**"],
  "skills": {
    "<skill-name>": {
      "sources": ["src/billing/", "package.json", ".github/workflows/ci.yml"],
      "generatedAt": "<today's date>",
      "headSha": "<sha>",
      "files": {
        "SKILL.md": "<git hash-object .claude/skills/<name>/SKILL.md>",
        "references/incidents.md": "<git hash-object .claude/skills/<name>/references/incidents.md>"
      }
    }
  },
  "probes": ".claude/skills/.skill-library/probes.md"
}
```

`sources` = the files/dirs whose change invalidates this skill. Choose them at authoring time
from the ledger citations — every `[VERIFIED: file:...]` source belongs in the list.
`files` = EVERY file the skill ships (SKILL.md plus each reference file), each with its own
`git hash-object` hash (portable, no extra tooling). Recompute and update all of a skill's
hashes after any builder-made fix in Phases 5–6 — builder edits must never later misclassify
as human edits.

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
   `git hash-object` for EVERY file in the skill's manifest `files` map — SKILL.md AND each
   reference file. A mismatch in ANY file marks the whole skill hand-edited. NEVER silently
   overwrite a hand-edited skill: diff manifest-era content vs current, present the conflict,
   and merge the human's changes into the regenerated version explicitly (their content wins
   where the repo doesn't contradict it). In unattended runs (`approve=auto`), hand-edited
   skills are SKIPPED and flagged in the report — never auto-merged.
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

## audit mode (writes nothing to the repo or the library)

The month-2 health check, cheap enough to run monthly or in CI. Note: step 4's Tier-2
re-verification (test/build commands) can produce normal working-tree side effects
(node_modules, build output, caches) — in unattended/scheduled runs, restrict step 4 to
Tier 1 commands and mark the rest "not re-verified":

1. Manifest exists? Every manifest skill directory still present? Every `.claude/skills/*/`
   directory represented in the manifest? Mismatches → report.
2. R1 mechanical lint over every skill (review.md) — catches hand edits that broke format.
3. Staleness: drift set vs each skill's sources (steps 2–3 above) → "stale" list with the
   drifting files named.
4. Sample re-verification: for each stale skill, run its re-verification one-liners and diff
   against recorded observations. Interactive runs: Tier 1–2. Unattended runs: Tier 1 only;
   mark skipped lines "not re-verified".
5. Hand-edit inventory: recompute `git hash-object` for every file in every skill's `files`
   map; any mismatch → hand-edited.
6. Report: healthy / stale (with drift evidence) / broken (lint failures) / orphaned /
   hand-edited — plus the single recommended action for each (usually `refresh`).

Audit writes nothing to the repo or the library — it is the mode to schedule.

## Month-2 ritual (put this in the final report, verbatim)

> Monthly, or after any large merge: run the skill-library-builder in `audit` mode. If it
> reports stale skills, run `refresh`. After refresh, re-run the probe set with your target
> model. Total cost: minutes. Skipping it converts your library from an asset into a
> liability at whatever speed your repo changes.
