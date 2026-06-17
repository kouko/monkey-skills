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


def die(msg):
    """Clean failure (stderr + exit 2) — matches the collectors' style."""
    print(f"cot_mermaid: error: {msg}", file=sys.stderr)
    sys.exit(2)


def title_bullets(n, ctx):
    """Pull (title, bullets) from a node dict, with actionable errors."""
    if not isinstance(n, dict):
        die(f"{ctx}: node must be an object, got {type(n).__name__}")
    if "title" not in n or "bullets" not in n:
        die(f"{ctx}: node missing 'title'/'bullets' (keys: {sorted(n)})")
    if not isinstance(n["bullets"], list) or not n["bullets"]:
        die(f"{ctx}: 'bullets' must be a non-empty list")
    return n["title"], n["bullets"]


def node(nid, title, bullets):
    body = san(title) + "<br/>━━━━<br/>" + "<br/>".join("• " + san(b) for b in bullets)
    return f'{nid}["{DL}{body}{DR}"]'


def chain(nodes):
    if not isinstance(nodes, list):
        die("chain 'nodes' must be a list")
    L = len(nodes)
    if L < 2:
        die("chain needs ≥2 nodes")
    roles = ["mech"] * L
    roles[0] = "trigger"
    roles[L - 1] = "concl"
    if L >= 4:
        roles[L - 2] = "result"
    ns = [node(f"N{i}", *title_bullets(n, f"chain node {i}")) for i, n in enumerate(nodes)]
    lines = ["```mermaid", "flowchart LR", "    " + " --> ".join(ns)]
    lines += [f"    style N{i} {ROLE[roles[i]]}" for i in range(L)]
    lines.append("```")
    return "\n".join(lines)


def web(nodes, edges):
    if not isinstance(nodes, list) or not isinstance(edges, list):
        die("web needs 'nodes' and 'edges' lists")
    by_id = {}
    for n in nodes:
        if not isinstance(n, dict) or "id" not in n:
            die(f"web node missing 'id': {n}")
        by_id[n["id"]] = n
    defined = set()

    def ref(nid):
        if nid not in by_id:
            die(f"edge references undefined node {nid!r}")
        if nid in defined:
            return nid
        defined.add(nid)
        return node(nid, *title_bullets(by_id[nid], f"web node {nid!r}"))

    lines = ["```mermaid", "flowchart TD"]
    for e in edges:
        if "from" not in e or "to" not in e:
            die(f"edge missing 'from'/'to': {e}")
        arrow = e.get("arrow", "-->")
        lbl = f"|{san(e['label'])}|" if e.get("label") else ""
        lines.append(f"    {ref(e['from'])} {arrow}{lbl} {ref(e['to'])}")
    for n in nodes:
        if n.get("role") not in ROLE:
            die(f"unknown/missing role {n.get('role')!r} on node {n['id']!r}")
        lines.append(f"    style {n['id']} {ROLE[n['role']]}")
    lines.append("```")
    return "\n".join(lines)


def render(d):
    if not isinstance(d, dict) or "type" not in d:
        die("input must be a JSON object with a 'type' field")
    if d["type"] == "chain":
        if "nodes" not in d:
            die("chain input needs 'nodes'")
        return chain(d["nodes"])
    if d["type"] == "web":
        if "nodes" not in d or "edges" not in d:
            die("web input needs 'nodes' and 'edges'")
        return web(d["nodes"], d["edges"])
    die(f"type must be 'chain' or 'web', got {d['type']!r}")


def main():
    try:
        raw = open(sys.argv[1], encoding="utf-8").read() if len(sys.argv) > 1 else sys.stdin.read()
    except OSError as e:
        die(f"cannot read input: {e}")
    try:
        d = json.loads(raw)
    except json.JSONDecodeError as e:
        die(f"invalid JSON input: {e}")
    print(render(d))


if __name__ == "__main__":
    main()
