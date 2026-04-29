# Write Architecture — Worked Examples (Companion to write-architecture.md)

Companion file containing 5 complete architecture documentation
examples spanning the L1 / L2 / data-flow / deployment / security
artifact types. Loaded by the `worker` agent via the `additional:`
field in full mode; **NOT** loaded in quick mode (architecture
documentation is hard-blocked from quick mode anyway, see
`protocols/quick-write.md` §Hard Block List).

**Parent protocol**: `protocols/write-architecture.md`
**Origin**: Examples 1, 3, 4, and 5 are adapted from
[Trong-Tra/agent-skills `documentation-specialist`](https://github.com/Trong-Tra/agent-skills/tree/main/documentation-specialist)
`architecture/examples.md` Examples 1, 4, 5, and 6. Example 2 (Payment
Service component spec) was originally written inline in
`write-architecture.md`; it moves here as part of the Strategy D
companion-file refactor.

## How to use this companion

Match the artifact you are writing to the closest example in the table:

| Artifact type | Example | Source structure |
|---------------|---------|------------------|
| L1 system context | Example 1: file-upload virus scanner | External actors + system boundary + trust annotations |
| L2 component spec | Example 2: Payment Service | All 10 required fields including failure modes |
| Data flow + error path | Example 3: user registration | Happy path + duplicate email error + race condition |
| Deployment topology | Example 4: multi-region active-passive | Region subgraphs + instance sizes + failover procedure |
| Security model | Example 5: fintech SOC 2 | Trust boundaries + auth layers + data classification |

---

## Example 1: System Context Diagram (L1)

**Scenario**: A team needs to understand what external systems their
file-upload service interacts with and where the trust boundary is.

```markdown
## System Context

Our system (blue subgraph) manages file uploads and virus scanning
for enterprise clients.

​```mermaid
graph TB
    subgraph "Our System"
        API[Upload API]
        SCAN[Virus Scanner]
        STORE[File Store]
        NOTIFY[Notification Service]
    end

    CLIENT[Enterprise Client] -->|HTTPS /upload| API
    API -->|gRPC| SCAN
    API -->|PUT| STORE
    SCAN -->|Pub/Sub| NOTIFY
    NOTIFY -->|Webhook| CLIENT
    SCAN -->|REST| CLAMAV[ClamAV Cloud]
    STORE -->|S3 API| S3[(AWS S3)]
​```

**External systems**:
- ClamAV Cloud: third-party virus scanning. Pay per scan.
- AWS S3: file storage. Our account, our buckets.

**Trust boundaries**:
- Client → Upload API: authenticated via API key
- Upload API → internal services: mTLS
- Upload API → S3: IAM role with least privilege
```

**Why this works**: clear system boundary via Mermaid subgraph.
External systems named and categorized (third-party vs first-party).
Trust boundaries explicit. Every arrow labeled with protocol.

---

## Example 2: Component Specification (L2)

**Scenario**: Documenting a payment processing service.

```markdown
## Payment Service

**Purpose**: Processes customer payments, handles refunds, and
manages payout schedules.

**Responsibilities**:
1. Validate payment requests (amount, currency, method)
2. Route to appropriate processor (Stripe for cards, ACH for bank)
3. Handle processor webhooks and update internal state
4. Calculate and schedule payouts to merchants
5. Maintain idempotency for all payment operations

**Tech stack**: Python 3.11, FastAPI, PostgreSQL 16, Redis, Celery

**API surface**:
- Public REST: `POST /v1/payments`, `POST /v1/refunds`
- Internal gRPC: `payment.v1.PaymentService`
- Webhooks: `POST /webhooks/stripe`, `POST /webhooks/ach`

**Inbound data**: payment requests from API Gateway, webhook events
from Stripe and ACH, refund requests from Support Dashboard.

**Outbound data**: payment events to Event Bus, payout instructions
to Stripe Connect, metrics to Prometheus, logs to Loki.

**State**:

| Store | Data | Retention |
|-------|------|-----------|
| PostgreSQL | Payments, refunds, payouts | 7 years (regulatory) |
| Redis | Idempotency keys, rate-limit counters | 24 hours |
| S3 | Webhook payloads (audit trail) | 7 years |

**Failure modes**:

| Scenario | Behavior | Alert |
|----------|----------|-------|
| Stripe API timeout | Retry 3× with exponential backoff; return 202 | `stripe_timeout_rate > 5%` |
| Database unavailable | Queue request in Redis; return 503 with Retry-After | `db_connection_pool_exhausted` |
| Duplicate idempotency key | Return cached response; log warning | None (expected) |
| Invalid webhook signature | Reject with 401; log security event | `webhook_auth_failure > 1/min` |

**Scaling**: stateless horizontal; database sharded by `merchant_id`;
Celery workers scale on `celery_queue_length`.

**Security notes**: card numbers never touch our servers (Stripe
Elements); webhook signatures verified with HMAC; database stores
only token references, not PANs.
```

**Why this works**: every required field present. Failure modes
table covers Stripe timeout, database outage, expected duplicates,
security events. Scaling notes are specific (sharded by
`merchant_id`), not vague ("scale horizontally"). Security notes
are concrete and verifiable.

---

## Example 3: Data Flow With Error Path

**Scenario**: User registration with email verification.

```markdown
### Happy path

​```mermaid
sequenceDiagram
    participant U as User
    participant C as Client App
    participant GW as API Gateway
    participant A as Auth Service
    participant DB as Users DB
    participant Q as Email Queue
    participant W as Email Worker
    participant S as SendGrid

    U->>C: Enter email + password
    C->>GW: POST /register
    GW->>A: CreateUser
    A->>DB: INSERT user (status=pending)
    A->>Q: Publish verification_email
    A-->>GW: UserResponse
    GW-->>C: 201 Created
    Q->>W: verification_email
    W->>S: Send verification email
    S-->>U: Email with link
    U->>C: Click verification link
    C->>GW: GET /verify?token=...
    GW->>A: VerifyEmail
    A->>DB: UPDATE status=active
    A-->>GW: Success
    GW-->>C: Redirect to dashboard
​```

### Error: duplicate email

​```mermaid
sequenceDiagram
    participant U as User
    participant C as Client App
    participant GW as API Gateway
    participant A as Auth Service
    participant DB as Users DB

    U->>C: Enter email + password
    C->>GW: POST /register
    GW->>A: CreateUser
    A->>DB: Check email exists
    DB-->>A: Email already registered
    A-->>GW: 409 Conflict
    GW-->>C: 409 + error body
    C-->>U: "Email already registered. Sign in?"
​```

### Error: SendGrid down

If SendGrid is unavailable:
1. Email Worker retries 5× with exponential backoff
2. After 5 failures, the message moves to a dead letter queue
3. Alert fires: `email_dlq_depth > 0`
4. User remains in `pending` status
5. When SendGrid recovers, manually reprocess the DLQ or the user
   requests a resend

### Race condition: double submit

If the user clicks register twice:
1. First request creates the user, publishes the email event
2. Second request hits the idempotency key (same key from client)
3. Returns the cached response from the first request
4. Only one email is sent
```

**Why this works**: shows happy path + one error path (duplicate
email) + one operational degradation (SendGrid down) + one race
condition (double submit). Each scenario gets its own diagram or
prose block. Race condition explicitly named — operators need to
know this exists.

---

## Example 4: Deployment Topology

**Scenario**: Multi-region active-passive system with cross-region
replication.

```markdown
## Production topology

### Overview

Multi-region active-passive. Primary in `us-east-1`, standby in
`eu-west-1`. RPO: 5 minutes. RTO: 15 minutes.

​```mermaid
graph TB
    subgraph "us-east-1 (Primary)"
        DNS[Route53] --> ALB1[ALB]
        ALB1 --> API1a[API 1a]
        ALB1 --> API1b[API 1b]
        API1a --> DB1[(RDS Primary)]
        API1b --> DB1
        API1a --> CACHE1[(ElastiCache)]
        API1b --> CACHE1
        API1a --> NATS1[NATS]
        API1b --> NATS1
    end

    subgraph "eu-west-1 (Standby)"
        ALB2[ALB] --> API2a[API 1a]
        ALB2 --> API2b[API 1b]
        API2a --> DB2[(RDS Replica)]
        API2b --> DB2
        API2a --> CACHE2[(ElastiCache)]
        API2b --> CACHE2
        API2a --> NATS2[NATS]
        API2b --> NATS2
    end

    DB1 -.->|Async replication| DB2
    NATS1 -.->|Mirror| NATS2
​```

### Instance sizes

| Component | Primary | Standby | Scaling trigger |
|-----------|---------|---------|-----------------|
| API | 4× c6i.large | 2× c6i.large | CPU > 70% |
| RDS | db.r6g.xlarge | db.r6g.large | Storage > 80% |
| ElastiCache | cache.r6g.large | cache.r6g.large | Memory > 70% |
| NATS | 3× t3.medium | 3× t3.medium | Fixed |

### Failover procedure

See runbook: `runbooks/db-failover.md` (devops-team).

Brief:
1. Update Route53 health check to fail primary
2. Promote RDS replica in standby region
3. Scale standby API to match primary capacity
4. Verify application health
5. Update status page

### Data replication

- RDS: asynchronous replication, lag typically <1s
- ElastiCache: NOT replicated. Standby cache warms on demand.
- File storage (S3): cross-region replication enabled.
- NATS: mirror streams replicate messages. Consumer state is NOT
  replicated.

### Known limitations

- Failover causes ~5 minutes of write unavailability
- ElastiCache cold start in standby causes higher latency for the
  first requests after failover
- NATS consumer state is lost during failover. Consumers reprocess
  from last checkpoint.
```

**Why this works**: regions in subgraphs show the boundary clearly.
Instance table is concrete (specific instance types, scaling
triggers). Replication policy is explicit per data store, including
what is NOT replicated (ElastiCache, NATS consumer state). Known
limitations are honest — operators read this first during
incidents.

---

## Example 5: Security Model

**Scenario**: A fintech company documenting their security
architecture for a SOC 2 audit.

```markdown
## Security architecture

### Trust boundaries

​```mermaid
graph LR
    EXT[Internet] -->|TLS 1.3| WAF[Cloudflare WAF]
    WAF -->|TLS 1.3| LB[AWS ALB]
    LB -->|mTLS| API[API Gateway]
    API -->|mTLS| SVC[Internal Services]
    SVC -->|TLS| DB[(PostgreSQL)]
    SVC -->|TLS| CACHE[(Redis)]
​```

### Authentication

| Layer | Method | Details |
|-------|--------|---------|
| Client → WAF | None | DDoS protection only |
| Client → API | JWT | RS256, 1-hour expiry, issued by Auth Service |
| Service → Service | mTLS | Certs from internal CA, 90-day expiry |
| Service → DB | Password + TLS | IAM authentication for RDS |
| Service → Cache | Password + TLS | Redis AUTH |

### Authorization

- RBAC with roles: `customer`, `support`, `admin`, `system`
- Permissions checked at API Gateway (coarse) and service level (fine)
- Admin actions require MFA and are logged to immutable audit store

### Data classification

| Class | Examples | Storage | Encryption |
|-------|----------|---------|------------|
| Public | Marketing content | S3 | SSE-S3 |
| Internal | System logs | S3, PostgreSQL | SSE-S3, AES-256 |
| Confidential | Customer profiles | PostgreSQL | AES-256 at rest, TLS in transit |
| Restricted | SSN, card tokens | PostgreSQL, Vault | AES-256-GCM, field-level encryption |

### Network segmentation

- Public subnet: ALB only
- Private subnet A: API Gateway, application services
- Private subnet B: databases, cache
- VPC endpoints for AWS services (S3, Secrets Manager)
- No direct internet access from private subnets

### Incident response

| Severity | Criteria | Response time | Escalation |
|----------|----------|---------------|------------|
| P1 | Data breach, payment system down | 15 min | CTO + Legal |
| P2 | Auth bypass, partial outage | 1 hour | Engineering Lead |
| P3 | Performance degradation | 4 hours | On-call Engineer |
| P4 | Minor bug, doc issue | 24 hours | Next business day |
```

**Why this works**: trust boundary diagram shows the layered defense
from internet down to databases. Each layer's authentication is
explicit. Data classification table maps classes to storage and
encryption — this is what auditors check first. Incident response
table integrates security ownership with the on-call rotation.

## Sources

- [Trong-Tra/agent-skills `documentation-specialist`](https://github.com/Trong-Tra/agent-skills/tree/main/documentation-specialist) `architecture/examples.md` — Examples 1, 3, 4, 5 adapted from corresponding Examples 1, 4, 5, 6
- [C4 model](https://c4model.com/) — system context (Example 1) follows C4 Level 1 conventions
- `standards/architecture-doc-structure.md` — required-fields rules referenced in each example annotation
