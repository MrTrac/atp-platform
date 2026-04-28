# ADR-0003: aokp-context-enrichment

- **Status:** Accepted
- **Date:** 2026-04-15 (v2.0.x; backfilled 2026-04-28)
- **Author(s):** anh Thu + Claude Code
- **Module(s):** ATP + AOKP (cross-module)
- **Governance:** AI_OS Doctrine §3.9.1 + DP#78
- **Decision tier:** Tier 3 (cross-module contract)

---

## 1. Context

LLM responses without ecosystem knowledge produce generic answers ("I don't have information about HCMOPS"). User queries about ATCC equipment / VATM ATM operations need AOKP knowledge graph context injected.

Direct user → LLM bypass → no AOKP awareness. Need ATP to inject context per-request based on intent classification.

---

## 2. Decision

ATP `bridge/context_enrichment.py` calls AOKP `/api/search` + `/api/managair/*` for every `kb_lookup` / `reasoning` intent run. Context appended to system prompt with attribution markers ("Found in MAIR KB: rack RPOPS01...").

Contract: `AOKP_ATP_v2.3.yaml` — defines query interface + response shape.

Timeout: 120s (matches AIOS-OC ADR-0005). Fallback: empty context with prompt instruction "answer from general knowledge if not found in KB".

---

## 3. Alternatives considered

| # | Alternative | Pros | Cons | Rejected |
|---|---|---|---|---|
| A | Always inject AOKP context | Consistent | Overhead for non-KB intents (chitchat, action) |
| B | Caller (AIOS-OC) injects context | ATP simpler | Multiple consumers reimplement — DRY violation |
| C (chosen) | ATP injects per-intent classification | Centralized + selective | Coupling: ATP knows intent classes |
| D | RAG framework (LlamaIndex / Haystack) | Pre-built | Heavy deps violate ATP zero-deps constraint (ADR-0001) |

---

## 4. Consequences

### 4.1 Positive
- All consumers benefit — no need to reimplement context injection
- Intent-based selectivity = no overhead for chitchat
- Attribution markers in prompt = transparency about KB sources
- DP#61 trace propagation: AOKP `/api/search` calls leave trace entries

### 4.2 Negative / trade-offs
- ATP coupling to AOKP API shape (mitigated: contract version `v2.3` enables migration)
- 120s timeout per AOKP query × multiple calls = total run could be 5+ minutes worst case
- AOKP downtime = ATP runs work but with no KB context (graceful degradation)

### 4.3 Risks accepted
- Phase 3 Multi-FIR scaling: ATP needs FIR-aware context selection (extend contract `AOKP_ATP_v3.x`)

---

## 5. Implementation
- `bridge/context_enrichment.py`
- Calls AOKP `/api/search?q=<query>&intent=<intent>`
- Compound queries pattern (matches AIOS-OC ADR-0005 v3.23.6 fallback)
- Run artifact records context.json for audit

## 6. References
- AIOS-OC ADR-0005 sister decision (timeout + fallback chain)
- AI_OS Doctrine §3.4.6 (G7 — ATP queries via API only, never AOKP filesystem direct)
- AOKP_ATP_v2.3 contract Phase 2 materialize per DP#98
