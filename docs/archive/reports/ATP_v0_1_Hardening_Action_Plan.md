# ATP v0.1 Hardening Action Plan

- **Ngày:** 2026-03-14
- **Phạm vi:** hardening repo-local ATP v0 theo freeze hiện hành
- **Mục tiêu:** siết semantic consistency, boundary clarity, và traceability của flow M1-M8

## Nguyên tắc ưu tiên

- Ưu tiên fix semantic drift đang tác động trực tiếp đến ATP v0 baseline
- Ưu tiên boundary clarity và test confidence hơn là refactor bề mặt
- Runtime materialization là phase sau; pass này không triển khai runtime materialization mới trừ khi cần cho một correction cực nhỏ và an toàn

## Immediate fixes

1. Đồng bộ vocabulary giữa approval, finalization, và handoff.
2. Siết semantics của `evidence_bundle` theo đúng continuity payload.
3. Làm rõ run-state trace qua `FINALIZED -> CLOSED/CONTINUE_PENDING`.
4. Chuẩn hóa runtime workspace path hint theo boundary chính thức.
5. Bổ sung targeted test cho các semantic zone yếu.

## Action plan

1. Đối chiếu implementation hiện tại với flow 14 bước và chốt các drift có tác động thực sự.
2. Sửa semantic mapping giữa approval, handoff, finalization, và close-run để vocabulary thống nhất.
3. Siết boundary runtime bằng cách tránh mọi runtime path hint mơ hồ trong repo.
4. Tăng test coverage tại các vùng yếu: execution failure normalization, finalization vocabulary, handoff continuity artifact, close-run behavior.
5. Ghi lại gap map và phần deferred để hardening tiếp theo không phải đoán lại.

## Đã thực hiện trong pass này

- Đồng bộ `final_status` cho handoff và finalization.
- Thu gọn `evidence_bundle` về selected continuity artifact đúng với ATP v0 semantics.
- Sắp lại run-state transition để finalization đứng trước close decision.
- Chuẩn hóa runtime path hint sang `SOURCE_DEV/workspace/...`.
- Bổ sung test cho failure normalization và finalization/handoff consistency.
- Cập nhật README mức module bị lệch thời điểm triển khai.

## Deferred items

- Chuẩn hóa thêm README mức module còn lại nếu cần một pass wording riêng.
- Xem xét schema-level validation runner cho preview outputs ở hardening pass kế tiếp.
- Review sâu hơn toàn bộ fixtures/examples nếu sau này schema contracts được siết chặt hơn.

## Cố ý deferred trong pass này

- Không thêm workspace materialization thật.
- Không thêm persistence-backed inspect hoặc schema validator mới.
- Không đổi cấu trúc module, registry, provider, adapter, hay flow orchestration.
- Không mở rộng sang remote execution behavior mới hoặc approval UI.

## Exit condition cho pass hardening này

- ATP vẫn nằm trong freeze boundary của v0.
- Flow M1-M8 dễ trace hơn qua code và test.
- Runtime boundary rõ hơn.
- Vocabulary giữa approval, finalization, handoff, và close-run không còn drift rõ ràng.

## Recommended next step

Sau hardening pass này, bước kế tiếp nên là một pass nhỏ tập trung vào schema-contract verification và wording cleanup còn deferred. Runtime materialization chỉ nên được bàn tới như một phase riêng, có decision rõ ràng, không gộp lẫn vào hardening v0.1 hiện tại.
