"""Minimal CLI for reflection backtesting."""

import sys
from .reflection import ReflectionEngine


def main():
    """Run the backtesting assistant."""
    model = sys.argv[1] if len(sys.argv) > 1 else None
    engine = ReflectionEngine(model)
    
    print("🧠 Backtesting Assistant")
    print(f"Chat model: {engine.llm.model}")
    print(f"Code model: {engine.code_llm.model} (strong model for implementation)")
    print()
    print("📋 How it works:")
    print("  Phase 1 (🔍 Understanding): I'll ask questions until I have complete info")
    print("  Phase 2 (⚙️ Implementation): I'll generate, test, and refine code")
    print("  Phase 3 (📊 Reporting): I'll create a professional analysis report")
    print()
    print("💬 You can:")
    print("  • Describe your strategy in plain English")
    print("  • Make changes anytime by saying 'actually...' or 'change...'")
    print("  • Type 'info' to see current phase and requirements")
    print("  • Type 'debug' if something goes wrong")
    print("  • Type 'exit' to quit")
    print()
    print("🚀 Ready! Describe your trading strategy...")
    
    while True:
        try:
            user_input = input("💭 You: ").strip()

            # Skip completely empty inputs or just prompts
            if not user_input:
                continue

            # Skip inputs that are just whitespace or newlines
            if len(user_input.replace(' ', '').replace('\n', '').replace('\t', '')) == 0:
                continue

            # Skip repeated empty prompts (defensive programming)
            if user_input == "💭 You:" or user_input.startswith("💭 You:"):
                continue
            
            if user_input.lower() in ["exit", "quit", "bye"]:
                print("\n👋 Goodbye!")
                break
            
            if user_input.lower() == "info":
                phase_info = {
                    "understanding": "🔍 Phase 1 - Gathering requirements and asking clarifying questions",
                    "ready_to_implement": "✅ Ready to implement - Waiting for your confirmation to proceed",
                    "implementation": "⚙️ Phase 2 - Generating Python code, testing, and refining",
                    "reporting": "📊 Phase 3 - Creating professional analysis report",
                    "complete": "✅ All phases complete - ready for new strategy"
                }
                
                print(f"\n📍 Current Phase: {phase_info.get(engine.phase, engine.phase)}")
                
                if engine.requirements:
                    print(f"\n📋 Requirements Gathered:")
                    for key, value in engine.requirements.items():
                        print(f"  • {key.title()}: {value}")
                
                if engine.phase == "understanding":
                    print(f"\n💬 What you can do:")
                    print(f"  • Answer my questions to provide missing info")
                    print(f"  • Say 'actually...' or 'change...' to modify requirements")
                    print(f"  • Provide more details about your strategy")
                elif engine.phase == "ready_to_implement":
                    print(f"\n💬 What you can do:")
                    print(f"  • Type 'yes', 'go', or 'proceed' to start implementation")
                    print(f"  • Type 'explain' for detailed implementation approach")
                    print(f"  • Type 'change [requirement]' to modify anything")
                elif engine.phase == "implementation":
                    print(f"\n💬 What you can do:")
                    print(f"  • Wait for code generation to complete")
                    print(f"  • Type 'debug' to see current progress")
                    print(f"  • Say 'change...' to modify requirements (restarts Phase 1)")
                elif engine.phase == "reporting":
                    print(f"\n💬 What you can do:")
                    print(f"  • Wait for report generation to complete")
                    print(f"  • The report will be saved automatically")
                else:
                    print(f"\n💬 What you can do:")
                    print(f"  • Start a new strategy by describing it")
                    print(f"  • Ask questions about the previous results")
                
                print()
                continue
            
            if user_input.lower() == "debug":
                print(f"\n🐛 Debug Info:")
                print(f"Phase: {engine.phase}")
                print(f"History length: {len(engine.history)}")
                if engine.history:
                    print(f"Last 3 history items:")
                    for item in engine.history[-3:]:
                        print(f"  {item}")
                if engine.requirements:
                    print(f"Requirements: {engine.requirements}")
                if engine.code:
                    print(f"\n📝 Last Code Generated:\n{engine.code[:500]}...")
                if engine.last_error:
                    print(f"\n❌ Last Error:\n{engine.last_error}")
                if engine.results:
                    print(f"\n✅ Last Results:\n{engine.results[:300]}...")
                print()
                continue
            
            # Process
            phase_emoji = {
                "understanding": "🔍",
                "ready_to_implement": "✅",
                "implementation": "⚙️", 
                "reporting": "📊",
                "complete": "✅"
            }
            
            print(f"\n{phase_emoji.get(engine.phase, '🤔')} Processing...", end="\r")
            sys.stdout.flush()
            
            response = engine.chat(user_input)

            print(" " * 60, end="\r")  # Clear processing line
            print(f"\n🤖 {response}\n")

            # Check if conversation is complete and handle accordingly
            if engine.phase == "complete":
                print("💡 Conversation completed! Ready for new strategy.\n")
            
        except KeyboardInterrupt:
            print("\n\nUse 'exit' to quit")
            continue
        except EOFError:
            break
        except Exception as e:
            print(f"\n❌ Error: {e}\n")


if __name__ == "__main__":
    main()

