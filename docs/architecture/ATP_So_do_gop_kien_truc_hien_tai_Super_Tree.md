# ATP – Sơ đồ gộp kiến trúc hiện tại (Super Tree)

Tài liệu này ghi lại **sơ đồ gộp kiến trúc ATP hiện tại** dưới một cấu trúc cây duy nhất, bao gồm đồng thời:

- cây thư mục lưu trữ;
- cây kiến trúc logic;
- cây luồng thực thi orchestration.

---

```text
ATP – Super Tree (Current Consolidated Architecture)

SOURCE_DEV/                                                        [portable workspace root]
├── platforms/                                                     [logic container]
│   └── ATP/                                                       [platform repo]
│       ├── core/                                                  [ATP core]
│       ├── adapters/                                              [provider integration layer]
│       │   ├── providers/
│       │   │   ├── chatgpt/
│       │   │   ├── claude/
│       │   │   ├── cursor/
│       │   │   ├── local_llm/
│       │   │   ├── local_ai_software/
│       │   │   ├── remote_private/
│       │   │   └── ...
│       │   └── contracts/
│       ├── registry/                                              [governance + metadata]
│       │   ├── providers/
│       │   ├── capabilities/
│       │   ├── products/
│       │   ├── nodes/
│       │   └── policies/
│       ├── routing/                                               [capability/provider/node routing]
│       ├── cost/                                                  [resource economics + budget logic]
│       ├── profiles/                                              [environment/user/provider profiles]
│       ├── prompts/                                               [prompt kits]
│       ├── templates/                                             [manifests/reports/notes]
│       ├── scripts/
│       ├── docs/
│       └── tests/
│
├── products/                                                      [logic container]
│   ├── TDF/                                                       [reference product #1 repo]
│   │   ├── tools/                                                 [product-managed tools]
│   │   ├── core/
│   │   ├── cli/
│   │   ├── docs/
│   │   └── ...
│   └── <other-product>/                                           [future product repos]
│       └── ...
│
├── shared/                                                        [shared assets repo]
│   ├── standards/
│   ├── templates/
│   ├── schemas/
│   ├── prompt-kits/
│   ├── glossaries/
│   └── common-libs/
│
├── utilities/                                                     [logic container]
│   └── <utility-name>/                                            [independent utility repo if needed]
│       └── ...
│
└── workspace/                                                     [runtime zone, not a repo]
    ├── atp-runs/
    │   └── <run-id>/
    │       ├── request/
    │       ├── manifests/
    │       ├── planning/
    │       ├── routing/
    │       ├── executor-outputs/
    │       ├── validation/
    │       ├── decisions/
    │       ├── final/
    │       └── logs/
    ├── atp-artifacts/
    ├── atp-cache/
    ├── atp-staging/
    └── exchange/
        ├── current-task/
        ├── current-review/
        └── current-approval/


ATP LOGICAL ARCHITECTURE
├── 1. Structural Foundation
│   ├── Workspace Root
│   │   └── SOURCE_DEV/
│   ├── Platform Repos
│   │   └── ATP
│   ├── Product Repos
│   │   └── TDF, future products...
│   ├── Shared Assets Repo
│   │   └── shared/
│   ├── Utility Zone
│   │   └── utilities/
│   └── Runtime Workspace
│       └── workspace/
│
├── 2. Product Portfolio Layer
│   ├── Product Portfolio Model
│   ├── Product Portfolio Governance
│   │   ├── domain
│   │   ├── maturity_level
│   │   ├── lifecycle_state
│   │   ├── owner/operator
│   │   ├── risk_level
│   │   ├── provider_policy
│   │   ├── approval_policy
│   │   └── portfolio_dependencies
│   └── Input Classification
│       ├── domain
│       ├── product_type
│       ├── request_type
│       └── execution_intent
│
├── 3. Context & Artifact Layer
│   ├── Product Identity
│   ├── Product Profile
│   ├── Task Manifest
│   ├── Evidence Bundle
│   │   ├── files/snippets/diffs/logs/tests/docs
│   │   └── freshness metadata
│   │       ├── timestamp
│   │       ├── run reference
│   │       ├── source step reference
│   │       └── authoritative/reference status
│   ├── Artifact Semantics
│   │   ├── raw
│   │   ├── filtered
│   │   ├── selected
│   │   ├── authoritative
│   │   └── deprecated
│   └── Workspace Artifact Handoff
│       ├── inline context
│       ├── evidence bundle
│       ├── exchange bundle
│       └── manifest reference
│
├── 4. Provider Architecture Layer
│   ├── Capability
│   ├── Provider
│   │   ├── SaaS UI Provider
│   │   ├── SaaS API Provider
│   │   ├── IDE Agent Provider
│   │   ├── Local LLM Runtime Provider
│   │   ├── Local AI Software Provider
│   │   ├── Remote Private Provider
│   │   └── Non-LLM Execution Provider
│   ├── Adapter
│   │   ├── UI Bridge Adapter
│   │   ├── API Adapter
│   │   ├── Local Service Adapter
│   │   ├── Desktop App Bridge Adapter
│   │   ├── Filesystem Exchange Adapter
│   │   └── SSH / Remote Command Adapter
│   ├── Provider Registry
│   │   ├── provider_id
│   │   ├── provider_class
│   │   ├── capabilities
│   │   ├── node_binding
│   │   ├── data_scope_policy
│   │   ├── preferred_product_domains
│   │   ├── interaction_pattern
│   │   └── ownership_model
│   └── BYOAI
│       ├── Bring Your Subscription
│       ├── Bring Your Endpoint
│       ├── Bring Your Node
│       └── Bring Your Local AI Software
│
├── 5. Node & Execution Topology Layer
│   ├── Dev Control Node
│   ├── ATP Control Node
│   ├── AI Compute Node
│   ├── Product Execution Node
│   └── Shared Service Node
│
├── 6. Routing & Cost Layer
│   ├── Capability-based Routing
│   ├── Node-aware Routing
│   ├── Routing Confidence
│   ├── Data Locality / Artifact Proximity
│   ├── Cost-Aware Routing
│   │   ├── Deterministic Tool Route
│   │   ├── Low-Cost Local Intelligence Route
│   │   ├── Premium Reasoning Route
│   │   └── Multi-Provider Arbitration Route
│   └── Cost Control Policy
│       ├── Run Budget
│       ├── Product Budget
│       ├── Capability Budget
│       ├── Escalation Gate
│       ├── Provider Priority Policy
│       └── Audit Cost Trace
│
└── 7. Operating Principles
    ├── platform-first
    ├── provider-agnostic
    ├── adapter-first
    ├── artifact-centric
    ├── human-gated
    ├── local-first but node-portable
    └── single source of contextual truth


ATP ORCHESTRATION FLOW
├── 1. User Request Intake
│   ├── receive raw request
│   ├── normalize request
│   └── create request artifact
│
├── 2. Classification
│   ├── domain
│   ├── product_type
│   ├── request_type
│   └── execution_intent
│
├── 3. Product Resolution
│   ├── identify target product
│   ├── load product profile
│   ├── load repo boundary
│   ├── load module/component scope
│   └── load policy/approval rules
│
├── 4. Context Packaging
│   ├── build Product Identity
│   ├── build Task Manifest
│   ├── select Evidence Bundle
│   ├── attach freshness metadata
│   └── mark authoritative references
│
├── 5. Routing Preparation
│   ├── determine required capability
│   ├── determine task sensitivity
│   ├── filter provider candidates
│   ├── filter node candidates
│   └── apply routing policy
│
├── 6. Route Selection
│   ├── tool-first?
│   ├── local/private-first?
│   ├── premium selective?
│   ├── multi-provider justified?
│   ├── evaluate cost/privacy/latency
│   ├── evaluate data locality
│   └── choose provider + node + route
│
├── 7. Execution
│   ├── choose adapter
│   ├── send task package
│   ├── send context bundle
│   ├── receive output
│   └── normalize output
│
├── 8. Artifact Capture
│   ├── store raw artifact
│   ├── create filtered artifact
│   ├── choose selected artifact
│   ├── mark authoritative artifact if any
│   └── write run/route/decision logs
│
├── 9. Validation / Review
│   ├── tool validation
│   ├── test / lint / build
│   ├── AI review if needed
│   ├── compare options if needed
│   └── accept / reject / revise
│
├── 10. Approval Gate
│   ├── user approval needed?
│   ├── escalation needed?
│   ├── second opinion needed?
│   └── record approval decision
│
├── 11. Handoff to Next Step
│   ├── inline context
│   ├── evidence bundle
│   ├── exchange bundle
│   └── manifest reference
│
└── 12. Finalization
    ├── finalize authoritative artifact
    ├── finalize summary
    ├── store final package
    ├── update run status
    └── close run or continue next step
```
