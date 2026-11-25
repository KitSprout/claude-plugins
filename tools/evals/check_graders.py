"""Self-test every ``type: regex`` eval grader against two sample files.

A regex grader that can never fail goes unnoticed, so each one carries
``graders/selftest/<grader>.pass.txt`` (the grader must pass on it) and
``graders/selftest/<grader>.fail.txt`` (it must fail). Model-free, stdlib only.

Only ``type``, ``pattern``, ``flags`` and ``match`` of the frontmatter are
read; other keys (including ``target``) are ignored. ``flags`` supports only
``i``. Patterns compile with ``re.ASCII``. Inline flag groups are rejected:
any ``(?`` not followed by ``:``, ``=``, ``!``, ``<=`` or ``<!`` is a problem,
which also rejects named groups such as ``(?P<n>...)`` and ``(?<n>...)``.

Usage: check_graders.py [PLUGIN_FOLDER]   (run from the repository root)
Baseline files are never checked.
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

WANTED = ("type", "pattern", "flags", "match")


def _unquote(raw: str) -> str:
    raw = raw.strip()
    if len(raw) >= 2 and raw[0] == "'" and raw[-1] == "'":
        return raw[1:-1].replace("''", "'")
    if len(raw) >= 2 and raw[0] == '"' and raw[-1] == '"':
        out, i, body = [], 0, raw[1:-1]
        while i < len(body):
            if body[i] == "\\" and i + 1 < len(body) and body[i + 1] in '\\"':
                out.append(body[i + 1])
                i += 2
            else:
                out.append(body[i])
                i += 1
        return "".join(out)
    return raw


def parse_frontmatter(text: str) -> dict[str, str]:
    lines = text.splitlines()
    if not lines or lines[0].strip() != "---":
        return {}
    fm: dict[str, str] = {}
    for line in lines[1:]:
        if line.strip() == "---":
            return fm
        m = re.match(r"([A-Za-z_][\w-]*):\s*(.*)$", line)
        if m and m.group(1) in WANTED:
            fm[m.group(1)] = _unquote(m.group(2))
    raise ValueError("unterminated frontmatter")


def has_inline_flags(pattern: str) -> bool:
    i, in_class = 0, False
    while i < len(pattern):
        c = pattern[i]
        if c == "\\":
            i += 2
            continue
        if in_class:
            if c == "]":
                in_class = False
        elif c == "[":
            in_class = True
            if pattern[i + 1:i + 2] == "^":
                i += 1
            if pattern[i + 1:i + 2] == "]":
                i += 1
        elif c == "(" and pattern[i + 1:i + 2] == "?":
            rest = pattern[i + 2:]
            if not (rest[:1] in (":", "=", "!") or rest[:2] in ("<=", "<!")):
                return True
        i += 1
    return False


def check(grader_path: Path) -> list[str]:
    grader_path = Path(grader_path)
    name = str(grader_path)
    try:
        fm = parse_frontmatter(grader_path.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError) as e:
        return [f"{name}: cannot read grader ({e})"]
    except ValueError as e:
        return [f"{name}: {e}"]
    if fm.get("type") != "regex":
        return []
    problems: list[str] = []
    pattern = fm.get("pattern")
    if not pattern:
        return [f"{name}: regex grader has no pattern"]

    flags = re.ASCII
    for ch in fm.get("flags", ""):
        if ch == "i":
            flags |= re.IGNORECASE
        else:
            problems.append(f"{name}: unsupported flag {ch!r} (only 'i')")
    if has_inline_flags(pattern):
        problems.append(f"{name}: inline flag group in pattern (use the flags field)")

    match = fm.get("match", "contains")
    count = None
    if match.startswith("count:"):
        try:
            count = int(match[6:])
            if count < 0:
                raise ValueError
        except ValueError:
            problems.append(f"{name}: invalid match {match!r}")
    elif match not in ("contains", "not_contains"):
        problems.append(f"{name}: unknown match {match!r}")

    rx = None
    try:
        rx = re.compile(pattern, flags)
    except re.error as e:
        problems.append(f"{name}: pattern does not compile ({e})")

    samples = {}
    for kind in ("pass", "fail"):
        sp = grader_path.parent / "selftest" / f"{grader_path.stem}.{kind}.txt"
        try:
            samples[kind] = sp.read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError):
            problems.append(f"{name}: missing or unreadable sample {sp}")
    if problems or rx is None:
        return problems

    def passes(text: str) -> bool:
        if count is not None:
            return len(rx.findall(text)) == count
        found = rx.search(text) is not None
        return found if match == "contains" else not found

    if not passes(samples["pass"]):
        problems.append(f"{name}: grader does not pass on its .pass.txt sample")
    if passes(samples["fail"]):
        problems.append(f"{name}: grader does not fail on its .fail.txt sample")
    return problems


def main(argv: list[str] | None = None) -> int:
    args = sys.argv[1:] if argv is None else argv
    if args:
        graders = sorted(Path(args[0]).glob("evals/*/graders/*.md"))
    else:
        graders = sorted(Path(".").glob("plugins/*/evals/*/graders/*.md"))
    problems: list[str] = []
    for g in graders:
        problems.extend(check(g))
    for p in problems:
        print(p)
    print(f"{len(problems)} problem(s) in {len(graders)} grader file(s)")
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main())
