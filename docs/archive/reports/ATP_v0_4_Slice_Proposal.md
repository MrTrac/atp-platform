# ATP v0.4 Slice Proposal

## 1. Nguyên tắc chia slice

- mỗi slice chỉ chốt một semantic gap rõ ràng
- ưu tiên contract clarity trước surface expansion
- giữ mọi thứ ở mức file-based, deterministic, testable
- không trộn persistence redesign, scheduling, UI, hay remote orchestration vào cùng phase

## 2. Slice structure đề xuất

## Slice A — Current-task persistence contract

### Mục tiêu

Chốt contract tối thiểu cho current-task state dưới workspace:

- file nào là active pointer
- file nào là current payload root
- rule nào xác định replacement / supersede

### Nội dung

- định nghĩa current-task persistence semantics ở mức hẹp
- không tạo database hay registry subsystem
- không thêm background process

### Giá trị

Đây là lát cắt đầu tiên cần có, vì toàn bộ recovery/resume semantics phụ thuộc vào current-task contract này.

## Slice B — Continue-pending recovery state

### Mục tiêu

Làm rõ entry point và recovery contract cho `continue_pending`.

### Nội dung

- chốt resume/recovery representation tối thiểu
- gắn rõ với exchange boundary decision, exchange state, và continuation state hiện có
- không thêm workflow state mới

### Giá trị

Slice này biến continuation từ “traceable” thành “recoverable ở mức operational tối thiểu”.

## Slice C — Supersede / active pointer traceability

### Mục tiêu

Làm rõ current-task nào đang active và current-task nào đã bị supersede, đồng thời vẫn giữ audit trail.

### Nội dung

- current pointer semantics
- supersede marker hoặc close-out marker ở mức tối thiểu
- traceability giữa active pointer và originating run

### Giá trị

Slice này giúp tránh mơ hồ khi current-task bị thay thế bởi run mới, nhưng vẫn chưa mở thành generalized indexing subsystem.

## Slice D — Optional inspect surface

### Mục tiêu

Thêm inspect/read surface rất nhỏ nếu cần để operator lần current-task và resume entry point dễ hơn.

### Nội dung

- CLI read-only hoặc summary output nhỏ
- không thêm operator console, UI, hay orchestration surface

### Giá trị

Đây là slice conditional. Chỉ nên làm nếu thiếu surface này thì persistence/recovery contract khó dùng hoặc khó test.

## 3. Thứ tự khuyến nghị

Thứ tự khuyến nghị cho v0.4:

1. Slice A
2. Slice B
3. Slice C
4. Slice D nếu cần

Lý do:

- A chốt persistence contract nền
- B làm rõ recovery behavior
- C làm rõ active/superseded traceability
- D chỉ thêm surface nhỏ khi contract bên dưới đã ổn

## 4. Cái gì không nằm trong slice proposal này

Không thuộc v0.4 proposal này:

- database hoặc persistence redesign rộng
- queue / scheduler
- remote orchestration
- approval UI
- generalized index/search subsystem
- broad operational automation

## 5. Exit criteria cấp phase cho v0.4

v0.4 nên được coi là hoàn tất nếu đạt:

- current-task persistence contract tối thiểu nhưng rõ ràng
- `continue_pending` có recovery/resume contract hẹp nhưng nhất quán
- active và superseded current-task được trace rõ
- boundary `SOURCE_DEV/platforms/ATP` vs `SOURCE_DEV/workspace` vẫn không bị blur
- không có scope creep sang production persistence hay orchestration expansion

## 6. Kết luận

Slice proposal tốt nhất cho v0.4 là một chuỗi ngắn xoay quanh **current-task persistence and recovery hardening**.

Nếu giữ đúng kỷ luật slice như trên, v0.4 sẽ là bước nối tự nhiên sau v0.3 mà vẫn giữ ATP ở đúng shape-correct discipline.
