#!/bin/bash
# Setup script for NLBT

set -e

echo "🚀 Setting up NLBT - Agentic Natural Language Backtesting Sandbox"

# Check if Python 3.9+ is available
python_version=$(python3 -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')")
required_version="3.9"

if [ "$(printf '%s\n' "$required_version" "$python_version" | sort -V | head -n1)" != "$required_version" ]; then
    echo "❌ Python 3.9+ is required. Found: $python_version"
    exit 1
fi

echo "✅ Python $python_version found"

# Install dependencies
echo "📦 Installing dependencies..."
pip install -e .

# Check if llm CLI is available
if ! command -v llm &> /dev/null; then
    echo "⚠️  llm CLI not found. Installing..."
    pip install llm
fi

echo "✅ llm CLI available"

# Create .env file if it doesn't exist
if [ ! -f .env ]; then
    echo "📝 Creating .env file..."
    cp env.example .env
    echo "✅ .env file created. Please edit it to configure your LLM model."
else
    echo "✅ .env file already exists"
fi

# Create necessary directories
echo "📁 Creating directories..."
mkdir -p reports cursor_chats .cache

echo "✅ Setup complete!"
echo ""
echo "Next steps:"
echo "1. Edit .env to configure your LLM model"
echo "2. Configure llm CLI with your provider:"
echo "   llm keys set openrouter"
echo "   llm models default openrouter/anthropic/claude-3.5-sonnet"
echo "3. Start chatting: nlbt chat"
echo ""
echo "Example usage:"
echo "  nlbt chat"
echo "  python scripts/example_usage.py"
