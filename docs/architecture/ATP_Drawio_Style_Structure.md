# ATP – Draw.io Style Structure

Tài liệu này là **bộ khung sơ đồ theo kiểu draw.io** cho ATP, dùng làm nguồn dựng hình kiến trúc.
Mục tiêu là giúp anh hoặc AI khác có thể:
- đưa vào draw.io để vẽ lại nhanh;
- dùng làm blueprint chuẩn cho việc dựng sơ đồ;
- giữ layout, grouping và nhãn logic nhất quán qua nhiều vòng chỉnh sửa.

---

## 1. Quy ước chung khi dựng trong draw.io

### 1.1 Kiểu khối
- **Container lớn**: hình chữ nhật bo góc lớn
- **Repo / Zone / Layer**: hình chữ nhật bo góc vừa
- **Node / Provider / Adapter**: hình chữ nhật thường
- **Decision / Gate**: hình thoi
- **Artifact / Output**: hình tài liệu hoặc hình chữ nhật góc mềm
- **Flow line**:
  - nét liền = flow chính
  - nét đứt = dependency / reference / optional path

### 1.2 Màu đề xuất
- **Structural / Storage**: xanh dương nhạt
- **Control Plane / Logic**: xanh lá nhạt
- **Provider / Adapter**: tím nhạt
- **Node Topology**: cam nhạt
- **Runtime / Artifact**: xám nhạt
- **Approval / Gate / Risk**: đỏ nhạt
- **Shared / Cross-cutting**: vàng nhạt

### 1.3 Quy tắc đặt nhãn
- Dùng **tiếng Anh cho thuật ngữ lõi**
- Dùng **tiếng Việt cho mô tả phụ nếu cần**
- Tránh label quá dài trong box; đưa mô tả dài sang note box nếu cần

---

## 2. Diagram A – ATP Overall Layered Architecture

### 2.1 Mục tiêu
Sơ đồ này dùng để nhìn ATP ở mức tổng thể theo các lớp kiến trúc.

### 2.2 Bố cục khuyến nghị
- Hướng dọc từ trên xuống
- User / Operator ở đỉnh
- Structural Foundation ở đáy
- Các lớp control, provider, node nằm giữa

### 2.3 Cấu trúc khối

```text
[User / Operator]
        |
[Requested Task / Product Goal]
        |
+------------------------------------------------------+
| Layer 1 – Interaction & Governance                   |
|  - Approval Gate                                     |
|  - Policies                                          |
|  - Product Portfolio Governance                      |
+------------------------------------------------------+
        |
+------------------------------------------------------+
| Layer 2 – ATP Control Plane                          |
|  - Request Intake                                    |
|  - Input Classification                              |
|  - Product Resolution                                |
|  - Context Packaging                                 |
|  - Routing Engine                                    |
|  - Cost Control                                      |
|  - Run State / Decision State                        |
+------------------------------------------------------+
        |
+------------------------------------------------------+
| Layer 3 – Provider & Adapter Layer                   |
|  - UI Bridge Adapter                                 |
|  - API Adapter                                       |
|  - Local Service Adapter                             |
|  - Desktop App Bridge Adapter                        |
|  - Filesystem Exchange Adapter                       |
|  - SSH / Remote Command Adapter                      |
+------------------------------------------------------+
        |
+------------------------------------------------------+
| Layer 4 – Execution Providers                        |
|  - SaaS UI Providers                                 |
|  - SaaS API Providers                                |
|  - IDE Agent Providers                               |
|  - Local LLM Runtime                                 |
|  - Local AI Software                                 |
|  - Remote Private Providers                          |
|  - Non-LLM Execution Providers                       |
+------------------------------------------------------+
        |
+------------------------------------------------------+
| Layer 5 – Structural Foundation                      |
|  - platforms/ATP                                     |
|  - products/*                                        |
|  - shared/                                           |
|  - utilities/                                        |
|  - workspace/                                        |
+------------------------------------------------------+
        |
+------------------------------------------------------+
| Layer 6 – Node Topology                              |
|  - Dev Control Node                                  |
|  - ATP Control Node                                  |
|  - AI Compute Node                                   |
|  - Product Execution Node                            |
|  - Shared Service Node                               |
+------------------------------------------------------+
```

