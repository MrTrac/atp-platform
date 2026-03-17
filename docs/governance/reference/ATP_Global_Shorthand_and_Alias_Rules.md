# ATP Global Shorthand and Alias Rules

- **Mục đích:** Tài liệu authority chuẩn hóa shorthand / alias đang dùng trong ATP.
- **Phạm vi:** ATP chat/project work, docs workflow, git workflow, planning/execution shorthand, AI-assisted collaboration contexts.
- **Trạng thái:** Active.
- **Loại:** Reference.
- **Version:** v1.0
- **Date:** 2026-03-15

## Mục đích

Tài liệu này là reference authority của ATP cho việc diễn giải shorthand / alias / chat-operating agreements đang được dùng trong thực tế.

Mục tiêu của tài liệu:

- giữ cách hiểu shorthand nhất quán giữa user và AI assistants
- giảm drift giữa chat agreements và repository docs
- chuẩn hóa canonical form, accepted variants, và rule đi kèm
- làm rõ alias nào chỉ là shortcut ngắn và alias nào kéo theo workflow rule bắt buộc

## Phạm vi áp dụng

Tài liệu này áp dụng cho:

- ATP chat/project work
- docs workflow
- git workflow
- planning / execution shorthand
- validation / test shorthand
- export / output shorthand
- AI-assisted collaboration contexts nơi ATP governance có hiệu lực

## Quy tắc diễn giải chung

1. Alias luôn được diễn giải theo current context, trừ khi argument explicit thu hẹp scope.
2. Nếu alias có tham số, tham số đó được ưu tiên hơn default context.
3. Nếu nhiều practical variants cùng map tới một intent, tài liệu này xác định canonical form và accepted variants.
4. Accepted variants không tạo ra semantics mới, trừ khi tài liệu này nói rõ.
5. Shorthand không được override ATP governance rules, Git safety rules, documentation rules, hay approval boundaries.
6. Alias nào kích hoạt workflow mạnh hơn thì tự động inherit các rule phụ thuộc bắt buộc tương ứng.
7. Nếu current context không đủ để diễn giải an toàn, actor phải làm rõ context thay vì tự suy diễn vượt governance boundary.

## Bảng alias chuẩn hóa

### 1. Thao tác chung

| Alias / biến thể | Canonical form | Ý nghĩa | Phạm vi | Rule đi kèm / ghi chú |
|---|---|---|---|---|
| `go` | `go` | Tiếp tục bước hiện tại theo current context | continuation | Inherit current-context continuation semantics |
| `gh` | `go` | Biến thể conversational của lệnh tiếp tục | continuation | Accepted variant của `go`, không tạo semantics riêng |
| `next` | `go` | Đi tiếp theo current context | continuation | Accepted variant, ưu tiên khi user nói ngắn |
| `next <x>` | `go <x>` | Đi tiếp vào step / phase / milestone `<x>` | continuation | Tham số thu hẹp scope |
| `go-<step x>` | `go <x>` | Thực hiện bước `<x>` của project hiện tại | continuation | Canonical normalized meaning là `go <x>` |
| `ok` | `ok` | Xác nhận tiếp tục theo đề xuất gần nhất / current context | continuation | Không override approval-required actions |
| `ok <x>` | `ok <x>` | Xác nhận tiếp tục với option / bước `<x>` | continuation | Argument là authoritative narrowing |
| `no` | `no` | Từ chối hướng đang được đề xuất / current action | continuation | Không tự tạo workflow mới |
| `no <x>` | `no <x>` | Từ chối option / bước `<x>` | continuation | Argument thu hẹp object bị từ chối |

### 2. Kiểm tra / sửa / cập nhật

