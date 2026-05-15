---
name: project-overview
purpose: List all projects user has access to, with sections and task counts.
---

## Inputs

- None (lists all accessible projects).
- `--json`: optional.

## Output

Default Markdown (v0.1.0 — project names only):
```
## Projects (12)

- Backend
- Frontend
- Eng Ops
- ...
```

`--json`: array of `{name}`.

**v0.2.0 deferred**: per-project section / task-count fetching requires navigating into each project (3 levels deep). Will add in v0.2.0 with batched parallel tab fetches. v0.1.0 returns top-level project list only.

## Procedure

```bash
ABX_SERVICE=asana abx open https://app.asana.com/0/projects
ABX_SERVICE=asana abx wait --load networkidle
SNAP=$(ABX_SERVICE=asana abx snapshot -i --json)

# Each project = role="row" within a grid, with name in role="link"
echo "$SNAP" | jq -r '
  .elements[]
  | select(.role=="row")
  | ([.children[]? | select(.role=="link") | .name] | first // "(unnamed)")
' | while read -r project; do
  echo "- $project"
done
```

## Failure modes

- "Projects" page empty → user has no projects (valid empty result)
- Login wall → "Auth expiry"
