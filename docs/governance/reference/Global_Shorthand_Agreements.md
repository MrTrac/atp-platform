# Global Shorthand Agreements
## Bộ thỏa thuận gõ tắt toàn cục cho các dự án và ngữ cảnh làm việc với AI

- **Version:** v1.0
- **Status:** Final-Reviewed
- **Date:** 2026-03-14
- **Scope:** Global shorthand rules
- **Audience:** User + AI assistants

---

# 1. Mục đích

Tài liệu này chuẩn hóa toàn bộ các alias / shorthand / thỏa thuận gõ tắt đã chốt, để:

- giảm thao tác lặp lại
- giảm phải giải thích lại ngữ cảnh
- giúp AI hiểu đúng yêu cầu ngay khi nhận alias
- giữ cách làm việc nhất quán giữa các dự án

---

# 2. Nhóm điều hướng / tiếp tục công việc

## `gh`
**Cú pháp:**
```text
gh
```

**Nghĩa:**
- go ahead
- tiếp tục công việc đang làm theo ngữ cảnh hiện tại

---

## `go`
**Cú pháp:**
```text
go
```

**Nghĩa:**
- go-on
- hãy tiếp tục / đi tiếp trong step đang làm / làm tiếp / tiếp tục theo ngữ cảnh hiện tại

---

## `go-<step x>`
**Cú pháp:**
```text
go-<step x>
```

**Ví dụ:**
```text
go-step-3
go-M4
```

**Nghĩa:**
- thực hiện bước `<step x>` của dự án hiện tại

---

# 3. Nhóm lập kế hoạch

## `make-plan`
**Cú pháp:**
```text
make-plan
```

**Nghĩa:**
- lập plan chi tiết cho dự án hiện tại

---

## `plan <X>`
**Cú pháp:**
```text
plan <X>
```

**Ví dụ:**
```text
plan M4
plan step 2
```

**Nghĩa:**
- lập plan chi tiết cho step / phase / milestone `<X>`

---

# 4. Nhóm kiểm tra output / lỗi / code

## `chkout` | `co`
**Cú pháp:**
```text
chkout
co
```

**Nghĩa:**
- check output
- kiểm tra output theo ngữ cảnh hiện tại

---

## `chkerr` | `ce`
**Cú pháp:**
```text
chkerr
ce
```

**Nghĩa:**
- check lỗi
- rà lỗi hiện tại theo ngữ cảnh

---

## `chkcode` | `cc`
**Cú pháp:**
```text
chkcode
cc
```

**Nghĩa:**
- check / rà soát code của script / codebase hiện hành đang gắn với ngữ cảnh làm việc

---

## `update` | `ud`
**Cú pháp:**
```text
update
ud
```

**Nghĩa:**
- update code của script / codebase hiện hành theo ngữ cảnh

---

## `fix`
**Cú pháp:**
```text
fix
```

**Nghĩa:**
- fix lỗi hiện tại của script / module / dự án đang làm

---

# 5. Nhóm version / git / release

## `uv`
**Cú pháp:**
```text
uv
uv <version>
```

**Ví dụ:**
```text
uv
uv 2.4.2
```

**Nghĩa:**
- update version
- cập nhật version theo chuẩn header/changelog đã chốt

---

## `git`
**Cú pháp:**
```text
git
```

**Nghĩa:**
- xử lý phần Git theo ngữ cảnh hiện tại
- thường bao gồm: `git add / commit / tag / merge / push` theo scope đang bàn

---

# 6. Nhóm test

## `test`
**Cú pháp:**
```text
test
```

**Nghĩa:**
- go-test các bài test cho mô hình / dự án hiện tại

---

## `test-full`
**Cú pháp:**
```text
test-full
```

**Nghĩa:**
- liệt kê và thực hiện toàn bộ test cho cả Mac và RHEL

---

## `test-mac`
**Cú pháp:**
```text
test-mac
```

**Nghĩa:**
- thực hiện bài test tiếp theo trên macOS

---

## `test-rhel`
**Cú pháp:**
```text
test-rhel
```

**Nghĩa:**
- thực hiện bài test tiếp theo trên RHEL

---

## `test-mac-full`
**Cú pháp:**
```text
test-mac-full
```

**Nghĩa:**
- thực hiện toàn bộ test trên macOS

---

## `test-rhel-full`
**Cú pháp:**
```text
test-rhel-full
```

**Nghĩa:**
- thực hiện toàn bộ test trên RHEL

---

# 7. Nhóm title / thread

## `Title = <Tên chat mới>`
**Cú pháp:**
```text
Title = <Tên chat mới>
```

**Nghĩa:**
- đặt / đổi tên thread hiện hành theo tên đã ghi

---

## `Title` | `tit`
**Cú pháp:**
```text
Title|tit = <Tên chat mới>
```

