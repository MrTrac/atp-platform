# Run Schema

Defines the shape of an ATP run record tracking the full lifecycle of a request execution.

- **Schema:** `run.schema.yaml`
- **Version:** 1.0
- **Used by:** `core/state/run_state.py`, `core/execution/orchestrator.py`
- **Key fields:** `run_id`, `request_id`, `status`, `resolution`, `routing`, `execution`, `validation`, `approval`
- **States:** RECEIVED, NORMALIZED, CLASSIFIED, RESOLVED, CONTEXT_PACKAGED, ROUTED, EXECUTED, VALIDATED, REVIEWED, APPROVED, FINALIZED, CLOSED, CONTINUE_PENDING, FAILED
