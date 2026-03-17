# Global Safe Git Branch Guard Rule (GSGR)

- **Mục đích:** Thiết lập global Git safety framework dùng lâu dài cho ATP, các dự án khác, và mọi AI-assisted Git workflow trên macOS.
- **Phạm vi:** Tất cả Git action quan trọng, mọi actor, mọi repo, Terminal.app, iTerm2, terminal tương đương.
- **Trạng thái:** Active.
- **Loại:** Mandatory.
- **Version:** v1.0
- **Date:** 2026-03-15

## 1. Kết luận điều hành

`Global Safe Git Branch Guard Rule` là rule Git an toàn toàn cục của ATP.

Rule này chốt một mô hình vận hành thống nhất gồm hai lớp:

1. **Execution layer**: command thật `gsgr`
2. **Interaction layer**: alias và AI shorthand để user không phải tự dựng low-level Git command

Mnemonic chính thức:

**GSGR = Check -> Switch -> Re-check -> Execute**

Từ thời điểm này, mọi Git combo quan trọng phải được điều phối theo guard pattern này, thay vì viết lệnh Git rời rạc rồi tự giả định branch/context là đúng.

Đối với slice execution, guard pattern này đồng thời là branch-lineage gate toàn cục trước mọi first pass của slice mới.

## 2. Scope áp dụng

Rule này áp dụng cho:

- ATP
- toàn bộ các dự án khác
- mọi AI
- mọi actor có thao tác Git
- mọi workflow Git có rủi ro branch/history/remote
- Terminal.app
- iTerm2
- terminal tương đương trên macOS

Rule này đặc biệt nhằm giảm các lỗi:

- commit nhầm branch
- push nhầm branch
- merge sai ngữ cảnh
- tag sai điểm
- cherry-pick nhầm nơi
- reset nhầm branch
- rebase sai branch
- add nhầm file ngoài scope
- làm bẩn `main`

## 3. Core doctrine

### 3.1 Check

Luôn kiểm tra:

- đang ở trong Git repo hay không
- working tree hiện tại
- current branch
- commit head gần nhất

### 3.2 Switch

Nếu action có target branch, phải switch về đúng branch theo ngữ cảnh.

Không được giả định terminal đang đứng sẵn ở branch đúng.

### 3.3 Re-check

Sau khi switch, phải kiểm tra lại:

- current branch
- working tree
- recent commits

### 3.4 Execute

Chỉ sau khi guard pass mới được chạy Git action chính.

### 3.5 Slice pre-implementation branch gate

Đối với mọi slice mới, `GSGR` áp như một pre-implementation gate bắt buộc.

Trước khi bắt đầu docs baseline, implementation, hoặc bounded execution pass đầu tiên của slice mới, bắt buộc phải đi qua đúng chuỗi:

`Check -> Switch -> Re-check -> Execute`

Diễn giải bắt buộc:

- `Check`: xác nhận đang ở đúng repo, biết current branch hiện tại, và biết worktree state hiện tại
- `Switch`: tạo branch của slice mới nếu chưa có và switch vào đúng branch đó
- `Re-check`: verify lại current repo, current branch, và worktree sau khi switch
- `Execute`: chỉ sau đó mới được bắt đầu work của slice mới

Không được bắt đầu slice mới khi vẫn đang đứng ở branch của slice cũ hoặc branch lineage khác.

Nếu phát hiện slice work đã bắt đầu trên sai branch thì phải:

- dừng ngay pass hiện tại
- sửa lineage / branch context trước
- re-check lại repo / branch / worktree
- chỉ tiếp tục sau khi branch gate pass

## 4. Runtime model chính thức

Runtime command chính thức là:

```bash
gsgr
```

Install path chính thức:

```bash
~/.config/shell/functions/git_safe.sh
```

`~/.zshrc` phải source file này bằng đúng dòng:

```bash
[ -f ~/.config/shell/functions/git_safe.sh ] && source ~/.config/shell/functions/git_safe.sh
```

