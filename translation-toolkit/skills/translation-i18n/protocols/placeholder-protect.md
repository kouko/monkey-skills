# Placeholder Protect — i18n-specific patterns

> **Base spec**: `references/protect-pass-spec.md` (functional copy of the canonical
> `scripts/canonical/protect-pass-spec.md`). Read that first — it defines the
> `⟦P:NN⟧` token format, the 8 base classes (ICU plural, curly braces, printf,
> fenced code, inline code, HTML, URL, email), the priority-order overlap
> rules, and the M1 count-parity check.
>
> This protocol layers **i18n-specific patterns on top** of the base classes. It
> does NOT replace the base spec — it adds patterns that only show up in PO /
> JSON / XLIFF / Android / iOS payloads, and clarifies how the base classes
> apply when those payloads are involved.

## Pattern stack — when this protocol applies

Run the base protect-pass first per `references/protect-pass-spec.md`. Then
apply the i18n-specific extensions below in the same priority-ordered overlap
model: earlier patterns win on overlap, longer / outer spans win on
containment.

## i18n-specific patterns

### 1. ICU `plural`, `select`, `selectordinal` — single token, ALL variants

The base spec already covers ICU plurals as P-class 1 — the entire
`{count, plural, …}` construct becomes ONE token; the inner arms are NOT
separately tokenised. The same rule applies to `select` and `selectordinal`
variants of the ICU MessageFormat:

```
SOURCE   : "{gender, select, female {Welcome, Ms. {name}} male {Welcome, Mr. {name}} other {Welcome, {name}}}"
MASKED   : "⟦P:01⟧"
TOKEN MAP: { ⟦P:01⟧: "{gender, select, female {Welcome, Ms. {name}} male {Welcome, Mr. {name}} other {Welcome, {name}}}" }
```

```
SOURCE   : "You are {position, selectordinal, one {#st} two {#nd} few {#rd} other {#th}} in line"
MASKED   : "You are ⟦P:01⟧ in line"
TOKEN MAP: { ⟦P:01⟧: "{position, selectordinal, one {#st} two {#nd} few {#rd} other {#th}}" }
```

**Why one token, not many:** ICU MessageFormat is a complete sub-grammar
inside the source string; translating the inner arms in isolation would
desyntax the construct. The translation engine MUST output the entire
construct verbatim from the token map; the per-language arm rewriting is the
target-locale resource author's job (typically done by hand or via a separate
ICU plural tool), not the LLM's.

Gender selectors are the same shape as `select` — the `gender` discriminator
is just a domain name; the protector treats it identically.

### 2. Android `<plurals>` blocks — child `<item>` values protected individually

Android resource format wraps plural variants in XML, NOT inside an ICU
MessageFormat string:

```xml
<plurals name="num_messages">
    <item quantity="one">%d message</item>
    <item quantity="other">%d messages</item>
</plurals>
```

This is **structurally different** from ICU plural strings. The XML wrapper
is a format-roundtrip concern (see `format-roundtrip.md` §Android), NOT a
protect-pass concern — the protect-pass operates on the **inner text** of
each `<item>` independently. Each `<item>` value goes through protect-pass
separately, with its own token map and its own translation pass.

After parsing the Android XML in Layer 2, the inner `%d message` /
`%d messages` strings are protected like any other printf-style string:

```
SOURCE   : "%d message"
MASKED   : "⟦P:01⟧ message"
TOKEN MAP: { ⟦P:01⟧: "%d" }
```

The XML wrapper, the `name` attribute, the `quantity` attributes, and the
ordering of `<item>` children are all preserved by the format-roundtrip Layer
2 parser — protect-pass never sees them.

The same rule applies to `<string-array>` children — each `<item>` is an
independent translation unit.

### 3. HTML inside i18n strings — base HTML class wins, attribute order preserved

UI strings frequently embed HTML for inline emphasis, links, or accessibility
hints:

```
SOURCE   : 'Read <a href="https://example.com" title="docs">our guide</a> first.'
MASKED   : 'Read ⟦P:01⟧our guide⟦P:02⟧ first.'
TOKEN MAP: { ⟦P:01⟧: '<a href="https://example.com" title="docs">', ⟦P:02⟧: '</a>' }
```

The base HTML class (P-class 6) handles the masking — the URL inside `href`
is owned by the surrounding tag's span (per base-spec containment rule).
**Attribute order is preserved verbatim** because the entire opening tag is
captured as one opaque substring; the LLM never sees the attribute list and
cannot reorder it. Restoration is byte-identical.

