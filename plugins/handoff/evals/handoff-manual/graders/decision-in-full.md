---
type: llm
focus: trace
---
Judge the handoff file written or edited under docs/handoffs/ in this run (the content of the Write or Edit tool calls in the trace); ignore everything else in the trace. PASS if the handoff states this session's decision itself (keep data 90 days, CSV only, no SQLite), not only a pointer to docs/decisions.md. FAIL otherwise.
