# ATP v1.1 — Merge Checklist (GSGR)

- **Ngày chuẩn bị:** 2026-04-04
- **Người review:** Mr. Thu (human approval bắt buộc)
- **Baseline stable:** `v1.0.4` trên `main`
- **Source branch đề xuất merge:** `fix/threaded-bridge-server`
- **Target:** `main` → tag `v1.1.0`

---

## Bối cảnh thực tế (đọc trước khi làm bất cứ thứ gì)

9 PRs được gọi trong `AI_NEXT_STEP.md` **không phải 9 branch độc lập song song**. Chúng được stacked thành một chuỗi linear:

```
main (v1.0.4)
  └─ codex/release-v1.1-execution   [89 commits — F-101→F-303 + docs v1.2/1.3/1.4]
       └─ feat/ollama-adapter        [+1 commit — Ollama adapter]
            └─ feat/wire-ollama-executor  [+1 — wire Ollama vào executor]
                 └─ feat/openclaw-atp-bridge  [+1 — OpenClaw→ATP bridge]
                      └─ feat/cloud-escalation-adapter  [+1 — Anthropic cloud]
                           └─ feat/bridge-server  [+2 — HTTP bridge server]
                                └─ feat/governance-hook  [+1 — aios-gate]
                                     └─ fix/threaded-bridge-server  [+1 — ThreadingHTTPServer fix]
```

**`fix/threaded-bridge-server` = nhánh đầy đủ nhất**, chứa tất cả 9 PRs (97 commits ahead of main).

Merge strategy đề xuất: **single merge từ `fix/threaded-bridge-server` → `main`**, vì đây là accumulated state cuối cùng đã qua test đầy đủ.

---

## GSGR Step 1 — G: CHECK (Kiểm tra trạng thái trước khi làm gì)

### 1.1 Xác nhận repo và branch

```bash
git rev-parse --show-toplevel
# Expected: .../SOURCE_DEV/platforms/ATP

git branch --show-current
# Expected: fix/threaded-bridge-server (source)

git remote -v
# Expected: origin = đúng remote ATP
```

### 1.2 Kiểm tra working tree sạch

```bash
git status
# Expected: "nothing to commit" (không có untracked/modified)
# ⚠️ Hiện tại có 1 untracked file: docs/architecture/ATP_Design_System_Audit.md
# → Quyết định: commit file này vào branch trước khi merge, HOẶC bỏ qua (nó nằm ngoài scope v1.1)
```

### 1.3 Fetch remote

```bash
git fetch origin
git log --oneline origin/main..main
# Expected: empty (main local = main remote)
```

### 1.4 Xem diff tổng thể trước khi merge

```bash
git diff --stat main..fix/threaded-bridge-server
# Expected: 107 files changed, ~15783 insertions(+), 13 deletions(-)
```

**STOP nếu:** diff khác xa con số trên → có gì đó thay đổi ngoài dự kiến.

---

## GSGR Step 2 — S: SCAN (Rà soát nội dung thay đổi)

### 2.1 Danh sách thay đổi theo nhóm

| Nhóm | Files | Nội dung |
|---|---|---|
| `adapters/ollama/` | 4 files | Ollama adapter + tests (qwen3:14b, qwen3:8b, deepseek-r1:8b) |
| `adapters/cloud/` | 4 files | Anthropic cloud escalation adapter + tests |
| `bridge/` | 3 files | HTTP bridge server + OpenClaw bridge + governance hook |
| `cli/` | ~10 files | CLI commands (compose-chain, execution-session, inspect, ...) |
| `core/` | ~15 files | Core modules F-101→F-303 |
| `docs/` | ~40 files | Architecture, governance, roadmap, execution docs |
| `tests/` | ~20 files | Unit + integration tests |
| `registry/` | ~5 files | Registry additions |
| `schemas/` | ~5 files | Schema additions |
| `atp` | 1 file | CLI entrypoint symlink |

### 2.2 Xác nhận các file quan trọng không bị xâm phạm

