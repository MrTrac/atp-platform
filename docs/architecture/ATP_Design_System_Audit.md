# ATP Design System Audit

**Date:** 2026-04-02
**Scope:** ATP platform repository (`SOURCE_DEV/platforms/ATP`)
**Dimensions:** Naming Consistency · Module/Contract Design · Documentation Coverage · Schema & Data Model · Local Model Integration Surface

---

## Summary

| Dimension | Issues Found | Score |
|-----------|-------------|-------|
| Naming Consistency | 4 issues | 7/10 |
| Module/Contract Design | 5 issues | 7/10 |
| Documentation Coverage | 8 issues | 6/10 |
| Schema & Data Model | 6 issues | 6/10 |
| Local Model Integration | Gap (not started) | 3/10 |
| **Overall** | **23 issues** | **6/10** |

The core business logic (`core/`) is structurally sound and internally consistent. The biggest gaps are in schema completeness, documentation at the edges (CLI modules, schema subdirs, test fixtures, profiles), and the complete absence of any LLM/local-model adapter surface despite it being called out in the architecture super-tree.

---

## 1. Naming Consistency

### ✅ What's Good
- All Python files follow `snake_case.py` throughout the repo.
- Schema files follow `<domain>.schema.yaml` consistently across all 6 schema domains.
- `build_*` function naming pattern is used uniformly for all data construction helpers across `core/`.
- `XxxError(ValueError)` is the standard error class pattern — all 10 domain error classes follow it correctly.
- Registry YAML entries use consistent key names (`provider:`, `node:`, `capability:`) within their types.

### ⚠️ Issues Found

**[N-1] `_RequestCliParser` duplicated across three CLI modules**
`cli/request_bundle.py`, `cli/request_flow.py`, and `cli/request_prompt.py` all define a private class named `_RequestCliParser`. While these are module-private and won't collide at runtime, they make text search and code navigation confusing — grep returns three unrelated classes with the same name.
**Recommendation:** Rename to `_RequestBundleCliParser`, `_RequestFlowCliParser`, `_RequestPromptCliParser` respectively.

**[N-2] `SliceDContractError` breaks domain-first naming convention**
Every other error class is named after its domain action: `RequestLoadError`, `RoutePreparationError`, `ProductResolutionError`. But `SliceDContractError` is named after an implementation slice, not a domain concept.
**Recommendation:** Rename to `DecisionContractError` to align with the domain vocabulary.

**[N-3] Test file naming uses three inconsistent numbering schemes**
Unit tests mix three naming conventions: `test_sliceNN_*.py` (10 files), `test_featureN_*.py` (5 files), and `test_featureXXX_*.py` (8 files with 200/300-series numbers). This creates ambiguity — it's unclear whether `test_slice09` and `test_feature02` cover overlapping or sequential concerns, or what the gap between `test_feature05` and `test_feature201` represents.
**Recommendation:** Standardize to a single scheme. If slice/feature distinction is meaningful, document it. Consider a flat `test_<domain>.py` naming for new tests going forward.

**[N-4] `local_service` adapter directory name is ambiguous**
`adapters/local_service/` implies a local service integration, but its README describes it as a placeholder for "service-backed local integration." This is distinct from `adapters/subprocess/` (process-level execution) and a future `adapters/local_llm/`. The name does not convey what kind of service it targets.
**Recommendation:** Rename to `adapters/local_http_service/` or clarify in README with concrete planned examples (e.g., ollama HTTP endpoint).

---

## 2. Module / Contract Design

### ✅ What's Good
- `adapters/contracts/` uses `typing.Protocol` consistently — clean structural subtyping, no ABC inheritance.
- Clear three-layer separation: `core/` → business logic, `adapters/` → infrastructure I/O, `cli/` → entrypoints. Boundaries are respected in imports.
- Builder function pattern (`build_routing_result`, `build_run_record`, `build_decision_record`, etc.) is consistent and makes data structures explicit.
- Shim pattern in `core/decision_control/slice_d_contract.py` and `core/resolution/slice_d_contract.py` correctly re-exports from the authority module without duplicating logic.

### ⚠️ Issues Found

**[C-1] Schemas are documentation-only — no runtime validation is wired in**
The `schemas/` directory contains 8 well-structured YAML schemas, but no Python code validates incoming data against them at runtime. There are no imports of `jsonschema`, `pydantic`, or `cerberus` anywhere in the core. The schemas describe what data should look like, but nothing enforces it.
**Recommendation:** At minimum, wire schema validation into the `core/validation/validator.py` module or `core/intake/normalizer.py` for `request.schema.yaml`. Mark schemas as "normative documentation only" in a README if runtime enforcement is intentionally deferred to a later version.

