# ATP v1.0 Milestone Proposal

## 1. Milestone identity

- Milestone: `ATP v1.0`
- Target version: `v1.0.0`
- Planning branch: `v1.0-planning`
- Status: `Proposed`

---

## 2. Proposal summary

`ATP v1.0` được đề xuất là milestone baseline chính thức đầu tiên của ATP.

Milestone này không nhằm mở rộng breadth lớn hay theo đuổi capability expansion quá sớm.  
Trọng tâm của nó là đưa ATP vào một trạng thái đủ chuẩn để:

- quản trị được
- kiểm thử được
- freeze được
- close-out được
- phát triển tiếp được theo nhịp version có kỷ luật

Nói cách khác, `v1.0` phải chốt được baseline vận hành của ATP theo bốn trục chính:

- governance
- documentation
- runtime / orchestration baseline
- testing / validation

---

## 3. Why this milestone exists

Sau chuỗi version nền trước đó, ATP đã có một lượng doctrine, governance intent, template, và roadmap material đủ để bước sang một mốc cao hơn: **biến các nguyên tắc thành cơ chế vận hành thực sự**.

Nếu không có `v1.0` với mục tiêu baseline hóa rõ ràng, ATP sẽ gặp các rủi ro sau:

- phát triển tiếp dựa trên ngầm hiểu thay vì rule rõ ràng
- drift giữa roadmap docs, active docs, archive docs, và close-out docs
- scope expansion quá sớm khi nền test/validation chưa đủ chắc
- không có version lifecycle đủ chuẩn để lặp lại bền vững
- khó đánh giá objectively khi nào một phase hoặc version thực sự done

Vì vậy, `v1.0` tồn tại để chốt một mốc: từ “đang hình thành” sang “có baseline chính thức”.

---

## 4. Strategic outcome expected

Sau khi hoàn tất `v1.0`, ATP phải đạt được các kết quả chiến lược sau:

### 4.1 Governance outcome
ATP có bộ rule vận hành đủ rõ cho planning, execution, freeze, close-out, README update, và definition of done.

### 4.2 Documentation outcome
ATP có docs system ổn định hơn, dễ điều hướng hơn, và giảm mâu thuẫn giữa các lớp tài liệu.

### 4.3 Runtime / orchestration outcome
ATP có baseline contract đủ rõ cho core orchestration flow, đủ để test, review, và mở rộng có kiểm soát.

### 4.4 Validation outcome
Test/validation trở thành điều kiện bắt buộc trước khi kết luận hoàn tất phase hoặc version.

### 4.5 Lifecycle outcome
ATP có version lifecycle chain rõ ràng và lặp lại được cho các version sau.

---

## 5. Problem statement

Hiện trạng cần giải quyết trong `v1.0`:

1. ATP đã có nhiều doctrine và rule intent, nhưng cần operationalize thành quy tắc thao tác rõ ràng.
2. Docs system cần tiếp tục được chuẩn hóa để tránh drift và reference inconsistency.
3. Core orchestration baseline cần được mô tả / chốt boundary rõ hơn để trở thành nền mở rộng về sau.
4. Test/validation cần được đặt thành gate chính thức, thay vì chỉ là bước phụ trợ.
5. Version lifecycle cần được đóng thành mô hình chuẩn: proposal → execution → freeze → close-out.

---

## 6. Proposed scope

### 6.1 In scope

#### A. Governance baseline
- chuẩn hóa rule cho planning / execution / freeze / close-out
- chốt definition of done ở level phase và version
- chuẩn hóa README update rule
- chuẩn hóa branch discipline ở mức version

#### B. Documentation baseline
- chuẩn hóa docs structure
- chuẩn hóa naming / placement / reference logic
- bảo đảm coherence giữa active docs, roadmap docs, archive docs, close-out docs
- dùng milestone templates nhất quán hơn

#### C. Runtime / orchestration baseline
- làm rõ contract cho core ATP orchestration
- làm rõ boundary giữa doctrine, orchestration, execution, evidence
- chốt baseline structure đủ dùng cho `v1.x`

#### D. Testing / validation baseline
- định nghĩa validation expectations tối thiểu
- tạo evidence logic cho pre-freeze assessment
- bảo đảm mọi phase hoàn tất đều có validation step
- đưa self-review thành bước bắt buộc trước khi freeze artifact

### 6.2 Out of scope

