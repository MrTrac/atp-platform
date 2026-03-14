# ATP Version Lineage & Documentation Continuity Rule

## Mục đích

Thiết lập một ATP governance rule bắt buộc để mọi version hoặc phase đều có:

- lineage rõ ràng
- documentation continuity rõ ràng
- authority path rõ ràng
- freeze hoặc close-out status rõ ràng khi milestone đã đi tới freeze boundary

Rule này tồn tại để ngăn việc coi branch, code, hoặc commit là đủ để đại diện cho một milestone đã hoàn chỉnh về mặt tài liệu.

## Phạm vi áp dụng

Áp dụng cho:

- mọi ATP version theo dạng `vX.Y`
- mọi frozen version theo dạng `vX.Y.Z`
- mọi planning phase, implementation phase, consolidation phase, và freeze phase có ý nghĩa quản trị
- mọi backfill tài liệu hồi tố cho các milestone cũ

## Vấn đề rule này giải quyết

ATP đã có practical evolution từ `v0.1` tới `v0.5`, nhưng continuity có thể bị rời rạc nếu:

- branch tồn tại nhưng không có authority path rõ
- code hoặc commit tồn tại nhưng không có lineage docs rõ
- freeze status hoặc close-out status không được ghi nhận nhất quán
- older milestones thiếu continuity docs nhưng không được backfill

Rule này buộc ATP phải giữ continuity như một phần của governance, không phải như ghi chú tùy chọn.

## Quy tắc bắt buộc

1. Mọi ATP version hoặc phase phải có explicit lineage.
2. Mọi ATP version hoặc phase phải có explicit documentation continuity.
3. Branch existence một mình không đủ để coi một milestone là established.
4. Code hoặc commit existence một mình không đủ để coi một milestone là documentation-complete.
5. Một version hoặc phase chỉ được coi là documentation-complete khi có:
   - authority path rõ
   - status rõ
   - freeze hoặc close-out status phù hợp với maturity của milestone
6. Missing continuity docs của các milestone cũ phải được backfill khi gap đã được xác định.
7. Khi có lineage-affecting change, các README/index docs ở level bị ảnh hưởng phải được review và cập nhật nếu cần.
8. Nếu evidence không đủ chắc, tài liệu phải ghi rõ `inferred`, `provisional`, hoặc `needs confirmation`.
9. Không được trình bày suy luận lịch sử như fact đã xác nhận.

## Metadata bắt buộc cho mỗi version/phase

Mỗi version hoặc phase phải có tối thiểu metadata sau, theo mức evidence hiện có:

- version hoặc phase name
- mục tiêu
- in-scope
- out-of-scope
- branch nếu biết hoặc recoverable
- trạng thái
- authoritative docs
- key commits hoặc implementation anchor nếu biết
- freeze hoặc close-out status
- predecessor relation nếu biết
- successor relation nếu biết

Nếu một field chưa prove được chắc chắn, phải gắn rõ:

- `inferred`
- `provisional`
- `needs confirmation`

## Bộ tài liệu tối thiểu cho mỗi version/phase

### Full form

Với một version hoặc phase đủ lớn, bộ tài liệu tối thiểu gồm:

- Proposal / Stage Intent
- Execution Plan
- Freeze Decision Record
- Close-out / Freeze Summary

### Yêu cầu áp dụng

- planning hoặc opening phase phải có ít nhất Proposal / Stage Intent và Execution Plan
- freeze-capable milestone phải có Freeze Decision Record và Close-out / Freeze Summary
- practical milestone map phải có entry tương ứng cho milestone đó

## Hình thức gộp cho phase nhỏ

Phase nhỏ được phép dùng compact form khi:

- scope hẹp
- không phải frozen release đầy đủ
- continuity vẫn đọc được rõ từ authority docs hiện có

Compact form được phép:

- gộp Proposal + Plan
- gộp Freeze + Close-out

Compact form không được dùng để bỏ qua freeze/close-out continuity của một version đã freeze.

## Quy tắc backfill hồi tố

1. Milestone cũ thiếu continuity docs phải được backfill khi gap đã được xác nhận.
2. Backfill phải dựa trên repo evidence hiện có:
   - active docs
   - archived reports
   - freeze close-out docs
   - git tags
   - merge history
   - branch evidence nếu recoverable
3. Nếu evidence chưa đủ, phải đánh dấu field là `inferred`, `provisional`, hoặc `needs confirmation`.
4. Backfill không được rewrite frozen history; nó chỉ chuẩn hóa authority path và continuity.

## Quan hệ với roadmap/stage docs

- Rule này là governance rule authoritative cho lineage và documentation continuity.
- `docs/roadmap/stages/ATP_Practical_Milestone_Map.md` là operational application của rule này.
- `docs/roadmap/stages/ATP_Development_Stage_Roadmap.md` mô tả capability stages, không thay practical milestone map trong việc theo dõi lineage cụ thể.

Nói ngắn gọn:

- rule này định nghĩa yêu cầu bắt buộc
- practical milestone map theo dõi continuity vận hành
- stage roadmap theo dõi maturity horizon

## Tài liệu liên quan / nguồn chuẩn liên quan

- `docs/governance/ATP_Development_Ruleset.md`
- `docs/README.md`
- `docs/roadmap/README.md`
- `docs/roadmap/stages/ATP_Practical_Milestone_Map.md`
- `docs/roadmap/stages/ATP_Development_Stage_Roadmap.md`
- `docs/archive/reports/ATP_v0_2_0_Freeze_Closeout.md`
- `docs/archive/reports/ATP_v0_3_0_Freeze_Closeout.md`
- `docs/archive/reports/ATP_v0_4_0_Freeze_Closeout.md`
