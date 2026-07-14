---
name: repo-truth-discovery
description: "Branch-explicit recon procedure for finding where a repository's truth actually lives before touching code: README trust test, doc-of-record sweep (CLAUDE.md/AGENTS.md @-includes, DECISIONS.md, PROGRESS.md, .planning/PROJECT.md), git history probes for pivot and squash commits, empty-repo protocol, supersession check, and a 10-line truth-map template. Use when opening an unfamiliar repo; when the README is missing, is a stock create-next-app or Lovable template, or contradicts the code; when asking 'what is this repo', 'where do I start', or 'which doc governs'; when a repo looks empty or abandoned (if a fleet- or portfolio-specific navigator skill names this exact repo, load that first); or when two docs disagree. Not for building a full skill library — use skill-library-builder (this skill is its Phase-0-style recon as a standalone everyday skill). Not for ranked repo health/quality audits — that is a code-review job, not recon. Not for debugging runtime failures."
---

# Repo Truth Discovery

Answers "where does the truth actually live in this repo?" before any work starts. The #1
observed weak-agent failure in unfamiliar repos is trusting README/surface signals — stale
READMEs, boilerplate READMEs, truth hiding in DECISIONS.md or .planning/, superseded sibling
repos, empty-looking clones with content on the remote [INFERRED: multi-repo portfolio survey
2026-07-02]. Output: a 10-line truth map (Step 7), written BEFORE any code change.

## When NOT to use
- Building a complete skill library for a repo → use **skill-library-builder** (it runs this
  style of recon as its Phase 0; this is the standalone version).
- Diagnosing a failing test, broken build, or runtime error → this skill maps documents and
  history, not defects.
- You already wrote a truth map for this repo in this session → reuse it; skip to your task.

## Procedure

### Step 1 — README trust test (~2 min)
Read README.md with your file-reading tool. Classify:
- No README **and** the root listing (Step 2 command) shows only `.git` or nothing → jump to
  Step 4 (empty-repo protocol).
- Body is a stock framework template — create-next-app's "Getting Started … run the
  development server", Vite/Lovable scaffold text, or a bare one-line `# <name>` →
  **BOILERPLATE**: weight it zero as evidence; continue to Step 2.
- README makes stateful claims (stack list, "launched", "v2", feature list) → cross-check:
  Run: `git --no-pager log -5 --format="%ad %s" --date=short`
  Expect: one `YYYY-MM-DD <subject>` line per commit [VERIFIED: cmd @ 2026-07-02]
  and open the manifest (package.json / pyproject.toml / go.mod).
  - Claims match commit dates and manifest → **TRUSTWORTHY**.
  - Claims contradict either → **STALE**: list each divergence in the truth map; keep the
    README as background only, never as instruction.
- README (or any doc) names commands to run (build / test / run / setup) → **a command is a
  claim too.** Verify each against the manifest's actual entries — package.json `scripts`,
  Makefile targets, pyproject `[project.scripts]`. A command a doc names but the manifest does
  not define is STALE: cite the manifest's real command, mark the doc wrong on truth-map
  line 2, and never hand the reader the undefined command. The script definition outranks any
  prose mention, **including the README's own quick-start** — and reading the manifest is not
  enough, you must PREFER it when the two conflict. [measured: poisoned-README test-command A/B
  on the weakest tier, 2026-07-12/13 — with this rule the skill shipped the correct command
  26/30 vs 10/30 without it (Fisher p≈5e-5); every resister debunked the stale command via this
  rule, and opening package.json without preferring it did not help (both arms opened it 30/30).]

### Step 2 — Doc-of-record sweep
Run a dot-safe root listing — bash: `ls -A` · PowerShell: `Get-ChildItem -Force -Name`
[VERIFIED: cmd @ 2026-07-02]. Do not rely on glob tools alone: they can skip dot-directories
such as `.planning/` and `.claude/`.
Read whichever of these exist, in this priority order (each outranks the README):
1. `CLAUDE.md` / `AGENTS.md` — follow @-includes: a CLAUDE.md whose whole body is
   `@AGENTS.md` delegates; read the target file too.
