"""Exercise the shipped ignore seed with Git itself, independently of model pilots."""

import re
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_ignore_protections_do_not_remove_existing_evidence(tmp_path):
    def git(*args):
        return subprocess.run(
            ["git", *args], cwd=tmp_path, check=False, capture_output=True, text=True
        )

    assert git("init", "-q").returncode == 0
    (tmp_path / ".local").mkdir()
    evidence = tmp_path / ".local/唯一证据"
    evidence.write_text("synthetic", encoding="utf-8")
    assert git("add", "-f", "--", ".local").returncode == 0
    original_index = git("ls-files", "--stage", "-z").stdout
    seed = (ROOT / "skills/setup-bw-harness/gitignore.md").read_text(encoding="utf-8")
    block = re.search(r"```gitignore\n(.*?)\n```", seed, re.DOTALL)[1]
    (tmp_path / ".gitignore").write_text("user-wip/\n" + block + "\n", encoding="utf-8")
    for path in (
        ".local/tmp",
        ".context/compound-engineering/run/output",
        ".compound-engineering/config.local.yaml",
        ".env",
        ".env.production",
        "a.har",
        "a.pcapng",
        "user-wip/draft",
    ):
        assert git("check-ignore", "-q", "--no-index", "--", path).returncode == 0, path
    for path in (
        ".env.example",
        ".compound-engineering/config.yaml",
        "docs/research/协议.md",
        "main.py",
        "src.js",
    ):
        assert git("check-ignore", "-q", "--no-index", "--", path).returncode == 1, path
    assert git("ls-files", "--stage", "-z").stdout == original_index
    assert evidence.read_text(encoding="utf-8") == "synthetic"


def test_compound_validates_real_solution_path(tmp_path):
    """Host regression: this command previously crashed before reading the solution on Python 3.9."""
    import sys

    subprocess.run(["git", "init", "-q"], cwd=tmp_path, check=True)
    (tmp_path / "library").mkdir()
    (tmp_path / "library/count.py").write_text("answer = 3\n", encoding="utf-8")
    doc = tmp_path / "solution.md"
    doc.write_text(
        "The verified result is in `library/count.py:1`.\n", encoding="utf-8"
    )
    script = ROOT / "skills/ce-compound/scripts/validate-doc-claims.py"
    cmd = [sys.executable, script, doc]
    subprocess.run(cmd, cwd=tmp_path, check=True)
    doc.write_text("The result is in `library/count.py:82`.\n", encoding="utf-8")
    bad = subprocess.run(
        cmd, cwd=tmp_path, capture_output=True, encoding="utf-8", check=False
    )
    assert bad.returncode == 1 and "library/count.py" in bad.stdout
