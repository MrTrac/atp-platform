# Changelog

All notable changes to ATP are documented here.

## [Unreleased]

### Fixed — `test_execute_timeout` did not test the timeout and left a coroutine un-awaited (KD-ATP-008)

The test patched `asyncio.wait_for` to raise `TimeoutError` at once. That (1) left the `communicate()` coroutine it had just created un-awaited — the `RuntimeWarning` that showed in every run —
and (2) skipped the timeout mechanism entirely: it never checked that `timeout_seconds` reaches `wait_for`, and it never asserted that the hung `claude` process is killed. Measured 14/10/2026:
removing `self._process.kill()` from `ClaudeCodeAdapter.execute`, or making it ignore `timeout_seconds`, left the old test green. With the default `timeout_seconds` of 7200 a missing kill would
leave an orphaned `claude` running for hours. The test now uses the real `asyncio.wait_for` with a 0.05 s timeout and a hung `communicate()`, and asserts the error text, `exit_code == -1`, that
`communicate()` was awaited, that `kill()` was called once, and that it returned in under 5 s. Seeded defects (all caught): no `kill()`; `timeout_seconds * 200`; a different error message.
Default test run: 1 warning -> 0.

### Fixed — bare `python3 -m pytest` failed on a library that was never meant to be launched (KD-ATP-003)

`tests/unit/test_cli_module_names.py::test_cli_scripts_start_on_this_interpreter` ran `python cli/<x>.py -h` for EVERY module in `cli/`, including `cli/output_contract.py`: a 745-line
library (no `__main__`, no argparse) that eight scripts `import` and `./atp` never runs. Launched bare it died with `No module named 'core'`; `make test` hid it because the Makefile exports
`PYTHONPATH=.`. The defect was in the test, not in the code. The test now launches only entry points (modules with an `if __name__ == "__main__"` guard, read with `ast`), and a second test
requires every script `./atp` launches to be one of them, so a script that loses its guard cannot silently drop out of the launch check. Bare `python3 -m pytest`: 1 failed -> 687 passed, 0 failed.
Seeded-defect checks (all caught): shim removed from `cli/validate.py`; guard string renamed in `cli/run.py`; guard replaced by `if True`.

### Changed — README.md / AGENTS.md list the bridge routes instead of "12 endpoints" (KD-ATP-011)

"12 endpoints" is ambiguous (12 distinct paths, 13 method+path pairs: `/runs/<id>` serves GET and DELETE) and nothing kept it true. Both files now list the routes, and
`tests/unit/test_bridge_routes_documented.py` reads the real routes from `bridge/bridge_server.py` with `ast` and requires the documented list to match them exactly, with no hand-counted
number. Seeded-defect checks (all caught): route renamed in the server; non-existent route documented; "12 endpoints" re-added; documented route dropped.

## [2.6.4] — 2026-10-14

### Fixed — `generators/llm.py` defaulted to the removed Ollama provider, so every real-mode call without an explicit model failed

`DEFAULT_MODEL` was `ollama/qwen3:8b`. `bridge_request` parsed it as provider `ollama`; the executor has had no handler for that provider since 2.6.0 removed the Ollama adapter, so the call
fell through to the deferred SSH stub (`status=deferred`, empty `stdout`) and `generators.llm` raised `LlmError`. Measured 2026-10-14 by calling `invoke_executor` directly: no network,
nothing launched. The default is now empty, so `bridge_request` applies the bridge's own default (anthropic, `claude-haiku-4-5-20251001`) — one source instead of a copy that can drift
(the sonnet-4 id that went 404 in 2.6.0 is the precedent). `ATP_GENERATORS_DEFAULT_MODEL` still overrides. The `report` generator's `model` parameter example no longer suggests an Ollama model.

macOS hosts must not run Ollama or any local LLM (`Global_Mac_No_Ollama_Rule`). Nothing in ATP can start one since 2.6.0; a read-only probe of the Mac on 2026-10-14 found no Ollama process,
no listener on 11434, no `ollama` binary or app. Guarded by `tests/unit/test_generators_llm_default.py` (3 tests; all 3 fail against the old default). Not exercised against the real Anthropic
API in this release: that needs a key and an outward call.

### Changed — `README.md` and `AGENTS.md` baseline lines now say v2.6.4

## [2.6.3] — 2026-10-14

### Fixed — `write_exchange_bundle()` wrote to the pre-2.0.4 exchange layout

`adapters/filesystem/exchange_adapter.py` still wrote bundles to `<workspace>/exchange/current-task/<run_id>/`, while the run writer (`workspace_writer.resolve_exchange_current_task_root`)
has used `<workspace>/_shared/exchange/current-task/<run_id>/` since 2.0.4 — so the two writers disagreed, and `./atp inspect` only found the adapter's output through its legacy fallback.
The adapter now calls the same resolver. It has no caller outside its tests today, so no running path changes. Covered by `test_writes_under_shared_exchange_layout`.

