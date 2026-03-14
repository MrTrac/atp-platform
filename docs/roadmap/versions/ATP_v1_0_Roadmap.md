# ATP v1.0 Roadmap

## 1. Version
- Version target: `v1.0.0`
- Planning branch: `v1.0-planning`

---

## 2. Strategic intent

`ATP v1.0` là mốc đầu tiên đưa ATP từ trạng thái nền tảng đang được hình thành sang trạng thái **baseline platform có thể quản trị, kiểm thử, freeze, và phát triển tiếp một cách kỷ luật**.

Mục tiêu của `v1.0` không phải là mở rộng breadth lớn, cũng không phải là thêm quá nhiều capability mới ngoài kiểm soát.  
Mục tiêu chính là:

- chốt **platform baseline**
- chốt **governance baseline**
- chốt **documentation baseline**
- chốt **testing / validation baseline**
- chốt **version lifecycle baseline**

`v1.0` phải tạo ra một trạng thái mà từ đó các version sau có thể phát triển theo nhịp ổn định, có luật, có tài liệu, có tiêu chuẩn freeze/close-out rõ ràng.

---

## 3. Positioning of v1.0

### 3.1 What v1.0 is
`v1.0` là version:

- xác lập baseline chính thức đầu tiên cho ATP
- làm rõ doctrine/rules thành cơ chế vận hành cụ thể
- chuẩn hóa lifecycle của một version từ planning đến freeze/close-out
- củng cố docs system để đủ khả năng scale tiếp
- yêu cầu test/validation như điều kiện bắt buộc trước khi coi phase hoặc version là done

### 3.2 What v1.0 is not
`v1.0` không phải là version để:

- mở rộng kiến trúc theo chiều rộng quá lớn
- đẩy ATP sang plugin ecosystem hoàn chỉnh
- thêm UI / visual layer nặng
- triển khai automation phức tạp vượt quá mức testable hiện tại
- thay đổi doctrine nền tảng một cách đột ngột

---

## 4. Core objectives

### Objective 1 — Governance baseline
Chuẩn hóa ATP governance thành rule vận hành thực thi được, không chỉ còn là mô tả mức định hướng.

Kết quả mong muốn:

- rule set rõ ràng cho planning / execution / freeze / close-out
- definition of done rõ ở level phase và level version
- rule cập nhật `README.md` khi có thay đổi ở bất kỳ location nào
- rule branch / freeze / close-out được áp dụng thống nhất

### Objective 2 — Documentation baseline
Chuẩn hóa hệ thống tài liệu ATP thành một bộ docs có cấu trúc ổn định, dễ mở rộng, dễ kiểm tra tính nhất quán.

Kết quả mong muốn:

- docs tree ổn định hơn
- naming convention rõ ràng
- milestone templates và version documents được dùng nhất quán
- active docs, archive docs, roadmap docs liên kết mạch lạc

### Objective 3 — Runtime / orchestration baseline
Làm rõ contract và boundary cho flow orchestration cốt lõi của ATP ở mức đủ dùng cho baseline platform.

Kết quả mong muốn:

- core flow được mô tả rõ
- boundary giữa doctrine / orchestration / execution artifacts không mơ hồ
- các thành phần cốt lõi có contract rõ để test và mở rộng về sau

### Objective 4 — Testing / validation baseline
Biến test/validation thành điều kiện bắt buộc của mọi phase hoàn tất và của version close-out.

Kết quả mong muốn:

- có checklist hoặc test evidence tối thiểu cho các flow chính
- có cách chứng minh baseline hoạt động đúng ở mức version
- mọi deliverable chính đều có self-review / validation trước freeze

### Objective 5 — Release lifecycle baseline
Chuẩn hóa vòng đời một version ATP thành chain tài liệu và hành động rõ ràng.

Kết quả mong muốn:

- proposal → execution plan → implementation → freeze decision → close-out
- có tính truy vết giữa planning docs và freeze/close-out docs
- tạo được mẫu lặp cho các version sau

---

## 5. In-scope items

Các nội dung nên nằm trong scope `v1.0`:

### 5.1 Version lifecycle standardization
- chuẩn hóa chuỗi tài liệu của version
- chuẩn hóa điều kiện chuyển phase
- chuẩn hóa freeze gate và close-out gate

### 5.2 Definition of done
- định nghĩa done cho task / phase / version
- bắt buộc hóa test/validation trước khi coi là completed

### 5.3 Documentation normalization
- chuẩn hóa docs structure
- chuẩn hóa tham chiếu giữa các tài liệu
- giảm drift giữa roadmap, governance, archive, README

