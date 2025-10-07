#!/usr/bin/env python3
"""v2 CLI - Minimal interface for triplet architecture."""

import sys
sys.path.insert(0, '.')  # Add current dir to path

from src.engine import Engine


def main():
    """Run the v2 backtesting assistant."""
    print("🚀 NLBT v2 - Triplet Architecture")
    print("=" * 40)
    print("Describe your trading strategy (or 'exit' to quit)")
    print()
    
    engine = Engine()
    
    while True:
        try:
            user_input = input("💭 You: ").strip()
            
            if not user_input:
                continue
            
            if user_input.lower() in ["exit", "quit", "bye"]:
                print("\n👋 Goodbye!")
                break
            
            # Process through engine
            response = engine.process(user_input)
            print(f"\n🤖 Agent: {response}\n")
            
        except KeyboardInterrupt:
            print("\n\nUse 'exit' to quit")
            continue
        except EOFError:
            break
        except Exception as e:
            print(f"\n❌ Error: {e}\n")


if __name__ == "__main__":
    main()