## [2.6.2] — 2026-10-11

### Fixed — every `python cli/*.py` crashed on Python ≥ 3.12 (the server runs 3.12.3)

`cli/inspect.py` shadowed the standard-library `inspect`. A script run as `python cli/<x>.py` has `cli/` first on `sys.path`, so the next stdlib import that needs
`inspect` (`dataclasses`, from Python 3.12) died with `module 'inspect' has no attribute 'get_annotations'`. Measured on `aios-server` (read-only): `python cli/run.py --help` crashed;
the bridge itself was unaffected (it never launches `cli/` scripts), which is why `/health` stayed green. CI ran 3.11, which does not trigger it, so CI never saw it.
Renamed to `cli/inspect_task.py` (the `./atp inspect` command is unchanged). `tests/unit/test_cli_module_names.py` fails if any `cli/` module takes a stdlib name and
starts every `cli/*.py` on the running interpreter.

### Fixed — `./atp inspect --run-id <id>` could not find any run written by the current writer

Since 2.0.4 the writer puts current-task exchanges under `<workspace>/_shared/exchange/current-task/`, but the reader still looked only under `<workspace>/exchange/current-task/`.
It now looks at the current layout first and the pre-2.0.4 layout second, and the error names both paths. Covered by a test that moves a run between the two layouts.

### Fixed — CI

