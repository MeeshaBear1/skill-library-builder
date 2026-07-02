# Phase 4: Authoring — format, verification, and style contracts

Author ONE skill at a time, working from `map.md` and `ledger.md`, re-reading cited sources as
you go — never from context memory. After each skill: update `state.json`, then start the next.

## Skill format contract (violations = silent load failure)

- Directory: `<repo>/.claude/skills/<name>/` — SKILL.md directly inside. Nothing nested deeper
  except a `references/` subdirectory.
- `name:` lowercase kebab-case `[a-z0-9-]`, ≤64 chars, EXACTLY equal to the directory name.
- `description:` ≤1024 chars, written to survive YAML: wrap in double quotes; no unescaped
  internal double quotes.
- Frontmatter is exactly `---` / `name:` / `description:` / `---`. Nothing else.
- After writing every skill, verify placement: Glob `.claude/skills/*/SKILL.md` and confirm
  each new skill appears at depth exactly `<name>/SKILL.md`.

## Description contract (the description is the ONLY thing that decides loading)

Template — third person, two parts, no filler:

> "<What the skill contains, concretely>. Use when <trigger situations: task types, concrete
> repo paths, command names, literal error strings>. Not for <adjacent situation> — use
> <sibling-skill> instead."

Rules:
- Include at least 3 concrete trigger tokens that literally appear in working sessions:
  file paths (`src/billing/`), commands (`make deploy-staging`), error strings
  (`ECONNREFUSED 5432`), task verbs ("adding a migration").
- Include negative routing whenever a sibling could plausibly match the same moment.
- Never write two descriptions whose trigger surfaces overlap — Phase 5's trigger matrix will
  send them back.

Example (good):
> "Debugging playbook for acme-api: known failure modes, log locations, and branch-explicit
> diagnosis procedures. Use when tests fail in CI but pass locally, when requests return 502
> after deploy, when `redis timeout` appears in logs, or when debugging anything under
> src/workers/. Not for writing new tests — use acme-test-and-validate."

Example (bad — will collide with every sibling and never discriminate):
> "Helps with debugging and troubleshooting issues in the project."

## Body budget and ordering

- SKILL.md ≤200 lines, target 80–150. Hard rule: the first screen (~40 lines) must contain
  the when-to-use line and the start of the procedure. Provenance and maintenance go LAST.
- Depth beyond the budget moves to `references/*.md` inside the skill directory, each linked
  with a CONDITIONAL pointer: "Read references/incidents.md only when the failure matches
  pattern X." Unconditional "see also" pointers are banned — they either always load (budget
  defeated) or never load (dead weight).
- Section order: Purpose (2 lines) → When NOT to use + siblings → Procedure → Decision gates →
  Known traps → Evidence for success → Re-verification → Provenance.

## Branch-explicit procedure style (the weaker-model contract)

Every procedure step is one of:

**(a) Command step** — literal command + shell + captured observation + branch table:

```
2. Run (bash): npm run test:unit
   Expect: "Tests: 412 passed" within ~90s  [VERIFIED: cmd @ 2026-07-02]
   - Output contains "FAIL src/billing" → step 5 (known flaky suite, see traps)
   - Output contains "Missing script"   → you are in the wrong directory; cd to repo root, retry once, then STOP and report
   - Any other failure                  → STOP; paste the last 30 lines into your report
```

**(b) Decision gate** — fully enumerated conditions, one action each, no residual judgment:

```
GATE: Is this change behavior-visible?
- touches src/api/** or any *.proto     → YES: follow acme-change-control before continuing
- only touches tests/, docs/, comments  → NO: continue to step 4
- anything else / unsure                → treat as YES
```

Banned in procedure text: *investigate, ensure, verify appropriately, as needed, relevant,
properly, handle, consider, if necessary*. Each of these is a judgment call the skill exists
to resolve. If you cannot resolve one into branches, the honest form is a STOP condition.

Every procedural skill MUST end its procedure with a stop/escalate list:
"Stop and ask the user when: <enumerated conditions>."

Every procedural skill includes ONE worked example: a short real transcript of the procedure
applied to an actual case from the ledger (a real past bug, a real build), with real output.

