"""RED test — verifies the deep_research package is importable and versioned."""


def test_imports():
    import deep_research  # noqa: PLC0415

    assert deep_research.__version__, "__version__ must be a non-empty string"
