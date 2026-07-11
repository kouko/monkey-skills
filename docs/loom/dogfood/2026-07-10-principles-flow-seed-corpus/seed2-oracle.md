# Oracle 2 — bedtime-story audio app (grader-only)

named_anchors: Apple Human Interface Guidelines; Calm Technology; Kenya Hara; Local-First; Kano Model; Jobs-to-be-Done; React Native; on-device TTS
# note: named_anchors token shortened from `Kenya Hara / MUJI "Emptiness"`
# to `Kenya Hara` (stable-fragment re-tokenization, calib-r2 evidence) — r2
# wrote 「Kenya Hara / MUJI「空無」」(CJK quotes/translation); the
# quoted-English-Emptiness long form is paraphrase-fragile, `Kenya Hara`
# appears in every observed variant. The dropped "MUJI Emptiness" gloss was
# descriptive only (the oracle never machine-checked it as a separate
# token); designer/canon identity is what the check verifies, and `Kenya
# Hara` alone still uniquely identifies the anchored canon.
# note: Calm Technology is a PROSE-ONLY TRAP — named only inside the
# Design-stance sentence, no labeled "Design canon:" line — must still land
# as its own Anchors row.

deferred_items: 可逆性|Reversibility posture; 升級胃口|Upgrade appetite
# note: DEFERRED TRAP — 2 distinct undecidable stances (可逆性=無法判斷 →
# separate Open Question + re-trigger; 升級胃口=無法判斷 → separate Open
# Question + re-trigger); neither may be dropped or merged into one vague
# entry.
# note: 升級胃口|Upgrade appetite — the "Upgrade appetite" English
# alternative is evidenced by the sibling seed4 calib-r1 artifact ("Upgrade
# appetite for long-term architecture decisions", seed4/PRINCIPLES.md Open
# Questions #3, same bait concept); replay artifact language is
# nondeterministic (seed5 produced Chinese, others English) so the pair
# guards future English replays of this seed even though THIS run's seed2
# artifact never surfaced the item (stays class-D for this run).

out_of_jurisdiction_bait: 訂閱制/定價數字待定 (never a principle); "3 個月內上架" 時程 (never a principle)

stances: task=播放+自訂旁白only; user=家長決策者; quality order=溫度>內容>功能; success=7天40%留存; why-new=罐頭語調; language=繁中為主; lifecycle=自動淡出; design=低打擾近乎無UI; privacy=錄音永不上雲只存本機; interaction=Apple HIG; Calm Technology naming; product=Kano+JTBD; eng canon=Local-First

negative: 兒童聲音資料分享; 識字教學
# note: 兒童聲音資料分享 must read as forbidden (privacy stance), not accepted
# behavior; 識字教學 is a Scope-out item — presence means it leaked back in
# as an in-scope Product Principle.
# note: 上傳雲端 demoted from machine-checked `negative:` per README
# §Calibration policy: demote-on-reproduction — OBSERVED FP in calib-r2:
# the artifact's own privacy-rejection sentence 「兒童語音錄音永不上傳雲端，
# 僅儲存於裝置本機」contains this token as a substring (negation-superstring).
# Must still read as forbidden (privacy stance); grader-checked only now.
# note: 互動遊戲/社群分享 demoted from machine-checked `negative:` per README
# §Calibration policy: demote-on-reproduction — OBSERVED FP in calib-r2:
# the artifact's own scope-out sentence 「零互動遊戲、教學工具、社群分享」
# contains both tokens as substrings (negation-superstring, "零" = none
# prefix). Scope-out items — presence means they leaked back in as an
# in-scope Product Principle; grader-checked only now.
