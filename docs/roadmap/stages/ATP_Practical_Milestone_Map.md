# ATP Practical Milestone Map

## Mục đích

Đây là lineage map vận hành của ATP từ `v0.1` tới `v0.5`.

Tài liệu này dùng để theo dõi:

- milestone nào đã được xác nhận rõ
- milestone nào mới có evidence một phần
- milestone nào còn continuity gap
- milestone nào đã freeze
- milestone nào đang ở active planning hoặc active implementation

Tài liệu này là lớp áp dụng thực tế của rule:

- `docs/governance/framework/ATP_Version_Lineage_and_Documentation_Continuity_Rule.md`

Nó không thay thế:

- architecture doctrine
- stage roadmap
- version roadmap
- freeze close-out reports

## Cách đọc tài liệu này

Mỗi milestone được đọc theo các trường:

- mục tiêu hoặc objective
- branch hoặc branch status nếu biết
- implementation status
- documentation status
- authoritative docs hiện biết
- continuity gaps
- freeze / close-out status
- notes / caveats

Nếu một field chưa chắc chắn, field đó phải được ghi rõ là:

- `inferred`
- `provisional`
- `needs confirmation`

## Quy ước trạng thái

- `documented`: milestone đã có authority path và continuity tương đối rõ
- `partial`: milestone có một phần docs nhưng continuity chưa đầy đủ
- `inferred`: có thể recover từ repo evidence, nhưng chưa có document chain hoàn toàn explicit
- `gap`: đã xác định còn thiếu continuity docs
- `frozen`: milestone đã freeze/tag và có freeze status rõ
- `active planning`: milestone đang ở planning phase active

## Bản đồ milestone thực dụng từ v0.1 đến v0.5

| Milestone | Mục tiêu / objective | Branch / branch status | Trạng thái implementation / documentation | Authority docs hiện biết | Missing docs / continuity gaps | Freeze / close-out status | Ghi chú |
|---|---|---|---|---|---|---|---|
| `v0.1` | Hardening baseline đầu tiên cho ATP v0 shape-correct MVP | Branch: `needs confirmation`; tags `v0.1.0`, `v0.1.0-mvp` có trong repo | Implementation: `partial`, `inferred`; Documentation: `partial`, `gap` | `docs/architecture/ATP_v0_1_hardening_snapshot_docs/`, tag evidence, hardening snapshot commits | Chưa có formal close-out theo format hiện hành; branch lineage cần confirmation | Tag có; close-out: `gap` | Mốc này có continuity gap lớn nhất trong chain hiện tại |
| `v0.2` | Consolidated runtime materialization baseline | Branch lineage `inferred`: `v0.2-slice4-retention-cleanup` là integration branch recoverable từ git history | Implementation: `documented`; Documentation: `documented` | `docs/archive/reports/ATP_v0_2_Integration_Review.md`, `docs/archive/reports/ATP_v0_2_Consolidation_Decision.md`, `docs/archive/reports/ATP_v0_2_0_Freeze_Closeout.md` | Không thấy continuity gap lớn đã xác nhận | Freeze/tag rõ: `v0.2.0`; close-out: `documented` | Merge commit và freeze date đã được recover trong close-out |
| `v0.3` | External boundary / continuation / reference completion baseline | Branch lineage `inferred`: `v0.3-planning` | Implementation: `documented`; Documentation: `documented` | `docs/archive/reports/ATP_v0_3_Integration_Review.md`, `docs/archive/reports/ATP_v0_3_Consolidation_Decision.md`, `docs/archive/reports/ATP_v0_3_0_Freeze_Closeout.md` | Không thấy continuity gap lớn đã xác nhận | Freeze/tag rõ: `v0.3.0`; close-out: `documented` | Historical continuity chain tương đối sạch |
| `v0.4` | Current-task persistence / recovery entry / pointer / inspect hardening | Branch lineage `inferred`: `v0.4-planning` | Implementation: `documented`; Documentation: `documented` | `docs/archive/reports/ATP_v0_4_Integration_Review.md`, `docs/archive/reports/ATP_v0_4_Consolidation_Decision.md`, `docs/archive/reports/ATP_v0_4_0_Freeze_Closeout.md` | Không thấy continuity gap lớn đã xác nhận | Freeze/tag rõ: `v0.4.0`; close-out: `documented` | Close-out đã được backfill từ repo evidence |
| `v0.5` | Hoàn tất lớp continuity thực dụng của `v0` major family theo trục `requested user ⇄ ATP ⇄ products` | Branch active: `v0.5-planning` | Implementation: `active planning`; Documentation: `partial` | `docs/roadmap/versions/ATP_v0_5_Roadmap.md`, `docs/roadmap/stages/ATP_Development_Stage_Roadmap.md`, `docs/governance/ATP_Development_Ruleset.md` | Chưa có integration review, consolidation decision, freeze close-out vì milestone chưa freeze | Freeze: `active planning`; close-out: `not applicable yet` | Runtime work trên branch là active evidence, không phải frozen fact |

## Documentation gaps hiện đã xác định

1. `v0.1` chưa có formal freeze close-out document theo format đang áp dụng từ `v0.2+`.
2. Branch lineage của `v0.1` chưa thể ghi như fact tuyệt đối từ active docs hiện có.
3. Một số milestone rất sớm của ATP có evidence phân tán hơn các mốc `v0.2+`, nên cần backfill cẩn trọng nếu muốn chain hoàn chỉnh hơn.

## Thứ tự backfill khuyến nghị

1. Backfill formal freeze close-out cho `v0.1.0` nếu repo evidence đủ.
2. Nếu recover được chắc hơn, chuẩn hóa branch / integration note cho `v0.1`.
3. Giữ cập nhật map này cùng lúc khi `v0.5` tiến tới integration review, consolidation, freeze, và close-out.

## Tài liệu liên quan / nguồn chuẩn liên quan

- `docs/governance/framework/ATP_Version_Lineage_and_Documentation_Continuity_Rule.md`
- `docs/governance/ATP_Development_Ruleset.md`
- `docs/roadmap/stages/ATP_Development_Stage_Roadmap.md`
- `docs/roadmap/versions/ATP_v0_5_Roadmap.md`
- `docs/archive/reports/ATP_v0_2_0_Freeze_Closeout.md`
- `docs/archive/reports/ATP_v0_3_0_Freeze_Closeout.md`
- `docs/archive/reports/ATP_v0_4_0_Freeze_Closeout.md`
