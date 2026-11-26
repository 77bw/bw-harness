"""Validate the distributed pack offline; never substitute this for host pilots."""

import json
import os
import re
import sys

from package_checks import ROOT, dependency_names, digest, files, inside, links, routes


def check(root):
    lock = json.loads((root / "upstream.lock.yml").read_text(encoding="utf-8"))
    patterns = dependency_names(lock, root)
    shipped = patterns[0]
    errors, mapped, patches = [], {}, set()
    for key, meta in lock.items():
        catalog, excluded = set(meta["skill_catalog"]), meta["excluded_routes"]
        if set(excluded) != catalog - shipped or not all(excluded.values()):
            errors.append(f"{key}: account for every unshipped upstream skill")
        if (
            not re.fullmatch(r"[a-f0-9]{40}", meta["commit"])
            or meta["license"] != "MIT"
        ):
            errors.append(f"{key}: expected pinned upstream and MIT attribution")
        for dst, item in meta["resources"].items():
            target = inside(root, dst)
            inside(root, item["source"])
            if dst in mapped:
                errors.append(f"{dst}: conflicting source mappings")
            mapped[dst] = item
            original, final = item["upstream_sha256"], item["sha256"]
            if not all(re.fullmatch(r"[a-f0-9]{64}", h) for h in (original, final)):
                errors.append(f"{dst}: malformed digest")
            if not target.exists() or digest(target) != final:
                errors.append(f"{dst}: missing or modified distributed resource")
            if original != final and not item.get("patch"):
                errors.append(f"{dst}: missing replayable patch")
            if item.get("patch"):
                patch = inside(root, item["patch"])
                if (
                    not item["patch"].startswith(f"patches/{key}/")
                    or not patch.is_file()
                    or not patch.stat().st_size
                ):
                    errors.append(f"{dst}: missing or invalid patch")
                patches.add(patch)
            for rel in item["executables"]:
                executable = inside(target, rel)
                if (
                    not executable.is_file()
                    or os.name != "nt"
                    and not executable.stat().st_mode & 0o111
                ):
                    errors.append(f"{dst}/{rel}: missing executable")
    if set((root / "patches").rglob("*.patch")) != patches:
        errors.append("orphaned or missing patch file")
    for skill in sorted((root / "skills").iterdir()):
        if not skill.is_dir():
            continue
        name, doc = skill.name, skill / "SKILL.md"
        if not doc.is_file():
            errors.append(f"{name}: missing SKILL.md")
            continue
        header = re.match(
            r"\A---\n(.*?)\n---(?:\n|$)", doc.read_text(encoding="utf-8"), re.DOTALL
        )
        if (
            not header
            or not re.search(rf"^name: {re.escape(name)}$", header[1], re.MULTILINE)
            or not re.search(r"^description:\s*\S", header[1], re.MULTILINE)
        ):
            errors.append(f"{name}: invalid frontmatter")
        deps, issues = routes(skill, patterns, lock)
        errors.extend(issues)
        metadata = mapped.get("skills/" + name)
        if metadata:
            if metadata["requires"] != deps:
                errors.append(
                    f"{name}: declared dependencies differ from shipped references"
                )
        elif name != "project-governance":
            errors.append(f"{name}: missing source attribution")
        for p in files(skill):
            p.read_text(encoding="utf-8")
            if p.suffix == ".md":
                errors.extend(links(p, root, skill))
    for dest, upstream in (
        ("bw-help", "ask-matt"),
        ("setup-bw-harness", "setup-matt-pocock-skills"),
    ):
        if mapped.get("skills/" + dest, {}).get("derived_from") != upstream:
            errors.append(f"{dest}: missing Matt derivative mapping")
    guides = root / "guides"
    if {p.stem for p in (guides / "skills").glob("*.md")} != shipped:
        errors.append("Skill and guide names differ")
    for p in [
        root / "AGENTS.md",
        root / "README.md",
        root / "CHANGELOG.md",
        *guides.rglob("*.md"),
    ]:
        errors.extend(links(p, root))
    package = json.loads((root / "package.json").read_text(encoding="utf-8"))
    npm = json.loads((root / "package-lock.json").read_text(encoding="utf-8"))
    versions = [npm["version"], npm["packages"][""]["version"]]
    for name in (".codex-plugin/plugin.json", ".claude-plugin/plugin.json"):
        versions.append(
            json.loads((root / name).read_text(encoding="utf-8"))["version"]
        )
    if any(v != package["version"] for v in versions):
        errors.append("inconsistent package/host manifest versions")
    for name in package["pi"]["extensions"]:
        if not inside(root, name).is_file():
            errors.append(
                f"{name}: missing extension; run npm ci --legacy-peer-deps --ignore-scripts"
            )
    return len(shipped), errors


if __name__ == "__main__":
    try:
        count, errors = check(ROOT)
        for message in sorted(set(errors)):
            print("ERROR", message)
        print(f"{count} skill entries; {len(errors)} errors (offline package checks)")
        sys.exit(bool(errors))
    except (OSError, ValueError, KeyError) as exc:
        sys.exit(f"ERROR: {exc}")
