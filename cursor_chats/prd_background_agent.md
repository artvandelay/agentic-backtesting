# PRD — Background Agent (Autonomous Backtesting) for NLBT

Owner: Jigar • Status: Draft • Date: 2025-10-02

## 1) Background & Problem
- Current interactive agent works end-to-end (gathers requirements → generates code → executes in sandbox → reports), but results feel underwhelming and require user babysitting.
- Goal: Add a “background agent” (in the spirit of Codex-like autonomous coding loops) that can run jobs end-to-end without user presence, iterate a few times on failures, and deliver a final report/logs.

## 1.a) Greenfield Constraint (From Scratch)
- This initiative must be implemented by a coding agent as a greenfield, “from scratch” build.
- The agent may read existing files for inspiration, but it must not import, call, or depend on existing NLBT modules, classes, or functions.
- All code paths for background execution, orchestration, and reporting must live in a new, isolated package namespace (e.g., `src/bgagent/`), with no imports from `src/nlbt/*`.
- Interaction boundaries: the only shared surfaces allowed are filesystem paths (reading/writing reports/logs) and environment variables. No in-process coupling.
- Rationale: evaluate whether a background-first design built independently can outperform or simplify the current approach.

## 2) Objectives & Success Metrics
- Reduce user interaction required to complete a backtest to near-zero for well-formed prompts.
- Decrease time-to-first-report (median) vs interactive flow by ≥20% for standard strategies.
- Improve completion rate (report generated without manual intervention) to ≥90% across a representative set of examples in `EXAMPLES.md`.
- Maintain or improve result quality (no regressions in metrics correctness based on spot checks).

## 3) In Scope
- New background execution mode with a single command that detaches, runs to completion, and saves outputs.
- Lightweight iteration loop (retry with small self-corrections) using a Producer–Critic pattern implemented anew (no reuse of existing agent code).
- Progress logs and final artifacts saved to disk.
- Minimal local orchestration: no external queues/brokers; keep it simple.

## 4) Out of Scope (Phase 1)
- Web UI / Gradio front-end (tracked separately in Phase 2).
- Distributed workers or Kubernetes.
- Parameter optimization / grid search (may be explored later).
 - Reusing NLBT code paths (session/agent/sandbox/data). Those are explicitly disallowed for this experiment.

## 5) User Experience (CLI-first)
- Command from project root:
  - Start a detached job that keeps running in the background and writes outputs:
  ```bash
  nlbt bg "Backtest AAPL 50/200 MA crossover in 2024 with $25K"
  ```
  - Optional flags:
  ```bash
  nlbt bg "…" \
    --model $LLM_MODEL \
    --timeout 120 \
    --max-iters 3 \
    --name job_aapl_ma
  ```
- Feedback:
  - Immediately prints: job ID, where logs will be written, and where the final report will appear.
  - Job runs in a detached session (prefer `tmux`), allowing the user to continue working.
- Artifacts:
  - Logs: `logs/<job_id>.log`
  - Report: `reports/<job_id>.md`
  - (Optional) JSON summary: `reports/<job_id>.json`
 - Greenfield note: the CLI must be implemented in a new command module that does not import existing `nlbt` modules.

## 6) Functional Requirements
- FR1: Accept a single-shot natural language strategy request as input.
- FR2: Spawn a background process (detached) that:
  - Reconstructs minimal conversation context
  - Runs the existing 3-phase pipeline (Understanding → Implementation → Reporting) automatically
  - Applies the existing retry/self-critique up to `--max-iters`
- FR3: Persist logs and final report paths deterministically based on job ID.
- FR4: Respect existing `.env` settings (model, timeouts, retries) and CLI overrides.
- FR5: Exit codes: 0 on success; non-zero on failure with error message in logs.
 - FR6 (Greenfield): No imports from `src/nlbt/*`. The background agent must provide its own:
   - LLM client wrapper
   - Minimal sandboxed execution approach
   - Simple data access layer (may use yfinance directly)
   - Report writer

