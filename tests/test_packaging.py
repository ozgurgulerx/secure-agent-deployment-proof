"""Verify the installed artifact outside the checkout, without runtime deps."""

import json
import os
import subprocess
import sys
import tempfile
import unittest
import venv
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


class InstalledArtifactTests(unittest.TestCase):
    def test_built_wheel_console_and_module_match(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            temporary = Path(directory)
            clean_env = {key: value for key, value in os.environ.items() if key != "PYTHONPATH"}
            wheels = temporary / "wheels"
            subprocess.run(
                [
                    sys.executable,
                    "-m",
                    "build",
                    "--wheel",
                    "--no-isolation",
                    "--outdir",
                    str(wheels),
                    str(ROOT),
                ],
                check=True,
                capture_output=True,
                text=True,
                timeout=120,
            )
            environment = temporary / "venv"
            venv.create(environment, with_pip=True)
            python = environment / "bin" / "python"
            subprocess.run(
                [
                    str(python),
                    "-m",
                    "pip",
                    "install",
                    "--no-index",
                    "--no-deps",
                    str(next(wheels.glob("*.whl"))),
                ],
                check=True,
                capture_output=True,
                text=True,
                cwd=temporary,
                env=clean_env,
                timeout=60,
            )
            outputs = []
            for command in [
                [str(environment / "bin" / "secure-agent-proof")],
                [str(python), "-m", "secure_agent_deployment_proof"],
            ]:
                result = subprocess.run(
                    [*command, "status", "--format", "json"],
                    cwd=temporary,
                    env=clean_env,
                    check=True,
                    capture_output=True,
                    text=True,
                    timeout=10,
                )
                outputs.append(result.stdout)
            self.assertEqual(outputs[0], outputs[1])
            self.assertEqual(json.loads(outputs[0])["status"], "scaffold")
