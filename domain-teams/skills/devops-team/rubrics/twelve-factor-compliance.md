# Twelve-Factor Compliance Gate

## Scope Boundary

Review an application's conformance to the Twelve-Factor App methodology.
This is a SHOULD gate that auto-triggers for new cloud-native applications
in the Deploy Spec Creation workflow, and a MUST gate when explicitly
invoked through the Twelve-Factor Audit workflow.

Do NOT review: code quality, security, performance, or deployment
mechanics — those belong to other gates. This gate evaluates only
architectural conformance to 12-Factor principles.

**Vocabulary reference**: `standards/twelve-factor.md`

## Scoring Approach

The 12 factors collapse into **4 evaluable dimensions** for practical scoring.
Factors VIII (Concurrency), XI (Logs), and XII (Admin processes) are scored
informally in a Notes section because they are modern-superseded or
context-dependent.

## Flag Definitions

### Dimension 1: Configuration Externalization
*Covers III (Config), X (Dev/prod parity)*

- 🔴 **Fatal**: Configuration is hardcoded in source or committed to the
  repository. Secrets live in version control. Different environments
  require different code branches.
- 🟡 **Warning**: Most config is externalized but one or two values are
  hardcoded (e.g., feature flags, default timeouts). Dev/prod parity has
  minor gaps.
- 🟢 **Clear**: All config via environment variables or secret manager;
  dev/staging/prod use the same code with different env vars; no
  environment-specific branches.

### Dimension 2: Statelessness & Disposability
*Covers VI (Processes), IX (Disposability)*

- 🔴 **Fatal**: Application stores state in local process memory or local
  filesystem. Restart causes data loss. Startup takes >1 minute. No
  graceful shutdown handling (drops in-flight requests on SIGTERM).
- 🟡 **Warning**: Mostly stateless but local caches are relied upon for
  correctness. Startup is 10-60 seconds. Graceful shutdown exists but
  has edge cases.
- 🟢 **Clear**: Fully stateless; all state in backing services;
  startup ≤10 seconds; graceful shutdown drains connections on SIGTERM.

### Dimension 3: Backing Services & Port Binding
*Covers IV (Backing services), VII (Port binding)*

- 🔴 **Fatal**: Backing services are hardcoded by hostname or driver.
  Changing a database requires code changes. App requires external web
  server (Apache, nginx, IIS) configured out-of-band to work.
- 🟡 **Warning**: Backing services are config-driven but tightly coupled
  to a specific implementation (e.g., Postgres-specific SQL without
  abstraction layer). Port binding works but requires non-standard setup.
- 🟢 **Clear**: All backing services attached via URLs/connection strings
  from config; swappable via env var change; app binds its own port and
  serves HTTP directly.

### Dimension 4: Build/Release/Run Separation
*Covers V (Build/release/run), I (Codebase), II (Dependencies)*

- 🔴 **Fatal**: Production servers run `git pull` or `npm install`. No
  immutable build artifacts. Dependencies declared implicitly (system
  packages, not in a manifest).
- 🟡 **Warning**: Build artifacts exist but are sometimes rebuilt per
  environment. Some dependencies are vendor-pinned but lockfile is
  not committed.
- 🟢 **Clear**: Strict build → release → run separation; immutable
  artifacts (container images) tagged with commit SHA; all dependencies
  declared in a lockfile committed to version control.

## Notes Section (Informal scoring)

These factors are evaluated but do not produce flags:

### VIII. Concurrency
Modern interpretation: horizontal pod autoscaling. Note whether the app
can scale horizontally without code changes. If the app is a singleton
that cannot run multiple instances, flag as informal concern.

### XI. Logs
Required: app writes unbuffered to stdout/stderr. The platform collects.
Violation: app writes to `/var/log/myapp.log` or manages its own log files.
Include as informal concern if violated.

### XII. Admin processes
Largely irrelevant in serverless. Context-dependent in containers. Note
the admin task approach (kubectl exec, job resources, etc.) without
scoring.

## Verdict Rules

1. **NEEDS_REVISION**: Any 1 🔴 fatal flag
2. **NEEDS_REVISION**: 2 or more 🟡 warning flags
3. **PASS_WITH_NOTES**: Exactly 1 🟡 warning flag, no 🔴
4. **PASS**: All 🟢 clear

## Skip Reasons (Documented Exceptions)

This gate may be skipped with one of these stated reasons:

- **"Legacy monolith migration in progress"** — 12-Factor gradually being
  adopted; skip for current pass, track progress elsewhere
- **"Serverless — XII N/A"** — admin processes factor doesn't apply
- **"On-prem deploy — IV fixed"** — backing services are tightly coupled
  to on-prem infrastructure by operational necessity
- **"Stateful workload by design"** — databases, message brokers, etc.
  have legitimate state; factor VI does not apply

A skip reason is not a verdict — it documents why the gate was not run.
The Twelve-Factor Audit workflow specifically forbids skipping (it's MUST
within that workflow); Deploy Spec Creation allows skipping with a reason.

## Rules

- **Do not penalize legacy characteristics that cannot be fixed.** 12-Factor
  is aspirational for new apps, not a cudgel for legacy.
- **Modern reinterpretations are acceptable.** If the app is on Kubernetes
  with HPA, that satisfies factor VIII even though Wiggins' original 2011
  text said "process model".
- **Aged factors are scored informally.** VIII, XI, XII are modern-
  superseded or context-dependent; they are noted but do not produce
  dimension flags.
- **When issuing NEEDS_REVISION, name the specific factor and suggest a fix.**

## Output Format

1. **Flags**: List each triggered flag with `[🔴 Dimension]` or `[🟡 Dimension]`
2. **Evidence**: Quote the specific deploy spec or config that triggered the flag
3. **Informal notes**: Factors VIII, XI, XII observations
4. **Fix instruction**: Specific factor to address
5. **Verdict**: PASS / PASS_WITH_NOTES / NEEDS_REVISION (or document skip reason)

## Sources

- `standards/twelve-factor.md` — authoritative vocabulary
- [12factor.net](https://12factor.net/) — original Wiggins text
- Hoffman, K. *Beyond the Twelve-Factor App*. O'Reilly, 2016.