* `ci` was red on every push: three test modules import `pytest`, which CI never installed (`unittest discover` could not even import them). CI now installs `.[dev]`, runs `make test`
  through pytest, and tests on 3.11 **and** 3.12 (the server's version).
* `Security Audit` was red on a vulnerability in the runner's own `setuptools` (PYSEC-2026-3447, fixed in 83.0.0), not in ATP (ATP has no runtime dependencies); the job now upgrades it first.
* `test_creates_artifact_directory` still expected the pre-2.0.4 `atp-artifacts/` directory; the code writes `ATP/artifacts/` (commit `6e43db6`). Test corrected.

### Included — SIGTERM fix (`aee4f7f`), merged after 2.6.1 and not released until now

### Added — `jinja2` declared as the optional extra `adapters`

`adapters/claude_code.py`, `codex.py` and `cursor.py` import `jinja2` in `_render_template`, but `pyproject.toml` declared no dependency (`dependencies = []`) and the server's venv has none, so those three
adapters would raise `ModuleNotFoundError` the first time they render a prompt (nothing noticed: the tests ran on a machine that had jinja2). Now `pip install -e ".[adapters]"` brings it in (`jinja2>=3,<4`).
The core stays dependency-free (ADR-0001) and `aios-server` does **not** install the extra: its journal since 7/10 shows only `/health` requests, no adapter run. `tests/unit/test_declared_dependencies.py`
fails if any shipped module imports a third-party package that `pyproject.toml` does not declare.

### Known, not changed

`adapters/filesystem/exchange_adapter.py:40` still writes exchange bundles to `<ws>/exchange/current-task/` (the writer uses `_shared/exchange/...` since 2.0.4); no observed use, left alone.

## [2.6.1] — 2026-10-10

### Fixed — `/health` reported a stale hand-set number, not the running version

The bridge answered `GET /health` with `"version": "1.7"` while the platform was 2.6.0
(`SERVER_VERSION` was a constant nobody maintained). A deployment could not prove which release
was actually running, and AIOS-OC's ecosystem-health panel showed `1.7`.

- `core/version.py` (new) — single source for `VERSION` and `RELEASED`.
- `bridge/bridge_server.py` — `/health`, `/` and `/status` now return `version` = platform
  version and `released` (ISO-8601 with timezone, G-VERSTAMP-1). The old `1.7` is kept as
  `bridge_version`; it is the bridge server revision, not the platform version. Additive for any
  client that only reads `status`; the one known reader of `version` (AIOS-OC) only displays it.
- `RELEASED` file next to `VERSION`.
- `tests/unit/test_version_consistency.py` (new) — keeps `VERSION`, `pyproject.toml`, `core/version.py`,
  `RELEASED` and this changelog's entry date in agreement, and checks the bridge serves them.

### Fixed — SIGTERM did not stop the bridge (every restart waited for SIGKILL)

`_handle_sigterm` called `server.shutdown()` from the main thread, the same thread running
`serve_forever()`, so it waited for a loop it was blocking: the process ignored SIGTERM (measured: two
SIGTERMs, still listening; only SIGKILL stopped it). Under systemd (`TimeoutStopUSec=1min 30s`) each
`systemctl restart aios-atp` took up to 90 s and the old process kept serving until then. The handler now
asks for the shutdown from another thread. `tests/unit/test_bridge_sigterm.py` starts the real server and
requires it to exit 0 within 5 s of SIGTERM.

Release prerequisite for publishing ATP through `aios-publish` (the release store checks that the
version inside a tag equals the version being published).

## [2.6.0] — 2026-06-26

### Removed — Ollama provider (Anthropic is now the sole/default LLM provider)

Per `~/AI_OS/00_AUTHORITY/Global_Mac_No_Ollama_Rule.md` (no local LLM on macOS).

- Deleted `adapters/ollama/`, `registry/providers/ollama_local.yaml`,
  `tests/integration/test_ollama_integration.py`.
- `executor.py`: removed the ollama adapter/dispatch; Anthropic is the primary path.
  Generalised result keys `ollama_manifest`/`ollama_routing` → `manifest`/`routing`.
- Bridge: `DEFAULT_MODEL` → `claude-haiku-4-5-20251001`, `DEFAULT_PROVIDER` →
  `anthropic`; unprefixed/unknown models default to anthropic. Dropped
  `OLLAMA_BASE_URL`/`OLLAMA_TIMEOUT` from config and the ollama pricing default.

### Fixed — cloud escalation used a deprecated model id → 404

`DEFAULT_CLOUD_MODEL` was `claude-sonnet-4-20250514` (deprecated 2026-06-15 → 404),
which broke every escalated run. Updated to `claude-sonnet-4-5-20250929`.

Verify: bridge healthy; named/bare/no-model runs default to anthropic (succeeded);
edited test files 103 passed / 0 failed.

## [2.5.0] — 2026-04-29

### Added — OpenAI Batch `wait` helper (full lifecycle parity with aios-flow)

- `adapters/cloud/openai_batch.py:wait_for_batch()` — polls
  `GET /v1/batches/{id}` until terminal state (`completed | failed |
  expired | cancelled | canceling`) or `timeout_s` elapses.
  Defaults: `timeout_s=600` (10min), `poll_interval_s=30`. Returns the
  ATP envelope plus `waited_s`, `poll_count`, `timed_out`. Short-
  circuits immediately on HTTP errors so callers don't spin until the
  timeout when OpenAI is down.
- `dispatch()` now routes `action="wait"` to `wait_for_batch` (joins
  the existing create / status / results / cancel / list actions).
- 8 new unit tests in `tests/unit/test_openai_batch.py`: missing
  batch_id rejected, terminal-on-first-poll, polls until terminal,
  timeout fires after configured wait, short-circuits on status error,
  recognizes `failed` as terminal, dispatch routes `wait`, dispatch
  error message mentions `wait`. Tests inject `sleep_fn` and `now_fn`
  for deterministic timing.

### Why
Mirrors the v2.4.0 aios-flow Phase 2 pattern (status + wait) so callers
can program against a uniform "submit → poll → terminate" lifecycle for
both DAG runs and Batch jobs. Closes the polling-helper gap noted after
v2.3.0 — batches with light queue often complete in minutes; an in-
process wait is now ergonomic without external orchestration.

## [2.4.0] — 2026-04-29

### Added — aios-flow Phase 2 (status + wait actions)

- `adapters/aios_flow/aios_flow_adapter.py` extended with two new actions
  routed via the existing top-level `dispatch()` function:
    - `action="status"` — single-shot snapshot via `GET /api/runs/{id}`,
      returns `flow_status` + full `flow_run` body. G9 trace records the
      route as `/api/runs/{id}` with method `GET`.
    - `action="wait"` — polls until terminal state (`success` |
      `succeeded` | `failed` | `cancelled` | `canceled` | `error`) or
      `timeout_s` elapses (default 300s, poll every `poll_interval_s`,
      default 2s). Returns `waited_s`, `poll_count`, `timed_out`.
- The original submit behavior is preserved as `action="dispatch"`
  (default when `action` is missing) — full backward compatibility with
  v2.1.0 callers.
- Wait function accepts injectable `sleep_fn` and `now_fn` for
  deterministic testing without real time delays.
- 11 new unit tests in `tests/unit/test_aios_flow_adapter.py`: status
  snapshot success/error, trace route correctness, wait reaches
  terminal, wait times out, wait short-circuits on failed/error, wait
  returns network error, wait via dispatch router, unknown action
  rejected, default action backward compat.

### Why
Closes the v2.1.0 Phase 2 commitment: callers couldn't programmatically
wait for a flow run to complete without polling externally. This makes
ATP a complete client for aios-flow's bounded execution lifecycle.

## [2.3.0] — 2026-04-29

### Added — OpenAI Batch API adapter (50% cost discount, async jobs)

- `adapters/cloud/openai_batch.py` — five functions wrapping OpenAI's Batch
  API:
    - `create_batch(requests, ...)` — uploads JSONL via `POST /v1/files`
      then creates batch via `POST /v1/batches`. Returns `batch_id`,
      `input_file_id`, `request_count`.
    - `get_batch_status(batch_id)` — `GET /v1/batches/{id}`. Returns
      `batch_status` (validating | in_progress | finalizing | completed |
      failed | expired | cancelled) + `request_counts`.
    - `get_batch_results(batch_id)` — looks up batch, downloads output
      file via `GET /v1/files/{id}/content`, parses JSONL into `results`
      list.
    - `cancel_batch(batch_id)` — `POST /v1/batches/{id}/cancel`.
    - `list_batches(limit, after)` — paginated list of recent batches.
- Stdlib only (urllib + multipart upload via hand-rolled boundary).
  Uses Bearer auth via `OPENAI_API_KEY` env var or per-request `api_key`.
- `bridge/openclaw_bridge.py` routing — `POST /run` with
  `adapter="openai-batch"` + `action=create|status|results|cancel|list`
  short-circuits to `openai_batch.dispatch()` (same pattern as `tdf-run`
  and `aios-flow`).
- 19 new unit tests in `tests/unit/test_openai_batch.py`: success +
  error paths for each of the 5 functions, JSONL serialization assertion,
  multipart upload assertion, dispatch routing for all 5 actions.

### Why
Batch API lets users submit 1000s of requests asynchronously at 50% cost
of the standard chat/completions endpoint. Useful for evaluation runs,
bulk dataset generation, and offline analysis — workloads that don't
need sub-second response times. Closes the v2.0.x gap noted in
`AI_NEXT_STEP.md` (option 5).

## [2.2.0] — 2026-04-29

### Added — Ollama streaming (parity with cloud providers)

- `adapters/ollama/ollama_adapter.py` — new `execute_ollama_stream()` generator
  function. Sets `stream: true` on Ollama's `/api/chat` endpoint and yields
  `(event_kind, data)` tuples matching the cloud-provider stream protocol:
  `token`, `manifest`, `error`, `aborted`. Token deltas come from each NDJSON
  line's `message.content`; the final `done: true` line populates the
  manifest with `input_tokens` (`prompt_eval_count`), `output_tokens`
  (`eval_count`), `stop_reason` (`done_reason`), and `cost_usd: 0.0`.
- `bridge/bridge_server.py` — `/run/stream` provider allowlist now includes
  `ollama` alongside `anthropic` and `openai`. Dispatch routes to
  `execute_ollama_stream` for Ollama requests.
- 8 new unit tests in `adapters/ollama/test_ollama_adapter.py` covering: token
  flow + manifest fields, contract validation (missing model / prompt),
  URLError handling, abort_event support, blank/invalid JSON line tolerance,
  `stream: true` payload assertion, empty-output completion validation.
- Tool-use deltas are NOT streamed — Ollama returns tool_calls only on the
  final `done` line, not as incremental deltas. Same behaviour applies if
  Ollama gains streaming tool support; the manifest event would carry it.

### Why
Closes the v2.0.x gap noted in `AI_NEXT_STEP.md`: streaming was cloud-only.
Ollama is now a first-class streaming citizen for local LLM workflows.

## [2.1.0] — 2026-04-29

### Added — Doctrine v5 compliance (G9 observability + aios-flow + evaluator)

- `core/trace.py` — G9 recordTrace() infrastructure: `generate_request_id()` (16-char hex),
  `build_traceparent()` (W3C `00-{32hex}-{16hex}-01`), `trace_headers()` (x-request-id /
  traceparent / x-source-module), `record_trace()` (JSONL append to
  `~/.aios/state/cross_module_trace.jsonl`, silent-fail, chmod 0o600)
- Instrumented `adapters/aokp/aokp_adapter.py` — W3C trace headers + record_trace on all 3
  routes (health / search / graph) with contract_version="AOKP_ATP_v2.3"
- Instrumented `bridge/tdf_run.py` — W3C trace headers + record_trace on TDF dispatch with
  contract_version="TDF_ATP_v1"
- `adapters/aios_flow/aios_flow_adapter.py` — new DAG runner provider dispatching to
  aios-flow :7700 `POST /api/runs`; routing short-circuit in `bridge/openclaw_bridge.py`
- `registry/providers/aios_flow.yaml` — aios-flow provider registration (incubating)
- `core/evaluator.py` — post-run evaluator: http-probe native (status + JSON key/value check);
  llm-judge / visual-diff stub to aios-flow delegation (Phase 2)
- Evaluator hook in `bridge/openclaw_bridge.py`: optional `"evaluator"` field triggers
  `run_evaluator()` and appends result to bridge response
- 28 new unit tests: `tests/unit/test_trace.py` (10), `tests/unit/test_aios_flow_adapter.py`
  (8), `tests/unit/test_evaluator.py` (10)

### Fixed

- Doctrine §4: corrected ATP framework description (`FastAPI` → `stdlib HTTP server (no framework)`)
  in `~/AI_OS/00_AUTHORITY/AI_OS_DOCTRINE_v5.0.md`

### Docs

- `AI_CURRENT_BASELINE.md` expanded (13 → ~100 lines) — closes DP#22
- `MODULE_BOUNDARY.md` trace_coverage updated to 80% achieved (G9 rollout complete)

## [2.0.4] — 2026-04-25

### Added — `tdf-run` bridge provider (P3 ATP↔TDF integration)

- `bridge/tdf_run.py` — new non-LLM provider that dispatches structured
  execution tasks to TDF Web Control Panel's `/api/exec/execute` endpoint
  (port `:4180`). Pass-through pattern: ATP owns task envelope + governance
  classification; TDF owns bounded execution + RBAC + audit trail.
- Routing in `bridge/openclaw_bridge.py`: requests with explicit
  `provider="tdf-run"` short-circuit BEFORE the `text`/`model` parser
  (TDF tasks carry structured target/params/mode envelopes, not prompts).
- Governance class mapping (per `~/SOURCE_DEV/products/TDF/tdf/docs/integrations/ATP_BRIDGE_INTEGRATION.md`):
    - `dry_run: true` → class **C** (auto-approved, preview only)
    - `validate` / non-destructive ops real → class **C**
    - `deploy.*` / `install.*` real → class **B** (requires human gate)
    - `rollback.*` / `uninstall.*` / `undeploy.*` real → class **A** (strict review)
- Env var: `TDF_WEB_URL` (default `http://localhost:4180`)
- 16 unit tests in `tests/unit/test_tdf_run.py`: validation, success path,
  failure modes (HTTP error, unreachable TDF, non-JSON response),
  governance class mapping for all op types.

### Why
Closes the P3 connection point in the AI_OS ecosystem roadmap. TDF v6.7.0
shipped a contract + reference Python skeleton in October 2025; this
release wires the ATP side. AOKP and AIOS-OC remain independent of this
provider — it only affects ATP's bridge dispatch table.

## [2.0.3] — 2026-04-19

### Added — codex + cursor CLI-agent adapters (parity with claude-code)

- `adapters/codex.py` — `CodexAdapter` spawns OpenAI `codex` CLI in the
  target repo. Template rendering + same base_ctx helpers as
  claude_code (uppercase REPO / BRANCH / YYYYMMDD / etc.). Validates
  `codex --version` + `OPENAI_API_KEY` at execute().
- `adapters/cursor.py` — `CursorAdapter` spawns Cursor `cursor-agent`
  CLI. Same config shape; Cursor's own auth handles credentials (no
  API key env needed). `FileNotFoundError` caught with install hint
  pointing to cursor.com/docs/cli.
