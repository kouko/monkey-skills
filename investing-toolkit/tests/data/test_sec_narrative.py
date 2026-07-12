"""test_sec_narrative.py — US SEC narrative extractor (edgartools migration).

Offline unit tests for the narrative acquisition / segmentation path.

edgartools (~100MB, pyarrow) is deliberately NOT installed in offline CI, so
`edgar` is injected as a `sys.modules` mock BEFORE importing sec_edgar_client —
the module's lazy `import edgar` then resolves to that stub. This is the
established pattern for every offline test in this file (later migration tasks
mock the real edgartools object shape captured by the @pytest.mark.network
live anchors in test_data_markets_live.py).

Run offline (exact CI command — no extra --with):
  uv run --quiet --with pytest --with 'pyyaml>=6.0' \
    pytest investing-toolkit/tests/ -m "not network" -q --tb=short

External-surface grounding: edgartools 5.42.0 —
  edgar.set_identity("<name> <email>") / env EDGAR_IDENTITY. The library does
  NOT fail-fast on an unset identity (get_identity() prompts interactively, then
  raises TimeoutError after ~60s), so this module's pre-send guard
  (_ensure_edgar_identity) is the load-bearing enforcer of SEC fair-access
  identity. Source: primary-source research (PyPI edgartools JSON + GitHub
  dgunning/edgartools source), captured 2026-07-12; see plan Notes
  §edgartools grounding in docs/loom/plans/2026-07-12-us-sec-narrative.md.
"""
from __future__ import annotations

import importlib
import sys
from pathlib import Path
from unittest import mock

import pytest

ROOT = Path(__file__).resolve().parents[2]
MARKETS_SCRIPTS = ROOT / "skills" / "data-markets" / "scripts"


@pytest.fixture
def sec_client():
    """Import sec_edgar_client with `edgar` stubbed in sys.modules.

    Offline CI has no edgartools; the stub persists in sys.modules so the
    module's lazy `import edgar` resolves to it. The fixture restores the
    prior sys.modules state on teardown so tests stay isolated.
    """
    if str(MARKETS_SCRIPTS) not in sys.path:
        sys.path.insert(0, str(MARKETS_SCRIPTS))
    edgar_stub = mock.MagicMock(name="edgar")
    saved_edgar = sys.modules.get("edgar")
    saved_client = sys.modules.get("sec_edgar_client")
    sys.modules["edgar"] = edgar_stub
    sys.modules.pop("sec_edgar_client", None)
    module = importlib.import_module("sec_edgar_client")
    module.edgar_stub = edgar_stub
    try:
        yield module
    finally:
        if saved_edgar is not None:
            sys.modules["edgar"] = saved_edgar
        else:
            sys.modules.pop("edgar", None)
        if saved_client is not None:
            sys.modules["sec_edgar_client"] = saved_client
        else:
            sys.modules.pop("sec_edgar_client", None)


def test_acquire_rejects_when_identity_unset(sec_client, monkeypatch):
    # No @req tag: this dispatch's plan/spec traces by
    # `<change-id> / Requirement / Scenario` join keys, not registered REQ-ids,
    # so per the implementer contract @req is omitted (see report).
    # Scenario: `SEC EDGAR fair-access compliance / Missing User-Agent is
    # rejected before send`.
    monkeypatch.setattr(sec_client, "USER_AGENT", "")

    def _boom(*args, **kwargs):
        raise AssertionError(
            "network boundary (_sec_get) must NOT be hit when SEC identity is unset"
        )

    monkeypatch.setattr(sec_client, "_sec_get", _boom)

    result = sec_client.action_narrative("0001045810-24-000316")

    assert isinstance(result, dict)
    assert "error" in result, f"expected a loud error slot, got: {result!r}"
