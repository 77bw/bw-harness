"""Shared, offline checks for the shipped skill trees (not consumer projects)."""

import hashlib
import re
from pathlib import Path, PurePosixPath

ROOT = Path(__file__).resolve().parents[1]
LINK = re.compile(r"\[[^\]\n]*\]\(([^ )#]+)(?:#[^ )]*)?\)")
RESOURCE = re.compile(
    r"(?<![\w/.-])(?:references|scripts|assets|examples|templates)/"
    r"[\w.-]+(?:/[\w.-]+)*\.(?:md|py|sh|mjs|js|ts|json|yaml|yml|txt|css)\b"
    r"|(?<![\w/.-])scripts/[\w-]+(?=[`'\"\s/])"
)


def inside(root, name):
    """Reject absolute paths, symlinks and parent traversal before reading/writing."""
    p = PurePosixPath(name)
    if (
        not p.parts
        or p.is_absolute()
        or ".." in p.parts
        or "\\" in name
        or ":" in name
        or any(i.lower() == ".git" for i in p.parts)
    ):
        raise ValueError(f"unsafe package path: {name}")
    path = root.joinpath(*p.parts)
    if any(
        q.is_symlink() for q in (path, *path.parents) if q != root and root in q.parents
    ):
        raise ValueError(f"symlink in package path: {name}")
    return path


def files(path):
    for f in (
        sorted(path.rglob("*"), key=lambda f: f.relative_to(path).parts)
        if path.is_dir()
        else [path]
    ):
        if f.is_symlink():
            raise ValueError(f"symlink in resource: {f}")
        if f.is_file():
            yield f


def digest(path):
    if not path.exists():
        raise ValueError(f"missing resource: {path}")
    h = hashlib.sha256()
    for f in files(path):
        h.update(f.relative_to(path).as_posix().encode() + b"\0")
        h.update(hashlib.sha256(f.read_bytes()).digest())
    return h.hexdigest()


def dependency_names(lock, root, restoring=()):
    ce = set(lock["ce"]["skill_catalog"])
    shipped = {p.parent.name for p in (root / "skills").glob("*/SKILL.md")} | set(
        restoring
    )
    matt = set(lock["matt"]["skill_catalog"])
    # Standalone CE identifiers are distinctive. Generic Matt names (e.g. pr,
    # research, handoff) also occur as normal prose, file names and CLI commands.
    distinct = ce | {s for s in matt | shipped if "-" in s and s != "code-review"}
    names = "|".join(map(re.escape, sorted(distinct, key=len, reverse=True)))
    exact = re.compile(r"(?<![\w-])(" + names + r")(?![\w-])")
    simple = "|".join(map(re.escape, sorted(matt | shipped, key=len, reverse=True)))
    explicit = re.compile(
        r"(?:\bskill:|(?<![\w/.-])/|(?<=`)\$|\b(?:invoke|load|use|see) (?:the )?`|\bskills/)("
        + simple
        + r")(?![\w./-])|\x60("
        + simple
        + r")\x60 skill\b"
    )
    return shipped, exact, explicit


HOST_CALL = re.compile(
    r"(?:/skill:|(?:invoke|load|call|run) (?:the )?[`/](?=ce-))"
    r"([a-z][a-z0-9]*(?:-[a-z0-9]+)+)(?![\w.-])",
    re.IGNORECASE,
)


def routes(skill, patterns, lock):
    shipped, exact, explicit = patterns
    edges, errors = set(), []
    annotations = {
        **lock["matt"].get("non_routes", {}),
        **lock["ce"].get("non_routes", {}),
    }
    for p in files(skill):
        rel = p.relative_to(skill.parent.parent).as_posix()
        # Scripts and config templates are included; not just SKILL.md.
        for line in p.read_text(encoding="utf-8").splitlines():
            mentions = set(exact.findall(line)) | set(HOST_CALL.findall(line))
            mentions.update((a or b).lower() for a, b in explicit.findall(line))
            for target in mentions - {skill.name}:
                stamp = hashlib.sha256(line.strip().encode()).hexdigest()[:16]
                if f"{rel}:{target}:{stamp}" in annotations:
                    continue  # exact audited line, not a blanket exclusion of the skill
                if target not in shipped:
                    errors.append(f"{rel}: {skill.name} -> missing skill {target}")
                else:
                    edges.add(target)
    return sorted(edges), errors


def links(doc, root, skill=None):
    errors, fenced = [], False
    for number, line in enumerate(doc.read_text(encoding="utf-8").splitlines(), 1):
        if line.lstrip().startswith(("```", "~~~")):
            fenced = not fenced
        for href in LINK.findall(line) if not fenced else []:
            if re.match(r"(?:https?://|mailto:)", href):
                continue
            path = (doc.parent / href).resolve()
            if root not in path.parents or not path.exists():
                errors.append(f"{doc.relative_to(root)}:{number}: broken link {href}")
        if not skill:
            continue
        for href in RESOURCE.findall(line):
            if not (skill / href).exists() and not (doc.parent / href).exists():
                errors.append(
                    f"{doc.relative_to(root)}:{number}: missing skill resource {href}"
                )
    return errors
