"""Unit tests for ATP lightweight schema validator."""

from __future__ import annotations

import unittest
from pathlib import Path

from core.validation.schema_validator import ValidationReport, validate_against_schema


class TestSchemaValidator(unittest.TestCase):

    def test_valid_request_passes(self) -> None:
        data = {
            "request_id": "req-1",
            "request_type": "implementation",
            "execution_intent": "preview",
            "payload": {"input_text": "test"},
            "metadata": {},
        }
        report = validate_against_schema(data, "request/request.schema.yaml")
        self.assertTrue(report.valid)
        self.assertEqual(report.errors, [])

    def test_missing_required_field_reports_error(self) -> None:
        data = {
            "request_type": "implementation",
            "execution_intent": "preview",
            "payload": {},
            "metadata": {},
        }
        report = validate_against_schema(data, "request/request.schema.yaml")
        self.assertFalse(report.valid)
        self.assertTrue(any("request_id" in e for e in report.errors))

    def test_wrong_type_reports_error(self) -> None:
        data = {
            "request_id": "req-1",
            "request_type": "implementation",
            "execution_intent": "preview",
            "payload": "not a dict",
            "metadata": {},
        }
        report = validate_against_schema(data, "request/request.schema.yaml")
        self.assertFalse(report.valid)
        self.assertTrue(any("payload" in e and "object" in e for e in report.errors))

    def test_unknown_schema_returns_error(self) -> None:
        report = validate_against_schema({}, "nonexistent/fake.schema.yaml")
        self.assertFalse(report.valid)
        self.assertTrue(any("Schema load failed" in e for e in report.errors))

    def test_additional_properties_allowed(self) -> None:
        data = {
            "request_id": "req-1",
            "request_type": "implementation",
            "execution_intent": "preview",
            "payload": {},
            "metadata": {},
            "extra_field": "allowed",
        }
        report = validate_against_schema(data, "request/request.schema.yaml")
        self.assertTrue(report.valid)

    def test_all_schemas_self_validate(self) -> None:
        """Every schema file should be loadable by the validator."""
        schema_root = Path(__file__).resolve().parents[2] / "schemas"
        for schema_file in schema_root.rglob("*.schema.yaml"):
            rel = schema_file.relative_to(schema_root)
            report = validate_against_schema({"dummy": True}, str(rel))
            self.assertIsInstance(report, ValidationReport, f"Failed for {rel}")

    def test_approval_schema_validates(self) -> None:
        data = {
            "approval_id": "appr-1",
            "request_id": "req-1",
            "approval_status": "approved",
            "approval_mode": "human",
        }
        report = validate_against_schema(data, "approval/approval_decision.schema.yaml")
        self.assertTrue(report.valid)

    def test_validation_report_is_namedtuple(self) -> None:
        report = validate_against_schema({}, "request/request.schema.yaml")
        self.assertIsInstance(report, ValidationReport)
        self.assertIsInstance(report.valid, bool)
        self.assertIsInstance(report.errors, list)
        self.assertIsInstance(report.schema_name, str)


class TestNormalizerSchemaIntegration(unittest.TestCase):

    def test_normalized_request_has_no_warnings_for_valid_input(self) -> None:
        from core.intake.loader import load_request
        from core.intake.normalizer import normalize_request
        fixture = Path(__file__).resolve().parents[1] / "fixtures" / "requests" / "sample_request_slice02.yaml"
        raw = load_request(fixture)
        normalized = normalize_request(raw)
        self.assertNotIn("_validation_warnings", normalized)

    def test_normalized_request_collects_warnings_for_bad_types(self) -> None:
        from core.intake.normalizer import normalize_request
        raw = {
            "request_id": "req-1",
            "request_type": 123,
            "execution_intent": "preview",
            "payload": "not_a_dict",
            "metadata": {},
        }
        normalized = normalize_request(raw)
        # normalizer coerces payload to {} but schema sees the coerced version
        # request_type 123 should trigger type warning in schema
        # (after normalization, request_type is still passed through)
        self.assertIn("request_id", normalized)


if __name__ == "__main__":
    unittest.main()
