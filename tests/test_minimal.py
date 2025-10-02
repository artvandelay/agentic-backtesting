#!/usr/bin/env python3
"""Test minimal reflection engine."""

import sys
sys.path.insert(0, 'src')

from nlbt.reflection import ReflectionEngine

print("Testing Minimal Reflection Engine")
print("=" * 50)

# Test 1: Creation
print("\n✓ Test 1: Create engine")
engine = ReflectionEngine()
assert engine.phase == "understanding"
print(f"  Phase: {engine.phase}")

# Test 2: History
print("\n✓ Test 2: History tracking")
engine.history.append("Test message")
assert len(engine.history) == 1
print(f"  History: {len(engine.history)} items")

# Test 3: Requirements
print("\n✓ Test 3: Requirements")
engine.requirements = {"ticker": "AAPL", "period": "2024"}
formatted = engine._format_requirements()
assert "AAPL" in formatted
print(f"  {formatted}")

# Test 4: Sandbox
print("\n✓ Test 4: Sandbox execution")
from nlbt.sandbox import Sandbox
sandbox = Sandbox()
result = sandbox.run("x = 1 + 1\nprint(x)")
assert result["success"]
print(f"  Output: {result['output'].strip()}")

# Test 5: LLM client
print("\n✓ Test 5: LLM client")
from nlbt.llm import LLM
llm = LLM()
print(f"  Model: {llm.model}")

print("\n" + "=" * 50)
print("✅ All structural tests passed!")
print("\nReady to test with actual LLM:")
print("  python -m nlbt.cli")

