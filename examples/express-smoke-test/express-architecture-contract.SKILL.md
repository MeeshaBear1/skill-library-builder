---
name: express-architecture-contract
description: "Ownership contract for the express codebase: which behavior the six lib/ files own, which APIs are re-exports of external packages (express.Router and Route from router, express.static from serve-static, express.json/raw/text/urlencoded from body-parser), the npm publish surface (files: LICENSE, Readme.md, index.js, lib/), and the createApplication() mixin structure. Use when editing anything under lib/ or index.js, when asked to fix routing, static-file, or body-parsing behavior, or when deciding where a change belongs in this repo. Not for running tests — use express-test-and-validate; not for failure triage — use express-debugging-playbook."
---

# express-architecture-contract

Purpose: state what this repo owns versus what it re-exports, so changes land in the code
that actually produces the behavior — the most expensive mistake here is editing lib/ for
behavior that ships from an external package.

## When NOT to use
- Running or writing tests → `express-test-and-validate`.
- A test is already failing and needs a cause → `express-debugging-playbook` (its step-3 gate applies this contract to failures).

## The contract

1. Entry point: `index.js` is one line — `module.exports = require('./lib/express')` [VERIFIED: index.js:11]. There is no build step, no dist/, no transpilation: lib/ ships as-is [VERIFIED: repo listing @ 2026-07-02 — no build config present].

2. Published surface is ONLY `LICENSE, Readme.md, index.js, lib/` [VERIFIED: package.json:85-90; node -p files @ 2026-07-02]. test/, examples/, .github/ never ship. A behavior fix that edits anything outside index.js + lib/ does not reach npm consumers.

3. lib/ is six files [VERIFIED: lib listing @ 2026-07-02]:
   - `express.js` — createApplication factory + re-exports (see 4).
   - `application.js` — app proto: settings, engines, mounting, listen.
   - `request.js` / `response.js` — req/res prototypes extending Node http.
   - `view.js` — template-engine resolution.
   - `utils.js` — internal helpers.

4. Re-exported, NOT owned here [VERIFIED: lib/express.js:70-81; require.resolve('router') resolves into node_modules @ 2026-07-02]:
   - `express.Router`, `express.Route` → `router` package.
   - `express.static` → `serve-static` package.
   - `express.json`, `express.raw`, `express.text`, `express.urlencoded` → `body-parser` package.
   GATE: asked to change behavior of one of these APIs?
   - Behavior is produced inside the external package → STOP; report that the fix is an upstream dependency change (version bump in package.json or an upstream PR), not a lib/ edit.
   - Behavior is in how lib/ wires or wraps them (e.g. app-level defaults) → edit lib/, then prove per `express-test-and-validate`.
   - Cannot tell which side produces it → reproduce first via `express-debugging-playbook` step 1; do not edit on a guess.

5. App structure invariant: `createApplication()` returns a callable request handler function and mixes in `EventEmitter.prototype` and the application proto with merge-descriptors; `app.request`/`app.response` are per-app prototypes created with `Object.create` [VERIFIED: lib/express.js:36-56]. Changes that replace this mixin pattern with a class break the public `express()` callable contract — the factory's shape is API.

6. Dependency policy constraints on any "just update the dep" fix: no lockfile exists by policy (`package-lock=false`) and lifecycle scripts are disabled (`ignore-scripts=true`) [VERIFIED: .npmrc:1,3]; dependabot ignores semver-major updates [VERIFIED: .github/dependabot.yml:15-17]. Version floors are enforced only by the ranges in package.json:34-63.

## Known traps
- Behavior fixes to res.send's header logic are regression-prone: commit 18e5985 "fix(res.send): add Content-Length header only if Transfer-Encoding is not present (#4893)" [VERIFIED: git log origin/master @ 2026-07-02] — the send path in `lib/response.js` has a dedicated trap (T3) in `express-debugging-playbook`; load it before editing that path.
- `app.listen` accepts 0 args through (port, host, backlog, cb) — the test file enumerates the accepted signatures [VERIFIED: test/app.listen.js:27-43]; narrowing them is a breaking change.

## Evidence for success
A correctly-placed change: edits only files inside the owning package (per gates above), keeps
`npm test` at 0 failing and `npm run lint` at exit 0 [VERIFIED: both commands @ 2026-07-02 baseline], and — if it must ship to npm consumers — touches only the published surface (item 2).

Stop and ask the user when: the fix belongs upstream (gate in item 4); a change would alter the createApplication mixin shape (item 5); a dependency bump would cross a semver-major boundary; anything requires adding a build step or expanding the files whitelist.

## Worked example (real, 2026-07-02, bash)
Task: "fix a routing bug in express" — locate the owner before editing.
```
$ node -e "const e=require('./'); console.log(typeof e.Router)"
function
$ node -e "console.log(require.resolve('router'))"
C:\...\smoke-express\node_modules\router\index.js
```
`express.Router` resolves into `node_modules/router` → owner is the external `router`
package → per item 4 gate: STOP, report upstream; no lib/ edit.

## Re-verification
```
node -p "require('./package.json').files.join(',')"   # verified 2026-07-02: LICENSE,Readme.md,index.js,lib/ (bash)
node -e "console.log(require.resolve('router'))"      # verified 2026-07-02: prints <repo>\node_modules\router\index.js (bash; needs npm install first)
git grep -n "exports.static" -- lib/express.js        # verified 2026-07-02: lib/express.js:79:exports.static = require('serve-static'); (bash)
```

## Provenance
- generated: 2026-07-02 by skill-library-builder v2 · HEAD 18e5985
- sources: index.js, lib/express.js, package.json, .npmrc, .github/dependabot.yml, test/app.listen.js
- verified-shell: bash (Git Bash on Windows)
- refresh: run skill-library-builder in refresh mode; this skill regenerates when its
  sources change.
