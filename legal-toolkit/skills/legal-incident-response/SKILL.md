---
name: legal-incident-response
description: Taiwan in-house 法務 incident response skill — 3-path classifier (個資外洩 PII-breach / 主管機關函覆 authority-letter / 合約違約 contract-breach). Auto-classifies free-text incident descriptions, dispatches per-path sub-protocols, emits 2-file audience-shaped output (legal.md / business.md) with ISO 8601 timeline + TBD migration tracker. PII-breach uses skeleton+LLM-fill templates pinned to current Taiwan law (Path A from SP2 verify run); authority-letter uses pure-LLM protocol; contract-breach delegates to legal-contract-review via handoff-context.json. Cross-references legal-playbook/profile.yml (shared with legal-document-draft) for company identity + regulatory_authorities + external_counsel.
---

# legal-incident-response

Taiwan in-house 法務 incident response (Phase 2 of legal-toolkit; v0.4.2).

Full design: `docs/superpowers/specs/2026-05-13-legal-toolkit-sp3b-incident-response-design.md`.

(Full SKILL.md body to be expanded in Task 8.)
