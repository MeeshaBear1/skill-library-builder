# Phase 5: Review — six gates

Gates run in order; a failed gate is fixed and re-run before the next. The two anti-
hallucination gates (R2, R6) and the trigger gate (R3) run in FRESH subagent context — the
context that authored a mistake will approve it on re-read. If subagents are unavailable in
this session, run those gates yourself but with a hard constraint: inputs are ONLY the
generated skill files and the repo — re-read every source; the ledger and your authoring
memory are off-limits for those passes.

**Fix protocol (all gates):** fixes may not introduce new unverified claims. Any text changed
by a fix gets a delta re-check by the gate that caught it. Track gate results per skill in
state.json.

## R1 — Mechanical lint (deterministic; no judgment)

Per generated skill, assert:
- [ ] frontmatter parses as YAML; exactly `name` + `description`.
- [ ] `name` is `[a-z0-9-]`, ≤64 chars, equals its directory name.
- [ ] description ≤1024 chars, double-quoted, contains ≥3 concrete trigger tokens and (where
      siblings overlap) negative routing.
- [ ] SKILL.md ≤200 lines; first 40 lines contain when-to-use + procedure start.
- [ ] every file path mentioned in the skill exists (Glob each one).
- [ ] every load-bearing claim carries a marker (`[VERIFIED:` / `[INFERRED:` /
      `[UNVERIFIED-CMD:`) — Grep for claims sentences without markers in Procedure/Traps/
      Gates sections.
- [ ] banned judgment verbs absent from Procedure sections (Grep:
      `investigate|ensure|as needed|appropriately|if necessary|properly|when relevant`).
- [ ] stop/escalate list present; worked example present (procedural skills).
- [ ] provenance block present and complete.
- [ ] placement: `.claude/skills/<name>/SKILL.md` exactly.

Output: lint table (skill × checks), included in the final report.

## R2 — Fresh-context factual verification

Spawn a subagent with access to the repo and the generated skills ONLY (no authoring
transcript). Instructions to it:

1. For each skill, extract every checkable claim (paths, commands, flags, versions, invariants,
   history statements).
2. Verify each against a concrete source: Read the cited file:line; re-run Tier-1/Tier-2
   commands (per authoring.md policy) and diff actual output against the skill's expected
   observation; for `[UNVERIFIED-CMD]` entries, statically confirm the command exists where
   claimed (script name in package.json, target in Makefile).
3. Emit a claim→evidence table: claim | marker in skill | evidence found | verdict
   (CONFIRMED / WRONG / UNSUPPORTED).

WRONG → fix from the evidence. UNSUPPORTED → downgrade to `[INFERRED]` or delete. A skill with
>20% non-CONFIRMED claims goes back to Phase 4 for re-authoring from sources, not spot-fixing.

## R3 — Trigger matrix (discrimination test)

1. Lay out ALL descriptions side by side — new skills PLUS pre-existing repo skills (they share
   the same trigger space now).
2. Take the probe tasks from `.claude/skills/.skill-library/probes.md` (add probes until there
   are ≥6 spanning the library's topics).
3. Give a fresh subagent ONLY the description list and one probe at a time: "which single
   skill do you load first?" No skill bodies, no repo access.
4. Score: every probe must map to the intended skill; no probe may plausibly tie between two
   descriptions. Misroute or tie → rewrite the colliding descriptions (sharper triggers,
   negative routing) and re-run the matrix. Descriptions converging on the same trigger
   language is the expected failure mode — fix with concrete tokens (paths, error strings),
   not more adjectives.

## R4 — Cross-skill consistency and context-fit

- Grep every literal command and every trap statement across all generated skills: a fact
  appearing in ≥2 skills violates canonical ownership — keep it in its assigned owner, replace
  elsewhere with a sibling reference (+ one-line summary).
- Contradiction sweep: same topic, different instruction (e.g., two different test commands).
  Resolve from the ledger; if the ledger is silent, re-verify at source.
- CLAUDE.md / AGENTS.md fit: no generated skill may contradict them. Conflict where the
  always-loaded file is RIGHT → fix the skill. Conflict where it is provably STALE
  (lockfile/CI disagree) → keep the skill correct AND flag the CLAUDE.md staleness in the
  final report; never silently edit CLAUDE.md.
- Duplication with always-loaded files: content already in CLAUDE.md appears in a skill only
  as a reference, never restated.

## R5 — Secrets scan (blocking)

Over `.claude/skills/**` (everything this run wrote, including build artifacts and the
manifest): Grep for `sk_live_|sk_test_|AKIA|ghp_|gho_|xox[bsp]|-----BEGIN|password\s*[:=]|
token\s*[:=]|secret\s*[:=]` plus any ≥20-char base64-ish literal
(`[A-Za-z0-9+/_-]{20,}={0,2}` — review hits manually; hashes and SHAs cited as provenance are
allowed, credentials are not). ANY credential hit blocks the final report: redact, then re-run
R5 from scratch. Report the scan result (pattern set + hit count) in the final report.

## R6 — Cold-context usability run

Spawn a fresh subagent with the repo + the library. Give it ONE probe task (a different one
than R3 used, if available) and no other help. Require it to follow the loaded skill's
procedure literally and report: which skill it loaded, each step's actual outcome vs the
skill's expected observation, and where it stalled or improvised.

- Stall/improvisation → that step lacked a branch or observation; fix the skill (usually:
  add the branch the subagent needed) and re-run R6 on the fixed skill.
- Wrong skill loaded → back to R3.
- Checkpoint reached with no improvisation → gate passes.

This gate is the library's first contact with its real consumer. Budget for 2–3 iterations;
passing R6 on the first try usually means the probe was too easy — prefer a probe that
exercises a decision gate.
