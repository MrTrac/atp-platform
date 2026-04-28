# ADR-0001: bounded-execution-model

- **Status:** Accepted
- **Date:** 2026-03-23 (v1.x foundation; backfilled 2026-04-28 per DP#123)
- **Author(s):** anh Thu + Claude Code
- **Module(s):** ATP (Transformation Plane)
- **Governance:** AI_OS Doctrine §1 G6 + §7.6 + DP#78
- **Decision tier:** Tier 3 (foundational architecture)

---

## 1. Context

ATP serves as Transformation Plane — accepts heterogeneous execution requests (LLM inference, code generation, file ops) from many consumers (AIOS-OC, aios-flow, OpenClaw). Need uniform contract that:
- Doesn't lock to single LLM vendor
- Provides governance gate (G6 tier classification)
- Enables observability (per-run artifacts)
- Doesn't bottleneck on Python startup (sub-second cold start)

---

## 2. Decision

**Bounded execution model** với 3 axioms:
1. Every `/run` request classified A-E governance tier via `governance_hook.py` (Tier A = blocking approval; B = warn; C/D = auto-approved; E = bypass)
2. Each run produces structured artifacts in `~/.aios/atp/runs/<run-id>/` (post-DP#50 migration): `request.json` + `response.json` + `run-summary.json` + per-adapter logs
3. Adapter dispatch via Z3 layer — vendor-agnostic interface, swappable implementations (cloud/anthropic, cloud/openai, ollama, claude_code, codex, cursor)

ATP itself = stdlib-only Python 3.11+ + FastAPI. **Zero heavy deps** to maintain sub-second cold start.

---

## 3. Alternatives considered

| # | Alternative | Pros | Cons | Rejected |
|---|---|---|---|---|
| A | LangChain / LlamaIndex framework | Pre-built abstractions | Heavy deps, vendor lock-in patterns, sluggish startup |
| B | OpenAI SDK only | Simple | Vendor lock; doesn't cover Claude/Ollama/local |
| C (chosen) | Custom adapter interface + governance hook | Full control, vendor-agnostic, governance integrated | Custom maintenance burden |
| D | gRPC + Protobuf + Python codegen | Type-safe | Overkill for HTTP/JSON workload, complicates adapter swap |

---

## 4. Consequences

### 4.1 Positive
- Adapter agnostic — Claude/OpenAI/Ollama/Codex/Cursor all 1-file adapters
- Governance gate enforced before every external LLM call
- Run artifacts = full audit trail (DP#49 backup-friendly)
- Zero-deps constraint = production stable across Python versions

### 4.2 Negative / trade-offs
- 25+ adapter files to maintain (`bridge/` + `adapters/{cloud,ollama,aokp,contracts,filesystem,subprocess,ssh_remote}/`)
- No automatic retries / circuit breakers (defer to caller — AIOS-OC handles)
- Run artifacts accumulate without auto-prune (DP#50 90-day prune Phase 2)

### 4.3 Risks accepted
- Custom adapter API may diverge from emerging MCP standard — accepted; ATP is governance + execution gateway, not pure tool integration

---

## 5. Implementation
- `bridge/bridge_server.py` — FastAPI :8765 dispatcher
- `bridge/governance_hook.py` — A-E classification
- `bridge/run_persistence.py` — artifact persistence
- `bridge/context_enrichment.py` — AOKP context injection
- `adapters/<vendor>/<vendor>_adapter.py` — uniform `AdapterInterface`
- `bridge/openclaw_bridge.py` + `bridge/tdf_run.py` — special-case adapters

## 6. References
- AI_OS Doctrine §3.1.3 (3 contracts produced + 5 consumed including TDF v1 new 2026-04-25)
- MODULE_BOUNDARY.md: `~/AI_OS/20_PROJECTS/ATP/MODULE_BOUNDARY.md`
- AOKP_ATP_v2.3 contract (Phase 2 materialize per DP#98)
