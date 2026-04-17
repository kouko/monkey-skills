#!/usr/bin/env sh
# investing-toolkit setup — install uv
#
# Priority:
#   1. uv already installed → skip
#   2. Homebrew available   → brew install uv
#   3. fallback             → official install script (curl)

set -e

# ── already installed? ──────────────────────────────────────────────────────
if command -v uv >/dev/null 2>&1; then
  echo "uv already installed: $(uv --version)"
  exit 0
fi

# ── Homebrew ─────────────────────────────────────────────────────────────────
if command -v brew >/dev/null 2>&1; then
  echo "Homebrew detected — installing uv via brew..."
  brew install uv
  echo "Done: $(uv --version)"
  exit 0
fi

# ── official install script (macOS / Linux fallback) ─────────────────────────
echo "Homebrew not found — installing uv via official script..."
curl -LsSf https://astral.sh/uv/install.sh | sh

echo ""
echo "uv installed to ~/.local/bin/uv"
echo "Restart your shell or run:  source ~/.zshrc  (or ~/.bashrc)"
