---
schema_version: 2.0
anchor_slug: en-kate-kiefer-lee-mailchimp-voice-tone
culture: EN
quadrant: Q3
landmark: center
creator_type: named content strategist — Mailchimp Voice & Tone style guide author (styleguide.mailchimp.com, 2013-), co-author "Nicely Said: Writing for the Web" (New Riders, 2014, with Nicole Fenton)
recast_from: en-mailchimp-voice-and-tone (brand anchor v1.3.x → named individual v1.8.0)
date: 2026-04-21
---

### Kate Kiefer Lee — Mailchimp Voice & Tone (EN | Q3 center, peer-helpful warmth)

## Voice direction
**What this register achieves**: Address one specific person — not "users," not "our community" — in the plain, uninflated English of a helpful colleague who just walked over to your desk. Warmth comes from precision, honesty, and context-appropriate restraint (the voice/tone split), NOT from corporate softeners ("we're so excited," "please kindly," "amazing community"). Humor is permitted but surgically excluded from error, money, privacy, and compliance states.

**Native critical read** (5):
- "Our voice doesn't change much from day to day, but our tone changes all the time" (Kate Kiefer Lee, styleguide.mailchimp.com/voice-and-tone/, 2013 — the voice-vs-tone split she codified, now the canonical distinction in UX writing)
- "Mailchimp's sense of humor is dry, and our mouth is clean. We're friendly without being folksy, and smart without being stuffy" (styleguide.mailchimp.com/voice-and-tone/, Kate's authored brand-voice line — "friendly but not folksy, smart but not stuffy" travels as the shorthand)
- "When in doubt, be plain. Plain is almost always better than clever" (Lee & Fenton, *Nicely Said*, 2014, Ch.2 "Principles" — the clear-over-clever operating rule)
- "Write for one person. Imagine a real human reading your words" (*Nicely Said*, 2014, Ch.1 — "you" is one reader, "we" is specific people at Mailchimp, never brand plural)
- "Keep the comedy out of your microcopy. Don't joke in error messages, billing, or legal" (Kate Kiefer Lee, "The Art and Science of UX Writing" talk, 2014, and *Nicely Said* Ch.8 — humor-suppression discipline by context, not by brand rule)

## Prose mechanics (8)

1. **Contractions always in flow copy** — "they give your writing an informal, friendly tone" (Voice & Tone, grammar-and-mechanics). Never "do not" / "cannot" / "we will" in UI.
2. **Sentence-initial "you" addresses one reader; "we" names specific people (a team, a support rep), not the brand as plural entity** — "Write like a person, not like a company" (*Nicely Said*, Ch.1)
3. **Bullet-heavy microcopy over prose paragraphs in help / settings / onboarding** — scannable lists with parallel sentence openings; one action per bullet
4. **Affirmative framing, imperative mood for instructions** — "Add your list" not "Don't forget to add your list"; "Check your email" not "Please be sure to check"
5. **Humor forbidden in: error states, money flows (billing, refunds, failed charges), privacy / data requests, compliance shutdowns, unsubscribe** — Kate's "keep the comedy out of your microcopy" rule is absolute, not a preference
6. **Lowercase the internet** — `email`, `internet`, `website`, `online` lowercase; anti-corporate-capitalization tic
7. **Em-dashes without spaces for asides; exclamation points sparingly and never in errors** — `text—aside—text`; one exclamation per screen at most
8. **Ban list: "powerful," "seamless," "effortless," "revolutionary," "leverage," "synergy," "solution," "please kindly," "we're so excited to announce"** — enterprise-ese and grandiose adjectives are failure states, not stylistic choices (Kate, *Nicely Said* Ch.4 "Type of Content")

## Examples (6 verbatim, ≥2 sources)

- "Our voice is human, it's familiar, friendly, and straightforward. Our priority is explaining our products and helping our users get their work done so they can get on with their lives." (styleguide.mailchimp.com/voice-and-tone/, Kate Kiefer Lee authored — voice-and-tone page)
- "Mailchimp's sense of humor is dry, and our mouth is clean. We're friendly without being folksy, and smart without being stuffy." (styleguide.mailchimp.com/voice-and-tone/ — the line that became the template for SaaS voice guides 2015-2023)
- "Oops! Looks like you forgot to enter an email address." (Mailchimp signup form error, pre-2020 UI — plain apology, named mistake, clear next step, no joke)
- "High five!" (Mailchimp post-send confirmation screen, pre-2020 UI — short affirmation; warmth carried by the two words + Freddie, not by copy elaboration)
- "Write for one person. Even if your site reaches millions, each reader is alone with their screen." (Lee & Fenton, *Nicely Said: Writing for the Web*, New Riders, 2014, Ch.1 "Principles," p.12)
- "Plain language is not dumbed down. It is the hardest kind of writing to do well." (Lee & Fenton, *Nicely Said*, 2014, Ch.2, p.28 — Kate's plain-over-clever discipline, restating Orwell without attribution)

## Don't / Over-mimic

- **Failure mode**: LLM defaults into "Mailchimp-ish" (contractions + plain English + mild warmth) automatically — Kate's style guide is saturated in training data and became the template for every 2015-2023 SaaS UX writing guide (Slack, Shopify, Dropbox, Atlassian, Asana). LLM FAILS on: (a) voice-vs-tone discipline (LLM collapses to a single flat register, ignoring context-switch); (b) humor-suppression in error / money / compliance (LLM softens serious messages with whimsy); (c) "we" as specific people, not brand plural (LLM writes "our team is excited"); (d) enterprise-ese ban list (LLM slips "powerful" / "seamless" / "please kindly" back in); (e) one-reader "you" (LLM defaults to "users," "customers," "our community").
- **Mitigation** (≤15 words): "Switch tone by context; ban enterprise-ese; address one person; no jokes in errors"

## Metadata

- Trigger slug: `en-kate-kiefer-lee-mailchimp-voice-tone`
- Over-mimic risk: **HIGH** — Mailchimp Voice & Tone (2013-) is the genre-template for SaaS UX writing; LLM baseline is already a diluted copy of this register, so producing it adds no signal without the specific disciplines (voice-vs-tone split, context humor-suppression, "we"-as-people, ban list)
- Pairs with form: [microcopy, short-form, light-action, help-doc]
- Cross-reference-valid-for: ja: MEDIUM (voice-vs-tone split translated widely in JP UX writing community via 『Nicely Said』 and 18F guidelines); zh: WEAK (Chinese UX writing communities reference Mailchimp but the contraction / "you"-addressing mechanics don't port)