The translation engine MUST preserve the **link text** (`our guide`) as
translatable prose between the two tokens. WRITER and REVISER outputs that
swallow the inner text, drop one of the tags, or invent new attributes
trigger M1 / M2 failures.

### 4. Format-arg tags inside `<![CDATA[...]]>` (Android XML) — CDATA boundaries are preserve-as-is

Android XML occasionally wraps strings in CDATA sections to escape `<` `>` `&`
that would otherwise need entity-encoding:

```xml
<string name="terms"><![CDATA[<b>I agree</b> to the <a href="%1$s">terms</a>.]]></string>
```

The CDATA wrapper is a parser-layer concern (the Layer 2 Android XML parser
strips `<![CDATA[…]]>` before handing the inner text to protect-pass, then
re-wraps after restore). Protect-pass operates on the **decoded inner
text**:

```
SOURCE   : '<b>I agree</b> to the <a href="%1$s">terms</a>.'
MASKED   : '⟦P:01⟧I agree⟦P:02⟧ to the ⟦P:03⟧terms⟦P:04⟧.'
TOKEN MAP:
  ⟦P:01⟧: '<b>'
  ⟦P:02⟧: '</b>'
  ⟦P:03⟧: '<a href="%1$s">'
  ⟦P:04⟧: '</a>'
```

The format-arg `%1$s` inside the `href` is owned by the HTML tag's span (base
spec HTML > URL containment rule); it is NOT separately tokenised. After
restore + format-roundtrip the CDATA wrapper is reattached.

If the Android XML is mis-authored (no CDATA, raw `<` and `>`), the format
parser bails to a `WARN` in the audit-trail and asks the user to either CDATA-
wrap the source or pre-escape the entities; protect-pass does not attempt to
heal mal-formed XML.

### 5. iOS `.strings` escaped quotes — handled by parser, not protect-pass

iOS `.strings` uses C-style escapes for embedded quotes and backslashes:

```
"alert.title" = "Don\"t forget to save your work!";
```

Escaping is a Layer 2 / Layer 5 parser concern (see `format-roundtrip.md`
§iOS). Protect-pass operates on the **decoded inner text** after the parser
has resolved escapes (`Don"t forget…`); restore + format-roundtrip re-escapes
on write. No `⟦P:NN⟧` token is involved for escape sequences.

If the source contains placeholder format args (`%@`, `%1$@`, etc.), those
are protected by the base printf class.

## Order of operations (i18n)

Per Layer 2 of `SKILL.md`:

1. **Parse format** (Layer 2 step 1) — strip XML / CDATA wrapper, decode
   `.strings` escapes, resolve key paths. Hands a clean per-entry string to
   protect-pass.
2. **Protect-pass** (Layer 2 step 2) — base 8 classes per
   `references/protect-pass-spec.md`, then i18n extensions above.
3. **Source analysis** (Layer 2 step 3) — operates on masked text.
4. **Glossary resolve** (Layer 2 step 4) — operates on masked text.
5. **Core loop** (Layer 3) — DRAFT / REFLECT / IMPROVE see only masked text.
6. **M1 verification** (Layer 4) — count `⟦P:NN⟧` tokens in v2 vs source.
7. **Restore** (Layer 5 step 1) — swap `⟦P:NN⟧` → original substring.
8. **Re-encode + re-wrap** (Layer 5 step 2 / format-roundtrip) — re-escape
   iOS `.strings`, re-wrap CDATA, re-emit XML / JSON / PO structure.

Steps 1, 7, 8 are owned by `protocols/format-roundtrip.md`. Steps 2-6 are
governed by this protocol + `references/protect-pass-spec.md`.

## What is NOT covered here

- **Markdown AST protection** (front-matter YAML, fenced code, link syntax) —
  see `translation-doc/protocols/markdown-ast-protect.md` (Task D4).
- **Brand-voice forbidden phrases** — see `translation-creative` (Task D5).
- **Existing-target diff protection in audit-only mode** — see
  `translation-audit` (Task D6).

## See also

- `references/protect-pass-spec.md` — canonical 8-class base spec, restoration
  rule, M1 count-parity check, examples.
- `protocols/format-roundtrip.md` — per-format wrapper handling (XML / CDATA
  / `.strings` escapes / PO / XLIFF).
- `references/verification-gates.md` §M1 — exact diff format on placeholder
  count mismatch.
- `references/core-loop.md` §7 — placeholder preservation as a hard contract
  on WRITER and REVISER.
