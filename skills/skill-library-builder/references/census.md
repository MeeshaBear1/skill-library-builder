# Phase 1–2: Census and System Map

Goal: an on-disk evidence ledger and system map that later phases author FROM. Nothing here is
written from memory or priors — every entry cites a source. Use the agent's dedicated tools
(Glob, Grep, Read) for all file discovery and content search: they are cross-platform,
output-capped, and prompt-free. Git — plus a plain directory listing (`ls -A` /
`Get-ChildItem -Force`) where noted below — are the only shell dependencies in this phase.

Tool caveat (prevents silently-wrong facts): on some harnesses Glob returns nothing for
paths inside dot-directories (`.github/`, `.claude/`, `.circleci/`). An EMPTY Glob result
for a path you have other evidence exists (it appeared in the top-level listing) is a tool
limitation, not repo absence — re-check with a directory listing (bash `ls -R .github`;
PowerShell `Get-ChildItem -Recurse -Force .github`) before recording anything. Rule:
recording an ABSENCE as a fact always requires two independent methods.

Scope discipline: EVERY Glob/Grep pattern in this phase is rooted at the `scope` path and
filtered by the `exclude` globs recorded in state.json during Preflight. A scoped run
censuses only its scope.

Source priority — when sources disagree, the higher one wins; record the disagreement itself
in the ledger (it is a known-trap candidate):

- **Behavior facts** (what the code does): code > tests/fixtures > CI config >
  lockfiles/manifests > runtime & deploy scripts > docs > default-branch git history >
  issues/TODOs/notes > inference (must be marked `[INFERRED]`).
- **Policy/workflow facts** (what the team runs and requires): CLAUDE.md/AGENTS.md >
  CONTRIBUTING > CI config > inference. Never contradict CLAUDE.md silently — see review
  gate R4.

## Working artifacts (created in Phase 0 — verify they exist before starting Phase 1)

`.claude/skills/.skill-library/build/` contains:

- `ledger.md` — evidence ledger. Append-only during census. Entry format:
  ```
  ### E<nnn> <short title>
  - source: <file:line | command>
  - observed: <trimmed content or output — REDACTED per Iron rule 6 before writing>
  - date: <today>
  ```
- `map.md` — system map (Phase 2, schema below).
- `state.json` — schema:
  ```json
  {
    "mode": "init|refresh|only:<name>|audit",
    "scope": ".",
    "exclude": ["vendor/**"],
    "approve": "auto|checkpoint",
    "phase": "0-7 or complete",
    "platform": "windows-powershell|windows-gitbash|linux|macos",
    "proposal": "taxonomy table (recorded when approve=auto; optional otherwise)",
    "skills": {
      "<name>": {
        "status": "planned|authored|reviewed",
        "gates": { "R1": "pass|fail|pending", "R2": "…", "R3": "…", "R4": "…", "R5": "…", "R6": "…" }
      }
    }
  }
  ```

Update `state.json` at every phase transition, after each skill is authored, and after each
review gate result.

## Phase 1 procedure

Order matters: cheap breadth first, then targeted depth. Cap everything — an unbounded sweep
floods context and produces a worse map than a sampled one.

**1. Top-level shape.** List the repo root with a directory listing — bash: `ls -A`;
PowerShell: `Get-ChildItem -Force -Name` (Tier 1). Do NOT use Glob `*` for the skeleton: it
returns file noise, can surface `.git` internals, and misses dot-directories. Record the
skeleton in the ledger, including dot-directories (`.github`, `.claude`, …).
For monorepos (classified in Preflight): list each unit's top level separately. Never derive
the repo shape from an alphabetical file listing — sample every unit.

**2. Manifests and build config.** Glob explicitly, then Read each hit:
`package.json`, `**/package.json` (cap: workspace roots only for monorepos),
`pyproject.toml`, `setup.py`, `requirements*.txt`, `Cargo.toml`, `go.mod`, `**/*.csproj`,
`*.sln`, `**/*.sln`, `Gemfile`, `composer.json`, `Makefile`, `justfile`, `Taskfile*`,
`Dockerfile*`, `docker-compose*`, `CMakeLists.txt`.
Ledger: languages, package manager (confirm via lockfile: `package-lock.json` vs `yarn.lock`
vs `pnpm-lock.yaml` — the lockfile outranks docs), script/target names verbatim.

**3. CI and gates.** Glob `.github/workflows/*`, `.gitlab-ci.yml`, `Jenkinsfile`,
`.circleci/**`, `azure-pipelines*`, `CODEOWNERS`, `.pre-commit-config.yaml`, husky/lefthook
configs — dot-directories: apply the tool caveat above (an empty result for a dir the
skeleton showed must be re-checked with a listing before concluding "no CI"). Read each. Ledger: what CI actually runs (commands verbatim), on which triggers,
which checks block merge. CI commands are the highest-value harvest in the census — they are
machine-executed, therefore verified by construction.

