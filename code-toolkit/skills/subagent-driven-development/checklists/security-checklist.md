<!--
FUNCTIONAL COPY — DO NOT EDIT IN PLACE
SSOT: domain-teams/skills/code-team/checklists/security-checklist.md
Sync via: code-toolkit/scripts/distribute.py
-->

# Security & Safety Checklist Gate

## Primary Sources

- **OWASP Foundation (2025)** *Application Security Verification
  Standard, Version 5.0.0*. Released **2025-05-30** at OWASP
  Global AppSec EU (Barcelona). Canonical URLs:
  https://asvs.dev/v5.0.0/ (per-chapter stable permalinks) and
  https://owasp.org/www-project-application-security-verification-standard/.
  License: CC BY-SA 4.0. Structure: **17 chapters (V1–V17)**,
  ~350 verification requirements, **3-tier L1/L2/L3 hierarchy**.
- OWASP Foundation (2021) *OWASP Top 10 Web Application Security
  Risks* — https://owasp.org/Top10/. Secondary framing for threat
  vocabulary (A03 Injection is referenced in CHK-SEC-004 below).
  Top 10 is awareness, ASVS is verification.
- **徳丸浩 (2018)** 『体系的に学ぶ 安全な Web アプリケーションの
  作り方 第 2 版 — 脆弱性が生まれる原理と対策の実践』, SB
  クリエイティブ. ISBN 978-4797393163. **Ch.6「文字コードと
  セキュリティ」** grounds CHK-SEC-005 below (JP multi-byte
  encoding concerns under-documented in English ASVS).
- Team standards:
  `standards/app-security-standard.md` (ASVS v5.0.0 alignment)
  and `standards/character-encoding-security.md` (JP preamble,
  徳丸本 Ch.6) are the authoritative code-team references.

### Target Tier

code-team's **default tier is ASVS L1** — the "minimum for all
applications" baseline (ASVS v5.0.0 Preface). Projects that handle
regulated data (PCI, HIPAA, PII at scale), payment flows, or
safety-critical functions MUST declare an elevated tier (L2 or L3)
in their TECH-SPEC.md, and the gate will enforce the higher tier.
When the tier is not declared, L1 applies.

### Migration Note (ASVS 4.0.3 → 5.0.0)

**ASVS 5.0.0 (2025-05-30) supersedes 4.0.3 (2021-10-28).** Chapter
structure was substantially reorganized. Common pre-2025 references
no longer resolve the same way:

| Claim                     | 4.0.3    | **v5.0.0**  |
|---------------------------|----------|-------------|
| Input validation          | V5       | **V2**      |
| Encoding / sanitization   | V5.3     | **V1**      |
| Secrets management        | V2 / V14 | **V14 + V13** |
| Error handling + logging  | V7.4     | **V16**     |
| Authentication            | V2       | V6          |
| Session management        | V3       | V7          |

Pre-2025 references to V5 (validation) and V7.4 (error handling)
are **ASVS 4.0.3 vocabulary** and are superseded. This gate cites
**only v5.0.0** going forward; `standards/app-security-standard.md`
§"Migration Note" contains the full mapping table.

## Evaluation Instructions

You are a strict auditor. Check each item below against the worker's output.
You MUST give `PASS`, `FAIL_FATAL`, or `FAIL_FIXABLE` for each item, with specific evidence.
The failure type for each item is defined below — use the type specified.

## Checklist

- [ ] **CHK-SEC-001 (Secrets)** [FATAL]: No hardcoded passwords, API keys, tokens, or secrets. All sensitive values read from environment variables or secret managers. **Grounded in**: OWASP ASVS v5.0.0 **V14 "Data Protection"** (secrets handling at rest) + **V13 "Configuration"** (secrets management, secure defaults). See `standards/app-security-standard.md` §Secrets (V13 + V14).
- [ ] **CHK-SEC-002 (Input Sanitization)** [FATAL]: All user-facing inputs have validation and sanitization. No raw user input passed to SQL queries, shell commands, or HTML rendering. **Grounded in**: OWASP ASVS v5.0.0 **V2 "Validation and Business Logic"** — allow-list over deny-list, type/range/format/length, canonicalize before validating. See `standards/app-security-standard.md` §Input Validation (V2).
- [ ] **CHK-SEC-003 (Error Exposure)** [FIXABLE]: Error handlers do NOT leak stack traces, internal paths, or system details to external responses. **Grounded in**: OWASP ASVS v5.0.0 **V16 "Security Logging and Error Handling"** — errors must not leak sensitive information to end users; security-relevant events must be logged without logging the sensitive inputs themselves. See `standards/app-security-standard.md` §Error Handling and Logging (V16).
- [ ] **CHK-SEC-004 (Injection Risk)** [FATAL]: No obvious SQL injection, XSS, command injection, or path traversal vulnerabilities. **Grounded in**: OWASP ASVS v5.0.0 **V1 "Encoding and Sanitization"** (context-specific output encoding: HTML body, HTML attribute, JS, URL, SQL, shell, LDAP) **+ V2 "Validation and Business Logic"** (input validation); OWASP Top 10 2021 **A03 Injection**. Injection prevention in v5.0.0 is **decoupled across V1 (encoding) and V2 (validation)** — previously (in 4.0.3) V5.3 handled both. See `standards/app-security-standard.md` §Encoding and Sanitization (V1).
- [ ] **CHK-SEC-005 (Character Encoding, JP locale applicable)** [FATAL]: Multi-byte character encoding is handled safely across the full request→DB→response pipeline. No silent encoding conversion; encoding-aware escape functions; parameterized queries to neutralize the **Shift_JIS 5C problem**; over-long UTF-8 and isolated surrogate halves are rejected; canonicalization (e.g. UTF-8 NFC) happens **before** validation. **JP locale applicable**: this item is load-bearing for Japanese-locale applications (Shift_JIS / EUC-JP legacy stacks, mixed-encoding CSV uploads, legacy JP APIs). For non-JP applications the Unicode edge cases (over-long encoding, surrogate halves) still apply but the Shift_JIS-specific concerns may be marked `NOT_APPLICABLE`. **Grounded in**: 徳丸浩 (2018) 『体系的に学ぶ 安全な Web アプリケーションの作り方 第 2 版』 **Ch.6「文字コードとセキュリティ」**; augments ASVS V1/V2. See `standards/character-encoding-security.md`.

## Verdict Rules

- Any **1 item** is `FAIL_FATAL` → final verdict is `NEEDS_REVISION` (escalate to user)
- Only `FAIL_FIXABLE` items (no FATALs) → final verdict is `PASS_WITH_NOTES` (trigger auto-revise)
- All items are `PASS` or `NOT_APPLICABLE` → final verdict is `PASS`
- `NOT_APPLICABLE` is permitted **only** for CHK-SEC-005 when the application has no JP-locale interaction and no multi-byte encoding surface; all other items MUST resolve to PASS / FAIL_FATAL / FAIL_FIXABLE.

## Output Format

```json
{
  "verdict": "PASS | PASS_WITH_NOTES | NEEDS_REVISION",
  "checklist_results": [
    {
      "id": "CHK-SEC-001",
      "status": "PASS | FAIL_FATAL | FAIL_FIXABLE | NOT_APPLICABLE",
      "evidence": "Specific code reference or finding",
      "fix_instruction": "How to resolve (for FAIL_FIXABLE items)"
    }
  ]
}
```