Không duplicate source line này.

## 5. Alias layer và AI interaction model

`gsgr` là command thực thi thật.

Các tên ngắn sau là **user-facing shorthand entrypoints** nếu không bị collision:

- `gs`
- `gsg`
- `git-safe`
- `git-guard`

Mục tiêu của alias layer là:

- giảm cognitive load
- tăng tốc giao tiếp giữa user và AI
- để user chỉ cần nói intent ngắn
- để AI chịu trách nhiệm dựng lệnh `gsgr ...` đầy đủ và an toàn

### 5.1 Nguyên tắc giao tiếp với AI

User có thể nói ngắn với AI bằng các cụm như:

- `git`
- `gs`
- `gsg`
- `git-safe`
- `git-guard`

và mô tả intent ngắn gọn, ví dụ:

- `gs commit docs governance`
- `gsg merge slice-c into main`
- `git-safe tag v1.0.2`
- `git-guard pick f44acc0 to v1.0-planning`

AI **không** được yêu cầu user tự xác định low-level Git arguments thủ công khi việc đó có thể suy ra an toàn từ context.

AI phải:

- hiểu intent
- xác định target branch/action phù hợp
- output câu lệnh `gsgr ...` cuối cùng
- giữ guard pattern an toàn

Rule này **không** yêu cầu xây natural-language parser trong shell.

## 6. Mandatory pre-install alias collision policy

Trước khi cài bất kỳ alias hoặc function name nào, phải check collision qua:

- alias hiện có
- shell function hiện có
- command trong `PATH`
- shell config files liên quan, nếu phát hiện được

Candidate names:

- `gsgr`
- `gs`
- `gsg`
- `git-safe`
- `git-guard`

### 6.1 Cách phân loại collision

Mỗi tên phải được phân loại thành một trong ba trạng thái:

- `free`
- `already used by the same intended Git safety layer`
- `already used by something unrelated`

### 6.2 Chính sách cài đặt

Ưu tiên bắt buộc:

1. giữ `gsgr`
2. cài tất cả alias collision-free trong nhóm:
   - `gs`
   - `gsg`
   - `git-safe`
   - `git-guard`
3. nếu alias đang bị dùng bởi behavior không liên quan, phải skip alias đó
4. không force-overwrite alias/function/command không liên quan

Kết quả cài đặt phải báo rõ:

- tên nào đã được check
- tên nào free
- tên nào occupied
- tên nào được install
- tên nào bị skip
- vì sao

## 7. Command interface chính thức

Command interface chuẩn:

```bash
gsgr <action> [args...]
```

Global options được hỗ trợ:

- `--dry-run`
- `--verbose`
- `--yes`

Supported actions:

1. `help`
2. `status`
3. `fetch`
4. `diff`
5. `log`
6. `show`
7. `branch-info`
8. `switch`
9. `create-branch`
10. `start-slice`
11. `publish-branch`
12. `commit`
13. `push`
14. `pull`
15. `merge-main`
16. `tag`
17. `pick`
18. `delete-branch`
19. `prune`
20. `reset`
21. `restore`
22. `rebase-main`

## 8. Action semantics

### 8.1 `gsgr help`

In usage, examples, alias guidance, installed alias layer, skipped aliases.

### 8.2 `gsgr status [target-branch]`

Guard only, không có state-changing Git action.

### 8.3 `gsgr fetch [target-branch]`

Inspect/sync-only action:

- fetch remote state cần thiết
- không mutate working tree
- không đổi HEAD chỉ để inspect

### 8.4 `gsgr diff [target-branch] [diff-args...]`

Inspect-only action:

- dùng để xem diff theo current context hoặc target branch hợp lệ
- không được switch branch thật chỉ để đọc diff
- không mutate working tree hoặc HEAD chỉ để inspect

### 8.5 `gsgr log [target-branch] [log-args...]`

Inspect-only action:

- dùng để xem history phù hợp với current context
- không được switch branch thật chỉ để inspect
- không mutate branch / HEAD chỉ để xem log

