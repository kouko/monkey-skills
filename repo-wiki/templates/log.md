# .repo-wiki/ Operation Log

> Append-only log of every init / ingest / query operation.
>
> Entry format: `## [YYYY-MM-DD] <operation>:<mode> | <title>`
>
> Operations: `init`, `ingest:git`, `ingest:manual`, `ingest:doc-import`, `query`
>
> Grep:
> ```
> grep "^## \[" .repo-wiki/log.md | tail -10        # recent activity
> grep "ingest:git" .repo-wiki/log.md               # only code changes
> grep "ingest:manual" .repo-wiki/log.md            # only context captures
> ```

<!-- entries appended in reverse chronological order (newest at top after this comment) -->
