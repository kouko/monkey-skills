---
name: required-identity-guard-must-reject-whitespace-not-just-empty
description: A "must be non-empty" guard written `if not value:` admits a WHITESPACE-ONLY string (" " is truthy) — for an authorization/identity boundary this is a real bypass (a caller supplies a blank-looking identity and passes). Use `if not (value and value.strip()):`, and pin the whitespace case with a RED-first test.
type: gotcha
origin: 2026-07-14 session — investing-toolkit analysis-kpi review_queue slice 2, adversarial code-quality review caught the auth-seam bypass
---

The operational-kpi review-queue's anti-fabrication seam requires a HUMAN
`adjudicated_by` before an adjudication is accepted (the pipeline must not
self-confirm). The first implementation guarded it with
`if actor_is_pipeline or not adjudicated_by:` — which looks right but is
bypassable: a whitespace-only string like `" "` is TRUTHY in Python, so
`not " "` is `False` and the guard passes. A pipeline caller could set
`adjudicated_by=" "`, leave `actor_is_pipeline` default False, and
self-confirm with a blank-looking identity — defeating the human-in-the-loop
boundary the whole capability exists to enforce.

**Why:** `not x` only rejects the falsy set (`None`, `""`, `0`, `[]`); a
string of spaces/tabs is truthy. For an AUTHORIZATION or REQUIRED-IDENTITY
check the empty check is not enough — the string must be non-blank after
stripping. A green suite testing only `""` and `None` never exercises the
whitespace arm, so the hole ships silently.

**How to apply:** for any "must be a non-empty/meaningful string" guard —
especially an identity, actor, owner, or authorization field — write
`if not (value and value.strip()):` (reject None, "", and whitespace-only),
not `if not value:`. Pin it with a RED-first test that adjudicates/authorizes
with `value=" "` and asserts it is rejected AND nothing changed — run that
test against the pre-fix code to confirm it actually fails (proves the bypass
was real), the same discipline as [[assertion-must-encode-the-property-it-claims]].
Related: an adversarial reviewer explicitly probing the whitespace/bypass case
is what caught this — see [[cold-read-and-adversarial-review-catch-different-failures]].
