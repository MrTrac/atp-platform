# ATP – Sơ đồ phân lớp và sơ đồ flow trực quan

Tài liệu này cung cấp 2 sơ đồ trực quan để dùng trong tài liệu kiến trúc ATP:

- **Sơ đồ phân lớp (Layered Architecture Diagram)**
- **Sơ đồ flow orchestration (Execution Flow Diagram)**

Các sơ đồ được viết bằng **Mermaid** để dễ nhúng vào markdown/docs về sau.

---

## 1. Sơ đồ phân lớp ATP

```mermaid
flowchart TB

    U["User / Operator"]
    R["Requested Task / Product Goal"]

    subgraph L1["Layer 1 – Interaction & Governance"]
        G1["Approval Gate"]
        G2["Policies\n(routing, privacy, budget, escalation)"]
        G3["Product Portfolio Governance\n(domain, lifecycle_state, risk, dependencies)"]
    end

    subgraph L2["Layer 2 – ATP Control Plane"]
        C1["Request Intake"]
        C2["Input Classification\n(domain / product_type / request_type / execution_intent)"]
        C3["Product Resolution"]
        C4["Context Packaging\nProduct Identity / Product Profile / Task Manifest / Evidence Bundle"]
        C5["Routing Engine"]
        C6["Cost Control"]
        C7["Run State / Decision State"]
    end

    subgraph L3["Layer 3 – Provider & Adapter Layer"]
        A1["UI Bridge Adapter"]
        A2["API Adapter"]
        A3["Local Service Adapter"]
        A4["Desktop App Bridge Adapter"]
        A5["Filesystem Exchange Adapter"]
        A6["SSH / Remote Command Adapter"]
    end

    subgraph L4["Layer 4 – Execution Providers"]
        P1["SaaS UI Providers\nChatGPT / Claude"]
        P2["SaaS API Providers"]
        P3["IDE Agent Providers\nCursor / others"]
        P4["Local LLM Runtime"]
        P5["Local AI Software"]
        P6["Remote Private Providers"]
        P7["Non-LLM Execution Providers\nshell / git / build / test / lint"]
    end

    subgraph L5["Layer 5 – Structural Foundation"]
        S1["Platform Repo\nplatforms/ATP"]
        S2["Product Repos\nproducts/TDF, ..."]
        S3["Shared Assets Repo\nshared/"]
        S4["Utilities Zone\nutilities/"]
        S5["Runtime Workspace\nworkspace/"]
    end

    subgraph L6["Layer 6 – Node Topology"]
        N1["Dev Control Node"]
        N2["ATP Control Node"]
        N3["AI Compute Node"]
        N4["Product Execution Node"]
        N5["Shared Service Node"]
    end

    U --> R
    R --> C1
    C1 --> C2
    C2 --> C3
    C3 --> C4
    C4 --> C5
    C5 --> C6
    C6 --> C7

    G2 --> C5
    G3 --> C3
    G1 --> C7

    C5 --> A1
    C5 --> A2
    C5 --> A3
    C5 --> A4
    C5 --> A5
    C5 --> A6

    A1 --> P1
    A2 --> P2
    A3 --> P4
    A4 --> P5
    A5 --> P3
    A5 --> P5
    A6 --> P6
    A6 --> P7

    C3 --> S2
    C4 --> S1
    C4 --> S2
    C4 --> S3
    C7 --> S5
    P7 --> S2
    P7 --> S5

    C5 --> N1
    C5 --> N2
    C5 --> N3
    C5 --> N4
    C5 --> N5
```

---

## 2. Sơ đồ flow orchestration ATP

```mermaid
flowchart TD

    A["1. User Request Intake"] --> B["2. Normalize Request"]
    B --> C["3. Input Classification\n(domain / product_type / request_type / execution_intent)"]
    C --> D["4. Product Resolution\nselect product + scope + policies"]
    D --> E["5. Context Packaging\nidentity + profile + manifest + evidence bundle"]
    E --> F["6. Routing Preparation\ncapability + sensitivity + provider candidates + node candidates"]
    F --> G["7. Route Selection\ntool-first / local-first / premium selective / multi-provider if justified"]
    G --> H["8. Execution via Adapter"]
    H --> I["9. Capture Output\nraw / filtered / selected / authoritative"]
    I --> J["10. Validation / Review\ntools + tests + AI review if needed"]
    J --> K{"11. Approval Gate / Escalation?"}
    K -- "Need revise" --> E
    K -- "Need second opinion" --> F
    K -- "Approved" --> L["12. Finalization\nfinal artifact + summary + run status"]
    L --> M["13. Handoff to Next Step\ninline / bundle / exchange / manifest reference"]
    M --> N["14. Close Run or Continue"]

    O["Runtime Workspace\nworkspace/atp-runs/<run-id>"] --- I
    O --- J
    O --- L
```

---

## 3. Sơ đồ flow chi tiết hơn theo artifact lifecycle

```mermaid
flowchart LR

    RQ["Request Artifact"] --> PL["Planning Artifact"]
    PL --> RT["Routing Decision Artifact"]
    RT --> EX["Executor Output Artifact"]
    EX --> FL["Filtered Artifact"]
    FL --> SL["Selected Artifact"]
    SL --> AU["Authoritative Artifact"]
    AU --> FN["Final Artifact Package"]

    EX -. can be stale .-> DP["Deprecated Artifact"]
    FL -. if rejected .-> DP
    SL -. superseded .-> DP
```

---

## 4. Gợi ý cách dùng trong docs ATP

- Dùng **Sơ đồ phân lớp ATP** ở phần mở đầu tài liệu kiến trúc tổng thể.
- Dùng **Sơ đồ flow orchestration ATP** ở phần mô tả execution model.
- Dùng **Sơ đồ artifact lifecycle** ở phần artifact-centric workflow, handoff và runtime workspace.

---

## 5. Ghi chú

Nếu hệ thống docs hoặc markdown renderer của anh chưa hỗ trợ Mermaid, có thể dùng chính các sơ đồ này làm nguồn để chuyển tiếp thành:
- PNG
- SVG
- draw.io
- hoặc sơ đồ trình chiếu.
