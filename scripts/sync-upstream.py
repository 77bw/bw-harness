"""Replay the *pinned* upstream sources and reviewed patches in isolation.

Default: verify and report drift, no writes to the pack. --apply restores only
missing, pristine upstream, or last committed lock-matching resources after all checks succeed.
Existing resources are retained at printed recovery paths, including concurrent open-file edits. To author a
patch, edit one distributed resource, then explicitly --record its package path,
inspect the patch/lock diff, and rerun the default verification.
"""

import argparse
import io
import json
import os
import shutil
import subprocess
import sys
import tarfile
import tempfile
from pathlib import Path

from package_checks import ROOT, dependency_names, digest, files, inside, routes


def git(cwd, *args):
    cmd = [
        "git",
        "-c",
        "core.autocrlf=false",
        "-c",
        "core.safecrlf=false",
        "-c",
        "core.hooksPath=/dev/null",
        *map(str, args),
    ]
    return subprocess.run(cmd, cwd=cwd, check=True, stdout=subprocess.PIPE).stdout


def copy(src, dst):
    dst.parent.mkdir(parents=True, exist_ok=True)
    if dst.is_dir():
        shutil.rmtree(dst)
    elif dst.exists():
        dst.unlink()
    (shutil.copytree if src.is_dir() else shutil.copy2)(src, dst)


def extract(repo, commit, source, tree, dst):
    """Read Git objects, not mutable cache files or CRLF checkout conversions."""
    inside(tree, source)
    target = inside(tree, dst)
    data = git(repo, "archive", commit, "--", source)
    with tarfile.open(fileobj=io.BytesIO(data)) as archive:
        for item in archive:
            if item.isdir():
                continue
            if not item.isfile():
                raise ValueError(f"{source}: unexpected archive entry {item.name}")
            rel = Path(item.name).relative_to(source)
            path = (
                target if rel == Path(".") else inside(tree, f"{dst}/{rel.as_posix()}")
            )
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(archive.extractfile(item).read())
            path.chmod(0o755 if item.mode & 0o111 else 0o644)
    return target


def executable_files(target):
    return sorted(
        f.relative_to(target).as_posix()
        for f in files(target)
        if f.stat().st_mode & 0o111
    )


def snapshot(path):
    if path.is_symlink():
        raise ValueError(f"symlink in resource: {path}")
    if not path.exists():
        return None
    return digest(path), None if os.name == "nt" else executable_files(path)


def checked_target(root, name, observed):
    target = inside(root, name)
    if snapshot(target) != observed:
        raise ValueError(f"{name}: destination changed during replay; not overwriting")
    return target


def rename_new(src, dst):
    """Atomically publish a whole resource without replacing even an empty racing target."""
    if os.name == "nt":
        os.rename(src, dst)  # Windows refuses an existing destination.
        return
    # POSIX rename/replace can silently destroy a newly created file or empty
    # directory. Use the native exclusive form or fail closed on unsupported FS.
    import ctypes

    libc = ctypes.CDLL(None, use_errno=True)
    a, b = os.fsencode(src), os.fsencode(dst)
    if sys.platform == "darwin" and hasattr(libc, "renamex_np"):
        result = libc.renamex_np(a, b, 4)  # RENAME_EXCL
    elif sys.platform.startswith("linux") and hasattr(libc, "renameat2"):
        result = libc.renameat2(-100, a, -100, b, 1)  # AT_FDCWD, RENAME_NOREPLACE
    else:
        raise OSError("atomic non-replacing rename is unavailable")
    if result:
        err = ctypes.get_errno()
        raise OSError(err, os.strerror(err), str(dst))


