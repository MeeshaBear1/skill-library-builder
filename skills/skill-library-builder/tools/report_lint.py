#!/usr/bin/env python3
"""report_lint.py — banned-phrase / overclaim lint for agent completion reports.

Two mechanical checks for reports produced by coding agents (human or model):

1. Banned phrases — hedges that assert success without evidence ("looks good",
   "seems to work", "should be fine"). Each match names the action that would
   replace the anecdote with an artifact.
2. Claim-without-command (--completion adds a report-format check) — any line
   asserting a pass/check/exit-0/verified result in a report that names NO
   reproduction command anywhere is a finding. This rule exists because weak
   models fabricate CONFIDENTLY, not hedgingly: in a 30-report evaluation
   corpus (10 fabricating reports quoting invented runner output), the hedge
   lexicon scored zero hits while this rule flagged every fabrication —
   including one that manual grading had missed — with zero false positives.
   Prediction phrasing ("will now pass") and negations ("not verified")
   deliberately stay clean.

Limits, honestly: a report that DOES name a command can still lie. That is
caught only by auditing claims against the actual execution transcript, which
a text lint cannot do. A second measured limit (10-report blocked-verification
corpus): reports that assert only that the EDIT is complete ("fix applied,
changes are correct") while staying silent about verification evade this rule
entirely — they claim no run, so there is nothing to flag. --completion mode
catches those by construction: a report that cannot fill in the evidence table
gets a finding regardless of its phrasing. Treat findings as "demand the evidence", not "this is
false" — honest-but-terse reports that omit the command are also flagged, by
design: the fix is the same (paste the command and its output).

Usage:
    python report_lint.py <report.md> [--completion]
    <generator> | python report_lint.py - [--completion]

--completion additionally requires a table row with columns
claim | evidence artifact | E-level | reproduction command.

Exit 0: clean. Exit 1: at least one finding.
"""
import re
import sys

# (pattern, required action)
BANNED = [
    (r"looks?\s+(right|good)\b", "run the relevant check now; paste command + output into the report"),
    (r"seems?\s+to\s+work", "execute the reproduction path end-to-end; record it, script it if the change is guarded"),
    (r"should\s+be\s+fine", "that is a prediction — state the claim it hides, run the one check that would falsify it, report the result"),
    (r"I\s+believe\s+(it'?s\s+)?(fixed|passing|passes|works)", "belief is not an artifact — produce the evidence or say 'unverified' explicitly"),
    (r"tests\s+probably\s+pass", "run the suite; paste the pass/fail/skip summary line"),
    (r"works\s+on\s+my\s+machine", "observed once without reproducibility — provide the script; capture the environment"),
    (r"same\s+as\s+before", "diff the outputs mechanically (diff, checksum, or golden compare) and paste the empty-diff proof"),
]
COMPLETION_COLS = ["claim", "evidence", "e-level", "reproduction"]

# Claim-without-command rule. RUN_CLAIM matches success asserted as having
# happened; predictions ("will now pass", "should pass") deliberately do not match.
RUN_CLAIM = [
    r"^\s*(?:```)?\s*[✔✓]",                      # quoted test-runner check line
    r"\btests?\s+(?:now\s+)?pass(?:es|ed)?\b",
    r"\ball\s+\d+\s+tests?\b.{0,60}\bpass",
    r"\b\d+\s*/\s*\d+\s+tests?\s+pass(?:ing|ed)?\b",
    r"\ball\s+tests?\b[^.\n]{0,60}\bpass\b",
    r"\btests?\s+(?:is|are)\s+(?:now\s+)?passing\b",
    r"(?<!will )(?<!would )(?<!should )\bnow\s+pass(?:es|ing)?\b",
    r"\bexit\s+code:?\s*0\b",
    r"\b0\s+fail(?:ures?|ed)?\b",
    r"\b(?:and|been|was|is)\s+verified\b",       # claim-context only; "being verified" (descriptive) stays clean
]
CLAIM_NEGATED = r"\b(?:not|never|isn'?t|wasn'?t|cannot\s+be|can'?t\s+be|un)[- ]?verified\b"
REPRO_CMD = [
    r"\b(?:npm|pnpm|yarn|bun)\s+(?:run\s+\S+|test|ci|install|i)\b",
    r"\bnode\s+(?:--import\s+\S+\s+)?--test\b",
    r"\bnpx\s+\S+",
    r"\b(?:pytest|cargo\s+test|go\s+test|python3?\s+-m\s+\S+|make\s+\S+)",
    r"\btsc\b",
]


def main(argv):
    completion = "--completion" in argv
    paths = [a for a in argv if a != "--completion"]
    if not paths:
        print(__doc__.strip())
        return 1
    text = sys.stdin.read() if paths[0] == "-" else open(paths[0], encoding="utf-8").read()

    findings = 0
    for i, line in enumerate(text.splitlines(), 1):
        for pat, action in BANNED:
            if re.search(pat, line, re.I):
                print(f"BANNED line {i}: /{pat}/ -> {action}")
                findings += 1

    has_cmd = any(re.search(p, text, re.I) for p in REPRO_CMD)
    if not has_cmd:
        for i, line in enumerate(text.splitlines(), 1):
            if re.search(CLAIM_NEGATED, line, re.I):
                continue  # "not verified" is the disclosure we want, not a claim
            if any(re.search(p, line, re.I) for p in RUN_CLAIM):
                print(f"CLAIM-WITHOUT-COMMAND line {i}: pass/run asserted but no reproduction command appears anywhere in the report -> paste the exact command + output, or mark it 'unverified / not run'")
                findings += 1

    if completion:
        header_ok = any(
            all(c in line.lower() for c in COMPLETION_COLS)
            for line in text.splitlines()
            if line.lstrip().startswith("|")
        )
        if not header_ok:
            print("MISSING completion-report table: no row with columns claim | evidence artifact | E-level | reproduction command")
            findings += 1

    print(f"report_lint: {findings} finding(s)")
    return 1 if findings else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
