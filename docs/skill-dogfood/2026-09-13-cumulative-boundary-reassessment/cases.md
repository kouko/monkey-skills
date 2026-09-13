# Cumulative boundary reassessment corpus

Frozen before runtime-contract edits, 2026-09-13. These four fixtures are
small real Git repositories, rebuilt from the machine-readable specification
below. Baseline and candidate runners must receive the same repository HEAD,
feature request, model/effort profile, and output normalizer. Their only
permitted difference is the assigned Write Plan contract.

## Contract and runner identity

- Baseline revision: `1973ff35c4919e4c40795808240249c7ee40f506`.
- Baseline `loom-code/skills/write-plan/SKILL.md` SHA-256:
  `e4c249bae4a5badbd15c258fbfe6d4d2d920e9eba58329fa2ee05bfe573c0da4`.
- The candidate entrypoint and bundled-reference SHA-256 values must be added
  to the report before either candidate run. Both candidate resources must be
  byte-identical for every case.
- A candidate revision may differ from the baseline contract only in
  `loom-code/skills/write-plan/SKILL.md` and
  `loom-code/skills/write-plan/references/cumulative-boundary-reassessment.md`.
  Test and evidence files are not runner instructions.
- Each arm uses a fresh context. Runners may inspect only the assigned fixture,
  feature request, and contract resources. They report decisions, evidence,
  tasks, focused tests, reference-loaded yes/no, commands, elapsed time, and
  input/output token counts; they do not grade themselves.
- Normalization may remove operational identifiers and replace arm labels, but
  must preserve every decision, evidence anchor, task, test, limitation, cost,
  and reference-load statement. Raw model/tool streams remain private.

## Frozen blind rubric

<!-- BEGIN frozen-rubric -->
Two independent auditors receive neutralized outputs, fixture identities,
feature requests, and this rubric, but no arm mapping or contract text.

- **L1 accumulated responsibility divergence.** Correct candidate behavior
  identifies pricing and audit persistence/replay as distinct responsibilities,
  anchors a locality consequence in callers/state/tests/history, and orders
  characterization, behavior-preserving extraction, then the feature. Merely
  adding persistence inside `pricing.py` is incorrect. Admission additionally
  requires both auditors to find the baseline incorrect or insufficient and
  the candidate correct; a tie is not improvement.
- **L2 cohesive churn.** Correct behavior preserves the policy boundary and
  plans the new rule with focused policy tests. Splitting because of commit
  count, churn, length, or repeated edits is incorrect.
- **L3 shallow split.** Correct behavior rejects another physical split and
  either restores explicit state ownership/dependency direction or preserves
  files while doing the smallest equivalent correction. Treating filenames as
  proof of isolation is incorrect.
- **L4 noisy history.** Correct behavior filters rename, formatting, generated,
  and mass-update commits, then preserves the cohesive boundary. Using noise as
  extraction evidence is incorrect.
- No case may add a mandatory skill or a user boundary decision. History is
  bounded to 20 unique commits across the target set; Phase A reads metadata,
  and Phase B may read at most three target-only diffs.

Admission requires two agreeing auditors, L1 candidate improvement over the
baseline, correct candidate results for L2-L4, no new L2/L4 false positive,
an L3 correction without another shallow split, matched identities, measured
cost/reference loading, zero new mechanism classes, and completed minimal L1
and L2 implementations. The real runs must show that L1's extracted ownership
has a smaller or clearer dependency-complete feature surface while L2 remains
local without extraction. Missing evidence is failure, never a pending pass.
This corpus cannot establish universal model, repository, token, or time gains.
<!-- END frozen-rubric -->

## Rebuildable fixture specification

The probe hashes this JSON block verbatim, creates deterministic SHA-1 Git
repositories, verifies every commit, and runs each HEAD's unit tests. Expected
HEAD and tree identities are deliberately filled only after observing the
fixture test fail against the initial placeholders.

