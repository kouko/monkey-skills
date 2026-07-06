---
name: chrome-debug-port-ipv6-gotcha
description: A user's main Chrome can hold 127.0.0.1:9222 answering 404 while the fresh debug instance binds IPv6-only — chrome-devtools MCP dials IPv4, so fall back to puppeteer-core over the IPv6 WebSocket
type: gotcha
origin: PR #477 (ui-verification skill, live dogfood 2026-07-03)
---

When driving Chrome via its remote-debugging port for UI
verification: the user's already-running everyday Chrome can be the
process holding `127.0.0.1:9222`, answering plain HTTP 404 (it is
not a debug endpoint), while the freshly launched debug-enabled
Chrome instance binds to IPv6 (`::1`) only. The chrome-devtools MCP
client dials IPv4, so it reaches the wrong instance and fails.

**Why:** the failure looks like "debug port is up but broken" — the
port answers, just not from the browser you launched. Easy to burn
time debugging the wrong process.

**How to apply:** if `127.0.0.1:9222` answers 404, suspect a port
collision with the user's main Chrome. Check which process owns the
port, and connect to the debug instance over its IPv6 WebSocket
endpoint with `puppeteer-core` instead of the IPv4-dialing
chrome-devtools MCP.
