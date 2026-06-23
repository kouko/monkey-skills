# .dbt-wiki/ Operation Log

> Append-only log of every init / rescan / query operation.
>
> Entry format: `## [YYYY-MM-DD] <operation> | <summary>`
>
> Operations: `init`, `rescan`, `query`
>
> Grep:
> ```
> grep "^## \[" .dbt-wiki/log.md | tail -10        # recent activity
> grep "rescan" .dbt-wiki/log.md                  # only rescan runs
> grep "sqlglot_failures" .dbt-wiki/log.md         # see parse failures
> ```

<!-- entries appended in reverse chronological order (newest at top after this comment) -->
