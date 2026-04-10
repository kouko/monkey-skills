# Application Security Standard

Application security grounded in **OWASP Application Security
Verification Standard (ASVS) v5.0.0** — the current canonical
baseline for verifying the security of web applications and web
services. This standard is the security anchor for code-team's code
review, design review, and implementation gates.

## Primary Sources

- **OWASP Foundation (2025) *Application Security Verification Standard, Version 5.0.0*.** Released **2025-05-30** at OWASP Global AppSec EU (Barcelona). Canonical URLs: https://asvs.dev/v5.0.0/ (per-chapter stable permalinks) and https://owasp.org/www-project-application-security-verification-standard/. License: CC BY-SA 4.0. Structure: 17 chapters (V1–V17), ~350 verification requirements, 3-tier L1/L2/L3 hierarchy.
- OWASP Foundation (2021) *OWASP Top 10 Web Application Security Risks* — https://owasp.org/Top10/. Secondary framing for prioritization and threat vocabulary; **not** a verification standard. Use ASVS for requirements, Top 10 for explaining *why* a requirement matters.
- Adjacent JP primary: 徳丸浩 (2018) 『体系的に学ぶ 安全な Web アプリケーションの作り方 第 2 版』, SB クリエイティブ. ISBN 978-4797393163. See `character-encoding-security.md` for the multi-byte-specific chapter (Ch.6) that this standard cross-references but does not replicate.

## Default Tier: L1

**ASVS v5.0.0 Preface**, L1 definition:

> *"L1 is the initial step to adopting the ASVS, providing the
> first layer of defense."*

code-team's **default tier is ASVS L1**. Rationale:

- L1 is "a minimum for all applications" — it represents the
  baseline controls every web application should have regardless
  of context.
- L2 is appropriate for applications handling significant
  business-to-business transactions, regulated data (PCI, HIPAA),
  or containing business logic that is attractive to attackers.
- L3 is reserved for the most critical applications (military,
  health, life safety, critical infrastructure).

Projects that handle regulated data, payment flows, or PII at
scale should **declare an elevated tier in their TECH-SPEC.md**
and the relevant gate will enforce the higher tier. When the tier
is not declared, L1 applies.

## The 17 Chapters (V1–V17)

