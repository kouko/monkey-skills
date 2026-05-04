# Lens: UX Critique (Nielsen-Norman)

> **Sources**:
> - Donald Norman, *The Design of Everyday Things* (Basic Books, 1988; **revised and expanded edition 2013** — significant addition: the *signifier* concept is introduced in the 2013 edition to clarify the original 1988 *affordance* concept). Affordance, signifier, mapping, feedback, and constraints are introduced in Ch 1 ("The Psychopathology of Everyday Things"); constraints get fuller treatment in Ch 4. Specific page locations vary between 1988 and 2013 editions; the 2013 expanded edition is canonical.
> - Jakob Nielsen, "10 Usability Heuristics for User Interface Design" (Nielsen Norman Group, originally 1994 based on Nielsen & Molich 1990 paper; **revised 2020** to update language and examples). The list is canonical at [https://www.nngroup.com/articles/ten-usability-heuristics/](https://www.nngroup.com/articles/ten-usability-heuristics/).

> **Synthesis note**: This file combines Norman's *Design of Everyday Things* (1988/2013) and Nielsen's 10 Heuristics (1994/2020). **This combination is organic** — Nielsen and Norman co-founded Nielsen Norman Group (NN/g) in 1998, and the two methods are routinely taught together as "NN/g UX critique." The combination in this lens reflects industry consensus more than synthetic composition. See [ADR-0003](../../../docs/adr/0003-lens-synthesis-disclosure.md) for the broader synthesis-disclosure policy.

Two complementary tools: Norman's **affordance / signifier / mapping /
feedback / constraints** for analyzing what an interface *invites and
prevents*, and Nielsen's **10 heuristics** for systematic usability
critique.

## When to apply this lens

- UI screens, app flows, websites
- Onboarding experiences
- Documentation portals (yes, docs are UX too)
- Forms, wizards, settings pages
- Any artifact with interactive elements

## When NOT to apply

- Pure text artifacts with no interaction
- Static visual content (posters, infographics) — use lens-semiotic instead
- Read-only reference material (use lens-genre)

---

## Part 1: Norman's Affordance Analysis

For each interactive element on the screen, examine five aspects:

| Aspect | Question |
|---|---|
| **Affordance** | What action does this element suggest? |
| **Signifier** | What signals invite the action? (color, shape, hover, label) |
| **Mapping** | Does the control match the outcome intuitively? |
| **Constraint** | What prevents misuse? |
| **Feedback** | What confirms the action happened? |

### Worked example: A "Subscribe" button

| Aspect | Analysis |
|---|---|
| Affordance | Click to start a subscription |
| Signifier | Strong color contrast, hover state, clear label "Subscribe" |
| Mapping | Direct (click → subscription start), no surprise |
| Constraint | Disabled until form is valid (prevents premature submit) |
| Feedback | Spinner during submit, success state after |

### Worked example: A "remember me" checkbox in a login form

| Aspect | Analysis |
|---|---|
| Affordance | Toggle persistent session |
| Signifier | Standard checkbox shape, label "Remember me" |
| Mapping | Reasonable — checkbox is binary, behavior is binary |
| Constraint | None (user can check without consequence) |
| Feedback | None (no confirmation that "remember me" worked) |

The missing feedback here is a typical UX gap. Future user can't
verify their preference was honored.

### Common affordance failures

- **Looks clickable but isn't** (decorative element with hover-like styling)
- **Is clickable but doesn't look it** (text that should be a link, shown as plain)
- **Affordance contradicts label** (button says "Save" but actually creates a draft)
- **Affordance without signifier** (gestures with no visual hint)
- **Constraint without explanation** (form rejects input without telling user why)

---

## Part 2: Nielsen's 10 Heuristics

Run each heuristic as a yes/no/partial check against the artifact.

| # | Heuristic | Question |
|---|---|---|
| 1 | Visibility of system status | Does the system tell the user what's happening? |
| 2 | Match between system and real world | Does it use familiar concepts and language? |
| 3 | User control and freedom | Can the user undo / escape easily? |
| 4 | Consistency and standards | Same actions, same names, same locations? |
| 5 | Error prevention | Does it prevent errors, not just handle them? |
| 6 | Recognition rather than recall | Are options visible vs requiring memory? |
| 7 | Flexibility and efficiency of use | Are there shortcuts for advanced users? |
| 8 | Aesthetic and minimalist design | Free of irrelevant content / decoration? |
| 9 | Help users recognize, diagnose, recover | Plain-language errors with solutions? |
| 10 | Help and documentation | Searchable, contextual help? |

### Output format for heuristics check

| # | Heuristic | Status | Evidence |
|---|---|---|---|
| 1 | Visibility of system status | ✓ | Loading spinner during submit |
| 2 | Match between system and real world | ✓ | "Cart" / "Checkout" terminology |
| 3 | User control and freedom | ⚠️ | No back button on confirmation step |
| 4 | Consistency and standards | ✓ | Buttons styled identically across flow |
| 5 | Error prevention | ✗ | Form accepts invalid email until submit |
| ... | ... | ... | ... |

A heuristic check produces 10 rows; any 3+ misses warrant attention.

## Part 3: Dark Pattern Reverse Check

UX deconstruction must include **dark pattern detection** — see
[`lens-persuasion.md`](lens-persuasion.md) for the full Brignull
12-pattern check, applied here:

| Pattern | UX manifestation |
|---|---|
| Confirmshaming | "No thanks, I don't want to save money" |
| Roach motel | Easy to subscribe, hard to cancel |
| Sneak into basket | Pre-checked add-on at checkout |
| Privacy zuckering | Default to public sharing |
| Misdirection | Visual emphasis on the path the company prefers |
| Hidden costs | Final price differs from listed price |
| Forced continuity | Free trial silently rolls into paid |
| Bait and switch | Unexpected outcome after click |
| Trick questions | Double negative in opt-out |
| Disguised ads | Sponsored content not clearly labeled |
| Friend spam | "Share with all your contacts" by default |
| Price comparison prevention | Different units / packages frustrate comparison |

For each pattern, mark: ✓ present (cite where) / ⚠️ borderline / ✗ absent.

---

## Worked example: Stripe signup flow

### Affordance analysis (key elements)

| Element | Affordance | Signifier | Mapping | Constraint | Feedback |
|---|---|---|---|---|---|
| "Get started" CTA | Begin signup | Purple, prominent | Direct | None | Page transition |
| Email field | Type email | Standard input + label | Direct | Inline validation | Real-time check |
| Country select | Choose country | Dropdown | Reasonable | Filters next options | Refreshes form |
| Stripe Tax checkbox | Opt into tax | Checkbox | Reasonable | None | None (gap) |

### Heuristics check (excerpt)

| # | Status | Evidence |
|---|---|---|
| 1 (status) | ✓ | Progress bar visible across multi-step |
| 5 (error prevention) | ✓ | Real-time email + card validation |
| 6 (recognition) | ✓ | Country pre-detected; suggested values |
| 8 (minimalist) | ✓ | Clean layout, no upsell during signup |
| 9 (errors) | ✓ | Plain-language with action suggestion |

### Dark pattern check

| Pattern | Status | Note |
|---|---|---|
| Hidden costs | ⚠️ borderline | Currency conversion fee not always upfront |
| Forced continuity | ✗ absent | Stripe doesn't trial-roll |
| Confirmshaming | ✗ absent | Opt-outs are neutral |

### Verdict

Stripe signup is largely **🟢 transparent** with one **🟡 gray-zone**
on currency-conversion fees. UX heuristics pass with high marks;
dark patterns mostly absent.

## Pitfalls

- **Heuristic checklist as ritual**: marking 10 checkboxes without
  evidence is bookkeeping. Every status mark needs a specific citation.
- **Confusing affordance with feature**: Norman's affordance is what
  the element *invites*, not what the feature *does*. A misleading
  affordance is a bug even if the feature works.
- **Dark pattern witch hunt**: legitimate persuasion ≠ dark pattern.
  Apply the **transparent / gray / manipulative / dark** spectrum
  (see lens-persuasion §"Ethical Position Verdict"), not a binary
  good/evil judgment.

## Output format

```markdown
### Affordance analysis
| Element | Affordance | Signifier | Mapping | Constraint | Feedback |
|---|---|---|---|---|---|
| ... | ... | ... | ... | ... | ... |

### Nielsen 10 heuristics
| # | Status (✓/⚠️/✗) | Evidence |
|---|---|---|
| 1 | ... | ... |
| ... | ... | ... |
| 10 | ... | ... |

### Dark pattern check
| Pattern | Status | Note |
|---|---|---|
| ... | ... | ... |
```

End with 1-line synthesis: "UX is **🟢/🟡/🔴/⚫** with **N** heuristic
issues and **M** dark patterns; the most significant gap is **X**."
