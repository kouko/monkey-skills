# Oracle 3 — API schema-diff CLI (grader-only)

named_anchors: Shneiderman; Nielsen; Hexagonal|Ports & Adapters; 12-Factor App; Working Backwards / PR-FAQ; Rust
# note: MIXED-TRADITION TRAP — Shneiderman + Nielsen are both named together
# in one Design/Interaction bullet; each is a separate canon needing its own
# Anchors row, not collapsed into one. TECH-STACK-IN-PROSE TRAP — Rust is
# named only inside the Idea sentence, no labeled "Tech-stack:" line — must
# still land as an Anchors row.
# note: SURNAME-FRAGMENT calibration (calib-r3 evidence) — both tokens
# re-tokenized from full-English-name form ("Shneiderman's Eight Golden
# Rules" / "Nielsen's 10 Usability Heuristics") to the bare surname: the
# r3 artifact anchored both in Chinese ("Shneiderman 八大金律" / "Nielsen
# 十項可用性啟發法則"), so the full-name token never appears verbatim in a
# CJK-output artifact. The surname is the stable fragment across every
# observed language variant.

deferred_items: none in this seed (2-deferred trap lives in seed 2)

out_of_jurisdiction_bait: "MIT license 開源後續 SaaS 付費規劃" (business model, never a principle); "6 個月 roadmap 衝 star 數後談 monetization" (timeline, never a principle)

stances: task=diff+分類+報告only; user=後端工程師; quality order=召回>速度>美觀; success=98% recall/100案例; why-new=誤報率高/無GraphQL; language=英文輸出; lifecycle=無狀態單次呼叫; design=雙格式人機可讀; interaction=Shneiderman+Nielsen mix; eng 可逆性=opt-out覆寫; privacy=純本地不上傳; eng 升級胃口=agent自行決定; product=Working Backwards; eng canon=Hexagonal+12-Factor; Rust tech-stack in prose

negative: none in this seed (machine-checked items demoted to grader-side notes — see # note lines)
# note: 上傳 schema 到雲端 must not read as accepted behavior (privacy stance
# is 純本地不上傳) — demoted from machine-checked `negative:` (round-3): a
# rejection sentence like 「絕不上傳 schema 到雲端」 contains this token as a
# substring, so the checker fired a reproduced false positive; grader-checked
# only now. mock server support / API gateway support are bait-leak
# coverage, grader-checked only (not machine-checked): mock server/API
# gateway are Scope-out items, and any acceptance phrase is a substring of
# its own natural rejection (negation-superstring — e.g. "does not offer
# mock server support" contains "mock server support"; no phrase choice
# fixes this under substring semantics). Separately (not machine-checked —
# no single literal string captures an absence-of-marker check): "好用的
# CLI" or any unchecked adjective with no `— check:` is a NEGATIVE finding
# for LLM/human graders.
