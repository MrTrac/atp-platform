# ATP v1.0 Slice A Execution Plan

## 1. Slice identity

- Version: `ATP v1.0`
- Slice: `Slice A`
- Slice title: `Review / Approval Gate Contract`
- Branch: `v1.0-planning`
- Status: `Implemented baseline, supporting-doc normalization pending consolidation`

## 2. Slice purpose

`ATP v1.0 Slice A` tồn tại để xác lập và giải thích một `review / approval gate contract` rõ ràng, bounded, traceable, và nối trực tiếp với lifecycle đã được chốt tại `v0.7.0`.

Slice này là bước operational maturity đầu tiên của `v1.0`. Nó không nhằm mở rộng ATP sang approval workflow implementation, mà nhằm làm rõ:

- ATP có explicit review / approval gate nào
- gate đó đứng ở đâu sau `finalization / closure record`
- gate đó ghi decision gì ở mức bounded
- gate đó cần evidence tối thiểu gì và được trace ra sao

## 3. Problem statement

Sau `v0.7.0`, ATP đã có foundational lifecycle chain tới mức `finalization / closure record`, nhưng chưa có một operational gate contract explicit để ghi nhận review / approval semantics ở mức file-based và governance-backed.

Nếu không chuẩn hóa gate này, ATP sẽ gặp các rủi ro sau:

- decision point tồn tại dưới dạng ngầm hiểu thay vì contract rõ
- khó xác định khi nào một lifecycle path được coi là đã qua review / approval gate
- khó chứng minh tại sao một outcome được approve, reject, defer, hoặc hold
- traceability giữa planning, evidence, gate decision, và close-out không đủ chặt

## 4. Slice objective

Slice A phải tạo ra một contract đủ rõ để trả lời:

1. ATP ghi explicit review / approval gate nào?
2. Gate đó nằm ở đâu sau `finalization / closure record` của `v0.7.0`?
3. Gate đó nhận input gì, dùng evidence gì, và ghi decision gì?
4. Gate đó nối lifecycle continuity hiện có như thế nào mà không drift sang UI hay orchestration rộng?

## 5. In-scope

Các nội dung nằm trong scope của Slice A:

### 5.1 Gate definition
- định nghĩa review / approval gate là gì trong ATP `v1`
- xác định purpose của gate này như một operational gate, không phải UI surface

### 5.2 Lifecycle placement
- xác định vị trí của gate ngay sau `finalization / closure record`
- mô tả pre-gate state, decision point, và resulting direction ở mức bounded

### 5.3 Gate contract semantics
- gate review subject là gì
- gate decision semantics là gì
- approval / reject / defer / hold semantics được hiểu bounded ra sao

### 5.4 Evidence and traceability
- evidence tối thiểu nào phải tồn tại
- gate decision phải trace được sang roadmap / plan / artifacts / review outcome / decision record nào

### 5.5 Acceptance and review logic
- điều kiện nào để Slice A được coi là explicit, usable, traceable, và ready cho integration review / consolidation pass

## 6. Out-of-scope

Slice A không bao gồm:

- approval UI
- recovery engine
- recovery execution
- provider selection
- provider arbitration
- routing logic
- cost-aware routing expansion
- topology-aware orchestration
- generalized orchestration
- portfolio orchestration
- distributed control
- broader implementation breadth ngoài gate contract semantics

## 7. Expected outputs

Slice A đã/phải tạo ra tối thiểu các output sau:

1. `ATP_v1_0_Slice_A_Gate_Contract.md`
2. `ATP_v1_0_Slice_A_Traceability_Model.md`
3. `ATP_v1_0_Slice_A_Acceptance_Criteria.md`
4. `ATP_v1_0_Slice_A_Review_Checklist.md`
5. `review-approval-gate-contract.json` được materialize dưới `SOURCE_DEV/workspace/atp-runs/<run-id>/manifests/`
6. execution plan này đã được normalize theo roadmap / proposal / execution baseline hiện hành

## 8. Execution tasks

### Task A1 — Normalize baseline
- rà sự nhất quán với `ATP_v1_Major_Roadmap.md`
- rà sự nhất quán với `ATP_v1_0_Roadmap.md`
- rà continuity với `ATP_v0_7_0_Freeze_Closeout.md`

### Task A2 — Define the gate
- viết định nghĩa ATP-level cho review / approval gate
- phân biệt gate này với freeze gate, close-out gate, và approval UI

### Task A3 — Place the gate in lifecycle
- mô tả gate nằm ở đâu sau `finalization / closure record`
- xác định pre-gate state và post-gate resulting direction

### Task A4 — Define decision semantics
- xác định approval / reject / defer / hold semantics
- xác định decision recording expectations

### Task A5 — Define evidence model
- xác định review subject
- xác định evidence tối thiểu
- xác định ownership và decision recording expectations

### Task A6 — Define traceability model
- xác định trace chain từ roadmap tới gate decision
- xác định review points, approval points, decision recording points, và trace anchors

### Task A7 — Normalize supporting docs for consolidation
- chốt tiêu chí explicit, usable, traceable, coherent, và boundary-safe cho Slice A
- align wording của bundle với contract implementation đã có
- giảm duplication giữa gate contract, traceability model, acceptance criteria, và checklist

## 9. Validation logic

Slice A chỉ được coi là đạt khi:

- gate được định nghĩa rõ, không mơ hồ
- gate có lifecycle placement rõ ràng sau `v0.7.0`
- gate semantics đủ bounded và không lấn sang implementation breadth
- evidence model đủ để review thật
- traceability model đủ để nối planning, evidence, decision, và continuity
- continuity với `v0.7.0` được giải thích nhất quán

## 10. Acceptance logic mức slice

Slice A chỉ nên được coi là ready cho integration review / consolidation pass khi:

- gate contract đã explicit
- traceability model đã operational
- acceptance criteria đã đủ chặt để pass/fail/defer/hold review
- review checklist đã đủ dùng để rà toàn bundle
- supporting docs không còn drift với implementation đã commit

## 11. Risks and controls

### Risk 1 — Gate definition quá abstract
Kiểm soát:
- buộc phải có pre-gate state, inputs, decision semantics, outputs, evidence, và traceability

### Risk 2 — Slice A bị nở sang approval workflow implementation
Kiểm soát:
- giữ boundary chặt, mọi UI / routing / orchestration breadth đều defer

### Risk 3 — Lifecycle placement vẫn mơ hồ
Kiểm soát:
- buộc mô tả explicit vị trí sau `v0.7.0 finalization / closure record`

### Risk 4 — Traceability không dùng được
Kiểm soát:
- gate phải nối được với artifact chain và decision chain cụ thể

## 12. Immediate next step

Sau execution plan này, bước kế tiếp đúng nhất là hoàn tất và normalize bundle tài liệu Slice A:

- `ATP_v1_0_Slice_A_Gate_Contract.md`
- `ATP_v1_0_Slice_A_Traceability_Model.md`
- `ATP_v1_0_Slice_A_Acceptance_Criteria.md`
- `ATP_v1_0_Slice_A_Review_Checklist.md`

Sau khi bundle này sạch và bounded, next step đúng là `ATP v1.0 Slice A integration review / consolidation pass`, không phải mở rộng scope mới.
