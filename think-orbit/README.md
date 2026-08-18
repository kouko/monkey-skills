# think-orbit

> Single-user decision-reasoning assistant — turns a discussion into a transparent chain of thought: one markdown file per node, assumption files with stale propagation, silent mechanical gates, and a regenerated DAG view.

Read this in: **English** | [日本語](README.ja.md) | [繁體中文](README.zh-TW.md)

**Version**: 0.1.0
**Part of**: [monkey-skills](https://github.com/kouko/monkey-skills)
**License**: MIT
**Status**: Part 1 — pre-release. The core conversation protocol is not yet implemented (lands in Task 11).

## Usage

Say "help me decide X" (or 「我要決定」/「決策推演」) to open a decision — the `using-think-orbit` entry skill routes you in; the agent asks a few questions and writes the reasoning to markdown files as you talk, regenerating a DAG view you can read at any time.

## Install

```bash
/plugin marketplace add kouko/monkey-skills
/plugin install think-orbit@monkey-skills
```

**Requires**: Python 3 with PyYAML (`pip install pyyaml`) — the gate and DAG scripts run on it.