def install(root, source, name, observed):
    target = checked_target(root, name, observed)
    target.parent.mkdir(parents=True, exist_ok=True)
    # Stage and recover outside discoverable skills and tracked pack resources.
    local = inside(root, ".local")
    local.mkdir(mode=0o700, exist_ok=True)
    if local.stat().st_dev != target.parent.stat().st_dev:
        raise ValueError(f"{name}: staging and destination must be on the same volume")
    with tempfile.TemporaryDirectory(prefix="upstream-stage-", dir=local) as tmp:
        incoming, staged = Path(tmp) / "incoming", Path(tmp) / "candidate"
        copy(source, incoming)
        # Probe exclusive rename support on this volume *before* displacing data.
        rename_new(incoming, staged)
        backup = None
        if observed is not None:
            recoveries = inside(root, ".local/upstream-backups")
            recoveries.mkdir(mode=0o700, exist_ok=True)
            directory = Path(tempfile.mkdtemp(dir=recoveries))
            backup = directory / target.name
        checked_target(root, name, observed)
        if backup is not None:
            target.rename(inside(root, backup.relative_to(root).as_posix()))
            print("BACKUP", name, backup, flush=True)
        try:
            if backup is not None and snapshot(backup) != observed:
                raise ValueError(f"{name}: destination changed during replacement")
            rename_new(staged, inside(root, name))
        except (OSError, ValueError) as error:
            if backup is not None:
                try:
                    rename_new(backup, inside(root, name))
                except (OSError, ValueError) as recovery_error:
                    raise ValueError(
                        f"{name}: {error}; current destination untouched; "
                        f"recover the displaced resource at {backup}: {recovery_error}"
                    ) from error
                backup.parent.rmdir()
            raise
        # Do not delete the backup: a writer holding an open descriptor can
        # still change the displaced tree after the validation above.


def committed_resources(root):
    """A previous *reviewed lock*, never the mere fact that a path is tracked."""
    top = subprocess.run(
        ["git", "rev-parse", "--show-toplevel"],
        cwd=root,
        check=False,
        capture_output=True,
        text=True,
        encoding="utf-8",
    )
    if top.returncode or Path(top.stdout.strip()).resolve() != root:
        return {}
    data = subprocess.run(
        ["git", "show", "HEAD:upstream.lock.yml"],
        cwd=root,
        check=False,
        capture_output=True,
    )
    if data.returncode:  # e.g. first import
        return {}
    lock = json.loads(data.stdout.decode("utf-8"))
    return {
        name: item
        for group in lock.values()
        for name, item in group["resources"].items()
    }


