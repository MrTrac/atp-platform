# ATP

ATP la platform repo tai `SOURCE_DEV/platforms/ATP`.

ATP MVP v0 duoc dinh vi la shape-correct MVP: giu dung boundary repo, Control Plane shape, registry shape, adapter shape, artifact lifecycle, va human-gated flow; khong mo rong scope ngoai kien truc da khoa.

## Boundary

- `SOURCE_DEV/` la logical workspace root.
- `SOURCE_DEV/platforms/ATP` la ATP source repo.
- `SOURCE_DEV/products/TDF` la product repo ATP phai resolve trong v0.
- `SOURCE_DEV/workspace` la runtime zone cho runs, artifacts, exchange, va logs.

ATP khong luu runtime artifact trong repo nay. Runtime artifact phai nam trong `SOURCE_DEV/workspace`.

## Tai lieu kien truc

- Freeze Decision Record: `docs/architecture/ATP_MVP_v0_Freeze_Decision_Record.md`
- Implementation Plan: `docs/architecture/ATP_MVP_v0_Implementation_Plan.md`
- Architecture index: `docs/README.md`

## Bootstrap local

```bash
make help
make tree
make validate-registry
make smoke
make test
```
