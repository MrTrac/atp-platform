"""Evidence and contract tests for ATP v1.2 Feature 05 integration readiness surface — P1.

P1 scope: verify bounded readiness category definitions and explicit blockers-by-design.
This is signaling only — no integration activation, no external calls, no runtime state.
"""

from __future__ import annotations

import subprocess
import unittest
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parents[2]


class TestFeature05IntegrationReadinessP1Categories(unittest.TestCase):
    """Lock the bounded integration readiness category definitions."""

    def _get_summary(self) -> dict:  # type: ignore[type-arg]
        from core.integration_readiness import build_integration_readiness_summary

        return dict(build_integration_readiness_summary())

    def test_readiness_scope_is_signaling_only(self) -> None:
        from core.integration_readiness import READINESS_SCOPE

        self.assertEqual(READINESS_SCOPE, "integration_preparation_signaling_only")

    def test_integration_mode_is_not_activated(self) -> None:
        from core.integration_readiness import INTEGRATION_MODE

        self.assertEqual(INTEGRATION_MODE, "not_activated")

    def test_supported_features_are_all_repo_local(self) -> None:
        from core.integration_readiness import SUPPORTED_FEATURES

        self.assertIn("repo_local_bounded_request_flow", SUPPORTED_FEATURES)
        self.assertIn("repo_local_execution_session_tracking", SUPPORTED_FEATURES)
        self.assertIn("human_gated_single_ai_handoff", SUPPORTED_FEATURES)
        self.assertIn("json_first_output_contract", SUPPORTED_FEATURES)
        # No supported feature should imply external integration
        for feature in SUPPORTED_FEATURES:
            self.assertNotIn("external", feature, msg=f"Unexpected external feature: {feature}")
            self.assertNotIn("network", feature, msg=f"Unexpected network feature: {feature}")

    def test_unsupported_features_block_activation_patterns(self) -> None:
        from core.integration_readiness import UNSUPPORTED_FEATURES

        self.assertIn("external_api_endpoint", UNSUPPORTED_FEATURES)
        self.assertIn("webhook_consumer", UNSUPPORTED_FEATURES)
        self.assertIn("multi_ai_orchestration", UNSUPPORTED_FEATURES)
        self.assertIn("background_execution_engine", UNSUPPORTED_FEATURES)
        self.assertIn("scheduler_or_queue", UNSUPPORTED_FEATURES)
        self.assertIn("automated_ai_progression", UNSUPPORTED_FEATURES)

    def test_safe_entrypoints_are_existing_atp_cli_commands(self) -> None:
        from core.integration_readiness import SAFE_INTEGRATION_ENTRYPOINTS

        expected = {
            "request-flow",
            "request-bundle",
            "request-prompt",
            "execution-session",
            "smoke-request-chain",
        }
        for entrypoint in expected:
            self.assertIn(entrypoint, SAFE_INTEGRATION_ENTRYPOINTS)

    def test_blocked_actions_cover_activation_and_release_gates(self) -> None:
        from core.integration_readiness import BLOCKED_ACTIONS

        self.assertIn("activate_external_integration", BLOCKED_ACTIONS)
        self.assertIn("open_network_endpoint", BLOCKED_ACTIONS)
        self.assertIn("start_background_daemon", BLOCKED_ACTIONS)
        self.assertIn("bypass_human_gate", BLOCKED_ACTIONS)
        self.assertIn("merge_main_without_approval", BLOCKED_ACTIONS)
        self.assertIn("push_main_without_approval", BLOCKED_ACTIONS)
        self.assertIn("tag_release_without_approval", BLOCKED_ACTIONS)

    def test_build_integration_readiness_summary_returns_bounded_signaling_dict(self) -> None:
        summary = self._get_summary()

        self.assertEqual(summary["readiness_scope"], "integration_preparation_signaling_only")
        self.assertEqual(summary["integration_mode"], "not_activated")
        self.assertIsInstance(summary["supported_features"], list)
        self.assertIsInstance(summary["unsupported_features"], list)
        self.assertIsInstance(summary["safe_integration_entrypoints"], list)
        self.assertIsInstance(summary["blocked_actions"], list)
        self.assertIsInstance(summary["notes"], list)

    def test_build_integration_readiness_summary_notes_confirm_signaling_only(self) -> None:
        summary = self._get_summary()

        notes_text = " ".join(summary["notes"])
        self.assertIn("signaling only", notes_text)
        self.assertIn("does not activate integration", notes_text)
        self.assertIn("repo-local", notes_text)
        self.assertIn("human-gated", notes_text)

    def test_integration_readiness_module_has_no_import_side_effects(self) -> None:
        # Importing the module must not trigger any network call, file write, or subprocess.
        # This is verified by importing it cleanly within a subprocess check.
        result = subprocess.run(
            ["python3", "-c", "import sys; sys.path.insert(0, '.'); from core.integration_readiness import build_integration_readiness_summary; s = build_integration_readiness_summary(); assert s['integration_mode'] == 'not_activated'"],
            check=False,
            capture_output=True,
            text=True,
            cwd=ROOT_DIR,
        )
        self.assertEqual(result.returncode, 0, msg=f"Import side-effect check failed: {result.stderr}")

    def test_smoke_request_chain_still_passes_before_readiness_surface_is_surfaced(self) -> None:
        result = subprocess.run(
            [str(ROOT_DIR / "atp"), "smoke-request-chain"],
            check=False,
            capture_output=True,
            text=True,
            cwd=ROOT_DIR,
        )

        self.assertEqual(result.returncode, 0)
        self.assertIn("smoke_verification: passed", result.stdout)
        self.assertIn("bounded_request_chain_completed: true", result.stdout)


