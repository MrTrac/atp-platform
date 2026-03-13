# ATP MVP v0 Freeze Decision Record

- **Title:** ATP MVP v0 Freeze Decision Record
- **Version:** v0.1
- **Status:** Draft-Final
- **Date:** 2026-03-14
- **Scope:** ATP MVP v0
- **Positioning:** Shape-correct MVP
- **Artifact Role:** Authoritative architecture decision artifact

## Source Documents

1. `ATP_AI_Workspace_Open_Rules.md`
2. `ATP_Drawio_Style_Structure.md`
3. `ATP_Glossary_VI_Refined_for_V1_3_1_Draft_R2.md`
4. `ATP_So_do_gop_kien_truc_hien_tai_Super_Tree.md`
5. `ATP_So_do_phan_lop_va_flow_truc_quan.md`
6. `ATP_Workspace_Artifact_Handoff_Model.md`

---

## FDR-01 — Nature of v0

**Decision:** ATP MVP v0 is a **shape-correct MVP**: it must preserve the ATP architectural shape and semantics, while implementing only the minimum required to execute **one complete end-to-end run** successfully.

**Implication:** v0 is not a full ATP platform implementation.

---

## FDR-02 — Repository and workspace boundary

**Decision:** ATP is a standalone platform repository at:

`SOURCE_DEV/platforms/ATP`

`SOURCE_DEV/` is a logical workspace root, not a monorepo root.

`SOURCE_DEV/workspace/` is a **runtime workspace zone**, separated from source repositories and must not be treated as the primary Git coding workspace.

---

## FDR-03 — Mandatory operating principles

**Decision:** ATP MVP v0 must preserve these principles:

- platform-first
- provider-agnostic
- adapter-first
- artifact-centric
- human-gated
- local-first but node-portable
- single source of contextual truth

---

## FDR-04 — Official ATP Control Plane modules for v0

**Decision:** The official ATP Control Plane naming for v0 is:

- Request Intake
- Input Classification
- Product Resolution
- Context Packaging
- Routing Engine
- Cost Control
- Run State / Decision State

**Constraint:** `planner` and `dispatcher` may exist only as internal components, not as the top-level architecture vocabulary.

---

## FDR-05 — Official orchestration flow for v0

**Decision:** ATP MVP v0 must follow this orchestration flow:

Request Intake  
→ Normalize  
→ Input Classification  
→ Product Resolution  
→ Context Packaging  
→ Routing Preparation  
→ Route Selection  
→ Execution via Adapter  
→ Capture Output  
→ Validation / Review  
→ Approval Gate  
→ Finalization  
→ Handoff to Next Step  
→ Close Run or Continue

---

## FDR-06 — Mandatory Provider/Adapter structural shape

**Decision:** ATP MVP v0 must contain the following structural shape from day one:

- Provider Registry
- Capability Registry
- Product Registry
- Node Registry
- Policy Registry
- Adapter contracts

**Constraint:** ATP routes by **capability**, not by hard-coded vendor identity.

---

## FDR-07 — Mandatory real provider in v0

**Decision:** The mandatory real provider for v0 is:

- **Non-LLM Execution Provider**

**Purpose:** ATP must be able to execute shell, git, build, test, lint, and similar operational tasks directly.

Other providers may exist only as registry entries and stubs in v0.

---

## FDR-08 — Mandatory real adapters in v0

**Decision:** The mandatory real adapters for v0 are:

- **Filesystem Exchange Adapter**
- **SSH / Remote Command Adapter**, or a local subprocess implementation with equivalent semantics

Other adapters may remain as contracts plus stubs in v0.

---

## FDR-09 — Product Resolution scope for v0

**Decision:** Product Resolution in v0 must support at minimum:

- `ATP`
- `TDF`

It must load at least:

- product identity
- repo boundary
- module/component scope at basic level
- minimal policy and approval rules

---

