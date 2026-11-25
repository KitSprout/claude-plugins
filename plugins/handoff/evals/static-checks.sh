#!/bin/bash
# Checks that need no model: what the SessionStart hook prints for each `auto`
# value and in a cloud session, and how much context the skills cost.
# Usage: static-checks.sh [plugin dir]
p="${1:-$(cd "$(dirname "$0")/.." && pwd)}"
skill="$p/skills/handoff/SKILL.md"
rescue="$p/skills/rescue/SKILL.md"
hook() { env -u CLAUDE_CODE_REMOTE "$@" /bin/sh "$p/hooks/auto-context"; }
fail=0
for v in off OFF Off false no 0 empty unset; do
  case $v in unset) out=$(hook -u CLAUDE_PLUGIN_OPTION_AUTO);; empty) out=$(hook CLAUDE_PLUGIN_OPTION_AUTO=);; *) out=$(hook CLAUDE_PLUGIN_OPTION_AUTO=$v);; esac
  [ -z "$out" ] && echo "PASS auto=$v prints nothing" || { echo "FAIL auto=$v printed text"; fail=1; }
done
out=$(hook CLAUDE_PLUGIN_OPTION_AUTO=on CLAUDE_CODE_REMOTE=true)
[ -z "$out" ] && echo "PASS auto=on in a cloud session prints nothing" || { echo "FAIL auto=on in a cloud session printed text"; fail=1; }
for v in on On ON; do
  out=$(hook CLAUDE_PLUGIN_OPTION_AUTO=$v)
  case "$out" in *"automatic handoff updates are on"*) echo "PASS auto=$v prints the note (${#out} chars)";; *) echo "FAIL auto=$v"; fail=1;; esac
done
d=$(python3 -c 'import json,sys; print(json.load(open(sys.argv[1]))["userConfig"]["auto"]["default"])' "$p/.claude-plugin/plugin.json")
[ "$d" = off ] && echo "PASS plugin.json auto default is off" || { echo "FAIL plugin.json auto default is $d"; fail=1; }
grep -qF 'auto to `off`' "$skill" && echo "PASS SKILL.md says auto defaults to off" || { echo "FAIL SKILL.md default sentence"; fail=1; }
desc=$(awk '/^description:/{f=1;next} f&&/^[a-z-]+:/{f=0} f' "$skill" | tr -s ' \n' ' ')
desc="${desc# }"; desc="${desc% }"
echo "SKILL.md: $(wc -c <"$skill" | tr -d ' ') bytes, $(wc -w <"$skill" | tr -d ' ') words; description: ${#desc} chars"
echo "rescue SKILL.md: $(wc -c <"$rescue" | tr -d ' ') bytes, $(wc -w <"$rescue" | tr -d ' ') words"
exit $fail
