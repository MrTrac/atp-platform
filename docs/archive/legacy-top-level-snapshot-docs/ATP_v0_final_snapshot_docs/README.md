# ATP

ATP is a platform repository for architecture-locked orchestration work inside the `SOURCE_DEV` workspace model.

## Repository boundary

ATP lives at:

```text
SOURCE_DEV/platforms/ATP
```

This repository is intentionally separate from:

- `SOURCE_DEV/products/TDF` — product repository
- `SOURCE_DEV/workspace` — runtime workspace zone

`SOURCE_DEV/` is a logical workspace root, not a monorepo root.

## ATP MVP v0 status

ATP MVP v0 is now implemented as an implemented baseline and should be understood as a shape-correct MVP.

## Current baseline

ATP v0 currently supports:

1. request intake
2. normalization
3. classification
4. product resolution
5. context packaging
6. routing preparation and deterministic route selection
7. local non-LLM execution path
8. artifact capture
9. validation and minimal review
10. approval gate summary
11. handoff outputs
12. finalization
13. close-run / continue-run decision

## Local bootstrap

```bash
cd /Users/nguyenthanhthu/SOURCE_DEV/platforms/ATP
python3 -m compileall cli core tests
make test
```