**[C-2] `executor.py` hardcodes provider/node routing logic outside the adapter registry**
`core/execution/executor.py` uses `if provider == "non_llm_execution" and node == "local_mac"` to dispatch to adapters. This means adding a new provider requires modifying the executor directly rather than registering a new adapter.
**Recommendation:** Replace the conditional chain with a registry or dispatch table: `EXECUTOR_MAP = {("non_llm_execution", "local_mac"): execute_local, ...}` populated from adapter registry entries.

**[C-3] `route_prepare.py` hardcodes candidate providers and nodes**
```python
provider_names = ["non_llm_execution"]
node_names = ["local_mac"]
```
These are not derived from the registry at runtime. This means adding a new provider (e.g., `ollama_local`) requires source code changes to route preparation, not just a new registry YAML.
**Recommendation:** Load candidate providers from `registry/providers/` by scanning active entries, filtered by required capabilities. The registry already supports this with `status: active` and `supported_capabilities`.

**[C-4] `adapters/contracts/` defines three Protocol contracts but they share the same method signature shape**
`ArtifactAdapter.persist()`, `ExecutionAdapter.execute()`, and `HandoffAdapter.handoff()` all accept `dict[str, Any]` and return `dict[str, Any]`. While minimal contracts are intentional for ATP v0, the lack of typed input/output shapes means the Protocol provides almost no static safety guarantee. A caller could pass a routing result to an artifact adapter with no type error.
**Recommendation:** Introduce typed dicts or dataclasses for at least the execution adapter contract inputs/outputs. This is a low-effort improvement with high static analysis benefit.

**[C-5] `core/decision_control/` has two shim files plus an authority**
`core/decision_control/contract.py` (authority), `core/decision_control/slice_d_contract.py` (shim), and `core/resolution/slice_d_contract.py` (another shim) — three files for one domain. The shim in `core/resolution/` is particularly unexpected because resolution and decision control are distinct domains.
**Recommendation:** Document clearly in each shim file which callers are expected to import from it vs. the authority, and add a deprecation timeline if the shims are temporary compatibility layers.

---

## 3. Documentation Coverage

### ✅ What's Good
- 100% README coverage across all code directories (`core/`, `adapters/`, `cli/`, `registry/`, `docs/`).
- All core business logic modules are well-documented (most at ≥ 80% docstring coverage).
- `docs/` has thorough architecture, governance, design, and roadmap documentation.
- Adapter contracts have 100% docstring coverage.

### ❌ Missing Documentation

**[D-1] `schemas/` subdirectories have no READMEs (6 directories)**
`schemas/request/`, `schemas/handoff/`, `schemas/routing/`, `schemas/run/`, `schemas/artifact/`, and `schemas/approval/` all lack README files. Readers cannot tell what each schema's purpose is, what version it covers, or how to validate against it, without reading the YAML itself.
**Priority: High** — schemas are the primary data contracts for ATP.

**[D-2] `profiles/ATP/` and `profiles/TDF/` have no READMEs**
Profile directories are undocumented — it's unclear what a profile is, how it's loaded, or what product-specific configuration it contains.

**[D-3] `templates/` subdirectories have no READMEs (3 directories)**
`templates/bundles/`, `templates/decisions/`, `templates/manifests/` are undocumented placeholder directories.

**[D-4] `tests/fixtures/`, `tests/unit/`, `tests/integration/` have no READMEs**
New contributors have no guidance on how to add fixtures, what test categories mean, or how to run the test suites beyond `make test`.

**[D-5] CLI module docstring coverage is weakest in the codebase**
Three CLI modules have 0/2 documented functions: `cli/deployability_check.py`, `cli/integration_contract.py`, `cli/review_summary.py`. Several others (`cli/execution_session.py` at 1/6, `cli/inspect.py` at 1/5) are also thin.

**[D-6] `core/decision_control/contract.py` has 5/10 documented**
The internal helper functions (`_require_non_empty`, `_require_one_of`, `_validate_source_state_ref`, `_validate_decision_semantics`, `_validate_transition_semantics`) have no docstrings. These are complex validation functions that are non-obvious to maintain.

**[D-7] `core/intake/request_flow.py` has only 2/7 documented**
This is a primary intake path — request flow helpers are underdocumented for a file of this importance.

