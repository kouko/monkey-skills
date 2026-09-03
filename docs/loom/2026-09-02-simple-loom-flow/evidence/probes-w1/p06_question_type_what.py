#!/usr/bin/env python3
"""P06 — a questions[] entry typed `what` whose text is plainly a
spec-quality / implementation question ("should the parser be recursive?").

check_questions() validates decision_point, non-empty text, and membership
in {what, behaviour, done, consequence}. Nothing checks that the text is a
question the USER can answer, which is what the decision points are for.

TARGET RULE: none — question-type/content validation is prose-only.
EXPECTED: escaped-by-design (this is a record, not a gate; the fixture
commit and dispatch entry are otherwise clean so this is the actual gap,
not a masking artifact).
Attack class: forge an artifact the gate trusts.
exit 0 always (record, not gate).
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from fixture import (adversarial_probes, expected_escape, git, new_repo,
                     push_case, review_doc, write)

repo = new_repo("p06")
write(repo, "src/parser.py", "def parse(s):\n    return s\n")
git(repo, "add", "-A")
git(repo, "commit", "-qm", "feat: parser\n\nTask: W1-01")
sha = git(repo, "rev-parse", "HEAD")

review = review_doc(sha)
review["probes"] += adversarial_probes(sha)
review["questions"] = [
    {"decision_point": 1, "text": "should the parser be recursive?", "type": "what"},
    {"decision_point": 2, "text": "shall I use a dict or a dataclass here?", "type": "behaviour"},
    {"decision_point": 3, "text": "which pytest fixture should hold the tmp path?", "type": "done"},
]
proc = push_case(repo, review)

sys.exit(expected_escape(
    "three implementation questions recorded as user decision-point questions "
    "and push does not block on them (content of a `what`/`behaviour`/`done` "
    f"question is prose-only, concept-model §0); rc={proc.returncode} "
    f"stderr={proc.stderr.strip()[:300]!r}",
))
