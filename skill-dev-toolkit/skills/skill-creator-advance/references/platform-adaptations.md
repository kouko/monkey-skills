# Platform Adaptations

Guidelines for adapting skills to different Claude interfaces.

## Platform Differences
Different Claude interfaces have varying capabilities that affect skill design:

| Platform | Constraints | Adaptation Strategy |
|---|---|---|
| **Claude.ai / Web** | Full tool access, file upload, long context | Standard skill design, leverage all available tools |
| **Claude for Desktop** | Similar to web, but may have local file access differences | Test local file paths, consider OS-specific tools |
| **Claude.ai / Cowork** | No browser access, no subagent spawning in some modes | Pre-compute data, avoid real-time web requests, use provided context |
| **Claude CLI / API** | Programmatic access, no interactive prompts | Design for headless operation, use structured inputs/outputs |
| **Mobile / Limited interfaces** | Shorter context, touch-focused | Prioritize concise outputs, avoid complex multi-step workflows |

## Adaptation Strategy
When adapting a skill for platform constraints:

### Step 1: Identify Constraint
- Which platform(s) will this skill run on?
- What specific capabilities are missing or limited?
- Example: "No subagent spawning" means you cannot use Agent() calls

### Step 2: Modify Approach
- Replace disallowed patterns with allowed alternatives
- Example: Instead of spawning subagents for parallel processing, use sequential processing with progress tracking
- Example: Instead of file upload/download, use clipboard or structured text exchange

### Step 3: Update Documentation
- Add platform-specific notes in SKILL.md using conditional syntax
- Example: `[Claude.ai only: Use file upload]` or `[CLI only: Expect JSON input]`
- Update references/platform-adaptations.md with your specific findings

### Step 4: Test
- Verify the skill works on all target platforms
- Document any remaining limitations in the skill description

## Common Adaptations
- **No subagents**: Pre-compute data, use sequential processing
- **No browser**: Embed essential data, avoid real-time scraping
- **Shorter context**: Chunk inputs, summarize history
- **No file upload**: Use inline text, base64 small assets when essential
EOF