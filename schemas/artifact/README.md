# Artifact Schema

Defines the shape of an ATP artifact envelope used across the artifact lifecycle.

- **Schema:** `artifact.schema.yaml`
- **Version:** 1.0
- **Used by:** `adapters/filesystem/artifact_store.py`, `core/artifact_export.py`
- **Key fields:** `artifact_id`, `artifact_type`, `artifact_status`, `payload_summary`
