# Global Safe Git Rule (GSGR)

## 1. Mục đích

`Global Safe Git Rule` là rule Git an toàn toàn cục, áp dụng để ngăn các lỗi phổ biến như:

- commit nhầm branch
- push nhầm branch
- merge sai ngữ cảnh
- tag sai điểm
- cherry-pick nhầm nơi
- reset nhầm branch
- đưa nhầm file ngoài scope vào commit
- làm bẩn `main`
- tạo lệch giữa branch dev và branch release

Rule này được áp dụng như một chuẩn thao tác bắt buộc cho mọi hoạt động Git quan trọng.

---

## 2. Phạm vi áp dụng

Rule này áp dụng cho:

- ATP
- toàn bộ các dự án khác
- mọi combo lệnh Git quan trọng chạy trên terminal Mac:
  - `Terminal.app`
  - `iTerm2`
  - terminal tương đương
- mọi AI
- mọi người tham gia thao tác Git
- mọi tình huống có liên quan đến quản lý Git an toàn

---

## 3. Nguyên tắc lõi

## **GSGR = Check → Switch → Re-check → Execute**

Trước mọi combo lệnh Git quan trọng, bắt buộc thực hiện đúng chuỗi sau:

### 3.1. Check
Kiểm tra trạng thái hiện tại:

- working tree
- branch hiện tại
- commit gần nhất

### 3.2. Switch
Chuyển về đúng branch theo ngữ cảnh hiện tại.

Không được giả định terminal đang đứng đúng branch.

### 3.3. Re-check
Kiểm tra lại sau khi switch:

- đã ở đúng branch chưa
- working tree có đúng kỳ vọng không
- commit head có đúng ngữ cảnh không

### 3.4. Execute
Chỉ sau đó mới được chạy combo Git chính.

---

## 4. Nhóm thao tác bắt buộc áp dụng rule

Rule này bắt buộc áp dụng cho các thao tác:

- `git add`
- `git commit`
- `git push`
- `git pull`
- `git merge`
- `git tag`
- `git cherry-pick`
- `git reset`
- `git rebase`
- `git restore`
- mọi block lệnh Git có khả năng thay đổi lịch sử, branch, hoặc remote state

---

## 5. Template chuẩn toàn cục

### 5.1. Guard tối thiểu

```bash
git status
git branch --show-current
```

### 5.2. Guard chuẩn bắt buộc nên dùng

```bash
git status
git branch --show-current
git log --oneline --decorate -n 3
```

### 5.3. Template đầy đủ trước mọi combo Git quan trọng

```bash
git status
git branch --show-current
git log --oneline --decorate -n 3

git switch <TARGET_BRANCH>

git status
git branch --show-current
git log --oneline --decorate -n 3

# rồi mới chạy combo git chính
```

---

## 6. Template thao tác chuẩn theo ngữ cảnh

### 6.1. Commit / push trên branch phát triển

```bash
git status
git branch --show-current
git log --oneline --decorate -n 3

git switch <DEV_BRANCH>

git status
git branch --show-current
git log --oneline --decorate -n 3

git add <đúng file theo scope>
git commit -m "..."
git push origin <DEV_BRANCH>
```

### 6.2. Merge vào `main`

```bash
git status
git branch --show-current
git log --oneline --decorate -n 3

git switch main

git status
git branch --show-current
git log --oneline --decorate -n 3

git pull origin main
git merge --no-ff <SOURCE_BRANCH> -m "merge: ..."
git push origin main
```

### 6.3. Tag release

```bash
git status
git branch --show-current
git log --oneline --decorate -n 3

git switch main

git status
git branch --show-current
git log --oneline --decorate -n 3

git tag -a <TAG> -m "..."
git push origin <TAG>
```

### 6.4. Cherry-pick cứu commit nhầm branch

```bash
git status
git branch --show-current
git log --oneline --decorate -n 5

git switch <CORRECT_BRANCH>

git status
git branch --show-current
git log --oneline --decorate -n 3

git cherry-pick <COMMIT_ID>
git push origin <CORRECT_BRANCH>
```

### 6.5. Reset an toàn

```bash
git status
git branch --show-current
git log --oneline --decorate -n 5

git switch <TARGET_BRANCH>

git status
git branch --show-current
git log --oneline --decorate -n 5

git reset --hard <SAFE_COMMIT>
git status
```

---

## 7. Quy tắc bổ sung bắt buộc

### 7.1. Không giả định branch
Dù trước đó terminal đang ở branch nào, vẫn phải check lại.

### 7.2. Không dùng `git add .` trong pass nhạy cảm
Chỉ add đúng file theo scope hiện tại.

### 7.3. `main` chỉ dùng cho:
- merge
- release tag
- kiểm tra baseline integrated

Không dùng `main` để commit work đang phát triển.

### 7.4. Branch dev chỉ dùng cho work đúng ngữ cảnh
Ví dụ:

- `v1.0-planning`
- `v1.1-planning`
- `feature/...`
- `hotfix/...`

### 7.5. Trước mọi merge/tag
Bắt buộc check lại:

- branch hiện tại
- clean working tree
- commit head gần nhất

---

## 8. Quy tắc áp dụng cho AI

Từ nay về sau, trong mọi hỗ trợ của AI liên quan đến Git:

- AI phải luôn prepend branch guard
- AI không được giả định branch hiện tại là đúng
- AI phải chỉ rõ target branch theo ngữ cảnh
- AI phải ưu tiên block lệnh an toàn
- AI phải tránh viết block Git có rủi ro commit nhầm branch

Nói cách khác:

## **mọi AI cũng phải tuân thủ Global Safe Git Rule**

---

## 9. Chuẩn ngắn gọn để ghi nhớ

## **GSGR = Check → Switch → Re-check → Execute**

---

## 10. Kết luận

`Global Safe Git Rule` là rule Git an toàn toàn cục, được áp dụng bắt buộc cho:

- ATP
- mọi dự án khác
- mọi AI
- mọi actor có liên quan đến quản lý Git an toàn
- mọi thao tác Git quan trọng trên terminal Mac

Từ thời điểm này, mọi combo Git quan trọng phải được xây theo đúng guard pattern của GSGR.
