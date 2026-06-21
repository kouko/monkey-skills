# PRESENTATION EVAL — seed: Postgres vs MySQL (COMPARISON question)

Question: PostgreSQL vs MySQL for a new OLTP-heavy backend service?
Three arms render the SAME confirmed claims. FLAT = current fixed template; FREE = model picks structure; HINT = question-type-matched directive.

---
## ARM FLAT
# PostgreSQL vs MySQL for a new OLTP-heavy backend service?
## Summary
Both PostgreSQL and MySQL InnoDB implement MVCC, so neither blocks readers under typical OLTP — the foundational concurrency model is not a differentiator. PostgreSQL edges ahead on extensibility, JSON storage, replication flexibility, and licensing freedom, while MySQL retains advantages in raw write throughput benchmarks and memory efficiency under high connection counts without a pooler. The choice narrows to rich data types + extensions (PostgreSQL) vs predictable high-concurrency write scaling with simpler ops (MySQL). PostgreSQL is the stronger default for most new services unless connection count or write-peak constraints push toward MySQL.
## Findings
- **Both use MVCC; readers never block writers** *(high)* — [0][1]
- **PostgreSQL JSONB outperforms MySQL JSON for in-document lookups** *(high)* — [2][3]
- **PostgreSQL significantly more extensible (PostGIS/pgvector/pg_trgm)** *(high)* — [4]
- **PostgreSQL native logical replication more flexible OOTB** *(high)* — [6][5]
- **PostgreSQL permissive license; MySQL GPL v2 distribution obligations** *(high)* — [7]
- **MySQL historically higher raw write throughput simple-PK; gap narrowed** *(medium)* — [8]
- **PostgreSQL needs PgBouncer at high connection counts; MySQL thread model more memory-efficient** *(high)* — [9][10]
- **PostgreSQL FTS more capable natively** *(medium)* — [11]
## Caveats
Write-throughput [8] blog-level medium; sysbench rarely maps to production. MySQL JSON [3] medium. PgBouncer is operational concern not blocker. GPL applies to distribution not SaaS; legal review advised.
## Open Questions
- Peak concurrent connection count; is PgBouncer acceptable overhead?
- Need specialized data types/extensions (geo/vector/fuzzy)?
- Write-peak requirements; validated the benchmark gap on real workload?
- Is the DB binary distributed (GPL concern)?

---
## ARM FREE
# PostgreSQL vs MySQL for a New OLTP-Heavy Backend
## Bottom Line
**Default to PostgreSQL** unless a specific constraint tips the balance (extensibility, JSON, licensing). MySQL compelling if max write throughput on simple PK, very high connection counts without a pooler, or already MySQL-centric.
## Concurrency & Isolation
Both MVCC, readers never block writers — not a differentiator. [0][1]
## JSON / Semi-Structured
PostgreSQL wins: JSONB parsed binary + GIN. [2] MySQL 8.0 native JSON + functional indexes but no GIN-on-JSONB. [3] (medium on MySQL side)
## Extensibility
PostGIS / pgvector / pg_trgm; MySQL no comparable surface. [4]
## Replication & HA
PG native logical replication since v10 (table-level, cross-version). [6] MySQL async binlog default; sync (Group Replication/InnoDB Cluster) adds complexity. [5] (medium)
## Write Throughput
MySQL historically higher on simple-PK sysbench, gap narrowed. [8] (medium, blog-sourced) — unlikely the deciding factor for mixed OLTP.
## Connection Model & Memory
| | PostgreSQL | MySQL |
|---|---|---|
| Model | Process-per-connection | Thread-per-connection |
| Memory at high connections | Higher | Lower |
| Fault isolation | Better | Weaker |
| Mitigation | PgBouncer | Less needed |
PG memory concern above a few hundred connections [9]; MySQL thread model more efficient but less isolated. [10]
## Full-Text Search
PG built-in stemming+ranking [11]; MySQL InnoDB FTS weaker. (medium) Neither replaces Elasticsearch.
## Licensing
PG permissive; MySQL Community GPL v2 (copyleft in distribution). [7]
## Decision Matrix
| Factor | PostgreSQL | MySQL | Notes |
|---|---|---|---|
| MVCC / read concurrency | ✓ | ✓ | Tied |
| JSON / semi-structured | ✓✓ | ✓ | PG win |
| Extensibility | ✓✓ | ✗ | PG win |
| Replication simplicity | ✓✓ | ✓ | PG |
| Raw write throughput | ✓ | ✓✓ | MySQL, gap narrow |
| High-connection memory | ✓ (pooler) | ✓✓ | MySQL |
| FTS built-in | ✓✓ | ✓ | PG |
| License (commercial) | ✓✓ | ✓ | PG |
## When to Choose MySQL Instead
existing MySQL ops team; validated simple-insert bottleneck; extreme connection counts without PgBouncer; light JSON.

---
## ARM HINT
# PostgreSQL vs MySQL for a new OLTP-Heavy Backend Service
## Comparison Table
| Attribute | PostgreSQL | MySQL (InnoDB) | Notes |
|---|---|---|---|
| **Concurrency / MVCC** | MVCC all isolation; readers never block writers [0] | MVCC InnoDB; non-blocking under typical OLTP [1] | Functionally equivalent |
| **JSON support** | JSONB parsed binary + GIN [2] | Native JSON 8.0 + functional indexes; no GIN/JSONB [3] | PG wins if JSON on critical path (med–high) |
| **Extensibility** | PostGIS/pgvector/pg_trgm [4] | Narrower; external tooling [4] | PG if feature surface wide |
| **Replication** | Native logical since v10 [6] | Async binlog default; sync adds complexity [5] | PG simpler sync path |
| **Write throughput** | Competitive; trailed on simple PK | Historically higher (sysbench); gap narrowed [8] | Workload-dependent (medium, blog) |
| **Connection model** | Process-per-conn; PgBouncer standard [9] | Thread-per-conn; efficient at high counts, less isolated [10] | MySQL simpler at very high counts |
| **Full-text search** | Native stemming/ranking [11] | InnoDB FTS weaker [11] | PG if FTS primary (medium) |
| **Licensing** | Permissive [7] | Community GPL v2 [7] | PG avoids license risk |
## Synthesis
Choose PostgreSQL: flexible JSON querying / extensibility / licensing clarity / built-in logical replication / in-DB FTS. Choose MySQL: high-volume simple-PK writes (benchmarked) / very high connection counts without pooler / deep MySQL expertise. Caveats: [8] medium blog — benchmark your own; both need a pooler at scale; MVCC parity means concurrency isn't a differentiator. **Default for greenfield with no MySQL-specific constraint: PostgreSQL.**
