<!-- 55f643bb-96d8-4a52-8796-24566481df56 f6eed092-b886-4ef0-8459-a6c6178f4794 -->
# Agentic Checkpoint Logging Plan

## Goals
- **Create a per-run checkpoint** that another LLM can fully reconstruct from.
- **Log everything**: metadata, CLI params, env, code snapshot, LLM conversation, agentic graph, backtest logs, and artifacts.
- **Keep it practical**: minimal integration points, low friction, machine- and human-readable output.

## Output Structure (per run)
- Directory: `reports/<run_id>/`
  - `agent.log` (single monolithic, human-readable log with delimited sections)
  - `messages.jsonl` (LLM prompts/responses; one JSON per line)
  - `graph.json` (agent graph nodes/edges with timestamps)
  - `params.json` (CLI args + config used)
  - `system_info.json` (git SHA, python version, os, pyproject deps)
  - `code.tar.gz` (exact code snapshot at run start)
  - `artifacts/` (plots, generated scripts, CSVs, backtest outputs)

## agent.log Sections
- `--- METADATA ---`: run_id, start_time, duration, git_sha, cwd, python, os
- `--- PARAMETERS ---`: CLI args, env keys (redacted values), config selected
- `--- CODE SNAPSHOT (INDEX) ---`: list of files included (+ hash & size)
- `--- CODE SNAPSHOT (INLINE) ---`:
  - `===== FILE: <path> =====` then file contents
- `--- LLM MESSAGES ---`: compact transcript with role, model, token counts
- `--- AGENT GRAPH ---`: summarized edges with timestamps and outcomes
- `--- BACKTEST LOG ---`: captured stdout/stderr while running backtest
- `--- ARTIFACTS INDEX ---`: relative paths, MIME/types, short description

## Files to Modify / Add
- Add `src/nlbt/checkpoint.py`:
  - `RunCheckpoint` class managing run directory, `agent.log`, sidecar files
  - APIs: `start()`, `log_metadata()`, `log_params()`, `snapshot_code()`, `log_llm_message()`, `log_graph_event()`, `tee_process_output()`, `record_artifact()`, `finalize()`
  - Redaction: env var names only + value hashing, configurable allowlist
  - Inclusion rules: include `src/**/*.py`, `tests/**/*.py`, `pyproject.toml`, `README.md`, `env.example` (configurable); exclude via `.checkpointignore`
- Update `src/nlbt/cli.py`:
  - Add flags: `--run-id`, `--checkpoint-dir`, `--no-code-snapshot`, `--include`, `--exclude`
  - Initialize `RunCheckpoint` early, write metadata/params, run main wrapped in output tee to `agent.log`
- Update `src/nlbt/llm/client.py`:
  - Hook before/after LLM calls to append to `messages.jsonl` and to `agent.log`
  - Log: role, model, tokens, latency, finish_reason
- Update `src/nlbt/reflection.py`:
  - Log agentic graph events (node enter/exit, tool calls, decision edges)
  - Emit compact `graph.json` (nodes/edges with ISO timestamps)
- Optional: `src/nlbt/checkpointignore.py` to parse `.checkpointignore` similar to `.gitignore`

## Logging Formats
- `messages.jsonl`: `{ timestamp, role, model, content, tokens, meta }`
- `graph.json`: `{ nodes: [...], edges: [...] }`
- `params.json`: exact CLI args used
- `system_info.json`: `{ git_sha, python, os, pyproject_deps }`
- `agent.log`: human-friendly sections with clear delimiters

## Retention and Size Control
- Toggle inline code block in `agent.log` via `--no-inline-code` (still keep `code.tar.gz`)
- Respect `.checkpointignore` to skip large files or secrets
- Truncate overly large stdout sections with a note, but keep full raw in `artifacts/backtest.log`

## Security & Privacy
- Redact env var values by default; allowlist via `--env-allow KEY1,KEY2`
- Never dump secrets files if matched by `.checkpointignore`

## Example Usage
- `nlbt run --strategy rsi --symbol NVDA --checkpoint-dir reports`
- Produces `reports/20251005_193000/` with the files listed above

## Open Questions (pick one for each)
1. Do you want only `agent.log`, or `agent.log` + structured sidecars?
   - a) `agent.log` + sidecars (recommended)
   - b) only `agent.log`
2. Code snapshot format?
   - a) Inline in `agent.log` + `code.tar.gz` (recommended)
   - b) Inline only


### To-dos

- [ ] Create RunCheckpoint in src/nlbt/checkpoint.py with APIs
- [ ] Wire checkpoint into src/nlbt/cli.py with CLI flags
- [ ] Hook LLM request/response logging in src/nlbt/llm/client.py
- [ ] Emit agent graph events in src/nlbt/reflection.py to graph.json
- [ ] Implement code snapshotter and .checkpointignore support
- [ ] Tee backtest stdout/stderr into agent.log and artifacts/backtest.log
- [ ] Write params.json and system_info.json at run start
- [ ] Add minimal test that a run creates expected files