# ATP v1.0 Execution Plan

## 1. Execution identity

- Milestone: `ATP v1.0`
- Target version: `v1.0.0`
- Planning branch: `v1.0-planning`
- Status: `Planned`

---

## 2. Execution objective

Mục tiêu của execution plan này là biến roadmap và proposal của `ATP v1.0` thành chuỗi thực thi có kiểm soát, có gate, có validation, và có điều kiện freeze rõ ràng.

Execution của `v1.0` phải bảo đảm:

- không drift khỏi baseline intent
- không mở rộng scope không kiểm soát
- có validation sau mỗi phase chính
- có bằng chứng đủ để freeze và close-out

---

## 3. Execution principles

Toàn bộ execution của `v1.0` tuân theo các nguyên tắc sau:

1. Baseline first, expansion later.
2. Governance clarity quan trọng hơn tốc độ.
3. Mọi phase hoàn thành đều phải có test/validation step.
4. Mọi tài liệu chính phải được self-review ít nhất hai lượt trước khi coi là ready.
5. Mọi thay đổi ảnh hưởng ATP structure/rules phải cập nhật `README.md` tại đúng vị trí liên quan.
6. Chỉ freeze khi evidence chain đầy đủ và nhất quán.
7. Không để active docs, roadmap docs, archive docs, và close-out docs mâu thuẫn nhau.

---

## 4. Planned execution phases

## Phase 0 — Planning baseline lock

### Purpose
Khóa planning baseline cho `v1.0`.

### Tasks
- tạo `ATP_v1_0_Roadmap.md`
- tạo `ATP_v1_0_Milestone_Proposal.md`
- tạo `ATP_v1_0_Execution_Plan.md`
- rà soát alignment giữa 3 tài liệu này
- xác nhận in-scope / out-of-scope rõ ràng

### Outputs
- roadmap hoàn chỉnh
- milestone proposal hoàn chỉnh
- execution plan hoàn chỉnh

### Validation
- 3 tài liệu không mâu thuẫn nhau
- strategic intent nhất quán
- slice structure rõ ràng
- scope boundary đủ chặt

### Exit criteria
- planning baseline sạch, coherent, reviewable

---

## Phase 1 — Governance baseline implementation

### Purpose
Operationalize governance thành rule vận hành cụ thể cho ATP.

### Tasks
- chuẩn hóa definition of done ở level phase và version
- chuẩn hóa freeze gate / close-out gate
- chuẩn hóa rule cập nhật `README.md`
- chuẩn hóa rule branch/freeze/merge baseline cho ATP
- rà soát và chỉnh các tài liệu governance liên quan

### Outputs
- governance docs / rule docs đã được cập nhật
- definition of done được ghi rõ
- freeze / close-out conditions được mô tả rõ

### Validation
- rule có thể dùng để ra quyết định thật, không chỉ là mô tả
- không có mâu thuẫn giữa governance docs và roadmap/proposal
- README system phản ánh đúng thay đổi

### Exit criteria
- governance baseline đủ rõ để điều khiển các phase sau

---

## Phase 2 — Documentation system baseline normalization

### Purpose
Ổn định docs system để giảm drift và tăng khả năng scale.

### Tasks
- rà soát docs tree liên quan đến ATP governance / roadmap / archive / templates
- chuẩn hóa naming / placement / reference logic
- rà soát link consistency
- giảm overlap hoặc ambiguity giữa active docs và archive docs
- cập nhật README tại các điểm bị ảnh hưởng

### Outputs
- docs structure được chuẩn hóa hơn
- references mạch lạc hơn
- giảm drift giữa các lớp tài liệu

### Validation
- document map rõ ràng hơn trước
- references không gãy
- narrative giữa active docs, roadmap, archive, close-out nhất quán

### Exit criteria
- docs system đạt baseline coherence chấp nhận được

---

## Phase 3 — Runtime / orchestration baseline clarification

