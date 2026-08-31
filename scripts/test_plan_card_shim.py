"""Pin scripts/plan_card.py as the exec shim onto loom-code/scripts/plan_card.py
(R11c) — stops a future full copy from silently replacing the SSOT pointer.
"""

from __future__ import annotations

from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
SHIM_PATH = REPO_ROOT / "scripts" / "plan_card.py"
SSOT_PATH = REPO_ROOT / "loom-code" / "scripts" / "plan_card.py"


def _is_execv_shim(text: str) -> bool:
    """A ~10-line os.execv passthrough onto loom-code/scripts/plan_card.py —
    no function bodies, no logic of its own."""
    lines = [line for line in text.splitlines() if line.strip()]
    return (
        len(lines) <= 15
        and "def " not in text
        and "os.execv(" in text
        and "loom-code" in text
        and "plan_card.py" in text
    )


def test_full_copy_of_ssot_is_rejected() -> None:
    """Discrimination proof: a full copy of the real plan_card.py (many
    `def`s, hundreds of lines) must fail the shim check — otherwise the
    check is too loose to ever catch a future full-copy regression."""
    ssot_text = SSOT_PATH.read_text(encoding="utf-8")
    assert not _is_execv_shim(ssot_text)


def test_repo_root_plan_card_is_execv_shim() -> None:
    shim_text = SHIM_PATH.read_text(encoding="utf-8")
    assert _is_execv_shim(shim_text)
