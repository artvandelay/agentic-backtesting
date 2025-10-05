#!/usr/bin/env python3
"""Test the simplified confirmation workflow like a user would."""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.nlbt.reflection import ReflectionEngine

def test_simplified_workflow():
    """Test the simplified confirmation workflow."""
    print("🧪 Testing Simplified Confirmation Workflow\n")
    
    # Create engine
    engine = ReflectionEngine()
    
    # Set up a ready state with requirements
    engine.requirements = {
        'ticker': 'AAPL', 
        'period': '2024', 
        'capital': '$10,000', 
        'strategy': 'buy and hold'
    }
    engine.phase = 'ready_to_implement'
    
    test_cases = [
        ("yes", "Should proceed to implementation"),
        ("go", "Should proceed to implementation"), 
        ("change ticker to TSLA", "Should go back to understanding"),
        ("explain how this works", "Should go back to understanding"),
        ("actually use 2023", "Should go back to understanding"),
        ("I'm not sure", "Should go back to understanding"),
        ("no", "Should go back to understanding"),
        ("reset", "Should go back to understanding")
    ]
    
    for user_input, expected in test_cases:
        print(f"📝 TEST: '{user_input}'")
        print(f"Expected: {expected}")
        
        # Reset to ready state
        engine.phase = 'ready_to_implement'
        
        try:
            result = engine._handle_implementation_confirmation(user_input)
            print(f"✅ Phase after: {engine.phase}")
            print(f"📄 Response preview: {result[:100]}...")
            
            if user_input in ["yes", "go"]:
                expected_phase = "implementation"
            else:
                expected_phase = "understanding"
                
            if engine.phase == expected_phase:
                print("✅ PASS - Correct phase transition")
            else:
                print(f"❌ FAIL - Expected {expected_phase}, got {engine.phase}")
                
        except Exception as e:
            print(f"❌ ERROR: {e}")
        
        print("-" * 60)

if __name__ == "__main__":
    test_simplified_workflow()