## 7) Non-Functional Requirements
- NFR1: Simplicity over heavy infra. Prefer a single `tmux`-backed detachment or `subprocess.Popen`.
- NFR2: Self-contained within the repo; no external services required.
- NFR3: All scripts run from project root. `.env` at project root is respected.
- NFR4: Background run should not block the shell; logs must be streamable to file.
 - NFR5 (Isolation): New package `src/bgagent/` must build and run independently from `src/nlbt/`.

## 8) System Design (Minimal)
- Entry point: add a new CLI module (e.g., `src/bgagent/cli.py`) and expose a console script `nlbt-bg` or keep `nlbt bg` by wiring a thin shim that only shells out to the new module.
- Implementation options (choose 1, default to tmux given user preference):
  1. tmux session per job: `tmux new-session -d -s bg_<job_id> 'python -m bgagent.bg_run …'`
  2. Fallback: `subprocess.Popen` detached process (if tmux unavailable).
- `bg_run` code path (new):
  - Loads `.env`, sets up job ID, opens `logs/<job_id>.log` for append.
  - Uses a brand-new autopilot runner: Understanding → Implementation → Reporting (no calls to nlbt code).
  - Provides its own sandboxed execution (minimal: `exec` with guards and timeout) and data fetch via yfinance.
  - Writes artifacts, returns exit code.

## 9) Interfaces
- CLI:
  - `nlbt bg <prompt> [--name NAME] [--timeout SECS] [--max-iters N] [--model M]`
  - `nlbt bg-status <job_id>` (optional; prints basic info if using tmux)
- Programmatic (optional):
  - `from bgagent import run_background_job(prompt, **opts) -> job_id`

## 10) Experiment & Evaluation Plan
- Dataset: Use 10–15 prompts from `EXAMPLES.md` covering MA crossover, RSI, Bollinger, MACD/RSI, stop-loss/take-profit.
- Baseline: Current interactive run (single attempt) initiated by a human.
- Treatment: Background agent with `--max-iters 3`.
- Metrics logged per job: time-to-report, completion (Y/N), retry count, error class if failed.
- Success criteria (see §2): meet or exceed the targets for time and completion rate; no obvious accuracy regressions.
 - Additional check: confirm no runtime imports from `nlbt` in logs (guardrails in CI can grep for `from nlbt` or `import nlbt`).

## 11) Telemetry & Logging
- Minimal structured logs to `logs/<job_id>.log`:
  - job_id, start/end times, model, iterations, each attempt result, final artifact path
- Append-only; human-readable first, JSON lines optional.
 - Log the resolved environment and confirm greenfield isolation at job start (e.g., print `imports_ok: true`).

## 12) Risks & Mitigations
- R1: Hallucinations/fragility during unattended runs → keep `max-iters` small; ensure clear error logging; keep sandbox timeouts.
- R2: Rate limits from providers → backoff on retries; respect cache layer.
- R3: Security of generated code → unchanged: sandbox + module restrictions + timeout.
- R4: Hidden state differences vs interactive → seed minimal context and print resolved parameters before execution.
 - R5: Scope creep through accidental reuse → add CI check that fails if `bgagent` imports `nlbt`.

## 13) Milestones
- M1 (Day 1–2): Create `src/bgagent/` package, greenfield CLI (`nlbt bg`) and `bg_run` detached runner. Smoke test on 3 prompts.
- M2 (Day 3): Add `--max-iters`, structured logging, status command, and isolation guard (no `nlbt` imports). Validate 10 prompts.
- M3 (Day 4): Evaluation run and short findings report saved to `reports/bg_eval_<date>.md`.

## 14) Operational Notes & Preferences
- Use `.env` at project root (do not commit) for defaults.
- Prefer running long jobs under a single tmux session and detaching.
- Keep implementation minimal; avoid complex job queues or services.
- All commands and scripts run from project root.
 - Create artifacts under `logs/` and `reports/` only; no coupling with `nlbt` internals.

## 15) Open Questions
- Should we enable optional parameter search (e.g., fast 2–3 variant tries) within the same job?
- Do we want a simple `bg list`/`bg stop` for tmux management or keep manual?
- Do we want a JSON result artifact in addition to markdown for downstream consumption?
 - Should we pin yfinance or provide an abstraction to swap providers later without reusing `nlbt` code?


