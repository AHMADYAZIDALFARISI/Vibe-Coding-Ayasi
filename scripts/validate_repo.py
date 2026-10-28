#!/usr/bin/env python3
"""Validate the Plumbline repository.

Checks skill frontmatter against the Agent Skills format, folder/name agreement,
relative Markdown links, required repo files, README coverage, and likely secrets.
Usage: python3 scripts/validate_repo.py [repo_root]
"""
import re
import sys
from pathlib import Path

import yaml

ALLOWED_KEYS = {"name", "description", "license", "allowed-tools", "metadata", "compatibility"}
REQUIRED_FILES = ["README.md", "LICENSE", "CONTRIBUTING.md", "SECURITY.md", "CHANGELOG.md",
                  ".gitignore", ".editorconfig"]
MAX_SKILL_LINES = 500
SECRET_PATTERNS = [
    ("aws-access-key", re.compile(r"AKIA[0-9A-Z]{16}")),
    ("github-token", re.compile(r"gh[pousr]_[A-Za-z0-9]{36,}")),
    ("anthropic-or-openai-key", re.compile(r"sk-(ant-)?[A-Za-z0-9_-]{24,}")),
    ("private-key", re.compile(r"-----BEGIN (RSA |EC |OPENSSH )?PRIVATE KEY-----")),
    ("assigned-secret", re.compile(r"(api[_-]?key|secret|password|token)\s*[:=]\s*['\"][^'\"\s]{12,}['\"]", re.I)),
]
SKIP_DIRS = {".git", "node_modules", "__pycache__"}
LINK_RX = re.compile(r"\[[^\]]*\]\(([^)\s]+)\)")


def check_skill(skill_dir):
    errors = []
    md = skill_dir / "SKILL.md"
    if not md.exists():
        return [f"{skill_dir}: SKILL.md missing"]
    extra = [p for p in skill_dir.rglob("SKILL.md") if p != md and "__pycache__" not in p.parts]
    if extra:
        errors.append(f"{skill_dir}: nested SKILL.md files {extra}")
    text = md.read_text(encoding="utf-8")
    m = re.match(r"^---\n(.*?)\n---\n", text, re.S)
    if not m:
        return errors + [f"{md}: missing or malformed YAML frontmatter"]
    try:
        fm = yaml.safe_load(m.group(1))
    except yaml.YAMLError as e:
        return errors + [f"{md}: invalid YAML: {e}"]
    if not isinstance(fm, dict):
        return errors + [f"{md}: frontmatter is not a mapping"]
    unexpected = set(fm) - ALLOWED_KEYS
    if unexpected:
        errors.append(f"{md}: unexpected keys {sorted(unexpected)}")
    name, desc = fm.get("name"), fm.get("description")
    if not isinstance(name, str) or not re.fullmatch(r"[a-z0-9]+(-[a-z0-9]+)*", name or "") or len(name) > 64:
        errors.append(f"{md}: name must be kebab-case, max 64 chars")
    elif name != skill_dir.name:
        errors.append(f"{md}: name '{name}' does not match folder '{skill_dir.name}'")
    if not isinstance(desc, str) or not desc.strip():
        errors.append(f"{md}: description missing")
    else:
        if len(desc) > 1024:
            errors.append(f"{md}: description over 1024 chars ({len(desc)})")
        if "<" in desc or ">" in desc:
            errors.append(f"{md}: description contains angle brackets")
    if len(text.splitlines()) > MAX_SKILL_LINES:
        errors.append(f"{md}: over {MAX_SKILL_LINES} lines; move detail to references/")
    return errors


def iter_files(root):
    for p in root.rglob("*"):
        if p.is_file() and not (set(p.relative_to(root).parts) & SKIP_DIRS):
            yield p


def check_links(root):
    errors = []
    for md in (p for p in iter_files(root) if p.suffix == ".md"):
        in_fence = False
        for n, line in enumerate(md.read_text(encoding="utf-8").splitlines(), 1):
            if line.lstrip().startswith("```"):
                in_fence = not in_fence
            if in_fence:
                continue
            for target in LINK_RX.findall(line):
                if re.match(r"^(https?:|mailto:|#)", target):
                    continue
                path = target.split("#")[0]
                if path and not (md.parent / path).exists():
                    errors.append(f"{md.relative_to(root)}:{n}: broken link {target}")
    return errors


def check_secrets(root):
    errors = []
    for f in iter_files(root):
        if f.suffix in {".png", ".jpg", ".gif", ".zip"}:
            continue
        try:
            text = f.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            continue
        for n, line in enumerate(text.splitlines(), 1):
            if "secret-scan: allow" in line:
                continue
            for label, rx in SECRET_PATTERNS:
                if rx.search(line):
                    errors.append(f"{f.relative_to(root)}:{n}: possible {label}")
    return errors


def validate(root):
    root = Path(root).resolve()
    errors = [f"missing required file {f}" for f in REQUIRED_FILES if not (root / f).exists()]
    skills = sorted(p for p in (root / "skills").iterdir() if p.is_dir())
    if not skills:
        errors.append("no skills found under skills/")
    readme = (root / "README.md").read_text(encoding="utf-8") if (root / "README.md").exists() else ""
    for s in skills:
        errors += check_skill(s)
        if f"`{s.name}`" not in readme:
            errors.append(f"README.md does not list skill `{s.name}`")
    errors += check_links(root)
    errors += check_secrets(root)
    return skills, errors


def main():
    skills, errors = validate(sys.argv[1] if len(sys.argv) > 1 else Path(__file__).parent.parent)
    for e in errors:
        print(f"FAIL {e}")
    print(f"{len(skills)} skills checked, {len(errors)} error(s)")
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
