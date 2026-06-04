#!/usr/bin/env bash
# Probe A — activation harness. Runs each corpus query 2x through `claude -p`
# against the sandbox skill menu (fact-check + 3 distractors), parses which
# Skill fired. Emits results.jsonl: {id, run, should_fire, route_to, fired, routed}.
set -u
REPO="/Users/kouko/GitHub/monkey-skills/.claude/worktrees/doogfood-testing-fieldtesting"
OUT="$REPO/docs/skill-dogfood/2026-06-04-fact-check"
SBX="$(cat /tmp/factcheck-sbx-path)"
CORPUS="$OUT/trigger-corpus.json"
RESULTS="$OUT/probe-a-results.jsonl"
: > "$RESULTS"
mkdir -p "$OUT/probe-a-raw"

n=$(jq '.queries | length' "$CORPUS")
for ((i=0; i<n; i++)); do
  id=$(jq -r ".queries[$i].id" "$CORPUS")
  q=$(jq -r ".queries[$i].query" "$CORPUS")
  sf=$(jq -r ".queries[$i].should_fire" "$CORPUS")
  rt=$(jq -r ".queries[$i].route_to" "$CORPUS")
  for run in 1 2; do
    raw="$OUT/probe-a-raw/${id}-r${run}.jsonl"
    ( cd "$SBX" && timeout 90 claude -p "$q" --max-turns 1 \
        --allowedTools Skill --output-format stream-json --verbose 2>/dev/null ) > "$raw"
    if grep -q '"name":"Skill"' "$raw"; then
      fired=true
      routed=$(jq -rc 'select(.type=="assistant") | .message.content[]? | select(.type=="tool_use" and .name=="Skill") | .input.skill' "$raw" 2>/dev/null | head -1)
    else
      fired=false
      routed=""
    fi
    printf '{"id":"%s","run":%d,"should_fire":%s,"route_to":"%s","fired":%s,"routed":"%s"}\n' \
      "$id" "$run" "$sf" "$rt" "$fired" "$routed" | tee -a "$RESULTS"
    sleep 2
  done
done
echo "=== DONE -> $RESULTS ==="
