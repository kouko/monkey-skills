---
name: a-recorded-word-count-must-be-python-split-never-wc
description: Any word count a gate recomputes across macOS and CI must be Python `len(str.split())` — BSD and GNU `wc -w` disagree in every locale (3 words apart under UTF-8; under LC_ALL=C GNU drops every all-non-ASCII word, 147 here), so "pin LC_ALL=C" made the mismatch worse, and `LC_ALL=C bash … | wc -w` pins bash, not wc
type: gotcha
origin: simple-loom-flow (2026-09-03) — CI-1 and CI-2 on PR #780; `check_mechanisms.py --measure` baseline 923fb84a = 5278 by str.split, 5281 by BSD wc, 5131 by GNU wc in C
---

`check_mechanisms.py --measure` recomputes the session-start baseline from
the recorded sha and fails closed when the number differs. The counter was
`wc -w`. It matched on the Mac, missed by three on the runner (GNU wc,
UTF-8), and after "fixing" that by pinning `LC_ALL=C` missed by 147: in
the C locale GNU wc counts only tokens containing a printable ASCII byte,
so every purely-CJK token vanishes; BSD wc counts them. The diagnosis was
confirmed before the second fix by emulating GNU's rule in Python over the
same bytes and reproducing CI's 5131.

Rule: record the method as
`… | python3 -c 'import sys;print(len(sys.stdin.read().split()))'` and
count the same way in code; never `wc`. When a CI number disagrees with a
local one, reproduce the *other* platform's rule locally first — the
first "fix" here was applied on a guess and cost a full review round.
