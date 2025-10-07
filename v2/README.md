# NLBT v2 — Promptification (3-Phase System)

This branch sketches a redesigned, prompt-first agent. The engine is a thin interface; LLMs drive decisions. A junior validator (<jr coding agent>) gates feasibility; a strong coder implements; a reporter can request one retry.

```mermaid
flowchart TD
  %% Styles
  classDef user fill:#d1e9ff,stroke:#1e73be,color:#0b3d91
  classDef llm fill:#fff7b2,stroke:#d4b200,color:#7a5a00
  classDef decision fill:#ffb3b3,stroke:#c70000,color:#660000
  classDef system fill:#e8f5e9,stroke:#43a047,color:#1b5e20

  U0([User]):::user --> P1[[Phase 1: Strategy Shaping]]:::system

  P1 --> JV[<jr coding agent> Validate implementability\n(weak model)]:::llm
  JV -->|YES| R1[Refined Strategy Spec]:::system
  JV -->|NO (bullets)| Q1[Ask clarifications (one message)\nloop until YES]:::llm
  Q1 --> P1

  R1 --> D1{Proceed?}:::decision
  D1 -->|Yes| P2[[Phase 2: Coding Agent (3 tries)]]:::system
  D1 -->|Change| P1

  P2 --> C1[Generate code + logs\n(strong model)]:::llm
  C1 --> X1[Execute in sandbox]:::system
  X1 --> CR[Critic evaluate]:::llm
  CR -->|PASS| P3[[Phase 3: Reporter]]:::system
  CR -->|RETRY (<3)| C1
  CR -->|FAIL| F1([Report failure]):::system

  P3 --> RQ{Data sufficient?}:::decision
  RQ -->|No (1 retry)| C1
  RQ -->|Yes| REP[Write report + TL;DR + optional insights]:::llm
  REP --> OUT([Report saved + TL;DR]):::system
```

## Key Ideas
- Broad acceptance: let users ask anything trading/backtest-related. <jr coding agent> says YES/NO.
- Weak model as validator: if it thinks it can be done, the strong coder will likely succeed.
- Reporter can trigger one coding retry if artifacts are insufficient.
- Thin interface: no hardcoded business logic; prompts carry structure.

## Next Steps
- Confirm this diagram/flow.
- Define prompt templates for: validator, coder, critic, reporter.
- Implement minimal driver that wires these prompts.
```