| Alias / biến thể | Canonical form | Ý nghĩa | Phạm vi | Rule đi kèm / ghi chú |
|---|---|---|---|---|
| `chkout`, `co` | `chkout` | Check output theo current context | review | Output có thể là screen hoặc logfile tùy context |
| `chkerr`, `ce` | `chkerr` | Kiểm tra lỗi hiện tại theo current context | review | Ưu tiên fault/error inspection |
| `chkcode`, `cc` | `chkcode` | Rà soát code / script / codebase hiện hành | code review | Không tự chuyển thành code rewrite nếu chưa được yêu cầu |
| `update`, `ud` | `update` | Update code / nội dung theo current context | edit | Inherit current task scope |
| `fix` | `fix` | Sửa lỗi hiện tại của script / module / project đang làm | edit | Ưu tiên bug fix hiện hành, không mở scope mới |

### 3. Version / plan / export

| Alias / biến thể | Canonical form | Ý nghĩa | Phạm vi | Rule đi kèm / ghi chú |
|---|---|---|---|---|
| `uv` | `uv` | Update version theo current context | versioning | Inherit version/header/changelog discipline khi relevant |
| `uv <version>` | `uv <version>` | Update version sang `<version>` | versioning | Version argument là authoritative |
| `make-plan` | `make-plan` | Lập plan chi tiết cho dự án / task hiện tại | planning | Ưu tiên current context, không tự mở scope mới |
| `plan <X>` | `plan <X>` | Lập plan chi tiết cho step / phase / milestone `<X>` | planning | `<X>` thu hẹp scope |
| `ex`, `export file` | `ex` | Xuất nội dung hiện tại ra file phù hợp | export | Format phụ thuộc context: docx/pdf/excel/html/markdown/zip bundle |

### 4. Output

| Alias / biến thể | Canonical form | Ý nghĩa | Phạm vi | Rule đi kèm / ghi chú |
|---|---|---|---|---|
| `o`, `out` | `o` | Nói về output hiện tại theo context | output | Có thể bao gồm screen hoặc logfile |
| `ocr`, `out-screen` | `ocr` | Nói về output trên screen / terminal | output | Focus vào screen output |
| `olf`, `out-logfile` | `olf` | Nói về output của logfile | output | Focus vào logfile output |

### 5. Test

| Alias / biến thể | Canonical form | Ý nghĩa | Phạm vi | Rule đi kèm / ghi chú |
|---|---|---|---|---|
| `test` | `test` | Chạy / rà test phù hợp cho current model/project | validation | Không claim pass nếu chưa chạy thật |
| `test-full` | `test-full` | Liệt kê và thực hiện toàn bộ test cho Mac và RHEL | validation | Scope rộng nhất trong nhóm test |
| `test-mac` | `test-mac` | Thực hiện bài test tiếp theo trên macOS | validation | Platform-scoped |
| `test-rhel` | `test-rhel` | Thực hiện bài test tiếp theo trên RHEL | validation | Platform-scoped |
| `test-mac-full` | `test-mac-full` | Thực hiện toàn bộ test trên macOS | validation | Platform full pass |
| `test-rhel-full` | `test-rhel-full` | Thực hiện toàn bộ test trên RHEL | validation | Platform full pass |

### 6. Git

| Alias / biến thể | Canonical form | Ý nghĩa | Phạm vi | Rule đi kèm / ghi chú |
|---|---|---|---|---|
| `git` | `git` | Xử lý Git theo current context | git workflow | Inherit Safe Git Branch Guard Rule |
| `gs` | `git` | Git shorthand ngắn theo current context | git workflow | Khi dùng như ATP shorthand thì inherit GSGR; actual shell install có thể collision-dependent |
| `gsg` | `git` | Git shorthand ngắn theo current context | git workflow | Inherit GSGR |
| `git-safe` | `git` | Git shorthand nhấn mạnh safety | git workflow | Inherit GSGR |
| `git-guard` | `git` | Git shorthand nhấn mạnh branch guard | git workflow | Inherit GSGR |
| `rpm` | `rpm` | Hướng dẫn cấu trúc và command build RPM cho current project trên RHEL | packaging | Bao gồm source transfer Mac -> RHEL nếu relevant |

