# ATP 3-Role Workflow
## Architect → Executor → Verifier

## 1. Mục đích

Tài liệu này chuẩn hóa workflow Multi-AI mặc định cho ATP đối với các phase quan trọng có ảnh hưởng đến:

- architecture
- governance
- contracts / schemas
- orchestration flow
- runtime boundary
- testing / validation
- release-readiness
- documentation bundles

Workflow chuẩn của ATP là mô hình 3 vai trò:

1. **ChatGPT = Architect / Governor**
2. **Codex = Primary Executor**
3. **Cursor = Independent Verifier**

Mục tiêu của mô hình này là:

- giữ ATP bám sát kiến trúc đã chốt
- giảm scope creep khi AI thực thi trực tiếp trên repo
- tách rời rõ vai trò thiết kế, thực thi, và kiểm định
- buộc mọi phase phải qua validation trước khi được coi là done
- tránh tình trạng một AI tự thiết kế, tự code, tự kết luận đúng

---

## 2. Phạm vi áp dụng

Workflow này **nên được áp dụng mặc định** cho các loại công việc sau:

- hardening pass
- architecture alignment
- docs normalization quy mô lớn
- schema / contract changes
- CLI contract changes
- orchestration flow updates
- validation / approval / finalization semantics
- release governance
- runtime boundary changes
- E2E test hardening

Workflow này **có thể rút gọn** đối với các thay đổi rất nhỏ, cục bộ, ít rủi ro, ví dụ:

- sửa typo
- chỉnh wording nhỏ trong docs
- fix test nhỏ không ảnh hưởng semantics rộng
- update comment hoặc metadata đơn giản

---

## 3. Vai trò chuẩn

### 3.1. ChatGPT = Architect / Governor

#### Nhiệm vụ chính
- hiểu bức tranh tổng thể của ATP
- bám các tài liệu authority
- xác định next task đúng với phase hiện tại
- chốt scope, guardrails, và Definition of Done
- viết prompt authority cho AI thực thi
- đọc lại kết quả từ executor và verifier
- kết luận phase:
  - done
  - conditionally done
  - not done
- xác định bước tiếp theo hợp lý nhất

#### Không dùng ChatGPT cho
- sửa code hàng loạt trực tiếp thay executor
- tự bỏ qua authority docs
- tự xác nhận phase done khi chưa có validation hoặc review đủ

---

### 3.2. Codex = Primary Executor

#### Nhiệm vụ chính
- thực thi chính trên repo
- đọc và bám chặt prompt authority
- chỉnh sửa code / docs / schemas / tests đúng scope
- tạo report files khi được yêu cầu
- chạy test / validation
- báo rõ:
  - file changed
  - fixes applied
  - deferred items
  - test results

#### Không dùng Codex để
- tự đổi kiến trúc
- tự mở rộng scope
- refactor lớn chỉ vì sở thích
- thay đổi semantics đã freeze mà không có chỉ đạo rõ

---

### 3.3. Cursor = Independent Verifier

#### Nhiệm vụ chính
- review độc lập sau khi executor hoàn tất
- kiểm tra alignment với frozen architecture
- kiểm tra boundary correctness
- kiểm tra semantics consistency
- kiểm tra diff discipline
- kiểm tra test confidence
- phát hiện:
  - scope creep
  - hidden redesign
  - over-editing
  - mismatch giữa report và repo state thật

#### Không dùng Cursor để
- phát triển song song cùng một task lớn ngay từ đầu nếu chưa phân vai
- âm thầm làm lại toàn bộ thay executor
- mở rộng phase khi nhiệm vụ đang là verification

---

## 4. Tài liệu authority bắt buộc

Mọi phase lớn của ATP phải bám theo thứ tự ưu tiên authority sau:

1. `README.md`
2. `docs/architecture/overview.md`
3. freeze decision record hiện hành
4. implementation plan hiện hành
5. active docs liên quan trong `docs/`
6. repo state thực tế nếu phù hợp với authority docs