**Nghĩa:**
- alias logic để đổi tên thread theo ngữ cảnh

---

# 8. Nhóm export file

## `ex` | `export file`
**Cú pháp:**
```text
ex
export file
```

**Nghĩa:**
- xuất nội dung hiện tại ra file
- tùy ngữ cảnh có thể là:
  - docx
  - pdf
  - excel
  - html
  - markdown
  - zip bundle

---

# 9. Nhóm output theo ngữ cảnh

## `o` | `out`
**Cú pháp:**
```text
o
out
```

**Nghĩa:**
- nói về output hiện tại
- có thể là screen output hoặc log file output theo ngữ cảnh dự án

---

## `ocr` | `out-screen`
**Cú pháp:**
```text
ocr
out-screen
```

**Nghĩa:**
- output của screen / terminal screen theo ngữ cảnh

---

## `olf` | `out-logfile`
**Cú pháp:**
```text
olf
out-logfile
```

**Nghĩa:**
- output của log file theo ngữ cảnh

---

# 10. Nhóm tài liệu / docs

## `chk-docs` | `chkdocs` | `c-docs` | `cdocs`
**Cú pháp:**
```text
chk-docs
chkdocs
c-docs
cdocs
```

**Nghĩa:**
- check docs
- rà soát + hiệu chỉnh + chuẩn hóa toàn bộ thư mục `docs/` theo đúng ngữ cảnh hiện tại

### Mode A — tôi thấy được nội dung tài liệu
Nếu tài liệu đã upload / đang hiện hữu / tôi đọc được:
- rà soát
- hiệu chỉnh
- chuẩn hóa
- edit trực tiếp nếu có thể
- hoặc tạo lại bản chuẩn để download

### Mode B — tôi không thấy được nội dung tài liệu
Nếu tôi không có nội dung:
- thông báo rõ giới hạn
- viết một prompt thật chặt để AI khác xử lý đúng ngữ cảnh

---

## `chk-doc` | `chkdoc` | `c-doc` | `cdoc [<tên tài liệu>]`
**Cú pháp:**
```text
chk-doc
chkdoc
c-doc
cdoc
cdoc <tên tài liệu hoặc bundle>
```

**Nghĩa:**
- rà soát + hiệu chỉnh + chuẩn hóa một tài liệu hoặc một bundle tài liệu

**Quy tắc:**
- nếu có tên kèm theo → xử lý theo tài liệu/bundle đó
- nếu không có tên kèm theo → xử lý theo tài liệu đã/đang xử lý gần nhất

---

# 11. Nhóm prompt delegation

## `pr [<tên | mô tả tác vụ>]`
**Cú pháp:**
```text
pr
pr <tên hoặc mô tả tác vụ>
```

**Nghĩa:**
- yêu cầu tôi viết một prompt thật chặt để AI khác thực hiện tác vụ

### Trường hợp 1 — có tên / mô tả cụ thể
- tôi phân tích tác vụ
- diễn giải rõ mục tiêu/ngữ cảnh
- viết prompt chặt, sẵn dùng

### Trường hợp 2 — không nêu nội dung cụ thể
- mặc định lấy tác vụ hiện đang xử lý
- diễn giải lại ngữ cảnh
- viết prompt chặt cho đúng task hiện tại

---

# 12. Nhóm show me / đề xuất

## `sh-me`
**Cú pháp:**
```text
sh-me
```

**Nghĩa:**
- show me
- đưa ra các đề xuất cho dự án hiện tại

---

# 13. Nhóm rpm

## `rpm`
**Cú pháp:**
```text
rpm
```

**Nghĩa:**
- hướng dẫn cấu trúc và tập lệnh build RPM cho dự án hiện tại trên RHEL
- có thể bao gồm:
  - build RPM trên RHEL
  - đồng bộ source từ Mac sang RHEL
  - quy trình build RPM trên máy RHEL mục tiêu

---

# 14. Rule nền đi kèm các alias này

## Rule A — xong một phase phải có testing/validation tương ứng
- code → compile/test/check
- docs → review/consistency/scope validation
- workflow → logic/operability validation

## Rule B — mọi tài liệu phải self-review ít nhất 2 vòng trước khi xuất file
- pass 1: logic / scope / nội dung
- pass 2: wording / consistency / usability

## Rule C — tài liệu/bundle cho dự án phải viết bằng tiếng Việt Unicode có dấu rõ ràng
- giữ nguyên các English technical terms cần thiết khi phù hợp

## Rule D — với docs aliases, nếu thấy nội dung thì xử lý trực tiếp; nếu không thấy nội dung thì viết prompt delegation phù hợp

---

# 15. Kết luận

Tài liệu này là bộ thỏa thuận shorthand toàn cục để dùng nhất quán giữa user và AI assistants trong các dự án hiện tại và về sau.
