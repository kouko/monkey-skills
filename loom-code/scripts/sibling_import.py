"""Shared sibling-module loader for loom-code's scripts/ directory.

Five call sites hand-rolled the same `importlib.util.spec_from_file_location`
idiom to load a sibling script module without cwd or sys.path coupling.
`load_sibling` is the single source: resolve the file relative to
`anchor` (default: this helper's own directory -- pass `anchor=__file__`
to resolve relative to another file instead), register the loaded module
in `sys.modules` under a caller-chosen unique name, execute it once, and
return it. Sibling-module
import (no `__init__.py`, no conftest), following the existing `import
distribute` precedent in this same scripts/ directory.
"""
from __future__ import annotations

import importlib.util
import sys
from pathlib import Path


def load_sibling(filename: str, *, name: str | None = None, anchor: str = __file__):
    """Load `filename` from the same directory as `anchor` and return the
    executed module, registered in `sys.modules` under `name` (default:
    the file's stem). Raises ImportError when the module spec or its
    loader cannot be resolved -- callers wrap that into their own
    exception type."""
    if name is None:
        name = Path(filename).stem
    path = Path(anchor).with_name(filename)
    spec = importlib.util.spec_from_file_location(name, path) if path.exists() else None
    if spec is None or spec.loader is None:
        raise ImportError(f"cannot load {filename}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module