Nếu có mâu thuẫn giữa repo state và authority docs:
- không tự ý chọn theo cảm tính
- phải ghi nhận thành issue / gap
- phải xử lý theo phase hardening hoặc clarification phù hợp

---

## 5. Quy trình chuẩn 6 bước

### Bước 1 — Architect chốt task
ChatGPT phải xác định rõ:

- phase hiện tại là gì
- mục tiêu chính là gì
- phạm vi được phép
- phạm vi không được phép
- Definition of Done
- guardrails
- prompt authority cho executor
- nếu cần: tiêu chí review cho verifier

#### Output tối thiểu
- task statement
- scope boundary
- DoD
- prompt authority

---

### Bước 2 — Executor thực thi
Codex thực hiện đúng prompt authority.

#### Yêu cầu
- đọc trước khi sửa
- không mở rộng scope
- ưu tiên precise diffs
- không đụng file không liên quan
- báo cáo trung thực

#### Output tối thiểu
- summary
- files changed
- report files
- test results
- deferred items

---

### Bước 3 — Thu thập output thực thi
Sau khi executor xong, cần thu tối thiểu:

- `git status`
- `git diff --stat`
- `git diff`
- danh sách file report mới tạo
- test output
- nếu có: commit hash hoặc patch snapshot

Đây là input chuẩn cho verifier.

---

### Bước 4 — Verifier review độc lập
Cursor review repo state sau executor.

#### Phạm vi review chuẩn
- architecture conformance
- repo/workspace boundary correctness
- schema/contract consistency
- approval/finalization/handoff semantics
- CLI contract correctness
- test relevance and adequacy
- diff discipline
- scope control

#### Output bắt buộc
- verdict
- grouped findings
- issue severity
- recommended correction
- fix-now vs defer

---

### Bước 5 — Xử lý sau review
#### Trường hợp PASS
- phase có thể được chốt
- chuẩn bị commit / tag / move next phase theo context

#### Trường hợp PASS WITH MINOR ISSUES
- chỉ sửa các điểm nhỏ cần thiết
- test lại phần liên quan
- rồi mới chốt phase

#### Trường hợp FAIL REQUIRES CORRECTION
- phase chưa được coi là done
- đưa findings quay lại executor
- sửa đúng các mục fail
- test lại
- nếu cần, review vòng ngắn thêm một lần

---

### Bước 6 — Architect chốt phase
ChatGPT đọc output từ executor + verifier rồi chốt:

- phase đã done hay chưa
- cái gì đạt
- cái gì chưa đạt
- cái gì defer
- next task là gì

Đây là bước cuối để tránh việc “test pass nhưng semantics vẫn sai”.

---

## 6. Verdict chuẩn

Verifier phải dùng đúng 3 mức verdict chuẩn sau:

### PASS
Phase đạt, có thể chốt.

### PASS WITH MINOR ISSUES
Phase đạt cơ bản, còn vài điểm nhỏ cần xử lý trước khi chốt.

### FAIL REQUIRES CORRECTION
Phase chưa đạt, không được coi là done.

Không dùng các kết luận mơ hồ kiểu:
- “mostly okay”
- “probably fine”
- “looks good enough”

ATP cần verdict rõ ràng, có thể hành động được.

---

## 7. Guardrails cố định

### Rule 1 — Không bỏ qua authority docs
Mọi phase lớn phải bám documents authority hiện hành.

### Rule 2 — Không silent scope expansion
Nếu task là hardening thì chỉ hardening.
Nếu task là docs normalization thì không tự chuyển thành redesign.

### Rule 3 — Không architecture redesign nếu chưa được yêu cầu
Mọi thay đổi kiến trúc phải là task riêng, explicit, và có phê duyệt rõ.

### Rule 4 — Mọi phase phải có validation
Một phase không được coi là done nếu chưa có test / validation phù hợp.

### Rule 5 — Docs phải qua self-review tối thiểu 2 vòng
- vòng 1: executor tạo/chỉnh
- vòng 2: verifier hoặc architect rà lại tính nhất quán

