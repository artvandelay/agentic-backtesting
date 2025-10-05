#!/usr/bin/env python3
"""Comprehensive test of the simplified confirmation workflow."""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.nlbt.reflection import ReflectionEngine

def test_comprehensive_scenarios():
    """Test various realistic user scenarios."""
    print("🧪 Comprehensive Testing of Simplified Workflow\n")
    
    scenarios = [
        # Basic proceed cases
        {
            "name": "Simple Yes",
            "input": "yes",
            "expected_phase": "complete",
            "should_generate_code": True
        },
        {
            "name": "Casual Go", 
            "input": "go for it",
            "expected_phase": "complete",
            "should_generate_code": True
        },
        {
            "name": "Formal Proceed",
            "input": "proceed with implementation",
            "expected_phase": "complete", 
            "should_generate_code": True
        },
        
        # Change scenarios
        {
            "name": "Change Ticker",
            "input": "change ticker to TSLA",
            "expected_phase": "understanding",
            "should_generate_code": False
        },
        {
            "name": "Change Period",
            "input": "actually use 2023 instead",
            "expected_phase": "understanding",
            "should_generate_code": False
        },
        {
            "name": "Change Capital",
            "input": "make it $50000",
            "expected_phase": "understanding", 
            "should_generate_code": False
        },
        {
            "name": "Change Strategy",
            "input": "let's do RSI strategy instead",
            "expected_phase": "understanding",
            "should_generate_code": False
        },
        
        # Question scenarios
        {
            "name": "Explain Request",
            "input": "explain how this works",
            "expected_phase": "understanding",
            "should_generate_code": False
        },
        {
            "name": "What Question",
            "input": "what indicators will you use?",
            "expected_phase": "understanding",
            "should_generate_code": False
        },
        {
            "name": "How Question", 
            "input": "how does backtesting work?",
            "expected_phase": "understanding",
            "should_generate_code": False
        },
        
        # Uncertain responses
        {
            "name": "Uncertainty",
            "input": "I'm not sure about this",
            "expected_phase": "understanding",
            "should_generate_code": False
        },
        {
            "name": "Maybe",
            "input": "maybe we should try something else",
            "expected_phase": "understanding",
            "should_generate_code": False
        },
        {
            "name": "Wait",
            "input": "wait let me think",
            "expected_phase": "understanding",
            "should_generate_code": False
        },
        
        # Edge cases
        {
            "name": "No",
            "input": "no",
            "expected_phase": "understanding",
            "should_generate_code": False
        },
        {
            "name": "Reset",
            "input": "reset everything",
            "expected_phase": "understanding", 
            "should_generate_code": False
        },
        {
            "name": "Start Over",
            "input": "let's start over",
            "expected_phase": "understanding",
            "should_generate_code": False
        },
        
        # Mixed keywords (tricky cases)
        {
            "name": "Yes But Change",
            "input": "yes but change the period to 2023",
            "expected_phase": "understanding",  # Should go to understanding because it's not pure "yes"
            "should_generate_code": False
        },
        {
            "name": "Go Explain",
            "input": "go ahead and explain the approach first",
            "expected_phase": "understanding",  # Should go to understanding because it's not pure "go"
            "should_generate_code": False
        }
    ]
    
    passed = 0
    failed = 0
    
    for scenario in scenarios:
        print(f"📝 TEST: {scenario['name']}")
        print(f"Input: '{scenario['input']}'")
        print(f"Expected: {scenario['expected_phase']}")
        
        # Create fresh engine for each test
        engine = ReflectionEngine()
        engine.requirements = {
            'ticker': 'AAPL', 
            'period': '2024', 
            'capital': '$10,000', 
            'strategy': 'buy and hold'
        }
        engine.phase = 'ready_to_implement'
        
        try:
            result = engine._handle_implementation_confirmation(scenario['input'])
            actual_phase = engine.phase
            
            print(f"Actual: {actual_phase}")
            
            # Check phase
            if actual_phase == scenario['expected_phase']:
                print("✅ PASS - Correct phase")
                passed += 1
            else:
                print(f"❌ FAIL - Expected {scenario['expected_phase']}, got {actual_phase}")
                failed += 1
            
            # Check if code generation occurred (for proceed cases)
            if scenario['should_generate_code']:
                if "🔄 Attempt" in result or "Strategy:" in result:
                    print("✅ Code generation occurred as expected")
                else:
                    print("❌ Expected code generation but didn't happen")
            else:
                if "Got it! Let me help you with that" in result:
                    print("✅ Correctly went to understanding conversation")
                else:
                    print("❌ Expected understanding conversation")
            
        except Exception as e:
            print(f"❌ ERROR: {e}")
            failed += 1
            import traceback
            traceback.print_exc()
        
        print("-" * 80)
    
    print(f"\n🎯 SUMMARY: {passed} passed, {failed} failed")
    success_rate = (passed / (passed + failed)) * 100 if (passed + failed) > 0 else 0
    print(f"Success Rate: {success_rate:.1f}%")
    
    if failed == 0:
        print("🎉 ALL TESTS PASSED!")
    else:
        print(f"⚠️  {failed} tests need attention")

if __name__ == "__main__":
    test_comprehensive_scenarios()
