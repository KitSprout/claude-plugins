#!/bin/bash
# Checks that need no model: what the SessionStart hook prints for each `auto`
# value, and how much context the skill costs. Usage: static-checks.sh [plugin dir]
p="${1:-$(cd "$(dirname "$0")/.." && pwd)}"
skill="$p/skills/handoff/SKILL.md"
fail=0
for v in off OFF Off; do
  out=$(CLAUDE_PLUGIN_OPTION_AUTO=$v /bin/sh "$p/hooks/auto-context")
  [ -z "$out" ] && echo "PASS auto=$v prints nothing" || { echo "FAIL auto=$v printed text"; fail=1; }
done
for v in on unset; do
  if [ $v = unset ]; then out=$(env -u CLAUDE_PLUGIN_OPTION_AUTO /bin/sh "$p/hooks/auto-context"); else out=$(CLAUDE_PLUGIN_OPTION_AUTO=$v /bin/sh "$p/hooks/auto-context"); fi
  case "$out" in *"automatic handoff updates are on"*) echo "PASS auto=$v prints the note (${#out} chars)";; *) echo "FAIL auto=$v"; fail=1;; esac
done
desc=$(awk '/^description:/{f=1;next} f&&/^[a-z-]+:/{f=0} f' "$skill" | tr -s ' \n' ' ')
echo "SKILL.md: $(wc -c <"$skill" | tr -d ' ') bytes, $(wc -w <"$skill" | tr -d ' ') words; description: ${#desc} chars"
exit $fail
