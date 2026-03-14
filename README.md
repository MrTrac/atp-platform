# ATP

ATP là `platform repository` tại `SOURCE_DEV/platforms/ATP`.

ATP MVP v0 là một `shape-correct MVP`: giữ đúng boundary của repo, hình thái control-plane, registry, adapter, artifact lifecycle, và flow human-gated đã được freeze. Repo này dùng để phát triển và duy trì ATP source; repo này không phải runtime artifact repository.

## Boundary chính

- `SOURCE_DEV/` là `logical workspace root`
- `SOURCE_DEV/platforms/ATP` là ATP source repo
- `SOURCE_DEV/products/TDF` là product repo mà ATP resolve trong v0
- `SOURCE_DEV/workspace` là runtime zone cho runs, artifacts, exchange, và logs

Runtime artifacts không được lưu trong repo này. Runs, output, exchange bundle, logs, và các artifact phát sinh trong quá trình vận hành phải thuộc `SOURCE_DEV/workspace`.

## Repo này dùng để làm gì

- phát triển ATP CLI, control-plane modules, adapters, registry, schema, profiles, và templates thuộc ATP
- duy trì tài liệu kiến trúc, thiết kế, vận hành, và governance của ATP
- hardening, refinement, và normalization trong phạm vi ATP v0 đã freeze

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
- giữ glossary, naming, schema, và artifact terminology đồng bộ với tài liệu ATP
- không đảo ngược source-of-truth order một cách ngầm định
- mọi thay đổi vượt ra ngoài ATP v0 freeze phải có decision rõ ràng do con người chốt
