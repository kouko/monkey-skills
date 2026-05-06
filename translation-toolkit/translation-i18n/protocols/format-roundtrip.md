# Format Roundtrip — per-format read+write algorithms

> Layer 2 step 1 (parse) and Layer 5 step 2 (write back) for the five i18n
> format families this skill handles. Each section gives the parse model, the
> write-back invariants, and a brief code-shape sketch (pseudo-Python; library
> equivalents in any runtime).
>
> Read the SKILL body first for context on where these slot into the
> 5-layer pipeline. This protocol is invoked **after** the format-checklist
> preflight (`checklists/i18n-format-checklist.md`) and **before**
> protect-pass (`protocols/placeholder-protect.md`).

## Detection

Auto-detect by **extension first**, then by content sniffing on ambiguity:

| Extension | Detected as | Sniff fallback if mis-named |
|---|---|---|
| `.po` / `.pot` | gettext PO | starts with `msgid ""` block |
| `.json` | JSON i18n | top-level `{ ... }` with string-valued leaves |
| `.xliff` / `.xlf` | XLIFF 2.x | root tag `<xliff version="2.x">` |
| `strings.xml` | Android resources | root tag `<resources>` |
| `.strings` | iOS NSLocalizedString | line shape `"key" = "value";` |

Mismatched extension vs content → fail-fast with checklist item #2 (file
format detected). Do not silently coerce.

## PO (gettext)

### Read

Parse via polib-equivalent algorithm. Each entry is one of:

- **singular** — `msgid` + `msgstr`
- **plural** — `msgid` + `msgid_plural` + `msgstr[0]`, `msgstr[1]`, ...
- **disambiguated** — same `msgid` with different `msgctxt` (each `msgctxt`
  yields a distinct entry)

Preserve, do not mutate:
- `msgctxt` (translation context)
- `msgid_plural` (plural source form)
- All comment classes:
  - `#:` reference (file:line)
  - `#.` extracted-comment (translator notes from source code)
  - `#,` flag (`fuzzy`, `c-format`, `python-format`, etc.)
  - `# ` translator-comment
- `obsolete` markers (`#~ msgid …`)
- Header entry (the `msgid ""` block at the top — `Project-Id-Version`,
  `Language`, `Plural-Forms`, etc.). The `Language` header MUST be updated to
  the target locale on write.

### Translate

Send `msgid` (and `msgid_plural` for plural entries) through Layer 2-4. The
translated forms are written into `msgstr` (singular) or `msgstr[N]`
(plural). For plural entries, the count of `msgstr[N]` slots is determined by
the target language's `Plural-Forms` header (e.g. Japanese has 1 plural form,
English has 2, Polish has 3). The skill MUST consult `Plural-Forms` from the
target locale's PO standard rather than copying the source count.

Skip entries flagged `#, fuzzy` from a previous translation pass — they need
human review before the i18n skill can safely overwrite them. Surface as
warnings in the audit-trail.

### Write

```python
# pseudo-code
import polib
po = polib.pofile(source_path)
po.metadata['Language'] = target_locale
po.metadata['Plural-Forms'] = plural_forms_for(target_locale)
for entry in po:
    if 'fuzzy' in entry.flags:
        continue  # surface as WARN
    if entry.msgid_plural:
        for n in range(plural_count_for(target_locale)):
            entry.msgstr_plural[n] = translate_plural(entry, n)
    else:
        entry.msgstr = translate(entry.msgid)
po.save(target_path)
```

## JSON

### Read

Parse with the runtime's JSON library. Walk recursively; every **string-valued
leaf** is a translation unit. Build a flat map of `dot.notation.key.path` →
`source string` (arrays use `[N]` index in the path).

```json
{ "dialog": { "cancel": "Cancel", "confirm": "OK" }, "errors": ["Network", "Timeout"] }
```

→
```
dialog.cancel       → "Cancel"
dialog.confirm      → "OK"
errors[0]           → "Network"
errors[1]           → "Timeout"
```

Skip:
- non-string leaves (numbers, booleans, nulls — pass through unchanged)
- keys flagged `"x-translate": false` if the source convention uses such
  metadata (sniff first; do not assume)
- keys ending in `_meta` / `_id` / `_url` if the project's existing target
  files leave them untranslated (heuristic; surfaces as audit-trail note)

### ICU vs interpolation convention detection

JSON i18n payloads use either ICU MessageFormat (`{count, plural, …}`) or
template interpolation (`{{var}}`, `{var}`, `%(var)s`, `${var}`). Detect by
sampling the first ~20 strings:

- ≥30% contain `{name, plural, …}` → assume ICU; protect-pass uses ICU class
- ≥30% contain `{{var}}` → assume Mustache-style; protect-pass uses curly class
- mixed / neither → fall through to base 8-class protect-pass

The detected convention is recorded in the audit-trail's `intake.metadata`
for downstream visibility.

### Write

**Preserve key order.** Python 3.7+ dict insertion order, JS `Object.keys`
insertion order, etc. — every modern JSON library preserves order on parse +
serialise. Verify by round-tripping a sample on the runtime first.

Preserve indentation and whitespace style. Detect from source: 2-space,
4-space, tab. Use `json.dumps(..., indent=2 / 4 / "\t", ensure_ascii=False)`
or equivalent. `ensure_ascii=False` is mandatory for CJK output (otherwise
every CJK character escapes to `\uXXXX` and the file becomes unreadable in
diffs).

```python
import json
data = json.load(open(source_path))
walk_and_translate_strings_in_place(data)  # respects key order
json.dump(data, open(target_path, 'w'),
          indent=detected_indent, ensure_ascii=False)
```

## XLIFF 2.x

### Read

XLIFF 2.x structure (XLIFF 1.2 is older and still in the wild — sniff
`<xliff version="…">` to pick the parser; v0.1 of this skill targets 2.x
primarily, with 1.2 as a best-effort fallback that falls through to the same
write contract):

```xml
<xliff version="2.0" srcLang="en-US" trgLang="ja-JP" xmlns="urn:oasis:names:tc:xliff:document:2.0">
  <file id="f1">
    <unit id="u1">
      <segment>
        <source>Cancel</source>
        <target>キャンセル</target>
      </segment>
    </unit>
  </file>
</xliff>
```

Each `<unit>` is one translation unit; each `<segment>` is one substring
within it. A `<unit>` may contain multiple `<segment>` children for
sentence-level segmentation. Translate each `<source>` → write `<target>` in
the same `<segment>`.

Preserve:
- `<unit>` `id` attribute (canonical translation-unit identifier)
- `<segment>` order within a unit
- `<file>` `id` and any `original=` attribute (source-file pointer)
- Inline elements within `<source>`: `<ph>` (placeholder), `<pc>` (paired
  code), `<sc>` / `<ec>` (start / end code) — these are XLIFF's own
  placeholder mechanism. Mask each as one `⟦P:NN⟧` token; restore byte-
  identical on write.
- `xml:space="preserve"` on entries that have it — those entries' whitespace
  must be byte-identical on write.

### Locale normalisation

XLIFF often uses `srcLang="en_US"` (underscore). BCP-47 standard is hyphen
(`en-US`). The toolkit's intake-spec uses hyphen form. On read, convert
underscore → hyphen for matching against the intake-spec; on write, preserve
whatever form the source used **for the file's own attributes**, but the
intake-spec / audit-trail use hyphen exclusively. This is also enforced by
checklist item #5 (target locale BCP-47 valid).

### Write

Use a streaming XML library (lxml / xml.etree / equivalent). Set or update
`trgLang` on the root element. Write `<target>` next to each `<source>`.

```python
from lxml import etree
tree = etree.parse(source_path)
ns = {'x': 'urn:oasis:names:tc:xliff:document:2.0'}
root = tree.getroot()
root.set('trgLang', target_locale)
for unit in root.findall('.//x:unit', ns):
    for seg in unit.findall('x:segment', ns):
        src = seg.find('x:source', ns)
        tgt = seg.find('x:target', ns) or etree.SubElement(seg, '{...}target')
        tgt.text = translate_inline(src)  # preserves <ph>/<pc> as ⟦P:NN⟧
tree.write(target_path, xml_declaration=True, encoding='utf-8')
```

## Android `strings.xml`

### Read

```xml
<resources>
    <string name="dialog_cancel">Cancel</string>
    <string name="hello_world" translatable="false">Hello %1$s</string>
    <plurals name="num_messages">
        <item quantity="one">%d message</item>
        <item quantity="other">%d messages</item>
    </plurals>
    <string-array name="planets">
        <item>Mercury</item>
        <item>Venus</item>
    </string-array>
</resources>
```

Translation units:
- Each `<string>` (unless `translatable="false"`)
- Each `<item>` inside `<plurals>` (each is independent through protect-pass)
- Each `<item>` inside `<string-array>`

Preserve:
- `name` attributes (key — never translate)
- `translatable="false"` (skip, but write back unchanged)
- `quantity` attributes inside `<plurals>` (mapping is target-locale-driven —
  e.g., Japanese only needs `other`)
