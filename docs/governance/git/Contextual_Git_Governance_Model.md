# Contextual Git Governance Model
## Tài liệu tham chiếu Git an toàn, tối ưu và theo ngữ cảnh cho ATP và các dự án khác

- **Version:** v1.0
- **Status:** Final-Reviewed
- **Date:** 2026-03-14
- **Audience:** User + AI coding assistants
- **Purpose:** Chuẩn hóa cách commit / tag / merge / push / quản lý branch một cách an toàn, tối ưu, theo ngữ cảnh dự án

## 1. Mục tiêu

Mục tiêu không phải chỉ là “dùng Git đúng lệnh”, mà là:

- luôn giữ `main` là nhánh sạch, ổn định, mới nhất, đã tích hợp
- cô lập thay đổi theo từng version / phase / context
- giảm tối đa nguy cơ merge sai làm hỏng repo root
- tạo ra quy trình mà cả user và AI assistants đều có thể tuân theo nhất quán
- tăng mức auto-check trước các thao tác nguy hiểm
- giảm chi phí sửa sai, giảm token/usage lãng phí, giảm thao tác thủ công

## 2. Giải thích nền tảng Git thật dễ hiểu

Git cho phép:
- lưu từng mốc thay đổi bằng commit
- phát triển song song bằng branch
- đóng băng mốc phát hành bằng tag
- đồng bộ lên GitHub bằng push
- tích hợp nhánh này vào nhánh khác bằng merge

### 5 khái niệm cốt lõi
- **Commit** = mốc lưu trạng thái code
- **Branch** = đường phát triển riêng để cô lập thay đổi
- **Main** = trạng thái sạch, mới nhất, đã tích hợp
- **Tag** = nhãn freeze version trên một commit
- **Remote** = repo trên GitHub hoặc máy chủ khác

## 3. Mô hình Git tối ưu nhất nói chung

Mô hình tối ưu cho đa số dự án vừa và lớn là:

- `main` = latest clean integrated state
- mỗi version / release / phase lớn làm trên branch riêng
- hoàn tất xong thì merge vào `main`
- freeze bằng tag
- version kế tiếp bắt đầu trên branch mới

## 4. Mô hình Git tối ưu nhất cho ATP

### Vai trò của `main`
`main` trong ATP là:
- nhánh chuẩn của repo
- sạch nhất
- mới nhất
- đã tích hợp xong
- đã pass check/test cần thiết
- là nhánh push remote chính

### Vai trò của các nhánh version
Ví dụ:
- `release/v0.1-hardening`
- `release/v0.2-workspace-baseline`
- `release/v1.0-core-platform`

### Vai trò của tag
Ví dụ:
- `atp-mvp-v0`
- `v0.1.0-mvp`
- `v0.1.1-hardening`
- `v0.2.0-workspace`
- `v1.0.0`

## 5. Branching strategy chuẩn đề xuất

### Branch chuẩn
- `main`
- `release/<version-context>`
- `feature/<scope>`
- `hotfix/<issue>`

### Quy tắc dùng
- `release/...` cho version hoặc phase lớn
- `feature/...` cho phần việc con
- `hotfix/...` cho fix nhanh có kiểm soát

## 6. Rule nền tảng bắt buộc cho user và AI

- Không code trực tiếp trên `main` trừ trường hợp rất nhỏ và rõ chủ đích
- Mỗi version / phase lớn có branch riêng
- Tag mới là nơi freeze version
- Chỉ merge vào `main` khi branch đã sạch
- Mỗi branch quan trọng có workspace/chat riêng với AI
- Remote phải đồng bộ branch model với local
- Trước mọi thao tác Git nguy hiểm phải qua gate check
- AI không được tự ý merge/push nếu chưa qua gate check

## 7. Định nghĩa Git governance theo ngữ cảnh

**Contextual Git Governance** là bộ quy tắc Git thay đổi theo:
- loại dự án
- giai đoạn dự án
- mức độ rủi ro
- vai trò của branch hiện tại
- loại thao tác Git đang định thực hiện

## 8. Git validation gates

### Gate trước commit
```bash
git status
git branch --show-current
git diff --stat
git diff --cached --stat
python3 -m compileall cli core tests
make test
```

### Gate trước merge vào `main`
```bash
git status
git branch --show-current
git fetch origin
git log --oneline --decorate --graph --max-count=20
git diff --stat main...HEAD
```

### Gate trước push `main`
```bash
git status
git branch --show-current
git remote -v
git log --oneline --decorate -n 10
```

## 9. Mô hình tối ưu nhất chốt cho ATP

- `main` = latest clean integrated state
- `release/<version-context>` = dev theo version/chặng
- tag = freeze mốc
- merge vào `main` chỉ sau gate check + approval
- một branch quan trọng = một workspace/chat riêng
- GitHub đồng bộ với local

## 10. Kết luận

Phương án chốt là:

**Contextual Git Governance + release-branch workflow**

Đây là mô hình vừa an toàn, vừa thực dụng, vừa đủ mạnh để dùng lâu dài cho ATP và các dự án khác.