### 2.4 Các đường nối nên có
- `Policies` -> `Routing Engine`
- `Product Portfolio Governance` -> `Product Resolution`
- `Routing Engine` -> toàn bộ nhóm adapters
- từng adapter -> nhóm provider phù hợp
- `Run State / Decision State` -> `workspace/`
- `Product Resolution` -> `products/*`
- `Context Packaging` -> `platforms/ATP`, `products/*`, `shared/`

### 2.5 Note box nên thêm
- ATP là **local-first but node-portable**
- ATP là **provider-agnostic**
- ATP là **artifact-centric**
- ATP là **single source of contextual truth**

---

## 3. Diagram B – Storage / Repo / Workspace Map

### 3.1 Mục tiêu
Sơ đồ này dùng để giải thích rất rõ:
- đâu là repo;
- đâu là container logic;
- đâu là runtime zone;
- đâu là shared repo;
- đâu là workspace root.

### 3.2 Bố cục khuyến nghị
- Hướng cây thư mục từ trái sang phải hoặc từ trên xuống
- `SOURCE_DEV/` là container lớn nhất

### 3.3 Cấu trúc khối

```text
+------------------------------------------------------------------+
| SOURCE_DEV/                                                      |
| [portable workspace root]                                        |
|                                                                  |
|  +-----------------------+                                       |
|  | platforms/            |  [logic container]                    |
|  |  +-----------------+  |                                       |
|  |  | ATP/            |  |  [repo]                              |
|  |  +-----------------+  |                                       |
|  +-----------------------+                                       |
|                                                                  |
|  +-----------------------+                                       |
|  | products/             |  [logic container]                    |
|  |  +-----------------+  |                                       |
|  |  | TDF/            |  |  [repo]                              |
|  |  |  tools/         |  |  [product-managed tools]             |
|  |  +-----------------+  |                                       |
|  |  | <other-product> |  |  [repo]                              |
|  |  +-----------------+  |                                       |
|  +-----------------------+                                       |
|                                                                  |
|  +-----------------------+                                       |
|  | shared/               |  [repo shared assets]                 |
|  |  - standards          |                                       |
|  |  - templates          |                                       |
|  |  - schemas            |                                       |
|  |  - prompt-kits        |                                       |
|  |  - glossaries         |                                       |
|  |  - common-libs        |                                       |
|  +-----------------------+                                       |
|                                                                  |
|  +-----------------------+                                       |
|  | utilities/            |  [logic container]                    |
|  |  <utility-name>/      |  [repo if needed]                     |
|  +-----------------------+                                       |
|                                                                  |
|  +-----------------------+                                       |
|  | workspace/            |  [runtime zone, not repo]             |
|  |  - atp-runs/          |                                       |
|  |  - atp-artifacts/     |                                       |
|  |  - atp-cache/         |                                       |
|  |  - atp-staging/       |                                       |
|  |  - exchange/          |                                       |
|  +-----------------------+                                       |
+------------------------------------------------------------------+
```

### 3.4 Note box nên thêm
- `SOURCE_DEV/` không là repo tổng
- `shared/` là repo riêng
- `workspace/` không dùng làm repo Git
- `utilities/` là optional container
- `tools/` thuộc `products/TDF/`, không tách repo quá sớm

---

## 4. Diagram C – Provider & Adapter Topology

### 4.1 Mục tiêu
Sơ đồ này dùng để giải thích:
- ATP không kết nối cứng theo vendor;
- provider được route qua adapter;
- BYOAI đi vào provider registry như thế nào.

