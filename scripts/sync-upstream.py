"""Compare the fixed upstream trees; write only with --apply. Run from pack root."""

import argparse
import hashlib
import json
import shutil
import subprocess
import tempfile
from pathlib import Path


def digest(path):
    h = hashlib.sha256()
    for p in sorted(path.rglob("*")) if path.is_dir() else [path]:
        if p.is_file():
            h.update(str(p.relative_to(path)).replace("\\", "/").encode() + b"\0")
            h.update(hashlib.sha256(p.read_bytes()).digest())
    return h.hexdigest()


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--apply", action="store_true")
    p.add_argument(
        "--cache", type=Path, help="existing clean upstream checkouts named matt and ce"
    )
    args = p.parse_args()
    with tempfile.TemporaryDirectory() as tmp:
        for key, meta in json.loads(Path("upstream.lock.yml").read_text()).items():
            repo = (args.cache or Path(tmp)) / key
            if not args.cache:
                subprocess.run(["git", "init", "-q", str(repo)], check=True)
                subprocess.run(
                    [
                        "git",
                        "fetch",
                        "--quiet",
                        "--depth=1",
                        meta["url"],
                        meta["commit"],
                    ],
                    cwd=repo,
                    check=True,
                )
                subprocess.run(
                    ["git", "checkout", "--quiet", "--detach", "FETCH_HEAD"],
                    cwd=repo,
                    check=True,
                )
            head = subprocess.check_output(
                ["git", "rev-parse", "HEAD"], cwd=repo, text=True
            ).strip()
            if head != meta["commit"]:
                raise SystemExit(f"{key}: unexpected revision")
            for dst, entry in meta["resources"].items():
                src = repo / entry["source"]
                if digest(src) != entry["sha256"]:
                    raise SystemExit(f"{src.name}: upstream checksum mismatch")
                target = Path(dst)
                if target.exists() and digest(target) == entry["sha256"]:
                    continue
                print("DIFF", dst)
                if args.apply:
                    if target.exists():
                        raise SystemExit(f"{dst}: move modified resource aside first")
                    target.parent.mkdir(parents=True, exist_ok=True)
                    (shutil.copytree if src.is_dir() else shutil.copy2)(src, target)
            print(key, head, "checked")


if __name__ == "__main__":
    main()