- `bridge/bridge_server.py` — router refactored: new
  `_run_cli_agent_adapter(incoming, adapter_kind)` handles all 3
  (`claude-code` | `codex` | `cursor`) so adding a 4th adapter is a
  one-branch change. Back-compat shim `_run_claude_code_adapter` still
  exports the old name.
- CodexAdapterConfig + CursorAdapterConfig accept `workspace_dir` +
  `isolation` for interface parity with ClaudeCodeAdapterConfig, even
  though the CLI flow doesn't use them yet.

### Added — launchd wrapper reads Keychain for API keys

- `~/AI_OS/30_RUNTIME/agents/launchd/atp-bridge-start.sh` — resolves
  `ANTHROPIC_API_KEY` / `OPENAI_API_KEY` / `CURSOR_API_KEY` from macOS
  Keychain (service names match env-var names — same service names
  AIOS-OC `/api/keys` writes to). Explicit PATH + full-path python3
  ensures Homebrew Python 3.14 (with jinja2) instead of
  CommandLineTools 3.9. plist now execs this wrapper.

### Verified

- Codex end-to-end: POST /run with `adapter=codex, model=gpt-5-pro`
  spawned `codex exec` subprocess, rendered template correctly (no
  more `'YYYYMMDD' is undefined`), persisted 4 zone files to
  `~/SOURCE_DEV/workspace/atp-runs/cx-…/`.
