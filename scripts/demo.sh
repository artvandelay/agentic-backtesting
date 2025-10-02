#!/bin/bash
# Quick demo script showing NLBT capabilities

echo "🎯 NLBT Demo - Natural Language Backtesting"
echo "==========================================="
echo ""

# Check if llm CLI is available
if ! command -v llm &> /dev/null; then
    echo "❌ Error: llm CLI not found. Please install it first:"
    echo "   pip install llm"
    exit 1
fi

# Check model
echo "📋 Available models:"
llm models list | head -5
echo ""

DEFAULT_MODEL=$(llm models default)
echo "✅ Using default model: $DEFAULT_MODEL"
echo ""

echo "🚀 Starting NLBT demo..."
echo ""
echo "Try these example queries:"
echo ""
echo "1. Simple Buy & Hold:"
echo "   > buy and hold Apple stock in 2024 with \$10,000"
echo ""
echo "2. Moving Average Crossover:"
echo "   > test a 50/200 day MA crossover on SPY for 2024 with \$25K"
echo ""
echo "3. Bollinger Bands:"
echo "   > backtest Tesla with Bollinger Bands strategy in 2024, \$15K"
echo ""
echo "4. RSI Strategy:"
echo "   > create RSI mean reversion strategy for NVDA: buy when RSI < 30, sell when > 70, 2024, \$20K"
echo ""
echo "5. Custom Multi-Indicator:"
echo "   > backtest Microsoft: buy when MACD crosses up AND RSI < 50, sell when MACD crosses down, 2024, \$50K"
echo ""
echo "---"
echo ""

# Launch the CLI
nlbt chat --model $DEFAULT_MODEL

