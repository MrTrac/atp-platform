# ATP v1.4 — F-302 Handoff / Planning Surface Consolidation

## 1. Feature identity

### Feature ID
**F-302**

### Feature name
**Handoff / Planning Surface Consolidation**

### Parent line
**ATP v1.4 — Operator Reviewability Consolidation**

---

## 2. Mục tiêu feature

Feature này nhằm tăng coherence giữa các bounded planning/handoff/review surfaces hiện có của ATP, để giảm fragmentation và giảm mental stitching cho operator.

Feature này không nhằm tạo workflow semantics hay phase/state engine.

---

## 3. Vấn đề cần giải quyết

Sau `v1.3`, ATP có nhiều surface đúng nhưng còn rời rạc ở góc nhìn planning/handoff/review, đặc biệt giữa:

- `compose-chain`
- `integration-contract`
- `deployability-check`
- continuity-related posture
- freeze/close-out / planning-entry framing nếu có liên quan thật

Khoảng trống ở đây là coherence gap, không phải execution capability gap.

---

## 4. In-scope

F-302 chỉ được phép bao gồm:

- bounded planning/handoff/review surface alignment
- narrow contract/framing consolidation
- coherent wording/structure improvements giữa các relevant surfaces
- selective summary/handoff refinements nếu thật sự justified
- giảm posture confusion giữa các bounded surfaces đã tồn tại

---

## 5. Out-of-scope

F-302 tuyệt đối không được mở sang:

- workflow engine
- phase/state engine
- execution router
- planning orchestrator
- meta-runtime coordinator
- scheduler/automation semantics
- provider/connector/deployment abstraction
- broad rewrite của toàn bộ CLI/doc tree

---

## 6. Expected outcome shape

Kết quả đúng của F-302 có thể là:

- narrow harmonization giữa một số bounded surfaces
- clearer planning/handoff framing
- concise contract alignment
- better operator interpretation across surfaces

Bad shape:
- “unified command center”
- “workflow map engine”
- “state coordinator”
- “handoff manager”
- “planning controller”

---

## 7. 3-pack execution structure

### P1 — Consolidation Gap Capture
#### Goal
- Chứng minh bounded coherence gap thật sự tồn tại giữa các relevant surfaces

#### Requirements
- evidence-first
- không đổi runtime behavior
- chỉ nhắm đúng các surfaces thật sự liên quan
- gap phải là coherence/framing gap, không phải runtime gap

#### Suggested evidence targets
- compose-related outputs
- integration-contract surface
- deployability-check surface
- continuity-related surfaces
- planning/freeze artifacts nếu thật sự cần cho reasoning

#### Expected P1 result
- gap rõ và bounded
- không có runtime drift
- commit evidence-only

---

### P2 — Bounded Surface Consolidation
#### Goal
- Thêm refinement nhỏ nhất cần thiết để các relevant surfaces coherent hơn

#### Requirements
- planning/handoff/review only
- no workflow semantics
- no execution routing semantics
- no operational progression semantics
- no broad spray across unrelated surfaces

#### Preferred shape
- narrow summary alignment
- selective wording/structure harmonization
- bounded contract linkage or interpretation refinement

#### Expected P2 result
- coherence tăng rõ ràng
- surfaces liên quan “nói chuyện với nhau” tốt hơn
- ATP không bị hiểu nhầm là có line coordinator hoặc workflow system

---

### P3 — Consolidation Posture Lock
#### Goal
- Khóa regression semantics cho coherence refinements vừa thêm

#### Requirements
- regression locks phải chặn:
  - workflow engine implications
  - planning controller implications
  - state machine implications
  - runtime progression implications
  - over-broad spread của consolidation semantics

#### Expected P3 result
- coherence gains được giữ
- no workflow drift
- feature đóng ở bounded state

---

## 8. Verification expectations

Mỗi pack phải xác nhận:

- coherence improvements là có thật và bounded
- no workflow/orchestration semantics
- no runtime capability inflation
- relevant operator-facing surfaces vẫn truthful

---

## 9. Fail-stop conditions

Dừng ngay F-302 nếu:

- feature bắt đầu trông như workflow system
- coherence logic yêu cầu state/progression model
- xuất hiện planning controller semantics
- phạm vi phải mở rộng quá nhiều surface cùng lúc
- rationale không còn là review/handoff coherence

---

## 10. Acceptance criteria

F-302 chỉ pass nếu:

- tăng coherence thực giữa các relevant surfaces
- giảm fragmentation/mental stitching cho operator
- không introduce workflow/state/operational semantics
- bounded và regression-safe

---

## 11. Final posture statement

F-302 chỉ hợp lệ nếu nó tạo ra **coherence tốt hơn giữa các bounded surfaces**, không tạo ra một **system để điều phối các surfaces đó**.