2. `DECISIONS.md` — decision log; latest dated entry wins within this file.
3. `PRINCIPLES.md` / `CHARTER.md` / `COMPLIANCE.md` / `CONFORMANCE.md` — gates and bans.
4. `launch-state.md` / `GO-LIVE.md` / `LAUNCH-CHECKLIST.md` — deployment truth.
5. `PROGRESS.md` / `BUILD_LOG.md` / `MORNING_REPORT.md` — autonomous-build session logs.
6. `.planning/` — GSD convention: `PROJECT.md` + phase plans. A repo can be 100% .planning
   with zero code; the plan IS the project state [INFERRED: portfolio survey 2026-07-02].
7. `docs/architecture*` — structural claims; cross-check against the actual source tree.
Branch: `.planning/PROJECT.md` exists → treat it as the primary statement of intent.
None of the above exist → the README (whatever its grade) plus git history is all you have;
say so on truth-map line 1.

### Step 3 — History probes
Run: `git rev-list --count HEAD`
Expect: a single integer [VERIFIED: cmd @ 2026-07-02]
- Fails with `fatal: ambiguous argument 'HEAD': unknown revision or path not in the working tree.`
  [VERIFIED: cmd in fresh git-init dir @ 2026-07-02, git 2.53.0.windows.1] — treat ANY fatal/
  nonzero exit here as the no-commits signal → Step 4.
- Prints `1` → single-commit repo. Subject looks like "initial", "import", "squash" → this
  is a squash import: zero archaeology available; weight docs higher and record that on
  truth-map line 3.
- Prints ≥2 → Run: `git --no-pager log --oneline -20`
  Expect: one `<sha> <subject>` line per commit [VERIFIED: cmd @ 2026-07-02]
  Scan subjects:
  - "pivot", "reframe", "redesign", "rename", "v2" → a pivot commit: every doc last touched
    before that commit's date is suspect; add it to truth-map line 8.
  - "backup", "checkpoint" → machine-move snapshot, not a milestone; do not read it as
    project progress [INFERRED: portfolio survey 2026-07-02].

### Step 4 — Empty-repo protocol
Trigger: 0 commits, or a working tree that is bare except `.git`.
Run: `git remote -v`
Expect: `origin <url> (fetch)` / `(push)` lines, or no output [VERIFIED: cmd @ 2026-07-02]
- No output → no remote. STOP: ask the operator what this repo is for before inventing a
  purpose or scaffolding anything.
- Remote listed → Run: `git ls-remote origin`
  Expect: `<sha>\tHEAD` plus one line per remote ref [VERIFIED: cmd @ 2026-07-02]
  - Refs printed → **the remote HAS content**. The correct first move is fetch/pull — a
    mutating step, so STOP and report it. NEVER scaffold over an un-pulled remote.
  - No refs → remote exists but is empty. STOP: confirm intended purpose with the operator.

### Step 5 — Supersession check
Look for: sibling directories one level up named `<repo>-redesign` / `-v2` / `-new` /
`-next`; forks named in the README; two deploy configs (vercel.json, netlify.toml, fly.toml)
in different subtrees. Candidate found → decide canon by evidence, in this order:
1. An explicit note in the newer repo ("supersedes <old>") → that note wins.
2. A deploy config pointing at the production domain → that repo is canon.
3. Latest commit dates across the siblings → newest is canon ONLY if 1–2 are absent and the
   date gap is unambiguous (weeks, not hours).
Evidence conflicts, or none of the three exists → STOP: ask, don't guess. Record the answer
on truth-map line 5. Doing the task in the superseded sibling is wasted work
[INFERRED: portfolio survey 2026-07-02].

### Step 6 — Which-doc-governs conflict rule
GATE: two docs disagree on a fact:
- The newer-dated claim is corroborated by an independent artifact (commit date, lockfile,
  CI config) → newer wins; mark the older doc stale on truth-map line 8.
- No corroboration → record the contradiction verbatim on truth-map line 6 and flag it to
  the operator. NEVER silently pick one side. NEVER rewrite the older doc to match.

### Step 7 — Write the truth map
Write this 10-line note (scratch file or task notes) BEFORE any code change:
```
# TRUTH MAP — <repo> — <date>
1. Governing docs (ranked): <e.g. .planning/PROJECT.md > DECISIONS.md > README>
2. README status: trustworthy | stale (divergences: …) | boilerplate | absent
3. History shape: <N> commits; pivots: <sha/subject | none>; squash-only: yes|no
4. Remote: <url | none>; local vs remote: in-sync | remote-has-content | local-only
5. Canon status: canonical | superseded by <sibling> | UNRESOLVED (escalated)
6. Open contradictions: <doc A says X; doc B says Y> | none
7. Gates/bans found: <charter/compliance lines that touch this task> | none
8. Staleness flags: <docs older than the last pivot commit>
9. Where this task's truth lives: <file(s)>
10. Blocked on operator: <question(s)> | nothing
```

