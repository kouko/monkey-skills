"""Classic Unicode tree / hierarchy renderer.

A node is a dict {"label": str, "children": [node, ...]} (children
optional / empty). The root label sits on line 1; each descendant is
prefixed with branch glyphs that precede the label, so CJK labels do
not affect the branch columns:

    訂單系統
    ├─ 訂單服務
    └─ 庫存サービス
       └─ 預扣

Per-ancestor continuation: a non-last ancestor contributes "│  ", a
last ancestor contributes "   " (three spaces). The connector for a
node itself is "├─ " unless it is its parent's last child, then "└─ ".
"""

_TEE = "├─ "
_ELBOW = "└─ "
_BAR = "│  "
_GAP = "   "


def render_tree(node: dict) -> str:
    """Render a node and its descendants as a multi-line tree string."""
    lines = [node["label"]]
    _render_children(node.get("children") or [], prefix="", lines=lines)
    return "\n".join(lines)


def _render_children(children: list, prefix: str, lines: list) -> None:
    last = len(children) - 1
    for i, child in enumerate(children):
        is_last = i == last
        connector = _ELBOW if is_last else _TEE
        lines.append(prefix + connector + child["label"])
        continuation = _GAP if is_last else _BAR
        _render_children(
            child.get("children") or [],
            prefix=prefix + continuation,
            lines=lines,
        )
