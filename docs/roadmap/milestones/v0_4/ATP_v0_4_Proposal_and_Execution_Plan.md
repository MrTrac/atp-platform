# ATP v0.4 — Proposal và Execution Plan (Backfill)

> **Ghi chú về tài liệu này:**
> Đây là backfill documentation continuity cho milestone `v0.4`, được dựng lại từ evidence hiện có trong repo.
> Không có Proposal hay Execution Plan gốc được tạo ra tại thời điểm milestone này diễn ra theo format hiện hành;
> tài liệu này tái tạo từ archive reports và git history đã recover được.
> Mọi claim được ghi rõ mức độ chắc chắn.

---

## [PROPOSAL] Bối cảnh và mục tiêu

### Lý do milestone này tồn tại

**Suy luận hợp lý từ repo hiện tại, freeze closeout v0.3, và ATP v0 major roadmap.**

Sau ATP `v0.3.0` (external boundary / continuation / reference baseline), ATP cần hardening tầng
operational runtime — cụ thể là:

- current-task persistence: trạng thái của current task phải được ghi lại một cách explicit và coherent
- recovery contract: khi task cần tiếp tục, ATP phải có contract rõ để recovery (không chỉ có state)
- pointer traceability: active pointer và supersede trace để audit lineage của task
- read-only inspect surface: cho phép kiểm tra runtime artifacts mà không thay đổi chúng

`v0.4` là milestone đầu tiên ATP có đủ bốn lớp operational runtime hardening này trong một baseline coherent.

### Vấn đề hoặc evolution mà milestone này giải quyết

**Suy luận hợp lý từ `ATP_v0_Major_Roadmap.md` và `ATP_v0_4_0_Freeze_Closeout.md`.**

Sau `v0.3.0`, ATP có runtime materialization và external boundary, nhưng thiếu:

- Cơ chế để persist current-task state một cách tường minh (không chỉ ephemeral in-memory)
- Contract rõ ràng cho recovery khi task `continue_pending` cần được resume
- Traceability để biết task nào đang active, task nào đã supersede
- Surface read-only để operator/developer inspect runtime artifacts mà không side-effect

`v0.4` lấp các khoảng trống này, hardening operational runtime layer trên nền `v0.3.0`.

### Mục tiêu

- Xác lập current-task persistence contract tường minh
- Xây dựng continue-pending recovery contract (contract, không phải engine)
- Thêm active/supersede pointer traceability artifacts
- Xây dựng read-only inspect surface lên runtime artifacts đã materialize
- Giữ rõ ranh giới: persistence ≠ recovery execution; inspect ≠ write/modify

### In-scope

**Đã xác nhận từ `ATP_v0_4_0_Freeze_Closeout.md`:**

- Slice A: current-task persistence contract
- Slice B: continue-pending recovery contract
- Slice C: active/supersede pointer traceability
- Slice D: read-only inspect surface

### Out-of-scope

**Đã xác nhận từ `ATP_v0_4_0_Freeze_Closeout.md`:**

- production persistence redesign
- scheduler / queue behavior
- remote orchestration
- approval UI hoặc broad operator console
- generalized pointer/index/search subsystem
- recovery execution engine
- pointer cleanup hoặc management subsystem rộng

### Giả định và ràng buộc

**Suy luận hợp lý:**

- Kế thừa `v0.3.0` frozen baseline: exchange materialization, continuation, reference/index đã đúng
- Ranh giới: current-task persistence ≠ recovery contract; recovery contract ≠ recovery execution
- Active pointer và supersede trace chỉ là traceability artifacts, không phải pointer management subsystem
- Inspect surface chỉ là read-only view lên runtime artifacts đã materialize

### Quan hệ với mốc trước / mốc sau

- **Predecessor:** `v0.3` — external boundary / continuation / reference baseline; tag `v0.3.0`; lineage status: `documented`
- **Successor:** `v0.5` — continuity completion của v0 major family; lineage status: `documented`

---

## [EXECUTION PLAN] Kế hoạch thực thi

### Phạm vi thực thi

**Đã xác nhận — branch recover được từ merge commit.**

Thực thi diễn ra trên branch `v0.4-planning` (recover được với độ tin cậy cao từ merge commit
`6985db68...` — xem `ATP_v0_4_0_Freeze_Closeout.md` section 1).

### Workstreams / Slices

| Slice | Nội dung | Trạng thái tại freeze |
|---|---|---|
| Slice A | Current-task persistence contract: ghi lại current-task state tường minh | Đã xác nhận — trong freeze scope |
| Slice B | Continue-pending recovery contract: contract rõ để resume task (không phải recovery engine) | Đã xác nhận — trong freeze scope |
| Slice C | Active/supersede pointer traceability artifacts | Đã xác nhận — trong freeze scope |
| Slice D | Read-only inspect surface lên runtime artifacts đã materialize | Đã xác nhận — trong freeze scope |

### Deliverables

**Đã xác nhận từ archive reports:**

- Current-task persistence artifacts
- Recovery contract artifacts (không phải execution engine)
- Active pointer và supersede trace artifacts (traceability only)
- Read-only inspect surface
- Semantics rõ: persistence ≠ recovery execution; inspect ≠ write side
- Integration review: `ATP_v0_4_Integration_Review.md`
- Consolidation decision: `ATP_v0_4_Consolidation_Decision.md`
- Freeze closeout: `ATP_v0_4_0_Freeze_Closeout.md`

### Test / validation strategy

**Suy luận hợp lý từ freeze closeout; chi tiết test command không được lưu như freeze artifact riêng.**

Coverage đã xác nhận bao gồm:

- current-task persistence, recovery contract, active pointer, supersede trace, và inspect vẫn tách biệt semantics
- repo/workspace boundary vẫn đúng
- inspect surface vẫn read-only

Số lượng test chính xác và output transcript tại thời điểm freeze: **cần xác nhận thêm / không recover được**.

### Dependencies / risks

**Suy luận hợp lý:**

- Phụ thuộc vào `v0.3.0` frozen baseline (exchange, continuation, reference đã đúng)
- Rủi ro chính: blur ranh giới recovery contract / recovery execution — kiểm soát qua semantics rõ trong Slice B
- Rủi ro scope creep sang production persistence redesign, pointer cleanup, scheduler — được defer rõ

### Exit criteria

**Đã xác nhận từ archive reports:**

- Cả 4 slice (A-D) tạo thành operational runtime model nhất quán trên nền `v0.3.0`
- Không có scope creep sang production persistence redesign, scheduler/queue, UI, remote orchestration
- Integration review không có blocker kiến trúc
- Consolidation decision kết luận `consolidated baseline ready to freeze/integrate`
- Merge vào `main` và gắn annotated tag `v0.4.0`

---

## Tài liệu liên quan / nguồn chuẩn liên quan

- `docs/archive/reports/ATP_v0_4_Integration_Review.md` — integration review chính thức
- `docs/archive/reports/ATP_v0_4_Consolidation_Decision.md` — consolidation decision
- `docs/archive/reports/ATP_v0_4_0_Freeze_Closeout.md` — freeze closeout (nguồn chuẩn authority)
- `docs/roadmap/milestones/v0_4/ATP_v0_4_Freeze_and_Closeout.md` — freeze decision + closeout backfill
- `docs/roadmap/milestones/v0_3/` — milestone predecessor
- `docs/roadmap/stages/ATP_Practical_Milestone_Map.md`
