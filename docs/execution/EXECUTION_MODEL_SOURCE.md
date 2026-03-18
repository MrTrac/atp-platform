# Execution Model Source — ATP

- **Project:** ATP
- **Repo:** `/Users/nguyenthanhthu/SOURCE_DEV/platforms/ATP`
- **Execution-plan instance location:** `docs/execution/`
- **Canonical model source:** `/Users/nguyenthanhthu/AI_OS/15_EXECUTION_MODEL`
- **Last updated:** 2026-03-18

## Mục đích
File này ghi rõ nguồn gốc canonical của execution-plan artifacts trong ATP để tránh đảo authority giữa AI_OS và project repo.

## Source mapping

### Canonical layer ở AI_OS
ATP execution-plan layer này được instantiate từ:
- `/Users/nguyenthanhthu/AI_OS/15_EXECUTION_MODEL/README.md`
- `/Users/nguyenthanhthu/AI_OS/15_EXECUTION_MODEL/EXECUTION_MODEL_GOVERNANCE.md`
- `/Users/nguyenthanhthu/AI_OS/15_EXECUTION_MODEL/PR_CMD_MODEL.md`
- `/Users/nguyenthanhthu/AI_OS/15_EXECUTION_MODEL/ROADMAP_EXECUTION_TEMPLATE.md`
- `/Users/nguyenthanhthu/AI_OS/15_EXECUTION_MODEL/PROMPT_CMD_INDEX_TEMPLATE.md`
- `/Users/nguyenthanhthu/AI_OS/15_EXECUTION_MODEL/PROMPT_CMD_FEATURE_TEMPLATE.md`
- `/Users/nguyenthanhthu/AI_OS/15_EXECUTION_MODEL/AI_OS_INTEGRATION.md`

### Project-instance layer ở ATP
ATP giữ instance project-specific dưới:
- `docs/execution/ROADMAP_EXECUTION.md`
- `docs/execution/PROMPT_CMD/INDEX.md`
- `docs/execution/PROMPT_CMD/*.md`

## Rule bắt buộc
- Canonical global model change phải đi ở AI_OS trước.
- ATP chỉ được customize execution planning ở mức project-instance:
  - feature naming
  - priority
  - dependencies
  - verification commands
  - staged packs theo ATP reality
- ATP instance không được tự biến thành doctrine global.

## ATP customization boundary
ATP hiện customize execution planning theo thực trạng:
- baseline stable trên `main` là `v1.0.4`
- execution branch active là `codex/release-v1.1-execution`
- current line là bounded single-AI operator-facing execution hardening
- không mở orchestration / scheduler / automation / provider abstraction trong layer này

## Kết luận
`docs/execution/` là execution PLAN layer của ATP, được instantiate từ AI_OS canonical execution model, nhưng chỉ dùng để điều hướng ATP execution theo feature-program một cách bounded, staged, fail-stop, và reviewable.
