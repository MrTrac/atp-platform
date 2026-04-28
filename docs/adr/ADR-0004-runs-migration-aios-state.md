# ADR-0004: runs-migration-aios-state

- **Status:** Accepted
- **Date:** 2026-04-27 (Phase 1 DP#50)
- **Author(s):** anh Thu + Claude Code
- **Module(s):** ATP
- **Governance:** AI_OS Doctrine §3.4.3 + DP#50 + DP#78
- **Decision tier:** Tier 2 (Z1 internal — runtime artifact location)

---

## 1. Context

ATP runs accumulated in source repo at `~/SOURCE_DEV/platforms/ATP/runs/`. 35 runs / 928K bytes. Problems:
- Runtime artifacts trong git source tree → noisy `git status`, repo bloat
- Backup tooling (DP#49 `aios-backup`) needs canonical path
- Other modules (aios-flow runners) hardcode `runs/<id>/...` paths

---

## 2. Decision

Migrate `~/SOURCE_DEV/platforms/ATP/runs/` → `~/.aios/atp/runs/` với symlink backward-compat:

```
~/SOURCE_DEV/platforms/ATP/runs → /Users/nguyenthanhthu/.aios/atp/runs (symlink)
```

35 runs (928K) moved physically. Symlink ensures existing code paths still work. Apply migration via one-time script logged to `~/.aios/.migration-audit.log`.

Future: 90-day TTL prune logic (DP#50 follow-up Phase 2 — extend `aios-runtime`).

---

## 3. Alternatives considered

| # | Alternative | Pros | Cons | Rejected |
|---|---|---|---|---|
| A | Keep in source repo, gitignore | Zero refactor | Backup tool needs special-case path discovery |
| B | Move + refactor all callers | Clean | High risk, many call sites in adapters |
| C (chosen) | Move + symlink backward-compat | Best of both — runtime artifacts out of source, code unchanged | Symlink fragility (don't rename `~/.aios/atp/`) |

---

## 4. Consequences

### 4.1 Positive
- `git status` clean (no untracked artifacts)
- DP#49 backup tool has canonical path target
- Sanitation Plan v3 closeout reflects clean source tree

### 4.2 Negative / trade-offs
- Symlink doesn't survive zip/tar archives unless preserved (`tar -h` flag)
- If user `mv ~/.aios/atp ~/.aios/atp_v2` → dangling symlink

### 4.3 Risks accepted
- DON'T rename `~/.aios/atp/` location (5-year invariant locked in MODULE_BOUNDARY.md)

---

## 5. Implementation
- One-time bash migration: `~/AI_OS/30_RUNTIME/scripts/migrate-atp-runs.sh`
- Creates `~/.aios/atp/runs/`, moves 35 directories, creates symlink at source repo location
- Audit logged to `~/.aios/.migration-audit.log`
- Verified post-migration: `git status` clean, ATP code reads via symlink succeeds

## 6. References
- AI_OS Doctrine §3.4.3 retention policy (90-day TTL TBD Phase 2)
- DP#49 `aios-backup` — target list includes `~/.aios/atp/runs/`
- AI_OS commit `e4c49cd` (Phase 1 DP#50 DONE)
