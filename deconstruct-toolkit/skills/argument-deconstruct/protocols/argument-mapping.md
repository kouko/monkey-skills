# Protocol: Argument Mapping (Mermaid format)

Render the deconstructed argument as a mermaid `flowchart TD` diagram.
The map's value is showing **hidden warrants** that the prose buries.

## Format

```mermaid
flowchart TD
    Claim["**Main Claim**: <claim text>"]

    Sub1["Sub-claim 1: <text>"]
    Sub2["Sub-claim 2: <text>"]
    Claim --> Sub1
    Claim --> Sub2

    G1["Grounds: <evidence>"]
    Sub1 --> G1
    G1 -.warrant.-> W1["**Hidden warrant**: Because <generalization>"]

    G2["Grounds: <evidence>"]
    Sub2 --> G2
    G2 -.warrant.-> W2["**Hidden warrant**: Because <generalization>"]

    R1["⚠️ **Missing rebuttal**: <what the writer would have to address>"]
    Claim -.weakness.-> R1

    Q["⚠️ **No qualifier**: claim stated as universal"]
    Claim -.weakness.-> Q

    classDef claim fill:#dbeafe,stroke:#1e40af,stroke-width:2px
    classDef warrant fill:#fef3c7,stroke:#b45309,stroke-width:2px
    classDef weakness fill:#fee2e2,stroke:#b91c1c,stroke-width:2px
    classDef grounds fill:#dcfce7,stroke:#15803d,stroke-width:2px
    class Claim,Sub1,Sub2 claim
    class W1,W2 warrant
    class R1,Q weakness
    class G1,G2 grounds
```

## Conventions

| Element | Style |
|---|---|
| Claim / sub-claim | Solid arrow from parent claim, blue node |
| Grounds | Solid arrow from claim it supports, green node |
| Warrant | **Dotted** arrow from grounds with label "warrant", yellow node — emphasizes that warrant is *hidden* and *bridges*, not directly stated |
| Weakness (missing rebuttal / no qualifier / contestable warrant) | Dotted arrow with "weakness" label, red node |
| Backing | Solid arrow from warrant up to backing, plain node (only if backing is non-trivial) |

## Why mermaid (not ASCII or images)

- Renders inline in GitHub / GitLab / Obsidian / many markdown viewers
- Editable in plain text
- Versionable in git
- Diff-friendly (commits show structural changes, not pixel diffs)

## When to skip the map

- Single-claim argument with no sub-claims and no hidden warrants — the prose is the map
- Trivial argument (< 50 words) — overhead of mermaid block exceeds value
- Argument is so unstructured the map would be misleading (signal: the report should say "no clear argument structure" rather than draw a flowchart)

## Worked example

For the AI regulation op-ed:

```mermaid
flowchart TD
    Claim["**Main Claim**: Require AI literacy for committee members"]
    Sub1["Sub-claim: Congress is failing at tech regulation"]
    Sub2["Sub-claim: Age / illiteracy causes failure"]

    Claim --> Sub1
    Claim --> Sub2

    G1["Grounds: Examples of regulatory misses"]
    Sub1 --> G1
    G1 -.warrant.-> W1["**Hidden warrant**: Because regulatory failures are caused by knowledge gaps (not by structural / speed mismatches)"]

    G2["Grounds: Average age of Congress members"]
    Sub2 --> G2
    G2 -.warrant.-> W2["**Hidden warrant**: Because age correlates with technical illiteracy AND credentialism solves illiteracy"]

    R1["⚠️ **Missing rebuttal**: Experienced regulators have successfully regulated novel tech (FDA biotech)"]
    Claim -.weakness.-> R1

    Q["⚠️ **No qualifier**: 'all members' overreaches"]
    Claim -.weakness.-> Q

    classDef claim fill:#dbeafe,stroke:#1e40af,stroke-width:2px
    classDef warrant fill:#fef3c7,stroke:#b45309,stroke-width:2px
    classDef weakness fill:#fee2e2,stroke:#b91c1c,stroke-width:2px
    classDef grounds fill:#dcfce7,stroke:#15803d,stroke-width:2px
    class Claim,Sub1,Sub2 claim
    class W1,W2 warrant
    class R1,Q weakness
    class G1,G2 grounds
```

## Pitfalls

- **Drawing only claim → grounds**: this reproduces the surface
  argument. The whole point of the map is the warrant level.
- **Hiding weakness**: don't pretend missing rebuttals don't exist.
  Mark them in the map.
- **Over-detailed maps**: more than ~12 nodes becomes unreadable.
  If your argument has more, either split into sub-maps or simplify.
- **Inconsistent labeling**: keep labels short (one phrase). The map
  is a visual aid, not a transcript.
