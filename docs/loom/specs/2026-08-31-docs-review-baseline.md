# establish docs review baseline — delivery brief

## Smallest End State

交付第一個可重算的 historical replay baseline：以凍結 corpus、人工 oracle、
弱模型 economy cohorts 與不可變 run/report records，量出 finding rate、
false-alarm rate、repeat agreement、可觀測時間／usage，以及缺陷來源能否被
證據歸因。此票綁定既有 change-folder
`docs/loom/2026-08-31-docs-review-baseline/`，結果必須明示三種文件的 case
coverage 與不足，不把 hard-case corpus 當成日常平均。

成功判準：validated spec 的 active scenarios 全部有可執行驗證；至少一個
真實 historical case 可端到端產生 immutable partial-or-full metric report；
Claude Code 與 Codex economy cohorts 的 scored/invalid/unavailable populations
分開呈現；任何不足被送回 Map fog，而不是由工具自行補答案。

## Acceptance

- [ ] Promised slice: 交付第一個可重算的 historical replay baseline：以凍結 corpus、人工 oracle、
弱模型 economy cohorts 與不可變 run/report records，量出 finding rate、
false-alarm rate、repeat agreement、可觀測時間／usage，以及缺陷來源能否被
證據歸因。此票綁定既有 change-folder
`docs/loom/2026-08-31-docs-review-baseline/`，結果必須明示三種文件的 case
coverage 與不足，不把 hard-case corpus 當成日常平均。

成功判準：validated spec 的 active scenarios 全部有可執行驗證；至少一個
真實 historical case 可端到端產生 immutable partial-or-full metric report；
Claude Code 與 Codex economy cohorts 的 scored/invalid/unavailable populations
分開呈現；任何不足被送回 Map fog，而不是由工具自行補答案。

Outcome Map ticket: docs/loom/maps/docs-review-efficiency/tickets/establish-docs-review-baseline.md

## Design-side on-ramp

fired: rows 3 — user chose detour

## Queue relation

unqueued — Outcome Map delivery ticket owns this arc; the backlog queue does not duplicate it.

## Delivery closure

policy: pr-ci
review-evidence: required before closure
verification-evidence: required before closure