### 8.6 `gsgr show <object>`

Inspect-only action:

- dùng để xem commit, tag, hoặc object Git cụ thể
- không mutate repo state

### 8.7 `gsgr branch-info [target-branch]`

Inspect-only action:

- hiển thị branch context, remote linkage, và state summary cần thiết
- không được switch branch thật chỉ để đọc thông tin
- không mutate branch / HEAD chỉ để inspect

### 8.8 `gsgr switch <target-branch>`

- guard target branch
- switch vào đúng branch được chỉ định
- re-check branch/worktree sau switch

### 8.9 `gsgr create-branch <new-branch> <base-branch>`

- verify repo / branch / worktree theo guard pattern
- tạo branch mới từ đúng `base-branch`
- switch vào branch mới
- re-check branch/worktree sau khi tạo

### 8.10 `gsgr start-slice <new-branch> <base-branch>`

Đây là canonical slice-start flow.

- tạo branch slice mới từ đúng `base-branch`
- switch vào branch mới
- verify lại repo / branch / worktree
- chốt pre-implementation gate trước khi bắt đầu slice work

Khi bắt đầu slice mới, đây là flow ưu tiên dùng để hiện thực hóa global slice branch gate.

### 8.11 `gsgr publish-branch <target-branch>`

- guard đúng branch local
- publish branch mới lên `origin`
- thiết lập remote tracking khi cần
- đặc biệt hữu ích ngay sau `create-branch` hoặc `start-slice`

### 8.12 `gsgr commit <target-branch> "<commit-message>" <file1> [file2 ...]`

- guard branch
- chỉ add các file được chỉ định
- không dùng `git add .`
- commit
- push đúng target branch

### 8.13 `gsgr push <target-branch>`

- guard branch
- push đúng branch đó

### 8.14 `gsgr pull <target-branch>`

- guard branch
- working tree phải sạch
- pull `origin <target-branch>`

### 8.15 `gsgr merge-main <source-branch> "<merge-message>"`

- guard về `main`
- working tree phải sạch
- pull `origin main`
- merge `--no-ff`
- push `origin main`
- là dangerous action, cần `--yes`

### 8.16 `gsgr tag <tag-name> "<tag-message>"`

- guard về `main`
- working tree phải sạch
- fail nếu tag đã tồn tại
- tạo annotated tag
- push tag
- là dangerous action, cần `--yes`

### 8.17 `gsgr pick <target-branch> <commit-id>`

- validate commit tồn tại
- guard target branch
- cherry-pick
- push đúng branch

### 8.18 `gsgr delete-branch <target-branch>`

- local-only guarded delete
- không phải remote delete
- chỉ xóa local branch khi guard pass
- là destructive action, cần `--yes`

### 8.19 `gsgr prune`

- dọn branch/reference state cũ theo guard có kiểm soát
- destructive hoặc semi-destructive cleanup phải được guarded
- action này không được dùng như remote-delete wrapper mù quáng

### 8.20 `gsgr reset <target-branch> <safe-commit>`

- validate commit tồn tại
- guard target branch
- dangerous action
- reset `--hard`
- show status sau đó
- cần `--yes`

### 8.21 `gsgr restore <target-branch> <file1> [file2 ...]`

- guard target branch
- restore đúng các file được chỉ định
- show status sau đó

### 8.22 `gsgr rebase-main <target-branch>`

- target branch không được là `main`
- guard target branch
- working tree phải sạch
- fetch `origin`
- rebase onto `origin/main`
- push `--force-with-lease`
- là dangerous action, cần `--yes`

## 8A. Canonical slice-start flow

Khi mở một slice mới, flow canonical bây giờ là:

```bash
gsgr start-slice <new-branch> <base-branch>
```

Nếu không dùng `start-slice`, flow tối thiểu phải là:

```bash
gsgr create-branch <new-branch> <base-branch>
gsgr publish-branch <new-branch>
gsgr status <new-branch>
```

