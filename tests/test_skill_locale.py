"""Guard Chinese prose coverage and the identifiers read by native workflows."""

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
HAN = re.compile(r"[\u3400-\u9fff]")
FENCE = re.compile(r"^\s*(`{3,}|~{3,})([\w-]*)\s*$")
ENGLISH = re.compile(r"\b[A-Za-z]+(?:[-'][A-Za-z]+)*\b")


def ascii_code_and_links(text):
    return re.sub(r"`[^`\n]+`|https?://\S+|<[^>]*>|\]\([^)]*\)", "", text)


def test_every_distributed_skill_and_markdown_reference_has_chinese_prose():
    skills = ROOT / "skills"
    paths = list(skills.rglob("*.md"))
    assert paths
    missing = []
    untranslated = []
    for p in paths:
        text = p.read_text(encoding="utf-8")
        if p.name == "SKILL.md":
            metadata = text.split("---\n", 2)[1]
            assert f"name: {p.parent.name}\n" in metadata
            assert HAN.search(re.search(r"(?m)^description: (.+)$", metadata)[1]), p
        body = text.split("---\n", 2)[2] if text.startswith("---\n") else text
        if len(HAN.findall(body)) < 20:
            missing.append(str(p.relative_to(ROOT)))
        # Outside literal examples, paragraphs (but not protocol headings) must
        # not silently revert to English after an upstream sync.
        fenced = None
        for number, line in enumerate(body.splitlines(), 1):
            match = FENCE.fullmatch(line)
            if match:
                if fenced is None:
                    fenced = match[1]
                elif not match[2] and len(match[1]) >= len(fenced):
                    fenced = None
                continue
            if fenced is not None or line.lstrip().startswith(("#", "<!--", "{")):
                continue
            prose = ascii_code_and_links(line)
            if not HAN.search(prose) and len(ENGLISH.findall(prose)) >= 12:
                untranslated.append(f"{p.relative_to(ROOT)}:{number}")
    assert not missing, missing
    assert not untranslated, untranslated


def test_template_protocol_tokens_are_not_localized():
    skills = ROOT / "skills"
    plan = (skills / "ce-plan/references/plan-sections.md").read_text(encoding="utf-8")
    for kind in (
        "Goal Capsule",
        "Product Contract",
        "Implementation Units",
        "Verification Contract",
        "Definition of Done",
    ):
        assert "`## " + kind + "`" in plan
    setup = (skills / "setup-bw-harness/SKILL.md").read_text(encoding="utf-8")
    assert "    ## Agent skills\n    - 领域术语" in setup
    directive = (skills / "ce-setup/assets/compounding-directive.md").read_text(
        encoding="utf-8"
    )
    assert "## Run automatically" in directive
    assert "`ce-compound mode:non-interactive`" in directive
