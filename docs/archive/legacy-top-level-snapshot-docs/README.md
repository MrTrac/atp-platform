# Legacy Top-Level Snapshot Docs

- **Trạng thái:** Archived. Không phải active authority path.
- **Mục đích:** Lưu bản sao lịch sử của các snapshot bundle từng đặt sai hoặc cũ ở top-level trong `docs/`.

## Nội dung

Thư mục này chứa **bản sao lịch sử** của các snapshot bundle trước đây nằm sai vị trí (top-level hoặc placement cũ). Thư mục được giữ lại chỉ để traceability và so sánh lịch sử, không dùng làm nguồn chuẩn.

## Nguồn chuẩn hiện tại

Các snapshot bundle authoritative hiện nằm dưới:

```text
docs/architecture/
```

- `ATP_v0_final_snapshot_docs/` — baseline MVP v0
- `ATP_v0_1_hardening_snapshot_docs/` — hardening v0.1

## Quy tắc

- **Không** dùng tài liệu trong thư mục này làm authority hiện hành.
- **Luôn** tham chiếu tới `docs/architecture/` khi cần snapshot baseline hoặc hardening.
- Thư mục này chỉ phục vụ traceability và so sánh lịch sử.