**Stop and ask the user when:**
- An empty local repo has content on its remote (Step 4) — fetch/pull is a mutating step.
- Supersession between sibling repos is unresolved after Step 5's three evidence checks.
- A CHARTER/COMPLIANCE/CONFORMANCE doc contains a gate or ban you cannot map to the task.
- A governing doc bans exactly what the task asks for.
- Two docs contradict on a fact the task depends on and Step 6 finds no corroboration.
- The repo has no commits, no remote, and no docs.

## Decision gates
GATE: may any file be edited yet?
- Truth map written; line 5 = canonical; lines 6/10 show nothing blocking this task → YES.
- Line 5 = superseded → NO: you are in the wrong repo.
- Line 5 = UNRESOLVED, or line 10 lists an open question the task depends on → NO: wait.
- No truth map exists → NO: run the procedure first.

## Known traps
- Stock README ≠ empty project: a create-next-app README beside a full `.planning/` means
  the repo is planned, not blank [INFERRED: portfolio survey 2026-07-02].
- `CLAUDE.md` containing only `@AGENTS.md`: reading CLAUDE.md alone yields nothing — follow
  the include.
- A 1-commit, 40k-line repo is a squash import, not a new project; its docs carry the whole
  history [INFERRED: portfolio survey 2026-07-02].
- Glob-based listings can miss dot-directories; the sweep uses `ls -A` /
  `Get-ChildItem -Force -Name` for exactly this reason.
- A quick-start command block is prose, not truth: a README line `npm run <x>` does not make
  `<x>` a real script — it may be renamed or never have existed. Read the manifest's `scripts`
  and prefer it on conflict; merely opening the manifest while still quoting the README's
  command is the observed failure, not the fix.
- Scaffolding into an empty clone whose remote has content creates a divergent history that
  later pulls will collide with.
- "Improving" the superseded sibling: the work lands in a repo nothing deploys.

## Worked example
[INFERRED: composite illustration from portfolio survey 2026-07-02 — repo name and output invented]
```
Repo: acme-site · task: "add a pricing page"
S1: README = stock create-next-app text → BOILERPLATE, weight zero.
S2: ls -A → CLAUDE.md (body: "@AGENTS.md"), AGENTS.md, DECISIONS.md, .planning/
    .planning/PROJECT.md: "pivoted from product landing to waitlist capture"
S3: git --no-pager log --oneline -20 → "b3c91f2 pivot: waitlist-first" → README + older
    docs/architecture.md flagged stale (line 8).
S5: sibling dir acme-site-redesign: newer commits AND its vercel.json names the production
    domain → acme-site is superseded (line 5). STOP → operator confirms redesign is canon.
Result: truth map written; pricing-page work redirected to acme-site-redesign.
```

## Evidence for success
- A ≤10-line truth map exists before the first edit, and every staleness/canon claim on it
  names its evidence (commit sha/date, file path, or remote ref).
- No contradiction was silently resolved: each one appears on line 6 or was escalated.
- No scaffold was created in a repo whose remote had content.

## Re-verification
This skill states no repo-specific volatile facts. Its [VERIFIED: cmd] markers attest only
that each command form runs and prints the described output shape (git 2.x, bash and
PowerShell, 2026-07-02). All [INFERRED] pattern claims come from a cross-repo survey — before
acting on one in YOUR repo, confirm it there (e.g. that a `.planning/` dir actually contains
PROJECT.md) by reading the files the procedure names.

## Provenance
- generated: 2026-07-02 · generator: portfolio-survey + manual verification
- sources: cross-repo portfolio survey (a large multi-repo portfolio; patterns only — no
  repo-identifying content retained); command forms executed 2026-07-02 in a local git
  repository (bash + PowerShell)
- verified-shell: bash and powershell (paired forms given where syntax differs)
- refresh: pattern-based discipline skill — re-review when doc conventions (GSD .planning/,
  CLAUDE.md @-includes) change; run skill-library-builder in refresh mode for library use.