- Cursor dispatch: returns actionable error
  "cursor-agent CLI not found in PATH — install from cursor.com/docs/cli"
  (no traceback, no generic "Bridge execution failed").

## [2.0.2] — 2026-04-19

### Fixed — claude-code adapter template ctx + bridge persist silent-fail

- **`adapters/claude_code.py` `_render_template`** — base Jinja context now
  includes uppercase aliases (`REPO`, `BRANCH`, `MODEL`, `SCOPE_SUMMARY`,
  `ISO_TIMESTAMP`, `NOW`, `TIMESTAMP`, `YYYYMMDD`, `YYYY`, `MM`, `DD`,
  `HHMM`, `HH`, `YYYYMMDD_HHMM`) in addition to the existing lowercase
  keys. Fixes `'YYYYMMDD' is undefined` Jinja errors when rendering
  playbook templates under `~/SOURCE_DEV/meta/claude-playbooks/prompts/`.
- **`bridge/bridge_server.py` persistence reporting** — when
  `persist_bridge_run` returns `{persisted: False, reason: "…"}`, the
  bridge response now surfaces the reason (as
  `persistence: {persisted: false, reason}`) and emits a structured
  `bridge.persist.error` log event, instead of the previous silent drop
  that made `persistence: null` responses indistinguishable from
  "persistence disabled". Unchanged for `reason == "disabled"` (benign).
