# Global AI-Assisted Development Rules and Working Procedures
## Áp dụng toàn cục, bao hàm ATP

## 1. Mục đích

Tài liệu này tổng hợp toàn bộ các rule, quy ước, shorthand, và quy trình làm việc chặt chẽ đã được chốt trong quá trình phát triển ATP, đồng thời được nâng lên thành chuẩn áp dụng toàn cục cho các dự án khác khi phù hợp.

Mục tiêu là đảm bảo:
- continuity ngữ cảnh
- governance rõ ràng
- Git an toàn
- tài liệu nhất quán
- phát triển theo slice/phase có kiểm soát
- AI-assisted workflow có tính kỷ luật, ít sai số, ít scope drift

---

## 2. Phạm vi áp dụng

Áp dụng cho:
- ATP
- các dự án khác của người dùng
- mọi AI tham gia hỗ trợ dev, review, docs, governance, planning
- mọi actor có liên quan đến quản lý Git an toàn
- mọi workflow dev/review/docs/governance có dùng ChatGPT hoặc AI tương tự

---

## 3. Nguyên tắc nền tảng

### 3.1. Không suy đoán lại roadmap
Khi đã có baseline, lineage, freeze chain, hoặc governance chain, AI không được tự suy đoán lại roadmap từ đầu.

Phải bám vào:
- baseline hiện tại
- docs authority hiện có
- governance chain hiện có
- quyết định đã freeze/chốt trước đó

### 3.2. Ưu tiên bounded scope
Mọi bước triển khai phải:
- bounded
- traceable
- reviewable
- có in-scope / out-of-scope rõ
- tránh scope creep

### 3.3. Không mở slice/phase tiếp theo nếu chưa có evidence
Không mở slice/phase mới chỉ vì “có thể cần”.
Chỉ mở khi:
- đã review baseline hiện tại
- có gap thật sự
- có evidence justify

### 3.4. Phân tách rõ planning / implementation / consolidation / freeze
Mỗi phase phải được tách rõ:
- planning baseline
- runtime implementation
- supporting docs
- integration review
- consolidation decision
- freeze-readiness
- freeze close-out
- merge / tag

Không được làm lẫn phase nếu không có lý do rõ.

---

## 4. Rule workflow chặt chẽ cho project work

### 4.1. Mỗi task phải đi theo luồng chuẩn
Chuẩn tối thiểu:
1. xác định task
2. xác định scope
3. xác định docs/rules authority
4. triển khai bounded pass
5. review
6. test / validation
7. consolidation / close-out nếu tới mốc phù hợp

### 4.2. Mỗi task phải có review step
Không coi task là xong nếu chưa có bước review phù hợp với loại task đó.

### 4.3. Mỗi phase hoàn tất phải có validation/test
Sau mỗi phase phải có bước:
- test
- validation
- verification
- hoặc review evidence tương đương

### 4.4. Gate conclusion phải dựa trên trạng thái thật
Kết luận:
- pass
- blocker
- defer
- ready
- freeze-ready
- close-out-ready

phải dựa trên:
- repo state thật
- docs thật
- test state thật
- artifact thật

không dựa trên summary mơ hồ của AI.

---

## 5. Rule tài liệu toàn cục

### 5.1. Tài liệu phải viết bằng tiếng Việt rõ ràng
Tài liệu dự án/bundle nên viết bằng tiếng Việt có dấu rõ ràng.

### 5.2. Giữ English technical terms khi cần
Không dịch ép các technical terms nếu giữ English giúp chính xác hơn.

### 5.3. Mỗi thay đổi liên quan docs phải rà README system
Khi có thay đổi ở một tầng docs, phải review xem:
- local README
- index README
- docs root
- governance/docs entrypoint

có cần update không.

### 5.4. Không vá docs chắp vá nếu đã xác định sẽ có README-system pass
Nếu đã có chủ đích làm một pass chuẩn hóa toàn hệ thống README/docs sau, có thể defer một số docs alignment nhỏ, nhưng phải ghi nhận rõ là intentional defer.

### 5.5. Tài liệu bundle phải có vai trò rõ
Trong một doc bundle, mỗi file phải giữ vai trò riêng:
- roadmap / proposal
- execution plan
- semantic contract doc
- traceability model
- acceptance criteria
- review checklist
- integration review
- consolidation decision
- freeze-readiness
- freeze decision
- freeze close-out

Không được để duplication mơ hồ giữa các file nếu không thật sự cần.

---

