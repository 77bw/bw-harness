"""A missing conditional route must identify its caller, not just a checksum."""

import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_missing_prototype(tmp_path):
    # Copy the validator and its inputs; never move files from a live install.
    for name in ("skills", "scripts", "guides", "licenses", ".pi"):
        shutil.copytree(ROOT / name, tmp_path / name)
    for name in ("README.md", "LICENSE", "package.json", "upstream.lock.yml"):
        shutil.copy2(ROOT / name, tmp_path / name)
    shim = tmp_path / "node_modules/pi-subagents/index.js"
    shim.parent.mkdir(parents=True)
    shim.touch()  # Only the extension presence check is exercised in this fixture.
    cmd = [sys.executable, str(tmp_path / "scripts/validate-package.py")]
    assert subprocess.run(cmd, check=False, capture_output=True).returncode == 0
    shutil.rmtree(tmp_path / "skills/ce-prototype")
    result = subprocess.run(cmd, check=False, capture_output=True, text=True)
    assert result.returncode == 1
    assert "ce-brainstorm -> missing skill ce-prototype" in result.stdout
