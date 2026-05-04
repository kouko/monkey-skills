# Fixture: JP newspaper 社説 — 「学校のICT化、急がば回れ」

**Source**: synthetic-representative (composed by maintainer for evaluation purposes; modeled on 朝日新聞 / 日経 社説 register conventions, ca. 2024)
**Accessed**: 2026-05-05 (composed)
**Capture method**: synthetic representative — not a real artifact
**License**: maintainer-authored, freely usable for plugin evaluation
**Honesty flag**: This is NOT a real fetched artifact. It is a maintainer-composed text built to exhibit the lens features cleanly (起承転結 4-part structure, 婉曲表現 hedges, reader-responsibility signals). Real-world 社説 vary in compactness and explicitness; eval results from this fixture are a smoke-test of `lens-rhetoric-ja` application, not a benchmark of real-text deconstruction quality.
**Eval target**: `artifact-deconstruct` must surface the 起承転結 4-part structure with sentence-range mapping, identify 転 as inductive juxtaposition (NOT mapped to Toulmin warrant), enumerate ≥2 reader-responsibility surface signals (vague topic statement / 婉曲 hedges / paragraph-level moves), and explicitly attribute analysis to `lens-rhetoric-ja`.

---

## 学校のICT化、急がば回れ

文部科学省が GIGA スクール構想を打ち出してから、もう数年が経つ。一人一台の端末配布は全国の小中学校でほぼ完了し、家庭への持ち帰りも当たり前になりつつある。

それに伴い、現場の声も多様化している。授業中に子どもがゲームを開いてしまう、家庭で動画ばかり見てしまう、保護者からの問い合わせが増えた——担任教員の負担は確実に増している。教育委員会の調査によれば、ICT 機器のトラブル対応に要する時間は、導入前と比較しておよそ三倍に膨らんだという。専門の支援員を配置している自治体は限られており、地方ほど人手不足が深刻だ。

先日、長野県のある山間部の小学校を訪ねた。築七十年の木造校舎の教室で、四年生の子どもたちは画面ではなく、地元の古老から聞いた山の言い伝えを、ノートに鉛筆で書き写していた。担任の先生に伺うと、その日はあえて端末を使わない授業の日だという。「便利さの中で見落としがちなものを、子どもたちに残してやりたい」。窓の外では、雪解けの川の音が静かに響いていた。

ICT は、もちろん教育の質を高める力を持っている。だが、それを急ぎすぎることで失われるものもあるのではないか。便利さと豊かさは、必ずしも同義ではない。現場の教員が、何を残し、何を取り入れるかを判断するための時間と裁量を確保すること——それが、政策の側に求められている姿勢だと言えるだろう。

---

## Annotations for evaluator

The fixture exhibits canonical 起承転結 structure with paragraph-aligned moves, plus several reader-responsibility surface signals that an Anglo Toulmin pass would systematically misread.

### lens-rhetoric-ja: kishōtenketsu structure

| Move | Surface signal | Sentence range |
|---|---|---|
| **起** | GIGA スクール構想の現状提示。一人一台端末がほぼ完了。topic-as-given. | ¶1 |
| **承** | 数値的拡張（三倍に膨らんだ）+ 地方の人手不足。problem-space accumulation, not yet a claim. | ¶2 |
| **転** | 長野県山間部の木造校舎。古老の言い伝えをノートに書き写す子どもたち。**juxtaposition, NOT counter-argument**. The image stands beside ¶1+¶2 without logical refutation. | ¶3 |
| **結** | 便利さと豊かさは同義ではない。教員の裁量を確保することが政策に求められる。**implicit claim**: the relationship between ¶1+¶2 and ¶3 is what speed obscures — softened with 「と言えるだろう」. | ¶4 |

### What 転 juxtaposes against 起+承

¶3 introduces an *image* (木造校舎・鉛筆・雪解けの川) that does not logically refute ¶1+¶2's data. Anglo reading: "anecdotal, no warrant." JP-register reading: 転 supplies persuasive force by image-juxtaposition; the bridge between data and image is the reader's to construct. The "claim" of the piece is the *configuration* of all four parts, not a single proposition extractable from ¶4.

### Reader-responsibility surface signals (Hinds 1987)

| Signal | Present? | Notes |
|---|---|---|
| No explicit topic sentence | yes | ¶1 establishes 状況, never states "本稿の主張は…" |
| No explicit warrant linking ¶3 to ¶4 | yes | The bridge between bakery-equivalent scene and policy claim is not made explicit |
| Paragraph-level 転 move | yes | ¶3 is the kishōtenketsu pivot; an Anglo reader would tag this as "digression" |
| 婉曲表現 hedges | yes | 「…ものもあるのではないか」「…と言えるだろう」「…必ずしも同義ではない」 |
| Claim left to reader | yes | ¶4 proposes a *relationship* (speed vs richness) without imperative mood |

### Mode selected

**起承転結 mode** — register cue: 社説 op-ed register, no 序論/本論/結論 section headings, image-driven 転 in ¶3, 婉曲 closure in ¶4.

### Ethical position

🟢 Register-appropriate. The 婉曲 hedges and reader-responsibility signals are conventional 社説 register, not evasion. Anglo Toulmin pass would mis-flag "missing warrant" / "unsupported anecdote" — which would be an Anglo-projection error, not an artifact flaw.

### Expected lessons

- Modern JP 社説 still uses kishōtenketsu — don't assume Western academic register
- 転 introduces image / scene, not counter-argument; do NOT map to Toulmin warrant
- 婉曲表現 (「のではないか」「と言えるだろう」) is required register, not low conviction
- The implicit claim is the *relationship* the 結 proposes, not a sentence extractable from any paragraph
- Applying `lens-rhetoric-anglo.md` to this artifact would systematically under-detect the 転 juxtaposition mechanism
