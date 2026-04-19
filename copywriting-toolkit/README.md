# copywriting-toolkit

Pipeline-structured copywriting plugin. Refactored from `domain-teams:copywriting-team` into 14 specialized skills — each with ONE job, self-contained standards, and hand-off envelopes between stages.

## Status

- **v1.0.0** — initial release. Coexists with `domain-teams:copywriting-team` for A/B comparison.

## 9-Phase Pipeline

```
Phase 0  copywriting-intake                       mandatory
Phase 1  [inline in intake]                       mandatory, LOOSE recommend planning-team
Phase 2  copywriting-ideation                     skippable
Phase 3  copywriting-neta-injection               skippable, hybrid pre/post
Phase 4  one of:                                  mandatory
           copywriting-short-form
           copywriting-mid-form
           copywriting-long-form-pasona
           copywriting-long-form-extended
           copywriting-light-action
Phase 5  copywriting-voice-positioning-stage      mandatory
Phase 6  copywriting-voice-tone-stage             mandatory
Phase 7  copywriting-ethics-check-stage           mandatory, evaluator-only
Phase 8  copywriting-form-check-stage             mandatory, evaluator-only
Alt      copywriting-audit-stage                  alternate entry for external copy
```

Entry router: `using-copywriting-toolkit`.

## Skills

| Skill | Phase | Role |
|---|---|---|
| using-copywriting-toolkit | — | Entry router / phase decision tree |
| copywriting-intake | 0-1 | Brief intake + message confirmation |
| copywriting-ideation | 2 | Mandalart + KJ + Taniyama + VS divergence / convergence |
| copywriting-neta-injection | 3 | Neta overlay (pre-draft or post-draft) |
| copywriting-short-form | 4 | キャッチコピー / headline (7-15 chars) |
| copywriting-mid-form | 4 | EC product copy (BEAF) |
| copywriting-long-form-pasona | 4 | Long PASONA / 新PASONA / PASBECONA |
| copywriting-long-form-extended | 4 | QUEST / PASTOR |
| copywriting-light-action | 4 | PREP / CREMA micro-conversion |
| copywriting-voice-positioning-stage | 5 | Voice Quadrant positioning |
| copywriting-voice-tone-stage | 6 | Tone fine-tuning + JP lineage craft |
| copywriting-ethics-check-stage | 7 | 景品表示法 / FTC Endorsement gate |
| copywriting-form-check-stage | 8 | Framework + length + CTA gate |
| copywriting-audit-stage | alt | Audit external copy through Phases 5-8 |

## Grounding

Primary sources from `domain-teams:copywriting-team` preserved verbatim. Standards include:

- 神田昌典 2016/2021 PASONA / 新PASONA / PASBECONA
- 谷山雅計 2007 散らかす→選ぶ→磨く + なんかいいよね禁止
- 今泉浩晃 1987 曼陀羅発想法
- 川喜田二郎 1967 KJ法
- Cialdini 1984 *Influence*
- Schwartz 1966 *Breakthrough Advertising*
- Zhang et al. 2025 Verbalized Sampling (arXiv:2510.01171)
- Fortin 2005 QUEST / Edwards 2016 PASTOR
- 小霜和也 2010/2014 本能分析
- 秋山隆平・杉山恒太郎 2004 AISAS / 飯髙悠太 2019 ULSSAS
- Kaushik 2007 micro/macro conversion
- 景品表示法 / FTC Endorsement Guides
- Voice tradition: 糸井重里, 岩崎俊一, 眞木準 via TCC 年鑑

## A/B with copywriting-team

Original `domain-teams:copywriting-team` remains untouched. Run both on the same brief and compare. Both use byte-identical standards files.

## License

MIT — see repository root.