### Rule 6 — Không nhảy phase khi phase hiện tại chưa chốt
Không chuyển sang phase mới nếu:
- chưa có verdict rõ
- chưa xử lý các issue phải-fix
- chưa test lại phần liên quan

### Rule 7 — Ưu tiên minimal meaningful change
Sửa ít nhưng đúng trọng tâm tốt hơn sửa rộng nhưng rủi ro.

---

## 8. Khi nào dùng workflow đầy đủ, khi nào dùng workflow rút gọn

### Dùng đầy đủ 3 vai trò khi
- thay đổi liên quan architecture
- phase hardening
- schema/contracts
- orchestration flow
- governance quan trọng
- release-readiness
- docs bundle quan trọng
- runtime boundary
- testing semantics

### Có thể dùng workflow rút gọn khi
- fix typo
- wording nhỏ
- sửa test đơn giản, cô lập
- cập nhật metadata nhẹ

### Các dạng rút gọn có thể chấp nhận
- ChatGPT → Codex
- ChatGPT → Cursor

Tuy nhiên, với ATP, các phase core vẫn nên ưu tiên workflow đủ 3 vai trò.

---

## 9. Output tiêu chuẩn cho từng vai trò

### 9.1. Output chuẩn của Architect
- task name
- objective
- scope
- out-of-scope
- DoD
- guardrails
- prompt authority

### 9.2. Output chuẩn của Executor
- executive summary
- files changed
- reports created
- fixes applied
- deferred items
- tests run
- test results

### 9.3. Output chuẩn của Verifier
- verification verdict
- findings by category
- severity
- affected files
- fix-now vs defer
- trusted / not trusted conclusion

---

## 10. SOP ngắn gọn

### ATP Multi-AI SOP

#### Phase 1 — Architect
- ChatGPT xác định task
- ChatGPT viết prompt authority
- ChatGPT nêu DoD + guardrails

#### Phase 2 — Execute
- Codex thực hiện đúng prompt
- Codex tạo changes + reports + tests
- Codex không mở rộng scope

#### Phase 3 — Verify
- Cursor review độc lập
- Cursor chấm verdict
- Cursor chỉ ra drift / scope creep / thiếu coverage

#### Phase 4 — Close
- sửa các issue cần sửa
- test lại
- ChatGPT chốt done / not done
- mới sang phase tiếp theo

---

## 11. Mẫu workflow meta ngắn

Có thể dùng đoạn sau để nhắc AI khác tuân thủ ATP workflow:

> ATP standard workflow applies:
> - ChatGPT = architect/governor
> - Codex = primary executor
> - Cursor = independent verifier
>
> Execution order:
> 1. Architect defines task, scope, DoD, and guardrails
> 2. Executor performs the task and produces concrete changes + tests + reports
> 3. Verifier independently checks architecture alignment, boundary correctness, semantics, scope control, and test confidence
> 4. Only after verification may the phase be considered done
>
> Rules:
> - No silent scope expansion
> - No architecture redesign unless explicitly requested
> - Every phase requires validation/testing before closure
> - Docs and implementation must stay aligned with ATP frozen architecture

---

## 12. Áp dụng mặc định cho ATP

Từ thời điểm tài liệu này được chấp nhận, ATP nên mặc định áp dụng mô hình:

**Architect → Executor → Verifier**

cho mọi phase có ảnh hưởng đáng kể đến:

- docs authority
- code semantics
- orchestration logic
- contracts / schemas
- runtime boundary
- validation / approval / finalization logic
- release governance

---

## 13. Kết luận

ATP là một platform repo có kiến trúc và semantics cần được giữ ổn định.
Vì vậy, workflow Multi-AI của ATP không được để một AI duy nhất tự:

- thiết kế
- thực thi
- kiểm tra
- kết luận

Mô hình chuẩn của ATP là:

- **ChatGPT định hướng**
- **Codex thực thi**
- **Cursor kiểm định**
- **ChatGPT chốt phase**

Đây là workflow mặc định để giảm rủi ro lệch kiến trúc, scope creep, và false completion.