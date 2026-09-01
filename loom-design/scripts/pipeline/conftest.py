"""Put this station directory on sys.path for bare sibling imports.

`--import-mode=importlib` (see ../pytest.ini) no longer inserts a test
file's own directory, so `import heading_window` and friends would fail.
This restores exactly that one entry -- no fixtures, no hooks.
"""
import sys
from pathlib import Path

_HERE = str(Path(__file__).resolve().parent)
if _HERE not in sys.path:
    sys.path.insert(0, _HERE)
