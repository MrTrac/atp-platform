# Safe Git Wrappers Spec
## Đặc tả cho bộ wrapper Git an toàn, tự động hóa cao và có approval points

- **Version:** v1.0
- **Status:** Final-Reviewed
- **Date:** 2026-03-14

## 1. Mục tiêu

Bộ wrapper này dùng để:
- giảm việc user phải nhớ tay từng lệnh Git
- gom pre-checks + summary + approval + post-checks vào cùng một flow
- tạo lớp automation an toàn cho AI và user
- ngăn merge/push/tag sai

## 2. Triết lý thiết kế

Wrappers phải:
- an toàn trước rồi mới nhanh
- ưu tiên check và summary trước action
- phân biệt low-risk vs high-risk actions
- dừng tại approval point đúng lúc
- luôn log rõ mình đang làm gì

## 3. Bộ wrapper đề xuất

- `safe-commit`
- `safe-merge-main`
- `safe-tag`
- `safe-push-branch`
- `safe-push-main`
- `safe-push-tag`

## 4. Wrapper behavior model

Mọi wrapper nên có cùng shape:

1. detect repo root
2. detect current branch
3. run pre-checks
4. run auto-checks
5. print summary
6. ask approval if needed
7. perform action
8. run post-checks
9. print final outcome

## 5. Output format chuẩn

Wrapper nên in:
- repo root
- current branch
- target branch/tag
- working tree status
- diff scope
- test/check result
- remote state if relevant
- approval prompt if needed
- final result

## 6. Approval interface model

Wrappers nên hỗ trợ:
- interactive mode
- non-interactive / AI-assisted mode

## 7. ATP-specific mapping

Compile/check:
```bash
python3 -m compileall cli core tests
```

Test:
```bash
make test
```

ATP approval defaults:
- commit on `main` → approval required
- merge into `main` → approval required
- push `main` → approval required
- push release tag → approval required

## 8. Suggested implementation roadmap

### Phase 1
- implement `safe-commit`
- implement `safe-push-branch`

### Phase 2
- implement `safe-merge-main`
- implement `safe-tag`

### Phase 3
- implement `safe-push-main`
- implement `safe-push-tag`

### Phase 4
- integrate project config + AI-friendly non-interactive mode

## 9. Kết luận

Bộ wrapper spec này là lớp chuyển từ governance sang hành động tự động hóa thật.
