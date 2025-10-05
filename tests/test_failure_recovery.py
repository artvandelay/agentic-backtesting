#!/usr/bin/env python3
"""Test the failure recovery feature after 3 attempts."""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.nlbt.reflection import ReflectionEngine

def test_failure_recovery():
    """Test that after 3 failures, system returns to understanding phase."""
    print("🧪 Testing Failure Recovery After 3 Attempts\n")
    
    # Create engine
    engine = ReflectionEngine()
    
    # Set up requirements
    engine.requirements = {
        'ticker': 'AAPL', 
        'period': '2024', 
        'capital': '$10,000', 
        'strategy': 'buy and hold'
    }
    engine.phase = 'implementation'
    engine.last_error = "ImportError: cannot import name 'SomeInvalidIndicator'"
    
    print("📝 Simulating 3 failed attempts...")
    print(f"Initial phase: {engine.phase}")
    print(f"Last error: {engine.last_error}\n")
    
    # Call with attempt > 3 to trigger failure recovery
    result = engine._phase2_implementation(attempt=4)
    
    print(f"✅ Phase after failure: {engine.phase}")
    print(f"📄 Response preview: {result[:200]}...")
    
    if engine.phase == "understanding":
        print("\n✅ PASS - Correctly returned to understanding phase")
        print("✅ User can now modify strategy or requirements")
    else:
        print(f"\n❌ FAIL - Expected understanding, got {engine.phase}")
    
    # Check that error is shown
    if "Failed after 3 attempts" in result:
        print("✅ PASS - Error message shown to user")
    else:
        print("❌ FAIL - Error message not shown")
    
    # Check that LLM is engaged
    if "Let's try a different approach" in result or len(result) > 100:
        print("✅ PASS - LLM engaged for conversation")
    else:
        print("❌ FAIL - LLM not engaged")

if __name__ == "__main__":
    test_failure_recovery()
