"""Offline guards for the shared lock-refresh workflow; no Poetry or cloud calls."""

import os
from pathlib import Path
import subprocess
import sys
import tempfile
import textwrap
import unittest

WORKFLOW = (
    Path(__file__).resolve().parents[1] / ".github/workflows/poetry-lock-refresh.yml"
)
INDEX = (
    "https://synthetic-region-python.pkg.dev/synthetic-project/synthetic-index/simple/"
)
VERSION = "0.63.3"


def guard_script(step):
    section = WORKFLOW.read_text().split(f"- name: {step}\n", 1)[1]
    script = section.split("python - <<'PYCODE'\n", 1)[1].split(
        "\n          PYCODE", 1
    )[0]
    return textwrap.dedent(script)


class LockRefreshGuards(unittest.TestCase):
    """Exercise the real inline guards with synthetic files and no cloud access."""

    def run_guard(self, step, filename, content, **overrides):
        with tempfile.TemporaryDirectory() as directory:
            Path(directory, filename).write_text(content)
            env = dict(
                os.environ, EXPECTED_QUIRE_VERSION=VERSION, EXTRA_INDEX_URL=INDEX
            )
            env.update(overrides)
            return subprocess.run(
                [sys.executable, "-c", guard_script(step)],
                cwd=directory,
                env=env,
                text=True,
                capture_output=True,
                check=False,
            )

    def source(self, constraint="^0.63.3", source_url=INDEX):
        return (
            "[tool.poetry.group.dev.dependencies]\n"
            f'quire = {{version = "{constraint}", source = "internal-pypi"}}\n'
            '[[tool.poetry.source]]\nname = "internal-pypi"\n'
            f'url = "{source_url}"\n'
        )

    def lock(self, version=VERSION, url=INDEX, reference="internal-pypi", extra=""):
        return (
            '[[package]]\nname = "quire"\n'
            f'version = "{version}"\n'
            '[package.source]\ntype = "legacy"\n'
            f'url = "{url}"\nreference = "{reference}"\n' + extra
        )

    def test_source_guard_accepts_the_reviewed_constraint_and_existing_source(self):
        """Description: Check source admission before any cloud authentication.

        Assumptions: Synthetic project metadata; no credentials or index requests.
        Criteria: Only the reviewed release constraint and source are admitted.
        Trace: FR-001-AC-1
        """
        result = self.run_guard(
            "Check the reviewed branch constraint and package source",
            "pyproject.toml",
            self.source(),
        )
        self.assertEqual(result.returncode, 0, result.stderr)

    def test_source_guard_rejects_wrong_constraint_and_mismatched_source(self):
        """Description: Check source admission before any cloud authentication.

        Assumptions: Synthetic project metadata; no credentials or index requests.
        Criteria: Only the reviewed release constraint and source are admitted.
        Trace: FR-001-AC-1
        """
        for source, message in [
            (self.source(constraint="^0.50.0"), "reviewed Quire constraint"),
            (
                self.source(source_url="https://example.invalid/simple/"),
                "match the existing",
            ),
        ]:
            with self.subTest(message=message):
                result = self.run_guard(
                    "Check the reviewed branch constraint and package source",
                    "pyproject.toml",
                    source,
                )
                self.assertNotEqual(result.returncode, 0)
                self.assertIn(message, result.stderr)

    def test_lock_guard_accepts_the_expected_release_and_source(self):
        """Description: Check the actual generated-lock guard with synthetic locks.

        Assumptions: Lock metadata is local and carries no real credentials.
        Criteria: Only the approved release/source and safe dependency URLs pass.
        Trace: FR-001-AC-4
        """
        result = self.run_guard(
            "Refresh only the selected dependency lock",
            "poetry.lock",
            self.lock(),
        )
        self.assertEqual(result.returncode, 0, result.stderr)

    def test_lock_guard_refuses_version_source_and_credential_drift(self):
        """Description: Check the actual generated-lock guard with synthetic locks.

        Assumptions: Lock metadata is local and carries no real credentials.
        Criteria: Only the approved release/source and safe dependency URLs pass.
        Trace: FR-001-AC-4
        """
        for lock, message in [
            (self.lock(version="0.63.2"), "exactly the approved"),
            (self.lock(reference="unreviewed-source"), "differs from"),
            (
                self.lock(
                    extra='\n[[package]]\nname = "synthetic-dependency"\nversion = "1.0.0"\n[package.source]\nurl = "https://synthetic-user:synthetic-password@example.invalid/repo"\n'
                ),
                "credential-bearing",
            ),
        ]:
            with self.subTest(message=message):
                result = self.run_guard(
                    "Refresh only the selected dependency lock",
                    "poetry.lock",
                    lock,
                )
                self.assertNotEqual(result.returncode, 0)
                self.assertIn(message, result.stderr)

    def test_source_guard_rejects_invalid_version_foreign_and_credential_urls(self):
        """Description: Refuse invalid inputs before authentication.

        Assumptions: Synthetic versions and URLs; no network operation.
        Criteria: Version syntax and index credential/host boundaries are enforced.
        Trace: FR-001-AC-1
        """
        result = self.run_guard(
            "Check the reviewed branch constraint and package source",
            "pyproject.toml",
            self.source(),
            EXPECTED_QUIRE_VERSION="unreleased",
        )
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("exact stable release", result.stderr)
        for url in [
            "https://example.invalid/simple/",
            "https://synthetic-user:synthetic-password@synthetic-python.pkg.dev/project/index/simple/",
        ]:
            with self.subTest(url=url):
                result = self.run_guard(
                    "Check the reviewed branch constraint and package source",
                    "pyproject.toml",
                    self.source(source_url=url),
                    EXTRA_INDEX_URL=url,
                )
                self.assertNotEqual(result.returncode, 0)
                self.assertIn("credential-free Artifact Registry", result.stderr)


if __name__ == "__main__":
    unittest.main()
