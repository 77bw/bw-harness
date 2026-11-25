"""Read-only structural checks. Dynamic imports and document semantics require review."""

import argparse
import ast
import json
import re
import subprocess
from pathlib import Path

ROOTS = {
    "src",
    "tests",
    "scripts",
    "docs",
    "experiments",
    "configs",
    ".local",
    ".git",
    ".venv",
    ".ruff_cache",
    ".pytest_cache",
    "__pycache__",
    "build",
    "dist",
    ".pi",
    ".claude",
    ".codex",
    ".agents",
    ".github",
    ".compound-engineering",
}
FILES = {
    "README.md",
    "AGENTS.md",
    "CLAUDE.md",
    "GLOSSARY.md",
    "CONTEXT.md",
    "CONCEPTS.md",
    "LICENSE",
    "pyproject.toml",
    "uv.lock",
    ".gitignore",
    ".copier-answers.yml",
    ".env",
    ".env.example",
    ".python-version",
    ".DS_Store",
}
DOCS = {"adr", "agents", "plans", "research", "solutions"}


def check(root):
    errors = []
    exceptions = set()
    policy = root / "configs" / "structure-exceptions.json"
    if policy.is_file() and policy.resolve().is_relative_to(root.resolve()):
        entries = json.loads(policy.read_text(encoding="utf-8"))
        if not isinstance(entries, dict) or not all(
            isinstance(v, str) and v.strip() for v in entries.values()
        ):
            raise ValueError(
                "structure-exceptions.json: expected {relative_path: reason}"
            )
        exceptions.update(entries)
    for p in sorted(root.iterdir()):
        if p.name not in (ROOTS if p.is_dir() else FILES) and p.name not in exceptions:
            errors.append(f"{p.name}: unexpected root entry")
        if p.name in {"CONTEXT.md", "CONCEPTS.md"}:
            print(f"WARN {p.name}: reconcile terms with GLOSSARY.md")
    for p in sorted((root / "docs").rglob("*.md")):
        parts = p.relative_to(root / "docs").parts
        if not (
            p.relative_to(root).as_posix() in exceptions
            or parts[0] in DOCS
            or parts in [("architecture.md",), ("status.md",), ("api.md",)]
        ):
            errors.append(f"{p.relative_to(root)}: unassigned document")
    for p in sorted((root / "src").rglob("*.py")):
        if p.is_symlink():
            errors.append(f"{p.relative_to(root)}: symlink requires review")
            continue
        if re.search(r"_(final|old|new|v\d+)\b", p.stem):
            print(f"WARN {p.relative_to(root)}: check for obsolete algorithm revision")
        try:
            tree = ast.parse(p.read_bytes(), filename=str(p))
        except SyntaxError as exc:
            errors.append(f"{p.relative_to(root)}:{exc.lineno}: {exc.msg}")
            continue
        for n in ast.walk(tree):
            names = (
                [a.name for a in n.names]
                if isinstance(n, ast.Import)
                else [n.module or ""]
                if isinstance(n, ast.ImportFrom)
                else []
            )
            if any(name.split(".")[0] in {"tests", "experiments"} for name in names):
                errors.append(f"{p.relative_to(root)}:{n.lineno}: forbidden dependency")
    if (root / ".git").exists():
        tracked = subprocess.check_output(
            ["git", "ls-files", "-z", "--", ".local", ".env", "*.pcap", "*.pcapng"],
            cwd=root,
        )
        errors.extend(
            f"{p.decode(errors='replace')}: forbidden tracked asset"
            for p in tracked.split(b"\0")
            if p
        )
    for error in errors:
        print("ERROR", error)
    return bool(errors)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("root", nargs="?", default=".", type=Path)
    raise SystemExit(check(parser.parse_args().root))
