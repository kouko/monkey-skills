# Data-Over-Abstractions Mindset

A philosophical anchor for design-time decisions: prefer generic data
structures and a small set of generic operations over specialized
custom types with their own bound methods. The mindset is a
counterweight to the reflex of "every concept deserves its own class".

## Primary Sources

- **Perlis, A. (1982) "Epigrams on Programming"**, *ACM SIGPLAN Notices* Vol.17 No.9. Published epigram #9: *"It is better to have 100 functions operate on one data structure than 10 functions on 10 data structures."* This is the canonical source of the quote; though widely associated with Lisp culture, the attribution is to Alan Perlis, not Rich Hickey.
- **Hickey, R. (2012) "The Value of Values"**, JaxConf / InfoQ talk. https://www.infoq.com/presentations/Value-Values/ — develops the data-vs-objects distinction and argues that immutable values, not stateful objects, are the better unit of program composition.
- **Fabian, R. (2018) *Data-Oriented Design*** (self-published). https://www.dataorienteddesign.com/dodbook/ — book-length treatment of organizing programs around data layouts rather than object hierarchies; originated in game-engine performance work but the design lessons generalize.
- **Acton, M. (2014) "Data-Oriented Design and C++"**, CppCon 2014. https://www.youtube.com/watch?v=rX0ItVEVjHc — practitioner talk applying DOD to performance-critical C++; useful for the diagnostic question "what shape is the data, really?"

## The Core Insight

**Perlis Epigram #9**:

> *"It is better to have 100 functions operate on one data structure
> than 10 functions on 10 data structures."*

Generic operations on generic data compose. Specialized operations on
specialized structures do not. A `Map<String, Value>` can be processed
by every map-handling function ever written; a `SettingsManager`
class can only be processed by methods you yourself wrote for it.

## Why Custom Abstractions Carry Hidden Cost

Every custom type, wrapper class, or specialized structure adds:

- **A concept to learn** — readers must understand what it is *before*
  they can read code that uses it
- **Its own operation surface** — every transformation needs a method
  on the class, or a free function the class exports
- **A composition wall** — code that wants to interact with two
  different custom types needs adapters, not just function composition
- **A maintenance attractor** — bug fixes, edge cases, and feature
  flags accumulate inside the type, not at the call site

A well-named map plus three pure functions is often better than a
class with five methods and a constructor.

## Information Over Behavior

Hickey's *Value of Values* reframes the design question:

- What **information** does this domain carry?
- What are the **essential relationships** between the pieces?
- What **transformations** does the program need to do?

Then represent the information with generic structures (maps, vectors,
sets, records) and let behavior live in functions that consume and
produce those structures. Custom types are reserved for the cases
where the behavior genuinely cannot be a free function — not for every
"this feels like its own thing" reflex.

## Practical Application

Before introducing a new class, type, or wrapper, ask:

1. **Could this be a map / dict with documented keys?** If yes, default
   to that — every map-handling function in the language and every
   third-party library will work on it.
2. **Could this be a tuple / record / NamedTuple?** Lightweight, no
   methods, structural rather than nominal — usually enough.
3. **Do I genuinely need bound behavior?** Methods only earn their
   weight when (a) they enforce an invariant the data structure can't,
   (b) the language insists on dispatch via methods (e.g. interface
   conformance in Go), or (c) operator overloading is the natural API
   (numeric types, geometric primitives).

If none of (a)/(b)/(c) holds, prefer functions over methods.

## When This Mindset Doesn't Apply

- **Strongly-typed boundaries** — at API edges (HTTP request bodies,
  message-queue payloads, database row mappers), nominal types are
  worth the ceremony for safety. The mindset applies to internal
  composition, not boundary contracts.
- **Algebraic data types in ML-family languages** — Rust enums,
  Haskell sum types, OCaml variants are *also* data, just statically
  tagged. Using them is consistent with this mindset, not opposed to it.
- **Domain primitives that prevent bugs** — wrapping a `string` in a
  `UserId` newtype to prevent confusion with `OrderId` is not what
  this mindset argues against; it argues against `UserManager`,
  `UserService`, `UserRepository` as the default decomposition.

## Cross-References

- `pragmatic-principles.md` — DRY (knowledge, not lines), Orthogonality,
  Rule of Three (don't abstract before you have three concrete examples
  — this mindset answers "and even when you have three, prefer data")
- `solid-principles.md` — SRP, ISP — generic data + free functions
  often satisfies SRP/ISP more cleanly than class hierarchies do
- `refactoring-standard.md` — Bad Smells "Large Class" / "Feature Envy"
  are symptoms this mindset prevents at design time

## Anti-Patterns

- ❌ **Class-first decomposition** — naming a class for every noun in
  the requirements doc before asking whether the noun needs methods
- ❌ **Hexagonal ports for plain data shuttling** — defining a
  `XxxPort` interface, an `XxxAdapter`, and a `XxxDto` to move a map
  from A to B
- ❌ **Manager / Service / Helper soup** — three classes whose
  combined behavior is "transform this dict into that dict"
- ❌ **Inheritance hierarchies for data variants** — when a tagged
  union (sum type) or a discriminator key on a map would do
- ❌ **Custom collection wrappers** — `UserCollection extends List<User>`
  with three convenience methods that could be free functions