def main(argv=None, root=ROOT):
    parser = argparse.ArgumentParser(description=__doc__)
    group = parser.add_mutually_exclusive_group()
    group.add_argument("--apply", action="store_true")
    group.add_argument(
        "--record",
        nargs="+",
        metavar="RESOURCE",
        help="author patches for explicitly reviewed resource(s); never implies --apply",
    )
    parser.add_argument(
        "--cache",
        type=Path,
        help="existing clones with pinned commits under matt/ and ce/",
    )
    args = parser.parse_args(argv)
    root = root.resolve()
    lock_path = root / "upstream.lock.yml"
    lock = json.loads(lock_path.read_text(encoding="utf-8"))
    known = {k for group in lock.values() for k in group["resources"]}
    selected = set(args.record or [])
    if selected and os.name == "nt":
        raise ValueError(
            "Record mode needs POSIX executable bits; use Linux, macOS, or WSL"
        )
    previous = committed_resources(root) if args.apply else {}
    if selected - known:
        raise ValueError(f"not a declared resource: {sorted(selected - known)}")
    staged, patches, drifts = [], {}, []
    patterns = dependency_names(
        lock,
        root,
        (Path(p).name for p in known if args.apply and p.startswith("skills/")),
    )
    with tempfile.TemporaryDirectory() as tmp:
        base = Path(tmp)
        for key, meta in lock.items():
            repo = (args.cache or base / "clones") / key
            if not args.cache:
                repo.mkdir(parents=True)
                git(repo, "init", "-q")
                git(repo, "fetch", "-q", "--depth=1", meta["url"], meta["commit"])
            commit = (
                git(repo, "rev-parse", "--verify", meta["commit"] + "^{commit}")
                .decode()
                .strip()
            )
            if commit != meta["commit"]:
                raise ValueError(f"{key}: unexpected revision")
            for dst, entry in meta["resources"].items():
                if selected and dst not in selected:
                    continue
                target = inside(root, dst)
                # Each resource is isolated even when it produces no pending writes.
                tree = Path(tempfile.mkdtemp(dir=base))
                source = extract(repo, commit, entry["source"], tree, dst)
                original = digest(source)
                original_modes = executable_files(source)
                if original != entry["upstream_sha256"]:
                    raise ValueError(f"{dst}: upstream checksum mismatch")
                patch_name = entry.get("patch")
                if selected:
                    actual = digest(target)
                    rel = f"patches/{key}/{target.name}.patch"
                    if actual != original or (
                        os.name != "nt"
                        and executable_files(target) != executable_files(source)
                    ):
                        git(tree, "init", "-q")
                        git(tree, "add", "-f", "--", dst)
                        old = git(tree, "write-tree").decode().strip()
                        copy(target, source)
                        git(tree, "add", "-A", "-f", "--", dst)
                        patches[inside(root, rel)] = git(
                            tree,
                            "diff",
                            "--cached",
                            "--binary",
                            "--full-index",
                            old,
                            "--",
                            dst,
                        )
                        entry["patch"] = rel
                    else:
                        entry.pop("patch", None)
                    if patch_name and patch_name != entry.get("patch"):
                        patches[inside(root, patch_name)] = None
                    entry["sha256"] = actual
                    entry["executables"] = executable_files(target)
                    if dst.startswith("skills/"):
                        deps, errors = routes(target, patterns, lock)
                        if errors:
                            raise ValueError("\n".join(errors))
                        entry["requires"] = deps
                    print("RECORD", dst)
                    continue
                if patch_name:
                    patch = inside(root, patch_name)
                    if not patch_name.startswith(f"patches/{key}/"):
                        raise ValueError(f"{dst}: invalid patch location")
                    git(tree, "init", "-q")
                    git(tree, "add", "-f", "--", dst)
                    git(
                        tree,
                        "apply",
                        "--cached",
                        "--check",
                        "--whitespace=nowarn",
                        patch,
                    )
                    before = git(tree, "write-tree").decode().strip()
                    git(tree, "apply", "--index", "--whitespace=nowarn", patch)
                    changed = (
                        git(tree, "diff", "--cached", "--name-only", "-z", before)
                        .decode()
                        .split("\0")
                    )
                    if not any(changed) or any(
                        p and p != dst and not p.startswith(dst + "/") for p in changed
                    ):
                        raise ValueError(f"{dst}: patch outside its declared resource")
                if digest(source) != entry["sha256"]:
                    raise ValueError(f"{dst}: replayed checksum mismatch")
                modes = entry.get("executables", [])
                if os.name != "nt" and executable_files(source) != modes:
                    raise ValueError(f"{dst}: replayed executable bits mismatch")
                if dst.startswith("skills/"):
                    deps, errors = routes(source, patterns, lock)
                    if errors or deps != entry["requires"]:
                        raise ValueError(
                            f"{dst}: dependency mismatch: {errors or deps}"
                        )
                observed = snapshot(target)
                if observed == (entry["sha256"], None if os.name == "nt" else modes):
                    continue
                print("DIFF", dst)
                drifts.append(dst)
                if args.apply:
                    if observed is not None:
                        found, mode = observed
                        old = previous.get(dst, {})
                        pristine = found == original and (
                            os.name == "nt" or mode == original_modes
                        )
                        committed = found == old.get("sha256") and (
                            os.name == "nt" or mode == old.get("executables")
                        )
                        if not (pristine or committed):
                            raise ValueError(
                                f"{dst}: local modifications; refusing to overwrite"
                            )
                    staged.append((source, dst, observed))
            print(key, commit, "checked")
        # Check the whole queue before applying any of it, and then each
        # destination at its own installation boundary.
        for _, name, observed in staged:
            checked_target(root, name, observed)
        for src, name, observed in staged:
            install(root, src, name, observed)
        if selected:
            for path, content in patches.items():
                if content is None:
                    path.unlink(missing_ok=True)
                else:
                    path.parent.mkdir(parents=True, exist_ok=True)
                    path.write_bytes(content)
            lock_path.write_bytes(
                (json.dumps(lock, ensure_ascii=False, indent=2) + "\n").encode()
            )
    return bool(drifts) and not args.apply


if __name__ == "__main__":
    try:
        sys.exit(main())
    except (OSError, ValueError, KeyError, subprocess.CalledProcessError) as exc:
        sys.exit(f"ERROR: {exc}")
