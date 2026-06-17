#!/usr/bin/env python3
"""Render a CoT diagram (node *content* → coloured Mermaid) for daily-news-digest.

The CoT visual style is FIXED and must stay consistent across every diagram in
every digest. So the agent (or its subagents) only supply node content; this
script applies the separators, the left-align wrapper, and the FIXED
role→colour scheme. Feed it JSON, get back a ```mermaid``` block.

Roles → colour (the one fixed scheme):
  觸發/事實  trigger  🟢 #d3f9d8/#2f9e44
  機制/為何  mech     🟣 #e5dbff/#5f3dc4
  結果       result   🟠 #ffe8cc/#d9480f
  含義/結論  concl    🔵 #c5f6fa/#0c8599

Input JSON (stdin or file arg):
  Chain (per-story / knowledge CoT 小圖) — roles assigned by POSITION:
    {"type":"chain","nodes":[{"title":"…","bullets":["a","b","c"]}, …]}
    first=trigger, last=concl, second-to-last=result (when ≥4 nodes), rest=mech.
  Web (day-level 總圖) — roles assigned EXPLICITLY:
    {"type":"web",
     "nodes":[{"id":"A","title":"…","bullets":[…],"role":"trigger"}, …],
     "edges":[{"from":"A","to":"B","label":"因果"[,"arrow":"-.->"]}, …]}

No third-party deps.
"""
import json
import sys

ROLE = {
    "trigger": "fill:#d3f9d8,stroke:#2f9e44,stroke-width:2px",
    "mech":    "fill:#e5dbff,stroke:#5f3dc4,stroke-width:2px",
    "result":  "fill:#ffe8cc,stroke:#d9480f,stroke-width:2px",
    "concl":   "fill:#c5f6fa,stroke:#0c8599,stroke-width:2px",
}
DL = "<div style='text-align:left'>"
DR = "</div>"


def san(s):
    """Obsidian-Mermaid node-text safety: parens → 「」."""
    return (s.replace("（", "「").replace("）", "」")
             .replace("(", "「").replace(")", "」"))


def node(nid, title, bullets):
    body = san(title) + "<br/>━━━━<br/>" + "<br/>".join("• " + san(b) for b in bullets)
    return f'{nid}["{DL}{body}{DR}"]'


def chain(nodes):
    L = len(nodes)
    if L < 2:
        sys.exit("chain needs ≥2 nodes")
    roles = ["mech"] * L
    roles[0] = "trigger"
    roles[L - 1] = "concl"
    if L >= 4:
        roles[L - 2] = "result"
    ns = [node(f"N{i}", n["title"], n["bullets"]) for i, n in enumerate(nodes)]
    lines = ["```mermaid", "flowchart LR", "    " + " --> ".join(ns)]
    lines += [f"    style N{i} {ROLE[roles[i]]}" for i in range(L)]
    lines.append("```")
    return "\n".join(lines)


def web(nodes, edges):
    by_id = {n["id"]: n for n in nodes}
    defined = set()

    def ref(nid):
        if nid in defined:
            return nid
        defined.add(nid)
        n = by_id[nid]
        return node(nid, n["title"], n["bullets"])

    lines = ["```mermaid", "flowchart TD"]
    for e in edges:
        arrow = e.get("arrow", "-->")
        lbl = f"|{san(e['label'])}|" if e.get("label") else ""
        lines.append(f"    {ref(e['from'])} {arrow}{lbl} {ref(e['to'])}")
    for n in nodes:
        if n["role"] not in ROLE:
            sys.exit(f"unknown role {n['role']!r}")
        lines.append(f"    style {n['id']} {ROLE[n['role']]}")
    lines.append("```")
    return "\n".join(lines)


def render(d):
    if d.get("type") == "chain":
        return chain(d["nodes"])
    if d.get("type") == "web":
        return web(d["nodes"], d["edges"])
    sys.exit("type must be 'chain' or 'web'")


def main():
    raw = open(sys.argv[1], encoding="utf-8").read() if len(sys.argv) > 1 else sys.stdin.read()
    print(render(json.loads(raw)))


if __name__ == "__main__":
    main()
