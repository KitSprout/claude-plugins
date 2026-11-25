from __future__ import annotations

import contextlib
import io
import json
import sys
import tempfile
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))

import compare as C  # noqa: E402


def summ(cases, suite=2, model="sonnet", partial=False, traps=(), runs=3,
         skill_bytes=1000):
    return {
        "format": 1, "plugin": "handoff", "suite": suite, "model": model,
        "runs": runs, "partial": partial, "skill_bytes": skill_bytes,
        "traps": list(traps), "notes": [],
        "cases": {
            name: {"runs": r, "errors": 0, "agent_cost_usd": 0.3,
                   "judge_cost_usd": 0.1,
                   "graders": {g: {"passed": p, "scored": s}
                               for g, (p, s) in gs.items()}}
            for name, (r, gs) in cases.items()
        },
    }


def one(case, p, s, r=3, **kw):
    return summ({case: (r, {"g": (p, s)})}, **kw)


def verdict(base, new):
    res = C.compare(base, new)
    return res, [row["verdict"] for row in res["rows"]]


class CompareTests(unittest.TestCase):
    def run_main(self, base, new):
        with tempfile.TemporaryDirectory() as d:
            paths = []
            for n, s in (("b.json", base), ("n.json", new)):
                p = Path(d) / n
                p.write_text(json.dumps(s))
                paths.append(str(p))
            out = io.StringIO()
            with contextlib.redirect_stdout(out):
                code = C.main(paths)
            return code, out.getvalue()

    def test_refuses_other_suite(self):
        base, new = one("c", 3, 3), one("c", 3, 3, suite=1)
        self.assertIn("suite", C.compare(base, new)["refused"])
        code, _ = self.run_main(base, new)
        self.assertEqual(code, 2)

    def test_refuses_other_model(self):
        r = C.compare(one("c", 3, 3), one("c", 3, 3, model="opus"))
        self.assertIn("model", r["refused"])

    def test_refuses_partial(self):
        r = C.compare(one("c", 3, 3), one("c", 3, 3, partial=True))
        self.assertIn("partial", r["refused"])
        r = C.compare(one("c", 3, 3, partial=True), one("c", 3, 3))
        self.assertIn("partial", r["refused"])

    def test_drop_of_two_is_regression(self):
        r, v = verdict(one("c", 3, 3), one("c", 1, 3))
        self.assertEqual(v, ["regression"])
        self.assertEqual(r["regressions"], 1)
        self.assertFalse(r["blocking"])

    def test_drop_of_one_is_noise(self):
        r, v = verdict(one("c", 3, 3), one("c", 2, 3))
        self.assertEqual(v, ["noise"])
        self.assertEqual(r["regressions"], 0)

    def test_improved_and_same(self):
        self.assertEqual(verdict(one("c", 1, 3), one("c", 3, 3))[1], ["improved"])
        self.assertEqual(verdict(one("c", 3, 3), one("c", 3, 3))[1], ["same"])

    def test_trap_failure_blocks(self):
        new = one("c", 2, 3, traps=["c/g"])
        r, v = verdict(one("c", 3, 3), new)
        self.assertEqual(v, ["trap-failed"])
        self.assertTrue(r["blocking"])
        self.assertEqual(r["regressions"], 0)
        # blocks even if the base was already failing
        r, v = verdict(one("c", 2, 3), new)
        self.assertEqual(v, ["trap-failed"])
        code, _ = self.run_main(one("c", 3, 3), new)
        self.assertEqual(code, 1)

    def test_trap_absent_blocks(self):
        # listed as a trap, but the case is missing from the new summary
        base = summ({"c": (3, {"g": (3, 3)}), "d": (3, {"x": (3, 3)})})
        new = summ({"d": (3, {"x": (3, 3)})}, traps=["c/g"])
        r, v = verdict(base, new)
        self.assertTrue(r["blocking"])
        self.assertIn(("c", "g", "trap-missing"),
                      [(x["case"], x["grader"], x["verdict"]) for x in r["rows"]])
        self.assertEqual(self.run_main(base, new)[0], 1)
        # absent from both summaries: still a row, still blocking
        r, _ = verdict(summ({"d": (3, {"x": (3, 3)})}), new)
        self.assertTrue(r["blocking"])
        self.assertIn("trap-missing", [x["verdict"] for x in r["rows"]])

    def test_trap_zero_scored_blocks(self):
        r, v = verdict(one("c", 3, 3), one("c", 0, 0, traps=["c/g"]))
        self.assertEqual(v, ["trap-missing"])
        self.assertTrue(r["blocking"])
        self.assertEqual(r["regressions"], 0)
        code, out = self.run_main(one("c", 3, 3), one("c", 0, 0, traps=["c/g"]))
        self.assertEqual(code, 1)
        self.assertIn("| c | g | 3/3 | 0/0 | trap-missing |", out)

    def test_trap_passing_is_not_flagged(self):
        r, v = verdict(one("c", 3, 3), one("c", 3, 3, traps=["c/g"]))
        self.assertEqual(v, ["same"])
        self.assertFalse(r["blocking"])

    def test_nearmiss_firing_is_regression(self):
        r, v = verdict(one("nearmiss-x", 3, 3), one("nearmiss-x", 2, 3))
        self.assertEqual(v, ["regression"])

    def test_trigger_miss_of_two(self):
        self.assertEqual(
            verdict(one("trigger-x", 3, 3), one("trigger-x", 1, 3))[1],
            ["regression"])
        self.assertEqual(
            verdict(one("trigger-x", 3, 3), one("trigger-x", 2, 3))[1],
            ["noise"])

    def test_nearmiss_failing_in_both_is_regression(self):
        r, v = verdict(one("nearmiss-x", 2, 3), one("nearmiss-x", 2, 3))
        self.assertEqual(v, ["regression"])

    def test_trigger_misses_regardless_of_base(self):
        r, v = verdict(one("trigger-x", 1, 3), one("trigger-x", 1, 3))
        self.assertEqual(v, ["regression"])

    def run_new(self, case, p, s, traps=()):
        base = summ({"other": (3, {"x": (3, 3)})})
        new = summ({"other": (3, {"x": (3, 3)}), case: (3, {"g": (p, s)})},
                   traps=traps)
        return C.compare(base, new)

    def test_new_failing_trap_blocks(self):
        r = self.run_new("c", 2, 3, traps=["c/g"])
        self.assertTrue(r["blocking"])
        self.assertIn("trap-failed", [x["verdict"] for x in r["rows"]])

    def test_new_nearmiss_firing_is_regression(self):
        self.assertEqual(self.run_new("nearmiss-x", 2, 3)["regressions"], 1)

    def test_new_trigger_missing_two_is_regression(self):
        self.assertEqual(self.run_new("trigger-x", 1, 3)["regressions"], 1)

    def test_new_passing_grader_is_new(self):
        r = self.run_new("trigger-x", 3, 3)
        self.assertEqual(r["regressions"], 0)
        self.assertIn("new", [x["verdict"] for x in r["rows"]])

    def test_trigger_single_run_drop_is_regression(self):
        self.assertEqual(
            verdict(one("trigger-x", 1, 1, r=1, runs=1),
                    one("trigger-x", 0, 1, r=1, runs=1))[1], ["regression"])
        self.assertEqual(
            verdict(one("trigger-x", 3, 3), one("trigger-x", 2, 3))[1],
            ["noise"])

    def test_new_and_removed_graders(self):
        base = summ({"c": (3, {"old": (3, 3), "both": (3, 3)})})
        new = summ({"c": (3, {"new": (3, 3), "both": (3, 3)})})
        r, _ = verdict(base, new)
        got = {row["grader"]: row["verdict"] for row in r["rows"]}
        self.assertEqual(got, {"old": "removed", "new": "new", "both": "same"})

    def test_runs_differ_compared_by_rate(self):
        r, v = verdict(one("c", 3, 3, r=3), one("c", 1, 1, r=1, runs=1))
        self.assertEqual(v, ["same"])
        self.assertTrue(any("run count" in n for n in r["notes"]))

    def test_cli_output(self):
        code, out = self.run_main(one("c", 3, 3), one("c", 2, 3))
        self.assertEqual(code, 0)
        self.assertIn("| c | g | 3/3 | 2/3 | noise |", out)
        self.assertIn("1000 -> 1000", out)
        self.assertIn("$0.1000 -> $0.1000", out)


if __name__ == "__main__":
    unittest.main()
