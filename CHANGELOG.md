# Changelog

All notable changes to ATP are documented here.

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
