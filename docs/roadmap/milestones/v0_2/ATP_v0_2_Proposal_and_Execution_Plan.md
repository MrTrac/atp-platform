# ATP v0.2 — Proposal và Execution Plan (Backfill)

> **Ghi chú về tài liệu này:**
> Đây là backfill documentation continuity cho milestone `v0.2`, được dựng lại từ evidence hiện có trong repo.
> Không có Proposal hay Execution Plan gốc được tạo ra tại thời điểm milestone này diễn ra; tài liệu này
> tái tạo các nội dung tương đương từ archive reports và git history đã recover được.
> Mọi claim được ghi rõ mức độ chắc chắn.

---

## [PROPOSAL] Bối cảnh và mục tiêu

### Lý do milestone này tồn tại

**Suy luận hợp lý từ repo hiện tại.**

Sau ATP `v0.1` (hardening baseline đầu tiên với shape-correct MVP), ATP cần xác lập một runtime materialization
baseline tối thiểu, có kiểm soát, để đưa các artifacts thực thi vào cấu trúc file-based dưới `SOURCE_DEV/workspace/`.

`v0.2` là milestone đầu tiên mà runtime output của ATP — run tree, handoff, authoritative projection, và retention
semantics — được định nghĩa rõ trong một model coherent, không chỉ tồn tại trong memory hay process-local state.

### Vấn đề hoặc evolution mà milestone này giải quyết

**Suy luận hợp lý từ archive reports.**

Trước `v0.2`, ATP thiếu:

- cấu trúc run tree file-based rõ dưới `SOURCE_DEV/workspace/atp-runs/<run-id>/`
- handoff materialization tối thiểu explicit
- authoritative projection tách biệt với run-local artifacts
- retention semantics tường minh, không tự động xóa

`v0.2` đặt nền để các milestone sau (`v0.3+`) có thể build tiếp trên runtime model đã có boundary rõ.

### Mục tiêu

- Xác lập consolidated runtime materialization baseline tối thiểu dưới `SOURCE_DEV/workspace/`
- Phân tách rõ: run tree, handoff, authoritative projection, retention
- Giữ repo/workspace boundary không bị blur
- Đạt trạng thái `consolidated baseline ready to freeze/integrate`

### In-scope

**Đã xác nhận từ `ATP_v0_2_0_Freeze_Closeout.md`:**

- Slice 1: run tree materialization dưới `SOURCE_DEV/workspace/atp-runs/<run-id>/`
- Slice 2: handoff materialization tối thiểu trong `handoff/`
- Slice 3: authoritative projection tối thiểu dưới `SOURCE_DEV/workspace/atp-artifacts/<artifact-id>/`
- Slice 4: retention / cleanup semantics tối thiểu, explicit, không auto-delete

### Out-of-scope

**Đã xác nhận từ `ATP_v0_2_0_Freeze_Closeout.md`:**

- `exchange/` materialization cho external handoff boundary
- continue_pending operational continuity state ở mức runtime riêng
- reference / index support file-based cho exchange và continuation
- persistence redesign ở mức production
- approval UI
- remote orchestration plane hoàn chỉnh
- advanced scheduling
- broad artifact lifecycle management hoặc cleanup automation

### Quan hệ với mốc trước / mốc sau

- **Predecessor:** `v0.1` — hardening baseline đầu tiên cho ATP shape-correct MVP
  - Lineage status: `inferred`; branch lineage v0.1 `needs confirmation` theo Practical Milestone Map
- **Successor:** `v0.3` — external boundary / continuation / reference completion baseline
  - Lineage status: `documented`

---

## [EXECUTION PLAN] Kế hoạch thực thi

### Phạm vi thực thi

**Suy luận hợp lý từ structure của Slices trong freeze closeout.**

Thực thi diễn ra trên branch `v0.2-slice4-retention-cleanup` (tên branch recover được với độ tin cậy cao
từ merge commit `022b18fb...` — xem `ATP_v0_2_0_Freeze_Closeout.md` section 1).

### Workstreams / Slices

| Slice | Nội dung | Trạng thái tại freeze |
|---|---|---|
| Slice 1 | Run tree materialization: tạo cấu trúc thư mục run dưới `atp-runs/<run-id>/` | Đã xác nhận — trong freeze scope |
| Slice 2 | Handoff materialization tối thiểu trong `handoff/` | Đã xác nhận — trong freeze scope |
| Slice 3 | Authoritative projection tối thiểu trong `atp-artifacts/<artifact-id>/` với traceability metadata | Đã xác nhận — trong freeze scope |
| Slice 4 | Retention / cleanup semantics tối thiểu, explicit, không auto-delete | Đã xác nhận — trong freeze scope |

### Deliverables

**Đã xác nhận từ archive reports:**

- Runtime materialization model cho run tree, handoff, authoritative projection, và retention
- Traceability metadata trong authoritative projection path
- Boundary semantics: run-local, handoff, authoritative projection là các lớp tách biệt
- Integration review: `ATP_v0_2_Integration_Review.md`
- Consolidation decision: `ATP_v0_2_Consolidation_Decision.md`
- Freeze closeout: `ATP_v0_2_0_Freeze_Closeout.md`

### Test / validation strategy

**Suy luận hợp lý từ freeze closeout; chi tiết test command không được lưu như freeze artifact riêng.**

Coverage đã xác nhận bao gồm:

- runtime root resolution
- run tree zone creation
- handoff materialization
- authoritative projection path và traceability metadata
- retention semantics cho close path và continue path ở mức hẹp
- happy path / reject path integration với isolated workspace

Số lượng test chính xác và output transcript tại thời điểm freeze: **cần xác nhận thêm / không recover được**.

### Dependencies / risks

**Suy luận hợp lý:**

- Phụ thuộc vào `v0.1` baseline đã đủ shape-correct để build tiếp
- Rủi ro chính: blur ranh giới repo/workspace — đã được kiểm soát qua integration review
- Rủi ro scope creep sang exchange materialization — được defer rõ sang `v0.3`

### Exit criteria

**Đã xác nhận — theo archive reports:**

- Cả 4 slice tạo thành runtime model nhất quán, đúng boundary
- Integration review không có blocker kiến trúc
- Consolidation decision kết luận `consolidated baseline ready to freeze/integrate`
- Không có scope creep được xác định
- Merge vào `main` và gắn annotated tag `v0.2.0`

---

## Tài liệu liên quan / nguồn chuẩn liên quan

- `docs/archive/reports/ATP_v0_2_Integration_Review.md` — integration review chính thức
- `docs/archive/reports/ATP_v0_2_Consolidation_Decision.md` — consolidation decision
- `docs/archive/reports/ATP_v0_2_0_Freeze_Closeout.md` — freeze closeout (nguồn chuẩn authority)
- `docs/roadmap/milestones/v0_2/ATP_v0_2_Freeze_and_Closeout.md` — freeze decision + closeout backfill
- `docs/roadmap/stages/ATP_Practical_Milestone_Map.md`
- `docs/governance/framework/ATP_Version_Lineage_and_Documentation_Continuity_Rule.md`
