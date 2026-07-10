# Diagram trigger card (ascii-graph-toolkit)
Before typing any box-drawing / ASCII diagram (┌─┐, +--+) in chat or a
text artifact: if the diagram has CJK (中/日) labels anywhere OR ≥3
boxes, invoke the `ascii-graph` skill FIRST — its width-aware generators
and verify-loop keep full-width characters aligned; eyeballed CJK padding
silently breaks. Trivial all-ASCII sketches (≤2 boxes, no CJK) may be
hand-drawn. Option comparisons stay markdown tables, not ASCII boxes.