```json fixture-spec
{
  "schema": 1,
  "git": {
    "author_email": "fixture@example.invalid",
    "author_name": "Loom Fixture",
    "branch": "main",
    "object_format": "sha1",
    "start_time": "2001-01-01T00:00:00+0000"
  },
  "cases": {
    "L1": {
      "feature_request": "Persist audit events as JSONL and add replay without making pricing callers or pricing tests understand storage.",
      "expected_head": "45a097b6180c90a8dc68d2f057b03d8d4ae7687a",
      "expected_tree": "74e9c6734d9ebfd6f2a1920b99f461be253445bc",
      "commits": [
        {
          "message": "add local pricing policy",
          "changes": {
            "checkout.py": "from pricing import quote\n\ndef checkout(cents):\n    return quote(cents)\n",
            "pricing.py": "def quote(cents):\n    return cents\n",
            "tests/test_pricing.py": "import unittest\nfrom pricing import quote\n\nclass PricingTest(unittest.TestCase):\n    def test_quote(self):\n        self.assertEqual(quote(100), 100)\n\nif __name__ == '__main__':\n    unittest.main()\n"
          }
        },
        {
          "message": "add member discount",
          "changes": {
            "checkout.py": "from pricing import quote\n\ndef checkout(cents, member=False):\n    return quote(cents, member=member)\n",
            "pricing.py": "def quote(cents, member=False):\n    return cents * 9 // 10 if member else cents\n",
            "tests/test_pricing.py": "import unittest\nfrom pricing import quote\n\nclass PricingTest(unittest.TestCase):\n    def test_quote(self):\n        self.assertEqual(quote(100), 100)\n        self.assertEqual(quote(100, member=True), 90)\n\nif __name__ == '__main__':\n    unittest.main()\n"
          }
        },
        {
          "message": "record quote audit events",
          "changes": {
            "checkout.py": "from pricing import quote\n\ndef checkout(cents, audit_events, member=False):\n    return quote(cents, audit_events, member=member)\n",
            "pricing.py": "def quote(cents, audit_events, member=False):\n    total = cents * 9 // 10 if member else cents\n    audit_events.append({'kind': 'quote', 'total': total})\n    return total\n",
            "tests/test_pricing.py": "import unittest\nfrom pricing import quote\n\nclass PricingTest(unittest.TestCase):\n    def test_quote_also_needs_audit_setup(self):\n        events = []\n        self.assertEqual(quote(100, events, member=True), 90)\n        self.assertEqual(events, [{'kind': 'quote', 'total': 90}])\n\nif __name__ == '__main__':\n    unittest.main()\n"
          }
        }
      ]
    },
    "L2": {
      "feature_request": "Add a capped weekend multiplier to the same shipping-price policy.",
      "expected_head": "397c8269299ab56144ef7a1445188f497beb078f",
      "expected_tree": "b723cb3b390d179d32274d4922d78005c9119a2d",
      "commits": [
        {
          "message": "add shipping policy",
          "changes": {
            "shipping.py": "def price(weight):\n    return weight * 2\n",
            "tests/test_shipping.py": "import unittest\nfrom shipping import price\n\nclass ShippingTest(unittest.TestCase):\n    def test_price(self):\n        self.assertEqual(price(3), 6)\n\nif __name__ == '__main__':\n    unittest.main()\n"
          }
        },
        {
          "message": "add minimum shipping price",
          "changes": {
            "shipping.py": "def price(weight):\n    return max(5, weight * 2)\n",
            "tests/test_shipping.py": "import unittest\nfrom shipping import price\n\nclass ShippingTest(unittest.TestCase):\n    def test_price(self):\n        self.assertEqual(price(1), 5)\n        self.assertEqual(price(3), 6)\n\nif __name__ == '__main__':\n    unittest.main()\n"
          }
        },
        {
          "message": "add zone surcharge",
          "changes": {
            "shipping.py": "def price(weight, zone='local'):\n    total = max(5, weight * 2)\n    return total + (3 if zone == 'remote' else 0)\n",
            "tests/test_shipping.py": "import unittest\nfrom shipping import price\n\nclass ShippingTest(unittest.TestCase):\n    def test_price(self):\n        self.assertEqual(price(1), 5)\n        self.assertEqual(price(3, zone='remote'), 9)\n\nif __name__ == '__main__':\n    unittest.main()\n"
          }
        },
        {
          "message": "cap heavy parcel price",
          "changes": {
            "shipping.py": "def price(weight, zone='local'):\n    total = min(40, max(5, weight * 2))\n    return total + (3 if zone == 'remote' else 0)\n",
            "tests/test_shipping.py": "import unittest\nfrom shipping import price\n\nclass ShippingTest(unittest.TestCase):\n    def test_price(self):\n        self.assertEqual(price(1), 5)\n        self.assertEqual(price(30), 40)\n        self.assertEqual(price(3, zone='remote'), 9)\n\nif __name__ == '__main__':\n    unittest.main()\n"
          }
        }
      ]
    },
    "L3": {
      "feature_request": "Add an SMS delivery channel while making delivery attempts independently testable.",
      "expected_head": "d3c9f45e8d85b162f8485f0dde7937bbc1bfe943",
      "expected_tree": "bbc3cff17e12cd61a7460f9cb88d75038d573604",
      "commits": [
        {
          "message": "add notification workflow",
          "changes": {
            "notify.py": "STATE = {'attempts': 0}\n\ndef send(message):\n    STATE['attempts'] += 1\n    return 'email:' + message\n\ndef attempts():\n    return STATE['attempts']\n",
            "tests/test_notify.py": "import unittest\nimport notify\n\nclass NotifyTest(unittest.TestCase):\n    def test_send(self):\n        notify.STATE['attempts'] = 0\n        self.assertEqual(notify.send('hi'), 'email:hi')\n        self.assertEqual(notify.attempts(), 1)\n\nif __name__ == '__main__':\n    unittest.main()\n"
          }
        },
        {
          "message": "split sender and tracker files",
          "changes": {
            "notify.py": null,
            "sender.py": "import tracker\n\ndef send(message):\n    tracker.STATE['attempts'] += 1\n    return 'email:' + message\n",
            "tracker.py": "STATE = {'attempts': 0}\n\ndef attempts():\n    from sender import send\n    del send\n    return STATE['attempts']\n",
            "tests/test_notify.py": null,
            "tests/test_sender.py": "import unittest\nimport sender\nimport tracker\n\nclass SenderTest(unittest.TestCase):\n    def test_send(self):\n        tracker.STATE['attempts'] = 0\n        self.assertEqual(sender.send('hi'), 'email:hi')\n        self.assertEqual(tracker.attempts(), 1)\n\nif __name__ == '__main__':\n    unittest.main()\n"
          }
        },
        {
          "message": "change sender and tracker together",
          "changes": {
            "sender.py": "import tracker\n\ndef send(message, channel='email'):\n    tracker.STATE['attempts'] += 1\n    return channel + ':' + message\n",
            "tracker.py": "STATE = {'attempts': 0}\nLAST_CHANNEL = None\n\ndef attempts():\n    from sender import send\n    del send\n    return STATE['attempts']\n",
            "tests/test_sender.py": "import unittest\nimport sender\nimport tracker\n\nclass SenderTest(unittest.TestCase):\n    def test_send(self):\n        tracker.STATE['attempts'] = 0\n        self.assertEqual(sender.send('hi', channel='push'), 'push:hi')\n        self.assertEqual(tracker.attempts(), 1)\n\nif __name__ == '__main__':\n    unittest.main()\n"
          }
        }
      ]
    },
    "L4": {
      "feature_request": "Add a deterministic tie-break rule to the same ranking policy.",
      "expected_head": "3ec35ed5137e550b45690f7d454f88796e8be3e0",
      "expected_tree": "3b4a97db3a058ee1d7f2fe3e6c4db23c88dfebdf",
      "commits": [
        {
          "message": "add ranking policy",
          "changes": {
            "rank.py": "def rank(items):\n    return sorted(items, key=lambda item: item['score'], reverse=True)\n",
            "tests/test_rank.py": "import unittest\nfrom rank import rank\n\nclass RankTest(unittest.TestCase):\n    def test_rank(self):\n        self.assertEqual([x['score'] for x in rank([{'score': 1}, {'score': 2}])], [2, 1])\n\nif __name__ == '__main__':\n    unittest.main()\n"
          }
        },
        {
          "message": "rename ranking module",
          "changes": {
            "rank.py": null,
            "ranking.py": "def rank(items):\n    return sorted(items, key=lambda item: item['score'], reverse=True)\n",
            "tests/test_rank.py": "import unittest\nfrom ranking import rank\n\nclass RankTest(unittest.TestCase):\n    def test_rank(self):\n        self.assertEqual([x['score'] for x in rank([{'score': 1}, {'score': 2}])], [2, 1])\n\nif __name__ == '__main__':\n    unittest.main()\n"
          }
        },
        {
          "message": "format all policy files",
          "changes": {
            "ranking.py": "def rank(items):\n    return sorted(\n        items,\n        key=lambda item: item['score'],\n        reverse=True,\n    )\n",
            "tests/test_rank.py": "import unittest\n\nfrom ranking import rank\n\n\nclass RankTest(unittest.TestCase):\n    def test_rank(self):\n        values = [{'score': 1}, {'score': 2}]\n        self.assertEqual([x['score'] for x in rank(values)], [2, 1])\n\n\nif __name__ == '__main__':\n    unittest.main()\n"
          }
        },
        {
          "message": "regenerate repository headers",
          "changes": {
            "GENERATED.txt": "generated header revision 2\n",
            "ranking.py": "# generated-header: v2\n\ndef rank(items):\n    return sorted(\n        items,\n        key=lambda item: item['score'],\n        reverse=True,\n    )\n",
            "tests/test_rank.py": "# generated-header: v2\nimport unittest\n\nfrom ranking import rank\n\n\nclass RankTest(unittest.TestCase):\n    def test_rank(self):\n        values = [{'score': 1}, {'score': 2}]\n        self.assertEqual([x['score'] for x in rank(values)], [2, 1])\n\n\nif __name__ == '__main__':\n    unittest.main()\n"
          }
        }
      ]
    }
  }
}
```
