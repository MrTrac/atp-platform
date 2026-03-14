# ATP v1.0 Slice A Acceptance Criteria

## 1. Mục đích

Tài liệu này chốt tiêu chí để quyết định khi nào `ATP v1.0 Slice A` được coi là done ở mức supporting-doc bundle và ready cho integration review / consolidation pass.

## 2. Slice-level done criteria

Slice A chỉ được coi là done khi:

- gate contract đã explicit
- gate contract đã usable ở mức planning/decision semantics
- traceability model đã rõ và dùng được
- acceptance logic không mâu thuẫn với roadmap/proposal/plan baseline
- boundary của Slice A được giữ chặt
- supporting docs không drift với contract đã implement

## 3. Explicitness criteria

Gate contract chỉ được coi là explicit khi:

- gate definition rõ
- gate purpose rõ
- lifecycle placement rõ
- pre-gate state rõ
- gate inputs rõ
- decision semantics rõ
- gate status / resulting direction rõ
- non-goals / boundary guardrails rõ

Nếu thiếu một trong các mục trên, Slice A chưa đạt explicitness threshold.

## 4. Usability criteria

Gate chỉ được coi là usable khi:

- reviewer có thể hiểu gate đang xét cái gì
- reviewer biết gate cần evidence gì
- reviewer biết gate có thể ghi những decision nào
- reviewer biết decision đó sẽ được nối sang resulting direction / continuity / decision record nào

## 5. Traceability criteria

Slice A chỉ đạt traceability khi:

- trace được từ `ATP_v1_Major_Roadmap.md`
- trace được từ `ATP_v1_0_Roadmap.md`
- trace được từ `ATP_v1_0_Milestone_Proposal.md`
- trace được từ `ATP_v1_0_Execution_Plan.md`
- trace được từ `ATP_v1_0_Slice_A_Execution_Plan.md`
- trace được tới `ATP_v0_7_0_Freeze_Closeout.md`
- trace được từ gate contract sang review outcome, resulting direction, và decision record / continuation state

## 6. Pass / fail / defer / hold criteria

### Pass
- gate semantics đầy đủ
- evidence model đủ
- traceability đầy đủ
- boundary control sạch

### Fail
- gate semantics mơ hồ
- lifecycle placement sai hoặc không rõ
- continuity với `v0.7.0` không chứng minh được
- boundary bị trôi sang UI / routing / orchestration

### Defer
- framing đúng nhưng evidence model hoặc traceability model còn thiếu chi tiết quan trọng

### Hold
- có ambiguity đủ lớn khiến Slice A không nên đi tiếp sang consolidation dù chưa fail hoàn toàn

## 7. Boundary control criteria

Slice A chỉ đạt boundary control khi:

- không mô tả approval UI
- không mô tả recovery engine
- không mô tả routing/provider selection
- không mô tả generalized orchestration
- không biến gate thành workflow engine

## 8. Coherence criteria với roadmap layers

Slice A chỉ đạt coherence khi:

- không mâu thuẫn với `ATP_v1_Major_Roadmap.md`
- không mâu thuẫn với `ATP_v1_0_Roadmap.md`
- không mâu thuẫn với `ATP_Development_Stage_Roadmap.md`
- continuity với `v0.7.0` được giải thích rõ

## 9. Review completeness criteria

Review bundle của Slice A chỉ được coi là complete khi:

- execution plan đã được normalize
- gate contract đã có
- traceability model đã có
- acceptance criteria đã có
- review checklist đã có
- cross-document consistency đã được rà ít nhất một lượt
- contract implementation đã được phản ánh đúng ở mức supporting docs

## 10. Minimum artifact completeness criteria

Các artifact tối thiểu phải tồn tại:

- `ATP_v1_0_Slice_A_Execution_Plan.md`
- `ATP_v1_0_Slice_A_Gate_Contract.md`
- `ATP_v1_0_Slice_A_Traceability_Model.md`
- `ATP_v1_0_Slice_A_Acceptance_Criteria.md`
- `ATP_v1_0_Slice_A_Review_Checklist.md`

## 11. Final acceptance statement

Slice A chỉ nên được coi là accepted cho bước tiếp theo khi:

- bundle tài liệu đã đủ explicit, usable, traceable
- không còn mâu thuẫn nguồn chuẩn
- không còn scope drift đã biết
- next step hợp lệ là integration review / consolidation pass cho `Review / Approval Gate Contract`
