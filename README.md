# ATP

ATP là `platform repository` tại `SOURCE_DEV/platforms/ATP`.

ATP là một governance-first platform tại baseline **v2.3.0**, phát triển từ v0 shape-correct MVP. Repo này dùng để phát triển và duy trì ATP source; repo này không phải runtime artifact repository.

Trạng thái release:

- `v0.1.0` — `v0.4.0` — frozen v0 baselines
- `v1.0.0` — `v1.0.4` — frozen v1 slices A–E
- `v1.1.0` — Ollama + Anthropic + bridge + governance gate
- `v1.2.0` — Structural hardening (registry-driven dispatch)
- `v1.3.0` — AOKP Phase 1 knowledge integration
- `v1.4.0` — Schema validation + bridge introspection + docs
- `v1.5.0` — Artifact persistence (M8)
- `v1.6.0` — Observability + hardening
- `v1.7.0` — Cloud API key passthrough, model auto-detection, AOKP v2.3.x
- `v1.8.0` — OpenAI adapter, retry/backoff, per-model cost & timeout
- `v1.9.0` — Tool use, JSON mode, vision, capabilities matrix
- `v2.0.0` — SSE streaming + request cancellation
- `v2.0.1`–`v2.0.4` — ecosystem alignment, codex/cursor adapters, tdf-run bridge provider
- `v2.1.0` — G9 observability, aios-flow adapter, evaluator wiring (Doctrine v5 compliance)
- `v2.2.0` — Ollama streaming parity
- **`v2.3.0`** — **current released baseline** (OpenAI Batch API adapter)

Runtime components (v2.3.0):

- **Ollama adapter** — local LLM execution (qwen3:14b, qwen3:8b, deepseek-r1:8b) + **streaming** (v2.2.0)
- **Anthropic adapter** — cloud + retry + pricing + tool use + JSON mode + vision + **streaming**
- **OpenAI adapter** — gpt-4o/5 + o1/o3 + retry + pricing + tool use + JSON mode + vision + **streaming** + **Batch API** (v2.3.0, async jobs at 50% cost)
- **AOKP adapter (v2.3.x)** — 6 endpoints: health, search, graph, chat, graph-rag, temporal
- **tdf-run bridge provider** — dispatches structured tasks to TDF Web Panel at `:4180` (governance-classified A–C)
- **aios-flow adapter** — dispatches DAG workflows to aios-flow at `:7700` via `POST /api/runs`
- **Bridge server** — stdlib HTTP at `localhost:8765` (12 endpoints incl. `/run/stream`, `/runs/active`)
- **SSE streaming** — `POST /run/stream` with event-stream protocol (start/token/tool_call/manifest/done/aborted)
- **Request cancellation** — `DELETE /runs/<id>` aborts in-flight via threading.Event
- **In-flight tracker** (`core/in_flight_tracker.py`) — thread-safe registry + abort events
- **Evaluator** (`core/evaluator.py`) — post-run validation: http-probe native, llm-judge/visual-diff → aios-flow stub
- **G9 observability** (`core/trace.py`) — W3C traceparent headers + `~/.aios/state/cross_module_trace.jsonl`
- **Pricing registry** — 13 models in `registry/pricing/model_prices.json`
- **Capabilities matrix** — 5 LLM capabilities per cloud provider
- **Retry logic** — exponential backoff for 429/5xx/network
- **Per-model timeout** — `ATP_MODEL_TIMEOUTS` env override
- **Governance hook** — aios-gate integration (tier A–E)

ATP không phải là một closed snapshot architecture và cũng không phải một ad hoc open architecture.

ATP được duy trì như:

- một stable core
- với modular boundaries
- explicit extension seams
- composable capabilities
- và controlled evolutionary governance

ATP cũng phải được hiểu qua operating axis:

`requested user ⇄ ATP ⇄ products`

ATP không mở rộng chỉ để tăng internal mechanisms. ATP mở rộng khi việc đó giúp ATP mediate tốt hơn giữa requested user và product execution surfaces.

## Boundary chính

- `SOURCE_DEV/` là `logical workspace root`
- `SOURCE_DEV/platforms/ATP` là ATP source repo
- `SOURCE_DEV/products/TDF` là product repo mà ATP resolve trong v0
- `SOURCE_DEV/workspace` là runtime zone cho runs, artifacts, exchange, và logs

Runtime artifacts không được lưu trong repo này. Runs, output, exchange bundle, logs, và các artifact phát sinh trong quá trình vận hành phải thuộc `SOURCE_DEV/workspace`.

## Repo này dùng để làm gì

- phát triển ATP CLI, control-plane modules, adapters, registry, schema, profiles, và templates thuộc ATP
- duy trì tài liệu kiến trúc, thiết kế, vận hành, và governance của ATP
- hardening, refinement, normalization, và planning có governance trong phạm vi current ATP `v0` major family và các frozen baselines đã có

## Repo này không dùng để làm gì

- không dùng làm nơi lưu runtime artifact
- không dùng làm workspace vận hành cho run output hoặc exchange output
- không dùng để mở rộng scope kiến trúc ngoài ATP v0 nếu chưa có decision rõ ràng

## Tài liệu nên đọc trước

Thứ tự đọc source of truth:

1. `docs/architecture/ATP_MVP_v0_Freeze_Decision_Record.md`
2. `docs/architecture/ATP_MVP_v0_Implementation_Plan.md`
3. `docs/README.md`
4. các tài liệu liên quan trong `docs/design/`, `docs/operators/`, và `docs/governance/`

Nếu cần historical freeze facts:

- `docs/archive/reports/ATP_v0_2_0_Freeze_Closeout.md`
- `docs/archive/reports/ATP_v0_3_0_Freeze_Closeout.md`
- `docs/archive/reports/ATP_v0_4_0_Freeze_Closeout.md`

Nếu cần roadmap continuity:

- `docs/roadmap/README.md`
- `docs/roadmap/ATP_Product_Roadmap.md`

Nếu cần operational development rules:

- `docs/governance/ATP_Development_Ruleset.md`

## Local bootstrap

```bash
make help
make tree
make validate-registry
make smoke
make test
```

## Nguyên tắc khi phát triển trong repo này

- giữ boundary giữa source repo và runtime zone
- ưu tiên refinement, normalization, và hardening hơn là mở rộng feature sớm
- mở rộng capability chỉ qua review, planning, verification, consolidation, freeze, close-out, và roadmap inheritance có kiểm soát
- giữ glossary, naming, schema, và artifact terminology đồng bộ với tài liệu ATP
- không đảo ngược source-of-truth order một cách ngầm định
- mọi thay đổi vượt ra ngoài ATP v0 freeze phải có decision rõ ràng do con người chốt
