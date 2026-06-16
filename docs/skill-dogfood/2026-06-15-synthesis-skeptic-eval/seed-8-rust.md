# SEED 8 — Rust adoption (DECISION; team no Rust exp + tight deadline = mooting potential)

## QUESTION
Should we commit to adopting Rust for our new backend service? (stack Go/Python; team has NO prior Rust experience; tight deadline)

## CONFIRMED CLAIMS BLOCK
### [0] Rust "most admired" language 9 yrs running (SO 2024, >80% want to continue). (9-0, primary, high)
### [1] Microsoft MSRC: ~70% of CVEs are memory-safety bugs Rust prevents at compile time; Google Project Zero corroborates ~70% Android. (8-2, primary, high)
### [2] Discord (2023) Go→Rust rewrite ~10x p99 latency improvement, attributed to no GC. (6-4, blog, medium — single case, workload-dependent)
### [3] Borrow-checker curve 3–6 months to productivity for systems programmers; longer from GC languages. (7-3, secondary, medium)
### [4] Teams with no prior Rust experience under deadline pressure consistently report significant initial velocity drops in the ownership/borrowing phase. (8-2, blog, medium — qualitative single-author + HN/Reddit corroboration)
### [5] Go designed for fast onboarding; baseline productivity 2–4 weeks for compiled-language devs. (9-1, primary, high)
### [6] Rust async (Tokio) production-ready but adds overhead (async/await, futures, pinning) compounding the curve. (7-3, primary tokio, medium)
### [7] Rust compile times 5–10x Go for large clean builds; incremental narrows gap. (6-4, blog, medium)
### [8] Go covers the majority of high-throughput backend use cases with sufficient latency/memory, no systems-level memory mgmt. (8-2, secondary, medium — "majority" not quantified)
### [9] Rust job market ~8x smaller than Go backend openings (LinkedIn early 2024). (5-3, primary listing, low — point-in-time, single informal survey)
### [10] Google Android: Rust new-code memory-safety vulns near zero vs ~76% old C/C++. (9-1, primary, high — systems/OS-specific, not typical backend)
### [11] Rust backend web ecosystem grown but ORM/DB tooling lags Go (Diesel/SeaORM < sqlx/GORM). (6-4, secondary, medium)

## ARM A — SINGLE-PASS SYNTHESIS
SUMMARY: For a team with no prior Rust experience facing a tight deadline, adopting Rust for a new backend service is high-risk and unlikely to pay off in the near term. The borrow-checker learning curve runs 3–6 months (longer coming from GC languages like Go or Python), and teams consistently report significant velocity drops in the first two months under deadline pressure — directly conflicting with a tight-timeline mandate. Go is already in the team's stack, was designed for fast onboarding (productive in 2–4 weeks), and is more than adequate for the vast majority of high-throughput backend use cases. Rust's genuine advantages — compile-time memory safety and GC-free latency predictability — are compelling for systems-level or latency-critical workloads, but do not materially benefit standard HTTP/gRPC/DB-facing microservices where Go already performs well. The recommendation is to stay on Go now and evaluate Rust for a future, non-deadline-bound service once the team has had time to build familiarity.

FINDINGS:
- [high] Steep curve: 3–6 months to productivity, longer from GC languages; teams under deadline report velocity drops first 1–2 months. | infoq + logankibler | evidence: self-reported surveys + HN/Reddit corroboration; medium-quality sourcing but directionally consistent.
- [high] Go fast onboarding (2–4 weeks); covers majority of high-throughput backend use cases with adequate latency/memory, no systems-level mem mgmt. | go.dev + teivah | evidence: Go spec verifiable (primary); perf broadly supported, "majority" not quantified.
- [high] Rust real memory safety: MSRC + Project Zero ~70% CVEs; Android near-zero vs ~76% C/C++ — but applies mainly to systems/low-level code, not typical Go/Python backends. | msrc + googleblog | evidence: two primary sources; caveat systems-specific.
- [medium] Rust perf advantage workload-specific: Discord ~10x p99 from no GC; not generalizable without profiling. | discord blog | evidence: single case study, plausible mechanism.
- [medium] Tokio production-ready but compounds overhead; ORM/DB tooling lags Go; compile times 5–10x. | tokio + lib.rs + matklad | evidence: Tokio primary, tooling directional, compile-time varies.
- [medium] Rust satisfaction very high (9 yrs most-admired, >80%) but job market ~8x thinner than Go → harder hiring/backfill. | SO 2024 + linkedin | evidence: satisfaction high-confidence; job-market low-confidence (point-in-time, single informal).

CAVEATS: Learning-curve/velocity estimates self-reported, vary by background/support/complexity. Discord case is single org w/ specific GC bottleneck — don't generalize without profiling. Memory-safety CVE stats from systems/OS contexts, don't directly translate to backend APIs. Tooling gap narrowing YoY; 2022–23 sources may understate current maturity. Job-market data single informal snapshot — verify before hiring arguments.

OPEN QUESTIONS:
- Does the new service have a specific latency/memory/throughput requirement Go demonstrably cannot meet? (If not, the perf argument doesn't apply.)
- What's the actual deadline length, and is there buffer to absorb a 2–3 month velocity dip?
- Is there a subset (hot path, security-sensitive module) where Rust could be adopted in isolation rather than whole-service?
- How will the team staff/maintain Rust long-term — hiring pipeline / training, or knowledge silo?
