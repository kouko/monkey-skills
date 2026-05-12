---
title: Quick start
description: Install and run the translation toolkit
---

# Quick start

Welcome to the translation toolkit. This guide shows you how to install
and run your first translation in under 5 minutes.

## Installation

Install via your package manager:

```bash
brew install translation-toolkit
```

Or download from <https://example.com/download>.

## Configuration

Create a `~/.translation-toolkit/config.yaml`:

```yaml
target_locale: ja-JP
glossary_path: ./docs/i18n/glossary-ja.md
```

Then run:

```bash
translate ./README.md
```

The output will be at `./README.ja.md`.

## See also
- [User guide](https://example.com/guide)
- [API reference](./api.md)
