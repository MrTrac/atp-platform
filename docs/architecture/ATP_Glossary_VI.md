# ATP Glossary VI – Refined for V1.3.1 Draft R2

## 1. Mục đích tài liệu

Tài liệu này chuẩn hóa các thuật ngữ lõi dùng trong hệ sinh thái ATP để:

- tránh dùng từ chồng chéo;
- giữ wording nhất quán giữa các tài liệu kiến trúc;
- hỗ trợ cleanup và xuất bản các version chính thức sau này.

Bản refined này được rà lại để đồng bộ tốt hơn với ATP V1.3.1 Draft R2.

Nguyên tắc ngôn ngữ:
- **thuật ngữ lõi** giữ bằng **tiếng Anh**;
- **phần diễn giải** dùng **tiếng Việt**.

---

## 2. Thuật ngữ lõi

### Platform
Một hệ lõi có vai trò điều phối, cung cấp hạ tầng, chuẩn hóa hoặc năng lực phục vụ cho nhiều product/workflow; không phải một sản phẩm đầu cuối đơn lẻ.

**Ví dụ:** ATP

---

### Product
Một sản phẩm hoặc hệ sản phẩm cụ thể mà ATP phục vụ phát triển, vận hành hoặc điều phối.

**Ví dụ:** TDF, eco-suite, ticket-suite

---

### Lifecycle State
Trạng thái vòng đời hiện tại của một product trong Product Portfolio.

**Ví dụ:** incubating, active development, stabilization, maintenance, archived

---

### Portfolio Dependencies
Quan hệ phụ thuộc ở cấp danh mục giữa product, platform, shared assets và utilities.

---

### Module
Một khối chức năng có ranh giới logic rõ trong một product.

**Ví dụ:** mobile-app, admin-portal, chat-hub

---

### Component
Một thành phần kỹ thuật hoặc kiến trúc nhỏ hơn, có thể là phần con của một module hoặc product.

**Ví dụ:** routing engine, approval manager, provider registry parser

---

### Tool
Một công cụ được quản lý bên trong product boundary hoặc một workflow cụ thể; chưa chắc có lifecycle độc lập.

**Ví dụ:** `TDF/tools/checkos`

---

### Utility
Một công cụ độc lập cấp workspace, có thể phục vụ nhiều product/workflow và có thể có repo/lifecycle riêng.

**Ví dụ:** `utilities/trace_log`

**Quy tắc chốt:** mọi utility đều là tool theo nghĩa rộng, nhưng không phải mọi tool đều là utility.

---

### Provider
Bất kỳ nguồn lực thực thi nào có thể cung cấp một hoặc nhiều capability cho ATP, bao gồm AI SaaS, AI API, AI local software, local/private LLM runtime, IDE agent hoặc non-LLM execution resource.

---

### Interaction Pattern
Kiểu tương tác/vận hành của một provider.

**Ví dụ:** sync, async, human-mediated, file-exchange, streaming, batch

---

### Ownership Model
Mô tả provider do system quản lý, do user quản lý, hay do nhiều bên cùng quản lý.

**Ví dụ:** system-managed, user-managed, shared-managed

---

### Human-bridged
Workflow hoặc interaction pattern trong đó người vận hành đóng vai trò cầu nối giữa ATP và provider/executor.

**Ví dụ:** copy task package từ ATP sang SaaS UI rồi lấy output quay lại ATP

---

### Adapter
Lớp trung gian chuẩn hóa giao tiếp giữa ATP core và một provider cụ thể.

---

### Capability
Năng lực mà ATP cần cho một task, độc lập với vendor hoặc provider cụ thể.

**Ví dụ:** `create_plan`, `edit_code`, `validate_patch`

---

### Execution Intent
Ý định thực thi thực tế của một request, dùng để bổ sung cho Input Classification Model.

**Ví dụ:** design-only, review-only, write-patch, validate-only, release-prep, migration

---

### Node
Một máy hoặc môi trường thực thi có vai trò cụ thể trong hệ sinh thái ATP.

**Ví dụ:** Dev Control Node, ATP Control Node, AI Compute Node

---

### Data Locality
Mức độ gần/gắn của dữ liệu hoặc artifact với node/provider đang được cân nhắc route.

**Ý nghĩa:** ATP không chỉ tối ưu compute cost, mà còn phải xét vị trí dữ liệu và chi phí di chuyển artifact.

---

### Workspace Root
Gốc logic của toàn hệ sinh thái ATP.

**Trong kiến trúc hiện tại:** `SOURCE_DEV/`

---

### Workspace Runtime Zone
Vùng chứa dữ liệu runtime của ATP, tách khỏi source repos.

**Trong kiến trúc hiện tại:** `SOURCE_DEV/workspace/`

---

### Artifact
Mọi đầu ra, tài liệu trung gian hoặc kết quả có thể lưu, đối chiếu, audit và tái dùng trong một run.

---

### Artifact Freshness
Mức độ mới/hợp lệ theo thời điểm của một artifact hoặc evidence bundle.