- `<![CDATA[…]]>` wrappers (see `placeholder-protect.md` §4)

### Android-specific escape rules

- `'` (apostrophe) → `\'` (or wrap whole string in `"..."`)
- `"` (double quote) → `\"`
- `\` (backslash) → `\\`
- newline → `\n`

The Layer 2 parser MUST decode escapes before handing text to protect-pass;
the Layer 5 writer MUST re-escape on output.

### Format-arg tags

`%1$s`, `%2$d`, `%s`, `%d` — protected by base printf class. The `$N` form is
positional and language-independent; the LLM MUST preserve the index `N`
exactly (this is what the M1 set-equality check enforces — token IDs
correspond to original positional indices).

### Write

Use a streaming XML library; preserve element order, comments, and
whitespace between elements.

```python
from lxml import etree
tree = etree.parse(source_path)
root = tree.getroot()
for s in root.findall('string'):
    if s.get('translatable') == 'false':
        continue
    s.text = translate_with_escape(s.text)
for p in root.findall('plurals'):
    target_quantities = quantities_for(target_locale)  # may be subset of source
    for item in list(p):
        # rewrite each <item> with target-locale quantity set
        ...
tree.write(target_path, xml_declaration=True, encoding='utf-8')
```

## iOS `.strings`

### Read

Plain text; each non-comment, non-blank line matches:

```
"key" = "value";
```

Comments use `/* … */` (block) or `//` (line). Both styles are preserved on
write — they often carry translator notes (`/* Title of the cancel button */`).

```
/* Title of the cancel button */
"dialog.cancel" = "Cancel";

/* Greeting with user name */
"home.greeting" = "Hello, %@!";
```

### Read encoding

Modern Xcode emits `.strings` as UTF-8. Older toolchains emit UTF-16 LE
with BOM (`FF FE`). Detect by sniffing the first 2 bytes; decode accordingly.

### iOS-specific escape rules

- `\"` → `"`
- `\\` → `\`
- `\n` → newline
- `\r` → carriage return
- `\t` → tab
- `\U0041` → Unicode escape (rare; preserve verbatim if encountered)

The Layer 2 parser MUST decode escapes; the Layer 5 writer MUST re-escape
backslashes and quotes on output.

### Format args

`%@` (Objective-C object), `%d`, `%1$@`, `%2$d`, etc. — protected by base
printf class.

### Write

```python
def parse_strings_file(path):
    text = open(path, encoding=detect_encoding(path)).read()
    return list(iter_strings_entries(text))  # yields (comment, key, value)

def write_strings_file(path, entries, target_locale):
    with open(path, 'w', encoding='utf-8') as f:
        for comment, key, value in entries:
            if comment:
                f.write(f'{comment}\n')
            f.write(f'"{key}" = "{escape_ios(value)}";\n\n')
```

Always write UTF-8 on output (modern Xcode-friendly), regardless of source
encoding. Surface any encoding conversion in the audit-trail.

## Output naming

Default convention when no explicit output path is given:

| Source | Output |
|---|---|
| `messages.po` | `messages.<target_locale>.po` |
| `en.json` | `<target_locale>.json` |
| `en.xliff` | `<target_locale>.xliff` (or write `<target>` in-place if monolingual XLIFF) |
| `strings.xml` (in `values/` dir) | `strings.xml` (in `values-<target>/` dir, Android convention) |
| `Localizable.strings` (in `en.lproj/`) | `Localizable.strings` (in `<target>.lproj/`) |

The exact mapping is project-convention-dependent; the skill emits a warning
if the inferred output path collides with an existing non-empty file, and
honours an explicit `--output=` flag when supplied.

## Round-trip invariant

For every supported format, the following MUST hold even when the
"translation" is an identity function (i.e. target == source):

```
parse(write(parse(source), identity)) == parse(source)
```

In plain prose: parse → translate-as-identity → write → parse-again must
yield the same internal structure. This is the integration-test contract for
each format adapter; a regression here is a Sev-1 bug. Test this in
`scripts/tests/` per format before shipping any adapter change.

## See also

- `protocols/placeholder-protect.md` — what protect-pass sees AFTER format
  parsing has stripped wrappers and decoded escapes.
- `checklists/i18n-format-checklist.md` — preflight that gates entry to this
  protocol.
- `references/audit-trail-spec.md` — where format-detection results, encoding
  conversions, and skipped (`fuzzy` / `translatable="false"`) entries are
  recorded.
- Spec §Sub-skill Responsibility Matrix (`docs/superpowers/specs/2026-05-06-translation-toolkit-design.md` line 435) — Layer 2 / Layer 5 are owned per-format by this skill.
