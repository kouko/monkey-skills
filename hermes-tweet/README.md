# hermes-tweet

> Hermes Agent X/Twitter workflow skill for sourced social-signal briefs.

Use this plugin when Claude should guide Hermes Agent through public X/Twitter
research tasks: profile checks, timeline scans, search briefs, post URL
analysis, and carefully gated write actions.

## Install

```bash
/plugin marketplace add kouko/monkey-skills
/plugin install hermes-tweet@monkey-skills
```

Then install the Hermes Agent plugin itself:

```bash
hermes plugins install Xquik-dev/hermes-tweet --enable
```

If the Hermes plugin install path cannot resolve Python packages in your
environment, install the published package into the Hermes Agent virtual
environment:

```bash
uv pip install --python ~/.hermes/hermes-agent/venv/bin/python hermes-tweet
```

## Configuration

Set `XQUIK_API_KEY` before running read or write workflows:

```bash
export XQUIK_API_KEY=...
```

Write actions remain disabled until you also opt in:

```bash
export HERMES_TWEET_ENABLE_ACTIONS=true
```

## Workflow

1. Start with `tweet_explore` for tool discovery and examples.
2. Use `tweet_read` for profile, timeline, search, post URL, and thread context.
3. Summarize findings with source URLs and clear uncertainty labels.
4. Use `tweet_action` only after the user explicitly requests a write action and
   `HERMES_TWEET_ENABLE_ACTIONS=true` is set.

## Links

- Hermes Tweet: https://github.com/Xquik-dev/hermes-tweet
- PyPI package: https://pypi.org/project/hermes-tweet/

