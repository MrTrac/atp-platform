# Safe Git Workflow Templates
## Bộ template thao tác Git an toàn cho ATP và các dự án khác

- **Version:** v1.0
- **Status:** Final-Reviewed
- **Date:** 2026-03-14

## 1. Mục tiêu

Bộ template này dùng để:
- giảm thao tác Git thủ công không cần thiết
- chuẩn hóa các bước trước commit / merge / tag / push
- buộc AI và user đi qua safety gates
- tăng khả năng automation có kiểm soát

## 2. Safe Commit Template

### Pre-checks
```bash
git rev-parse --show-toplevel
git branch --show-current
git status
git diff --stat
git diff --cached --stat
python3 -m compileall cli core tests
make test
```

### Command flow
```bash
git add -A
git commit -m "<purposeful-message>"
```

### Post-checks
```bash
git status
git log --oneline --decorate -n 5
```

## 3. Safe Merge-to-Main Template

### Pre-checks
```bash
git rev-parse --show-toplevel
git branch --show-current
git status
git fetch origin
git log --oneline --decorate --graph --max-count=20
git diff --stat main...HEAD
python3 -m compileall cli core tests
make test
```

### Approval
Merge vào `main` luôn cần user approve.

### Command flow
```bash
git checkout main
git pull
git merge --no-ff <source-branch>
```

### Post-checks
```bash
git status
git log --oneline --decorate -n 10
python3 -m compileall cli core tests
make test
```

## 4. Safe Tag Template

### Pre-checks
```bash
git status
git branch --show-current
git log --oneline --decorate -n 10
git tag
```

### Approval
Tag release/version luôn cần user approve.

### Command flow
```bash
git tag <tag-name>
git show <tag-name> --stat
```

## 5. Safe Push Template

### Safe Push Branch
```bash
git status
git branch --show-current
git remote -v
git log --oneline --decorate -n 10
git push -u origin <branch-name>
```

### Safe Push Main
```bash
git status
git branch --show-current
git remote -v
git log --oneline --decorate -n 10
git push origin main
```

### Safe Push Tags
```bash
git tag
git show <tag-name> --stat
git remote -v
git push origin <tag-name>
```

## 6. Stop conditions

Phải dừng ngay nếu:
- không chắc branch hiện tại là branch đúng
- working tree bẩn ngoài dự kiến
- diff vượt scope
- compile/test fail
- remote lạ / sai
- user chưa approve nhưng action đang thuộc nhóm high-risk

## 7. ATP-specific standard flow

### Bắt đầu phase mới
```bash
git checkout main
git pull
git checkout -b release/v0.1-hardening
```

### Commit an toàn
```bash
git status
python3 -m compileall cli core tests
make test
git add -A
git commit -m "docs(atp): refine v0.1 hardening phase A consistency rules"
```

### Merge phase hoàn tất vào main
```bash
git checkout main
git pull
git merge --no-ff release/v0.1-hardening
python3 -m compileall cli core tests
make test
```

### Tag và push
```bash
git tag v0.1.1-hardening
git push origin main
git push origin v0.1.1-hardening
```
