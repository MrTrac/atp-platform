# Boundary repo của ATP

ATP là một `standalone platform repo` tại:

```text
SOURCE_DEV/platforms/ATP
```

## Boundary authoritative

ATP phải luôn được hiểu với ba vùng tách biệt:

- `SOURCE_DEV/platforms/ATP` - source repo của ATP
- `SOURCE_DEV/products/TDF` - product repo riêng, không phải repo root của ATP
- `SOURCE_DEV/workspace` - runtime workspace zone, không phải coding root của ATP

## Nguyên tắc boundary đang có hiệu lực

- Không coi `SOURCE_DEV/` là monorepo coding root của ATP
- Không lưu runtime artifact chính thức trong repo ATP
- Không trộn vai trò giữa source repo, product repo, và workspace runtime zone
- Mọi handoff sang runtime zone phải giữ authority rõ ràng về source và artifact

## Phạm vi product resolution tối thiểu của ATP v0

ATP v0 hiện hỗ trợ product resolution tối thiểu cho:

- `ATP`
- `TDF`

## Quy tắc thay đổi boundary

Mọi thay đổi liên quan đến boundary repo, boundary workspace, hoặc boundary kiến trúc phải được chốt bằng decision artifact phù hợp trước khi áp dụng vào repo.
