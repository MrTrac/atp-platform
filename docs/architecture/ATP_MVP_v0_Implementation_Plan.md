# ATP MVP v0 Implementation Plan

- **Title:** ATP MVP v0 Implementation Plan
- **Version:** v0.1
- **Status:** Draft-Final
- **Date:** 2026-03-14
- **Scope:** ATP MVP v0
- **Source Baseline:** `ATP_MVP_v0_Freeze_Decision_Record.md`

---

## 1. Planning principle

ATP MVP v0 is implemented as a **shape-correct MVP**:
- correct ATP repository and workspace boundary
- correct Control Plane semantics
- correct Provider / Adapter / Registry shape
- correct artifact lifecycle
- correct workspace artifact handoff model
- correct glossary and naming
- minimum implementation sufficient to execute **one full end-to-end run**

The implementation plan below converts the approved backlog into:
- phases
- milestone gates
- dependency map
- build order from empty repo to working MVP

---

## 2. Phase-to-milestone map

| Milestone | Phase | Objective | Exit condition |
|---|---|---|---|
| M0 | Foundation / Boundary / Bootstrap | Create ATP repo and runtime boundary correctly | Repo boundary and workspace zones are correct |
| M1 | Glossary / Domain Model / Naming Freeze | Freeze vocabulary and core schemas | Request / Run / Artifact / Handoff models are stable |
| M2 | Request Intake / Normalize / Classification | Build first control-plane entry flow | Request can be loaded, normalized, classified, and state-updated |
| M3 | Product Resolution / Registry / Policy Loading | Resolve ATP/TDF and load minimal policy context | Product Resolution works for ATP and TDF |
| M4 | Context Packaging / Manifest / Evidence Bundle | Build ATP context semantics | Task Manifest, Product Context, Evidence Bundle are materialized |
| M5 | Provider / Capability / Node / Routing Shape | Build routing structure and rule-based route selection | Capability-based routing works in v0 |
| M6 | Adapter Contracts / Execution | Execute real operational tasks via adapter | Real execution path works end-to-end |
| M7 | Artifact Capture / Validation / Review | Enforce artifact lifecycle and decision semantics | Artifacts are persisted and validated correctly |
| M8 | Approval / Handoff / Finalization / CLI / E2E | Close the full ATP run loop | One full end-to-end run passes with inspectable outputs |

---

## 3. Phase breakdown

### Phase 0 — Foundation / Boundary / Bootstrap
**Milestone:** M0

#### Included work-items
- ATP-0001 — Khởi tạo repo ATP đúng boundary
- ATP-0002 — Khởi tạo workspace runtime zones chuẩn ATP
- ATP-0003 — Đưa Freeze Decision Record vào docs chính thức

#### Objective
Establish the ATP repository as a standalone platform repo and establish the runtime workspace model exactly as approved.

#### Outputs
- `SOURCE_DEV/platforms/ATP`
- runtime zones in `SOURCE_DEV/workspace/`
- authoritative Freeze Decision Record in repo docs

#### Exit criteria
- source and runtime are clearly separated
- ATP repo tree is initialized correctly
- runtime zones exist and are not mixed with Git source

---

### Phase 1 — Glossary / Domain Model / Naming Freeze
**Milestone:** M1

#### Included work-items
- ATP-0101 — Chốt vocabulary chính thức cho schema và code
- ATP-0102 — Định nghĩa Request model v0
- ATP-0103 — Định nghĩa Run model v0
- ATP-0104 — Định nghĩa Artifact model v0
- ATP-0105 — Định nghĩa handoff models

#### Objective
Lock the vocabulary and domain contracts before building orchestration logic.

#### Outputs
- naming convention document
- Request schema
- Run schema
- Artifact schema
- Handoff schemas:
  - InlineContext
  - EvidenceBundle
  - ExchangeBundle
  - ManifestReference

#### Exit criteria
- model vocabulary matches approved glossary
- artifact lifecycle states are represented
- handoff mechanisms have stable structure

---

### Phase 2 — Request Intake / Normalize / Classification
**Milestone:** M2

#### Included work-items
- ATP-0201 — Build request loader
- ATP-0202 — Build normalize pipeline
- ATP-0203 — Build rule-based Input Classification engine
- ATP-0204 — Update run state for intake and classification

#### Objective
Implement the first official Control Plane stages.

#### Outputs
- raw request materialization
- normalized request artifact
- classification artifact
- run state updates for early stages

#### Exit criteria
- a request can enter ATP
- normalized request is always generated
- classification produces stable fields:
  - `domain`
  - `product_type`
  - `request_type`
  - `execution_intent`

---

### Phase 3 — Product Resolution / Registry / Policy Loading
**Milestone:** M3

#### Included work-items
- ATP-0301 — Build Product Registry v0
- ATP-0302 — Build product profile loader
- ATP-0303 — Build minimal Policy Registry
- ATP-0304 — Build Product Resolution engine

#### Objective
Resolve ATP/TDF correctly and load boundary-aware product context.

