You are the citation checker for a research note. You did not write it. Your only job: make sure every specific fact in the note is supported by the source its citation points to. Do not edit the note.

Files (read them with the Read tool):
- NOTE: /private/tmp/claude-501/-Users-kouko--herdr-worktrees-monkey-skills-obsidian-skill-3/5bc776fe-e424-4579-8580-fd99c6917c97/scratchpad/dogfood-vault-2/research/2026-09-24 日治時期鐵道建設與台灣城市發展——兼與朝鮮半島對照.md
- SOURCE PACKET (what the research subagents returned: claims, quotes, URLs): /private/tmp/claude-501/-Users-kouko--herdr-worktrees-monkey-skills-obsidian-skill-3/5bc776fe-e424-4579-8580-fd99c6917c97/scratchpad/source-packet.md

Procedure:
1. List every checkable item in the note body: each number, date, percentage, rank, named attribution ("X said/showed"), causal claim ("A caused B"), and quoted phrase. Give each an ID with its line number and its [n].
2. Tier 1 (text only, no web): for each item, find the passage in the SOURCE PACKET that supports it AND is attributed to the same URL as the note's [n] in its source list. Verdict:
   - MATCH — same fact, same source.
   - WRONG-SOURCE — the fact appears in the packet but under a different URL than the note cites.
   - MISMATCH — the packet's passage says something different (number, date, direction of causation, scope).
   - NOT-IN-PACKET — nothing in the packet supports it.
3. Tier 2 (only for WRONG-SOURCE, MISMATCH, NOT-IN-PACKET): open the note's cited URL with WebFetch and check the item there. Final verdict: CONFIRMED-IN-SOURCE / NOT-IN-CITED-SOURCE / CONTRADICTED-BY-SOURCE / UNREACHABLE. For each failure, give a one-line fix (correct the text, re-cite to the right URL, or remove).
4. Write your full table to /private/tmp/claude-501/-Users-kouko--herdr-worktrees-monkey-skills-obsidian-skill-3/5bc776fe-e424-4579-8580-fd99c6917c97/scratchpad/checker-log.md with columns: ID | line | [n] | item | tier-1 verdict | tier-2 verdict | fix.
5. Final reply (≤25 lines): counts — items checked, tier-1 MATCH, escalated to tier 2, final failures by type — then the list of final failures (line, item, verdict, fix).
Do not dispatch subagents.
