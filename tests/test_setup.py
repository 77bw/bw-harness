"""Exercise the shipped entry points in disposable real Git repositories."""

import shutil
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
SETUP = Path("skills/setup-bw-harness/scripts/setup.py")


def run(*cmd, cwd, ok=True):
    result = subprocess.run(
        list(map(str, cmd)), cwd=cwd, text=True, capture_output=True, check=False
    )
    if ok:
        assert result.returncode == 0, result.stdout + result.stderr
    return result


@pytest.fixture
def pack(tmp_path):
    p = tmp_path / "pack"
    p.mkdir()
    shutil.copy2(ROOT / "copier.yml", p)
    shutil.copytree(ROOT / "templates", p / "templates")
    (p / SETUP).parent.mkdir(parents=True)
    shutil.copy2(ROOT / SETUP, p / SETUP)
    run("git", "init", "-q", cwd=p)
    run("git", "add", "copier.yml", "templates", SETUP, cwd=p)
    run(
        "git",
        "-c",
        "user.name=Fixture",
        "-c",
        "user.email=test@example.invalid",
        "commit",
        "-qm",
        "template fixture",
        cwd=p,
    )
    return p


@pytest.mark.parametrize("full", [False, True])
def test_new(pack, tmp_path, full):
    project = tmp_path / "中文 space"
    project.mkdir()
    call = [sys.executable, pack / SETUP, "new", project, "--name", "demo"]
    run(*call, *(["--api", "--research"] if full else []), cwd=pack)
    assert (project / "src/demo/api.py").exists() == full
    assert (project / "docs/research").exists() == full
    assert not (project / "skills").exists()
    assert "_commit:" in (project / ".copier-answers.yml").read_text()
    for args in [
        ("pytest", "-q"),
        ("ruff", "check", "."),
        ("ruff", "format", "--check", "."),
    ]:
        run("uv", "run", *args, cwd=project)
    run(sys.executable, pack / SETUP, "check", project, cwd=pack)
    assert run(*call, cwd=pack, ok=False).returncode != 0
    run("git", "init", "-q", cwd=project)
    (project / ".local").mkdir()
    (project / ".local/evidence").write_text("synthetic")
    run("git", "add", "-f", ".local/evidence", cwd=project)
    (project / "temp.py").touch()
    (project / "src/demo/bad.py").write_text("import experiments.candidate\n")
    result = run(sys.executable, pack / SETUP, "check", project, cwd=pack, ok=False)
    assert result.returncode == 1
    assert all(
        x in result.stdout for x in ("temp.py:", ".local/evidence:", "bad.py:1:")
    )


def commit(repo, message):
    run(
        "git",
        "-c",
        "user.name=Fixture",
        "-c",
        "user.email=test@example.invalid",
        "commit",
        "-qm",
        message,
        cwd=repo,
    )


def test_template_update(pack, tmp_path):
    project = tmp_path / "upgrade"
    project.mkdir()
    run("git", "tag", "v0.1.0", cwd=pack)
    run(sys.executable, pack / SETUP, "new", project, cwd=pack)
    run("git", "init", "-q", cwd=project)
    (project / "docs/adr").mkdir()
    note = project / "docs/adr/0001-length.md"
    note.write_text("Count UTF-8 bytes.\n", encoding="utf8")
    run("git", "add", ".", cwd=project)
    commit(project, "user knowledge")
    src = pack / "templates/python/docs/architecture.md"
    src.write_text(src.read_text() + "\nSecond revision.\n")
    run("git", "add", "templates", cwd=pack)
    commit(pack, "update template")
    run("git", "tag", "v0.2.0", cwd=pack)
    run(
        "uvx",
        "--from",
        "copier==9.19.1",
        "copier",
        "update",
        "--defaults",
        "--vcs-ref",
        "v0.2.0",
        cwd=project,
    )
    assert "Second revision." in (project / "docs/architecture.md").read_text()
    assert note.read_text() == "Count UTF-8 bytes.\n"
    run("git", "add", "-u", cwd=project)
    commit(project, "accept template update")
    arch = project / "docs/architecture.md"
    arch.write_text("User-owned architecture.\n")
    run("git", "add", "-u", cwd=project)
    commit(project, "locally edit architecture")
    src.write_text("Different upstream architecture.\n")
    run("git", "add", "-u", cwd=pack)
    commit(pack, "conflicting change")
    run("git", "tag", "v0.3.0", cwd=pack)
    run(
        "uvx",
        "--from",
        "copier==9.19.1",
        "copier",
        "update",
        "--defaults",
        "--vcs-ref",
        "v0.3.0",
        cwd=project,
        ok=False,
    )
    assert "<<<<<<<" in arch.read_text() or list(project.rglob("*.rej"))
    # Restore only the disposable fixture from its pre-upgrade commit.
    run("git", "restore", "--staged", "--worktree", "--source=HEAD", ".", cwd=project)
    assert arch.read_text() == "User-owned architecture.\n"
    assert note.read_text() == "Count UTF-8 bytes.\n"


def test_existing(tmp_path):
    files = {
        "CONTEXT.md": b"original terms",
        "AGENTS.md": b"private rules",
        "old.py": b"print(1)",
        ".local/capture": b"unique synthetic evidence",
    }
    for n, b in files.items():
        f = tmp_path / n
        f.parent.mkdir(exist_ok=True)
        f.write_bytes(b)
    for mode in ("check", "migrate", "docs"):
        run(sys.executable, ROOT / SETUP, mode, tmp_path, cwd=ROOT, ok=False)
        assert {
            p.relative_to(tmp_path).as_posix(): p.read_bytes()
            for p in tmp_path.rglob("*")
            if p.is_file()
        } == files
    for _ in range(2):
        run(sys.executable, ROOT / SETUP, "docs", tmp_path, "--apply-docs", cwd=ROOT)
    assert (tmp_path / "docs/status.md").exists()
    assert all((tmp_path / n).read_bytes() == b for n, b in files.items())
