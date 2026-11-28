"""Negative controls for the actual shipped graph. No model runs are simulated."""

import shutil
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]


@pytest.fixture
def pack(tmp_path):
    for name in (
        "skills",
        "scripts",
        "guides",
        "patches",
        "licenses",
        ".pi",
        ".codex-plugin",
        ".claude-plugin",
    ):
        shutil.copytree(ROOT / name, tmp_path / name)
    for name in (
        "AGENTS.md",
        "CHANGELOG.md",
        "README.md",
        "LICENSE",
        "package.json",
        "package-lock.json",
        "upstream.lock.yml",
    ):
        shutil.copy2(ROOT / name, tmp_path / name)
    shim = tmp_path / "node_modules/pi-subagents/index.js"
    shim.parent.mkdir(parents=True)
    shim.touch()  # Only extension existence is tested; no claim of host installation.
    assert validate(tmp_path).returncode == 0
    return tmp_path


def validate(path):
    return subprocess.run(
        [sys.executable, str(path / "scripts/validate-package.py")],
        check=False,
        capture_output=True,
        text=True,
        encoding="utf-8",
    )


def test_missing_menu_target_identifies_caller(pack):
    shutil.rmtree(pack / "skills/ce-prototype")
    result = validate(pack)
    assert (
        result.returncode
        and "ce-brainstorm -> missing skill ce-prototype" in result.stdout
    )


def test_excluded_name_is_not_a_free_pass(pack):
    file = pack / "skills/ce-setup/references/config-template-lines.txt"
    with file.open("a", encoding="utf-8") as f:
        f.write("\n现在调用ce-sweep继续。\n")
    result = validate(pack)
    assert result.returncode and "ce-setup -> missing skill ce-sweep" in result.stdout


def test_missing_reachable_reference(pack):
    (pack / "skills/ce-work/references/shipping-workflow.md").unlink()
    result = validate(pack)
    assert (
        result.returncode
        and "missing skill resource references/shipping-workflow.md" in result.stdout
    )


def test_broken_guide_link_and_encoding(pack):
    doc = pack / "guides/skills/bw-help.md"
    with doc.open("a", encoding="utf-8") as f:
        f.write("\n[坏链接](absent.md)\n")
    assert "broken link absent.md" in validate(pack).stdout
    doc.write_bytes(b"\xff")
    assert validate(pack).returncode != 0


def test_missing_cross_skill_plain_text_reference(pack):
    doc = pack / "skills/bw-help/SKILL.md"
    with doc.open("a", encoding="utf-8") as f:
        f.write("\nRead `ce-work/references/absent.md` before routing.\n")
    assert (
        "missing skill resource ce-work/references/absent.md" in validate(pack).stdout
    )
