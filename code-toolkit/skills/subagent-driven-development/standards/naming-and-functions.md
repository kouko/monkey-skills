<!--
FUNCTIONAL COPY — DO NOT EDIT IN PLACE
SSOT: domain-teams/skills/code-team/standards/naming-and-functions.md
Sync via: code-toolkit/scripts/distribute.py
-->

# Naming and Functions

Names and function shape determine whether the next reader understands
the code without running it. 命名與函數粒度是 code craft 的第一道 review
防線 — 壞名字與巨型函數會讓所有後續的 refactor、debugging、review 成本倍增。

## Primary Sources

- Martin, R.C. (2008) *Clean Code: A Handbook of Agile Software Craftsmanship*, Prentice Hall (Robert C. Martin Series). ISBN 978-0132350884. Chapters cited: Ch.2 Meaningful Names, Ch.3 Functions, Ch.4 Comments.
- Hunt, A. & Thomas, D. (2019) *The Pragmatic Programmer: Your Journey to Mastery, 20th Anniversary Edition*, Addison-Wesley. ISBN 978-0135957059. Ch.2 A Pragmatic Approach, Topic 9 "DRY — The Evils of Duplication"; Topic 10 "Orthogonality".
- Henney, K. (ed.) / 和田卓人 (監修) / 夏目大 (訳) (2010) 『プログラマが知るべき 97 のこと』, オライリー・ジャパン. ISBN 978-4-87311-479-8. 日本人追加エッセイ: まつもとゆきひろ「名前重要」(JP preamble anchor).

## Naming Rules

### Semantic meaning over brevity

**Clean Code Ch.2, "Use Intention-Revealing Names"**: a name should
answer *why it exists, what it does, and how it is used*. If a name
requires a comment to explain it, the name has not revealed its intent.

- Good: `elapsedTimeInDays`, `daysSinceCreation`, `fileAgeInDays`
- Bad: `d` (elapsed time? days?), `theList`, `data1`

**Clean Code Ch.2, "Avoid Disinformation"**: do not use names that
imply false things — `accountList` must actually be a List, not a
Set or Map; `hp` should not be a variable name in a non-medical domain
because it collides with the Unix platform name.

### One concept, one word

**Clean Code Ch.2, "Use One Word per Concept"**: pick one word for an
abstract concept and stick with it. Mixing `fetch`, `retrieve`, and
`get` for the same operation across a codebase is a 語彙 inconsistency
that fights the reader.

### Language idioms (house convention)

code-team adopts per-language idioms as house conventions where
Clean Code is silent:

- **Python**: `snake_case` for functions/variables, `PascalCase` for
  classes, `UPPER_SNAKE` for module-level constants (PEP 8).
- **TypeScript / JavaScript**: `camelCase` for functions/variables,
  `PascalCase` for classes and type aliases.
- **Go**: exported identifiers `PascalCase`, unexported `camelCase`
  (Go spec).

These idioms are load-bearing only when the host-language community
has a canonical style guide; when unclear, follow the existing file's
convention over introducing a new one (see DRY below).

## Function Shape

### Small functions

**Clean Code Ch.3, "Small!"**: *"The first rule of functions is that
they should be small. The second rule of functions is that they should
be smaller than that."* Martin's concrete heuristic in the same
section is that functions should rarely exceed 20 lines, and should
"hardly ever" be 100+.

code-team adopts a **soft target of 20 lines and a hard ceiling of
50 lines**, with the rationale documented in-comment when exceeded.
The 50-line ceiling is a house relaxation of Martin's aggressive 20 —
some host languages (e.g. SQL-heavy Go handlers, switch-exhaustive
Rust match arms) legitimately need more lines without decomposition.

### Do one thing

**Clean Code Ch.3, "Do One Thing"**: *"Functions should do one thing.
They should do it well. They should do it only."* A function does
"one thing" if you cannot extract another meaningful function with a
name that is not merely a restatement of the implementation.

### Step-down rule

**Clean Code Ch.3, "The Step-down Rule"**: code should read like a
top-down narrative — every function should be followed by those at
the next level of abstraction. This is the *Single Level of
Abstraction Per Function* rule: do not mix high-level policy with
low-level detail in the same body.

## Comments

### Comments are a last resort

**Clean Code Ch.4, opening**: *"The proper use of comments is to
compensate for our failure to express ourselves in code. Comments are
always failures."* Before writing a comment, try:

1. Rename for clarity
2. Extract a function whose name explains the intent
3. Replace magic numbers with named constants
4. Restructure the control flow

### When comments are justified

A comment taxonomy — **house convention inspired by Clean Code Ch.4
"Good Comments"**:

- **Docstring / API contract** — public interface of a module, class,
  or function, describing inputs / outputs / preconditions.
- **Intent / "why we chose this approach"** — the reason for a
  non-obvious implementation choice.
- **Warning of consequences** — "this is slow on N > 10^6"; "not
  thread-safe".
- **"Why NOT" reasons** — why the obvious alternative was rejected.
- **TODO with owner and issue link** — Clean Code Ch.4 permits TODO
  comments that track real follow-ups, not wishlist items.

### Stale comments are worse than no comments

**Clean Code Ch.4, "Bad Comments → Misleading Comments"**: an
out-of-date comment actively lies to the reader. When code changes,
comments must change with it; if that is impractical, delete the
comment.

## DRY and Naming

**Pragmatic Programmer Ch.2, Topic 9 "DRY — The Evils of Duplication"**:
*"Every piece of knowledge must have a single, unambiguous,
authoritative representation within a system."* Two functions with
almost-the-same name (`computeTotal` vs `calculateTotal`) usually
signal duplicated knowledge that should be unified — the naming
inconsistency is often the first visible symptom.

## Japanese Anchor (preamble)

まつもとゆきひろ (Matz, Ruby 作者) の「名前重要」エッセイ (97 のこと
日本語版 所収) は、命名がただのラベルではなく **設計の中核** である
ことを強調する。コードを書く時、適切な名前が思い浮かばなければそれは
概念そのものが曖昧な sign であり、名前をつける作業こそが設計である、
という立場。これは Clean Code Ch.2 の "Use Intention-Revealing Names"
と同じ命題を独立に日本語で定式化している。

## Anti-Patterns

- ❌ **Cryptic abbreviations**: `cstLst`, `usrMgr`, `tmpBuf`
- ❌ **Hungarian notation** in statically-typed languages (`strName`,
  `iCount`) — the type system already encodes the type
- ❌ **Noise words** that add no information: `ProductInfo` vs
  `ProductData` vs `Product` (Clean Code Ch.2 "Make Meaningful
  Distinctions")
- ❌ **Commented-out dead code** instead of deleting it (Clean Code
  Ch.4 "Commented-Out Code") — git history preserves it
- ❌ **Javadoc for every getter/setter** (Clean Code Ch.4 "Noise
  Comments") — doc comments on trivial accessors are noise
- ❌ **Functions longer than 50 lines** without documented rationale
- ❌ **Mixing levels of abstraction** in one function (high-level
  policy next to bit-twiddling)
