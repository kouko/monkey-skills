# Spec Writing Protocol

Write implementation-ready technical specs (TECH-SPEC.md).
If a PRODUCT-SPEC.md exists, use it as the primary input.
The TECH-SPEC.md should trace back to PRODUCT-SPEC.md sections.

A good tech spec lets a developer (or agent)
start coding by reading only this document.

## Phase 1: Scope & Constraints

1. Clarify project type and delivery form:
   - CLI tool / Desktop app / Web app / API service / Library / Mobile app
2. Define Goals (what it does) and Non-Goals (what it explicitly won't do)
3. Document hard constraints (language, platform, deployment, privacy, performance)

## Phase 2: Architecture

1. Choose and document the technical approach with rationale (why this, not alternatives)
2. Draw system architecture (ASCII or Mermaid) showing components and data flow
3. Document external dependencies with versions, licenses, and acquisition method

Project-type specifics:
- CLI: packaging strategy, distribution method
- Web app / API: deployment target, scaling model, auth strategy
- Mobile / Desktop: platform targets, native vs cross-platform, update mechanism
- Library: public API surface, supported runtimes, versioning policy

## Phase 3: Module Design

For each module:
1. Define input format (types, shapes, ranges, examples)
2. Define output format (types, examples)
3. List external dependencies (APIs, libraries, models)
4. Specify error handling (what can fail, how to recover)
5. Address edge cases (empty input, missing files, malformed data, timeouts)
6. Mark readiness: READY / PARTIAL / BLOCKED

Project-type specifics:
- CLI: flags, config keys, defaults, environment variables
- API service: endpoints, request/response schemas, status codes, rate limits
- Web app: routes, state management, component hierarchy
- Library: public types, function signatures, error types

## Phase 4: Interface & Data Flow

1. Define user-facing interface:
   - CLI: flags, subcommands, config file format, output formats
   - API: endpoint paths, HTTP methods, auth headers, pagination
   - Web: pages/routes, forms, user flows
   - Library: exported functions, types, configuration
2. Document end-to-end data flow (input → processing → output)
3. Cross-reference: every interface element must trace to a module

## Phase 5: Testing & Verification

1. Testing strategy per module (unit / integration / e2e)
2. Key edge cases to test
3. Acceptance criteria (when is it "done"?)

## Rules

- Self-contained: reading the spec alone must be enough to implement
- Every technical decision includes rationale (why, not just what)
- Non-Goals are as important as Goals — explicitly exclude scope
- Use concrete examples (sample input/output) over abstract descriptions
- Mark each module READY/PARTIAL/BLOCKED — no ambiguity about what's implementable
- Keep structure flat — avoid deeply nested sections

## Output Structure

Adapt section numbering and depth to the project. Typical structure:

1. Project Overview (Goals, Non-Goals, Constraints)
2. Technical Architecture (approach, diagram, dependencies)
3. Module Design (per module: I/O, deps, errors, edge cases, readiness)
4. Interface Definition (varies by project type)
5. Data Flow (end-to-end pipeline)
6. External Dependencies (versions, licenses, acquisition)
7. Testing Strategy (per module + acceptance criteria)