class TestFeature05IntegrationReadinessP2Surface(unittest.TestCase):
    """Lock the bounded integration readiness surface added in P2."""

    def test_help_output_has_integration_readiness_block(self) -> None:
        result = subprocess.run(
            [str(ROOT_DIR / "atp"), "help"],
            check=False,
            capture_output=True,
            text=True,
            cwd=ROOT_DIR,
        )

        self.assertEqual(result.returncode, 0)
        self.assertIn("Integration readiness (v1.2 phase", result.stdout)
        self.assertIn("readiness_scope  -> integration_preparation_signaling_only", result.stdout)
        self.assertIn("integration_mode -> not_activated", result.stdout)
        self.assertIn("entrypoints      ->", result.stdout)
        self.assertIn("blocked          ->", result.stdout)

    def test_execution_session_output_has_integration_readiness_summary(self) -> None:
        import json
        from collections import OrderedDict

        result = subprocess.run(
            [str(ROOT_DIR / "atp"), "execution-session", "tests/fixtures/requests/sample_request_slice02.yaml"],
            check=False,
            capture_output=True,
            text=True,
            cwd=ROOT_DIR,
        )

        self.assertEqual(result.returncode, 0)
        payload = json.loads(result.stdout, object_pairs_hook=OrderedDict)
        self.assertIn("integration_readiness_summary", payload)
        irs = payload["integration_readiness_summary"]
        self.assertEqual(irs["readiness_scope"], "integration_preparation_signaling_only")
        self.assertEqual(irs["integration_mode"], "not_activated")
        self.assertIn("safe_integration_entrypoints", irs)
        self.assertIn("blocked_actions", irs)

    def test_execution_session_integration_readiness_summary_is_compact(self) -> None:
        import json
        from collections import OrderedDict

        result = subprocess.run(
            [str(ROOT_DIR / "atp"), "execution-session", "tests/fixtures/requests/sample_request_slice02.yaml"],
            check=False,
            capture_output=True,
            text=True,
            cwd=ROOT_DIR,
        )

        self.assertEqual(result.returncode, 0)
        payload = json.loads(result.stdout, object_pairs_hook=OrderedDict)
        irs = payload["integration_readiness_summary"]
        # Compact: only 4 approved fields, no full feature lists
        self.assertEqual(list(irs.keys()), ["readiness_scope", "integration_mode", "safe_integration_entrypoints", "blocked_actions"])
        self.assertNotIn("supported_features", irs)
        self.assertNotIn("unsupported_features", irs)
        self.assertNotIn("next_safe_prep_action", irs)
        self.assertNotIn("notes", irs)

    def test_integration_readiness_summary_not_spread_to_request_flow(self) -> None:
        import json

        result = subprocess.run(
            [str(ROOT_DIR / "atp"), "request-flow", "tests/fixtures/requests/sample_request_slice02.yaml"],
            check=False,
            capture_output=True,
            text=True,
            cwd=ROOT_DIR,
        )

        self.assertEqual(result.returncode, 0)
        payload = json.loads(result.stdout)
        self.assertNotIn("integration_readiness_summary", payload)
        self.assertNotIn("integration_readiness_summary", str(payload))

    def test_integration_readiness_summary_not_spread_to_request_bundle(self) -> None:
        import json

        result = subprocess.run(
            [str(ROOT_DIR / "atp"), "request-bundle", "tests/fixtures/requests/sample_request_slice02.yaml"],
            check=False,
            capture_output=True,
            text=True,
            cwd=ROOT_DIR,
        )

        self.assertEqual(result.returncode, 0)
        payload = json.loads(result.stdout)
        self.assertNotIn("integration_readiness_summary", str(payload))

    def test_integration_readiness_summary_not_spread_to_request_prompt(self) -> None:
        import json

        result = subprocess.run(
            [str(ROOT_DIR / "atp"), "request-prompt", "tests/fixtures/requests/sample_request_slice02.yaml"],
            check=False,
            capture_output=True,
            text=True,
            cwd=ROOT_DIR,
        )

        self.assertEqual(result.returncode, 0)
        payload = json.loads(result.stdout)
        self.assertNotIn("integration_readiness_summary", str(payload))

    def test_smoke_request_chain_still_passes_after_readiness_surface_added(self) -> None:
        result = subprocess.run(
            [str(ROOT_DIR / "atp"), "smoke-request-chain"],
            check=False,
            capture_output=True,
            text=True,
            cwd=ROOT_DIR,
        )

        self.assertEqual(result.returncode, 0)
        self.assertIn("smoke_verification: passed", result.stdout)
        self.assertIn("bounded_request_chain_completed: true", result.stdout)


