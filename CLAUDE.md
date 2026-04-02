# CLAUDE.md

This file provides context for Claude Code (and other AI assistants) working in the ATP platform repository.

## Project overview

**ATP (Autonomous Task Platform)** is a control-plane platform that mediates between requested users and product execution surfaces. The operating axis is:

```
requested user <-> ATP <-> products
```

ATP v0 is a **shape-correct MVP** — not a runtime artifact repository. This repo maintains the control-plane source of truth: core logic, adapters, registry data, schemas, templates, and documentation.

## Repository boundaries

| Boundary | Path | Purpose |
|----------|------|---------|
| ATP source repo | `SOURCE_DEV/platforms/ATP` | This repository |
| Product repo | `SOURCE_DEV/products/TDF` | Product ATP resolves in v0 |
| Runtime zone | `SOURCE_DEV/workspace` | Runs, artifacts, exchange, logs |

Runtime artifacts, run outputs, exchange bundles, and logs must **never** live in this repo.

## Directory structure

```
atp-platform/
├── adapters/          # Extension seams (filesystem, subprocess, SSH, API, etc.)
│   ├── contracts/     # Base adapter contracts (artifact, execution, handoff)
│   ├── filesystem/    # Filesystem materialization (active)
│   ├── subprocess/    # Local execution (active)
│   └── ...            # ssh_remote, api, desktop_bridge, etc. (placeholders)
├── cli/               # CLI entry points
│   ├── atp            # Bash dispatcher: run, inspect, validate, help
│   ├── run.py         # M1-M8 run preview
│   ├── inspect.py     # Inspect current task
│   └── validate.py    # Validate requests
├── core/              # Control-plane logic (~3,300 LOC across 13 modules)
│   ├── intake/        # Request loading & normalization
│   ├── classification/# Rule-based request classification
│   ├── resolution/    # Product & policy resolution
│   ├── routing/       # Route preparation & selection
│   ├── context/       # Bundle materialization & context
│   ├── execution/     # Execution orchestration
│   ├── validation/    # Artifact validation
│   ├── approvals/     # Approval gate control
│   ├── handoff/       # Exchange boundary & continuation
│   ├── finalization/  # Run closure/continuation
│   ├── state/         # Run & decision state management
│   └── decision_control/ # Slice D decision contracts
├── docs/              # Architecture, design, governance, roadmap (~136 files)
├── profiles/          # Product/service profiles (ATP, TDF)
├── prompts/           # Prompt templates (execution, handoff, review)
├── registry/          # Static lookup data (YAML)
│   ├── products/      # Product definitions (ATP.yaml, TDF.yaml)
│   ├── capabilities/  # shell_execution, build, git, lint, test
│   ├── providers/     # Provider definitions
│   ├── nodes/         # Node definitions (local_mac.yaml)
│   └── policies/      # approval, routing, cost, escalation
├── schemas/           # YAML schemas (request, artifact, approval, handoff, routing, run)
├── scripts/           # Bash maintenance scripts
├── templates/         # Template bundles (evidence, exchange, decisions, manifests)
└── tests/             # Unit (8 files) + integration (4 files) + fixtures
```

## Tech stack

- **Language:** Python 3.11 (standard library, no external dependencies)
- **Build:** GNU Make
- **CI:** GitHub Actions (`.github/workflows/ci.yml`) — push/PR triggers, ubuntu-latest, Python 3.11
- **Testing:** Python `unittest` framework
- **Data formats:** YAML (schemas, registry, profiles, templates)
- **Documentation:** Markdown (Vietnamese + English technical terms)

## Common commands

```bash
make test               # Run all unit + integration tests
make smoke              # Run ATP M1-M2 smoke flow
make validate-registry  # Verify registry seed files exist
make tree               # Print repo tree summary
make help               # Show all available targets

# CLI usage
cli/atp run <request.yaml>       # Preview M1-M8 flow
cli/atp inspect                  # Inspect current task state
cli/atp validate <request.yaml>  # Validate request format

# AI_OS bridge
make aios-context       # Print ATP-side AI_OS bridge context
make aios-status        # Context + git status
make aios-verify        # Verify bridge surface
```

## Testing

Tests use Python's built-in `unittest` with `discover`:

```bash
python3 -m unittest discover -s tests/unit -p 'test_*.py'
python3 -m unittest discover -s tests/integration -p 'test_*.py'
```

Test fixtures are in `tests/fixtures/` (sample requests, product context, output dir).

## Core operating flow

```
Intake -> Normalize -> Classify -> Resolve Product ->
Build Context -> Route -> Prepare Execution ->
Execute -> Validate -> Review -> Approve ->
Handoff/Exchange -> Finalize/Close/Continue
```

## Governance rules (binding)

These rules from `AGENTS.md` apply to all AI agents:

1. **Source-of-truth hierarchy** (apply in order):
   1. Human-approved current task instruction
   2. `docs/architecture/ATP_MVP_v0_Freeze_Decision_Record.md`
   3. ATP v0 implementation plan and architecture docs
   4. Design, operators, and governance docs
   5. Existing code and file layout

2. **Minimal churn** — prefer the smallest justified change. No speculative restructuring.

3. **Preserve frozen boundaries** — do not expand scope outside the frozen ATP v0 architecture without explicit human approval.

4. **No vocabulary invention** — use existing ATP terminology. Do not rename files, concepts, or contracts casually.

5. **Archive discipline** — `docs/archive/` is for historical traceability, not active authority.

6. **When uncertain** — do not guess architecture, expand scope, or invent new authority paths. Document the gap instead.

## Approval gates

The following actions require explicit human approval:

- Merge to `main`
- Push to `main`
- Tag a release

## Frozen versions

| Version | Scope |
|---------|-------|
| v0.1.0 | Hardening baseline |
| v0.2.0 | Consolidated runtime materialization |
| v0.3.0 | Consolidated exchange boundary & continuity |
| v0.4.0 | Consolidated task persistence & recovery |
| v1.0.0-v1.0.4 | Slice E governance/docs line |

## Code conventions

- **Editor config:** UTF-8, LF line endings, 2-space indent, trim trailing whitespace (`.editorconfig`)
- **Python style:** Standard library only, unittest for tests, type hints where present in existing code
- **YAML schemas:** All data structures defined in `schemas/` directory
- **Module pattern:** Each `core/` module has its own directory with focused `.py` files and `__init__.py`
- **Adapter pattern:** Contracts in `adapters/contracts/`, implementations in subdirectories

## External AI operating context

ATP integrates with an external AI_OS operating context at `/Users/nguyenthanhthu/AI_OS`. This path is the owner's local machine and may not exist in CI or other environments. The bridge files (CLAUDE.md, AGENTS.md, .cursorrules, copilot-instructions.md, AI_OS_CONTEXT.md) reference this external context for session continuity and global governance rules.

When these external paths are unavailable, operate using repo-local governance (AGENTS.md, docs/) as the authority.
