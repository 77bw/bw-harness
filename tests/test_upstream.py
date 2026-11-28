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


def load_sync(trees):
    import importlib.util

    root, _ = trees
    spec = importlib.util.spec_from_file_location(
        "fixture_replay", root / "scripts/sync-upstream.py"
    )
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


@pytest.mark.parametrize("initial", ("missing", "pristine"))
def test_apply_rechecks_earlier_destination_after_later_repo_fetch(
    trees, monkeypatch, initial
):
    root, cache = trees
    module = load_sync(trees)
    target = root / "skills/fixture"
    if initial == "missing":
        (target / "SKILL.md").unlink()
        target.rmdir()
    else:
        (target / "SKILL.md").write_bytes(b"original\n")
    real_git = module.git

    def later_git(repo, *args):
        if repo == cache / "ce" and args[:1] == ("rev-parse",):
            target.mkdir(exist_ok=True)
            (target / "private-note").write_bytes(b"new user knowledge\n")
        return real_git(repo, *args)

    monkeypatch.setattr(module, "git", later_git)
    with pytest.raises(ValueError, match="changed"):
        module.main(["--cache", str(cache), "--apply"], root=root)
    assert (target / "private-note").read_bytes() == b"new user knowledge\n"
    if initial == "missing":
        assert not (target / "SKILL.md").exists()
    else:
        assert (target / "SKILL.md").read_bytes() == b"original\n"


@pytest.mark.skipif(os.name == "nt", reason="requires POSIX symbolic links")
def test_apply_revalidates_destination_parent(trees, monkeypatch, tmp_path):
    root, cache = trees
    module = load_sync(trees)
    target = root / "skills/fixture/SKILL.md"
    target.write_bytes(b"original\n")
    external = tmp_path / "external"
    real_git = module.git

    def later_git(repo, *args):
        if repo == cache / "ce" and args[:1] == ("rev-parse",):
            (root / "skills").rename(external)
            (root / "skills").symlink_to(external, target_is_directory=True)
        return real_git(repo, *args)

    monkeypatch.setattr(module, "git", later_git)
    with pytest.raises(ValueError, match="symlink"):
        module.main(["--cache", str(cache), "--apply"], root=root)
    assert (external / "fixture/SKILL.md").read_bytes() == b"original\n"


def test_changed_displaced_tree_is_restored(trees, monkeypatch):
    root, cache = trees
    module = load_sync(trees)
    target = root / "skills/fixture"
    (target / "SKILL.md").write_bytes(b"original\n")
    original_rename = Path.rename

    def during_move(source, destination):
        if source == target:
            (source / "SKILL.md").write_bytes(b"uncommitted late edit\n")
        return original_rename(source, destination)

    monkeypatch.setattr(Path, "rename", during_move)
    with pytest.raises(ValueError, match="changed during replacement"):
        module.main(["--cache", str(cache), "--apply"], root=root)
    assert (target / "SKILL.md").read_bytes() == b"uncommitted late edit\n"


def test_exclusive_install_keeps_racing_empty_target_and_recoverable_backup(
    trees, monkeypatch
):
    root, cache = trees
    module = load_sync(trees)
    target = root / "skills/fixture"
    (target / "SKILL.md").write_bytes(b"original\n")
    original_rename = module.rename_new

    def during_install(source, destination):
        if source.name == "candidate":
            # POSIX plain rename would replace this newly created, empty directory.
            target.mkdir()
        original_rename(source, destination)

    monkeypatch.setattr(module, "rename_new", during_install)
    with pytest.raises(ValueError, match="recover the displaced resource"):
        module.main(["--cache", str(cache), "--apply"], root=root)
    assert list(target.iterdir()) == []
    backups = list((root / ".local/upstream-backups").glob("*/fixture/SKILL.md"))
    assert len(backups) == 1 and backups[0].read_bytes() == b"original\n"


@pytest.mark.skipif(os.name == "nt", reason="open files use Windows sharing modes")
def test_writer_with_open_descriptor_retains_its_late_edit_in_backup(trees):
    root, _ = trees
    target = root / "skills/fixture/SKILL.md"
    target.write_bytes(b"original\n")
    with target.open("ab") as writer:
        result = sync(trees, "--apply")
        assert result.returncode == 0 and "BACKUP" in result.stdout
        writer.write(b"late edit via original open descriptor\n")
    (original,) = (root / ".local/upstream-backups").glob("*/fixture/SKILL.md")
    assert original.read_bytes().endswith(b"late edit via original open descriptor\n")
    assert target.read_bytes() == b"adapted\n"


def test_apply_stages_outside_skill_tree_and_keeps_original_outside_pack(
    trees, monkeypatch
):
    root, cache = trees
    module = load_sync(trees)
    target = root / "skills/fixture/SKILL.md"
    target.write_bytes(b"original\n")
    real_rename = module.rename_new

    def rename(src, dst):
        # Verify the actual temporary location during each file publication.
        assert root / ".local" in src.parents
        assert {p.name for p in (root / "skills").iterdir()} <= {"fixture"}
        real_rename(src, dst)

    monkeypatch.setattr(module, "rename_new", rename)
    assert module.main(["--cache", str(cache), "--apply"], root=root) is False
    assert sorted(p.name for p in (root / "skills").iterdir()) == ["fixture"]
    assert target.read_bytes() == b"adapted\n"
    (backup,) = (root / ".local/upstream-backups").glob("*/fixture/SKILL.md")
    assert backup.read_bytes() == b"original\n"
    assert not list((root / ".local").glob("upstream-stage-*"))


@pytest.mark.skipif(os.name == "nt", reason="requires POSIX symbolic links")
def test_apply_rejects_symlinked_recovery_store(trees, tmp_path):
    root, _ = trees
    skill = root / "skills/fixture/SKILL.md"
    skill.write_bytes(b"original\n")
    outside = tmp_path / "other"
    outside.mkdir()
    (root / ".local").symlink_to(outside, target_is_directory=True)
    result = sync(trees, "--apply")
    assert result.returncode != 0 and "symlink" in result.stderr
    assert list(outside.iterdir()) == []
    assert skill.read_bytes() == b"original\n"