## 6. Global shorthand / gõ tắt toàn cục

### 6.1. Agreement / decision shorthand
- `ok` = đồng ý với ngữ cảnh hiện tại / đề xuất / ý kiến hiện tại
- `ok <a b c...>` = chỉ đồng ý với phần `<a b c...>` trong ngữ cảnh hiện tại
- `no` = không đồng ý với ngữ cảnh hiện tại / đề xuất / ý kiến hiện tại
- `no <a b c...>` = chỉ không đồng ý với phần `<a b c...>`

### 6.2. Flow shorthand
- `go` = tiếp tục task / step / phase hiện tại theo ngữ cảnh
- `next` = bước / task / phase kế tiếp
- `next <a b c...>` = bước / task / phase kế tiếp là `<a b c...>`

### 6.3. Chat transition shorthand
Khi người dùng gõ:
- `sang chat mới`
- `switch new chat`
- hoặc câu tương đương mang nghĩa chuyển sang chat mới

AI phải:
1. đề xuất tên chat tối ưu theo ngữ cảnh
2. in ra handoff chuẩn để paste sang chat mới

---

## 7. Global Safe Git Rule (GSGR)

### 7.1. Nguyên tắc lõi
**GSGR = Check → Switch → Re-check → Execute**

Trước mọi combo Git quan trọng:
1. Check
2. Switch về đúng branch theo ngữ cảnh
3. Re-check
4. Execute

### 7.2. Mục tiêu
Ngăn các lỗi:
- commit nhầm branch
- push nhầm branch
- merge sai ngữ cảnh
- tag sai điểm
- cherry-pick nhầm nơi
- reset nhầm branch
- add nhầm file ngoài scope
- làm bẩn `main`

### 7.3. Phạm vi áp dụng
Áp dụng cho:
- ATP
- mọi project khác
- mọi combo Git quan trọng trên terminal Mac
- mọi AI
- mọi actor có liên quan đến Git an toàn

### 7.4. Các thao tác bắt buộc áp GSGR
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
- và mọi block Git có thể thay đổi history / branch / remote state

### 7.5. Quy tắc bổ sung
- không giả định terminal đang ở đúng branch
- không dùng `git add .` trong pass nhạy cảm
- `main` chỉ dùng cho merge / release / integrated baseline checks
- branch dev chỉ dùng cho work đúng ngữ cảnh
- trước mọi merge/tag phải check branch + clean tree + recent commits

---

## 8. Global Git-AI Command Completion Rule

### 8.1. Rule cốt lõi
Khi làm việc với Git qua AI:

- người dùng chỉ cần gõ alias ngắn
- AI phải là bên hoàn thiện câu lệnh cuối cùng
- AI phải trả ra lệnh:
  - đầy đủ
  - đúng ngữ cảnh hiện tại
  - an toàn theo GSGR
  - không bắt người dùng tự nghĩ low-level args

### 8.2. Alias đầu vào
Ví dụ:
- `git`
- `gs`
- `gsg`
- `git-safe`
- `git-guard`

### 8.3. Cách hiểu đúng
Các alias trên chỉ là:
- tín hiệu gọi chế độ Git-safe

Chúng không tự mang nghĩa:
- “làm bước tiếp theo” nếu chưa có mục tiêu rõ

### 8.4. Nghĩa vụ của AI
Khi nhận alias Git, AI phải:
1. nhận ra đây là Git-safe mode
2. suy ra ngữ cảnh hiện tại tốt nhất có thể
3. hoàn thiện thành một lệnh `gsgr ...` cuối cùng
4. không bắt người dùng tự viết dài hoặc tự chọn args thấp tầng

### 8.5. Baseline runtime đã chốt
- `gsgr` = global safe Git execution baseline

---

## 9. Rule command wrapper Git toàn cục

### 9.1. Runtime chuẩn
`gsgr` là command runtime chuẩn để thực thi Git an toàn.

### 9.2. Alias layer
Alias layer cho người dùng / AI có thể gồm:
- `gsg`
- `git-safe`
- `git-guard`

Alias nào bị collision với môi trường hiện có thì không overwrite thô bạo.

### 9.3. Collision-safe policy
Trước khi cài alias mới, phải check collision với:
- existing aliases
- shell functions
- commands
- shell config liên quan

Nếu alias đang được dùng cho mục đích unrelated:
- không overwrite
- skip alias đó
- report rõ