#### Outputs
- product registry
- product profiles
- minimal policy registry
- product resolution artifact

#### Exit criteria
- ATP and TDF resolve correctly
- repo boundary and basic scope are loaded
- minimal approval and routing policies are available

---

### Phase 4 — Context Packaging / Manifest / Evidence Bundle
**Milestone:** M4

#### Included work-items
- ATP-0401 — Build Product Identity packager
- ATP-0402 — Build Task Manifest generator
- ATP-0403 — Build product context manifest
- ATP-0404 — Build evidence selection rules
- ATP-0405 — Build Evidence Bundle materializer

#### Objective
Create ATP-native contextual packaging rather than generic task execution context.

#### Outputs
- `manifests/task_manifest.yaml`
- `manifests/product_context.yaml`
- evidence selection policy
- evidence bundle artifact

#### Exit criteria
- context is packaged for routing and execution
- evidence selection is explicit and rule-based
- the next step receives only relevant artifacts

---

### Phase 5 — Provider / Capability / Node / Routing Shape
**Milestone:** M5

#### Included work-items
- ATP-0501 — Build Capability Registry v0
- ATP-0502 — Build Provider Registry v0
- ATP-0503 — Build Node Registry v0
- ATP-0504 — Build Routing Preparation engine
- ATP-0505 — Build rule-based Route Selection engine
- ATP-0506 — Build minimal Cost Control policy evaluator

#### Objective
Implement capability-based, node-aware, rule-based routing for v0.

#### Outputs
- capability registry
- provider registry
- node registry
- routing preparation artifact
- routing decision artifact
- cost decision artifact

#### Exit criteria
- ATP routes by capability, not vendor
- route decision is explainable and persisted
- node and cost context are represented

---

### Phase 6 — Adapter Contracts / Execution
**Milestone:** M6

#### Included work-items
- ATP-0601 — Define adapter contracts
- ATP-0602 — Implement Filesystem Exchange Adapter
- ATP-0603 — Implement Non-LLM execution adapter
- ATP-0604 — Build Execution orchestrator

#### Objective
Make ATP execute real operational work via adapter contracts.

#### Outputs
- adapter interfaces
- filesystem exchange adapter
- local subprocess / SSH-equivalent execution adapter
- execution orchestrator
- executor output artifacts

#### Exit criteria
- ATP can execute real shell / git / build / test / lint style work
- execution is driven by routing decisions
- outputs are normalized and persisted

---

### Phase 7 — Artifact Capture / Validation / Review
**Milestone:** M7

#### Included work-items
- ATP-0701 — Build Artifact Store v0
- ATP-0702 — Build artifact state transitions
- ATP-0703 — Implement validation pipeline
- ATP-0704 — Implement review decision logic

#### Objective
Make ATP artifact-centric in actual implementation, not only in diagrams.

#### Outputs
- artifact persistence layer
- artifact lifecycle logic
- validation artifacts
- review artifacts

#### Exit criteria
- raw / filtered / selected / authoritative / deprecated are represented
- validation artifacts exist
- review decision is recorded in the correct decision boundary

---

### Phase 8 — Approval / Handoff / Finalization / CLI / E2E
**Milestone:** M8

#### Included work-items
- ATP-0801 — Build manual-first Approval Gate
- ATP-0802 — Implement Inline Context handoff
- ATP-0803 — Implement Manifest Reference handoff
- ATP-0804 — Implement Exchange Bundle basic
- ATP-0805 — Build finalization engine
- ATP-0806 — Build close-run / continue-run transition
- ATP-0901 — Build CLI entrypoints v0
- ATP-0902 — Build inspect command
- ATP-0903 — End-to-end happy path run
- ATP-0904 — Validation reject path
- ATP-0905 — Write operator guide for ATP v0

#### Objective
Close the loop from intake to approval, handoff, finalization, inspection, and test validation.

#### Outputs
- approval artifacts
- handoff artifacts
- final package
- close-run / continue-run transition
- CLI
- inspect command
- integration tests
- operator guide

#### Exit criteria
- one full end-to-end run passes
- reject path is also covered
- outputs are inspectable and aligned with ATP semantics

---

## 4. Dependency map

### 4.1 High-level dependency chain

```text
Phase 0
  -> Phase 1
  -> Phase 2
  -> Phase 3
  -> Phase 4
  -> Phase 5
  -> Phase 6
  -> Phase 7
  -> Phase 8
```

### 4.2 Detailed critical dependency chain

```text
ATP-0001
-> ATP-0002
-> ATP-0101
-> ATP-0102
-> ATP-0103
-> ATP-0104
-> ATP-0105
-> ATP-0201
-> ATP-0202
-> ATP-0203
-> ATP-0301
-> ATP-0302
-> ATP-0303
-> ATP-0304
-> ATP-0402
-> ATP-0403
-> ATP-0404
-> ATP-0405
-> ATP-0501
-> ATP-0502
-> ATP-0503
-> ATP-0504
-> ATP-0505
-> ATP-0601
-> ATP-0602
-> ATP-0603
-> ATP-0604
-> ATP-0701
-> ATP-0702
-> ATP-0703
-> ATP-0704
-> ATP-0801
-> ATP-0803
-> ATP-0805
-> ATP-0806
-> ATP-0901
-> ATP-0903
```

