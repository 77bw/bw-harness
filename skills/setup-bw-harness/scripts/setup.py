"""Initialize an empty destination or diagnose an existing project without writes."""

import argparse
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
DOCS = (
    "AGENTS.md",
    "CLAUDE.md",
    "GLOSSARY.md",
    "docs/status.md",
    "docs/architecture.md",
    "docs/agents/domain.md",
    "docs/agents/issue-tracker.md",
    ".compound-engineering/config.yaml",
)


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("mode", choices=["new", "check", "migrate", "docs"])
    p.add_argument("target", type=Path)
    p.add_argument("--name", default="sample_project")
    p.add_argument("--research", action="store_true")
    p.add_argument("--api", action="store_true")
    p.add_argument("--apply-docs", action="store_true")
    a = p.parse_args()
    root = a.target.resolve(strict=True)
    if not root.is_dir():
        p.error("target must be a directory")
    if a.mode == "new":
        if any(f.name != ".git" for f in root.iterdir()):
            p.error("nonempty target: use check or migrate; no changes made")
        cmd = [
            "uvx",
            "--from",
            "copier==9.19.1",
            "copier",
            "copy",
            "--defaults",
            "-d",
            f"package_name={a.name}",
            "-d",
            f"api={a.api}",
            "-d",
            f"research={a.research}",
        ]
        if (ROOT / ".git").exists():
            rev = subprocess.check_output(
                ["git", "rev-parse", "--verify", "HEAD"], cwd=ROOT, text=True
            ).strip()
            cmd.extend(["--vcs-ref", rev])
        return subprocess.call([*cmd, str(ROOT), str(root)])
    missing = []
    for name in DOCS:
        dst = root / name
        if dst.is_symlink() or dst.resolve() != dst:
            p.error(f"unsafe symlink: {name}")
        if not dst.exists():
            missing.append(name)
    for name in missing:
        print("missing:", name)
        if a.mode == "docs" and a.apply_docs:
            dst = root / name
            dst.parent.mkdir(parents=True, exist_ok=True)
            with dst.open("xb") as f:
                f.write((ROOT / "templates/python" / name).read_bytes())
    if a.mode == "docs":
        return 0
    print(
        "Review existing documents; do not replace or remove unique evidence.",
        flush=True,
    )
    status = subprocess.call(
        [
            sys.executable,
            str(ROOT / "templates/python/scripts/check_structure.py"),
            str(root),
        ]
    )
    return int(bool(status or missing))


if __name__ == "__main__":
    sys.exit(main())
