# Changelog

All notable changes to ATP are documented here.

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