### 4.2 Bố cục khuyến nghị
- ATP Control Plane ở giữa trái
- Adapter Layer ở giữa
- Providers ở bên phải
- Provider Registry ở trên hoặc dưới ATP
- BYOAI ở dưới cùng hoặc góc dưới phải

### 4.3 Cấu trúc khối

```text
+-----------------------------+
| ATP Control Plane           |
| - Routing Engine            |
| - Cost Control              |
| - Context Packaging         |
+-----------------------------+
            |
            v
+-----------------------------+
| Adapter Layer               |
| - UI Bridge Adapter         |
| - API Adapter               |
| - Local Service Adapter     |
| - Desktop App Bridge        |
| - Filesystem Exchange       |
| - SSH / Remote Command      |
+-----------------------------+
            |
            v
+------------------------------------------------------+
| Providers                                            |
|  - SaaS UI Providers                                 |
|  - SaaS API Providers                                |
|  - IDE Agent Providers                               |
|  - Local LLM Runtime Providers                       |
|  - Local AI Software Providers                       |
|  - Remote Private Providers                          |
|  - Non-LLM Execution Providers                       |
+------------------------------------------------------+

+------------------------------------------+
| Provider Registry                        |
| - provider_id                            |
| - provider_class                         |
| - capabilities                           |
| - node_binding                           |
| - data_scope_policy                      |
| - interaction_pattern                    |
| - ownership_model                        |
| - preferred_product_domains              |
+------------------------------------------+

+------------------------------------------+
| BYOAI                                    |
| - Bring Your Subscription                |
| - Bring Your Endpoint                    |
| - Bring Your Node                        |
| - Bring Your Local AI Software           |
+------------------------------------------+
```

### 4.4 Các đường nối nên có
- `ATP Control Plane` -> `Provider Registry`
- `Provider Registry` -> `Routing Engine`
- `Routing Engine` -> `Adapter Layer`
- `BYOAI` -> `Provider Registry`
- `Provider Registry` -> từng nhóm provider
- note nét đứt từ `Policies` -> `Provider Registry`

### 4.5 Note box nên thêm
- route theo **capability**, không theo vendor
- local/private AI là **first-class provider**
- non-LLM executors là **provider hợp lệ**
- BYOAI phải khai báo `interaction_pattern` và `ownership_model`

---

## 5. Diagram D – Node Topology / Routing / Cost

### 5.1 Mục tiêu
Sơ đồ này dùng để nhìn ATP như hệ multi-node.

### 5.2 Bố cục khuyến nghị
- ATP Control Node ở trung tâm
- Dev Control Node ở bên trái
- AI Compute Node ở bên phải trên
- Product Execution Node ở bên phải dưới
- Shared Service Node ở dưới trung tâm

### 5.3 Cấu trúc khối

```text
                  +-----------------------+
                  | Dev Control Node      |
                  | - user interaction    |
                  | - review / approval   |
                  +-----------------------+
                              |
                              |
+-----------------------+     |      +-----------------------+
| Shared Service Node   |-----+------| ATP Control Node      |
| - artifact service    |            | - ATP repo            |
| - registry service    |            | - policies            |
| - shared cache        |            | - run state           |
+-----------------------+            | - routing / cost      |
                                     +-----------------------+
                                              /   \
                                             /     \
                                            /       \
                           +-------------------+   +-----------------------+
                           | AI Compute Node   |   | Product Execution Node|
                           | - local AI        |   | - build / test / run  |
                           | - private infer   |   | - product validation  |
                           +-------------------+   +-----------------------+
```

### 5.4 Route note boxes
Thêm 4 note box nhỏ cạnh `ATP Control Node`:
- Deterministic Tool Route
- Low-Cost Local Intelligence Route
- Premium Reasoning Route
- Multi-Provider Arbitration Route

### 5.5 Cost / routing note box
- route theo capability + provider + node
- xét cost, privacy, availability
- xét data locality và artifact proximity
- tránh chi phí di chuyển artifact không cần thiết

---

## 6. Diagram E – ATP Orchestration Execution Flow

