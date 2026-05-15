---
name: project-overview
purpose: List all projects user has access to, with sections and task counts.
---

## Inputs

- None (lists all accessible projects).
- `--json`: optional.

## Output

Default Markdown:
```
## Projects (12)

### Backend (kouko, public)
- Engineering (8 tasks, 3 incomplete)
- Reviews (5 tasks, 5 incomplete)
- Operations (2 tasks, 0 incomplete)

### Frontend (kouko, public)
- ...
```

`--json`: array of `{name, owner, visibility, sections: [{name, total, incomplete}]}`.

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
  echo "### $project"
done

# For each project, navigate and snapshot sections
# (loop is illustrative; production implementation may batch via agent-browser tabs)
```

## Failure modes

- "Projects" page empty → user has no projects (valid empty result)
- Login wall → "Auth expiry"
