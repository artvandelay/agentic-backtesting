#!/usr/bin/env bash
set -euo pipefail

run_case() {
  local title="$1"
  local convo="$2"
  echo "=============================="
  echo "CASE: $title"
  echo "------------------------------"
  printf "%b" "$convo" | nlbt | sed -e 's/\r//g' | tail -n +1
  echo
}

# 1) Clear single-ticker (should proceed to READY)
run_case "single_ticker_rsi" $'Buy SPY when RSI < 30, sell when RSI > 70, 2023, $10,000\nproceed\nexit\n'

# 2) Multi-ticker (should block with clarifications)
run_case "multi_ticker_block" $'Rotate between GLD and SPY based on momentum, 2020-2024, $50k\nexit\n'

# 3) Vague trigger (should ask for numeric dip definition)
run_case "vague_dip" $'Buy SPY on dips in 2024 with $20k\nexit\n'

# 4) Contradictory rules (should ask to resolve)
run_case "contradictory_rsi" $'Buy when RSI > 70 and < 30 simultaneously, SPY, 2023, $10k\nexit\n'

# 5) Unsupported features (options)
run_case "unsupported_options" $'Options iron condor on SPY, 2024, $10k\nexit\n'

# 6) Multi-turn clarity: start vague, then clarify fully
run_case "multi_turn_clarity" $'Buy SPY on dips\nBuy SPY when price drops 5% below 10-day EMA, sell on cross back above; 2023; $10k\nproceed\nexit\n'

echo "All scenarios executed. Review outputs above for validation prompts and READY transitions."

