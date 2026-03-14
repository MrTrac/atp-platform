# ATP v0.3 — Proposal và Execution Plan (Backfill)

> **Ghi chú về tài liệu này:**
> Đây là backfill documentation continuity cho milestone `v0.3`, được dựng lại từ evidence hiện có trong repo.
> Không có Proposal hay Execution Plan gốc được tạo ra tại thời điểm milestone này diễn ra theo format hiện hành;
> tài liệu này tái tạo từ archive reports và git history đã recover được.
> Mọi claim được ghi rõ mức độ chắc chắn.

---

## [PROPOSAL] Bối cảnh và mục tiêu

### Lý do milestone này tồn tại

**Suy luận hợp lý từ repo hiện tại và freeze closeout.**

Sau ATP `v0.2.0` (runtime materialization baseline), ATP cần mở rộng ra external boundary — cho phép ATP biết khi
nào một handoff vượt ra ngoài run-local context để trở thành external exchange candidate, đồng thời xây dựng:

- operational continuity state (`continue_pending`) ở mức runtime riêng
- minimal reference / index support file-based

`v0.3` là milestone đầu tiên ATP có cả bốn lớp: run-local handoff, external exchange materialization, operational
continuity, và reference/index — tất cả được tách biệt semantics rõ ràng.

### Vấn đề hoặc evolution mà milestone này giải quyết

**Suy luận hợp lý từ freeze closeout section 2 và follow-on direction của v0.2.**

`v0.2` defer các vấn đề sau sang `v0.3`:

- `exchange/` materialization: ATP chưa biết phân biệt run-local handoff với external exchange candidate
- `continue_pending`: chưa có runtime state riêng cho continuity
- reference/index support: chưa có file-based index cho exchange và continuation artifacts

`v0.3` giải quyết ba khoảng trống này, mở rộng baseline materialization ra external boundary mà không blur
ranh giới đã thiết lập ở `v0.2`.

### Mục tiêu

- Xác lập external boundary decision model tối thiểu: khi nào handoff là exchange candidate
- Materialize exchange artifacts dưới `SOURCE_DEV/workspace/exchange/current-task/<run-id>/`
- Xây dựng `continue_pending` operational continuity state ở mức runtime riêng
- Thêm minimal reference / index support file-based
- Giữ `final/` làm vùng chứa continuation, retention, và reference artifacts của current run
- Giữ `atp-artifacts/` chỉ dành cho authoritative projection

### In-scope

**Đã xác nhận từ `ATP_v0_3_0_Freeze_Closeout.md`:**

- Slice A: exchange boundary decision model
- Slice B: minimal exchange materialization dưới `SOURCE_DEV/workspace/exchange/current-task/<run-id>/` khi boundary yêu cầu
- Slice C: continue_pending operational continuity state
- Slice D: minimal file-based reference / index support

### Out-of-scope

**Đã xác nhận từ `ATP_v0_3_0_Freeze_Closeout.md`:**

- persistence redesign ở mức production
- generalized index / catalog subsystem
- search/query subsystem cho references
- queue, scheduler, hay continuation engine rộng
- approval UI
- remote orchestration
- broad workflow expansion hoặc operational automation

### Giả định và ràng buộc

**Suy luận hợp lý:**

- Kế thừa `v0.2.0` frozen baseline làm nền; run tree, handoff, authoritative projection giữ nguyên semantics
- Ranh giới: `run_local_handoff` ≠ `external_exchange_candidate`; `handoff/` ≠ `exchange/current-task/`
- `atp-artifacts/` vẫn chỉ dành cho authoritative projection — không mở rộng scope

### Quan hệ với mốc trước / mốc sau

- **Predecessor:** `v0.2` — runtime materialization baseline; tag `v0.2.0`; lineage status: `documented`
- **Successor:** `v0.4` — current-task persistence / recovery / pointer / inspect hardening
  Lineage status: `documented`

---

## [EXECUTION PLAN] Kế hoạch thực thi

### Phạm vi thực thi

**Đã xác nhận — branch recover được từ merge commit.**

Thực thi diễn ra trên branch `v0.3-planning` (recover được với độ tin cậy cao từ merge commit
`36b6a757...` — xem `ATP_v0_3_0_Freeze_Closeout.md` section 1).

### Workstreams / Slices

| Slice | Nội dung | Trạng thái tại freeze |
|---|---|---|
| Slice A | Exchange boundary decision model: xác định khi nào handoff là external exchange candidate | Đã xác nhận — trong freeze scope |
| Slice B | Exchange materialization tối thiểu dưới `exchange/current-task/<run-id>/` khi boundary yêu cầu | Đã xác nhận — trong freeze scope |
| Slice C | continue_pending operational continuity state ở mức runtime riêng | Đã xác nhận — trong freeze scope |
| Slice D | Minimal file-based reference / index support | Đã xác nhận — trong freeze scope |

### Deliverables

**Đã xác nhận từ archive reports:**

- Exchange boundary decision model (run-local vs external)
- Exchange materialization artifacts trong `exchange/current-task/`
- Continuation state artifacts cho `continue_pending`
- Reference/index artifacts file-based
- Semantics: `final/` chứa continuation + retention + reference; `atp-artifacts/` chỉ authoritative projection
- Integration review: `ATP_v0_3_Integration_Review.md`
- Consolidation decision: `ATP_v0_3_Consolidation_Decision.md`
- Freeze closeout: `ATP_v0_3_0_Freeze_Closeout.md`

### Test / validation strategy

**Suy luận hợp lý từ freeze closeout; chi tiết test command không được lưu như freeze artifact riêng.**

Coverage đã xác nhận bao gồm:

- exchange boundary decision, exchange payload, continuation state, và reference/index support vẫn tách biệt semantics
- repo/workspace boundary vẫn đúng
- traceability giữa exchange, continuation, manifest reference, và authoritative refs là coherent

Số lượng test chính xác và output transcript tại thời điểm freeze: **cần xác nhận thêm / không recover được**.

### Dependencies / risks

**Suy luận hợp lý:**

- Phụ thuộc vào `v0.2.0` frozen baseline (run tree, handoff, projection, retention đã đúng)
- Rủi ro chính: blur ranh giới `handoff/` và `exchange/current-task/` — kiểm soát qua semantics rõ trong Slice A
- Rủi ro scope creep sang continuation engine rộng — được defer rõ

### Exit criteria

**Đã xác nhận từ archive reports:**

- Cả 4 slice (A-D) tạo thành runtime model nhất quán trên nền `v0.2.0`
- Không có scope creep sang production persistence, scheduling, UI, remote orchestration
- Integration review không có blocker kiến trúc
- Consolidation decision kết luận `consolidated baseline ready to freeze/integrate`
- Merge vào `main` và gắn annotated tag `v0.3.0`

---

## Tài liệu liên quan / nguồn chuẩn liên quan

- `docs/archive/reports/ATP_v0_3_Integration_Review.md` — integration review chính thức
- `docs/archive/reports/ATP_v0_3_Consolidation_Decision.md` — consolidation decision
- `docs/archive/reports/ATP_v0_3_0_Freeze_Closeout.md` — freeze closeout (nguồn chuẩn authority)
- `docs/roadmap/milestones/v0_3/ATP_v0_3_Freeze_and_Closeout.md` — freeze decision + closeout backfill
- `docs/roadmap/milestones/v0_2/` — milestone predecessor
- `docs/roadmap/stages/ATP_Practical_Milestone_Map.md`