Diễn giải thực dụng cho nhóm `git`:

- AI phải map shorthand này về action surface GSGR hiện hành, gồm: `status`, `fetch`, `diff`, `log`, `show`, `branch-info`, `switch`, `create-branch`, `start-slice`, `publish-branch`, `commit`, `push`, `pull`, `merge-main`, `tag`, `pick`, `delete-branch`, `prune`, `reset`, `restore`, `rebase-main`
- với slice mới, canonical flow ưu tiên là `gsgr start-slice <new-branch> <base-branch>`
- nếu không dùng `start-slice`, AI phải ưu tiên flow tối thiểu: `gsgr create-branch <new-branch> <base-branch>` -> `gsgr publish-branch <new-branch>` -> `gsgr status <new-branch>`
- `diff`, `log`, và `branch-info` là inspect-only; không được mutate branch / HEAD chỉ để inspect
- `delete-branch` hiện chỉ là local-only guarded delete, chưa phải remote delete

### 7. Docs

| Alias / biến thể | Canonical form | Ý nghĩa | Phạm vi | Rule đi kèm / ghi chú |
|---|---|---|---|---|
| `chk-docs`, `chkdocs`, `c-docs`, `cdocs` | `chk-docs` | Rà soát + refine + normalize toàn bộ `docs/` theo current context | docs | Inherit docs-folder review/refine/normalize rule |
| `chk-doc`, `chkdoc`, `c-doc`, `cdoc` | `chk-doc` | Rà soát + refine + normalize một tài liệu hoặc một bundle tài liệu | docs | Nếu không có argument, mặc định bám tài liệu gần nhất trong current context |

### 8. Prompt

| Alias / biến thể | Canonical form | Ý nghĩa | Phạm vi | Rule đi kèm / ghi chú |
|---|---|---|---|---|
| `pr` | `pr` | Viết một prompt thật chặt cho current task để user copy/paste cho AI khác | prompt delegation | Inherit AI_OS global `pr` rule + single-block handoff/verify-pass loop |
| `pr <name|description>` | `pr <name|description>` | Viết prompt chặt cho task được nêu để user copy/paste cho AI khác | prompt delegation | Argument là authoritative narrowing + inherit AI_OS global `pr` rule |

### 9. Title / chat

| Alias / biến thể | Canonical form | Ý nghĩa | Phạm vi | Rule đi kèm / ghi chú |
|---|---|---|---|---|
| `Title = <Tên new chat>` | `Title = <Tên new chat>` | Đặt / đổi tên thread theo tên explicit | chat/thread | Đây là canonical full form |
| `Title` | `Title = <Tên new chat>` | Dùng theo logic đổi tên thread khi context đã rõ | chat/thread | Thực tế thường đi kèm target title |
| `tit` | `Title = <Tên new chat>` | Accepted shorthand cho title rename | chat/thread | Không tạo semantics riêng |

### 10. Gợi ý / đề xuất

| Alias / biến thể | Canonical form | Ý nghĩa | Phạm vi | Rule đi kèm / ghi chú |
|---|---|---|---|---|
| `sh-me`, `sh me` | `sh-me` | Show me các đề xuất cho current project / task | suggestion | Hai form được coi là equivalent |

## Rule phụ thuộc bắt buộc

Các alias dưới đây không chỉ là shortcut; chúng tự động inherit rule mạnh hơn:

- `git`, `gs`, `gsg`, `git-safe`, `git-guard`
  - inherit [Global Safe Git Branch Guard Rule](../Global_Safe_Git_Branch_Guard_Rule.md)
  - mọi diễn giải phải bám pattern `Check -> Switch -> Re-check -> Execute`
  - khi mở slice mới, phải ưu tiên `start-slice` hoặc flow `create-branch -> publish-branch -> status`
- `chk-docs`, `chkdocs`, `c-docs`, `cdocs`
  - inherit docs folder review / refine / normalize rule từ governance documentation discipline
  - nếu đã thấy nội dung thì phải ưu tiên xử lý trực tiếp trong scope cho phép