- Verified end-to-end with AIOS-OC v3.8.0 Flow Canvas — a full
  `claude-code-agent` run (AOKP repo, prompts/01-uv-version-bump.md,
  sonnet) now persists to `~/SOURCE_DEV/workspace/atp-runs/<req_id>/`
  with request/routing/executor-outputs zones + run-summary.json.

## [2.0.1] — 2026-04-19

### Chore — ecosystem alignment bump
- Administrative patch bump as part of `uv all` (option B) across managed projects. ATP's `/run` and governance-hook behaviour unchanged; no new provider adapters added in this release.
- aios-flow (§5.4.1) is now a formal Transformation subsystem that consumes ATP `/run` per step — reconfirms the boundary that **every LLM / adapter call still flows through ATP**; aios-flow never calls providers directly.
- Pack hydrated via `aios sync reverse ATP --apply`.

## [2.0.0] — 2026-04-15

### Added — Streaming & Cancellation (BREAKING)
- **SSE streaming endpoint** `POST /run/stream` — Server-Sent Events streaming for cloud adapters
  - Events: `start`, `token`, `tool_call`, `manifest`, `error`, `done`, `aborted`
  - Supported by Anthropic and OpenAI (Ollama/local not supported in v2.0.0)
  - Optional `request_id` in body; auto-generated `stream-<hash>` if omitted
  - Respects `MODEL_ALLOWLIST` + `MAX_BODY_BYTES` security checks
- **Request cancellation** `DELETE /runs/<id>` — abort in-flight request
  - Sets abort event on in-flight tracker; adapter checks between SSE chunks
  - Adapter yields `aborted` event and stops when flag set
  - Returns 200 `{cancelled: true}` for active requests, 404 otherwise
- **In-flight tracker** (`core/in_flight_tracker.py`) — thread-safe request registry
  - `register(request_id, provider, model)` → `threading.Event`
  - `cancel(request_id)` → bool
  - `list_active()` → snapshot of active requests
  - `GET /runs/active` lists in-flight requests for AIOS-OC monitoring
- **SSE formatter** (`core/streaming.py`) — canonical event emission
- **Anthropic streaming** (`execute_anthropic_stream`) — uses `stream=true` Messages API
  - Parses `content_block_delta`, `content_block_start/stop`, `message_delta`
  - Streams text deltas + accumulated tool_use input JSON
  - Captures `stop_reason`, token usage at stream end
- **OpenAI streaming** (`execute_openai_stream`) — uses `stream=true` + `stream_options.include_usage`
  - Aggregates tool_calls piecewise (OpenAI streams function arguments as partial strings)
  - Captures `finish_reason`, token usage from final chunk

### Changed
- Bridge server docstring updated for 3 new endpoints
- AIOS-OC v2.9.1 abort feature now has end-to-end ATP integration (finally wire-compatible)

### Why this is v2.0.0 (not v1.10.0)
New endpoints + new event-stream protocol = API-level addition. Existing `/run` stays fully
backwards-compatible, but clients adopting SSE must handle new event types and request lifecycle.

### Tests
- 29 new tests in `tests/unit/test_v20_features.py`
  - In-flight tracker (8): register/cancel/list, thread safety
  - SSE formatter (7): all 6 event types produce valid SSE
  - Anthropic streaming (5): tokens, tool_use, missing key, missing model, abort
  - OpenAI streaming (6): tokens, tool_call delta aggregation, error paths, abort
  - Bridge cancellation integration (3): active cancel, post-unregister, abort state

