# ATP

ATP là `platform repository` tại `SOURCE_DEV/platforms/ATP`.

ATP MVP v0 là một `shape-correct MVP`: giữ đúng boundary của repo, hình thái control-plane, registry, adapter, artifact lifecycle, và flow human-gated đã được freeze. Repo này dùng để phát triển và duy trì ATP source; repo này không phải runtime artifact repository.

Trạng thái baseline đã freeze:

- `v0.1.0` — hardening baseline
- `v0.2.0` — consolidated runtime materialization baseline
- `v0.3.0` — consolidated exchange boundary và continuity baseline
- `v0.4.0` — consolidated current-task persistence, recovery, pointer, và inspect baseline

Branch hiện tại có thể đi tiếp sang planning phase mới, nhưng không được ghi đè historical facts của các version đã freeze.

ATP không phải là một closed snapshot architecture và cũng không phải một ad hoc open architecture.

ATP được duy trì như:

- một stable core
- với modular boundaries
- explicit extension seams
- composable capabilities
- và controlled evolutionary governance

ATP cũng phải được hiểu qua operating axis:

`requested user ⇄ ATP ⇄ products`

ATP không mở rộng chỉ để tăng internal mechanisms. ATP mở rộng khi việc đó giúp ATP mediate tốt hơn giữa requested user và product execution surfaces.

## Boundary chính

- `SOURCE_DEV/` là `logical workspace root`
- `SOURCE_DEV/platforms/ATP` là ATP source repo
- `SOURCE_DEV/products/TDF` là product repo mà ATP resolve trong v0
- `SOURCE_DEV/workspace` là runtime zone cho runs, artifacts, exchange, và logs

Runtime artifacts không được lưu trong repo này. Runs, output, exchange bundle, logs, và các artifact phát sinh trong quá trình vận hành phải thuộc `SOURCE_DEV/workspace`.

## Repo này dùng để làm gì

- phát triển ATP CLI, control-plane modules, adapters, registry, schema, profiles, và templates thuộc ATP
- duy trì tài liệu kiến trúc, thiết kế, vận hành, và governance của ATP
- hardening, refinement, normalization, và planning có governance trong phạm vi current ATP `v0` major family và các frozen baselines đã có

## Repo này không dùng để làm gì

- không dùng làm nơi lưu runtime artifact
- không dùng làm workspace vận hành cho run output hoặc exchange output
- không dùng để mở rộng scope kiến trúc ngoài ATP v0 nếu chưa có decision rõ ràng

## Tài liệu nên đọc trước

Thứ tự đọc source of truth:

1. `docs/architecture/ATP_MVP_v0_Freeze_Decision_Record.md`
2. `docs/architecture/ATP_MVP_v0_Implementation_Plan.md`
3. `docs/README.md`
4. các tài liệu liên quan trong `docs/design/`, `docs/operators/`, và `docs/governance/`

Nếu cần historical freeze facts:

- `docs/archive/reports/ATP_v0_2_0_Freeze_Closeout.md`
- `docs/archive/reports/ATP_v0_3_0_Freeze_Closeout.md`
- `docs/archive/reports/ATP_v0_4_0_Freeze_Closeout.md`

Nếu cần roadmap continuity:

- `docs/roadmap/README.md`
- `docs/roadmap/ATP_Product_Roadmap.md`

Nếu cần operational development rules:

- `docs/governance/ATP_Development_Ruleset.md`

## Local bootstrap

```bash
make help
make tree
make validate-registry
make smoke
make test
```

## Nguyên tắc khi phát triển trong repo này

- giữ boundary giữa source repo và runtime zone
- ưu tiên refinement, normalization, và hardening hơn là mở rộng feature sớm
- mở rộng capability chỉ qua review, planning, verification, consolidation, freeze, close-out, và roadmap inheritance có kiểm soát
- giữ glossary, naming, schema, và artifact terminology đồng bộ với tài liệu ATP
- không đảo ngược source-of-truth order một cách ngầm định
- mọi thay đổi vượt ra ngoài ATP v0 freeze phải có decision rõ ràng do con người chốt
