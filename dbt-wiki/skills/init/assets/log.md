# .dbt-wiki/ Operation Log

> Append-only log of every init / refresh / query operation.
>
> Entry format: `## [YYYY-MM-DD] <operation> | <summary>`
>
> Operations: `init`, `refresh`, `query`
>
> Grep:
> ```
> grep "^## \[" .dbt-wiki/log.md | tail -10        # recent activity
> grep "refresh" .dbt-wiki/log.md                  # only refresh runs
> grep "sqlglot_failures" .dbt-wiki/log.md         # see parse failures
> ```

<!-- entries appended in reverse chronological order (newest at top after this comment) -->
