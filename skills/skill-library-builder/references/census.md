# Phase 1–2: Census and System Map

Goal: an on-disk evidence ledger and system map that later phases author FROM. Nothing here is
written from memory or priors — every entry cites a source. Use the agent's dedicated tools
(Glob, Grep, Read) for all file discovery and content search: they are cross-platform,
output-capped, and prompt-free. Git is the only shell dependency in this phase.

## Working artifacts (create first)

Create `.claude/skills/.skill-library/build/` containing:

- `ledger.md` — evidence ledger. Append-only during census. Entry format:
  ```
  ### E<nnn> <short title>
  - source: <file:line | command>
  - observed: <trimmed content or output — REDACTED per Iron rule 6 before writing>
  - date: <today>
  ```
- `map.md` — system map (Phase 2, schema below).
- `state.json` — `{ "mode", "scope", "approve", "phase", "platform", "skills": {<name>: "planned|authored|reviewed"} }`.

Update `state.json` at every phase transition and after each skill is authored.

## Phase 1 procedure

Order matters: cheap breadth first, then targeted depth. Cap everything — an unbounded sweep
floods context and produces a worse map than a sampled one.

**1. Top-level shape.** Glob `*` and `*/`. Record the directory skeleton in the ledger.
For monorepos (classified in Preflight): Glob each unit's top level separately. Never derive
the repo shape from an alphabetical file listing — sample every unit.

**2. Manifests and build config.** Glob explicitly, then Read each hit:
`package.json`, `**/package.json` (cap: workspace roots only for monorepos),
`pyproject.toml`, `setup.py`, `requirements*.txt`, `Cargo.toml`, `go.mod`, `*.csproj`,
`Gemfile`, `composer.json`, `Makefile`, `justfile`, `Taskfile*`, `Dockerfile*`,
`docker-compose*`, `CMakeLists.txt`.
Ledger: languages, package manager (confirm via lockfile: `package-lock.json` vs `yarn.lock`
vs `pnpm-lock.yaml` — the lockfile outranks docs), script/target names verbatim.

**3. CI and gates.** Glob `.github/workflows/*`, `.gitlab-ci.yml`, `Jenkinsfile`,
`.circleci/**`, `azure-pipelines*`, `CODEOWNERS`, `.pre-commit-config.yaml`, husky/lefthook
configs. Read each. Ledger: what CI actually runs (commands verbatim), on which triggers,
which checks block merge. CI commands are the highest-value harvest in the census — they are
machine-executed, therefore verified by construction.

**4. Tests.** Glob `**/*test*`, `**/*spec*` — but treat as path *segments*: match `tests/`,
`test_*.py`, `*.test.ts`, `*_test.go`, `spec/`; do NOT count incidental substrings (`contest`,
`latest`). Read 2–3 representative test files per unit. Ledger: test framework, how tests are
invoked (from CI or manifest scripts, not guessed), fixtures/factories location, anything the
tests reveal about invariants.

**5. Docs.** Glob `README*`, `CONTRIBUTING*`, `CHANGELOG*`, `docs/**`, `adr/**`, `**/ADR*`,
`*.md` at root. Read README + CONTRIBUTING fully; skim the rest by headings. Remember
source-priority: docs lose to code, tests, CI, and lockfiles when they disagree — record the
disagreement itself in the ledger, it is a known-trap candidate.

**6. TODO/trap sweep.** Grep, output_mode `content`, head_limit 200:
pattern `TODO|FIXME|HACK|XXX|WORKAROUND|flaky|known issue|do not|DO NOT|deprecated`
Ledger: only entries that reveal operating knowledge (traps, constraints, footguns) — not
routine TODOs. Each entry keeps its file:line.

**7. Git history (default branch only).** Determine the default branch:
`git symbolic-ref --short refs/remotes/origin/HEAD` (fallback: `git branch --show-current`).
Then:
- `git log <branch> --oneline -n 100` — recent activity shape.
- `git log <branch> --grep="revert" --grep="rollback" --grep="hotfix" -i -n 30` — WITH full
  bodies (default format, not --oneline). Failure evidence lives in explanatory commit bodies;
  a bare subject line is not evidence of a cause. Quote bodies in the ledger; never narrate a
  cause the message does not state.
- `git log <branch> --format="%H %ad %s" --date=short -n 300 -- <hot path>` for any area the
  map flags as risky.
Do NOT use `--all`: unmerged branches are not shipped behavior (Iron rule 9).

**8. Runtime/config surface.** Glob `*.env.example`, `config/**`, `*.config.*`,
`settings*`, `helm/**`, `k8s/**`, `terraform/**`. Read example/template files only.
NEVER read live credential files (Iron rule 6 list). Ledger: config variable NAMES, where each
is documented as coming from, which config is required vs optional.

**9. Probe mining (for Phase 6 — collect now while history is fresh).** From steps 3–7, list
5–10 recent, concrete, repeatable tasks: real merged bug fixes, small features, CI failures.
Record per probe: task statement, entry point file, observable success checkpoint (a command
and its expected output, a file state, a passing test). Save to
`.claude/skills/.skill-library/probes.md`.

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
