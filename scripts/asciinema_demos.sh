#!/usr/bin/env bash
set -euo pipefail

# Ensure asciinema is installed (Homebrew on macOS, fallback to cargo if available)
if ! command -v asciinema >/dev/null 2>&1; then
  if command -v brew >/dev/null 2>&1; then
    brew install asciinema || true
  fi
fi

mkdir -p reports/demos

# 1) Lucky demo (no LLM)
echo "[demos] recording lucky.cast"
asciinema rec -y reports/demos/lucky.cast -c "bash -lc 'printf \"lucky\\nexit\\n\" | nlbt'"

# 2) India-friendly run with Hindi summary and trades table
echo "[demos] recording reliance_hi.cast"
asciinema rec -y reports/demos/reliance_hi.cast -c "bash -lc 'printf \"Test RELIANCE strategy: Buy when RSI < 30, sell when RSI > 70; period 2023; capital ₹10,00,000; lang hi\\nyes\\nexit\\n\" | nlbt'"

echo "[demos] done. Files saved in reports/demos/"

