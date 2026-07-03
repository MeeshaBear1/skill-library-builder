---
name: express-debugging-playbook
description: "Sourced failure modes and triage procedures for the express repo: the Windows cold-run flake 'should 404 when URL too long' / 'Timeout of 2000ms exceeded' in test/express.static.js, mocha --check-leaks 'global leak(s) detected' failures, the res.send Content-Length vs Transfer-Encoding conflict class (#4893), res.status RangeError for codes outside 100-999, and deciding whether a bug lives in lib/ or in the external router/body-parser/serve-static/send packages. Use when npm test fails, a mocha timeout or leak error appears, res.* or req.* behavior differs from expectation, or a routing/static/body-parsing bug is reported. Not for how to run or write tests — use express-test-and-validate."
---

# express-debugging-playbook

Purpose: turn this repo's observed failures — captured test-run output and quoted merged-fix
history — into fixed triage branches, so no failure gets a guessed cause.

## When NOT to use
- You only need to run/target/extend tests → `express-test-and-validate` (owns all mocha invocations; this skill only interprets their failures).
- You are deciding where code belongs before editing `lib/` → `express-architecture-contract`.

## Triage procedure

1. Reproduce with the narrowest owner command (bash): single failing file first —
   `npx mocha --require test/support/env --reporter spec test/<failing-file>.js`
   (invocation contract owned by `express-test-and-validate`).
   - Passes in isolation but failed in the full suite → step 2 (interaction/flake class).
   - Fails in isolation → step 3 (deterministic class).

2. Interaction/flake class — match against traps T1 and T2 below.
   - Matches a trap → follow that trap's action.
   - Matches neither → run the full suite once more; if the same test fails twice, treat as deterministic (step 3). If a DIFFERENT test fails each run → STOP; report both outputs verbatim.

3. Deterministic class — decide the owner before touching code:
   GATE: Where does the failing behavior live?
   - Stack trace or failing API is `express.Router`/`express.Route` → external `router` package [VERIFIED: lib/express.js:70-71; require.resolve('router') -> node_modules/router @ 2026-07-02]. Fix is an upstream dependency change, NOT a lib/ edit → STOP and report which package owns it.
   - `express.static` serving behavior (not the test harness) → external `serve-static` [VERIFIED: lib/express.js:79]. Same STOP rule.
   - `express.json/raw/text/urlencoded` parsing → external `body-parser` [VERIFIED: lib/express.js:77-81]. Same STOP rule.
   - `res.*` / `req.*` helpers, app lifecycle, view resolution → this repo's `lib/response.js`, `lib/request.js`, `lib/application.js`, `lib/view.js` [VERIFIED: lib/ listing @ 2026-07-02] → fix here, then prove per `express-test-and-validate`.

## Known traps (each quoted from captured output or default-branch history)

**T1 — Windows cold-run static timeout (flaky).**
Observed on the first full-suite run after fresh install: exit 1 with
"1257 passing (19s) / 1 failing — express.static() fallthrough when false should 404 when
URL too long: Error: Timeout of 2000ms exceeded." plus stderr "superagent: double callback bug"
[VERIFIED: npm test run 1 @ 2026-07-02]. The same file alone: "90 passing (933ms)", exit 0
[VERIFIED: cmd @ 2026-07-02]. Second full run: "1258 passing (16s)", exit 0 [VERIFIED: npm test run 2 @ 2026-07-02].
Action: re-run the full suite exactly once. Fails on a DIFFERENT test → step 2. Same test fails again → treat as deterministic (step 3); do not loop.

**T2 — `--check-leaks` global leak failure.**
`npm test` runs mocha with `--check-leaks` [VERIFIED: package.json:94]; a test that sets any
global fails the suite even though its assertions pass. Action: the error names the leaked
global — remove the global assignment in the test you touched; nothing else.

**T3 — Content-Length vs Transfer-Encoding (res.send).**
Merged fix 18e5985 (#4893): "fix(respond): add Content-Length header only if Transfer-Encoding
is not present" with "tests for all transfer encodings" [VERIFIED: git log origin/master @ 2026-07-02].
Action: any change to the send path in lib/response.js must keep test/res.send.js green
(75 tests as of 2026-07-02 [VERIFIED: cmd @ 2026-07-02]); setting both headers is the
historically shipped bug.

**T4 — res.status throws outside 100-999.**
Commit 723b545 (#4212): "Throw on invalid status codes" — RangeError; its body notes tests use
status 100 carefully "to avoid 100-continue behavior" [VERIFIED: git log origin/master @ 2026-07-02].
Action: a RangeError from res.status is contract, not a bug; do not widen the range.

**T5 — security patches can be reverted; do not trust a "sec:" commit is live.**
Commit 697547c: 'Revert "sec: security patch for CVE-2024-51999" / This reverts commit 2f64f68'
[VERIFIED: git log origin/master @ 2026-07-02]. The revert body states no cause.
Action: before reasoning from any security-related commit, check it is still reachable and
un-reverted: `git log origin/master --oneline --grep="<CVE id>"` and look for a matching Revert.
Why it was reverted is not recorded in the repo [INFERRED: absence of explanatory body in 697547c — re-verify against the GitHub PR/issue trail before citing a reason].

**T6 — engines floor vs legacy CI.**
package.json declares node >= 18 [VERIFIED: package.json:83] but legacy.yml still gates Node 16/17
[VERIFIED: .github/workflows/legacy.yml:33-34]. Action: a failure that only appears on Node 16/17
is still a blocking failure; do not dismiss it as "unsupported version".

## Evidence for success
A diagnosis is done when: the failure is reproduced by a single quoted command, matched to a
trap or to an owner via the step-3 gate, and — if the owner is this repo — the fix leaves
`npm test` at exit 0 with 0 failing (proof procedure in `express-test-and-validate`).

Stop and ask the user when: two consecutive full-suite runs fail on different tests; the
step-3 gate lands on an external package (upstream fix needed); a failure reproduces only on
a Node version you cannot run locally; any fix would need to edit files outside lib/ and test/.

## Worked example (real, 2026-07-02, bash)
```
$ npm test            # run 1, fresh node_modules
  1257 passing (19s)
  1 failing
  1) express.static() fallthrough when false should 404 when URL too long:
     Error: Timeout of 2000ms exceeded. ...
$ npx mocha --require test/support/env --reporter spec test/express.static.js
  90 passing (933ms)   # exit 0 → interaction/flake class → T1
$ npm test            # run 2, per T1: exactly one retry
  1258 passing (16s)   # exit 0 → T1 confirmed, no code change needed
```

## Re-verification
```
npx mocha --require test/support/env --reporter spec test/express.static.js  # verified 2026-07-02: exit 0, "90 passing (933ms)" (bash)
git log origin/master --oneline -n 1                                         # verified 2026-07-02: 18e5985 fix(res.send): add Content-Length header only if Transfer-Encoding is not present (#4893) (bash)
node -e "console.log(require.resolve('router'))"                             # verified 2026-07-02: prints <repo>\node_modules\router\index.js (bash; needs npm install first)
```

## Provenance
- generated: 2026-07-02 by skill-library-builder v2 · HEAD 18e5985
- sources: lib/express.js, package.json, .github/workflows/legacy.yml, test/express.static.js, git log origin/master (default branch via symbolic-ref), captured npm test/mocha runs 2026-07-02
- verified-shell: bash (Git Bash on Windows)
- refresh: run skill-library-builder in refresh mode; this skill regenerates when its
  sources change.
