#!/usr/bin/env python3
"""Port v1 battle-tested scenarios to v2 - these SHOULD break something!"""

import subprocess
import time
import json
from datetime import datetime

class V1BattleTestRunner:
    def __init__(self):
        self.results = []
        self.start_time = datetime.now()
    
    def run_v1_scenario(self, test_num: int, name: str, conversation: list, expected_behavior: str, difficulty: str):
        """Run a v1-style multi-turn conversation."""
        print(f"\n{'⚔️'*80}")
        print(f"V1 BATTLE TEST {test_num}: {name}")
        print(f"DIFFICULTY: {difficulty}")
        print(f"{'⚔️'*80}")
        print(f"Conversation: {conversation}")
        print(f"Expected: {expected_behavior}")
        print(f"{'⚔️'*80}")
        
        test_start = time.time()
        
        # Build input sequence
        input_sequence = "\n".join(conversation) + "\nexit\n"
        
        try:
            process = subprocess.Popen(
                ['python', 'cli.py'],
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                cwd='.'
            )
            
            stdout, stderr = process.communicate(input=input_sequence, timeout=180)  # 3 minute timeout
            test_duration = time.time() - test_start
            timeout_occurred = False
            
        except subprocess.TimeoutExpired:
            process.kill()
            stdout, stderr = process.communicate()
            test_duration = 180.0
            timeout_occurred = True
            print("⏰ TIMEOUT: Process killed after 3 minutes")
        
        # Analyze results
        result = {
            "test_num": test_num,
            "name": name,
            "conversation": conversation,
            "expected": expected_behavior,
            "difficulty": difficulty,
            "duration": test_duration,
            "timeout": timeout_occurred,
            "stdout": stdout,
            "stderr": stderr,
            "analysis": {}
        }
        
        # Count conversation turns
        turns = len([turn for turn in conversation if turn.strip()])
        result["analysis"]["conversation_turns"] = turns
        
        # Analyze conversation handling
        agent_responses = stdout.count("🤖 Agent:")
        result["analysis"]["agent_responses"] = agent_responses
        
        # Check for conversation state bugs
        if turns > agent_responses + 1:  # +1 for welcome message
            result["analysis"]["missing_responses"] = True
        
        # Detailed outcome analysis
        if timeout_occurred:
            result["outcome"] = "TIMEOUT - Process killed"
            result["success"] = False
        elif "✅ Report generated!" in stdout:
            result["outcome"] = "SUCCESS - Report Generated"
            result["success"] = True
        elif "I need some clarifications:" in stdout or "clarifications:" in stdout.lower():
            result["outcome"] = "CLARIFICATION - Asked for more info"
            result["success"] = True  # This might be correct behavior
        elif "Failed to implement strategy" in stdout:
            result["outcome"] = "IMPLEMENTATION_FAILED - Code generation failed"
            result["success"] = False
        elif "👋 Goodbye!" in stdout and len(stdout.split('\n')) < 10:
            result["outcome"] = "EARLY_EXIT - Conversation ended prematurely"
            result["success"] = False
        elif "[DEBUG]" in stdout:
            result["outcome"] = "DEBUG_ERROR - Implementation error"
            result["success"] = False
        else:
            result["outcome"] = "UNKNOWN - Unexpected behavior"
            result["success"] = False
        
        # Extract specific analysis
        if "[DEBUG]" in stdout:
            debug_lines = [line for line in stdout.split('\n') if '[DEBUG]' in line]
            result["analysis"]["debug_errors"] = debug_lines[:2]  # First 2 errors only
        
        if "Full report:" in stdout:
            for line in stdout.split('\n'):
                if "Full report:" in line:
                    result["analysis"]["report_path"] = line.split("Full report:")[-1].strip()
        
        # Multi-turn conversation analysis
        if turns > 1:
            result["analysis"]["multi_turn"] = True
            # Check if system handled state changes
            state_change_keywords = ["change", "instead", "actually", "make it", "let's do"]
            has_state_changes = any(keyword in " ".join(conversation).lower() for keyword in state_change_keywords)
            if has_state_changes:
                result["analysis"]["has_state_changes"] = True
        
        # Print results
        print(f"Duration: {test_duration:.1f}s")
        print(f"Turns: {turns} | Agent Responses: {agent_responses}")
        print(f"Outcome: {result['outcome']}")
        
        if result["success"]:
            print("✅ PASSED")
        else:
            print("❌ FAILED")
            
        print(f"\nOutput Preview:\n{stdout[:600]}{'...' if len(stdout) > 600 else ''}")
        if stderr:
            print(f"\nErrors Preview:\n{stderr[:200]}{'...' if len(stderr) > 200 else ''}")
        
        self.results.append(result)
        time.sleep(1)  # Brief pause between tests
        
        return result