### Purpose
Làm rõ baseline contract của core ATP orchestration.

### Tasks
- xác định rõ core orchestration flow
- mô tả boundary giữa doctrine / orchestration / execution artifacts / evidence
- chuẩn hóa mô tả structure hoặc implementation baseline nếu cần
- rà soát consistency giữa kiến trúc logic và docs

### Outputs
- tài liệu mô tả contract / boundary rõ hơn
- baseline structure đủ để review, test, và mở rộng

### Validation
- boundary không mơ hồ
- flow cốt lõi có thể giải thích nhất quán
- core model không xung đột với governance/docs baselines

### Exit criteria
- core ATP baseline đủ rõ để làm nền cho `v1.x`

---

## Phase 4 — Testing / validation baseline establishment

### Purpose
Đặt validation thành gate chính thức của ATP version lifecycle.

### Tasks
- xác định validation criteria tối thiểu cho các output chính
- xác định proof set / evidence set cho pre-freeze
- chuẩn hóa self-review expectations cho tài liệu
- chuẩn hóa logic “done only after validation”

### Outputs
- validation criteria
- proof/evidence expectations
- review and validation logic cho freeze readiness

### Validation
- evidence model đủ để hỗ trợ freeze decision
- phase completion logic rõ ràng
- không có deliverable chính nào thiếu validation expectation

### Exit criteria
- ATP có baseline validation gate dùng được ở mức version

---

## Phase 5 — Pre-freeze integration review

### Purpose
Đánh giá toàn cục `v1.0` trước khi freeze.

### Tasks
- rà soát coherence giữa governance, docs, runtime, validation
- rà soát README updates
- rà soát scope integrity
- rà soát out-of-scope contamination
- tổng hợp freeze readiness assessment

### Outputs
- integration review
- freeze readiness assessment
- danh sách blocker / non-blocker nếu có

### Validation
- mọi nhóm deliverable liên kết logic với nhau
- không còn drift nghiêm trọng
- evidence đủ để ra quyết định freeze

### Exit criteria
- `v1.0` được đánh giá freeze-ready hoặc có list blocker rõ

---

## Phase 6 — Freeze decision and close-out

### Purpose
Khóa version theo chuẩn ATP version lifecycle.

### Tasks
- tạo freeze decision record
- chốt trạng thái version
- tạo close-out document
- bảo đảm archive/active docs coherence tại thời điểm freeze
- chuẩn bị merge sạch vào `main`
- chuẩn bị tag `v1.0.0`

### Outputs
- `ATP_v1_0_Freeze_Decision_Record`
- `ATP_v1_0_Closeout`
- trạng thái version sẵn sàng merge/tag

### Validation
- freeze decision có rationale rõ
- close-out phản ánh đúng trạng thái version
- main-ready state có thể chứng minh được

### Exit criteria
- `v1.0` đủ điều kiện merge vào `main` và tag chính thức

---

## 5. Slice-to-phase mapping

### Slice A — Governance and version-control baseline
Đi qua chủ yếu:
- Phase 1
- một phần Phase 5
- một phần Phase 6

### Slice B — Documentation baseline
Đi qua chủ yếu:
- Phase 2
- một phần Phase 5
- một phần Phase 6

### Slice C — Runtime / orchestration baseline
Đi qua chủ yếu:
- Phase 3
- một phần Phase 5

### Slice D — Testing / validation baseline
Đi qua chủ yếu:
- Phase 4
- một phần Phase 5
- một phần Phase 6

---

## 6. Control gates

## Gate G0 — Planning gate
Điều kiện qua gate:
- roadmap / proposal / execution plan đầy đủ
- scope boundary rõ
- slices rõ

## Gate G1 — Governance gate
Điều kiện qua gate:
- definition of done rõ
- freeze / close-out logic rõ
- README update rule được phản ánh trong docs liên quan

