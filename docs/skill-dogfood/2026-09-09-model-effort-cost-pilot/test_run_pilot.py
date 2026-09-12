"""Focused tests for the replay runner's publication boundary."""

from __future__ import annotations

import hashlib
import importlib.util
import io
import json
import subprocess
import sys
import tempfile
import unittest
import uuid
from contextlib import redirect_stdout
from pathlib import Path
from unittest import mock


RUNNER = Path(__file__).with_name("run_pilot.py")
SPEC = importlib.util.spec_from_file_location("run_pilot", RUNNER)
assert SPEC and SPEC.loader
run_pilot = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(run_pilot)


class RunPilotTest(unittest.TestCase):
    def test_main_hash_mismatch_does_not_call_claude(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            corpus = Path(directory) / "corpus.md"
            corpus.write_text("changed", encoding="utf-8")
            argv = [
                "run_pilot.py",
                "--model",
                "sonnet",
                "--effort",
                "low",
                "--replicate",
                "1",
            ]
            with (
                mock.patch.object(run_pilot, "CORPUS", corpus),
                mock.patch.object(run_pilot.subprocess, "run") as run,
                mock.patch.object(sys, "argv", argv),
                self.assertRaisesRegex(SystemExit, "corpus hash mismatch"),
            ):
                run_pilot.main()

            run.assert_not_called()

    def test_main_missing_required_flag_does_not_run_review(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            output_dir = Path(directory)
            corpus = output_dir / "corpus.md"
            corpus_bytes = b"frozen corpus"
            corpus.write_bytes(corpus_bytes)
            help_result = subprocess.CompletedProcess(
                args=["claude", "--help"],
                returncode=0,
                stdout=b"--model --output-format",
                stderr=b"",
            )
            argv = [
                "run_pilot.py",
                "--model",
                "sonnet",
                "--effort",
                "low",
                "--replicate",
                "1",
            ]

            with (
                mock.patch.object(run_pilot, "HERE", output_dir),
                mock.patch.object(run_pilot, "CORPUS", corpus),
                mock.patch.object(
                    run_pilot,
                    "EXPECTED_SHA256",
                    hashlib.sha256(corpus_bytes).hexdigest(),
                ),
                mock.patch.object(
                    run_pilot.subprocess, "run", return_value=help_result
                ) as run,
                mock.patch.object(sys, "argv", argv),
                self.assertRaisesRegex(SystemExit, "missing required flags"),
            ):
                run_pilot.main()

            run.assert_called_once()

    def test_main_success_persists_only_sanitized_publication_artifacts(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            output_dir = Path(directory)
            corpus = output_dir / "corpus.md"
            corpus_bytes = b"frozen corpus"
            corpus.write_bytes(corpus_bytes)
            session_id = uuid.UUID("12345678-1234-4234-9234-123456789abc")
            raw_stdout = json.dumps(
                {"session_id": str(session_id), "result": {"verdict": "ACCEPT"}}
            ).encode()
            completed = subprocess.CompletedProcess(
                args=["claude"], returncode=0, stdout=raw_stdout, stderr=b""
            )
            help_result = subprocess.CompletedProcess(
                args=["claude", "--help"],
                returncode=0,
                stdout=" ".join(run_pilot.REQUIRED_FLAGS).encode(),
                stderr=b"",
            )
            argv = [
                "run_pilot.py",
                "--model",
                "sonnet",
                "--effort",
                "low",
                "--replicate",
                "1",
            ]
            stdout = io.StringIO()

            with (
                mock.patch.object(run_pilot, "HERE", output_dir),
                mock.patch.object(run_pilot, "CORPUS", corpus),
                mock.patch.object(
                    run_pilot,
                    "EXPECTED_SHA256",
                    hashlib.sha256(corpus_bytes).hexdigest(),
                ),
                mock.patch.object(run_pilot.uuid, "uuid4", return_value=session_id),
                mock.patch.object(
                    run_pilot.subprocess,
                    "run",
                    side_effect=[help_result, completed],
                ),
                mock.patch.object(sys, "argv", argv),
                redirect_stdout(stdout),
            ):
                self.assertEqual(run_pilot.main(), 0)

            persisted = b"\n".join(
                path.read_bytes()
                for path in sorted(output_dir.glob("sonnet-low-r1.*"))
            )
            self.assertNotIn(str(session_id).encode(), persisted)
            self.assertNotIn(str(session_id), stdout.getvalue())
            metadata = json.loads(
                (output_dir / "sonnet-low-r1.metadata.json").read_text()
            )
            self.assertNotIn("session_id", metadata)


if __name__ == "__main__":
    unittest.main()