### 4.3 Parallelizable work

The following items may be developed in parallel after their dependencies are satisfied:

- ATP-0103 and ATP-0104 after ATP-0101
- ATP-0302 and ATP-0303 after ATP-0301
- ATP-0401 and ATP-0402 after ATP-0304
- ATP-0502 and ATP-0503 after ATP-0501
- ATP-0602 and ATP-0603 after ATP-0601 / ATP-0505
- ATP-0703 and ATP-0701 after ATP-0604 / schema readiness
- ATP-0802 / ATP-0803 / ATP-0804 after artifact and handoff models stabilize
- ATP-0902 and ATP-0905 after output structure is stable

---

## 5. Recommended build order from empty repo to working MVP

### Step 1
Create repository boundary and workspace runtime zones.
- ATP-0001
- ATP-0002
- ATP-0003

### Step 2
Freeze naming and schemas.
- ATP-0101
- ATP-0102
- ATP-0103
- ATP-0104
- ATP-0105

### Step 3
Implement the intake path.
- ATP-0201
- ATP-0202
- ATP-0203
- ATP-0204

### Step 4
Implement product-aware ATP logic.
- ATP-0301
- ATP-0302
- ATP-0303
- ATP-0304

### Step 5
Build ATP-native context packaging.
- ATP-0401
- ATP-0402
- ATP-0403
- ATP-0404
- ATP-0405

### Step 6
Build routing structure and rule-based route selection.
- ATP-0501
- ATP-0502
- ATP-0503
- ATP-0504
- ATP-0505
- ATP-0506

### Step 7
Connect execution through adapter contracts.
- ATP-0601
- ATP-0602
- ATP-0603
- ATP-0604

### Step 8
Make artifact lifecycle and validation real.
- ATP-0701
- ATP-0702
- ATP-0703
- ATP-0704

### Step 9
Close the ATP decision loop.
- ATP-0801
- ATP-0802
- ATP-0803
- ATP-0804
- ATP-0805
- ATP-0806

### Step 10
Expose MVP via CLI and prove it with tests.
- ATP-0901
- ATP-0902
- ATP-0903
- ATP-0904
- ATP-0905

---

## 6. Milestone acceptance gates

### M0 acceptance gate
- ATP repo is initialized in the correct platform boundary
- runtime workspace zones exist
- authoritative Freeze Decision Record is in repo docs

### M1 acceptance gate
- core schemas are stable
- vocabulary matches the approved glossary
- handoff contracts are defined

### M2 acceptance gate
- request intake works
- normalized request is generated
- classification output is persisted
- run state is updated

### M3 acceptance gate
- Product Resolution works for ATP and TDF
- product profile and basic policies are loaded

### M4 acceptance gate
- task manifest exists
- product context exists
- evidence bundle is selected and materialized correctly

### M5 acceptance gate
- route preparation works
- route selection is capability-based and rule-based
- provider / node / cost context is persisted

### M6 acceptance gate
- real execution is working via adapter path
- execution outputs are captured and normalized

### M7 acceptance gate
- artifact lifecycle states work
- validation and review artifacts are produced
- decision boundary is auditable

### M8 acceptance gate
- full happy-path run passes
- reject path also passes
- inspect command works
- final package and handoff artifacts are correct

---

## 7. Recommended implementation cadence

### Sprint A
Focus:
- Phase 0
- Phase 1
- Phase 2

Goal:
- ATP repo and workspace established
- schemas frozen
- request enters ATP correctly

### Sprint B
Focus:
- Phase 3
- Phase 4

Goal:
- ATP becomes product-aware
- ATP context and evidence packaging become real

### Sprint C
Focus:
- Phase 5
- Phase 6

Goal:
- ATP can route and execute real work

### Sprint D
Focus:
- Phase 7
- Phase 8

Goal:
- ATP closes the loop with validation, approval, handoff, finalization, CLI, and E2E proof

---

## 8. Definition of Done for this implementation plan

This implementation plan is fulfilled when ATP MVP v0 can:

- accept a request into the official ATP run flow
- classify and resolve ATP/TDF correctly
- package context and evidence in ATP-native form
- select a route using capability/provider/node-aware rule-based routing
- execute real operational work through approved adapters
- persist artifacts using the official workspace layout
- validate and review results
- pass through a manual-first Approval Gate
- finalize outputs and hand off using:
  - Inline Context
  - Evidence Bundle
  - Manifest Reference
- materialize Exchange Bundle in basic form
- expose the run through CLI and inspect command
- pass both happy-path and reject-path integration tests

---

## 9. Final planning note

This document should be used as the direct parent planning artifact for:
1. ATP MVP v0 final repo skeleton
2. ATP MVP v0 work breakdown execution board
3. ATP MVP v0 milestone tracking
4. ATP MVP v0 implementation review