```bash
git diff main..fix/threaded-bridge-server -- core/state/run_state.py
git diff main..fix/threaded-bridge-server -- AGENTS.md
git diff main..fix/threaded-bridge-server -- docs/architecture/ATP_MVP_v0_Freeze_Decision_Record.md
# Expected: ít hoặc không có thay đổi ở các frozen core files
```

### 2.3 Xác nhận không có runtime artifacts trong diff

```bash
git diff --name-only main..fix/threaded-bridge-server | grep -E "\.log$|\.jsonl$|/workspace/|/runs/"
# Expected: empty — không có runtime artifacts lọt vào repo
```

---

## GSGR Step 3 — G: GATE (Validation gates trước merge)

### 3.1 Compile check

```bash
python3 -m compileall adapters core cli bridge tests
# Expected: không có SyntaxError
```

### 3.2 Full test suite

```bash
make test
# Expected:
# Ran 284 unit tests — OK
# Ran 28 integration tests — OK (6 skipped là bình thường)
```

**Test kết quả đã xác nhận (2026-04-04, trên `fix/threaded-bridge-server`):**
- ✅ 284 unit tests — PASS
- ✅ 28 integration tests — PASS (6 skipped)
- ✅ 11 Ollama adapter tests — PASS
- ✅ 9 Anthropic adapter tests — PASS
- ✅ Compile clean — không có error

### 3.3 Smoke check nhanh

```bash
make smoke
# Expected: ATP M1-M2 smoke flow pass
```

### 3.4 Kiểm tra bridge server import (không cần chạy)

```bash
python3 -c "from bridge.bridge_server import ATPBridgeHandler; print('bridge OK')"
python3 -c "from adapters.ollama.ollama_adapter import OllamaAdapter; print('ollama OK')"
python3 -c "from adapters.cloud.anthropic_adapter import AnthropicAdapter; print('cloud OK')"
# Expected: mỗi lệnh in OK, không có ImportError
```

**STOP nếu:** bất kỳ test nào fail → không merge. Fix trên branch trước.

---

## ⛔ APPROVAL GATE — Phải dừng tại đây

Tất cả bước dưới đây **bắt buộc có human approval trước khi thực hiện**.

AI không được tự thực thi các lệnh trong Bước 4, 5, 6, 7.

---

## GSGR Step 4 — R: REVIEW SUMMARY (Tóm tắt để human duyệt)

### Merge summary

| Mục | Thông tin |
|---|---|
| Source branch | `fix/threaded-bridge-server` |
| Target | `main` |
| Commits ahead of main | 97 commits |
| Files changed | 107 files |
| Insertions | ~15,783 |
| Deletions | ~13 |
| Tests | 312/312 PASS |
| Compile | CLEAN |

### Nội dung chính của v1.1

**Execution chain (codex/release-v1.1-execution — 89 commits):**
- F-101: bounded multi-request flow
- F-102: execution session tracking
- F-103: operator readability
- F-104: control-plane hardening
- F-105: integration readiness
- F-201: artifact export
- F-202: CLI composition (compose-chain)
- F-203: session-artifact continuity
- F-204: integration contract projection
- F-205: deployability readiness
- F-301: operator review summary
- F-302: handoff planning consolidation
- F-303: reviewability posture guard
- v1.2/1.3/1.4 docs + close-out artifacts

**Adapters và bridge (8 commits mới):**
- Ollama adapter (qwen3:14b, qwen3:8b, deepseek-r1:8b)
- Anthropic cloud escalation adapter
- OpenClaw → ATP bridge
- HTTP bridge server (localhost:8765)
- AI_OS governance gate hook (aios-gate)
- ThreadingHTTPServer fix (concurrent request handling)

### Rủi ro cần xem xét

| Rủi ro | Mức độ | Ghi chú |
|---|---|---|
| Untracked file `ATP_Design_System_Audit.md` trong working tree | Thấp | Cần quyết định: commit vào branch hoặc bỏ qua |
| Bridge server không có unit test riêng trong `tests/unit/` | Trung bình | Tests nằm ở `adapters/ollama/test_*.py` và `adapters/cloud/test_*.py`, không trong standard test dir |
| `AI_PROJECT_CONTEXT.md` bị stale (vẫn ghi "non-provider-abstracted") | Thấp | Cần update sau merge hoặc trước merge |
| 97 commits lớn → khó revert từng PR riêng sau khi merge | Trung bình | Cân nhắc xem có cần giữ feature branches lại sau merge không |

