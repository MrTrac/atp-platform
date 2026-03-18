# Checklist 5 bước — Đóng phase / Đổi baseline (ATP ↔ AI_OS sync)

## 1. Chốt baseline trong ATP

1. Đảm bảo code/docs/tests trên branch target (thường `main` hoặc branch release) sạch và pass.
2. Commit + (nếu cần) tag baseline bằng `gsgr`:
   - `gsgr commit <branch> "..." <files...>`
   - `gsgr --yes tag <version> "..."` (nếu baseline kèm release tag).
3. Đảm bảo `git status` sạch và remote đã cập nhật: `gsgr push <branch>`.

---

## 2. Ghi nhận baseline và phase mới trong AI_OS

Trong `~/AI_OS/20_PROJECTS/ATP/`:

1. Cập nhật `AI_CURRENT_BASELINE.md` với version/tag/commit, branch, phase (vd. `v1.0.4`, Slice E Closed).
2. Nếu cần, cập nhật `AI_PROJECT_CONTEXT.md` cho phù hợp với lineage mới.
3. Cập nhật `AI_NEXT_STEP.md` để ghi rõ phase tiếp theo và task đầu tiên.

---

## 3. Cập nhật handoff mới nhất (AI_HANDOFF_LATEST.md)

1. Mở `AI_HANDOFF_LATEST.md` trong `~/AI_OS/20_PROJECTS/ATP/`.
2. Ghi Handoff block mới (baseline, phase, scope in/out, open gates, context files).
3. Đảm bảo wording ở đây khớp với `AI_CURRENT_BASELINE.md`, `AI_PROJECT_CONTEXT.md`, `AI_NEXT_STEP.md`.

---

## 4. Đồng bộ bridge trong ATP (nếu cần)

Trong repo ATP (`/Users/nguyenthanhthu/SOURCE_DEV/platforms/ATP`):

1. Kiểm tra `AI_OS_CONTEXT.md`, `.cursorrules`, `AGENTS.md`, `CLAUDE.md` — chỉ sửa nếu có text hard-code baseline/phase bị lệch.
2. Nếu có thay đổi, dùng `gsgr commit` để ghi lại:
   - `gsgr commit main "chore: align AI_OS bridges for <phase/baseline>" <files...>`

---

## 5. Cross-check sync ATP ↔ AI_OS

1. Từ AI_OS:
   - Đọc `AI_CURRENT_BASELINE.md`, `AI_NEXT_STEP.md`, `AI_HANDOFF_LATEST.md`.
2. Từ ATP:
   - Kiểm tra `git log`/tag trên branch baseline; đọc các freeze close-out / integration review liên quan.
3. Nếu có lệch, không đoán: sửa AI_OS *hoặc* ATP (nhỏ nhất có thể) cho tới khi baseline, phase, next step và handoff khớp hoàn toàn.
