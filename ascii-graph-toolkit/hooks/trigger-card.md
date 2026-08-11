# Diagram trigger card (ascii-graph-toolkit)
Before typing any box-drawing / ASCII diagram (┌─┐, +--+) in chat or a
text artifact: if the diagram has CJK (中/日) labels anywhere OR ≥3
boxes, invoke the `ascii-graph` skill FIRST — its width-aware generators
and verify-loop keep full-width characters aligned; eyeballed CJK padding
silently breaks. Trivial all-ASCII sketches (≤2 boxes, no CJK) may be
hand-drawn. Option comparisons stay markdown tables, not ASCII boxes.

GENERATIVE trigger — when you are
about to EXPLAIN in chat any flow / state machine / architecture
involving ≥3 steps, states, or components: invoke the `ascii-graph`
skill FIRST and lead the explanation with the generated diagram,
then narrate. Skip when one short paragraph fully covers it —
never draw for decoration; option comparisons keep the table rule
above.
