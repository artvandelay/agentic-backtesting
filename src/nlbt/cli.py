"""Minimal CLI for reflection backtesting."""

import sys
from .reflection import ReflectionEngine
from rich.console import Console
from rich.panel import Panel


def main():
    """Run the backtesting assistant."""
    model = sys.argv[1] if len(sys.argv) > 1 else None
    engine = ReflectionEngine(model)
    console = Console()
    header = (
        f"[bold cyan]🧠 Backtesting Assistant (WIP)[/bold cyan]\n"
        f"[dim]Chat model:[/dim] {engine.llm.model}\n"
        f"[dim]Code model:[/dim] {engine.code_llm.model} (strong model for implementation)\n\n"
        "[bold]📋 How it works:[/bold]\n"
        "  • Phase 1 (🔍 Understanding): Ask until info is complete\n"
        "  • Phase 2 (⚙️ Implementation): Generate, test, refine code\n"
        "  • Phase 3 (📊 Reporting): Produce a professional report\n\n"
        "[bold]⚠️ Current limitations:[/bold]\n"
        "  • Single ticker strategies work best (multi-asset may fail)\n"
        "  • Uses Yahoo Finance data (US stocks, ETFs, crypto with -USD suffix)\n"
        "  • Max 3 code generation attempts per strategy\n"
        "  • Requires LLM API access and credits\n"
        "  • Generated code runs locally (trusted environment only)\n\n"
        "[bold]💬 You can:[/bold]\n"
        "  • Describe your strategy (e.g. 'Buy SPY when RSI < 30')\n"
        "  • Type 'info' for current phase and requirements\n"
        "  • Type 'debug' for internal state\n"
        "  • Type 'exit' to quit\n\n"
        "🚀 Ready! Describe your single-ticker trading strategy..."
    )
    console.print(Panel.fit(header, title="NLBT", border_style="cyan"))
    
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
                console.print("\n[bold]🐛 Debug Info:[/bold]")
                console.print(f"Phase: {engine.phase}")
                console.print(f"History length: {len(engine.history)}")
                if engine.history:
                    console.print("Last 3 history items:")
                    for item in engine.history[-3:]:
                        console.print(f"  {item}")
                if engine.requirements:
                    console.print(f"Requirements: {engine.requirements}")
                if engine.code:
                    console.print(f"\n📝 Last Code Generated:\n{engine.code[:500]}...")
                if engine.last_error:
                    console.print(f"\n❌ Last Error:\n{engine.last_error}")
                if engine.results:
                    console.print(f"\n✅ Last Results:\n{engine.results[:300]}...")
                if getattr(engine, 'last_validation', None) is not None:
                    console.print(f"\n🔎 Last Validation:\n{engine.last_validation}")
                console.print()
                continue
            
            # Process
            phase_emoji = {
                "understanding": "🔍",
                "ready_to_implement": "✅",
                "implementation": "⚙️", 
                "reporting": "📊",
                "complete": "✅"
            }
            
            with Console().status(f"{phase_emoji.get(engine.phase, '🤔')} Processing...", spinner="dots"):
                response = engine.chat(user_input)
            Console().print(f"\n🤖 {response}\n")

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