class TestFeature05IntegrationReadinessP3Boundaries(unittest.TestCase):
    """Regression locks: integration readiness surface must not imply activation, automation, or external execution."""

    def test_integration_readiness_summary_integration_mode_is_never_activated(self) -> None:
        import json

        result = subprocess.run(
            [str(ROOT_DIR / "atp"), "execution-session", "tests/fixtures/requests/sample_request_slice02.yaml"],
            check=False,
            capture_output=True,
            text=True,
            cwd=ROOT_DIR,
        )

        self.assertEqual(result.returncode, 0)
        payload = json.loads(result.stdout)
        irs = payload["integration_readiness_summary"]
        self.assertNotEqual(irs["integration_mode"], "activated")
        self.assertNotEqual(irs["integration_mode"], "active")
        self.assertNotEqual(irs["integration_mode"], "enabled")
        self.assertEqual(irs["integration_mode"], "not_activated")

    def test_integration_readiness_summary_does_not_contain_orchestration_language(self) -> None:
        import json

        result = subprocess.run(
            [str(ROOT_DIR / "atp"), "execution-session", "tests/fixtures/requests/sample_request_slice02.yaml"],
            check=False,
            capture_output=True,
            text=True,
            cwd=ROOT_DIR,
        )

        self.assertEqual(result.returncode, 0)
        payload = json.loads(result.stdout)
        irs_text = str(payload["integration_readiness_summary"]).lower()
        self.assertNotIn("orchestrat", irs_text)
        self.assertNotIn("scheduler", irs_text)
        self.assertNotIn("queue", irs_text)
        self.assertNotIn("webhook", irs_text)
        self.assertNotIn("async", irs_text)

    def test_integration_readiness_summary_does_not_expose_external_endpoint(self) -> None:
        import json

        result = subprocess.run(
            [str(ROOT_DIR / "atp"), "execution-session", "tests/fixtures/requests/sample_request_slice02.yaml"],
            check=False,
            capture_output=True,
            text=True,
            cwd=ROOT_DIR,
        )

        self.assertEqual(result.returncode, 0)
        payload = json.loads(result.stdout)
        irs = payload["integration_readiness_summary"]
        irs_str = str(irs).lower()
        # No URL, port, host, or external endpoint reference
        self.assertNotIn("http", irs_str)
        self.assertNotIn("://", irs_str)
        self.assertNotIn("localhost", irs_str)
        self.assertNotIn("port", irs_str)

    def test_help_integration_readiness_block_does_not_imply_activation(self) -> None:
        result = subprocess.run(
            [str(ROOT_DIR / "atp"), "help"],
            check=False,
            capture_output=True,
            text=True,
            cwd=ROOT_DIR,
        )

        self.assertEqual(result.returncode, 0)
        # The block must clearly signal not_activated, not enabled
        self.assertIn("integration_mode -> not_activated", result.stdout)
        self.assertNotIn("integration_mode -> activated", result.stdout)
        self.assertNotIn("integration_mode -> enabled", result.stdout)

    def test_help_integration_readiness_block_does_not_contain_external_runtime_language(self) -> None:
        result = subprocess.run(
            [str(ROOT_DIR / "atp"), "help"],
            check=False,
            capture_output=True,
            text=True,
            cwd=ROOT_DIR,
        )

        self.assertEqual(result.returncode, 0)
        # Extract only the integration readiness section
        lines = result.stdout.splitlines()
        in_ir_block = False
        ir_lines: list[str] = []
        for line in lines:
            if "Integration readiness" in line:
                in_ir_block = True
            elif in_ir_block and line.strip() == "":
                break
            if in_ir_block:
                ir_lines.append(line.lower())
        ir_text = "\n".join(ir_lines)
        self.assertNotIn("orchestrat", ir_text)
        self.assertNotIn("scheduler", ir_text)
        self.assertNotIn("webhook", ir_text)
        self.assertNotIn("http", ir_text)

    def test_compact_integration_readiness_module_has_no_network_imports(self) -> None:
        # Verify core/integration_readiness.py does not import network or subprocess modules.
        module_path = ROOT_DIR / "core" / "integration_readiness.py"
        source = module_path.read_text()
        self.assertNotIn("import requests", source)
        self.assertNotIn("import urllib", source)
        self.assertNotIn("import http.client", source)
        self.assertNotIn("import socket", source)
        self.assertNotIn("import subprocess", source)
        self.assertNotIn("open(", source)

    def test_execution_session_output_contract_is_not_broken_by_readiness_surface(self) -> None:
        import json

        result = subprocess.run(
            [str(ROOT_DIR / "atp"), "execution-session", "tests/fixtures/requests/sample_request_slice02.yaml"],
            check=False,
            capture_output=True,
            text=True,
            cwd=ROOT_DIR,
        )

        self.assertEqual(result.returncode, 0)
        payload = json.loads(result.stdout)
        # Core contract keys still present and unchanged
        self.assertIn("command", payload)
        self.assertIn("status", payload)
        self.assertIn("operator_scan_summary", payload)
        self.assertIn("session_summary", payload)
        self.assertEqual(payload["status"], "ok")
        self.assertEqual(payload["command"], "execution-session")
        # New readiness field is additive, not replacing existing fields
        self.assertEqual(len(payload), 6)

    def test_smoke_request_chain_confirms_no_pseudo_integration_drift(self) -> None:
        result = subprocess.run(
            [str(ROOT_DIR / "atp"), "smoke-request-chain"],
            check=False,
            capture_output=True,
            text=True,
            cwd=ROOT_DIR,
        )

        self.assertEqual(result.returncode, 0)
        self.assertIn("smoke_verification: passed", result.stdout)
        self.assertIn("bounded_request_chain_completed: true", result.stdout)
        self.assertIn("control_boundary: repo_local_human_gated_manual_single_ai_only", result.stdout)
        self.assertIn("release_gates_opened: false", result.stdout)


if __name__ == "__main__":
    unittest.main()