### 6.1 Mục tiêu
Sơ đồ này là flow chính để giải thích ATP thực thi một request như thế nào.

### 6.2 Bố cục khuyến nghị
- Hướng dọc từ trên xuống
- Decision/Gate ở giữa
- Finalization ở cuối
- Runtime Workspace note box nằm bên phải

### 6.3 Cấu trúc khối

```text
[1. User Request Intake]
          |
[2. Normalize Request]
          |
[3. Input Classification]
(domain / product_type / request_type / execution_intent)
          |
[4. Product Resolution]
(select product + scope + policies)
          |
[5. Context Packaging]
(identity + profile + manifest + evidence bundle)
          |
[6. Routing Preparation]
(capability + sensitivity + provider candidates + node candidates)
          |
[7. Route Selection]
(tool-first / local-first / premium selective / multi-provider if justified)
          |
[8. Execution via Adapter]
          |
[9. Capture Output]
(raw / filtered / selected / authoritative)
          |
[10. Validation / Review]
(tools + tests + AI review if needed)
          |
       <Decision>
 [11. Approval Gate / Escalation?]
       /           |            \
 revise      second opinion    approved
   |               |             |
   +-------> [5]   +-----> [6]   v
                             [12. Finalization]
                                      |
                          [13. Handoff to Next Step]
                         (inline / bundle / exchange / manifest)
                                      |
                           [14. Close Run or Continue]
```

### 6.4 Runtime workspace note box
Vẽ note box bên phải:
```text
Runtime Workspace
- atp-runs/<run-id>/
- request/
- manifests/
- planning/
- routing/
- executor-outputs/
- validation/
- decisions/
- final/
- logs/
```

### 6.5 Note box nên thêm
- ATP là **single source of contextual truth**
- AI không tự mò toàn bộ workspace
- ATP handoff artifact theo ngữ cảnh có kiểm soát

---

## 7. Diagram F – Artifact Lifecycle

### 7.1 Mục tiêu
Sơ đồ này dùng để giải thích rõ semantics của artifact.

### 7.2 Bố cục khuyến nghị
- Hướng ngang từ trái sang phải
- `Deprecated Artifact` ở dưới hoặc bên dưới các nhánh lỗi/thay thế

### 7.3 Cấu trúc khối

```text
[Request Artifact]
        |
[Planning Artifact]
        |
[Routing Decision Artifact]
        |
[Executor Output Artifact]
        |
[Filtered Artifact]
        |
[Selected Artifact]
        |
[Authoritative Artifact]
        |
[Final Artifact Package]

Rejected / stale / superseded
        \
         \
      [Deprecated Artifact]
```

### 7.4 Note box nên thêm
- freshness phải đi cùng authoritative status
- selected chưa chắc là authoritative
- authoritative có thể bị superseded về sau
- deprecated không xóa nghĩa là vẫn cần audit trail

---

## 8. Trình tự dựng sơ đồ trong draw.io

### Bước 1
Dựng **Diagram B – Storage / Repo / Workspace Map** trước để chốt nền.

### Bước 2
Dựng **Diagram A – Overall Layered Architecture** để chốt các lớp logic.

### Bước 3
Dựng **Diagram C – Provider & Adapter Topology** và **Diagram D – Node Topology / Routing / Cost**.

### Bước 4
Dựng **Diagram E – Orchestration Execution Flow**.

### Bước 5
Dựng **Diagram F – Artifact Lifecycle**.

---

## 9. Ghi chú chốt

Bộ draw.io style structure này nên được xem là:
- blueprint dựng hình cho ATP;
- nguồn gốc cho slide-ready diagram pack về sau;
- điểm chuẩn để nhiều AI khác nhau có thể vẽ lại sơ đồ mà vẫn giữ đúng logic.

Nếu cần export đẹp hơn, có thể chuyển các sơ đồ này sang:
- draw.io
- diagrams.net
- SVG
- PNG
- slide presentation.
