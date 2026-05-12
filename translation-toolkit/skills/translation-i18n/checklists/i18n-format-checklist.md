# i18n format checklist — 8-item preflight

> Run before Layer 2 parse + before Layer 5 write. Any unchecked item halts
> the run with a clear actionable message; do not silently degrade.
>
> All eight items combined are cheap (file stat + extension match + a single
> regex pass over a short header). The point is fail-fast on
> mis-shaped input — Layer 2 parsing on a mis-named file produces opaque
> errors deep in the pipeline that are far harder to diagnose.

## The 8 items

- [ ] **1. File readable.** Source path exists, has read permission, is non-
      empty (zero-byte source = nothing to translate; surface as a hard
      error, not silently produce an empty translation). For inline-string
      input (no path), this item is N/A.

- [ ] **2. Format detected (extension matches content).** Per
      `protocols/format-roundtrip.md` §Detection — auto-detect by extension,
      then verify against content sniff. Fail if `.po` file is actually JSON
      or vice versa (mis-naming is a real failure mode in CI environments
      where output paths are templated). The mismatch message MUST tell the
      user what extension they have vs what content sniffing detected.

- [ ] **3. Placeholder count > 0 → masked via protect-pass.** Run a quick
      pre-scan over each entry's source string; if any entry contains a
      placeholder pattern (`{var}` / `%s` / `%1$@` / `<a …>` / ICU plural /
      etc.) but the protect-pass run produces zero `⟦P:NN⟧` tokens, the
      protect-pass logic has a bug or the placeholder pattern is novel.
      Halt with a diagnostic showing the unmasked entry. (Entries with no
      placeholders pass this item trivially — the gate triggers only on
      "placeholder visible AND token count == 0".)

- [ ] **4. Source not empty.** For each translation unit, the source string
      is non-empty after format parsing (i.e. after stripping XML wrappers
      / decoding `.strings` escapes / resolving `msgid_plural` arms).
      Empty-source entries are usually a mistake in the source file (PO
      entries with `msgid ""` that aren't the header, JSON keys mapped to
      `""`, XLIFF segments with no `<source>` text). Surface as a WARN per
      entry and skip those entries; do NOT translate `""` → some hallucinated
      target.

- [ ] **5. Target locale BCP-47 valid.** The `target_locale` from the
      intake-spec parses as a valid BCP-47 tag (`ja-JP`, `zh-TW`, `zh-CN`,
      `en-US`). Hyphen-form is canonical. Note that XLIFF `srcLang` /
      `trgLang` attributes commonly use underscore form (`ja_JP`); the Layer
      2 parser normalises these to hyphen for matching, but the intake-spec
      itself MUST use hyphen. v0.1 supports the four-locale matrix (en-US ↔
      ja-JP ↔ zh-TW ↔ zh-CN); other targets surface a `glossary coverage:
      degraded` warning per the router's "When NOT to use" rule, not a halt.

- [ ] **6. Glossary path resolvable or skipped.** If the caller supplied
      `glossary_path`, the file MUST exist and be readable. If they did
      NOT supply one, the resolver checks
      `<repo>/docs/i18n/glossary-{target_locale}.md` and falls through to L2
      bundled (`glossary/glossary-{source}--{target}.md`) silently when the
      L1 path is missing. **Halt only when the caller explicitly named a
      glossary path that does not exist** — that's a typo the user wants
      fast feedback on.

- [ ] **7. At least one tier matches at least one term.** After Layer 2
      glossary resolve completes, count the resolution hits across all
      tiers. If **every** candidate term in the source falls all the way
      through L1 → L2 → L3 → L4 with zero hits anywhere, log a `WARN:
      glossary-coverage-zero` in the audit-trail. This typically means
      either (a) the source has no domain-specific terminology — fine, the
      WARN is just informational — or (b) the wrong glossary file was loaded
      (e.g. `glossary-ja-JP.md` when `target_locale=zh-TW`). The skill does
      NOT halt on this — it proceeds with L4-only resolution — but the WARN
      is loud enough that the caller should investigate before shipping.

- [ ] **8. File is writable for output.** The target path's parent directory
      exists and is writable. If the parent doesn't exist, attempt to
      create it (Android-convention `values-<target>/` and iOS-convention
      `<target>.lproj/` directories often need to be created). If creation
      fails (permission denied / read-only filesystem), halt before any
      Layer 3 LLM calls — the user will lose those calls' cost if Layer 5
      fails to write. This is the cheap "permission probe" — do `os.access`
      / `Path.touch` before paying the LLM.

## When to run

| Step | Items |
|---|---|
| Before Layer 2 parse | 1, 2, 5, 6, 8 |
| After Layer 2 parse, before Layer 3 | 3, 4 |
| After Layer 2 glossary resolve | 7 |

Items 3 / 4 / 7 require the format to be parsed and the glossary resolver to
have run; the rest are pre-parse cheap checks.

## What this checklist does NOT cover

- **M1 / M2 verification** — that's Layer 4 (`references/verification-gates.md`).
  The preflight is structural; gates are post-translation.
- **Project glossary tier mismatch** (e.g. domain-mismatch). That's M2's
  responsibility.
- **Translation quality** — that's the 4D reflection axes
  (`references/4d-reflection.md`).

## See also

- `protocols/format-roundtrip.md` — owners of items 1, 2, 4, 5, 8
- `protocols/placeholder-protect.md` — owner of item 3
- `references/orthogonal-axes.md` — defines the 4-tier glossary resolver
  consulted by items 6 and 7
- `references/audit-trail-spec.md` — where checklist results are recorded
  on a halt or WARN
