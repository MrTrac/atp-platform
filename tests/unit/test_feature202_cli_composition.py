"""Evidence and contract tests for ATP v1.3 Feature 202 — Structured CLI Composition Surface.

P1 scope: verify bounded composition contract definitions (stage model, envelope schema, fail-stop).
P2 scope: verify compose-chain command implementation.
P3 scope: regression locks — individual commands unchanged, no automation drift.
"""

from __future__ import annotations

import json
import subprocess
import tempfile
import unittest
from pathlib import Path


ROOT_DIR = Path(__file__).resolve().parents[2]
FIXTURE = "tests/fixtures/requests/sample_request_slice02.yaml"


class TestFeature202CliCompositionP1Contract(unittest.TestCase):
    """Lock the bounded composition contract definitions."""

    def test_composition_contract_version_is_defined(self) -> None:
        from core.composition_contract import COMPOSITION_CONTRACT_VERSION

        self.assertEqual(COMPOSITION_CONTRACT_VERSION, "1.0")

    def test_composition_mode_is_synchronous(self) -> None:
        from core.composition_contract import COMPOSITION_MODE

        self.assertIn("synchronous", COMPOSITION_MODE)
        self.assertIn("human_initiated", COMPOSITION_MODE)
        self.assertNotIn("async", COMPOSITION_MODE)
        self.assertNotIn("background", COMPOSITION_MODE)
        self.assertNotIn("retry", COMPOSITION_MODE)

    def test_stage_sequence_has_three_stages_in_order(self) -> None:
        from core.composition_contract import COMPOSITION_STAGE_SEQUENCE

        self.assertEqual(len(COMPOSITION_STAGE_SEQUENCE), 3)
        self.assertEqual(COMPOSITION_STAGE_SEQUENCE[0], "request_flow")
        self.assertEqual(COMPOSITION_STAGE_SEQUENCE[1], "request_bundle")
        self.assertEqual(COMPOSITION_STAGE_SEQUENCE[2], "request_prompt")

    def test_fail_stop_model_is_halt_on_first_failure(self) -> None:
        from core.composition_contract import FAIL_STOP_MODEL

        self.assertEqual(FAIL_STOP_MODEL, "halt_on_first_stage_failure")
        self.assertNotIn("continue", FAIL_STOP_MODEL)
        self.assertNotIn("retry", FAIL_STOP_MODEL)

    def test_composition_scope_is_bounded_to_single_request(self) -> None:
        from core.composition_contract import COMPOSITION_SCOPE

        self.assertIn("single_request", COMPOSITION_SCOPE)
        self.assertIn("synchronous", COMPOSITION_SCOPE)
        self.assertNotIn("multi", COMPOSITION_SCOPE)

    def test_composition_status_constants_defined(self) -> None:
        from core.composition_contract import COMPOSITION_STATUS_FAIL, COMPOSITION_STATUS_OK

        self.assertEqual(COMPOSITION_STATUS_OK, "all_stages_complete")
        self.assertEqual(COMPOSITION_STATUS_FAIL, "halted_at_stage_failure")

    def test_non_goals_list_excludes_automation(self) -> None:
        from core.composition_contract import COMPOSITION_NON_GOALS

        self.assertIn("parallel_stage_execution", COMPOSITION_NON_GOALS)
        self.assertIn("retry_on_failure", COMPOSITION_NON_GOALS)
        self.assertIn("background_execution", COMPOSITION_NON_GOALS)
        self.assertIn("async_mode", COMPOSITION_NON_GOALS)

    def test_build_composition_envelope_ok_returns_correct_fields(self) -> None:
        from core.composition_contract import (
            COMPOSITION_STATUS_OK,
            build_composition_envelope,
            build_stage_result,
        )

        stages = [build_stage_result(stage="request_flow", status="ok", output={"status": "ok"})]
        envelope = dict(
            build_composition_envelope(
                request_file=FIXTURE,
                run_id="run-f202-001",
                composition_status=COMPOSITION_STATUS_OK,
                stages=stages,
            )
        )
        self.assertEqual(envelope["command"], "compose-chain")
        self.assertEqual(envelope["composition_status"], COMPOSITION_STATUS_OK)
        self.assertEqual(envelope["composition_mode"], "synchronous_sequential_human_initiated")
        self.assertEqual(envelope["request_file"], FIXTURE)
        self.assertIn("stage_sequence", envelope)
        self.assertIn("stages_executed", envelope)
        self.assertNotIn("fail_stage", envelope)

    def test_build_composition_envelope_fail_requires_fail_stage(self) -> None:
        from core.composition_contract import COMPOSITION_STATUS_FAIL, build_composition_envelope

        with self.assertRaises(ValueError):
            build_composition_envelope(
                request_file=FIXTURE,
                run_id="run-f202-001",
                composition_status=COMPOSITION_STATUS_FAIL,
                stages=[],
                fail_stage=None,
            )

    def test_build_composition_envelope_rejects_invalid_status(self) -> None:
        from core.composition_contract import build_composition_envelope

        with self.assertRaises(ValueError):
            build_composition_envelope(
                request_file=FIXTURE,
                run_id="run-f202-001",
                composition_status="unknown_status",
                stages=[],
            )

    def test_build_stage_result_rejects_invalid_stage(self) -> None:
        from core.composition_contract import build_stage_result

        with self.assertRaises(ValueError):
            build_stage_result(stage="invalid_stage", status="ok", output={})

    def test_build_stage_result_returns_correct_fields(self) -> None:
        from core.composition_contract import build_stage_result

        result = dict(build_stage_result(stage="request_bundle", status="ok", output={"x": 1}))
        self.assertEqual(result["stage"], "request_bundle")
        self.assertEqual(result["status"], "ok")
        self.assertEqual(result["output"], {"x": 1})

    def test_composition_contract_module_has_no_subprocess_at_p1(self) -> None:
        """Verify the module contains no subprocess or CLI calls at P1."""
        module_path = ROOT_DIR / "core" / "composition_contract.py"
        source = module_path.read_text()
        self.assertNotIn("import subprocess", source)
        self.assertNotIn("def run_compose_chain", source)
        self.assertNotIn("import cli", source)

    def test_composition_contract_module_has_no_file_io_at_p1(self) -> None:
        """Verify the module contains no file write operations at P1."""
        module_path = ROOT_DIR / "core" / "composition_contract.py"
        source = module_path.read_text()
        self.assertNotIn("open(", source)
        self.assertNotIn("write_text", source)
        self.assertNotIn("mkdir", source)


