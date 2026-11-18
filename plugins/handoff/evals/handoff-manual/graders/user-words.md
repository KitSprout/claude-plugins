---
type: llm
focus: trace
---
Judge the handoff file written or edited under docs/handoffs/ in this run (the content of the Write or Edit tool calls in the trace); ignore everything else in the trace. PASS if the handoff quotes the user's own words for at least one of: the retention decision ("keep data for 90 days only…") or the rule about deletions ("ask me before anything that deletes data…"). FAIL if neither is quoted.
