# ATP v1.0 Slice B Acceptance Criteria

## 1. Mục đích

Tài liệu này chốt tiêu chí để quyết định khi nào `ATP v1.0 Slice B` được coi là done ở mức supporting-doc bundle và ready cho integration review / consolidation pass.

## 2. Slice-level done criteria

Slice B chỉ được coi là done khi:

- follow-up contract đã explicit
- follow-up contract đã usable ở mức planning/decision semantics
- traceability model đã rõ và dùng được
- acceptance logic không mâu thuẫn với roadmap và Slice A freeze baseline
- boundary của Slice B được giữ chặt
- supporting docs không drift với contract đã implement

## 3. Explicitness criteria

Follow-up contract chỉ được coi là explicit khi:

- follow-up definition rõ
- follow-up purpose rõ
- lifecycle placement rõ
- pre-follow-up state rõ
- follow-up inputs rõ
- bounded follow-up semantics rõ
- follow-up status / continuity signal rõ
- non-goals / boundary guardrails rõ

Nếu thiếu một trong các mục trên, Slice B chưa đạt explicitness threshold.

## 4. Usability criteria

Follow-up chỉ được coi là usable khi:

- reviewer có thể hiểu follow-up đang xác nhận cái gì
- reviewer biết follow-up đang kế thừa gate nào
- reviewer biết follow-up có thể ghi những semantics nào
- reviewer biết follow-up đó sẽ được nối sang continuity signal / decision state nào

## 5. Traceability criteria

Slice B chỉ đạt traceability khi:

- trace được từ `ATP_v1_Major_Roadmap.md`
- trace được từ `ATP_v1_0_Roadmap.md`
- trace được từ `ATP_v1_0_0_Freeze_Closeout.md`
- trace được từ `ATP_v1_0_Slice_B_Execution_Plan.md`
- trace được từ `ATP_v1_0_Slice_B_Followup_Contract.md`
- trace được tới `ATP_v0_7_0_Freeze_Closeout.md`
- trace được từ follow-up contract sang continuity signal và decision state liên quan

## 6. Pass / fail / defer / hold criteria

### Pass
- follow-up semantics đầy đủ
- evidence model đủ
- traceability đầy đủ
- boundary control sạch

### Fail
- follow-up semantics mơ hồ
- lifecycle placement sai hoặc không rõ
- continuity với Slice A hoặc `v0.7.0` không chứng minh được
- boundary bị trôi sang UI / workflow / orchestration

### Defer
- framing đúng nhưng evidence model hoặc traceability model còn thiếu chi tiết quan trọng

### Hold
- có ambiguity đủ lớn khiến Slice B không nên đi tiếp sang consolidation dù chưa fail hoàn toàn

## 7. Boundary control criteria

Slice B chỉ đạt boundary control khi:

- không mô tả approval UI
- không mô tả workflow engine
- không mô tả recovery execution
- không mô tả routing/provider selection
- không mô tả generalized orchestration

## 8. Coherence criteria với roadmap layers

Slice B chỉ đạt coherence khi:

- không mâu thuẫn với `ATP_v1_Major_Roadmap.md`
- không mâu thuẫn với `ATP_v1_0_Roadmap.md`
- không mâu thuẫn với `ATP_Development_Stage_Roadmap.md`
- continuity với `ATP_v1_0_0_Freeze_Closeout.md` được giải thích rõ

## 9. Review completeness criteria

Review bundle của Slice B chỉ được coi là complete khi:

- execution plan đã được normalize
- follow-up contract đã có
- traceability model đã có
- acceptance criteria đã có
- review checklist đã có
- cross-document consistency đã được rà ít nhất một lượt
- contract implementation đã được phản ánh đúng ở mức supporting docs

## 10. Minimum artifact completeness criteria

Các artifact tối thiểu phải tồn tại:

- `ATP_v1_0_Slice_B_Execution_Plan.md`
- `ATP_v1_0_Slice_B_Followup_Contract.md`
- `ATP_v1_0_Slice_B_Traceability_Model.md`
- `ATP_v1_0_Slice_B_Acceptance_Criteria.md`
- `ATP_v1_0_Slice_B_Review_Checklist.md`

## 11. Runtime alignment criteria

Slice B chỉ đạt runtime alignment khi supporting docs phản ánh đúng:

- `gate-outcome-operational-followup-contract.json`
- `followup_scope = gate_outcome_operational_followup_only`
- `finalization_closure_record_ref`
- `review_approval_gate_ref`
- `gate_outcome_or_operational_followup`
- `followup_rationale`
- `traceability`
- bốn bounded semantics:
  - `approved_operational_followup`
  - `rejected_operational_followup`
  - `held_operational_followup`
  - `deferred_operational_followup`

## 12. Final acceptance statement

Slice B chỉ nên được coi là accepted cho bước tiếp theo khi:

- bundle tài liệu đã đủ explicit, usable, traceable
- không còn mâu thuẫn nguồn chuẩn
- không còn scope drift đã biết
- next step hợp lệ là integration review / consolidation pass cho `Gate Outcome / Operational Follow-up Contract`
