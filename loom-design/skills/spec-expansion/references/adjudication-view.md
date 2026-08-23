# Adjudication view — local display contract

> Companion to [`../SKILL.md`](../SKILL.md). This contract governs how
> spec-expansion presents its English machine-precision layers for human
> judgment in a Traditional Chinese or Japanese conversation. It is a local
> packaged contract: using spec-expansion never requires another plugin's
> files to exist.

## Artifact boundary

The English requirement and GIVEN / WHEN / THEN source remains unchanged.
The view is disposable and regenerated from that source; it never becomes
the input to another rendition. Preserve every source unit one-to-one,
carry technical nouns, identifiers, enum tokens, numbers, paths, and RFC-2119
modal force through unchanged, and mark any translator-added explanation
with 「譯注」. An omission must be visible as 「已略」 rather than silently
dropped.

## Supported language duties

The view fires only for the supported conversation-language profiles
`zh-Hant` and `ja`. An English session reads the source directly. Any other
non-English language is N/A-loud: report that no profile exists and do not
pretend to provide a validated rendition.

When a renderer or lint command accepts a language profile, the executor
MUST pass `--lang zh-Hant` or `--lang ja` explicitly. Never rely on a default:
using the wrong profile can reject a faithful rendition or conceal a changed
obligation.

### zh-Hant

Preserve modal force with this closed mapping: must→必須, should→應, may→可,
must not→不得, should not→不應. Negation preservation is a **hard-fail** duty;
a missing Chinese negation marker blocks the view.

### ja

Preserve modal force with these accepted suffixes: must→なければならない;
must not→てはならない; should→ことが望ましい / のがよい / ことを推奨する;
should not→望ましくない / ない方がよい; may→てもよい / てよい /
差し支えない. These are verb-independent suffixes and must be attached to
the translated predicate. Japanese negation preservation is a **warning**
duty because inflectional negation collides with ordinary vocabulary; relay
the warning for human judgment but do not turn it into a hard failure.

## Failure behavior

If unit count, anchors, modal force, or the profile-specific negation duty
fails validation, do not publish the view as trustworthy. Report the source
unit and the failed duty, correct the rendition, and validate it again. The
machine-precision English artifact remains authoritative throughout.
