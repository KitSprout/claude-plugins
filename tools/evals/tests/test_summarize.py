from __future__ import annotations

import copy
import json
import sys
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))

import summarize as S  # noqa: E402

FIXTURE = HERE / "fixtures" / "aggregate-small.json"

KW = dict(plugin="handoff", plugin_version="0.2.0", plugin_commit="abc1234",
          suite=2, traps=[], model="sonnet", judge="sonnet",
          date="2026-11-18", skill_bytes=1000, notes=[])


def load():
    return json.loads(FIXTURE.read_text())


class SummarizeTests(unittest.TestCase):
    def test_counts_passed_and_scored(self):
        out = S.summarize(load(), **KW)
        g = out["cases"]["handoff-continued"]["graders"]["continues-from"]
        self.assertEqual(g, {"passed": 2, "scored": 2})
        self.assertEqual(out["format"], 1)
        self.assertEqual(out["claude_code"], "2.1.323")

    def test_error_run_counts_as_no_pass(self):
        out = S.summarize(load(), **KW)
        c = out["cases"]["handoff-manual"]
        self.assertEqual(c["errors"], 1)
        self.assertEqual(c["runs"], 2)
        self.assertEqual(c["graders"]["no-secret"], {"passed": 1, "scored": 2})

    def test_missing_field_stops(self):
        r = load()
        del r["cases"][0]["arms"]
        with self.assertRaises(SystemExit) as cm:
            S.summarize(r, **KW)
        self.assertIn("cases[0].arms", str(cm.exception))

    def test_partial_is_kept(self):
        r = load()
        r["partial"] = True
        self.assertTrue(S.summarize(r, **KW)["partial"])

    def test_costs_summed(self):
        r = load()
        out = S.summarize(r, **KW)
        for c in r["cases"]:
            runs = c["arms"]["with"]
            agent = round(sum(x["costUsd"] - x["judgeCostUsd"] for x in runs), 3)
            judge = round(sum(x["judgeCostUsd"] for x in runs), 3)
            self.assertEqual(out["cases"][c["name"]]["agent_cost_usd"], agent)
            self.assertEqual(out["cases"][c["name"]]["judge_cost_usd"], judge)

    def test_no_paths_in_output(self):
        r = load()
        r["suite"]["root"] = "/Users/x/proj/plugins/handoff"
        r["suite"]["plugins"][0]["path"] = "/private/var/folders/x/handoff"
        text = json.dumps(S.summarize(r, **KW))
        for bad in ("/private/", "/var/folders/", "/Users/"):
            self.assertNotIn(bad, text)

    def test_judge_mismatch_stops(self):
        with self.assertRaises(SystemExit):
            S.summarize(load(), **{**KW, "judge": "opus"})

    def test_notes_keep_order(self):
        out = S.summarize(load(), **{**KW, "notes": ["b", "a"]})
        self.assertEqual(out["notes"], ["b", "a"])

    def _plugin_dir(self, tmp):
        pd = Path(tmp) / "plugins" / "demo"
        (pd / ".claude-plugin").mkdir(parents=True)
        (pd / "evals").mkdir()
        (pd / ".claude-plugin" / "plugin.json").write_text('{"version": "1.2.3"}')
        (pd / "evals" / "suite.json").write_text(
            json.dumps({"suite": 2, "traps": ["a/b"], "changes": []}))
        return pd

    def _run(self, pd, out, *extra):
        S.main([str(FIXTURE), "--plugin-dir", str(pd), "--model", "sonnet",
                "--judge", "sonnet", "--plugin-commit", "abc1234",
                "--skill-bytes", "5", "--out", str(out), *extra])

    def test_cli_filename_overwrite_traps(self):
        import contextlib
        import io
        import tempfile
        with tempfile.TemporaryDirectory() as tmp:
            pd = self._plugin_dir(tmp)
            out = Path(tmp) / "out"
            with contextlib.redirect_stdout(io.StringIO()):
                self._run(pd, out)
                f = out / "1.2.3__suite-2__sonnet__2026-11-18.json"
                self.assertTrue(f.exists())
                data = json.loads(f.read_text())
                self.assertEqual(data["traps"], ["a/b"])
                with self.assertRaises(SystemExit):
                    self._run(pd, out)
                self._run(pd, out, "--suite", "99", "--note", "n1")
            d99 = json.loads(
                (out / "1.2.3__suite-99__sonnet__2026-11-18.json").read_text())
            self.assertEqual(d99["traps"], [])
            self.assertEqual(d99["notes"], ["n1", "traps not defined for suite 99"])

    def test_cli_label_writes_a_second_file(self):
        import contextlib
        import io
        import tempfile
        with tempfile.TemporaryDirectory() as tmp:
            pd = self._plugin_dir(tmp)
            out = Path(tmp) / "out"
            with contextlib.redirect_stdout(io.StringIO()):
                self._run(pd, out)
                self._run(pd, out, "--label", "corrected", "--note", "fix")
                with self.assertRaises(SystemExit):
                    self._run(pd, out, "--label", "corrected")
                with self.assertRaises(SystemExit):
                    self._run(pd, out, "--label", "a/b")
                with self.assertRaises(SystemExit) as cm:
                    self._run(pd, out, "--label", "")
                self.assertIn("non-empty", str(cm.exception))
            plain = json.loads((out / "1.2.3__suite-2__sonnet__2026-11-18.json").read_text())
            self.assertNotIn("label", plain)
            lab = json.loads(
                (out / "1.2.3__suite-2__sonnet__2026-11-18__corrected.json").read_text())
            self.assertEqual(lab["label"], "corrected")
            self.assertEqual(lab["notes"], ["fix"])


if __name__ == "__main__":
    unittest.main()