**[D-8] Test files have near-zero function-level docstrings**
Most test files document only the module level. Individual test methods lack docstrings describing what behavior they verify. This is acceptable for simple test cases but makes complex integration test intent opaque.

---

## 4. Schema & Data Model

### ✅ What's Good
- All 8 schemas use a consistent YAML structure (`type: object`, `required:`, `properties:`).
- `additionalProperties: true` is applied uniformly — appropriate for ATP v0 where schema evolution is expected.
- Handoff schemas use a discriminated union pattern via `handoff_type` enum (`exchange_bundle`, `evidence_bundle`, `inline_context`, `manifest_reference`) — this is an excellent design for type-safe deserialization.
- `request_id` appears as a common field across all schemas — good for cross-schema traceability.

### ❌ Issues Found

**[S-1] `approval_decision.schema.yaml` is missing a `title:` field**
Every other schema has a `title:` (e.g., `title: ATP Request`, `title: ATP Artifact`). The approval schema starts directly with `type: object` and no title, breaking consistency.
**Fix:** Add `title: ATP Approval Decision` at line 1.

**[S-2] No `$schema` declaration in any schema file**
Without a `$schema: "http://json-schema.org/draft-07/schema#"` line, these YAML files cannot be validated by standard JSON Schema tooling (e.g., VS Code schema validation, `jsonschema` CLI).
**Recommendation:** Add `$schema` to all 8 schema files.

**[S-3] No schema versioning mechanism**
There is no `x-atp-schema-version` or equivalent field in any schema. When a breaking change is made (e.g., a new required field), there's no way to know which schema version a runtime artifact was produced against.
**Recommendation:** Add an `x-schema-version: "1.0"` extension field to all schemas, bumped on breaking changes.

**[S-4] `run.schema.yaml` nested object shapes are opaque**
The `run` schema defines sub-objects (`resolution`, `context_package`, `routing`, `execution`, `artifacts`, `validation`, `review`, `approval`, `finalization`) all typed simply as `type: object` with no sub-schema. A run document has the full lifecycle state embedded, but the schema gives no guidance on what shape each sub-object should have.
**Recommendation:** Add `$ref` links to relevant schemas (e.g., `routing` → `routing_decision.schema.yaml`), or at minimum add `description:` fields explaining what each sub-object contains.

**[S-5] `validation_result` has no schema**
`core/validation/validation_result.py` builds a structured validation payload with well-defined fields (`validation_id`, `validation_status`, `exit_code`, `stdout_preview`, etc.) but there is no corresponding `schemas/validation/validation_result.schema.yaml`.
**Recommendation:** Add a `schemas/validation/` directory and schema to cover validation output.

**[S-6] `request.schema.yaml` allows ambiguous optional routing fields**
`product`, `product_hint`, `provider`, `adapter`, and `capability` are all optional. A request can arrive with none of them set, relying entirely on ATP's resolution logic. The schema does not document the resolution precedence order (which field wins if multiple are provided).
**Recommendation:** Add `description:` fields explaining resolution priority, or add a `oneOf`/`if-then` constraint capturing that `product` and `product_hint` are mutually preferred alternatives.

---

## 5. Local Model Integration Surface (openclaw / ollama)

### Current State
ATP currently supports **one provider** (`non_llm_execution`) targeting **one node** (`local_mac`) via subprocess execution. There is **no LLM provider** of any kind wired into the registry, adapters, or routing logic.

The architecture super-tree document (`ATP_So_do_gop_kien_truc_hien_tai_Super_Tree.md`) shows a planned `adapters/providers/local_llm/` directory, but this directory **does not exist** in the codebase.

`adapters/local_service/` exists as a stub README only, explicitly described as a placeholder.

### What's Needed to Support ollama / openclaw

To integrate local LLM models (ollama, openclaw), ATP needs changes across four layers:

**Layer 1 — Registry** (low effort, no code change)
- Add `registry/providers/ollama_local.yaml` with `provider_type: llm`, `supported_capabilities: [llm_chat, llm_completion]`, `supported_nodes: [local_mac]`
- Add `registry/providers/openclaw_local.yaml` similarly
- Add `registry/capabilities/llm_chat.yaml` and `registry/capabilities/llm_completion.yaml`

**Layer 2 — Adapter** (medium effort)
- Create `adapters/local_llm/ollama_adapter.py` implementing the `ExecutionAdapter` Protocol
- The adapter should call the ollama HTTP API (default: `http://localhost:11434`) and normalize output to the ATP execution result shape
- Create `adapters/local_llm/openclaw_adapter.py` similarly