**4. Tests.** Two pattern families — filename conventions AND directory contents (a filename
glob does not see inside `tests/`): Glob `**/*test*` and `**/*spec*` for suffix conventions
(`test_*.py`, `*.test.ts`, `*_test.go`), PLUS `**/tests/**`, `**/test/**`, `**/__tests__/**`,
`**/spec/**` for directory contents (fixtures, factories, helpers live there under non-test
names). Discard incidental substring hits (`contest`, `latest`). Read 2–3 representative test
files per unit. Ledger: test framework, how tests are
invoked (from CI or manifest scripts, not guessed), fixtures/factories location, anything the
tests reveal about invariants.

**5. Docs.** Glob `README*`, `CONTRIBUTING*`, `CHANGELOG*`, `docs/**`, `adr/**`, `**/ADR*`,
`*.md` at root. Read README + CONTRIBUTING fully; skim the rest by headings. Remember
source-priority: docs lose to code, tests, CI, and lockfiles when they disagree — record the
disagreement itself in the ledger, it is a known-trap candidate.

**6. TODO/trap sweep.** Grep, output_mode `content`, head_limit 200:
pattern `TODO|FIXME|HACK|XXX|WORKAROUND|flaky|known issue|do not|DO NOT|deprecated`
Exclude changelog files (`CHANGELOG*`, `History.md`, `docs/changelog*`) — they flood the cap
with prose hits. If the first pass still floods on generic terms (`do not`, `deprecated`),
re-run without those terms and record the pattern disposition in the ledger.
Ledger: only entries that reveal operating knowledge (traps, constraints, footguns) — not
routine TODOs. Each entry keeps its file:line.

**7. Git history (default branch only).** Determine the default branch — walk this chain and
take the first that succeeds:
1. `git symbolic-ref --short refs/remotes/origin/HEAD`
2. `git rev-parse --verify origin/main`, then `origin/master`
3. `git rev-parse --verify main`, then `master`
4. None resolved → ask the user which branch is the default. Unattended (`approve=auto`) and
   cannot ask → use `git branch --show-current`, tag EVERY history-derived ledger entry
   `[INFERRED: default branch unknown; history read from <branch>]`, and flag it in the
   final report.

Record in the ledger which branch was used and by which chain step. Then:
- `git log <branch> --oneline -n 100` — recent activity shape.
- `git log <branch> --grep="revert" --grep="rollback" --grep="hotfix" -i -n 30` — WITH full
  bodies (default format, not --oneline). Failure evidence lives in explanatory commit bodies;
  a bare subject line is not evidence of a cause. Quote bodies in the ledger; never narrate a
  cause the message does not state.
- `git log <branch> --format="%H %ad %s" --date=short -n 300 -- <hot path>` for any area the
  map flags as risky.
Do NOT use `--all`: unmerged branches are not shipped behavior (Iron rule 9).

**8. Runtime/config surface.** Glob `.env.example`, `.env*.example`, `*.env.example`,
`.env.sample`, `.env.template`, `config/**`, `*.config.*`, `settings*`, `helm/**`, `k8s/**`,
`terraform/**`. Read example/template files only — Iron rule 6 permits `.example`/`.sample`/
`.template` files and forbids every other `.env*` and credential file. Ledger: config variable NAMES, where each
is documented as coming from, which config is required vs optional.

**9. Probe mining (for Phase 6 — collect now while history is fresh).** From steps 3–7, list
5–10 recent, concrete, repeatable tasks: real merged bug fixes, small features, CI failures.
Record per probe: task statement, entry point file, observable success checkpoint (a command
and its expected output, a file state, a passing test). Save to
`.claude/skills/.skill-library/probes.md`. Write the literal placeholder line
`expected primary skill: TBD-phase-3` in each probe now — the Phase 3 taxonomy checkpoint
replaces it (skills don't exist yet).

## Phase 2: System map

Write `map.md` with these sections. **Every entry cites a ledger ID or file:line.** An entry
without a citation is deleted, not kept as color.

- **Domain** — what the repo models; core nouns and their meanings.
- **Units** — (monorepo) every workspace/service: purpose, build, test, owner-signals.
- **State** — durable + runtime state: schemas, stores, caches, files; where each lives.
- **Actors** — services, processes, jobs, clients; what runs when.
- **Ownership** — which code/actor may mutate each piece of state.
- **Workflow** — idea→merge→release path as the repo actually enforces it (CI + hooks +
  CODEOWNERS), not as docs describe it.
- **Risks** — traps from the sweep, disagreements between sources, flaky areas, quoted
  failure history.
- **Tools** — test commands, scripts, linters, profilers, log locations — verbatim names only.
- **Success** — what CI + tests define as a passing change.

## Thin-map rule (termination, not retry-forever)

If a section is thin: do ONE more targeted discovery pass for that section. If the second pass
adds fewer than 3 new sourced entries, the section is as deep as the repo — record
"section thin: repo has no <X>" as a VERIFIED fact and move on. A thin map of a thin repo is
correct output; route it to the taxonomy sizing rules, not back into discovery. Only a map
that is thin because you skipped census steps is a defect.
