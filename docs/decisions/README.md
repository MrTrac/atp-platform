# Chỉ mục decisions

- **Mục đích:** Chỉ mục decision records; authority path tới freeze và hardening snapshot.
- **Phạm vi:** Baseline freeze, hardening snapshot, mở rộng tương lai.
- **Trạng thái:** Active.

## Authority path

Decision artifact authoritative hiện nằm dưới `docs/architecture/`, không nằm trong `docs/decisions/`.

## Chỉ mục nhanh

| Loại | Path | Ghi chú |
|------|------|---------|
| **Baseline freeze** | `architecture/ATP_MVP_v0_Freeze_Decision_Record.md` | Freeze MVP v0; baseline kiến trúc |
| **Hardening snapshot** | `architecture/ATP_v0_1_hardening_snapshot_docs/ATP_v0_1_Hardening_Freeze_Decision_Record.md` | Freeze v0.1 hardening; không mở rộng scope |
| **Implementation plan** | `architecture/ATP_v0_final_snapshot_docs/`, `ATP_v0_1_hardening_snapshot_docs/` | Plan và runbook trong snapshot bundle |

## Thêm decision record mới

- Decision mới nên đặt dưới `docs/architecture/` theo domain hoặc release track, hoặc trong snapshot bundle tương ứng.
- Không tạo authority path song song với `docs/architecture/` nếu chưa có quyết định rõ ràng.
- Khi số lượng tăng, mở rộng bảng chỉ mục trên theo domain hoặc timeline.
