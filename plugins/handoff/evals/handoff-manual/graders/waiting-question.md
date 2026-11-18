---
type: llm
focus: trace
---
Judge the handoff file written or edited under docs/handoffs/ in this run (the content of the Write or Edit tool calls in the trace); ignore everything else in the trace. PASS if the handoff lists, as still waiting on the user, whether the cleanup job should use cron or a systemd timer, with a recommendation. FAIL if the question is missing or presented as decided.
