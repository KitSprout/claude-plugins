"""Checks the handoff-auto-first `tool_used` patterns against known outputs.

The four graders match one Write call by its `input_match`, which the eval
runner tests (JavaScript RegExp, no flags) against the tool input serialized
as compact JSON on one line. These patterns use only syntax that Python `re`
reads the same way, so Python checks them here. Samples are kept in this file.
"""
from __future__ import annotations

import json
import re
import sys
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))

import check_graders as G  # noqa: E402

GRADERS = HERE.parents[2] / "plugins" / "handoff" / "evals" / "handoff-auto-first" / "graders"
NAMES = ("goal-and-scope", "user-rules", "not-saved-elsewhere", "continues-read-first")
NEW = "/workspace/docs/handoffs/2026-11-25-1432-humidity.md"
EARLIER = "/workspace/docs/handoffs/2026-11-16-0900-station.md"

GOOD_CREATE = """# Handoff: humidity sensor
Written 2026-11-25 14:32. Project: ~/weather-station. Session: 99999999-aaaa-4bbb-8ccc-dddddddddddd.
Continues from: docs/handoffs/2026-11-16-0900-station.md; read it first; this file holds only what changed since

## Goal and scope
Connect the humidity sensor to station/logger.py.

## The user's rules
- "Ask me before installing anything on the Pi."

## Where things stand
read_humidity() added to station/logger.py; not committed.

## Next steps
waiting for the user

## Waiting on the user
- Timestamps in UTC or local time? Recommendation: UTC. (carried over)

## What changed
- station/logger.py: read_humidity() (uncommitted).

## Not yet saved elsewhere
- The rule about installing (only in this handoff).
"""

# What 0.2.0's low level writes when it creates the file: six sections, the plain Continues-from line.
OLD_STYLE_LOW_CREATE = """# Handoff: humidity sensor
Written 2026-11-25 14:32. Project: /workspace. Session: 99999999-aaaa-4bbb-8ccc-dddddddddddd.
Continues from: docs/handoffs/2026-11-16-0900-station.md

## Where things stand
read_humidity() added to station/logger.py; not committed. The user asked to be asked before installing anything on the Pi.

## Next steps
waiting for the user

## Waiting on the user
- Timestamps in UTC or local time? Recommendation: UTC.

## Decisions
- none this session

## Tried or rejected (don't propose again)
- Polling the sensor over Bluetooth: the range was too short in the garden (carried over).

## What changed
- station/logger.py: read_humidity() (uncommitted).
"""

# The rule appears, but not under "The user's rules".
RULE_ELSEWHERE = GOOD_CREATE.replace(
    '## The user\'s rules\n- "Ask me before installing anything on the Pi."',
    "## The user's rules\n- Keep each change small.",
).replace(
    "## Next steps\nwaiting for the user",
    "## Next steps\nAsk before installing anything on the Pi; then wait for the user.",
)


def write_input(path: str, content: str) -> str:
    """The runner's inputText for a Write call: compact JSON on one line."""
    return json.dumps({"file_path": path, "content": content}, separators=(",", ":"), ensure_ascii=False)


def load_pattern(name: str) -> "re.Pattern[str]":
    text = (GRADERS / f"{name}.md").read_text(encoding="utf-8")
    for line in text.splitlines()[1:]:
        if line.strip() == "---":
            break
        m = re.match(r"input_match:\s*(.*)$", line)
        if m:
            return re.compile(G._unquote(m.group(1)))
    raise AssertionError(f"{name}.md has no input_match")


class HandoffAutoFirstPatterns(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.rx = {n: load_pattern(n) for n in NAMES}

    def check(self, text: str, expected: dict[str, bool]) -> None:
        for name, want in expected.items():
            with self.subTest(grader=name):
                self.assertEqual(self.rx[name].search(text) is not None, want)

    def test_good_create_passes_all(self) -> None:
        self.check(write_input(NEW, GOOD_CREATE), {n: True for n in NAMES})

    def test_old_style_low_create_fails_all(self) -> None:
        self.check(write_input(NEW, OLD_STYLE_LOW_CREATE), {n: False for n in NAMES})

    def test_writing_into_the_earlier_handoff_fails_all(self) -> None:
        self.check(write_input(EARLIER, GOOD_CREATE), {n: False for n in NAMES})

    def test_rule_outside_its_section_fails_user_rules_only(self) -> None:
        self.assertIn("installing anything", RULE_ELSEWHERE)
        self.check(write_input(NEW, RULE_ELSEWHERE), {
            "user-rules": False, "goal-and-scope": True, "not-saved-elsewhere": True, "continues-read-first": True})

    def test_curly_apostrophe_heading_passes_user_rules(self) -> None:
        self.check(write_input(NEW, GOOD_CREATE.replace("The user's rules", "The user’s rules")), {"user-rules": True})


if __name__ == "__main__":
    unittest.main()
