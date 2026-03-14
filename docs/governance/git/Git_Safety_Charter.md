# Git Safety Charter
## Chuẩn an toàn Git cho ATP và các dự án phát triển có AI hỗ trợ

- **Version:** v1.0
- **Status:** Final-Reviewed
- **Date:** 2026-03-14

## 1. Mục tiêu

Git Safety Charter tồn tại để:

- giữ `main` là nhánh tích hợp sạch, mới nhất, đã review
- buộc mọi thay đổi lớn phải đi qua nhánh riêng
- áp validation gates trước commit / merge / tag / push
- giảm tối đa rủi ro phá repo root do merge sai hoặc push sai
- chuẩn hóa vai trò của AI trong các tác vụ Git

## 2. Các nguyên tắc nền tảng

- `main` là latest clean integrated state
- Version / phase lớn phải làm trên branch riêng
- Tag mới là nơi freeze version
- Không merge vào `main` nếu chưa qua gate
- AI không được tự ý thực hiện Git action nguy hiểm
- Branch nào cũng phải có ngữ cảnh rõ
- Remote phải phản ánh branch model local
- Không dùng thao tác Git “mù”

## 3. Approval model

### User approval bắt buộc cho:
- merge vào `main`
- tag version/release
- push `main`
- push tags release
- xóa branch release
- rebase / reset / history rewrite trên branch quan trọng

### AI có thể tự làm nếu đã được giao rõ:
- tạo branch mới
- commit trên branch làm việc
- chạy test/check
- tạo diff summary
- chuẩn bị merge summary
- push branch feature/release nếu user đã cho phép mức đó

## 4. Validation gates

### Pre-commit gate
```bash
git rev-parse --show-toplevel
git branch --show-current
git status
git diff --stat
git diff --cached --stat
python3 -m compileall cli core tests
make test
```

### Pre-merge-main gate
```bash
git status
git branch --show-current
git fetch origin
git log --oneline --decorate --graph --max-count=20
git diff --stat main...HEAD
```

### Pre-push-main gate
```bash
git status
git branch --show-current
git remote -v
git log --oneline --decorate -n 10
```

## 5. Quy tắc thao tác Git an toàn

- Luôn check branch trước khi làm gì lớn
- Luôn xem diff trước merge hoặc commit lớn
- Luôn dùng merge có chủ đích
- Không push mù
- Không sửa lịch sử nếu không thật sự cần

## 6. Mô hình assistant workspace

- Một branch quan trọng = một workspace/chat riêng
- Không trộn context cross-branch

## 7. Điều tuyệt đối phải tránh

- code trực tiếp trên `main` một thời gian dài
- merge khi chưa xem diff
- để AI merge/push `main` mà không có gate
- dùng cùng một AI context cho nhiều branch
- không tag mốc release quan trọng

## 8. Định nghĩa thành công

Git governance được coi là đang vận hành tốt khi:
- `main` luôn sạch và dễ tin cậy
- version/chặng được cô lập tốt
- merge/push hiếm khi gây bất ngờ
- AI làm được phần nặng nhưng không vượt quyền
- user chỉ phải approve ở điểm quan trọng