---

## GSGR Step 5 — Merge (chỉ thực hiện sau khi human APPROVE)

```bash
# Switch về main
git checkout main
git pull origin main
git log --oneline -5
# Xác nhận: HEAD tại v1.0.4 (146a02e)

# Merge với no-ff để giữ history rõ
git merge --no-ff fix/threaded-bridge-server -m "merge: ATP v1.1.0 — Ollama adapter + cloud escalation + bridge server + governance gate"

# Verify ngay sau merge
git status
python3 -m compileall adapters core cli bridge tests
make test
```

---

## GSGR Step 6 — Tag (chỉ sau khi merge thành công và test xanh)

```bash
git tag v1.1.0
git show v1.1.0 --stat | head -20
# Xác nhận tag đúng commit
```

---

## GSGR Step 7 — Push (chỉ sau khi tag đúng, human confirm)

```bash
git push origin main
git push origin v1.1.0
# Verify
git log --oneline --decorate -5
```

---

## GSGR Step 8 — Post-merge cleanup

Sau khi merge, tag, push thành công:

```bash
# Cập nhật AI_OS context files
# AI_CURRENT_BASELINE.md → version: v1.1.0
# AI_HANDOFF_LATEST.md → update lineage
# AI_PROJECT_CONTEXT.md → sửa "non-provider-abstracted" → phản ánh Ollama + cloud adapter

# Xem có cần xóa feature branches không (sau khi confirm không cần rollback)
git branch -d feat/ollama-adapter feat/wire-ollama-executor feat/openclaw-atp-bridge
git branch -d feat/cloud-escalation-adapter feat/bridge-server feat/governance-hook
git branch -d fix/threaded-bridge-server
# ⚠️ Chỉ xóa sau khi main+v1.1.0 đã push thành công và xác nhận stable
```

---

## Checklist tổng hợp — Human sign-off

```
PRE-MERGE CHECKS (AI đã hoàn thành):
[ ] Compile: PASS (đã xác nhận 2026-04-04)
[ ] 284 unit tests: PASS
[ ] 28 integration tests: PASS
[ ] 11 Ollama tests: PASS
[ ] 9 Anthropic tests: PASS
[ ] Diff review: 107 files, nội dung đúng scope
[ ] Không có runtime artifacts trong diff

HUMAN APPROVAL (bắt buộc):
[ ] Human đã đọc merge summary ở Bước 4
[ ] Human đã quyết định về untracked file ATP_Design_System_Audit.md
[ ] Human đã quyết định về stale AI_PROJECT_CONTEXT.md
[ ] Human APPROVE merge fix/threaded-bridge-server → main
[ ] Human APPROVE tag v1.1.0
[ ] Human APPROVE push origin main
[ ] Human APPROVE push origin v1.1.0

POST-MERGE:
[ ] merge thực hiện với --no-ff
[ ] test pass sau merge
[ ] tag v1.1.0 tạo đúng
[ ] push main thành công
[ ] push tag thành công
[ ] AI_OS context files (baseline, handoff, project context) đã update
[ ] Feature branches đã cleanup (nếu quyết định xóa)
```

---

## Lệnh AI có thể chạy ngay (không cần approval)

Các lệnh read-only để xác nhận trạng thái — AI có thể chạy bất cứ lúc nào:

```bash
# Xác nhận test xanh trên source branch
git checkout fix/threaded-bridge-server
make test

# Xem diff summary
git diff --stat main..fix/threaded-bridge-server

# Xem commit log đầy đủ
git log --oneline main..fix/threaded-bridge-server

# Kiểm tra không có conflict ẩn
git merge-tree $(git merge-base main fix/threaded-bridge-server) main fix/threaded-bridge-server | grep -c "^conflict" || echo "0 conflicts detected"
```

---

*Checklist này chuẩn bị theo Git Safety Charter + Safe Git Workflow Templates + Release Governance Bundle của ATP.*
*Mọi action từ Bước 5 trở đi: HUMAN APPROVAL BẮT BUỘC.*
