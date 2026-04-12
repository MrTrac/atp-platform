# AOKP Knowledge Adapter

Context enrichment adapter connecting ATP to the AOKP Knowledge Plane.

## Purpose

AOKP is a **context source**, not an executor. This adapter retrieves knowledge
from AOKP's Phase 1 APIs to enrich request context before execution. It respects
the governance boundary: AOKP provides knowledge, ATP remains the execution plane.

## API Surface

| Function | AOKP Endpoint | Purpose |
|---|---|---|
| `check_health()` | `GET /api/phase1/status` | Verify AOKP is reachable |
| `query_knowledge(request)` | `POST /api/search` | Retrieve ranked knowledge hits |
| `query_graph(request)` | `POST /api/graph` | Query knowledge graph entities |

## Environment Variables

| Variable | Default | Purpose |
|---|---|---|
| `ATP_AOKP_ENABLED` | `""` (disabled) | Enable AOKP context enrichment |
| `ATP_AOKP_URL` | `http://localhost:3002` | AOKP base URL |

## Error Handling

AOKP being unavailable never crashes ATP. All functions return structured
error results with `status: "failed"` or `status: "unavailable"`. When
disabled or unavailable, requests pass through to the executor unchanged.
