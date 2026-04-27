---
id: atp-14-step
group: runbook
title: 14-step transformation flow
status: ok
since: v2.0.0
readingTime: 8
order: 1
lede: "Mỗi request qua ATP trải qua 14 bước. Hiểu sơ bộ giúp đọc trace + debug nhanh khi run fail."
---

## 14 step tổng quan

| # | Step | Mục đích |
|---|---|---|
| 1 | resolve-route | Chọn provider (Ollama/Claude/GPT) theo policy |
| 2 | resolve-role | Áp prompt template theo role (executor/reviewer/...) |
| 3 | retrieve-context | Query AOKP cho top-K evidence |
| 4 | build-system-prompt | Compose system prompt với context |
| 5 | build-user-prompt | Format user message |
| 6 | preflight-validate | Schema check input |
| 7 | call-inference | Gọi LLM endpoint |
| 8 | parse-response | Extract structured fields |
| 9 | postflight-validate | Schema check output |
| 10 | extract-citations | Match output với source evidence |
| 11 | governance-gate | Compliance check (PII, scope) |
| 12 | persist-run | Lưu run record + traces |
| 13 | emit-events | Push events cho subscribers |
| 14 | format-response | Final shape cho client |

## Khi run fail, đọc trace ở step nào?

:::Steps
1. **Mở AIOS-OC → tab Workspace → ATP → Runs** — Liệt kê các run gần đây với status (done/failed).

2. **Click vào run failed** — Mở detail panel với 14 step traces.

3. **Tìm step `failed`** — Step đầu tiên có status `failed` là nguyên nhân. Các step sau bị skip.

4. **Đọc error message + payload** — Mỗi step có `input`, `output`, `error`. Copy error → search trong Help (FAQ dưới đây).
:::

## FAQ

:::FAQ
### Step `retrieve-context` fail với "AOKP unreachable"?
AOKP service :3002 down. Trong AIOS-OC StatusBar check đèn AOKP. Nếu đỏ → start AOKP: `pnpm dev` trong AOKP repo.

### Step `call-inference` fail với "model timeout"?
LLM call quá 30s. Nguyên nhân thường gặp: Ollama cold-start lần đầu (model lớn), hoặc network sang cloud API chậm. Retry là cách đơn giản nhất.

### Step `postflight-validate` fail với "schema mismatch"?
LLM trả output không match schema mong muốn. Có thể do prompt không rõ, hoặc model nhỏ "ngẫu hứng". Đổi sang model mạnh hơn (Claude/GPT) qua Route dropdown.

### Step `governance-gate` fail với "PII detected"?
Output chứa data nhạy cảm (số CMND, SĐT, email cá nhân). ATP block để bảo vệ. Nếu legitimate → whitelist scope trong governance config.
:::