class TestFeature202CliCompositionP2Implementation(unittest.TestCase):
    """Lock the P2 compose-chain command implementation."""

    def _run(self, cmd: list[str]) -> tuple[int, str, str]:
        result = subprocess.run(
            cmd, capture_output=True, text=True, cwd=ROOT_DIR,
        )
        return result.returncode, result.stdout, result.stderr

    def test_compose_chain_command_exits_zero_on_valid_fixture(self) -> None:
        rc, stdout, _ = self._run(["./atp", "compose-chain", FIXTURE])
        self.assertEqual(rc, 0)

    def test_compose_chain_output_is_valid_json(self) -> None:
        rc, stdout, _ = self._run(["./atp", "compose-chain", FIXTURE])
        self.assertEqual(rc, 0)
        data = json.loads(stdout)
        self.assertEqual(data["command"], "compose-chain")

    def test_compose_chain_reports_all_stages_complete(self) -> None:
        rc, stdout, _ = self._run(["./atp", "compose-chain", FIXTURE])
        self.assertEqual(rc, 0)
        data = json.loads(stdout)
        self.assertEqual(data["composition_status"], "all_stages_complete")

    def test_compose_chain_output_has_three_stages_in_order(self) -> None:
        rc, stdout, _ = self._run(["./atp", "compose-chain", FIXTURE])
        self.assertEqual(rc, 0)
        data = json.loads(stdout)
        stages = [s["stage"] for s in data["stages_executed"]]
        self.assertEqual(stages, ["request_flow", "request_bundle", "request_prompt"])

    def test_compose_chain_each_stage_has_ok_status(self) -> None:
        rc, stdout, _ = self._run(["./atp", "compose-chain", FIXTURE])
        self.assertEqual(rc, 0)
        data = json.loads(stdout)
        for stage in data["stages_executed"]:
            self.assertEqual(stage["status"], "ok", f"Stage {stage['stage']!r} not ok")

    def test_compose_chain_output_contains_composition_mode(self) -> None:
        rc, stdout, _ = self._run(["./atp", "compose-chain", FIXTURE])
        self.assertEqual(rc, 0)
        data = json.loads(stdout)
        self.assertIn("synchronous", data["composition_mode"])

    def test_compose_chain_exits_nonzero_on_missing_request_file(self) -> None:
        rc, _, _ = self._run(["./atp", "compose-chain", "nonexistent_file.yaml"])
        self.assertNotEqual(rc, 0)

    def test_compose_chain_halts_at_first_stage_failure(self) -> None:
        rc, stdout, _ = self._run(["./atp", "compose-chain", "nonexistent_file.yaml"])
        self.assertNotEqual(rc, 0)
        data = json.loads(stdout)
        self.assertEqual(data["composition_status"], "halted_at_stage_failure")
        self.assertEqual(data["fail_stage"], "request_flow")
        # Only stage 1 should have been attempted
        self.assertEqual(len(data["stages_executed"]), 1)

    def test_compose_chain_export_dir_writes_artifact(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            rc, _, _ = self._run(["./atp", "compose-chain", FIXTURE, "--export-dir", tmp])
            self.assertEqual(rc, 0)
            run_id = "compose-chain-0001"
            artifact = Path(tmp) / run_id / "request_prompt.json"
            manifest = Path(tmp) / run_id / "export_manifest.json"
            self.assertTrue(artifact.exists(), f"artifact not found: {artifact}")
            self.assertTrue(manifest.exists(), f"manifest not found: {manifest}")

    def test_atp_help_mentions_compose_chain(self) -> None:
        rc, stdout, _ = self._run(["./atp", "help"])
        self.assertEqual(rc, 0)
        self.assertIn("compose-chain", stdout)


class TestFeature202CliCompositionP3RegressionLocks(unittest.TestCase):
    """Regression locks — individual commands unchanged, no automation drift."""

    def _run(self, cmd: list[str]) -> tuple[int, str]:
        result = subprocess.run(
            cmd, capture_output=True, text=True, cwd=ROOT_DIR,
        )
        return result.returncode, result.stdout

    def test_request_flow_unchanged_after_compose_chain_added(self) -> None:
        rc, stdout = self._run(["python3", "cli/request_flow.py", FIXTURE])
        self.assertEqual(rc, 0)
        data = json.loads(stdout)
        self.assertEqual(data["status"], "ok")
        self.assertEqual(data["command"], "request-flow")

    def test_request_bundle_unchanged_after_compose_chain_added(self) -> None:
        rc, stdout = self._run(["python3", "cli/request_bundle.py", FIXTURE])
        self.assertEqual(rc, 0)
        data = json.loads(stdout)
        self.assertEqual(data["status"], "ok")
        self.assertEqual(data["command"], "request-bundle")

    def test_request_prompt_unchanged_after_compose_chain_added(self) -> None:
        rc, stdout = self._run(["python3", "cli/request_prompt.py", FIXTURE])
        self.assertEqual(rc, 0)
        data = json.loads(stdout)
        self.assertEqual(data["status"], "ok")
        self.assertEqual(data["command"], "request-prompt")

    def test_compose_chain_does_not_spawn_background_process(self) -> None:
        """Verify compose_chain.py source has no background spawn patterns."""
        module_path = ROOT_DIR / "cli" / "compose_chain.py"
        source = module_path.read_text()
        self.assertNotIn("threading", source)
        self.assertNotIn("asyncio", source)
        self.assertNotIn("multiprocessing", source)
        self.assertNotIn("Popen", source)

    def test_compose_chain_does_not_retry_on_failure(self) -> None:
        """Verify compose_chain.py source has no retry implementation patterns."""
        module_path = ROOT_DIR / "cli" / "compose_chain.py"
        source = module_path.read_text()
        # No retry loop or backoff logic
        self.assertNotIn("while True", source)
        self.assertNotIn("for attempt", source)
        self.assertNotIn("time.sleep", source)

    def test_composition_mode_constant_does_not_imply_automation(self) -> None:
        from core.composition_contract import COMPOSITION_MODE

        self.assertNotIn("auto", COMPOSITION_MODE)
        self.assertNotIn("background", COMPOSITION_MODE)
        self.assertNotIn("async", COMPOSITION_MODE)
        self.assertNotIn("retry", COMPOSITION_MODE)
        self.assertIn("human_initiated", COMPOSITION_MODE)

    def test_compose_chain_output_is_synchronous_signal(self) -> None:
        rc, stdout = self._run(["./atp", "compose-chain", FIXTURE])
        self.assertEqual(rc, 0)
        data = json.loads(stdout)
        self.assertIn("synchronous", data["composition_mode"])
        self.assertNotIn("async", data["composition_mode"])

    def test_smoke_chain_passes_after_compose_chain_added(self) -> None:
        result = subprocess.run(
            ["./atp", "smoke-request-chain"],
            capture_output=True, text=True, cwd=ROOT_DIR,
        )
        self.assertEqual(result.returncode, 0, f"Smoke chain failed:\n{result.stdout}\n{result.stderr}")


if __name__ == "__main__":
    unittest.main()
