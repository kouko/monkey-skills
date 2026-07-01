---
title: dbt-wiki Index
type: index
last_updated: <YYYY-MM-DD>
manifest_sha: <md5>
source_language: <lang>      # resolved at Phase B step 0 (detect_source_language)
dialect: <sqlglot dialect>   # resolved at Step 4a (adapter -> dialect); read by dbt-wiki:pack
---

# dbt-wiki Index

> Master catalog of all model / source / macro pages in `.dbt-wiki/`.
> Regenerated on every `/dbt-wiki:init` and `/dbt-wiki:rescan` run.
> Do not edit by hand — changes will be overwritten.

## Models

### Staging (`models/staging/`)
- (auto-populated by init)

### Intermediate (`models/intermediate/` or `models/interm/`)
- (auto-populated by init)

### Marts (`models/marts/` and tier-specific marts)
- (auto-populated by init)

### Other tiers
- (auto-populated by init)

## Models by Materialization

### Table
- (auto-populated)

### View
- (auto-populated)

### Incremental
- (auto-populated)

### Ephemeral
- (auto-populated)

## Models by Tag
- (auto-populated; one section per distinct tag)

## Models by Group
- (auto-populated; one section per group from groups.yml)

## Sources
- (auto-populated; grouped by source_name)

## Macros (used by ≥1 model)
- (auto-populated; project macros first, then external packages)

## Seeds
- (auto-populated)

## Snapshots
- (auto-populated)

## Singular Tests
- (auto-populated; only tests/*.sql files, not schema.yml column tests)

## Exposures
- (auto-populated; or "No exposures declared" if section empty)

## Statistics
- Total models: <N>
- Total sources: <N>
- Total macros (used): <N>
- Column lineage extracted: <N>/<total models> (<percent>%)
- sqlglot parse failures: <N> (see log.md for details)
