# Eval probes — mined during census (2026-07-02)

Fields: task | entry point | success checkpoint | expected primary skill (assigned at Phase 3)

> NOTE: this smoke test authored only 3 of the 5 approved skills. **P3 and P6
> name `express-change-control`, which was NOT authored here** — they can only
> ever score "expected skill never loaded," so EXCLUDE them from the minimal A/B
> run (or author that skill first). The runnable set is P1, P2, P4, P5, P7.
> See `README.md` and `RESULTS.md`.

### P1 Run the full test suite
- task: "Set up this repo and prove the test suite passes."
- entry point: package.json:94 (`npm test`)
- success checkpoint: `npm test` exits 0; mocha spec reporter prints passing count and "0 failing".
- expected primary skill: express-test-and-validate

### P2 Reproduce a merged header-conflict fix
- task: "Verify res.send does not set Content-Length when Transfer-Encoding is set (regression #4893, commit 18e5985)."
- entry point: lib/response.js send path; test/res.send.js
- success checkpoint: `npx mocha --require test/support/env --reporter spec test/res.send.js` exits 0.
- expected primary skill: express-debugging-playbook

### P3 Fix a lint violation
- task: "Code using the global Buffer fails lint — fix it the way this repo requires."
- entry point: .eslintrc.yml:11-14 (no-restricted-globals Buffer)
- success checkpoint: `npm run lint` exits 0.
- expected primary skill: express-change-control (⚠️ NOT authored in this 3-skill smoke test — excluded from the A/B run; see NOTE above)

### P4 Add an edge-case test for a response API
- task: "Add a test for res.type() edge cases like merged commit b4ab7d6 (#7037)."
- entry point: test/res.type.js (flat per-API test layout, E009)
- success checkpoint: new `it()` runs green inside `npx mocha --require test/support/env --reporter spec test/res.type.js`; full `npm test` still 0 failing.
- expected primary skill: express-test-and-validate

### P5 Debug a single failing test file without running the whole suite
- task: "test/app.listen.js is failing — isolate and diagnose."
- entry point: test/app.listen.js
- success checkpoint: single-file mocha run reproduces, then passes after fix.
- expected primary skill: express-debugging-playbook

### P6 Bump a dependency minimum safely (CVE class)
- task: "Bump the qs minimum version like merged commits 925a1df / a08da78."
- entry point: package.json:55 (dependencies.qs)
- success checkpoint: `npm install` (no lockfile to update — E003) then `npm test` exits 0.
- expected primary skill: express-change-control (⚠️ NOT authored in this 3-skill smoke test — excluded from the A/B run; see NOTE above)

### P7 Explain where routing behavior lives
- task: "Fix a routing bug in this repo" (trick: routing is NOT in lib/ — external `router` package, E011).
- entry point: lib/express.js:70-71
- success checkpoint: agent identifies the `router` npm package as the code owner, does not patch node_modules or lib/ blindly.
- expected primary skill: express-architecture-contract
