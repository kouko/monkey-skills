# Blind-run report — the template

The blind run produces `docs/loom/<change-id>/blind-run-report.md`. This is
the document the user reads at decision point ③ to say "yes, that is what I
wanted". They never read the diff, so anything not in here is invisible to
them.

Write it in the user's own language and in their words: what they asked
for, what happened when it was tried, what it cost them. No file paths, no
function names, no loom vocabulary. Every section below is required; a
section with nothing to say says so in one line rather than disappearing.

---

```markdown
# <change title> — what I tried and what happened

Tried on <date>, in a clean copy of the project at <short sha>.

## What you asked for, one line at a time

### 1. <the intent's first Acceptance line, verbatim>
- **How I tried it**: <the commands typed or the buttons pressed, in plain words>
- **What happened**: <what came back>
- **Evidence**: <screenshot / output file / test name>
- **Verdict**: works / partly / not yet — <one line>

### 2. <the second Acceptance line>
…

<For a product change, one further block per UI flow in the spec, in the
same shape: what I did, what appeared, evidence.>

## 對你既有的資料做了什麼 (what this did to data you already had)

<One paragraph, always present. If the change reads and writes nothing the
user already owned, the line is: "Nothing — it only touched files this
change created." If it did touch existing data, say exactly what changed,
whether the old form can still be read, and where the backup is.>

## I decided for you

<Every fork the agent resolved without asking, and every finding of
severity important or worse that a reviewer dismissed. One bullet each:>

- **<the choice>** — I picked <option> because <reason>. Changing it later
  means <cost>.
- **<the dismissed finding>** — <reviewer> raised <finding>; dismissed
  because <reason>. If that reason is wrong, this is where it shows.

<If there were none: "Nothing — every choice was either yours or forced.">

## Things I am not sure you want

<Open questions, in the user's terms, each answerable with a sentence. If
none: "Nothing.">
```

---

## What makes a report unusable

- An Acceptance line reported as "works" with no evidence anyone can look
  at. Evidence is a screenshot, a captured output, or a named test — not
  the runner's word.
- The data paragraph missing. It is fixed because the blind run happens in
  a clean environment and structurally cannot hit the user's real data:
  that harm is only ever caught by saying out loud what would happen.
- Decisions folded into prose instead of listed. If the user has to hunt
  for what was decided for them, it was not disclosed.
