"""Compare two eval summaries (see TESTING.md, "Comparing").

Usage:
  python3 tools/evals/compare.py BASE.json NEW.json

Prints a Markdown table (case, grader, before, after, verdict), skill bytes and
agent cost per run (before -> after), then notes. Exit 2 refused (different
suite or agent model, or a partial summary), 1 blocking (a trap failed, or a
trap has no scored run in the new summary), 0 otherwise; regressions alone do
not change the exit code.
"""
from __future__ import annotations

import json
import sys


def _rate(g):
    return g["passed"] / g["scored"] if g["scored"] else 0.0


def _fmt(g):
    return "-" if g is None else "%d/%d" % (g["passed"], g["scored"])


def _verdict(case, grader, b, n, traps):
    trap = "%s/%s" % (case, grader) in traps
    if trap and (n is None or not n["scored"]):
        return "trap-missing"
    if n is None:
        return "removed"
    if trap and n["passed"] < n["scored"]:
        return "trap-failed"
    if case.startswith("nearmiss-") and n["passed"] < n["scored"]:
        return "regression"
    if case.startswith("trigger-") and n["scored"] - n["passed"] >= 2:
        return "regression"
    if b is None:
        return "new"
    rb, rn = _rate(b), _rate(n)
    if rn > rb:
        return "improved"
    if rn == rb:
        return "same"
    return "regression" if rb - rn >= 0.5 else "noise"


def compare(base, new):
    out = {"refused": None, "blocking": False, "regressions": 0,
           "notes": [], "rows": []}
    reasons = []
    if base.get("suite") != new.get("suite"):
        reasons.append("suite differs (%s vs %s)"
                       % (base.get("suite"), new.get("suite")))
    if base.get("model") != new.get("model"):
        reasons.append("model differs (%s vs %s)"
                       % (base.get("model"), new.get("model")))
    if base.get("partial") or new.get("partial"):
        reasons.append("partial summary")
    if reasons:
        out["refused"] = "refused: " + "; ".join(reasons)
        return out

    traps = set(new.get("traps", []))
    bcases, ncases = base.get("cases", {}), new.get("cases", {})
    differ = base.get("runs") != new.get("runs")
    for case in sorted(set(bcases) | set(ncases)):
        bc, nc = bcases.get(case), ncases.get(case)
        if bc and nc and bc.get("runs") != nc.get("runs"):
            differ = True
        bg = (bc or {}).get("graders", {})
        ng = (nc or {}).get("graders", {})
        for grader in sorted(set(bg) | set(ng)):
            b, n = bg.get(grader), ng.get(grader)
            v = _verdict(case, grader, b, n, traps)
            if v == "regression":
                out["regressions"] += 1
            elif v in ("trap-failed", "trap-missing"):
                out["blocking"] = True
            elif v == "noise":
                out["notes"].append("%s/%s: small drop (%s -> %s), noise"
                                    % (case, grader, _fmt(b), _fmt(n)))
            out["rows"].append({"case": case, "grader": grader,
                                "before": _fmt(b), "after": _fmt(n),
                                "verdict": v})
    seen = {"%s/%s" % (r["case"], r["grader"]) for r in out["rows"]}
    for t in sorted(traps - seen):
        case, _, grader = t.partition("/")
        out["blocking"] = True
        out["rows"].append({"case": case, "grader": grader, "before": "-",
                            "after": "-", "verdict": "trap-missing"})
    if differ:
        out["notes"].append("run counts differ between the summaries; "
                            "compared by pass rate")
    return out


def _cost_per_run(s):
    cases = s.get("cases", {}).values()
    runs = sum(c.get("runs", 0) for c in cases)
    cost = sum(c.get("agent_cost_usd", 0.0) for c in cases)
    return cost / runs if runs else 0.0


def main(argv=None):
    argv = sys.argv[1:] if argv is None else argv
    if len(argv) != 2:
        print(__doc__.strip(), file=sys.stderr)
        return 2
    with open(argv[0]) as f:
        base = json.load(f)
    with open(argv[1]) as f:
        new = json.load(f)
    res = compare(base, new)
    if res["refused"]:
        print(res["refused"])
        return 2
    print("| case | grader | before | after | verdict |")
    print("|---|---|---|---|---|")
    for r in res["rows"]:
        print("| %s | %s | %s | %s | %s |" % (
            r["case"], r["grader"], r["before"], r["after"], r["verdict"]))
    print()
    print("Skill bytes: %s -> %s" % (base.get("skill_bytes"),
                                     new.get("skill_bytes")))
    print("Agent cost per run: $%.4f -> $%.4f" % (_cost_per_run(base),
                                                  _cost_per_run(new)))
    if res["notes"]:
        print()
        for n in res["notes"]:
            print("- " + n)
    print()
    print("Regressions: %d; blocking: %s" % (res["regressions"],
                                             "yes" if res["blocking"] else "no"))
    return 1 if res["blocking"] else 0


if __name__ == "__main__":
    sys.exit(main())
