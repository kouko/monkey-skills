# Protect-pass spec

> Canonical algorithm for masking placeholders before LLM translation and
> restoring them afterwards. Distributed to each translation skill's
> `references/` folder via `scripts/distribute.py`. Reference this file from
> SKILL prompts whenever the model is about to call a translate step.

## Why

LLMs left to themselves localise every token-like span — `{name}` becomes
`{名前}`, `%s` becomes `％ｓ`, `</a>` becomes `</リンク>`, code blocks get
"helpfully" reflowed. For i18n strings, code, URLs, and HTML this breaks the
downstream consumer. The protect-pass replaces every such span with an opaque
sentinel before the LLM ever sees the source, then restores the originals
after translation.

## Token format

`⟦P:NN⟧` where `NN` is a zero-padded two-digit counter (auto-widens past 99,
so the 100th token is `⟦P:100⟧`). The brackets are mathematical white square
brackets (U+27E6 / U+27E7) — LLMs are extremely unlikely to invent them, so
accidental token collisions are astronomically rare.

## What gets masked

In **priority order** — earlier patterns in this list win on overlap or
containment.

| Class | What                | Example pattern                                           |
|------:|---------------------|-----------------------------------------------------------|
| 1     | ICU plurals         | `{count, plural, one {1 item} other {# items}}`           |
| 2     | Curly braces        | `{name}`, `{0}`, `{{var}}`                                |
| 3     | printf-style        | `%s`, `%d`, `%1$s`, `%f`, `%x`                            |
| 4     | Fenced code blocks  | <code>```python\n…\n```</code>                            |
| 5     | Inline code         | `` `npm install` ``                                       |
| 6     | HTML tags           | `<a href="…">`, `</a>`, `<br/>`                           |
| 7     | URLs                | `https://example.com/x`                                   |
| 8     | Email addresses     | `user@example.com`                                        |
| 9     | File paths          | `/usr/…`, `C:\\…` — **DEFERRED to v0.2** (false-positive risk too high to regex safely; manual check until then) |

### Overlap / containment rules

- **ICU plurals beat generic curly braces.** The whole `{count, plural, …}`
  construct becomes ONE token; the inner `{1 item}` / `{# items}` arms are
  **not** separately tokenised.
- **Fenced code beats inline code.** Backticks inside a fenced block are part
  of the fence's span and don't get a second token.
- **HTML tags beat URLs.** A URL inside `href="…"` is owned by the surrounding
  HTML tag's span — there is no separate URL token for it.
- **In general:** if span A contains span B, A wins (B is dropped). If two
  spans tie at the same start offset, the higher-priority pattern wins.

### Known limitations (v0.1)

- **URLs with internal parentheses are truncated at the first `)`.** The URL
  pattern stops at `)` so it does not swallow the closer of a markdown link
  `[text](url)`. Consequence: a bare URL such as
  `https://en.wikipedia.org/wiki/Bracket_(mathematics)` is captured as
  `https://en.wikipedia.org/wiki/Bracket_(mathematics` (trailing `)` left in
  the surrounding prose). Round-trip text remains visually correct because
  the orphan `)` stays in the unmasked stream. Tradeoff accepted in v0.1;
  revisit if real corpora show > 1 % of URLs containing parens.
- **HTML attribute values containing `>` are not handled.**
  `<button title="a > b">` matches only up to the first `>` — i.e.
  `<button title="a >`. Rare in i18n strings; deferred.
- **File paths (P-class 9) are not protected.** Regexing path-like strings
  produces too many false positives for v0.1; manual review until v0.2.

## Restoration rule

Replace every `⟦P:NN⟧` in the translated text with the original substring from
`token_map`. Tokens absent from the translation are silently ignored at the
restore step (the count check below is what surfaces them). Tokens present in
the translation but absent from the map are left untouched so a reviewer can
spot LLM-invented placeholders.

## M1 verification (count parity)

After translation, **count `⟦P:NN⟧` tokens in the translated text** and
compare to `len(token_map)`. The two must be equal:

- Equal → no drops, no inventions → M1 passes.
- Unequal → either a placeholder was deleted or an extra one was hallucinated
  → M1 fails; reject the translation and retry.

This is a structural primitive only — it does not check that the *same*
tokens appear, just that the *count* matches. Stronger same-set verification
lives in higher gates.

## Examples

### 1. Curly + printf

```
SOURCE   : "Hello {user}, you have %d unread messages."
MASKED   : "Hello ⟦P:01⟧, you have ⟦P:02⟧ unread messages."
TOKEN MAP: { ⟦P:01⟧: "{user}", ⟦P:02⟧: "%d" }
LLM OUT  : "こんにちは ⟦P:01⟧、未読メッセージは ⟦P:02⟧ 件あります。"
RESTORED : "こんにちは {user}、未読メッセージは %d 件あります。"
```

### 2. ICU plural — one token, not three

```
SOURCE   : "{count, plural, one {1 item} other {# items}}"
MASKED   : "⟦P:01⟧"
TOKEN MAP: { ⟦P:01⟧: "{count, plural, one {1 item} other {# items}}" }
```

### 3. URL inside HTML — HTML wins

```
SOURCE   : 'Click <a href="https://example.com">here</a>'
MASKED   : 'Click ⟦P:01⟧here⟦P:02⟧'
TOKEN MAP: { ⟦P:01⟧: '<a href="https://example.com">', ⟦P:02⟧: '</a>' }
```

The `https://example.com` is **not** a separate token — it lives inside the
opening tag's span.

### 4. Fenced code block — single token

```
SOURCE   :
    Header
    ```python
    def foo():
        pass
    ```
    End

MASKED   :
    Header
    ⟦P:01⟧
    End

TOKEN MAP: { ⟦P:01⟧: "```python\ndef foo():\n    pass\n```" }
```
