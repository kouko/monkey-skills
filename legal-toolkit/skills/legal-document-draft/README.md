# legal-document-draft

Drafts new Taiwan-law legal documents (privacy / ToS / DPA / NDA) from a company profile + negotiation playbook.

## Quick start

1. Ensure `legal-playbook/profile.yml` exists in your repo (see `assets/profile-schema.yml` for the schema)
2. Optionally maintain `legal-playbook/<clause>.md` files for stance defaults
3. Invoke via the `using-legal-toolkit` router by asking to "draft a privacy policy" / "write an NDA" / etc.
4. The skill asks for session-specific variables (product name, data categories, SDK list, etc.) interactively
5. Output appears at `legal-outputs/<timestamp>-<mode>/`:
   - `<doc-type>.md` — publish-ready document
   - `compliance.md` — 法務 review with checklist verdicts + TBD migration

## Modes

| Mode | Document | Primary statutes |
|---|---|---|
| privacy | 隱私權政策 / 個資告知事項 | 個資法 §8, §9, §21, 施行細則 §22, §27 |
| tos | Terms of Service / 服務條款 | 民法, 消保法 §11-1 + §17, 公平交易法 |
| dpa | 委託處理協議 | 個資法 §4 + §8, 施行細則 §12 |
| nda | 保密協議 | 民法 §227, §247-1, §250, 商業慣例 |

## TBD migration

Items deferred to PDPC 子法 (e.g., specific breach notification timeframe, reporting threshold) appear as TBD entries in `compliance.md`. The `references/tbd-migration-template.md` documents the patch path when PDPC sub-regulations land — typically a `<10-line edit to `assets/template-*.md` + `checklists/compliance-*.md`.

## Not in scope

- Drafting GDPR-style documents (Path A is Taiwan-current-law only; see spec §3 + §13)
- Reviewing existing documents — use `legal-contract-review` instead
- Auto-monitoring PDPC for sub-regulation publication — manual monitoring sufficient at low publication frequency

## See also

- `legal-contract-review` — review counterparty drafts (NDA / SaaS / etc.)
- `legal-playbook-author` — author the negotiation stances draft consumes
