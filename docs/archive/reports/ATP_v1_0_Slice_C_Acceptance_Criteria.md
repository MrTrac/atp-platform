# ATP v1.0 Slice C Acceptance Criteria

## 1. Mục đích

Tài liệu này chốt tiêu chí để quyết định khi nào `ATP v1.0 Slice C` được coi là done ở mức supporting-doc bundle và ready cho integration review / consolidation pass.

## 2. Slice-level done criteria

Slice C chỉ được coi là done khi:

- continuity state contract đã explicit
- continuity state contract đã usable ở mức planning/decision semantics
- traceability model đã rõ và dùng được
- acceptance logic không mâu thuẫn với roadmap và Slice B freeze baseline
- boundary của Slice C được giữ chặt
- supporting docs không drift với contract đã implement

## 3. Explicitness criteria

Continuity state contract chỉ được coi là explicit khi:

- continuity state definition rõ
- continuity state purpose rõ
- lifecycle placement rõ
- pre-state inputs rõ
- bounded state semantics rõ
- `state_status` / `continuity_signal` / `close_or_continue` rõ
- non-goals / boundary guardrails rõ
- quan hệ với `final/continuation-state.json` rõ

Nếu thiếu một trong các mục trên, Slice C chưa đạt explicitness threshold.

## 4. Usability criteria

Continuity state chỉ được coi là usable khi:

- reviewer có thể hiểu state đang xác nhận cái gì
- reviewer biết state đang kế thừa follow-up nào
- reviewer biết state có thể ghi những semantics nào
- reviewer biết state đó sẽ được nối sang runtime continuity / decision state nào

## 5. Traceability criteria

Slice C chỉ đạt traceability khi:

- trace được từ `ATP_v1_Major_Roadmap.md`
- trace được từ `ATP_v1_0_Roadmap.md`
- trace được từ `ATP_v1_0_Slice_B_Freeze_Closeout.md`
- trace được từ `ATP_v1_0_Slice_C_Execution_Plan.md`
- trace được từ `ATP_v1_0_Slice_C_Continuity_State_Contract.md`
- trace được tới `ATP_v1_0_0_Freeze_Closeout.md`
- trace được tới `ATP_v0_7_0_Freeze_Closeout.md`
- trace được từ continuity state contract sang runtime continuity / decision state liên quan

## 6. Pass / fail / defer / hold criteria

### Pass
- continuity state semantics đầy đủ
- evidence model đủ
- traceability đầy đủ
- boundary control sạch

### Fail
- continuity state semantics mơ hồ
- lifecycle placement sai hoặc không rõ
- continuity với Slice B, Slice A, hoặc `v0.7.0` không chứng minh được
- boundary bị trôi sang UI / workflow / recovery / orchestration

### Defer
- framing đúng nhưng evidence model hoặc traceability model còn thiếu chi tiết quan trọng

### Hold
- có ambiguity đủ lớn khiến Slice C không nên đi tiếp sang consolidation dù chưa fail hoàn toàn

## 7. Boundary control criteria

Slice C chỉ đạt boundary control khi:

- không mô tả approval UI
- không mô tả workflow engine
- không mô tả recovery execution
- không mô tả routing/provider selection
- không mô tả generalized orchestration
- không nhập nhằng Slice C với Slice A gate hay Slice B follow-up
- không mô tả Slice C như bản thay thế cho `final/continuation-state.json`

## 8. Coherence criteria với roadmap layers

Slice C chỉ đạt coherence khi:

- không mâu thuẫn với `ATP_v1_Major_Roadmap.md`
- không mâu thuẫn với `ATP_v1_0_Roadmap.md`
- không mâu thuẫn với `ATP_Development_Stage_Roadmap.md`
- continuity với `ATP_v1_0_Slice_B_Freeze_Closeout.md` được giải thích rõ

## 9. Review completeness criteria

Review bundle của Slice C chỉ được coi là complete khi:

- execution plan đã được normalize
- continuity state contract đã có
- traceability model đã có
- acceptance criteria đã có
- review checklist đã có
- cross-document consistency đã được rà ít nhất một lượt
- contract implementation đã được phản ánh đúng ở mức supporting docs

## 10. Minimum artifact completeness criteria

Các artifact tối thiểu phải tồn tại:

- `ATP_v1_0_Slice_C_Execution_Plan.md`
- `ATP_v1_0_Slice_C_Continuity_State_Contract.md`
- `ATP_v1_0_Slice_C_Traceability_Model.md`
- `ATP_v1_0_Slice_C_Acceptance_Criteria.md`
- `ATP_v1_0_Slice_C_Review_Checklist.md`

## 11. Runtime alignment criteria

Slice C chỉ đạt runtime alignment khi supporting docs phản ánh đúng:

- `operational-continuity-gate-followup-state-contract.json`
- `state_scope = operational_continuity_gate_followup_state_only`
- `finalization_closure_record_ref`
- `review_approval_gate_ref`
- `gate_outcome_operational_followup_ref`
- `operational_continuity_state`
- `state_rationale`
- `traceability`
- bốn bounded semantics:
  - `approved_continuity_ready`
  - `rejected_continuity_closed`
  - `held_continuity_pending`
  - `deferred_continuity_deferred`

## 12. Artifact separation criteria

Slice C chỉ đạt artifact separation khi:

- supporting docs nêu rõ contract mới nằm dưới `manifests/`
- supporting docs nêu rõ `final/continuation-state.json` vẫn là runtime artifact khác lớp
- không có wording hợp nhất hai artifact thành một state engine

## 13. Final acceptance statement

Slice C chỉ nên được coi là accepted cho bước tiếp theo khi:

- bundle tài liệu đã đủ explicit, usable, traceable
- không còn mâu thuẫn nguồn chuẩn
- không còn scope drift đã biết
- next step hợp lệ là integration review / consolidation pass cho `Operational Continuity / Gate Follow-up State Contract`