Flow này là cách hiện thực hóa trực tiếp:

- global slice branch gate
- pre-implementation gate cho mọi slice mới
- doctrine `Check -> Switch -> Re-check -> Execute`

## 9. Safety validations bắt buộc

System phải fail rõ ràng khi:

- không ở trong Git repo
- thiếu hoặc sai arguments
- branch target không tồn tại ở local hoặc origin
- action nguy hiểm chạy khi chưa có `--yes`
- merge/tag/pull/rebase/reset chạy khi working tree bẩn
- `commit` không có file list
- commit hoặc safe commit không tồn tại
- tag đã tồn tại
- `delete-branch` được yêu cầu như remote delete
- inspect-only action đang cố mutate repo state chỉ để inspect

System không được silently continue qua unsafe states.

## 10. UX requirements chính thức

Runtime output phải giữ:

- stage headers rõ: `CHECK / SWITCH / RE-CHECK / EXECUTE`
- error messages dễ hiểu
- return codes ổn định
- help text ngắn, dùng được ngay

Khuyến nghị mạnh:

- ANSI colors
- `--dry-run`
- `--verbose`
- `--yes`

## 11. Logging model

Logging phải nhẹ, user-global, và nằm ngoài project repos.

Location chuẩn:

```bash
~/.local/state/gsgr/gsgr.log
```

Minimum fields:

- timestamp
- action
- repo path
- current branch
- target branch
- success / failure

Không overengineer logging thành workflow engine.

## 12. Quy tắc cho `main`

`main` chỉ là branch tích hợp/baseline:

- merge
- tag/release
- kiểm tra integrated baseline

Không dùng `main` cho dev work thường ngày.

## 13. Ví dụ vận hành chuẩn

### 13.1 Commit an toàn trên branch dev

```bash
gsgr commit v1.0-planning "docs: integrate GSGR" docs/governance/README.md docs/README.md
```

### 13.2 Push branch

```bash
gsgr push v1.0-planning
```

### 13.2a Start slice an toàn

```bash
gsgr start-slice v1.0-slice-e v1.0-planning
```

### 13.2b Start slice bằng flow tách rời

```bash
gsgr create-branch v1.0-slice-e v1.0-planning
gsgr publish-branch v1.0-slice-e
gsgr status v1.0-slice-e
```

### 13.3 Merge vào `main`

```bash
gsgr --yes merge-main v1.0-planning "merge: v1.0 planning into main"
```

### 13.4 Tag release

```bash
gsgr --yes tag v1.0.2 "release: v1.0.2"
```

### 13.5 Cherry-pick an toàn

```bash
gsgr pick v1.0-planning f44acc0
```

### 13.6 Reset có kiểm soát

```bash
gsgr --yes reset v1.0-planning abc1234
```

### 13.7 Rebase lên `origin/main`

```bash
gsgr --yes rebase-main v1.0-planning
```

## 14. Vai trò trong ATP governance

Trong ATP, rule này là:

- global safe Git governance rule
- authority doc cho branch guard pattern
- companion doc cho Git governance bundle hiện có
- nền bắt buộc để AI-assisted Git workflow không commit/push/merge/tag sai ngữ cảnh

Rule này **không** thay thế:

- `docs/governance/ATP_Development_Ruleset.md`
- `docs/governance/git/Contextual_Git_Governance_Model.md`
- `docs/governance/git/AI_Branch_Operation_Rules.md`

Nó bổ sung một execution-ready guard discipline dùng chung cho tất cả các tài liệu đó.

## 15. Kết luận

`Global Safe Git Branch Guard Rule` là permanent global Git safety framework của ATP và các workflow liên quan.

Từ nay:

- `gsgr` là command runtime chính thức
- alias layer là lớp tương tác ngắn gọn nếu không collision
- user có thể nói intent ngắn với AI
- AI phải xuất ra lệnh `gsgr ...` cuối cùng và an toàn
- mọi Git combo quan trọng phải đi qua:

**Check -> Switch -> Re-check -> Execute**
