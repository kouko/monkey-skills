"""Horizontal bar chart generator with CJK-aware label alignment.

Each row is: label (right-padded to a common display-width over all
labels, using display_width so CJK/JP labels align in a monospace
terminal), a space, a bar of █ scaled so the max value maps to
`width` cells, a space, then the numeric value.
"""

import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1] / "scripts"))

from width import display_width

_BAR = "█"


def render_bar(pairs: list[tuple[str, float]], width: int = 20) -> str:
    """Render labelled values as a CJK-aligned horizontal bar chart."""
    if not pairs:
        return ""
    label_width = max(display_width(label) for label, _ in pairs)
    max_value = max(value for _, value in pairs)

    lines = []
    for label, value in pairs:
        pad = " " * (label_width - display_width(label))
        bar_len = round(value / max_value * width) if max_value else 0
        lines.append(f"{label}{pad} {_BAR * bar_len} {value}")
    return "\n".join(lines)
