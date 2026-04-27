---
id: atp-what-is
group: overview
title: ATP là gì?
status: ok
since: v2.0.0
readingTime: 4
order: 1
lede: "**ATP** (Autonomous Task Platform) là Transformation plane của AI_OS — service chuẩn hóa mọi request qua 14 bước (context → prompt → inference → validation → governance) trên port `:8765`."
---

## Khi nào ATP chạy?

ATP không phải app người dùng mở trực tiếp. Mỗi câu hỏi từ AIOS-OC, mỗi flow
trong aios-flow đều đi qua ATP để được:
- Lấy thêm context từ AOKP
- Build prompt theo role/policy
- Gọi inference (Ollama / Claude / GPT)
- Validate output
- Áp governance (xác nhận compliance)

::::WhatGrid
:::WhatCard{tone="info" icon="🔌" label="Bridge mode"}
**HTTP REST** — Endpoint `/api/atp/run` chấp nhận request, trả response. Dùng cho synchronous flow.
:::

:::WhatCard{tone="accent" icon="🤖" label="Agent mode"}
**CLI subprocess** — Chạy local agent (claude/codex/cursor) qua adapter. Dùng cho long-running flow.
:::

:::WhatCard{tone="violet" icon="📊" label="Observability"}
**Run history** — Mỗi request lưu thành 1 run với 14 step traces. Quan sát qua AIOS-OC tab Workspace → ATP.
:::
::::

## Sub-app này phục vụ cái gì?

Help port `:8766` là Next.js sub-app riêng — **không** ảnh hưởng FastAPI bridge `:8765`.
Người vận hành click nút **Help** trong Web UI ATP → mở sub-app này. Bridge production
giữ nguyên port + traffic, sub-app help isolated.
