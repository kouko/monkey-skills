# intake-explicit — explicit-input intake protocol

**Mode**: `--explicit` / `-e` (opt-in)
**Inverse**: see `protocols/intake-auto.md` (default)

---

## Purpose

In **explicit** mode the user supplies all 5 axes plus skopos directly — no source-analysis inference. Use when:

- The auto-inferred spec misfired and the user wants to correct it.
- The user has a strong opinion about strategy / register / domain that source content alone wouldn't reveal (e.g. "we want to foreignize even though it's marketing copy").
- The downstream skill is `translation-audit` and the user wants the audit to compare against a specific declared register / strategy rather than the LLM's guess.

All values land in the audit trail with `inferred=false` per axis, distinguishing user authority from heuristic guess.

---

## The 5 axes — allowable values

| Axis | Allowable values | Required? | Notes |
|---|---|---|---|
| **mode** | `literal` \| `faithful` \| `localized` \| `transcreation` | yes | controls reflection-axis count (4D vs 5D) and S1 threshold |
| **register** | `formal` \| `neutral` \| `warm` \| `playful` | yes | checked by S2 gate |
| **strategy** | `domestication` \| `foreignization` | yes | independent of mode |
| **locale** | BCP-47 tags — both `source_locale` and `target_locale` | **always required** (no auto) | v0.1.0 first-class set: `en-US` / `ja-JP` / `zh-TW` / `zh-CN` |
| **domain** | one or more from `{general, ui, tech.software, tech.web, tech.data, tech.crypto, gov, legal, medical, finance, marketing, statistics, typography}` | yes | comma-join when multiple (e.g. `ui,tech.software`) |

**Skopos** is a free-form string, not enumerated:

- Prompt the user with: **"Who reads this and what action should they take?"**
- Examples of acceptable answers:
  - `"App users navigating the settings screen — should be able to find and tap a button"`
  - `"Investors evaluating quarterly earnings — must understand the financial summary in 5 minutes"`
  - `"Internal engineers reading API docs — need to integrate the endpoint correctly on first attempt"`

---

## Interaction pattern

The skill walks the user through 6 prompts (5 axes + skopos) sequentially. If the user invoked `--explicit` after an auto pass, the prompts are seeded with the auto inferences as defaults — the user accepts (Enter) or overrides.

### Prompt sequence

```
1. mode? [literal / faithful / localized / transcreation]
   (default if seeded from auto: <auto value>)

2. register? [formal / neutral / warm / playful]
   (default if seeded: <auto value>)

3. strategy? [domestication / foreignization]
   (default if seeded: <auto value>)

4. source locale? (BCP-47, e.g. en-US, ja-JP, zh-TW, zh-CN)
   (default: <user-provided at invocation>)

5. target locale? (BCP-47)
   (default: <user-provided at invocation>)

6. domain? (one or more, comma-joined: e.g. "ui" or "ui,tech.software")
   (default if seeded: <auto value>)

7. skopos? (Who reads this and what action should they take?)
   (default if seeded: <auto value>)
```

### Sample transcript

User has invoked the skill on a short marketing brief, source-locale `en-US`, target-locale `ja-JP`, `--explicit` flag set without prior auto pass.

```
> Mode? Choose one: literal | faithful | localized | transcreation
> transcreation

> Register? Choose one: formal | neutral | warm | playful
> warm

> Strategy? Choose one: domestication | foreignization
> domestication

> Source locale? (BCP-47)
> en-US

> Target locale? (BCP-47)
> ja-JP

> Domain? (one or more from the 13-domain taxonomy, comma-joined)
> marketing

> Skopos — who reads this and what action should they take?
> Landing-page hero CTA for productivity SaaS — visitors should sign up for a free trial in under 30 seconds
```

Resulting intake spec:

```json
{
  "mode": "transcreation",
  "register": "warm",
  "strategy": "domestication",
  "source_locale": "en-US",
  "target_locale": "ja-JP",
  "domain": "marketing",
  "intent": "Landing-page hero CTA for productivity SaaS — visitors should sign up for a free trial in under 30 seconds",
  "inferred": {
    "mode": false,
    "register": false,
    "strategy": false,
    "domain": false
  }
}
```

---

## Seeded-from-auto pattern (override case)

When the user re-invokes with `--explicit` after an auto pass disappointed them, EVERY axis the user changes must capture the auto-inferred value via `add_inferred_value`. Example:

Auto inferred `{mode: faithful, register: neutral, strategy: domestication, domain: general}`. User overrides `mode` to `transcreation` and leaves the rest. The audit-trail builder sequence:

```python
# Step 1: set the user-confirmed final spec.
builder.set_intake(
    mode="transcreation",          # user override
    register="neutral",            # user accepted auto
    strategy="domestication",      # user accepted auto
    source_locale="en-US",
    target_locale="ja-JP",
    domain="general",              # user accepted auto
    intent="brand-voice tagline for app store listing",
    inferred={
        "mode": False,             # user overrode
        "register": False,         # user explicitly confirmed
        "strategy": False,
        "domain": False,
    },
)

# Step 2: capture what auto would have picked for the overridden axis
# so the audit shows the disagreement.
builder.add_inferred_value("mode", "faithful")
```

This produces `intake.inferred_values: {"mode": "faithful"}` in the audit trail — the auto guess preserved alongside the user override, ready for retrospective heuristic-tuning analysis.

When the user explicitly **confirms** an auto value (i.e. accepts the seeded default), `inferred=false` for that axis — the user took authority, even if the value is the same. `add_inferred_value` is NOT called in this case (no disagreement to record).

---

## Validation rules

- All 5 axis values MUST be one of the enumerated allowable values. Reject and re-prompt on typos.
- `source_locale` and `target_locale` MUST be valid BCP-47. Reject empty input — locale never has a heuristic default.
- `domain` MUST contain at least one taxonomy value. Reject empty.
- `intent` (skopos) — non-empty string; no enumeration constraint. Empty string warned, default placeholder offered.
- `source_locale != target_locale` (translating a doc to itself is rejected).

---

## What this protocol does NOT do

- Does **not** infer anything from source content. That is `protocols/intake-auto.md`'s job.
- Does **not** translate or audit. Intake captures parameters only.
- Does **not** silently default any axis when `--explicit` is set — every axis is explicitly prompted (with seeded defaults if an auto pass preceded). Silently defaulting in explicit mode would defeat the purpose of the flag.