## FDR-10 — Official workspace runtime layout

**Decision:** Every run in ATP MVP v0 must materialize using this layout:

```text
SOURCE_DEV/workspace/
└── atp-runs/
    └── <run-id>/
        ├── request/
        ├── manifests/
        ├── planning/
        ├── routing/
        ├── executor-outputs/
        ├── validation/
        ├── decisions/
        ├── final/
        └── logs/
```

Additionally, the workspace must contain these zones:

```text
SOURCE_DEV/workspace/
├── atp-runs/
├── atp-artifacts/
├── atp-cache/
├── atp-staging/
└── exchange/
    ├── current-task/
    ├── current-review/
    └── current-approval/
```

---

## FDR-11 — Mandatory artifact lifecycle

**Decision:** ATP MVP v0 must model artifacts at least with these states:

- raw
- filtered
- selected
- authoritative
- deprecated

`deprecated` must be supported in the model even if used minimally in v0.

---

## FDR-12 — Rule for authoritative artifact

**Decision:** An authoritative artifact is the currently effective source for a given run, decision boundary, or handoff boundary.

An authoritative artifact in v0 must record:

- artifact freshness
- run reference
- source step reference
- authoritative status

**Constraint:** a selected artifact is not automatically authoritative.

---

## FDR-13 — Handoff mechanisms for v0

**Decision:** ATP MVP v0 must support the following handoff mechanisms at architecture level:

- Inline Context
- Evidence Bundle
- Exchange Bundle
- Manifest Reference

**Implementation rule for v0:**

- must work for real: Inline Context, Evidence Bundle, Manifest Reference
- must exist in basic materialized form: Exchange Bundle

---

## FDR-14 — Hard handoff rule

**Decision:** ATP must never expose the entire runtime workspace blindly to an AI or executor.

ATP must:

- select only the correct artifacts
- exclude irrelevant artifacts
- guarantee correct run scope
- guarantee correct step scope
- package correctly for the target executor
- record which artifacts were used by which step

---

## FDR-15 — Official vocabulary rule

**Decision:** All schemas, code, and docs for v0 must follow the official glossary vocabulary, including at minimum:

- platform
- product
- tool
- utility
- provider
- adapter
- capability
- execution_intent
- node
- artifact
- artifact_freshness
- authoritative artifact
- evidence bundle
- exchange bundle
- manifest reference
- policy
- approval gate

**Language rule:** core terms remain in English; explanatory prose may be in Vietnamese.

---

## FDR-16 — Human-gated approval in v0

**Decision:** Approval Gate is mandatory in ATP MVP v0, but implementation may be **manual-first**.

v0 does not require a full approval UI system. It must produce at least:

- approval decision artifact
- escalation decision
- second-opinion flag
- corresponding run state update

---

## FDR-17 — Routing and cost scope for v0

**Decision:** ATP MVP v0 must include structural support for:

- capability-based routing
- node-aware routing
- data locality / artifact proximity
- cost-aware routing
- routing confidence
- cost control policy

**Implementation rule:** route selection in v0 may remain fully **rule-based**. A true multi-provider arbitration engine is not required in v0.

---

## FDR-18 — Definition of Done for ATP MVP v0

**Decision:** ATP MVP v0 is considered complete when it can:

- execute one end-to-end run following the official orchestration flow
- resolve products at minimum for ATP and TDF
- route through the mandatory provider/adapters defined in this record
- persist complete run artifacts using the official workspace layout
- produce validation/review and approval decision artifacts
- hand off using Inline Context, Evidence Bundle, and Manifest Reference
- remain consistent with the official glossary and architecture boundary rules

---

## Final note

This Freeze Decision Record is the baseline decision artifact for:

1. ATP MVP v0 backlog / work-items
2. ATP v0 repository skeleton
3. ATP v0 schema and model naming
4. ATP v0 implementation sequencing
5. ATP v0 review and approval alignment