**Layer 3 — Executor Dispatch** (medium effort, requires fixing C-2 first)
- Add ollama and openclaw to the executor dispatch map:
  `("ollama_local", "local_mac"): execute_ollama`
- This is where fixing C-2 (hardcoded dispatcher) becomes critical — without that fix, adding LLM support requires more code surgery

**Layer 4 — Route Preparation** (low effort, requires fixing C-3 first)
- Once C-3 is fixed (load candidates from registry), LLM providers will be discovered automatically
- If C-3 is not fixed first, add `provider_names = ["non_llm_execution", "ollama_local", "openclaw_local"]` to `route_prepare.py`

### Capability Gap
There is currently no `llm_chat` or `llm_completion` capability defined. These are semantically different from `shell_execution` — they need a different input shape (prompt text, model name, temperature) and a different output shape (generated text, token counts). The `ExecutionAdapter` Protocol may need a companion `LLMAdapter` Protocol, or the existing protocol can be extended if the dict-in/dict-out shape is kept generic.

---

## Priority Actions

**Priority 1 — Schema completeness** (quick wins, high impact)
1. Add `title:` to `approval_decision.schema.yaml` (5 minutes)
2. Add `$schema` declarations to all 8 schema files (15 minutes)
3. Add READMEs to all 6 `schemas/` subdirectories explaining purpose and usage (1 hour)
4. Add `x-schema-version` fields to all schemas (30 minutes)

**Priority 2 — Contract hardening**
5. Fix executor dispatch to use a registry/map rather than hardcoded conditionals (C-2)
6. Fix route preparation to load candidates from registry dynamically (C-3)
7. Add schema validation to `core/intake/normalizer.py` for incoming requests (C-1)

**Priority 3 — Documentation gaps**
8. Add docstrings to CLI modules (`deployability_check.py`, `integration_contract.py`, `review_summary.py`)
9. Add docstrings to `core/decision_control/contract.py` private helpers
10. Add READMEs to `profiles/ATP/`, `profiles/TDF/`, and `tests/` subdirectories

**Priority 4 — Naming cleanup**
11. Rename `_RequestCliParser` to be module-specific in each CLI file (N-1)
12. Rename `SliceDContractError` → `DecisionContractError` (N-2)

**Priority 5 — Local model integration** (new work, requires P2 first)
13. Add `registry/providers/ollama_local.yaml` and `registry/capabilities/llm_chat.yaml`
14. Create `adapters/local_llm/ollama_adapter.py` implementing `ExecutionAdapter`
15. Create `adapters/local_llm/openclaw_adapter.py`
16. Wire into executor dispatch (after fixing C-2)

---

## Component Completeness Matrix

| Module | Docstrings | README | Schema | Tests | Score |
|--------|-----------|--------|--------|-------|-------|
| `core/intake/` | ⚠️ | ✅ | ✅ request | ✅ | 8/10 |
| `core/routing/` | ⚠️ | ✅ | ✅ routing_decision | ✅ | 7/10 |
| `core/execution/` | ✅ | ✅ | — | ✅ | 8/10 |
| `core/validation/` | ✅ | ✅ | ❌ missing | ✅ | 7/10 |
| `core/handoff/` | ⚠️ | ✅ | ✅ 4 schemas | ✅ | 8/10 |
| `core/decision_control/` | ⚠️ | ✅ | — | ✅ | 7/10 |
| `core/state/` | ✅ | ✅ | ✅ run | ✅ | 9/10 |
| `core/resolution/` | ⚠️ | ✅ | — | ✅ | 7/10 |
| `core/approvals/` | ✅ | ✅ | ✅ approval | ✅ | 9/10 |
| `adapters/contracts/` | ✅ | ✅ | — | — | 8/10 |
| `adapters/filesystem/` | ⚠️ | ✅ | — | ✅ | 7/10 |
| `adapters/subprocess/` | ⚠️ | ✅ | — | ✅ | 7/10 |
| `adapters/local_llm/` | ❌ | ❌ | ❌ | ❌ | 0/10 |
| `cli/` | ❌ | ✅ | — | ✅ | 5/10 |
| `registry/` | ✅ | ✅ | — | — | 9/10 |
| `schemas/` | — | ❌ subdirs | ⚠️ gaps | — | 5/10 |
| `profiles/` | — | ❌ | — | — | 2/10 |
| `templates/` | — | ❌ subdirs | — | — | 3/10 |

---

*Audit produced by Cowork / Claude · ATP v1.x · 2026-04-02*
