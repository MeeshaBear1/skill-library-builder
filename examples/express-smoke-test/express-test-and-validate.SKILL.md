---
name: express-test-and-validate
description: "Runbook for running, targeting, and extending the express test suite: the exact mocha invocation with --require test/support/env and --check-leaks, single-file runs, coverage via test-ci/test-cov, and the acceptance tests that exercise examples/. Use when running npm test, adding or editing files under test/ or test/acceptance/, running one test file, or measuring coverage. Not for diagnosing why a test fails or a mocha 'Timeout of 2000ms exceeded' error — use express-debugging-playbook. Not for lint or CI-gate policy — use express-change-control."
---

# express-test-and-validate

Purpose: run and extend this repo's mocha suite exactly the way the team and CI do, and
prove a change green locally before it reaches CI.

## When NOT to use
- A test is failing and you need a cause → load `express-debugging-playbook` (owns failure triage, flaky-test list, upstream-vs-lib decision).
- Deciding what lint/CI will block a PR → load `express-change-control` (not authored in this build — read `.github/workflows/ci.yml` directly).
- Editing `lib/` and unsure where behavior lives → load `express-architecture-contract`.

## Procedure

1. Run (bash): `npm install`
   Expect: exit 0 within ~60s. Lifecycle scripts are disabled repo-wide (`ignore-scripts=true`) [VERIFIED: .npmrc:3]; no lockfile is created or wanted (`package-lock=false`) [VERIFIED: .npmrc:1]. [VERIFIED: npm install @ 2026-07-02]
   - `EACCES`/network failure → STOP; report the npm error verbatim.
   - A `package-lock.json` appears in `git status` → delete is NOT yours to run; STOP and report (it is gitignored [VERIFIED: .gitignore:3] and disabled by .npmrc — its appearance means npm config was overridden).

2. Run (bash): `npm test`
   This expands to `mocha --require test/support/env --reporter spec --check-leaks test/ test/acceptance/` [VERIFIED: package.json:94].
   Expect: exit 0, final line like "1258 passing (16s)" [VERIFIED: npm test @ 2026-07-02].
   - Exactly 1 failing: "should 404 when URL too long" with a 2000ms timeout → known Windows cold-run flake; go to `express-debugging-playbook` trap T1 before re-running.
   - Any other failure → go to `express-debugging-playbook`.
   - "0 passing" or "Missing script" → you are not at the repo root; cd to the directory containing package.json, retry once, then STOP and report.

3. To run ONE test file (bash): `npx mocha --require test/support/env --reporter spec test/<file>.js`
   Expect: exit 0; e.g. test/res.send.js prints "75 passing (664ms)" [VERIFIED: cmd @ 2026-07-02]. The `--require test/support/env` part is mandatory — it sets `NODE_ENV=test` and `NO_DEPRECATION=body-parser,express` [VERIFIED: test/support/env.js:2-3]; without it, deprecation output and env-dependent behavior diverge from `npm test`.

4. To add a test: match the existing layout — one flat file per API surface (`test/app.*.js`, `test/res.*.js`, `test/req.*.js`, `test/express.*.js`) [VERIFIED: test/ listing @ 2026-07-02]. Tests use mocha + supertest + node:assert [VERIFIED: test/express.static.js:3-8]. Fixtures live in `test/fixtures/`, helpers in `test/support/` [VERIFIED: test/ listing @ 2026-07-02]. Acceptance tests in `test/acceptance/` boot the apps in `examples/` — editing an example means the matching acceptance file must still pass.

5. Coverage (bash): `npm run test-cov` (html+text report) or `npm run test-ci` (lcov, what CI uploads) [VERIFIED: package.json:95-96]. Both wrap `npm test` in nyc excluding examples/test/benchmarks. [UNVERIFIED-CMD: not executed in this build — identical inner command to step 2, nyc adds only local ./coverage output]

## Decision gates

GATE: Which command proves my change?
- change touches only `test/**` → step 3 on the touched file(s), then step 2 once.
- change touches `lib/**` or `index.js` → step 2 (full suite; `--check-leaks` and acceptance coverage only run there).
- change touches `examples/**` → step 3 on the matching `test/acceptance/<name>.js`, then step 2.
- anything else / unsure → step 2.

## Known traps
- `--check-leaks` fails the whole run if any test leaks a global variable [VERIFIED: package.json:94 flag]. A leak error names the global — the leak is in the test you just wrote, not in mocha.
- First full-suite run after a fresh `npm install` on Windows can fail exactly one static-file timeout test; second run passes [VERIFIED: npm test runs 1 and 2 @ 2026-07-02]. Triage steps live in `express-debugging-playbook` (T1) — do not re-run blindly more than once.
- Node >= 18 is the declared floor [VERIFIED: package.json:83] but CI also tests Node 16/17 in legacy.yml — a change passing locally on new Node can still fail the legacy gate [VERIFIED: .github/workflows/legacy.yml:33-34].

## Evidence for success
- `npm test` exit 0 with "N passing, 0 failing" (N was 1258 on 2026-07-02) AND `npm run lint` exit 0 [VERIFIED: both commands @ 2026-07-02]. That approximates the blocking CI jobs, which run `npm run lint` and `npm run test-ci` across Node 18-26 on ubuntu and windows [VERIFIED: .github/workflows/ci.yml:39-42,49,80].

Stop and ask the user when: `npm install` fails; the same test fails twice in a row (after the T1 flake check); a test failure appears in a file you did not touch and `express-debugging-playbook` triage does not match any trap; you would need to change `package.json` scripts or `.npmrc` to make anything pass.

## Worked example (real, 2026-07-02, bash)
Task: prove test/res.send.js still passes after reading the #4893 header fix.
```
$ npx mocha --require test/support/env --reporter spec test/res.send.js
  ...
  75 passing (664ms)
$ echo $?
0
```
Full suite afterwards: `npm test` → "1258 passing (16s)", exit 0.

## Re-verification
```
node -p "require('./package.json').scripts.test"  # verified 2026-07-02: prints mocha --require test/support/env --reporter spec --check-leaks test/ test/acceptance/ (bash)
npm test                                          # verified 2026-07-02: exit 0, "1258 passing (16s)" (bash; first-ever run may hit trap T1)
npx mocha --require test/support/env --reporter spec test/res.send.js  # verified 2026-07-02: exit 0, "75 passing (664ms)" (bash)
```

## Provenance
- generated: 2026-07-02 by skill-library-builder v2 · HEAD 18e5985
- sources: package.json, .npmrc, .gitignore, test/support/env.js, test/express.static.js, test/app.listen.js, .github/workflows/ci.yml, .github/workflows/legacy.yml
- verified-shell: bash (Git Bash on Windows)
- refresh: run skill-library-builder in refresh mode; this skill regenerates when its
  sources change.