- plugin ecosystem hoàn chỉnh
- UI / dashboard layer lớn
- generalization quá sớm vượt quá nhu cầu baseline
- automation expansion lớn nếu chưa có test harness tương xứng
- refactor lớn không trực tiếp phục vụ baseline readiness
- breadth expansion ngoài các boundary đã nêu trong roadmap

---

## 7. Proposed milestone slices

### Slice A — Governance and control baseline
Mục tiêu:
- operationalize ATP doctrine/rules
- chuẩn hóa freeze / close-out / done criteria
- khóa governance behavior ở mức platform baseline

### Slice B — Documentation baseline
Mục tiêu:
- normalize docs tree
- reduce document drift
- làm rõ map giữa active, roadmap, archive, template, close-out materials

### Slice C — Runtime / orchestration baseline
Mục tiêu:
- chốt contract / boundary của core orchestration
- mô tả baseline structure phục vụ implementation và review

### Slice D — Testing / validation baseline
Mục tiêu:
- chuẩn hóa validation gate
- tạo baseline evidence model
- hỗ trợ freeze decision bằng cơ sở kiểm chứng rõ ràng

---

## 8. Risks and controls

### Risk 1 — Scope expansion too early
Rủi ro:
`v1.0` bị kéo sang breadth expansion thay vì baseline completion.

Kiểm soát:
- bám chặt roadmap boundary
- mọi nội dung không phục vụ baseline phải defer
- dùng exit criteria để chặn scope creep

### Risk 2 — Governance remains descriptive only
Rủi ro:
rule vẫn chỉ là mô tả, không thành quy tắc thao tác cụ thể.

Kiểm soát:
- yêu cầu mỗi rule phải có tác động vận hành rõ
- review chéo giữa governance docs và execution docs

### Risk 3 — Documentation inconsistency
Rủi ro:
active docs, archive docs, roadmap docs không đồng bộ.

Kiểm soát:
- normalize references
- review toàn chuỗi tài liệu liên quan
- cập nhật README theo standing rule

### Risk 4 — Weak validation gate
Rủi ro:
version được xem là done nhưng thiếu evidence đủ mạnh.

Kiểm soát:
- bắt buộc validation step sau mỗi phase
- yêu cầu proof set tối thiểu trước freeze
- close-out phải phản ánh đúng trạng thái validation

### Risk 5 — Boundary ambiguity in core ATP model
Rủi ro:
core orchestration baseline không rõ boundary, gây drift ở các version sau.

Kiểm soát:
- mô tả contract rõ
- tách rõ doctrine / flow / evidence / docs responsibilities
- review lại bằng tiêu chí consistency và extensibility

---

## 9. Dependencies

Milestone này phụ thuộc vào:

- trạng thái freeze/close-out sạch của `v0.7`
- branch `v1.0-planning` sạch và dùng làm planning baseline
- bộ template milestone đã được dựng trước đó
- standing governance rules đã được chốt trong ATP doctrine/documentation system

---

## 10. Deliverables proposed

Các deliverable chính của milestone:

- `ATP_v1_0_Roadmap.md`
- `ATP_v1_0_Milestone_Proposal.md`
- `ATP_v1_0_Execution_Plan.md`
- các tài liệu cập nhật thuộc docs/governance/runtime/test baselines
- `ATP_v1_0_Freeze_Decision_Record`
- `ATP_v1_0_Closeout`
- validation / evidence bundle phục vụ freeze decision

---

## 11. Acceptance logic for entering execution

Milestone `v1.0` được phép chuyển từ proposal sang execution khi:

- roadmap đã chốt boundary rõ
- proposal đã xác lập đúng strategic intent
- các slice đã được xác định rõ mục tiêu
- scope / out-of-scope đủ chặt để kiểm soát drift
- execution plan có thể viết thành chuỗi hành động cụ thể

---

## 12. Proposal decision

### Proposed decision
**Approve entry into `ATP v1.0` execution planning.**

### Rationale
`v1.0` là milestone cần thiết và đúng thời điểm để ATP chốt baseline platform đầu tiên.  
Không thực hiện milestone này sẽ làm tăng rủi ro drift, scope creep, thiếu governance clarity, và thiếu chuẩn version lifecycle cho các bước tiếp theo.

---

## 13. Immediate next step

Sau proposal này, tài liệu cần tạo tiếp theo là:

- `ATP_v1_0_Execution_Plan.md`

Tài liệu đó sẽ chuyển milestone từ mức “đề xuất đúng” sang mức “có thể thực thi theo phase/slice rõ ràng”.