## [1.9.0] — 2026-04-15

### Added — Agentic Capabilities
- **Tool use / function calling** — both Anthropic and OpenAI adapters
  - Pass `tools` (list of definitions) and optional `tool_choice`
  - Tool use blocks/calls extracted into `result.tool_calls = [{id, name, input}]`
  - Tool-only responses (no text) treated as valid completion
- **JSON mode** — both adapters
  - Pass `json_mode=true`
  - Anthropic: appends "Respond ONLY with valid JSON…" to system prompt
  - OpenAI: sets `response_format = {"type": "json_object"}`
- **Vision** — pass-through via messages array
  - Anthropic: `{"type": "image", "source": {...}}` content blocks
  - OpenAI: `{"type": "image_url", "image_url": {...}}` content parts
  - Supported by claude-3*, claude-sonnet-4*, gpt-4o*, gpt-5
  - NOT supported by o1/o3 (text-only reasoning models)
- **Capabilities matrix** expansion (`registry/capabilities/`)
  - `llm_tool_use.yaml` — function calling capability
  - `llm_json_mode.yaml` — structured JSON output
  - `llm_vision.yaml` — multimodal image inputs
- **Provider registry** updated: anthropic + openai now declare 5 capabilities
- **Bridge propagation**: `tools`, `tool_choice`, `json_mode` flow incoming → executor → adapter
- **Result surfacing**: `tool_calls` bubbles up through normalize_adapter_result → bridge_request

### Tests
- 29 new tests in `tests/unit/test_v19_features.py` (tool use, JSON mode, vision, capabilities, propagation, end-to-end)

## [1.8.0] — 2026-04-15

### Added — Cloud Foundations
- **OpenAI adapter** (`adapters/cloud/openai_adapter.py`) — cloud LLM via OpenAI Chat Completions API
  - Supports gpt-4, gpt-4o, gpt-5, o1/o1-preview/o1-mini, o3-mini
  - Auto-uses `max_completion_tokens` for o1/o3 reasoning models
  - Same input/output contract as Anthropic adapter
  - `api_key` passthrough (request body → `OPENAI_API_KEY` env fallback)
  - HTTPError diagnostic body capture
- **Retry/backoff** (`core/retry.py`) — exponential backoff with jitter for transient errors
  - Retries on 429, 502, 503, 504, network errors (URLError)
  - Honors `Retry-After` header when present
  - Caps: 3 attempts, 30s per attempt, 120s total wait
  - Wired into both Anthropic and OpenAI adapters
