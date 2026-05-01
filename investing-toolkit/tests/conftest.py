"""conftest.py — root-level shared marker registration for investing-toolkit tests.

Registers the `network` marker so live-API tests can be selected/skipped at the
root `tests/` collection level (the per-subdir conftests under tests/data/ etc.
register the same marker for sub-directory collection scopes; both are required
because pytest only auto-discovers conftests on the path from rootdir to the
collected file).

    pytest -m network        # opt-in: run live API calls
    pytest -m "not network"  # offline-safe (CI default)

The cross-cutting test files at this level (test_skill_structure.py,
test_plugin_metadata.py, test_sync_clients.py, test_path_conventions.py,
test_pipeline_integration.py) use this marker for end-to-end pipeline tests
that require real data fetches.
"""
from __future__ import annotations


def pytest_configure(config):
    config.addinivalue_line(
        "markers",
        "network: requires external API calls (skip in offline CI)",
    )
