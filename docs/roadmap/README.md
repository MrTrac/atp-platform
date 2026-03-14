# Roadmap ATP

- **Mục đích:** Lớp roadmap active cho ATP; cung cấp development guidance forward-looking giữa product direction, major family, version planning, consolidation, freeze, và close-out.
- **Phạm vi:** Product roadmap, major roadmap, version roadmap, và inheritance rules.
  Bao gồm cả stage-based roadmap để mô tả ATP theo các maturity stages thực dụng.
- **Trạng thái:** Active.

## Roadmap dùng để làm gì

Roadmap của ATP là một forward-looking development map.

Roadmap không chủ yếu dùng để kể lại những gì đã hoàn tất. Lịch sử frozen chỉ được dùng như evidence và inheritance baseline để định hướng bước tiếp theo.

Roadmap của ATP cũng không phải feature wishlist. ATP dùng roadmap để mô tả capability horizons, governance gates, và logic chuyển tiếp giữa các maturity steps.

Roadmap của ATP phải luôn quay lại operating axis cốt lõi:

`requested user ⇄ ATP ⇄ products`

Nếu một capability horizon không làm mạnh hơn trục này, nó không nên được đưa vào roadmap chỉ vì implementation convenience.

## Phân lớp tài liệu

ATP tách rõ bốn lớp:

- **Architecture specification** — doctrine, stable core, modular boundaries, extension seams, và fitness rules
- **Roadmap guidance** — capability horizons và transition logic cho tương lai
- **Version execution planning** — goal, scope, slices, freeze criteria, và integration criteria cho từng version
- **Freeze close-out / history** — factual record của các version đã freeze

Roadmap phải kế thừa từ architecture doctrine, không được override architecture chỉ vì implementation convenience.

Operational rules và gates để thi hành doctrine/roadmap không nằm trong cây này; chúng thuộc `docs/governance/ATP_Development_Ruleset.md`.

Version lineage và documentation continuity rule cũng không nằm trong cây này; rule authoritative tương ứng nằm tại:

- `docs/governance/framework/ATP_Version_Lineage_and_Documentation_Continuity_Rule.md`

## Roadmap layering

ATP dùng roadmap 3 tầng:

- **Product roadmap** — mô tả strategic horizons dài hạn của ATP
- **Major roadmap** — mô tả capability horizon của một major family như `v0`, `v1`, `v2`
- **Version roadmap** — mô tả execution horizon cụ thể mà một version cần unlock cho major family hiện tại

Bổ sung một lớp practical mapping:

- **Stage roadmap** — mô tả ATP có hình hài gì, làm được gì, chưa làm được gì ở từng development stage

## Quy tắc inheritance

Mỗi version roadmap mới phải kế thừa từ:

- previous frozen version
- consolidation baseline của version trước đó
- freeze close-out của version trước đó khi đã tồn tại
- major roadmap và product roadmap đang active

## Quy tắc governance

Roadmap không phải optional writing. Trong ATP:

- mỗi version phải có planning baseline
- implementation không nên đi trước planning baseline acceptance
- freeze không nên diễn ra nếu chưa có consolidation decision
- sau mỗi version đã freeze, formal freeze close-out là bắt buộc
- roadmap continuity là một phần của release/documentation governance
- roadmap phải dùng capability horizons và governance gates, không được drift thành ad hoc feature expansion

## Tài liệu trong miền

- `ATP_Product_Roadmap.md` — product-level direction và capability horizon logic
- `stages/` — stage-based roadmap cho ATP theo practical development stages
- `stages/ATP_Practical_Milestone_Map.md` — practical lineage map cho continuity từ `v0.1` tới milestone hiện tại
- `templates/milestones/` — template bundle cho Proposal, Execution Plan, Freeze Decision Record, và Closeout của từng milestone
- `milestones/` — milestone documentation backfill cho từng version trong ATP v0 family (`v0.2` → `v0.5`)
- `majors/` — roadmap cho từng major family
- `versions/` — roadmap cho từng version cụ thể