### 9.4. Logging
Nếu có logging cho `gsgr`, log phải:
- nằm ngoài repo
- nhẹ
- không làm fail main command nếu logging error

---

## 10. Rule branch / merge / release cho ATP và project tương tự

### 10.1. Main là integrated clean baseline
- `main` giữ trạng thái integrated/latest clean baseline
- dev làm trên branch ngữ cảnh riêng
- merge vào `main` khi baseline đủ chín

### 10.2. Mỗi version/release nên có branch hoặc nhịp riêng
Ví dụ:
- `v1.0-planning`
- `v1.0-slice-d`
- `v1.1-planning`

### 10.3. Freeze xong rồi mới merge/tag
Một baseline nên đi theo nhịp:
1. implementation
2. docs support
3. integration review
4. consolidation
5. freeze-readiness
6. freeze close-out
7. merge vào `main`
8. tag release

### 10.4. Không nhảy version/minor line quá sớm
Nếu major intent hiện tại chưa đủ dày, nên tiếp tục slice trong cùng line trước khi mở minor line mới.

---

## 11. Rule lineage / freeze / governance discipline

### 11.1. Mỗi baseline quan trọng phải có close-out
Sau khi freeze một baseline/version/slice, phải có close-out doc tương ứng.

### 11.2. Không rewrite frozen history tùy tiện
Docs freeze/close-out cũ không được rewrite bừa bãi.
Nếu cần correction, phải làm hẹp, rõ lý do.

### 11.3. Governance chain phải khép kín
Một freeze chain chuẩn nên có:
- integration review
- consolidation decision
- freeze-readiness assessment
- freeze decision
- freeze close-out

### 11.4. Conditions phải rõ
Khi baseline ready to integrate:
- phải nêu rõ merge/tag có cần explicit human approval hay không
- không claim merge/tag đã xảy ra nếu chưa thực sự xảy ra

---

## 12. Rule về ngữ cảnh chat và handoff

### 12.1. Khi chat quá nặng thì chuyển chat
Nếu chat quá nặng/chậm hoặc không còn phù hợp để dev, nên chuyển chat mới.

### 12.2. Chat mới phải có handoff chuẩn
Mục tiêu là:
- giữ continuity
- tránh AI suy đoán sai roadmap
- khóa đúng baseline hiện tại
- khóa đúng rule / shorthand / governance / git safety

### 12.3. Chat cũ có thể giữ làm review/history
Một chat có thể chuyển vai trò thành:
- review
- audit
- historical reference

khi dev flow đã cần sang chat mới.

---

## 13. Rule về cách AI phải phản hồi trong dev workflow

### 13.1. AI phải ưu tiên lệnh đúng scope
Nếu worktree có file dirty ngoài scope:
- AI phải cảnh báo
- AI phải đưa lệnh commit chỉ đúng file trong scope

### 13.2. AI không được trộn scope
Không commit lẫn:
- runtime slice hiện tại
- governance docs ngoài scope
- README-wide changes
- unrelated dirty files

### 13.3. AI phải giữ phân tách giữa:
- runtime baseline
- supporting docs
- governance/docs-global
- README-system cleanup
- release / merge / tag

### 13.4. AI phải phân biệt:
- bước dev
- bước docs
- bước review
- bước verification
- bước Git
- bước chat transition

Không được mặc định rằng một alias hay một câu ngắn đã tự xác định đủ toàn bộ ngữ cảnh nếu chưa có mục tiêu rõ.

---

## 14. ATP-specific expression đã được nâng lên thành global pattern

Các pattern đã được kiểm nghiệm trong ATP và có thể dùng làm global standard:

- slice-based bounded development
- supporting-doc bundle per slice
- integration review + consolidation per slice
- freeze-readiness + close-out per slice
- branch-safe Git via GSGR
- AI returns final safe command, user keeps shorthand input short
- chat handoff chuẩn khi context quá lớn

---

## 15. Kết luận

Bộ rule và quy trình trong tài liệu này là chuẩn làm việc toàn cục đã được hình thành từ quá trình phát triển ATP và đã được kiểm nghiệm thực tế.

Các nguyên tắc cốt lõi cần nhớ là:

- bounded scope
- governance-first discipline
- docs alignment
- test/review before conclusion
- freeze chain rõ ràng
- Git an toàn theo GSGR
- user shorthand ngắn, AI hoàn thiện command đầy đủ
- handoff chuẩn khi chuyển chat

Tài liệu này được dùng như một baseline toàn cục cho AI-assisted development workflow going forward.
