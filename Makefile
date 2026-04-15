SHELL := /bin/bash
PYTHONPATH := .
export PYTHONPATH

.PHONY: help tree validate-registry smoke test test-unit test-integration bridge bridge-raw version \
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
	@python3 -m unittest discover -s tests/unit -p 'test_*.py'

test-integration:
	@python3 -m unittest discover -s tests/integration -p 'test_*.py'

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
