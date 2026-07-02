---
name: hermes-tweet
description: Guide Hermes Agent through sourced X/Twitter research and gated posting workflows with the Hermes Tweet plugin. Use when the user asks for profile, timeline, post, search, thread, or social-signal analysis on X/Twitter, or asks Hermes Agent to draft or perform a gated X/Twitter action.
---

# Hermes Tweet

Use this skill when the task needs Hermes Agent to work with X/Twitter through
the Hermes Tweet plugin.

## Preconditions

- Hermes Agent is installed.
- The Hermes Tweet plugin is enabled:

  ```bash
  hermes plugins install Xquik-dev/hermes-tweet --enable
  ```

- `XQUIK_API_KEY` is set for read workflows.
- `HERMES_TWEET_ENABLE_ACTIONS=true` is set only when the user has explicitly
  opted into write actions.

If Hermes Agent cannot resolve the plugin package, install the published PyPI
package into the Hermes Agent virtual environment:

```bash
uv pip install --python ~/.hermes/hermes-agent/venv/bin/python hermes-tweet
```

## Tool Order

1. Call `tweet_explore` first when tool names, examples, or argument shapes are
   unclear.
2. Call `tweet_read` for read-only work:
   - profile summaries
   - timeline scans
   - search result briefs
   - post URL analysis
   - thread context
   - public engagement checks
3. Call `tweet_action` only when all action gates pass.

## Action Gate

Before any `tweet_action` call, verify every item:

- The user explicitly requested the write action in this conversation.
- `HERMES_TWEET_ENABLE_ACTIONS=true` is set.
- The action target, account, text, and timing are unambiguous.
- The final text has been shown to the user unless they already approved exact
  text.
- The action is not spam, harassment, credential collection, impersonation, or
  evasion.

If any item fails, stop and ask for the missing approval or clarification.

## Research Workflow

For social-signal research:

1. Define the question, account, post URL, search phrase, or time window.
2. Use `tweet_read` to collect only the context needed for the request.
3. Separate observed facts from interpretation.
4. Cite source URLs or stable identifiers where available.
5. Include uncertainty when data is partial, unavailable, rate-limited, or time
   sensitive.

## Output Shape

Use concise sections:

- `Findings`: sourced observations.
- `Signals`: interpretation, momentum, risks, or audience patterns.
- `Gaps`: missing context or limits.
- `Next Actions`: optional read-only follow-ups, or gated write steps if the
  user requested action.

## Safety Boundaries

- Do not expose API keys, tokens, cookies, or local environment values.
- Do not claim whole-platform coverage.
- Do not turn partial X/Twitter data into definitive personal, financial,
  medical, legal, or safety conclusions.
- Do not perform write actions without the action gate.

