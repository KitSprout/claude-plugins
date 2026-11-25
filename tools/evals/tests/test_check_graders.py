from __future__ import annotations

import sys
import tempfile
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))

import check_graders as G  # noqa: E402


def make(tmp, name, pattern, match=None, flags=None, quote="'",
         pass_text=None, fail_text=None, extra=""):
    gdir = Path(tmp) / "graders"
    (gdir / "selftest").mkdir(parents=True, exist_ok=True)
    lines = ["---", "type: regex", "target: trace"]
    lines.append(f"pattern: {quote}{pattern}{quote}")
    if match:
        lines.append(f"match: {match}")
    if flags:
        lines.append(f"flags: {flags}")
    if extra:
        lines.append(extra)
    lines += ["---", "body"]
    path = gdir / f"{name}.md"
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    if pass_text is not None:
        (gdir / "selftest" / f"{name}.pass.txt").write_text(pass_text, encoding="utf-8")
    if fail_text is not None:
        (gdir / "selftest" / f"{name}.fail.txt").write_text(fail_text, encoding="utf-8")
    return path


class CheckTests(unittest.TestCase):
    def setUp(self):
        self._t = tempfile.TemporaryDirectory()
        self.tmp = self._t.name
        self.addCleanup(self._t.cleanup)

    def test_missing_samples_reported(self):
        p = make(self.tmp, "g", "abc")
        problems = G.check(p)
        self.assertEqual(len(problems), 2)
        self.assertTrue(all(str(p) in x for x in problems))

    def test_contains_semantics(self):
        p = make(self.tmp, "g", "abc", pass_text="xabcx", fail_text="xyz")
        self.assertEqual(G.check(p), [])
        p = make(self.tmp, "g", "abc", pass_text="xyz", fail_text="xyz")
        self.assertEqual(len(G.check(p)), 1)
        p = make(self.tmp, "g", "abc", pass_text="abc", fail_text="abc")
        self.assertEqual(len(G.check(p)), 1)

    def test_not_contains_semantics(self):
        p = make(self.tmp, "g", "secret", match="not_contains",
                 pass_text="clean", fail_text="has secret")
        self.assertEqual(G.check(p), [])
        p = make(self.tmp, "g", "secret", match="not_contains",
                 pass_text="has secret", fail_text="clean")
        self.assertEqual(len(G.check(p)), 2)

    def test_count_semantics(self):
        p = make(self.tmp, "g", "ab", match="count:2",
                 pass_text="ab ab", fail_text="ab ab ab")
        self.assertEqual(G.check(p), [])
        p = make(self.tmp, "g", "ab", match="count:2",
                 pass_text="ab", fail_text="ab ab")
        self.assertEqual(len(G.check(p)), 2)

    def test_inline_flag_rejected(self):
        p = make(self.tmp, "g", "(?i)abc", pass_text="ABC", fail_text="x")
        problems = G.check(p)
        self.assertEqual(len(problems), 1)
        self.assertIn("inline", problems[0])

    def test_lookaround_allowed(self):
        p = make(self.tmp, "g", "a(?=b)(?:b)", pass_text="ab", fail_text="ac")
        self.assertEqual(G.check(p), [])

    def test_ascii_digits(self):
        p = make(self.tmp, "g", r"\d", pass_text="3", fail_text="٣")
        self.assertEqual(G.check(p), [])

    def test_flag_i_and_unknown_flag(self):
        p = make(self.tmp, "g", "abc", flags="i", pass_text="ABC", fail_text="x")
        self.assertEqual(G.check(p), [])
        p = make(self.tmp, "g", "abc", flags="is", pass_text="ABC", fail_text="x")
        self.assertEqual(len(G.check(p)), 1)

    def test_unknown_match_value(self):
        p = make(self.tmp, "g", "abc", match="exactly", pass_text="abc", fail_text="x")
        self.assertEqual(len(G.check(p)), 1)

    def test_quoting_styles(self):
        p = make(self.tmp, "g", "it''s", pass_text="it's", fail_text="its")
        self.assertEqual(G.check(p), [])
        p = make(self.tmp, "g", r"a\\d\"", quote='"', pass_text='a5"', fail_text='a\\5"')
        self.assertEqual(G.check(p), [])

    def test_inline_target_mapping_ignored(self):
        p = make(self.tmp, "g", "abc", pass_text="abc", fail_text="x",
                 extra="target: {source: file, path: docs/x.md}")
        self.assertEqual(G.check(p), [])

    def test_non_regex_ignored(self):
        gdir = Path(self.tmp) / "graders"
        gdir.mkdir()
        p = gdir / "q.md"
        p.write_text("---\ntype: llm\n---\nbody\n", encoding="utf-8")
        self.assertEqual(G.check(p), [])

    def test_unterminated_frontmatter_reported(self):
        gdir = Path(self.tmp) / "graders"
        gdir.mkdir()
        p = gdir / "u.md"
        p.write_text("---\ntype: regex\npattern: 'abc'\nbody\n", encoding="utf-8")
        problems = G.check(p)
        self.assertEqual(len(problems), 1)
        self.assertIn("unterminated frontmatter", problems[0])

    def test_bad_regex(self):
        p = make(self.tmp, "g", "(abc", pass_text="abc", fail_text="x")
        self.assertEqual(len(G.check(p)), 1)

    def test_main_restricts_to_folder(self):
        plugin = Path(self.tmp) / "plugins" / "p" / "evals" / "c"
        plugin.mkdir(parents=True)
        make(plugin, "g", "abc")
        self.assertEqual(G.main([str(Path(self.tmp) / "plugins" / "p")]), 1)
        make(plugin, "g", "abc", pass_text="abc", fail_text="x")
        self.assertEqual(G.main([str(Path(self.tmp) / "plugins" / "p")]), 0)


if __name__ == "__main__":
    unittest.main()
