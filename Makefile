SHELL := /bin/bash

.PHONY: help tree validate-registry smoke test aios-context aios-status aios-authority aios-verify

help:
	@printf 'Targets:\n'
	@printf '  help               Show available targets\n'
	@printf '  tree               Print repo tree summary\n'
	@printf '  validate-registry  Run safe registry seed checks\n'
	@printf '  smoke              Run ATP M1-M2 smoke flow\n'
	@printf '  test               Run lightweight ATP tests\n'
	@printf '  aios-context       Print ATP-side AI_OS bridge context\n'
	@printf '  aios-status        Print ATP-side AI_OS bridge context plus git status\n'
	@printf '  aios-authority     Print ATP authority and bridge paths for AI_OS\n'
	@printf '  aios-verify        Verify ATP-side AI_OS bridge surface\n'

tree:
	@find . -maxdepth 3 | sort

validate-registry:
	@./scripts/validate_registry.sh

smoke:
	@./scripts/smoke_run.sh

test:
	@python3 -m unittest discover -s tests/unit -p 'test_*.py'
	@python3 -m unittest discover -s tests/integration -p 'test_*.py'

aios-context:
	@./scripts/aios_bridge.sh context

aios-status:
	@./scripts/aios_bridge.sh status

aios-authority:
	@./scripts/aios_bridge.sh authority

aios-verify:
	@./scripts/aios_bridge.sh verify
