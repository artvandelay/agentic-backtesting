# Changelog

All notable changes to NLBT (Natural Language Backtesting) will be documented in this file.

## [0.3.0] - 2025-10-07

### 🚀 Major Features - "Extreme Promptification"

**Complete architectural overhaul** replacing hardcoded logic with 8 LLM-powered intelligence features:

#### Added
- **Smart Title Generation**: Dynamic, context-aware report titles via LLM
- **Intelligent Requirement Extraction**: Structured JSON parsing from natural language
- **Flexible User Intent Detection**: LLM understands "yes", "go", "proceed" variations
- **Adaptive Result Validation**: LLM evaluates backtest quality with structured reasoning
- **Multilingual Section Naming**: LLM generates localized headings for any language
- **Smart Column Detection**: LLM automatically finds best DataFrame columns
- **Dynamic Clarification Limits**: LLM decides when enough information is gathered
- **Targeted Error Diagnosis**: LLM analyzes errors and suggests specific fixes
- **Full Multilingual Support**: Generate entire reports in any language via `lang <language>`

#### Performance Improvements
- **Dramatically improved strategy execution**: Real-world testing shows up to 24x better returns
- **Example**: Same NVDA RSI strategy: 10% → 240% return (multiple trades vs single trade)
- **Better code generation**: More sophisticated strategy implementations

#### Architecture Improvements
- **20% code reduction**: Removed 311 lines of redundant/dead code (1,534 → 1,223 lines)
- **LLM-first design**: Intelligent reasoning replaces hardcoded regex patterns
- **Clean fallbacks**: Simple backups instead of complex nested logic
- **Zero breaking changes**: Complete backward compatibility maintained

#### Developer Experience
- **8 isolated test scripts**: Individual testing for each LLM-powered feature
- **Comprehensive documentation**: Updated README, REPO_NOTES, and architecture docs
- **Better error handling**: Intelligent diagnosis with targeted fix suggestions

### Technical Details

#### Removed (Dead Code Cleanup)
- `_create_implementation_plan()` (50 lines) - never called
- `_generate_code_from_plan()` (93 lines) - never called  
- `_test_code_components()` (30 lines) - never called
- `_regex_fallback_extraction()` (118 lines) → `_basic_regex_extraction()` (37 lines)
- `_critique_results_original()` (29 lines) - duplicate logic
- Various redundant error handlers and complex fallback patterns

#### Testing
- All existing tests pass (3/3 comprehensive test suite)
- 13+ minutes of thorough testing including failure recovery scenarios
- Real-world comparison testing with before/after performance metrics

---

## [0.2.0] - Previous Release

### Features
- Basic 3-phase reflection engine
- Natural language strategy input
- Code generation and execution
- Report generation with PDF output
- Multi-language support (basic)

---

## Development Philosophy

This release demonstrates the successful implementation of **"extreme promptification"** - the practice of replacing hardcoded logic with LLM-powered reasoning while maintaining clean, maintainable code architecture.

### Key Insights
1. **LLM-first architecture** improves both code quality and output quality
2. **Surgical refactoring** can remove significant redundancy while adding intelligence
3. **Intelligent fallbacks** are better than complex nested conditionals
4. **Reasoning over rules** produces more adaptive and robust systems
