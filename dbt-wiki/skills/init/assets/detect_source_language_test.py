#!/usr/bin/env python3
"""Smoke test for detect_source_language.py.

Run from this directory:

    python3 detect_source_language_test.py

Pure stdlib. Builds throwaway .dbt-wiki fixtures and asserts the resolved
language code (auto-detect + explicit overrides).
"""
from __future__ import annotations

import os
import subprocess
import sys
import tempfile
from pathlib import Path

SCRIPT = Path(__file__).parent / "detect_source_language.py"


def build_wiki(tmp: Path, description: str) -> Path:
    """Write a minimal .dbt-wiki with one evidence model carrying `description`."""
    d = tmp / ".dbt-wiki" / "_evidence" / "models"
    d.mkdir(parents=True, exist_ok=True)
    (d / "x.md").write_text(
        "---\nunique_id: model.p.x\n---\n## Description\n" + description + "\n",
        encoding="utf-8",
    )
    return tmp / ".dbt-wiki"


# English filler that always dwarfs the CJK char count (mimics ASCII identifiers/SQL).
EN = ("daily revenue per store net of refunds aggregated by region and channel "
      "for monthly reporting joined to customers and orders ") * 3

# (description_text, argv_extra, env_extra, expected_code)
CASES = [
    # 1. Chinese prose + lots of ASCII -> zh (Han fraction floor, not majority)
    ("這個模型彙總每日營業額,處理發票開立與作廢,並依地區與通路認列。" + EN, [], {}, "zh"),
    # 2. English only -> en
    (EN, [], {}, "en"),
    # 3. Tiny Chinese (<5%) amid heavy English -> en (floor cuts the other way)
    (EN + EN + "註", [], {}, "en"),
    # 4. Japanese (kana present) -> ja
    ("この毎日の売上モデルは請求書の発行と取消を処理する。" + EN, [], {}, "ja"),
    # 5. Korean (hangul) -> ko
    ("이 일일 매출 모델은 송장 발행과 취소를 처리합니다." + EN, [], {}, "ko"),
    # 6. --language override beats auto-detect (Chinese fixture, forced ko)
    ("這個模型彙總每日營業額。" + EN, ["--language", "ko"], {}, "ko"),
    # 7. DBT_WIKI_LANGUAGE env override
    ("這個模型彙總每日營業額。" + EN, [], {"DBT_WIKI_LANGUAGE": "fr"}, "fr"),
]


def run(wiki: Path, argv_extra, env_extra) -> str:
    env = {**os.environ, **env_extra}
    proc = subprocess.run(
        [sys.executable, str(SCRIPT), str(wiki), *argv_extra],
        capture_output=True, text=True, timeout=10, env=env,
    )
    return proc.stdout.strip()


def main() -> int:
    failures = 0
    for i, (desc, argv_extra, env_extra, expected) in enumerate(CASES, 1):
        with tempfile.TemporaryDirectory() as td:
            wiki = build_wiki(Path(td), desc)
            got = run(wiki, argv_extra, env_extra)
        ok = got == expected
        print(f"[{i}/{len(CASES)}] {'OK  ' if ok else 'FAIL'} expect={expected} got={got}")
        if not ok:
            failures += 1
    # 8. nonexistent dir -> safe default 'en'
    got = subprocess.run([sys.executable, str(SCRIPT), "/no/such/dir"],
                         capture_output=True, text=True).stdout.strip()
    ok = got == "en"
    print(f"[8/8] {'OK  ' if ok else 'FAIL'} nonexistent-dir expect=en got={got}")
    failures += 0 if ok else 1
    total = len(CASES) + 1
    print(f"\n{total - failures}/{total} passed")
    return 0 if failures == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
