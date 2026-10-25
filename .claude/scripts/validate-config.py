"""Valida JSON, YAML e frontmatter de SKILL.md no repositório claude-config.

Espelha a lógica do CI em .github/workflows/validate-config.yml para que
possa ser executado localmente antes de push.
"""
import json
import pathlib
import sys

import yaml

ROOT = pathlib.Path(".")
IGNORE_DIRS = {".git", "node_modules"}


def iter_files(pattern):
    for path in sorted(ROOT.rglob(pattern)):
        if any(part in IGNORE_DIRS for part in path.parts):
            continue
        yield path


def validate_json():
    errors = []
    n = 0
    for path in iter_files("*.json"):
        n += 1
        try:
            json.loads(path.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, UnicodeDecodeError) as e:
            errors.append(f"[json] {path}: {e}")
    return n, errors


def validate_yaml():
    errors = []
    n = 0
    for pattern in ("*.yaml", "*.yml"):
        for path in iter_files(pattern):
            n += 1
            try:
                list(yaml.safe_load_all(path.read_text(encoding="utf-8")))
            except yaml.YAMLError as e:
                errors.append(f"[yaml] {path}: {e}")
    return n, errors


def validate_skill():
    errors = []
    n = 0
    for path in iter_files("SKILL.md"):
        n += 1
        text = path.read_text(encoding="utf-8")
        if not text.startswith("---"):
            errors.append(f"[skill] {path}: missing YAML frontmatter (must start with '---')")
            continue
        end = text.find("\n---", 3)
        if end == -1:
            errors.append(f"[skill] {path}: frontmatter block is never closed with '---'")
            continue
        try:
            frontmatter = yaml.safe_load(text[3:end]) or {}
        except yaml.YAMLError as e:
            errors.append(f"[skill] {path}: frontmatter is not valid YAML: {e}")
            continue
        for field in ("name", "description"):
            if not str(frontmatter.get(field, "")).strip():
                errors.append(f"[skill] {path}: frontmatter is missing a non-empty '{field}'")
    return n, errors


def main():
    errors = []
    n_json, json_errors = validate_json()
    n_yaml, yaml_errors = validate_yaml()
    n_skill, skill_errors = validate_skill()
    errors.extend(json_errors)
    errors.extend(yaml_errors)
    errors.extend(skill_errors)

    print(f"Checked {n_json} JSON file(s), {n_yaml} YAML file(s), {n_skill} SKILL.md file(s).")

    if errors:
        print(f"\n{len(errors)} problem(s) found:\n")
        for e in errors:
            print(f"  - {e}")
        sys.exit(1)

    print("All configuration files are valid.")


if __name__ == "__main__":
    main()
