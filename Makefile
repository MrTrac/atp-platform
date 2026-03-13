SHELL := /bin/bash

.PHONY: help tree validate-registry smoke test

help:
	@printf 'Targets:\n'
	@printf '  help               Show available targets\n'
	@printf '  tree               Print repo tree summary\n'
	@printf '  validate-registry  Run safe registry seed checks\n'
	@printf '  smoke              Run ATP M1-M2 smoke flow\n'
	@printf '  test               Run lightweight ATP tests\n'

tree:
	@find . -maxdepth 3 | sort

validate-registry:
	@./scripts/validate_registry.sh

smoke:
	@./scripts/smoke_run.sh

test:
	@python3 -m unittest discover -s tests/unit -p 'test_*.py'
	@python3 -m unittest discover -s tests/integration -p 'test_*.py'
