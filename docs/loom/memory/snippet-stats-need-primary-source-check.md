---
name: snippet-stats-need-primary-source-check
description: A web-search snippet paraphrasing a statistic needs a primary-source check before citing — a different-agent reviewer with web access catches what the generator's shared priors miss
type: practice
origin: PR #443 (deliberate-simplification ledger research, 2026-06-22)
---

A web-search result snippet that paraphrases a statistic is not
citable as-is. Real case from the PR #443 research synthesis: a
snippet's "around 8%" turned out to be a single-project (Hadoop)
ratio, not the general figure (the actual literature value was
~5.3%), and a second statistic was mis-credited to the wrong authors
(attributed to Maldonado; actually Maipradit/Zampetti 2018). Both
errors were caught only when a DIFFERENT agent with web access
reviewed the citations against primary sources — the generating
agent's own review missed them, because generator and self-reviewer
share the same priors.

**Why:** snippets compress and decontextualize numbers; a
same-model self-check tends to re-derive the same plausible-looking
misreading instead of catching it.

**How to apply:** before citing any statistic sourced from a search
snippet, open the primary source and verify the number, its scope
(one project vs field-wide), and the attribution. For research
syntheses, have a separate agent with web access do the citation
check rather than relying on the author's self-review.

**Second instance — wholly fabricated URL (loom-product-principles
0.7.0, 2026-07-12):** the same failure mode extends past misread
statistics to *fabricated citations*. Authoring a grounding doc
(`docs/loom/research/2026-07-12-ui-surface-treatments-canon.md`), the
implementer cited a plausible-looking Smashing Magazine URL that
404'd — the titled article never existed. The accurate underlying
claim (neumorphism's low-contrast WCAG risk) was real, but the URL was
invented. The code-quality reviewer (different agent, web access)
caught it; it was replaced with a verified source. **A doc whose sole
purpose is sourcing cannot carry an unverifiable link — verify every
URL live, not just the claim it supports.** Reinforces the same
different-agent-review remedy above.
