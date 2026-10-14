SHELL := /bin/bash
PYTHONPATH := .
export PYTHONPATH

.PHONY: help tree validate-registry smoke test test-unit test-integration ci-local bridge bridge-raw version \
        aios-context aios-status aios-authority aios-verify

help:
	@printf 'Targets:\n'
	@printf '  help               Show available targets\n'
	@printf '  version            Print current ATP version\n'
	@printf '  tree               Print repo tree summary\n'
	@printf '  validate-registry  Run safe registry seed checks\n'
	@printf '  smoke              Run ATP M1-M2 smoke flow\n'
	@printf '  test               Run all tests (unit + integration)\n'
	@printf '  test-unit          Run unit tests only\n'
	@printf '  test-integration   Run integration tests only\n'
	@printf '  ci-local           Run the tests like CI does: clean clone of HEAD, clean environment, every Python of the CI matrix (run before pushing)\n'
	@printf '                     options: CI_LOCAL_ARGS="--ref <ref> | --python 3.12 | --strict | --keep | --self-check"\n'
	@printf '  bridge             Start ATP bridge server (loads API keys from macOS Keychain)\n'
	@printf '  bridge-raw         Start ATP bridge server without keychain lookup (env-only)\n'
	@printf '  aios-context       Print ATP-side AI_OS bridge context\n'
	@printf '  aios-status        Print ATP-side AI_OS bridge context plus git status\n'
	@printf '  aios-authority     Print ATP authority and bridge paths for AI_OS\n'
	@printf '  aios-verify        Verify ATP-side AI_OS bridge surface\n'

version:
	@cat VERSION

tree:
	@find . -maxdepth 3 -not -path './.git/*' -not -path './.claude/*' | sort

validate-registry:
	@./scripts/validate_registry.sh

smoke:
	@./scripts/smoke_run.sh

test: test-unit test-integration

test-unit:
	@python3 -m pytest -q -p no:cacheprovider tests/unit

test-integration:
	@python3 -m pytest -q -p no:cacheprovider tests/integration

# `make test` runs in this working copy with this machine's environment; this runs what CI runs. See scripts/ci_local.sh.
ci-local:
	@./scripts/ci_local.sh $(CI_LOCAL_ARGS)

bridge:
	@./scripts/bridge_with_keychain.sh

bridge-raw:
	@python3 bridge/bridge_server.py

aios-context:
	@./scripts/aios_bridge.sh context

aios-status:
	@./scripts/aios_bridge.sh status

aios-authority:
	@./scripts/aios_bridge.sh authority

aios-verify:
	@./scripts/aios_bridge.sh verify