**ASVS v5.0.0 Preface + chapter index** (verified against
https://asvs.dev/v5.0.0/):

| V# | Chapter | code-team relevance |
|----|---------|---------------------|
| **V1** | Encoding and Sanitization | Output encoding, context-specific sanitization (HTML, SQL, shell, LDAP). Load-bearing for XSS / injection prevention. |
| **V2** | Validation and Business Logic | **Input validation** and business-rule enforcement. This is the primary chapter for any code handling user input. |
| V3 | Web Frontend Security | Browser-side controls (CSP, SRI, cookie flags). |
| V4 | API and Web Service | REST / GraphQL / SOAP interface security. |
| V5 | File Handling | Upload validation, path traversal, MIME handling. |
| **V6** | Authentication | Password storage, MFA, credential recovery. |
| **V7** | Session Management | Session tokens, timeout, invalidation. |
| V8 | Authorization | Access control, RBAC / ABAC enforcement. |
| V9 | Self-contained Tokens | JWT, PASETO — token structure and validation. |
| V10 | OAuth and OIDC | Federated identity protocols. |
| **V11** | Cryptography | Algorithm selection, key management. |
| V12 | Secure Communication | TLS configuration, certificate handling. |
| **V13** | Configuration | **Secrets management**, secure defaults, dependency management. |
| **V14** | Data Protection | **Secrets handling at rest**, data classification. |
| V15 | Secure Coding and Architecture | Architectural controls, defense in depth. |
| **V16** | Security Logging and Error Handling | Audit logs, error message hygiene. |
| V17 | WebRTC | Real-time communication security. |

The bolded chapters are the ones code-team gates reference most
frequently — input validation (V2), authentication (V6), session
(V7), secrets (V13 + V14), logging & error handling (V16),
encoding (V1), and cryptography (V11).

## Core Verification Categories for Code Review

### Input Validation (V2)

**ASVS v5.0.0 V2 "Validation and Business Logic"**: every piece of
untrusted input must be validated against an explicit schema. "Untrusted"
includes anything not under the application's direct control — user
input, upstream API responses, files from other systems, message
queue payloads.

Validation strategies from V2 (paraphrased):

- **Allow-list over deny-list**: define what is allowed; reject
  everything else. Deny-lists are brittle.
- **Type, range, format, length** — all four dimensions for any
  scalar input.
- **Canonicalize before validating** — normalize encoding, case,
  and path separators, then validate the canonical form.

### Encoding and Sanitization (V1)

**ASVS v5.0.0 V1 "Encoding and Sanitization"**: output encoding is
context-specific. The same string must be encoded differently for
HTML body, HTML attribute, JavaScript context, URL, SQL, shell, and
LDAP. V1 contains requirements for each context.

**Injection prevention** in v5.0.0 is decoupled across V1 (encoding)
and V2 (validation) — previously (in 4.0.3) V5.3 handled both. When
specifying injection controls, reference V2 for the validation step
and V1 for the encoding step.

### Secrets (V13 + V14)

**ASVS v5.0.0 V13 "Configuration"** and **V14 "Data Protection"**:
secrets (API keys, DB passwords, encryption keys, tokens) must not
be in source code, in build artifacts, or in logs. Use a secrets
manager or environment injection; rotate on compromise; audit access.

### Authentication (V6) and Session Management (V7)

**ASVS v5.0.0 V6 "Authentication"**: password storage uses a modern
adaptive hash (argon2id, bcrypt, scrypt). MFA for privileged
operations. Rate-limit credential submissions.

**ASVS v5.0.0 V7 "Session Management"**: sessions are invalidated
on logout, on credential change, and on inactivity timeout. Session
tokens are unpredictable, transport-secured, and not logged.

### Error Handling and Logging (V16)

**ASVS v5.0.0 V16 "Security Logging and Error Handling"**: errors
must not leak sensitive information (stack traces, SQL, internal
paths, secrets) to end users. Security-relevant events (auth
success/failure, access control decisions, input validation
failures) must be logged with enough context for incident response,
but without logging the sensitive inputs themselves.

## Migration Note: ASVS 4.0.3 → 5.0.0

**ASVS 5.0.0 (2025-05-30) supersedes 4.0.3 (2021-10-28).** Pre-2025
citations using V-numbers from 4.0.3 are no longer authoritative —
chapter structure was substantially reorganized. Mapping of the
most common code-review claims:

| Claim | 4.0.3 reference | **v5.0.0 reference** |
|-------|-----------------|----------------------|
| Input validation | V5 | **V2** |
| Encoding / sanitization | V5.3 (combined with validation) | **V1** (decoupled from validation) |
| Secrets management | V2 or V14 | **V14 + V13** |
| Error handling + logging | V7.4 | **V16** |
| Authentication | V2 | **V6** |
| Session management | V3 | **V7** |
| Authorization | V4 | **V8** |
| Cryptography | V6 | **V11** |

When reading older security guidance that cites V5, V7.4, etc.,
treat it as referring to ASVS 4.0.3 and translate to v5.0.0 using
the table above. code-team standards, gates, and checklists cite
**only v5.0.0** going forward.

## Japanese Cross-Reference

Multi-byte character encoding vulnerabilities (Shift_JIS 5C problem,
UTF-8 over-long encoding, multi-byte boundary XSS) are
under-documented in OWASP ASVS v5.0.0. For Japanese-locale
applications, consult the companion standard
`character-encoding-security.md`, which is grounded in 徳丸浩
『体系的に学ぶ 安全な Web アプリケーションの作り方 第 2 版』Ch.6
「文字コードとセキュリティ」.

Both files must be consulted when evaluating code that handles
user input in a JP locale.

## Cross-References

- `character-encoding-security.md` — JP-specific multi-byte
  encoding vulnerabilities (徳丸本 Ch.6), augments V1/V2
- `tdd-standard.md` — security-critical code MUST have failing
  tests first (code-team critical-path coverage rule)
- `pragmatic-principles.md` — Trade-off Dimensions list includes
  security as an explicit axis

## Anti-Patterns

- ❌ **Citing ASVS V5 for input validation** in new standards —
  that's 4.0.3 vocabulary, superseded by V2 in v5.0.0
- ❌ **Deny-list validation** (blacklist of dangerous chars) —
  ASVS V2 requires allow-list
- ❌ **Secrets in source code** — even temporarily, even in
  private repos (V13 / V14 violation)
- ❌ **Logging secrets or full request bodies** — V16 violation;
  logs are an audit surface that often leaks via backup / SIEM
- ❌ **Stack traces to end users** in production (V16 violation)
- ❌ **Home-grown crypto** — use vetted libraries per V11, never
  implement cipher primitives yourself
- ❌ **MD5 / SHA-1 for password hashing** — V6 requires an
  adaptive hash
- ❌ **Citing OWASP Top 10 as the verification standard** — Top
  10 is awareness, ASVS is verification; they are not interchangeable
- ❌ **Skipping character-encoding review for JP-locale apps** —
  ASVS alone is insufficient; see `character-encoding-security.md`
