# AI Branch Operation Rules
## Bộ quy tắc vận hành cho AI theo từng branch và từng mức rủi ro Git

- **Version:** v1.0
- **Status:** Final-Reviewed
- **Date:** 2026-03-14

## 1. Mục tiêu

Tài liệu này dùng để:
- buộc AI luôn biết mình đang đứng trên branch nào
- buộc AI hành động đúng theo vai trò của branch đó
- tránh dùng cùng một AI context cho nhiều branch khác nhau
- chuẩn hóa quyền và giới hạn của AI khi commit / merge / tag / push
- giúp user chỉ approve ở các điểm thật sự quan trọng

## 2. Quy tắc nền tảng

- Mỗi branch quan trọng phải có ngữ cảnh riêng
- AI phải tự xác minh ngữ cảnh repo trước khi làm việc
- Branch quyết định quyền hành động của AI
- AI phải ưu tiên automation-first, nhưng approval-aware

## 3. Branch classes

### `main`
AI mode:
- read-heavy
- review-heavy
- merge-sensitive
- push-sensitive

AI không được tự ý:
- develop dài hạn trực tiếp
- merge branch vào `main`
- push `main`
- tag release

### `release/<version-context>`
AI mode:
- build-heavy
- test-heavy
- commit-allowed
- merge-prep-allowed

AI không được tự ý:
- merge vào `main`
- tag release chính thức
- push `main`

### `feature/<scope>`
AI mode:
- implementation-heavy
- commit-heavy
- merge-upward-prep

### `hotfix/<issue>`
AI mode:
- change-small
- test-critical
- merge-sensitive

## 4. Approval levels theo branch

- **L0** — read/check only
- **L1** — edit/test/commit on working branch
- **L2** — prepare merge/tag/push summary
- **L3** — high-risk action with explicit approval

Mapping mặc định:
- `main` → L0 đến L2
- `release/...` → L1 đến L2
- `feature/...` → L1
- `hotfix/...` → L1 đến L2

## 5. AI workflow theo branch

Khi bắt đầu phiên làm việc, AI phải xác minh:

```bash
git rev-parse --show-toplevel
git branch --show-current
git status
```

Khi chuẩn bị merge/tag/push `main`, AI phải:
- review diff
- chạy checks phù hợp
- tóm tắt action rõ ràng
- dừng để user approve

## 6. Stop conditions cho AI

AI phải dừng ngay nếu:
- branch hiện tại không khớp với ngữ cảnh nhiệm vụ
- working tree bẩn ngoài dự kiến
- diff vượt scope
- remote không đúng hoặc không rõ
- tests fail
- chưa có approval nhưng action đang là high-risk

## 7. Quy tắc workspace/chat cho AI

- Một branch quan trọng = một chat/workspace riêng
- Chat `main` dùng cho review baseline, merge readiness, tag/push planning
- Chat `release/...` dùng cho code, docs, tests, phase work
- Không tái sử dụng chat cũ cho branch mới nếu ngữ cảnh thay đổi lớn
