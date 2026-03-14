# ATP v1.0 Milestone Proposal

## 1. Milestone identity

- Milestone: `ATP v1.0`
- Target version: `v1.0.0`
- Planning branch: `v1.0-planning`
- Status: `Proposed`

## 2. Proposal summary

`ATP v1.0` được đề xuất là major continuation đầu tiên sau `v0.7.0`.

Milestone này không nhằm reset kiến trúc hay mở rộng breadth lớn. Trọng tâm của nó là bắt đầu operational maturity trên stable core mà `v0` đã chốt, theo hướng controlled operationalization.

Điểm mở đầu của milestone này là:

- thiết lập một `Review / Approval Gate Contract` explicit
- đặt gate đó đúng vị trí sau `finalization / closure record`
- làm rõ operational gate semantics mà không kéo ATP sang approval UI, recovery engine, hay orchestration rộng

## 3. Why this milestone exists

Sau `v0.7.0`, ATP đã có một foundational lifecycle chain coherent:

- request-to-product execution chain của `v0.5.0`
- closure chain của `v0.6.0`
- finalization / closure record của `v0.7.0`

Điều còn thiếu không còn là seam nền tảng của `v0`, mà là một operational gate layer rõ để ATP có thể bắt đầu maturity horizon mới ở mức kiểm soát vận hành.

Nếu không mở `v1.0` ở điểm này, ATP sẽ tiếp tục kéo dài `v0.x` dù boundary của foundational family đã khép lại, làm mờ distinction giữa:

- foundational hardening
- operational maturity

## 4. Strategic outcome expected

Sau khi hoàn tất `v1.0`, ATP phải đạt được các kết quả chiến lược sau:

### 4.1 Major-transition outcome
ATP chuyển major family từ `v0` sang `v1` một cách có evidence và có continuity rõ.

### 4.2 Operational gate outcome
ATP có một review / approval gate layer explicit, bounded, file-based, và traceable.

### 4.3 Lifecycle continuity outcome
Gate layer mới nối được với `finalization / closure record` của `v0.7.0` mà không phá stable core.

### 4.4 Governance outcome
Operationalization mới vẫn bám đúng governance discipline hiện có: planning, slices, consolidation, freeze, close-out.

## 5. Problem statement

Hiện trạng cần giải quyết trong `v1.0`:

1. ATP đã có finalization / closure record nhưng chưa có operational gate contract rõ sau điểm đó.
2. Operational review / approval semantics hiện có nguy cơ bị hiểu như UI hoặc workflow behavior nếu không được contract hóa rõ.
3. ATP cần một bước đầu tiên của `v1` đủ hẹp để tăng maturity vận hành mà không mở breadth quá sớm.
4. Boundary giữa lifecycle continuity và operational decision gate cần được làm rõ trước khi nghĩ tới các horizon rộng hơn.

## 6. Proposed scope

### 6.1 In scope

#### A. `v1` operational maturity baseline
- xác nhận `v1` là operational maturity horizon đầu tiên sau `v0.7.0`
- giữ continuity rõ giữa `v0` foundation và `v1` operational layer

#### B. Slice A — Review / Approval Gate Contract
- định nghĩa gate là gì
- xác định gate nằm ở đâu sau `finalization / closure record`
- xác định gate cần evidence gì
- xác định gate ghi decision gì và traceability gì

#### C. Boundary discipline
- giữ separation rõ với approval UI
- giữ separation rõ với recovery engine
- giữ separation rõ với routing / provider selection
- giữ separation rõ với broader orchestration

### 6.2 Out of scope

- approval UI
- recovery engine hoặc recovery execution
- provider selection / provider arbitration
- routing expansion
- cost-aware routing expansion
- topology-aware orchestration
- distributed control
- generalized orchestration
- portfolio orchestration
- broad `v2` semantics

## 7. Proposed milestone slices

### Slice A — Review / Approval Gate Contract
Mục tiêu:

- định nghĩa explicit operational gate đầu tiên của `v1`
- nối gate này với `v0.7.0` finalization continuity
- tạo foundation cho review/approval chain về sau mà không mở implementation breadth

Các slice tiếp theo, nếu có, chỉ nên được đề xuất sau khi Slice A được implement, review, và xác nhận vẫn nằm trong controlled operationalization.

## 8. Risks and controls

### Risk 1 — `v1.0` drift thành breadth expansion
Kiểm soát:

- bám chặt scope Slice A
- mọi UI / routing / orchestration expansion đều defer

### Risk 2 — Gate semantics quá mơ hồ
Kiểm soát:

- buộc phải có gate definition, lifecycle placement, decision semantics, evidence model, và traceability model

### Risk 3 — Boundary với `v0.7.0` continuity không rõ
Kiểm soát:

- buộc mô tả continuity sau `finalization / closure record`
- buộc trace được về close-out chain của `v0.7.0`

## 9. Dependencies

Milestone này phụ thuộc vào:

- `ATP_v0_7_0_Freeze_Closeout.md`
- `ATP_v1_Major_Roadmap.md`
- `ATP_v1_0_Roadmap.md`
- current governance baseline của ATP
- docs design baseline cho artifact, handoff, request, run, runtime boundary

## 10. Deliverables proposed

Các deliverable chính của milestone trong current pass planning:

- `ATP_v1_0_Roadmap.md`
- `ATP_v1_0_Milestone_Proposal.md`
- `ATP_v1_0_Execution_Plan.md`
- bundle supporting docs cho `ATP_v1_0` Slice A

## 11. Acceptance logic for entering execution

Milestone `v1.0` được phép chuyển từ proposal sang execution khi:

- roadmap, major-roadmap, và stage-roadmap không mâu thuẫn nhau
- Slice A boundary rõ và không drift sang `v2`
- continuity sau `v0.7.0` được giải thích rõ
- execution plan có thể phân rã thành một bundle planning/implementation hẹp cho Slice A

## 12. Proposal decision

### Proposed decision
**Approve entry into `ATP v1.0` execution planning.**

### Rationale
`v1.0` là bước đúng để bắt đầu operational maturity của ATP sau khi `v0` đã hoàn tất foundational family. Slice A đủ hẹp, đúng maturity boundary, và phù hợp để làm first step của `v1`.

## 13. Immediate next step

Sau proposal này, tài liệu cần tạo tiếp theo là:

- `ATP_v1_0_Execution_Plan.md`
- bundle supporting docs cho `ATP_v1_0` Slice A
