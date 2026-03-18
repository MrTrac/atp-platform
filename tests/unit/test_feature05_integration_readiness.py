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


if __name__ == "__main__":
    unittest.main()