- **Per-model cost table** (`registry/pricing/model_prices.json` + `core/pricing.py`)
  - 13 models with accurate pricing (Claude Sonnet/Opus/Haiku, GPT-4/4o/5, o1/o3)
  - Provider defaults as fallback for unknown models
  - JSON format (ATP YAML loader doesn't support nested dict-of-dicts)
- **Per-model timeout** (`ATP_MODEL_TIMEOUTS` env var, `core/config.get_timeout_for_model()`)
  - Overrides default 120s for specific models (e.g., `o1=600` for reasoning)
- **Registry**: `registry/providers/openai_cloud.yaml` — OpenAI provider entry
- **EXECUTOR_MAP**: `openai` handler registered (auto-detection now end-to-end)
- **Config**: `OPENAI_API_KEY`, `OPENAI_TIMEOUT` (default 300s), `MODEL_TIMEOUTS` env vars

### Changed
- Anthropic adapter now uses `core.pricing.calculate_cost()` instead of hardcoded Sonnet 4 rates
  (Haiku now ~6x cheaper as expected; Opus ~5x more expensive)
- Anthropic adapter wrapped in `with_retry()` for 429 handling

### Tests
- 37 new tests in `tests/unit/test_v18_features.py`
  - Pricing table (10): all model lookups, fallbacks, edge cases
  - Retry logic (12): retryable/non-retryable, exponential delay, Retry-After
  - OpenAI adapter (10): success, API key flows, o1/gpt distinction, errors
  - Executor dispatch (2): EXECUTOR_MAP completeness
  - Per-model timeout (2): defaults + overrides
  - Anthropic pricing migration (1): Haiku now uses Haiku rates

## [1.7.0] — 2026-04-14

### Added
- Cloud API key passthrough: accept `api_key` from request body with env-var fallback (Anthropic adapter, executor, bridge)
- Model auto-detection in OpenClaw bridge: auto-detect cloud provider from model name prefix (`claude-*` → anthropic, `gpt-*/o1/o3` → openai)

### Changed
- Anthropic adapter: catch `HTTPError` separately and read response body for detailed error diagnostics
- Bridge server: include top-level `error` field in response when `status=failed` for AIOS-OC consumption

## [1.6.0] — 2026-04-13

### Added
- Central config module (`core/config.py`): single source of truth for all env vars with startup validation
- Structured JSON logging (`core/structured_log.py`): JSON-lines to stderr with request_id, provider, cost, error_code
- Error classification (`core/error_codes.py`): typed codes (network_error, timeout, contract_violation, etc.)
- Cost tracking: Anthropic adapter estimates USD from token counts; Ollama marks cost=0.0
- Request body size limit (`ATP_BRIDGE_MAX_BODY`, default 10 MB)
- Model allowlist (`ATP_MODEL_ALLOWLIST`, optional comma-separated)
- Config validation at bridge server startup with structured warnings
- Bridge server version bumped to 1.6 with updated docstring for all 9 endpoints
- 18 new tests covering config, error codes, structured logging, and security

## [1.5.0] — 2026-04-12

### Added
- Artifact persistence: `store_artifact()` writes to `workspace/atp-artifacts/` when enabled
- Exchange bundle persistence: `write_exchange_bundle()` writes to `workspace/exchange/` when enabled
- Bridge run persistence: each `/run` writes request, routing, execution to `workspace/atp-runs/`
- Bridge endpoints: `GET /runs` (list), `GET /runs/<id>` (detail with zone files)
- Environment variables: `ATP_PERSIST_ARTIFACTS`, `ATP_PERSIST_RUNS` (default: disabled)
- 13 new tests for persistence (tmpdir-isolated)

## [1.4.0] — 2026-04-12

### Added
- Lightweight JSON Schema validator (`core/validation/schema_validator.py`) — no external deps
- Advisory schema validation wired into normalizer (warnings only, never blocks)
- Bridge introspection endpoints: `GET /status`, `GET /providers`, `GET /capabilities`
- 8 READMEs for undocumented directories (profiles, templates, tests)
- 15 new tests (schema validator + bridge introspection)

## [1.3.0] — 2026-04-12

### Added
- AOKP knowledge adapter: `check_health()`, `query_knowledge()`, `query_graph()`
- KnowledgeAdapter Protocol + typed shapes (KnowledgeQuery, KnowledgeResult, GraphQuery, GraphResult)
- Context enrichment module: opt-in AOKP knowledge injection before executor dispatch
- Bridge integration: AOKP context appended to payload before execution
- Registry entries: `aokp` provider, `knowledge_retrieval` + `graph_query` capabilities
- Environment variables: `ATP_AOKP_ENABLED`, `ATP_AOKP_URL` (default: disabled)
- 19 new tests (14 unit + 5 registry)

## [1.2.0] — 2026-04-12

### Changed
- Executor dispatch refactored to registry-driven `EXECUTOR_MAP` (replaces hardcoded conditionals)
- Route preparation discovers providers/nodes from registry dynamically
- `SliceDContractError` renamed to `DecisionContractError`
- CLI parsers renamed to module-specific (`_RequestFlowCliParser`, etc.)

### Added
- Typed adapter contracts: `LLMRequest`, `LLMResult`, `LocalExecResult`
- Registry entries for Ollama and Anthropic providers + LLM capabilities
- Schema metadata: `$schema`, `title`, `x-schema-version` on all 10 schemas
- READMEs for all 7 schema subdirectories
- New `validation_result` schema
- `register_executor()` API for runtime provider registration
- 17 new tests (dispatch, discovery, schema metadata)

### Updated
- AGENTS.md and README.md for v1.1.0+ baseline

## [1.1.0] — 2026-04-04

### Added
- Ollama adapter: local LLM execution (qwen3:14b, qwen3:8b, deepseek-r1:8b)
- Anthropic adapter: cloud escalation path
- OpenClaw bridge: end-to-end request flow integration
- HTTP bridge server at localhost:8765 (ThreadingHTTPServer)
- AI_OS governance gate integration (aios-gate, tier A–E classification)
- Escalation policy: local → cloud fallback
- 9 PRs merged (#2–#9)

## [1.0.4] — 2026-03-19

- Slice E: governance/docs line (frozen)

## [1.0.3] — 2026-03-19

- Slice D: decision/transition control contracts (frozen)

## [1.0.2] — 2026-03-19

- Slice C: exchange boundary and continuity (frozen)

## [1.0.1] — 2026-03-19

- Slice B: review bundle and execution prompt (frozen)

## [1.0.0] — 2026-03-19

- Slice A: operational maturity baseline (frozen)

## [0.7.0] — 2026-03-14

- Final v0 baseline (frozen)
