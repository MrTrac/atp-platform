# ATP v0.1 Hardening Runbook

- **Title:** ATP v0.1 Hardening Runbook
- **Version:** v0.1 R2
- **Status:** Draft-Baseline
- **Date:** 2026-03-14

## 1. Purpose

This runbook describes how ATP v0.1 hardening work should be approached.

ATP v0.1 is a hardening track for the ATP MVP v0 implemented baseline.

## 2. Working rule

Operate only inside:

```text
/Users/nguyenthanhthu/SOURCE_DEV/platforms/ATP
```

ATP v0.1 hardening must not modify:

- `SOURCE_DEV/products/TDF`
- `SOURCE_DEV/workspace`

## 3. Verification sequence

Before and after meaningful hardening changes, run:

```bash
cd /Users/nguyenthanhthu/SOURCE_DEV/platforms/ATP
python3 -m compileall cli core tests
make test
```

## 4. Hardening focus areas

ATP v0.1 hardening should focus on:

- docs cleanup
- naming consistency
- CLI summary normalization
- inspect hardening
- fixture cleanup
- test coverage improvement
- artifact summary / final summary polish

## 5. What not to do

ATP v0.1 hardening must not be used for:

- adding new execution providers
- adding production workspace persistence
- redesigning approval flow
- redesigning routing model
- introducing new orchestration layers
- adding remote orchestration plane behavior

## 6. Non-goals

ATP v0.1 hardening must not turn into expansion work.

The following remain out of scope:

- production workspace materialization
- approval UI
- remote orchestration plane
- advanced scheduling
- multi-provider arbitration
- major new execution capability

## 7. Recommended execution order

1. docs cleanup and naming consistency
2. CLI and inspect hardening
3. fixture cleanup and test hardening
4. artifact/report polish

## 8. Operator interpretation

If a proposed change:
- improves clarity
- improves consistency
- improves maintainability
- improves regression confidence

then it is likely valid ATP v0.1 hardening work.

If a proposed change:
- adds a new orchestration plane
- adds a major new execution mode
- adds approval UI
- adds workspace production persistence

then it likely belongs after ATP v0.1.

## 9. Completion rule

ATP v0.1 hardening is complete when the ATP v0 implemented baseline is cleaner, more consistent, easier to operate, and better protected by tests — without changing the MVP boundary.
