from pathlib import Path


def append_journal_line(campaign_doc_path: Path, line_text: str) -> None:
    original = campaign_doc_path.read_text(encoding="utf-8")
    had_trailing_newline = original.endswith("\n")
    lines = original.splitlines()

    journal_idx = next(
        (i for i, ln in enumerate(lines) if ln.strip() == "## Journal"), None
    )
    if journal_idx is None:
        raise ValueError("No '## Journal' section found in campaign doc")

    # Section runs until the next level-1/level-2 heading, else EOF.
    section_end = len(lines)
    for i in range(journal_idx + 1, len(lines)):
        if lines[i].startswith("## ") or lines[i].startswith("# "):
            section_end = i
            break

    # Insert after the last content line, skipping trailing blanks in the section.
    insert_at = section_end
    while insert_at - 1 > journal_idx and lines[insert_at - 1].strip() == "":
        insert_at -= 1

    lines.insert(insert_at, line_text)

    new_text = "\n".join(lines)
    if had_trailing_newline:
        new_text += "\n"
    campaign_doc_path.write_text(new_text, encoding="utf-8")
