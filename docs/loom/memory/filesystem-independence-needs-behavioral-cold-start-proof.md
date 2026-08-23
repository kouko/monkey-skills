---
name: filesystem-independence-needs-behavioral-cold-start-proof
description: A plugin can pass filesystem-boundary checks while still requiring an absent sibling at runtime; standalone guarantees need cold-start tests that execute documented commands from a renamed isolated install and observe real success, rejection, and state effects
type: practice
origin: codex/loom-plugin-specialization close-out
---

A relative-link and private-path scan proves that one plugin does not reach
through another plugin's directory. It does not prove that the plugin can
actually perform its advertised work alone: prose can still mandate a sibling
skill, and documented commands can still assume the monorepo's checkout shape.

**Why:** This arc passed filesystem boundaries while ordinary design stations
still depended on checkout-shaped paths and sibling behavior. Only copied-root
execution and no-op mutations exposed the gap.

**How to apply:** For every standalone plugin claim, copy the plugin to an
arbitrarily named isolated root with siblings absent. Parse the commands and
contracts from the packaged documents, execute their real success and rejection
paths, assert observable receipts or state changes, and replace each required
tool with a no-op to prove the test cannot false-green.