- `chk-doc`, `chkdoc`, `c-doc`, `cdoc`
  - inherit single-document / bundle review / refine / normalize rule
  - nếu không có đủ nội dung thì phải nói rõ limitation hoặc viết prompt delegation chặt
- `uv`
  - inherit script header / version / changelog discipline khi relevant
  - không được đổi version tùy tiện ngoài current scope
- `go`, `gh`, `next`
  - inherit current-context continuation semantics
  - không tự override approval-sensitive boundary hoặc change scope
- `pr`
  - inherit semantics “write a tight prompt for the named/current task” từ AI_OS global shorthand authority
  - prompt phải bám current governance context, không viết chung chung
  - prompt phải được viết ở một chỗ duy nhất để user copy/paste dễ dàng; không phân mảnh thành nhiều block nếu không thật sự cần
  - trong prompt hoặc hướng dẫn đi kèm phải nói rõ: sau khi AI mục tiêu thực hiện xong, user sẽ dán kết quả lại đây
  - bước tiếp theo bắt buộc là `verify`
  - `verify` phải PASS
  - chỉ sau khi `verify` PASS thì mới review sâu hơn hoặc viết tiếp một prompt review / follow-up lần nữa nếu cần

## Ghi chú về canonical form và accepted variants

Quy tắc chuẩn hóa:

- Mỗi intent có một canonical form để dùng trong docs authority.
- Accepted variants chỉ là practical spelling variants đã tồn tại trong thực tế làm việc.
- Accepted variants không tạo semantics mới, trừ khi có ghi chú explicit.

Các normalization bắt buộc:

- `sh-me` là canonical form; `sh me` là accepted variant.
- `chk-docs` là canonical form; `chkdocs`, `c-docs`, `cdocs` là accepted variants.
- `chk-doc` là canonical form; `chkdoc`, `c-doc`, `cdoc` là accepted variants.
- `Title = <Tên new chat>` là canonical full form; `Title` và `tit` là accepted shorthand forms.
- `go` là canonical continuation form; `gh` và `next` là accepted variants cùng intent.
- `go <x>` là canonical normalized meaning cho cả `next <x>` và `go-<step x>`.
- `ex` là canonical short form; `export file` là accepted descriptive variant.
- `o`, `ocr`, `olf` là canonical short forms; `out`, `out-screen`, `out-logfile` là accepted descriptive variants.

Diễn giải quan trọng:

- `ok` / `ok <x>` là acceptance/continue shorthand theo current proposal hoặc current option; không tự động coi là approval cho high-risk Git/release actions.
- `no` / `no <x>` là rejection shorthand theo current proposal hoặc current option; không tự tạo task mới nếu user chưa nêu.
- `git` group aliases có thể có khác biệt về shell install thực tế ngoài ATP, nhưng ở mức ATP shorthand semantics chúng cùng map về intent Git workflow và cùng inherit GSGR.

## Tài liệu liên quan / nguồn chuẩn liên quan

- [docs/governance/README.md](../README.md)
- [docs/governance/ATP_Development_Ruleset.md](../ATP_Development_Ruleset.md)
- [docs/governance/Global_Safe_Git_Branch_Guard_Rule.md](../Global_Safe_Git_Branch_Guard_Rule.md)
- [docs/governance/documentation/Documentation_Governance_Bundle.md](../documentation/Documentation_Governance_Bundle.md)
- [docs/governance/reference/Global_Shorthand_Agreements.md](./Global_Shorthand_Agreements.md)
- [docs/governance/reference/AI_Session_Bootstrap_Template.md](./AI_Session_Bootstrap_Template.md)

Tài liệu này thay vai trò authority reference cho việc diễn giải shorthand / alias trong ATP. Các tài liệu shorthand cũ, nếu còn tồn tại, được hiểu là predecessor/reference context trừ khi đã được revise để trỏ về tài liệu này.
