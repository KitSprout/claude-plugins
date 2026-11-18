# Sources behind the rules

For maintaining the skill; a debate does not need this file. Pages opened and checked on 2026-11-17 (abstract pages for arXiv papers).

| Rule in SKILL.md | Source | What it found |
|---|---|---|
| Independent first reports matter more than rounds of argument | [Debate or Vote](https://arxiv.org/abs/2508.17536) (NeurIPS 2025) | on seven benchmarks, majority voting alone accounts for most of the gains credited to multi-agent debate |
| Same | [Stop Overvaluing Multi-Agent Debate](https://arxiv.org/abs/2502.08788) (2025) | five debate methods often fail to beat single-agent baselines such as self-consistency; argues for mixing models |
| A judge from another model than the debaters | [Replacing Judges with Juries](https://arxiv.org/abs/2404.18796) (2024) | a panel of smaller models from other families beats one large judge and shows less intra-model bias; it tested different model families, not two models of one vendor |
| No weaker models as default debaters | [Rethinking Mixture-of-Agents](https://arxiv.org/abs/2502.00674) (2025) | mixing in weaker models when generating answers often lowers quality |
| Reviewers do not see the author's reasoning | [Chain-of-Verification](https://arxiv.org/abs/2309.11495) (2023) | answering verification questions independently, so answers are not biased by other responses, reduces hallucination |
| Verification is a step of its own | [Why Do Multi-Agent LLM Systems Fail?](https://arxiv.org/abs/2503.13657) (2025) | multi-agent gains over single agents are often minimal; missing or incorrect verification is one of three failure classes |
| No single consensus; the judge rules | [Beyond Consensus](https://arxiv.org/abs/2608.30373) (Findings of EMNLP 2026) | in subjective evaluation a single judge aligned best with human ratings; consensus-style debate degraded alignment |
| Selection by a judge | [When Agents Disagree](https://arxiv.org/abs/2603.20324) (Applied Sciences 2026) | a diverse team with judge-based selection won 0.810 against a single model, a homogeneous team 0.512 |
| A judge rules on the debaters' reports | [On scalable oversight with weak LLMs judging strong LLMs](https://arxiv.org/abs/2407.04622) (2024) | debate beat consultancy on all tasks when the consultant's side was randomly assigned; against direct answering it won on extractive QA with information asymmetry and was mixed elsewhere |

Shown failures in past debates (one machine, November 2026) are summarised in the rules themselves; measured runs are in `usage.md`.