**Ví dụ:** timestamp tạo bundle, run reference, source step reference, authoritative status

---

### Authoritative Artifact
Artifact được ATP coi là nguồn chuẩn đang có hiệu lực cho một run, một decision boundary hoặc một step handoff cụ thể.

**Ví dụ:** final approved plan, final validation summary, selected authoritative patch

---

### Run
Một instance thực thi hoàn chỉnh của ATP cho một request hoặc task cụ thể.

---

### Routing
Logic chọn capability path, provider, node và policy để thực thi một task.

---

### Policy
Tập quy tắc kiểm soát việc ATP ra quyết định, bao gồm routing policy, privacy policy, budget policy, escalation policy, approval policy.

---

### Approval Gate
Điểm dừng bắt buộc yêu cầu con người xác nhận trước khi ATP tiếp tục.

---

### Evidence Bundle
Một nhóm artifact được ATP chọn lọc và đóng gói để giao cho step tiếp theo hoặc cho một executor/reviewer cụ thể.

---

### Exchange Bundle
Một handoff bundle materialized trong `workspace/exchange/` để phục vụ workflow file-based hoặc UI-based.

---

### Manifest Reference
Một cơ chế handoff trong đó ATP không đưa toàn bộ nội dung, mà đưa manifest chỉ rõ artifact nào là authoritative, file nào phải đọc và file nào chỉ tham khảo.

---

## 3. Quy tắc dùng từ chính thức

1. Dùng **platform** cho ATP và các thực thể nền tảng tương tự.
2. Dùng **product** cho TDF và các sản phẩm ATP phục vụ.
3. Dùng **tool** khi nói về công cụ nằm trong product boundary.
4. Dùng **utility** khi nói về công cụ độc lập cấp workspace.
5. Dùng **provider** cho mọi nguồn lực thực thi đã đăng ký vào ATP, kể cả non-LLM.
6. Dùng **node** cho máy hoặc môi trường chạy.
7. Dùng **artifact** cho output có giá trị lưu giữ/audit.
8. Dùng **run** cho một phiên thực thi logic của ATP.
9. Dùng **lifecycle_state** khi nói về trạng thái vòng đời của product.
10. Dùng **portfolio_dependencies** khi nói về quan hệ phụ thuộc ở cấp danh mục.
11. Dùng **execution_intent** khi muốn phân biệt ý định thực thi so với loại request.
12. Dùng **interaction_pattern** và **ownership_model** như metadata chuẩn của provider registry.
13. Dùng **artifact freshness** khi cần nói về độ mới và độ hợp lệ theo thời điểm của context/artifact.
14. Dùng **authoritative artifact** khi muốn chỉ artifact đang có hiệu lực chuẩn cho một run hoặc decision boundary.
15. Dùng **data locality** khi nói về độ gần/gắn của dữ liệu với node/provider trong routing.
16. Dùng **human-bridged** khi nói về workflow có người làm cầu nối giữa ATP và provider/executor.

---

## 4. Cảnh báo các cặp từ dễ nhầm

### Tool vs Utility
- **Tool**: có thể nằm trong product
- **Utility**: độc lập cấp workspace

### Module vs Component
- **Module**: thiên về khối chức năng
- **Component**: thiên về cấu phần kỹ thuật/kiến trúc

### Workspace Root vs Workspace Runtime Zone
- **Workspace Root**: `SOURCE_DEV/`
- **Workspace Runtime Zone**: `SOURCE_DEV/workspace/`

### Provider vs Adapter
- **Provider**: nguồn lực thực thi
- **Adapter**: cách ATP giao tiếp với provider

### Request Type vs Execution Intent
- **Request Type**: loại yêu cầu
- **Execution Intent**: ý định thực thi thực tế của yêu cầu

### Provider vs Ownership Model
- **Provider**: nguồn lực thực thi
- **Ownership Model**: ai quản lý/kiểm soát provider đó

### Artifact vs Artifact Freshness
- **Artifact**: đầu ra hoặc bằng chứng được lưu
- **Artifact Freshness**: độ mới/hợp lệ theo thời điểm của artifact

### Selected Artifact vs Authoritative Artifact
- **Selected Artifact**: artifact được ATP chọn để dùng tiếp
- **Authoritative Artifact**: artifact được ATP coi là nguồn chuẩn đang có hiệu lực

### Data Locality vs Cost Profile
- **Data Locality**: dữ liệu/artifact đang nằm gần đâu
- **Cost Profile**: node/provider đó có chi phí vận hành ở mức nào

### Human-bridged vs API-driven
- **Human-bridged**: có người làm cầu nối
- **API-driven**: ATP có thể giao tiếp lập trình trực tiếp

---

## 5. Kết luận

Glossary này là nguồn chuẩn để:
- cleanup wording cho ATP V1.3 Draft;
- đồng bộ ngôn ngữ giữa các tài liệu ATP;
- làm baseline glossary đồng bộ cho V1.3, V1.3.1 Draft và V1.3.1 Draft R2.
