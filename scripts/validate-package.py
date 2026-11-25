"""Verify imported bytes, skill names, guide coverage, and local hand-written links."""

import json
import re
import runpy
from pathlib import Path

root = Path(__file__).resolve().parents[1]
digest = runpy.run_path(str(root / "scripts/sync-upstream.py"))["digest"]
errors = []
locked = set()
lock = json.loads((root / "upstream.lock.yml").read_text(encoding="utf-8"))
for meta in lock.values():
    for path, item in meta["resources"].items():
        if not (root / path).exists() or digest(root / path) != item["sha256"]:
            errors.append(f"{path}: missing or modified upstream resource")
        locked.add(path)
skills = list((root / "skills").glob("*/SKILL.md"))
for skill in skills:
    name = skill.parent.name
    if not re.search(rf"^name: {re.escape(name)}$", skill.read_text(), re.MULTILINE):
        errors.append(f"{name}: missing or mismatched name")
    if (
        name not in {"setup-bw-harness", "bw-help", "project-governance"}
        and "skills/" + name not in locked
    ):
        errors.append(f"{name}: no source attribution")
# Match exact upstream identifiers, not CSS classes, scratch names or ce-* flags.
names = {p.parent.name for p in skills}
ce = lock["ce"]
required = set(ce["skill_catalog"]) - set(ce["excluded_routes"])
required.update(
    Path(k).name for k in lock["matt"]["resources"] if k.startswith("skills/")
)
pattern = re.compile(
    r"(?<![\w-])(?:" + "|".join(map(re.escape, sorted(required))) + r")(?![\w-])"
)
for skill in skills:
    for doc in skill.parent.rglob("*.md"):
        for missing in sorted(
            set(pattern.findall(doc.read_text(encoding="utf-8"))) - names
        ):
            errors.append(
                f"{doc.relative_to(root)}: {skill.parent.name} -> missing skill {missing}"
            )
guides = list((root / "guides/skills").glob("*.md"))
if {p.stem for p in guides} != {p.parent.name for p in skills}:
    errors.append("Skill and guide names differ")
for doc in [root / "README.md", *(root / "guides").rglob("*.md")]:
    for href in re.findall(r"\[[^\]]*\]\(([^ )#]+)(?:#[^ )]*)?\)", doc.read_text()):
        if "://" not in href and not (doc.parent / href).exists():
            errors.append(f"{doc.relative_to(root)}: broken link {href}")
for glob in json.loads((root / "package.json").read_text())["pi"]["extensions"]:
    if not (root / glob).is_file():
        errors.append(
            f"{glob}: extension missing; run npm ci --legacy-peer-deps --ignore-scripts"
        )
for msg in errors:
    print("ERROR", msg)
print(f"{len(skills)} skill entries; {len(guides)} guides; {len(errors)} errors")
raise SystemExit(bool(errors))
