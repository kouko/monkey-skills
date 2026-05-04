# Fixture: Stripe signup flow (text-extract, 2024)

**Source**: https://dashboard.stripe.com/register (signup flow, public access)
**Accessed**: 2026-05-04
**License**: Quoted as fair-use educational analysis of publicly accessible signup UX. Text-only extraction; no screenshots. UI element descriptions in plain English.
**Eval target**: artifact-deconstruct must apply NN/g 10 heuristics, identify ≥3 affordances, check Brignull 12 dark patterns, assign ethical position per persuasion principle.

---

## Step 1: Email + password

**Page title**: "Create your Stripe account"

**Subtitle**: "Already have an account? Sign in"

**Form**:
- Field: Email address (input, with inline validation: red if invalid format, green checkmark if valid)
- Field: Full name (input)
- Field: Password (input, masked)
  - Helper text below: "Use at least 10 characters. Avoid common passwords."
  - Real-time strength meter (red / yellow / green)
- Checkbox: "I agree to Stripe's Terms of Service and Privacy Policy" (links inline; checkbox unchecked by default; submit disabled until checked)

**Primary CTA**: "Create account"
**Secondary**: "Sign in" (top-right corner)

**Status indicator**: 4-step progress bar at top: ●○○○ (filled: step 1)

---

## Step 2: Verify email

**Page title**: "Check your email"

**Body**: "We've sent a 6-digit code to <user-email>. Enter it below."

**Form**:
- Field: 6-digit code (six individual input boxes; auto-advance on each digit; auto-submit when complete)

**Secondary actions**:
- "Resend code" (clickable; greyed for first 30 seconds; shows countdown)
- "Use a different email" (link)

**Status**: ●●○○ (filled: 1 + 2)

---

## Step 3: Country + business type

**Page title**: "Tell us about your business"

**Form**:
- Field: Country (dropdown, pre-populated based on IP geo-detection)
- Field: Business type (radio):
  - Individual / sole proprietor
  - Company
  - Non-profit
  - Government

**Helper text**: "This affects which info we'll need next. You can change it later."

**Primary CTA**: "Continue"
**Secondary**: "Back" (text link, lower-left)

**Status**: ●●●○

---

## Step 4: Activation summary

**Page title**: "Almost there"

**Body**: "Stripe needs a few more details to activate payments. You can do this now or later — your account is ready to use either way."

**Two options shown side-by-side**:
- **Activate now** (primary CTA): "Add bank, identity, business details" — estimated 5 minutes
- **Activate later** (secondary CTA, equal visual weight): "Skip for now"

**Below both**: "You'll need to activate payments before you can accept live charges. Test mode works without activation."

**Status**: ●●●●

---

## Annotations for evaluator

The fixture is constructed to contain (so eval can verify):

### Affordance analysis (≥3 affordances)

| Element | Affordance | Signifier | Mapping | Constraint | Feedback |
|---|---|---|---|---|---|
| Step 1 email field | Type email | Standard input + label | Direct | Inline format validation | Red/green inline |
| Step 1 password field | Set password | Masked input + strength meter | Direct | Min 10 chars enforced | Live strength color |
| Step 2 code boxes | Enter 6-digit code | Six adjacent boxes | Direct (visual chunks) | Numeric only | Auto-advance per digit |
| Step 4 dual CTA | Choose activate-now-or-later | Equal visual weight, both labeled | Direct | None (genuine choice) | Page transition |

### NN/g 10 heuristics (full check)

| # | Heuristic | Status | Evidence |
|---|---|---|---|
| 1 | Visibility of system status | ✓ | 4-step progress bar persistent |
| 2 | Match real world | ✓ | Plain English ("Create your account" / "Almost there") |
| 3 | User control / freedom | ✓ | "Back" available; "Use a different email" on Step 2 |
| 4 | Consistency / standards | ✓ | Same button styling across all 4 steps |
| 5 | Error prevention | ✓ | Real-time email + password validation; submit disabled until ToS checked |
| 6 | Recognition rather than recall | ✓ | Country pre-detected; business type as radio (visible options) |
| 7 | Flexibility / efficiency | ✓ | Auto-advance on code entry; auto-submit on complete |
| 8 | Aesthetic / minimalist | ✓ | One question per step; no upsell during signup |
| 9 | Help users recover from errors | ✓ | Plain-language inline errors with suggestion |
| 10 | Help / documentation | ⚠️ | No contextual help link visible during signup |

### Cialdini persuasion principles

| Principle | Triggered? | How | Position |
|---|---|---|---|
| Reciprocity | ✓ | "Test mode works without activation" — gift before commitment | 🟢 Transparent |
| Commitment | ✓ | Multi-step (4) — small commits accumulate | 🟢 Transparent (necessary, not engineered) |
| Social proof | ✗ | Not used in signup flow | — |
| Authority | ✓ (mild) | Brand as authority signal | 🟢 |
| Liking | — | Not used | — |
| Scarcity | ✗ | None | — |
| Unity | ✗ | None | — |

### Brignull 12 dark patterns

| Pattern | Detected? | Note |
|---|---|---|
| Confirmshaming | ✗ | "Skip for now" is neutral, not "I don't want to be successful" |
| Roach motel | ✗ | Account deletion findable in settings |
| Hidden costs | ✗ | Stripe fees disclosed elsewhere; signup itself is free |
| Forced continuity | ✗ | No trial-rollover; activation is optional |
| Bait and switch | ✗ | Each step does what it says |
| Trick questions | ✗ | All form labels are positive-direction |
| Sneak into basket | ✗ | No add-ons during signup |
| Disguised ads | ✗ | None |
| Misdirection | ✗ | "Activate now" and "Activate later" have equal visual weight (Stripe's deliberate design) |
| Privacy zuckering | ✗ | Only essential fields requested |
| Friend spam | ✗ | None |
| Price comparison prevention | ✗ | Pricing not part of signup flow |

### Verdict

**🟢 Transparent UX**. 9/10 Nielsen heuristics pass; help/docs is the
only ⚠️. Cialdini principles used minimally and only as side-effects
of the multi-step flow itself. Zero dark patterns detected.

**Most distinctive feature**: Step 4's **equal-weight dual CTA**
("Activate now" vs "Activate later"). Most signup flows would
visually de-emphasize the "later" option to reduce abandonment.
Stripe's choice signals confidence — they trust users to come back.

### Negative space (3+)

- No "why us / why Stripe" pitch during signup (assumed pre-decided)
- No competitor mention (e.g., "switching from Square?")
- No referral / social-share invitation
- No upsell or feature reveal during signup
- No urgency mechanism (countdown, scarcity)

The cumulative absence is itself a design choice: Stripe's signup is
**logistically minimal**, signaling that Stripe sells via developer
trust, not signup-flow seduction.
