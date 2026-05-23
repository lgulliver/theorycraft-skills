#!/usr/bin/env python3
"""
Build .skill files and release bundles for the theorycraft skill suite.

Usage:
    python3 scripts/package.py skills/theorycraft-<name>   # single skill
    python3 scripts/package.py --all                        # all skills + suite bundle

.skill files are zip archives containing SKILL.md and references/.
"""

import argparse
import shutil
import zipfile
from pathlib import Path

SKILLS_DIR = Path("skills")
BUNDLE_NAME = "theorycraft-suite.zip"
OPENCODE_DIR = Path(".opencode")
OPENCODE_BUNDLE_NAME = "opencode-skills.zip"


def parse_frontmatter_name(skill_dir: Path) -> str:
    """Extract the `name` field from SKILL.md frontmatter."""
    skill_file = skill_dir / "SKILL.md"
    if not skill_file.exists():
        raise SystemExit(f"Error: {skill_file} not found")
    text = skill_file.read_text(encoding="utf-8")
    if not text.startswith("---\n"):
        raise SystemExit(f"Error: {skill_file} missing YAML frontmatter (---)")
    parts = text.split("---\n", 2)
    if len(parts) < 3:
        raise SystemExit(f"Error: {skill_file} has incomplete YAML frontmatter")
    frontmatter = parts[1]
    for line in frontmatter.strip().splitlines():
        if line.startswith("name:"):
            return line.split(":", 1)[1].strip()
    raise SystemExit(f"Error: {skill_file} frontmatter missing 'name' field")


def build_skill(skill_dir: Path, output_dir: Path) -> Path:
    """Create a .skill zip from a skill directory. Returns path to the .skill file."""
    name = parse_frontmatter_name(skill_dir)
    skill_path = output_dir / f"{name}.skill"
    with zipfile.ZipFile(skill_path, "w", zipfile.ZIP_DEFLATED) as zf:
        root_len = len(skill_dir.parent.parts)
        for filepath in sorted(skill_dir.rglob("*")):
            if filepath.is_file() and filepath.name != ".DS_Store":
                arcname = str(Path(*filepath.parts[root_len:]))
                zf.write(filepath, arcname)
    print(f"  Built {skill_path}")
    return skill_path


def build_all(output_dir: Path, opencode: bool = False) -> list[Path]:
    """Build all skills. If opencode=True, also install into .opencode/skills/."""
    built: list[Path] = []
    for entry in sorted(SKILLS_DIR.iterdir()):
        if entry.is_dir() and (entry / "SKILL.md").exists():
            built.append(build_skill(entry, output_dir))
            if opencode:
                install_to_opencode(entry)
    return built


def install_to_opencode(skill_dir: Path) -> Path:
    """Copy skill directory into .opencode/skills/<name>/ for opencode discovery."""
    name = parse_frontmatter_name(skill_dir)
    dest = OPENCODE_DIR / "skills" / name
    dest.mkdir(parents=True, exist_ok=True)
    for entry in skill_dir.iterdir():
        if entry.name == ".DS_Store":
            continue
        dest_entry = dest / entry.name
        if entry.is_dir():
            shutil.copytree(entry, dest_entry, dirs_exist_ok=True)
        else:
            shutil.copy2(entry, dest_entry)
    print(f"  Installed {dest}")
    return dest


def build_suite_bundle(built: list[Path], output_dir: Path) -> Path:
    """Zip all built .skill files into the suite bundle."""
    bundle_path = output_dir / BUNDLE_NAME
    with zipfile.ZipFile(bundle_path, "w", zipfile.ZIP_DEFLATED) as zf:
        for skill_path in built:
            zf.write(skill_path, skill_path.name)
    print(f"  Built {bundle_path}")
    return bundle_path


def build_opencode_bundle(output_dir: Path) -> Path:
    """Zip .opencode/skills/ into a release-ready bundle."""
    source_dir = OPENCODE_DIR / "skills"
    bundle_path = output_dir / OPENCODE_BUNDLE_NAME
    with zipfile.ZipFile(bundle_path, "w", zipfile.ZIP_DEFLATED) as zf:
        for filepath in sorted(source_dir.rglob("*")):
            if filepath.is_file() and filepath.name != ".DS_Store":
                zf.write(filepath, filepath.relative_to(OPENCODE_DIR))
    print(f"  Built {bundle_path}")
    return bundle_path


def main():
    parser = argparse.ArgumentParser(description="Build theorycraft skill packages")
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("skill_dir", nargs="?", type=Path, help="Path to a skill directory (e.g. skills/theorycraft-architecture)")
    group.add_argument("--all", action="store_true", help="Build all skills and the suite bundle")
    parser.add_argument("--output", "-o", type=Path, default=Path("."), help="Output directory (default: current directory)")
    parser.add_argument("--opencode", action="store_true", help="Also install skills into .opencode/skills/ for opencode")
    args = parser.parse_args()

    output_dir = args.output.resolve()
    output_dir.mkdir(parents=True, exist_ok=True)

    if args.all:
        print("Building all skills...")
        built = build_all(output_dir, opencode=args.opencode)
        print(f"\nBuilt {len(built)} skills.")
        suite = build_suite_bundle(built, output_dir)
        print(f"Suite bundle: {suite}")
        if args.opencode:
            opencode_bundle = build_opencode_bundle(output_dir)
            print(f"Opencode bundle: {opencode_bundle}")
    else:
        skill_dir = args.skill_dir.resolve()
        if not skill_dir.is_dir():
            raise SystemExit(f"Error: {skill_dir} is not a directory")
        print(f"Building {skill_dir.name}...")
        build_skill(skill_dir, output_dir)
        if args.opencode:
            install_to_opencode(skill_dir)


if __name__ == "__main__":
    main()