### 5.4 Governance operationalization
- biến doctrine/rules thành quy tắc thao tác cụ thể
- làm rõ rule áp dụng cho branch strategy, freeze, close-out, README update

### 5.5 Baseline orchestration contract
- xác định rõ mô hình flow cốt lõi của ATP
- mô tả boundary giữa các lớp logic/tài liệu/thực thi
- chuẩn bị nền cho expansion sau `v1.0`

### 5.6 Validation evidence
- tạo baseline evidence cho tính đúng đắn của core flow và docs/governance chain
- bảo đảm version có thể freeze trên cơ sở đã được kiểm chứng

---

## 6. Out-of-scope items

Các nội dung sau không nên đưa vào `v1.0` trừ khi thật sự bắt buộc để giữ integrity của baseline:

- mở rộng kiến trúc breadth lớn ngoài core baseline
- pluginization sâu hoặc generalization quá sớm
- UI / dashboard / visual management layer lớn
- automation liên nền tảng quá nặng khi test harness chưa đủ
- các cải tiến “nice-to-have” không trực tiếp phục vụ baseline readiness
- refactor lớn không gắn trực tiếp với governance/docs/runtime baseline

---

## 7. Planned execution shape

`v1.0` nên được triển khai theo các nhóm công việc sau:

### Slice A — Governance and version-control baseline
Tập trung vào:
- branch/freeze/close-out rules
- definition of done
- README update rule
- governance operational rules

### Slice B — Documentation system baseline
Tập trung vào:
- docs tree normalization
- version/milestone templates usage
- reference/link consistency
- archive vs active docs coherence

### Slice C — Runtime / orchestration baseline
Tập trung vào:
- core orchestration contract
- boundary clarification
- baseline implementation logic / structure nếu cần

### Slice D — Testing / validation baseline
Tập trung vào:
- test checklist / validation criteria
- evidence collection
- pre-freeze review gates
- close-out proof set

---

## 8. Mandatory constraints

Trong toàn bộ `v1.0`, các ràng buộc sau là bắt buộc:

1. Không hy sinh governance clarity để đổi lấy tốc độ.
2. Không mở rộng scope khi chưa chốt xong baseline hiện tại.
3. Mọi phase hoàn thành đều phải có test/validation step.
4. Mọi tài liệu giao ra phải được self-review ít nhất hai lượt trước khi freeze.
5. Mọi thay đổi ảnh hưởng đến ATP structure/rules phải cập nhật `README.md` đúng vị trí liên quan.
6. Không merge `main` khi chưa hoàn tất freeze evidence cần thiết.
7. Không để active docs và archive docs mâu thuẫn nhau tại thời điểm freeze.

---

## 9. Deliverables

Các deliverable tối thiểu cho `v1.0`:

- `ATP_v1_0_Roadmap.md`
- `ATP_v1_0_Milestone_Proposal.md`
- `ATP_v1_0_Execution_Plan.md`
- các tài liệu thực thi / cập nhật liên quan trong docs tree
- `ATP_v1_0_Freeze_Decision_Record`
- `ATP_v1_0_Closeout`
- test / validation evidence bundle tương ứng

---

## 10. Exit criteria

`v1.0` chỉ được coi là hoàn tất khi:

- scope baseline đã hoàn thành đúng boundary
- governance rules đủ rõ và được hiện thực thành tài liệu vận hành
- docs structure và references không còn drift nghiêm trọng
- core orchestration baseline đã được mô tả / hiện thực ở mức đủ dùng
- test/validation evidence đạt ngưỡng chấp nhận
- freeze decision có cơ sở rõ ràng
- close-out document chốt được trạng thái version một cách nhất quán
- branch có thể merge sạch vào `main`
- version có thể tag chính thức là `v1.0.0`

---

## 11. Success definition

`ATP v1.0` thành công nếu sau khi freeze:

- ATP có một baseline vận hành rõ ràng
- việc phát triển `v1.x` và các version sau không còn phụ thuộc vào “ngầm hiểu”
- governance, docs, test, và version lifecycle đã trở thành hệ thống có thể lặp lại
- `main` phản ánh đúng trạng thái integrated, stable, reviewable của platform

---

## 12. Immediate next step

Sau khi roadmap này được tạo, bước kế tiếp là tạo:

1. `ATP_v1_0_Milestone_Proposal.md`
2. `ATP_v1_0_Execution_Plan.md`

rồi phân rã `v1.0` thành các slice thực thi có thứ tự ưu tiên rõ ràng.