## Gate G2 — Documentation coherence gate
Điều kiện qua gate:
- docs tree / references đủ nhất quán
- active vs archive vs roadmap không drift nghiêm trọng

## Gate G3 — Core baseline gate
Điều kiện qua gate:
- orchestration contract / boundary đủ rõ
- core ATP model có thể review/test được

## Gate G4 — Validation gate
Điều kiện qua gate:
- validation criteria rõ
- evidence model đủ dùng
- phase-completion logic đã gắn với validation

## Gate G5 — Freeze readiness gate
Điều kiện qua gate:
- integration review pass
- không còn blocker nghiêm trọng
- freeze decision có cơ sở rõ

---

## 7. Required evidence

Để `v1.0` được freeze, cần tối thiểu các nhóm evidence sau:

1. Planning evidence
- roadmap
- proposal
- execution plan

2. Governance evidence
- definition of done
- freeze/close-out logic
- rule updates liên quan

3. Documentation evidence
- docs normalization outputs
- reference consistency evidence
- README updates tương ứng

4. Runtime / orchestration evidence
- contract/boundary clarification artifacts
- consistency proof với ATP logic tổng thể

5. Validation evidence
- review records
- checklist / validation outputs
- freeze readiness assessment

6. Closure evidence
- freeze decision record
- close-out document
- main/tag readiness proof

---

## 8. Roles of review within execution

Trong `v1.0`, review không phải bước phụ. Review là một phần của execution logic.

### Review layer 1 — Artifact self-review
Mỗi tài liệu chính phải được rà ít nhất hai lượt trước khi coi là ready.

### Review layer 2 — Cross-document consistency review
Phải rà tính nhất quán giữa roadmap, proposal, execution plan, governance docs, README, archive, close-out.

### Review layer 3 — Freeze-readiness review
Phải có integration review trước freeze decision.

---

## 9. Risk handling during execution

### Risk handling rule 1
Nếu có dấu hiệu scope creep, ưu tiên cắt scope hơn là làm milestone phình ra.

### Risk handling rule 2
Nếu governance clarity chưa đạt, không chuyển sang freeze.

### Risk handling rule 3
Nếu docs còn drift rõ ràng, không chấp nhận close-out.

### Risk handling rule 4
Nếu validation evidence chưa đủ, phase chưa được coi là done.

### Risk handling rule 5
Nếu một thay đổi ảnh hưởng system-level docs mà chưa cập nhật README, phase đó chưa hoàn tất.

---

## 10. Completion criteria

Execution plan này được xem là hoàn tất thành công khi:

- toàn bộ phases đã đi qua với validation tương ứng
- scope không bị drift khỏi baseline intent
- governance baseline đủ rõ
- docs baseline đủ nhất quán
- runtime/orchestration baseline đủ rõ
- validation baseline đủ dùng cho version lifecycle
- freeze decision và close-out được lập đúng chuẩn
- branch sẵn sàng merge sạch vào `main`
- version sẵn sàng tag `v1.0.0`

---

## 11. Immediate execution order

Thứ tự thực hiện khuyến nghị:

1. Phase 1 — Governance baseline
2. Phase 2 — Documentation baseline
3. Phase 3 — Runtime / orchestration baseline
4. Phase 4 — Testing / validation baseline
5. Phase 5 — Pre-freeze integration review
6. Phase 6 — Freeze decision and close-out

Lưu ý:  
Phase 2, 3, 4 có thể giao thoa một phần, nhưng governance baseline nên được chốt trước để làm luật điều khiển các phase còn lại.

---

## 12. Next actionable step

Sau khi execution plan này được tạo, bước thực thi đầu tiên đúng nhất là:

**mở Slice A / Phase 1: Governance baseline implementation**

Cụ thể:
- chốt definition of done
- chốt freeze / close-out gate
- chốt README update rule ở dạng vận hành rõ ràng
- rà tài liệu governance liên quan để update đồng bộ