def main():
    """Execute all v1 battle-tested scenarios."""
    runner = V1BattleTestRunner()
    
    print("⚔️ v2 vs v1 BATTLE TEST SUITE - BRING ON THE FAILURES!")
    print("=" * 80)
    print("These are battle-tested v1 scenarios that SHOULD break v2...")
    print("=" * 80)
    
    # Test 1: Multi-turn state changes (v1's bread and butter)
    runner.run_v1_scenario(
        1, "Multi-Turn State Changes",
        [
            "Buy and hold AAPL with $10k",
            "actually change ticker to TSLA", 
            "make it $50000",
            "use 2023 instead of 2024",
            "let's do RSI strategy instead"
        ],
        "Should handle multiple requirement changes gracefully",
        "HARD"
    )
    
    # Test 2: Confirmation workflow (v1 had explicit confirmation)
    runner.run_v1_scenario(
        2, "Confirmation Workflow",
        [
            "Buy SPY when RSI < 30, sell when RSI > 70, 2023, $10,000",
            "yes",
            "proceed with implementation"
        ],
        "Should proceed after confirmation (v1 behavior)",
        "MEDIUM"
    )
    
    # Test 3: Mixed proceed/change (v1's tricky case)
    runner.run_v1_scenario(
        3, "Mixed Proceed and Change",
        [
            "Test RSI strategy on AAPL in 2024 with $20k",
            "yes but change the period to 2023",
            "go ahead and explain the approach first"
        ],
        "Should handle mixed confirmation with changes",
        "HARD"
    )
    
    # Test 4: Uncertainty and questions (v1 handled these)
    runner.run_v1_scenario(
        4, "Uncertainty and Questions",
        [
            "Buy NVDA on momentum signals",
            "I'm not sure about this",
            "what indicators will you use?",
            "how does backtesting work?",
            "maybe we should try something else"
        ],
        "Should handle uncertainty and educational questions",
        "MEDIUM"
    )
    
    # Test 5: Reset and restart (v1 workflow)
    runner.run_v1_scenario(
        5, "Reset and Restart",
        [
            "Buy and hold AAPL in 2024 with $10k",
            "no",
            "reset everything", 
            "let's start over",
            "Buy SPY with RSI strategy in 2023 with $30k"
        ],
        "Should handle reset/restart workflow",
        "MEDIUM"
    )
    
    # Test 6: Complex multi-asset validation (from v1 validation script)
    runner.run_v1_scenario(
        6, "Multi-Asset Validation",
        [
            "Rotate between GLD and SPY based on momentum, 2020-2024, $50k"
        ],
        "Should block with clarifications (v1 validation behavior)",
        "EASY"
    )
    
    # Test 7: Vague strategy clarification (v1 validation)
    runner.run_v1_scenario(
        7, "Vague Strategy Clarification",
        [
            "Buy SPY on dips in 2024 with $20k"
        ],
        "Should ask for numeric dip definition",
        "EASY"
    )
    
    # Test 8: Contradictory logic (v1 edge case)
    runner.run_v1_scenario(
        8, "Contradictory Logic",
        [
            "Buy when RSI > 70 and < 30 simultaneously, SPY, 2023, $10k"
        ],
        "Should ask to resolve contradiction",
        "MEDIUM"
    )
    
    # Test 9: Unsupported features (v1 handled this)
    runner.run_v1_scenario(
        9, "Unsupported Features",
        [
            "Options iron condor on SPY, 2024, $10k"
        ],
        "Should explain unsupported and suggest alternatives",
        "EASY"
    )
    
    # Test 10: Multi-turn clarification (v1's strength)
    runner.run_v1_scenario(
        10, "Multi-Turn Clarification",
        [
            "Buy SPY on dips",
            "Buy SPY when price drops 5% below 10-day EMA, sell on cross back above; 2023; $10k",
            "proceed"
        ],
        "Should handle vague->specific->proceed workflow",
        "HARD"
    )
    
    # Generate comprehensive analysis
    total_duration = time.time() - runner.start_time.timestamp()
    successful_tests = sum(1 for r in runner.results if r["success"])
    failed_tests = [r for r in runner.results if not r["success"]]
    multi_turn_tests = [r for r in runner.results if r["analysis"].get("multi_turn")]
    state_change_tests = [r for r in runner.results if r["analysis"].get("has_state_changes")]
    
    print(f"\n{'⚔️'*80}")
    print(f"V1 BATTLE TEST SUITE COMPLETE")
    print(f"{'⚔️'*80}")
    print(f"Total Duration: {total_duration:.1f}s")
    print(f"Success Rate: {successful_tests}/{len(runner.results)} ({successful_tests/len(runner.results)*100:.1f}%)")
    
    # Conversation analysis
    print(f"\n📊 CONVERSATION ANALYSIS:")
    print(f"Multi-turn tests: {len(multi_turn_tests)}/{len(runner.results)}")
    print(f"State change tests: {len(state_change_tests)}/{len(runner.results)}")
    
    # Detailed failure analysis
    if failed_tests:
        print(f"\n💥 FAILURES FOUND ({len(failed_tests)}):")
        for test in failed_tests:
            print(f"  ❌ Test {test['test_num']}: {test['name']}")
            print(f"     Difficulty: {test['difficulty']} | Outcome: {test['outcome']}")
            if "debug_errors" in test["analysis"]:
                print(f"     Error: {test['analysis']['debug_errors'][0] if test['analysis']['debug_errors'] else 'Unknown'}")
    
    # State management analysis
    state_failures = [r for r in failed_tests if r["analysis"].get("has_state_changes")]
    if state_failures:
        print(f"\n🔄 STATE MANAGEMENT FAILURES ({len(state_failures)}):")
        for test in state_failures:
            print(f"  🔄 Test {test['test_num']}: {test['name']}")
            print(f"     This suggests v2 might not handle state changes as well as v1")
    
    # Multi-turn conversation failures
    multi_turn_failures = [r for r in failed_tests if r["analysis"].get("multi_turn")]
    if multi_turn_failures:
        print(f"\n💬 MULTI-TURN CONVERSATION FAILURES ({len(multi_turn_failures)}):")
        for test in multi_turn_failures:
            print(f"  💬 Test {test['test_num']}: {test['name']}")
            print(f"     Turns: {test['analysis']['conversation_turns']} | Responses: {test['analysis']['agent_responses']}")
    
    # Save detailed results
    with open('v1_battle_results.json', 'w') as f:
        json.dump({
            "timestamp": runner.start_time.isoformat(),
            "total_duration": total_duration,
            "success_rate": successful_tests/len(runner.results),
            "multi_turn_success": len([r for r in multi_turn_tests if r["success"]]) / len(multi_turn_tests) if multi_turn_tests else 0,
            "state_change_success": len([r for r in state_change_tests if r["success"]]) / len(state_change_tests) if state_change_tests else 0,
            "tests": runner.results
        }, f, indent=2)
    
    print(f"\nDetailed results saved to: v1_battle_results.json")
    
    # Final battle summary
    print(f"\n⚔️ BATTLE SUMMARY:")
    for i, result in enumerate(runner.results, 1):
        status = "✅" if result["success"] else "❌"
        difficulty_emoji = {"EASY": "🟢", "MEDIUM": "🟡", "HARD": "🔴"}[result["difficulty"]]
        duration = result["duration"]
        outcome = result["outcome"]
        turns = result["analysis"]["conversation_turns"]
        print(f"Test {i}: {status} {difficulty_emoji} {outcome} ({turns} turns, {duration:.1f}s)")
    
    print(f"\n⚔️ BATTLE ANALYSIS COMPLETE!")
    if successful_tests == len(runner.results):
        print("🏆 v2 DOMINATED v1's battle tests - system is incredibly robust!")
        print("🎯 Need even MORE brutal tests to find failures!")
    else:
        print(f"💥 Found {len(failed_tests)} battle casualties - v1 scenarios exposed v2 weaknesses!")
        print("🔧 Time to analyze and strengthen v2!")

if __name__ == "__main__":
    main()
