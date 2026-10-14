"""Unit and CLI end-to-end checks for the honest offline status report."""

import io
import json
import os
import subprocess
import sys
import unittest
from contextlib import redirect_stdout
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def run_cli(*args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, "-m", "secure_agent_deployment_proof", *args],
        env={**os.environ, "PYTHONPATH": str(ROOT / "src")},
        text=True,
        capture_output=True,
        check=False,
        timeout=10,
    )


class StatusUnitTests(unittest.TestCase):
    def test_report_is_honest_and_independent(self) -> None:
        from secure_agent_deployment_proof.readiness import status_report

        first = status_report()
        self.assertEqual(first["status"], "scaffold")
        self.assertEqual(first["deployment_readiness"], "not_assessed")
        self.assertEqual(first["execution_mode"], "offline")
        self.assertEqual(first["implemented"], ["deterministic_status_cli"])
        self.assertEqual(
            first["not_implemented"],
            ["agent_workflow", "cloud_deployment", "oauth", "live_evals", "telemetry"],
        )
        first["implemented"].append("fake_cloud")
        self.assertEqual(status_report()["implemented"], ["deterministic_status_cli"])

    def test_main_returns_zero_and_json_is_report(self) -> None:
        from secure_agent_deployment_proof.cli import main
        from secure_agent_deployment_proof.readiness import status_report

        output = io.StringIO()
        with redirect_stdout(output):
            result = main(["status", "--format", "json"])
        self.assertEqual(result, 0)
        self.assertEqual(json.loads(output.getvalue()), status_report())


class StatusEndToEndTests(unittest.TestCase):
    def test_json_output_is_deterministic_and_truthful(self) -> None:
        first = run_cli("status", "--format", "json")
        second = run_cli("status", "--format", "json")
        self.assertEqual(first.returncode, 0, first.stderr)
        self.assertEqual(first.stdout, second.stdout)
        self.assertEqual(first.stderr, "")
        self.assertEqual(json.loads(first.stdout)["deployment_readiness"], "not_assessed")

    def test_default_text_explains_limits(self) -> None:
        result = run_cli("status")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("Status: scaffold", result.stdout)
        self.assertIn("Deployment readiness: not_assessed", result.stdout)
        self.assertIn("cloud_deployment", result.stdout)

    def test_invalid_arguments_fail_without_status_output(self) -> None:
        for args in [
            [],
            ["deploy"],
            ["status", "--format", "yaml"],
            ["status", "--token", "do-not-echo-this"],
        ]:
            with self.subTest(args=args):
                result = run_cli(*args)
                self.assertEqual(result.returncode, 2, result.stderr)
                self.assertEqual(result.stdout, "")
                self.assertIn("error:", result.stderr)
                self.assertNotIn("do-not-echo-this", result.stderr)

    def test_help_is_available(self) -> None:
        result = run_cli("--help")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("status", result.stdout)


class InProcessCliTests(unittest.TestCase):
    def test_text_path(self) -> None:
        from secure_agent_deployment_proof.cli import main

        output = io.StringIO()
        with redirect_stdout(output):
            self.assertEqual(main(["status"]), 0)
        self.assertIn("Status: scaffold", output.getvalue())

    def test_invalid_arguments_exit_two(self) -> None:
        from contextlib import redirect_stderr

        from secure_agent_deployment_proof.cli import main

        with redirect_stderr(io.StringIO()), self.assertRaises(SystemExit) as caught:
            main(["status", "--format", "xml"])
        self.assertEqual(caught.exception.code, 2)

    def test_module_entrypoint(self) -> None:
        import runpy
        from unittest.mock import patch

        with patch.object(sys, "argv", ["secure-agent-proof", "status"]):
            with redirect_stdout(io.StringIO()), self.assertRaises(SystemExit) as caught:
                runpy.run_module("secure_agent_deployment_proof", run_name="__main__")
        self.assertEqual(caught.exception.code, 0)
