"""Exercise fixed-object replay with real commits, disposable clones and a real patch."""

import json
import os
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from package_checks import digest, inside

PATCH = """diff --git a/skills/fixture/SKILL.md b/skills/fixture/SKILL.md
--- a/skills/fixture/SKILL.md
+++ b/skills/fixture/SKILL.md
@@ -1 +1 @@
-original
+adapted
"""


def git(repo, *args):
    return subprocess.check_output(
        [
            "git",
            "-c",
            "user.name=Fixture",
            "-c",
            "user.email=test@example.invalid",
            *args,
        ],
        cwd=repo,
    )


@pytest.fixture
def trees(tmp_path):
    root, cache = tmp_path / "包 中文", tmp_path / "cache"
    root.mkdir()
    import shutil

    shutil.copytree(ROOT / "scripts", root / "scripts")
    lock = {}
    for key in ("matt", "ce"):
        repo = cache / key
        (repo / "source").mkdir(parents=True)
        (repo / "source/SKILL.md").write_bytes(b"original\n")
        git(repo, "init", "-q")
        git(repo, "add", "source")
        git(repo, "commit", "-qm", "pinned fixture")
        rev = git(repo, "rev-parse", "HEAD").decode().strip()
        lock[key] = {
            "url": "unused",
            "commit": rev,
            "skill_catalog": ["fixture"],
            "resources": {},
        }
    target = root / "skills/fixture"
    target.mkdir(parents=True)
    (target / "SKILL.md").write_bytes(b"adapted\n")
    patch = root / "patches/matt/fixture.patch"
    patch.parent.mkdir(parents=True)
    patch.write_bytes(PATCH.encode())
    lock["matt"]["resources"]["skills/fixture"] = {
        "source": "source",
        "upstream_sha256": digest(cache / "matt/source"),
        "sha256": digest(target),
        "patch": "patches/matt/fixture.patch",
        "requires": [],
        "executables": [],
    }
    (root / "upstream.lock.yml").write_bytes(json.dumps(lock).encode())
    return root, cache


def sync(trees, *args):
    root, cache = trees
    return subprocess.run(
        [sys.executable, root / "scripts/sync-upstream.py", "--cache", cache, *args],
        check=False,
        capture_output=True,
        text=True,
        encoding="utf-8",
    )


def test_replay_from_immutable_objects_and_drift(trees):
    root, cache = trees
    (cache / "matt/source/SKILL.md").write_bytes(b"dirty cache copy\n")
    assert sync(trees).returncode == 0
    skill = root / "skills/fixture/SKILL.md"
    skill.write_bytes(b"user work\n")
    assert sync(trees).returncode != 0 and skill.read_bytes() == b"user work\n"
    assert (
        sync(trees, "--apply").returncode != 0 and skill.read_bytes() == b"user work\n"
    )
    skill.write_bytes(b"original\n")
    assert sync(trees, "--apply").returncode == 0 and skill.read_bytes() == b"adapted\n"


def test_failed_patch_does_not_touch_destination_or_lock(trees):
    root, cache = trees
    # This missing first resource is valid and queued for restoration. A bad
    # patch on the second resource must not leave a partially restored pack.
    lock_path = root / "upstream.lock.yml"
    metadata = json.loads(lock_path.read_bytes())
    checksum = digest(cache / "matt/source/SKILL.md")
    queued = "licenses/fixture-note"
    metadata["matt"]["resources"] = {
        queued: {
            "source": "source/SKILL.md",
            "upstream_sha256": checksum,
            "sha256": checksum,
            "executables": [],
        },
        **metadata["matt"]["resources"],
    }
    lock_path.write_bytes(json.dumps(metadata).encode())
    path = root / "patches/matt/fixture.patch"
    path.write_bytes(path.read_bytes().replace(b"-original", b"-WRONG"))
    lock = (root / "upstream.lock.yml").read_bytes()
    result = sync(trees, "--apply")
    assert result.returncode != 0 and "patch" in result.stderr
    assert queued in result.stdout and not (root / queued).exists()
    assert (root / "skills/fixture/SKILL.md").read_bytes() == b"adapted\n"
    assert (root / "upstream.lock.yml").read_bytes() == lock


@pytest.mark.skipif(
    os.name == "nt",
    reason="Git patch authoring preserves POSIX modes; verify/replay runs everywhere",
)
def test_explicit_record_is_replayable(trees):
    root, _ = trees
    skill = root / "skills/fixture/SKILL.md"
    skill.write_text("新的能力\n", encoding="utf-8")
    assert sync(trees, "--record", "skills/fixture").returncode == 0
    assert sync(trees).returncode == 0
    skill.unlink()
    skill.parent.rmdir()
    assert (
        sync(trees, "--apply").returncode == 0
        and skill.read_text(encoding="utf-8") == "新的能力\n"
    )


@pytest.mark.parametrize(
    "name", ("../outside", ".git/config", "C:/outside", "/abs", r"a\..\b")
)
def test_unsafe_paths_rejected(tmp_path, name):
    with pytest.raises(ValueError):
        inside(tmp_path, name)


def test_apply_upgrades_only_exact_last_committed_distribution(trees):
    root, _ = trees
    skill = root / "skills/fixture/SKILL.md"
    lock = root / "upstream.lock.yml"
    wanted = lock.read_bytes()
    old = json.loads(wanted)
    skill.write_bytes(b"previous distributed patch\n")
    old["matt"]["resources"]["skills/fixture"]["sha256"] = digest(skill.parent)
    lock.write_bytes(json.dumps(old).encode())
    git(root, "init", "-q")
    git(root, "add", "upstream.lock.yml", "skills")
    git(root, "commit", "-qm", "reviewed older distribution")
    lock.write_bytes(wanted)
    before = skill.read_bytes()
    skill.write_bytes(before + b"uncommitted custom notes\n")
    assert sync(trees, "--apply").returncode
    assert skill.read_bytes() == before + b"uncommitted custom notes\n"
    skill.write_bytes(before)
    assert sync(trees, "--apply").returncode == 0
    assert skill.read_bytes() == b"adapted\n"


@pytest.mark.skipif(
    os.name == "nt", reason="Native Windows checkout lacks POSIX executable metadata"
)
def test_apply_does_not_erase_chmod_only_local_change(trees):
    root, _ = trees
    skill = root / "skills/fixture/SKILL.md"
    skill.write_bytes(b"original\n")
    skill.chmod(0o755)
    assert sync(trees, "--apply").returncode
    assert skill.stat().st_mode & 0o111 and skill.read_bytes() == b"original\n"