## Evidence markers (machine-scannable; review greps for them)

- `[VERIFIED: <file>:<line>]` — claim read directly from source.
- `[VERIFIED: <command> @ <date>]` — claim observed by running the command in this build.
- `[INFERRED: <basis>]` — pattern-based conclusion. The skill must tell its consumer to
  re-verify INFERRED claims before acting on them.
- `[UNVERIFIED-CMD: <reason>]` — command published without execution (destructive, needs
  credentials, needs missing services). The skill must say what running it requires.

Every load-bearing claim (any statement a consumer would act on) carries exactly one marker.
Hedged prose ("probably", "should") is not a substitute and fails review.

## Command verification protocol

Three-tier execution policy (Iron rule 10) for commands you run during authoring:

- **Tier 1 — run freely**: read-only: `git status/log/show/diff/branch`, Glob/Grep/Read,
  version checks (`node --version`).
- **Tier 2 — inspect, then run contained**: repo scripts, build, test, lint. BEFORE running:
  Read the script body / Makefile target / package.json entry INCLUDING pre/post hooks. Run
  only if side effects are contained to the working tree and local caches (no network writes,
  no DB migrations, no global installs). If the repo needs dependencies installed to do
  anything (fresh clone): ask the user before any install whose lifecycle scripts you have
  not read.
- **Tier 3 — forbidden without explicit user authorization**: installs with lifecycle hooks
  you haven't cleared, anything mutating a DB or network resource, deploy/publish, `rm`,
  `git` mutating verbs (reset/checkout/switch/clean/commit/push/pull/merge/rebase/stash),
  writes outside `.claude/skills/` and the build dir. Ambiguous → Tier 3.

For every command that will appear in a generated skill:
1. Classify its tier. Tier 1–2 → execute it; capture exit code + trimmed output into the
   ledger; quote the observation from that capture. Tier 3 or un-runnable → publish with
   `[UNVERIFIED-CMD: <reason>]` and verify what CAN be verified statically (script exists in
   package.json [VERIFIED: package.json:41]).
2. Record the shell it ran in; publish the shell with the command. If the repo's team spans
   platforms, prefer platform-neutral invocations (`npm run x`, `make x`, `git x`) over raw
   pipelines; give paired PowerShell/POSIX forms when a pipeline is unavoidable.
3. For search/read steps inside generated skills, instruct the consumer to use Grep/Glob/Read
   (named as "your file search tools"), not shell pipelines — consumers run on any OS.

Re-verification one-liners (see template): run each ONCE during authoring; append the observed
result: `# verified 2026-07-02: prints 1 line`.

## Redaction rules (applied at WRITE time, not review time)

Before any ledger entry or skill content is written: strip values of variables whose names
match `KEY|TOKEN|SECRET|PASSWORD|PASSWD|CREDENTIAL|PRIVATE`, strings with known prefixes
(`sk_live_`, `sk_test_`, `AKIA`, `ghp_`, `gho_`, `xox`, `-----BEGIN`), and any ≥20-char
high-entropy literal from config/output. Replace with `<REDACTED:VAR_NAME>`. Document where a
value comes from ("set DATABASE_URL — see 1Password vault 'acme-dev'" [VERIFIED: README:88]),
never what it is. Internal hostnames in captured output: keep only if they already appear in
committed, non-gitignored files; otherwise redact.

## Per-skill provenance block (last section of every SKILL.md)

```
## Provenance
- generated: 2026-07-02 by skill-library-builder v2 · HEAD <sha>
- sources: <files/dirs consulted, comma-separated>
- verified-shell: <bash|powershell|zsh>
- refresh: run skill-library-builder in refresh mode; this skill regenerates when its
  sources change.
```

The same data goes into the manifest (references/refresh.md) at authoring time — not
reconstructed later.

## Collisions with existing skills

Name or topic collides with an existing skill → do NOT write. Diff your would-be content
against the existing skill; propose a merge to the user (their hand-tuned content wins by
default); or rename yours AND carve disjoint trigger space in both descriptions. Iron rule 7.
