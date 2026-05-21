#!/usr/bin/env bats
#
# Verifies salesforce-toolkit/.mcp.json schema:
#   - Top-level `mcpServers` envelope (Claude Code plugin MCP loader contract)
#   - stdio mode + bash launcher shim (Decision Q1 Path D)
#   - toolsets default = data (Decision Q2; v0.1.0 dropped `metadata` after
#     dogfood confirmed `metadata` toolset includes destructive `deploy_metadata`
#     tool, breaking the "read-only" claim)
#   - args include ${CLAUDE_PLUGIN_ROOT} placeholder + sf-mcp-launcher.sh shim
#
# Scope: file structure only. Launcher runtime behavior is T4's scope.

MCP_JSON="${BATS_TEST_DIRNAME}/../.mcp.json"

setup() {
  command -v jq >/dev/null 2>&1 || skip "jq not available"
}

@test ".mcp.json exists" {
  [ -f "$MCP_JSON" ]
}

@test ".mcp.json is valid JSON" {
  run jq empty "$MCP_JSON"
  [ "$status" -eq 0 ]
}

@test ".mcp.json has top-level mcpServers object envelope" {
  run jq -e '.mcpServers | type == "object"' "$MCP_JSON"
  [ "$status" -eq 0 ]
}

@test "salesforce server type is stdio and command is bash" {
  run jq -e '.mcpServers.salesforce.type == "stdio" and .mcpServers.salesforce.command == "bash"' "$MCP_JSON"
  [ "$status" -eq 0 ]
}

@test "salesforce.args[0] points at sf-mcp-launcher.sh shim" {
  run jq -e '.mcpServers.salesforce.args[0] | contains("sf-mcp-launcher.sh")' "$MCP_JSON"
  [ "$status" -eq 0 ]
}

@test "salesforce.args[0] uses \${CLAUDE_PLUGIN_ROOT} placeholder" {
  # Boundary: verifies placeholder string literal is present in .mcp.json.
  # Runtime expansion is Claude Code MCP platform contract (out of test scope).
  run jq -e '.mcpServers.salesforce.args[0] | contains("${CLAUDE_PLUGIN_ROOT}")' "$MCP_JSON"
  [ "$status" -eq 0 ]
}

@test "salesforce.args contains --toolsets data pair (read-only)" {
  run jq -e '.mcpServers.salesforce.args | index("--toolsets") as $i | .[$i+1] == "data"' "$MCP_JSON"
  [ "$status" -eq 0 ]
}

@test "salesforce.args contains --orgs DEFAULT_TARGET_ORG pair" {
  run jq -e '.mcpServers.salesforce.args | index("--orgs") as $i | .[$i+1] == "DEFAULT_TARGET_ORG"' "$MCP_JSON"
  [ "$status" -eq 0 ]
}
