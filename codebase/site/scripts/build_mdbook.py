#!/usr/bin/env python3
"""Generate mdBook source directory from matrix files and existing handbooks.

Scans 矩陣/*.md for building metadata, matches against existing handbook files
in codebase/建築/, and generates a clean book-src/ directory with:
  - SUMMARY.md (sidebar/TOC)
  - intro.md (landing page, modified from 導賞目標建築矩陣.md)
  - Category index pages (lightweight link lists)
  - Copies of all handbook files (with mdBook-safe filenames)

Usage:
    python3 scripts/build_mdbook.py [--root /path/to/repo]

The --root flag defaults to the parent of the script's directory.
"""

import argparse
import os
import re
import shutil
import sys
from pathlib import Path

REPO_ROOT_DEFAULT = Path(__file__).resolve().parent.parent.parent.parent
BOOK_SRC_DIR_NAME = "codebase/site/book-src"
INTRO_SOURCE = "specbase/導賞目標建築矩陣.md"
MATRIX_DIR_NAME = ".crewai/矩陣"
BUILDING_DIR_NAME = "codebase/建築"

MATRIX_FILE_ORDER = ["法定古蹟/建築.md", "樓宇/市區建築.md", "樓宇/新界建築.md"]

CATEGORY_CONFIG = [
    {
        "matrix_file": "法定古蹟/建築.md",
        "subdir": "法定古蹟",
        "group": "法定古蹟",
        "index_dir": "法定古蹟",
        "index_title": "法定古蹟導賞手冊",
        "index_desc": "香港法定古蹟導賞團 — 資料來源：CSDI 開放數據 KML/KMZ",
    },
    {
        "matrix_file": "樓宇/市區建築.md",
        "subdir": "樓宇/市區",
        "group": "樓宇",
        "index_dir": "樓宇-市區",
        "index_title": "樓宇導賞手冊（市區）",
        "index_desc": "香港樓宇導賞團 — 資料來源：差餉物業估價署 RVD (Urban)",
    },
    {
        "matrix_file": "樓宇/新界建築.md",
        "subdir": "樓宇/新界",
        "group": "樓宇",
        "index_dir": "樓宇-新界",
        "index_title": "樓宇導賞手冊（新界）",
        "index_desc": "香港樓宇導賞團 — 資料來源：差餉物業估價署 RVD (NT)",
    },
]


def has_chinese(text: str) -> bool:
    """Check if text contains any CJK Unified Ideograph characters."""
    if not text:
        return False
    for ch in text:
        cp = ord(ch)
        if 0x4E00 <= cp <= 0x9FFF or 0x3400 <= cp <= 0x4DBF or 0x20000 <= cp <= 0x2A6DF:
            return True
    return False


def display_name(name_tc: str, name_en: str) -> str:
    """Determine the display name for a building.

    Rule: If 中文名稱 contains Chinese characters, use it.
    Otherwise, fall back to 英文名稱.
    """
    if has_chinese(name_tc):
        return name_tc.strip()
    if name_en and name_en.strip():
        return name_en.strip()
    return (name_tc or "").strip() or "未命名"


def split_matrix_row(line: str) -> list:
    """Split a Markdown table row on | (respecting \\| escapes)."""
    parts = re.split(r"(?<!\\)\|", line)
    parts = parts[1:-1]
    return [p.strip().replace("\\|", "|") for p in parts]


def extract_link_path(link_cell: str) -> str | None:
    """Extract the file path from a 歷史檔案（連結） cell.

    Expected format: [`歷史檔案（連結）`](codebase/建築/...)
    The path itself may contain parentheses (e.g. 00018-侯王古廟(九龍城).md),
    so we greedily match up to the final .md).
    """
    m = re.search(r"\]\((.+\.md)\)", link_cell)
    if m:
        return m.group(1)
    return None


def sanitize_for_mdbook(filename: str) -> str:
    """Sanitize a filename to be safe in mdBook SUMMARY.md links.

    Removes/replaces characters that break Markdown link syntax: ( ) ' & + @ , |
    and various CJK punctuation. Keeps CJK chars, alphanumerics, - _ .
    """
    sanitized = re.sub(
        r"[^\u4e00-\u9fff\u3400-\u4dbf\U00020000-\U0002a6df"
        r"\U0002a700-\U0002b73f0-9a-zA-Z._\-]",
        "_",
        filename,
    )
    sanitized = re.sub(r"_+", "_", sanitized)
    sanitized = sanitized.replace("-_", "-").replace("_-", "-")
    sanitized = sanitized.replace("_.", ".")
    return sanitized


def parse_matrix_file(filepath: Path) -> list[dict]:
    """Parse a matrix sub-file, return list of building info dicts.

    Each dict has: N, category, name_tc, name_en, addr_tc, addr_en,
    tag, credibility, completion, link_raw, link_path, display_name
    """
    buildings = []
    with open(filepath, "r", encoding="utf-8") as f:
        for line in f:
            if not line.startswith("|"):
                continue
            if "編號" in line or "---" in line:
                continue
            parts = split_matrix_row(line)
            if len(parts) < 10 or not parts[0].isdigit():
                continue

            name_tc = parts[2]
            name_en = parts[3]
            link_raw = parts[9]
            link_path = extract_link_path(link_raw)

            buildings.append(
                {
                    "N": parts[0],
                    "category": parts[1],
                    "name_tc": name_tc,
                    "name_en": name_en,
                    "addr_tc": parts[4],
                    "addr_en": parts[5],
                    "tag": parts[6],
                    "credibility": parts[7],
                    "completion": parts[8],
                    "link_raw": link_raw,
                    "link_path": link_path,
                    "display_name": display_name(name_tc, name_en),
                }
            )
    return buildings


def extract_filename_from_link(link_path: str) -> str | None:
    """Extract the filename from a link path like 建築/樓宇/00001-name.md."""
    if not link_path:
        return None
    return Path(link_path).name


def generate_index_page(
    config: dict, buildings: list[dict], total_count: int
) -> str:
    """Generate a lightweight index page for a category."""
    lines = [
        f"# {config['part_num']}.{config['chapter_num']} {config['index_title']}",
        "",
        f"> {config['index_desc']}",
        "",
        f"> 已完成導賞手冊：**{len(buildings)}** / {total_count} 項",
        "",
        "---",
        "",
    ]

    for b in buildings:
        safe_name = sanitize_for_mdbook(b["handbook_filename"])
        rel_path = f"../建築/{config['subdir']}/{safe_name}"
        name = b["display_name"]
        addr = b["addr_tc"] if b["addr_tc"] and b["addr_tc"] != "待查" else ""
        n_id = str(int(b["N"])).zfill(5)
        if addr:
            lines.append(f"1. [{n_id} - {name}]({rel_path}) — {addr}")
        else:
            lines.append(f"1. [{n_id} - {name}]({rel_path})")

    lines.append("")
    return "\n".join(lines)


def generate_summary(section_data: list[dict]) -> str:
    """Generate SUMMARY.md content with hierarchical numbering."""
    lines = ["# Summary", "", "- [香港建築導賞](intro.md)", ""]

    current_part = None
    for section in section_data:
        if section["part_num"] != current_part:
            current_part = section["part_num"]
            lines.append(f"# {section['part_num']} {section['group']}")
            lines.append("")

        index_path = f"{section['index_dir']}/index.md"
        chapter_prefix = f"{section['part_num']}.{section['chapter_num']}"
        lines.append(f"- [{chapter_prefix} {section['index_title']}]({index_path})")
        for i, entry in enumerate(section["entries"], 1):
            lines.append(
                f"  - [{chapter_prefix}.{i} {entry['name']}]({entry['path']})"
            )
        lines.append("")

    return "\n".join(lines)


def fix_intro_links(intro_content: str) -> str:
    """Replace matrix file links in the intro page with category index links."""
    replacements = {
        "../.crewai/矩陣/法定古蹟/建築.md": "法定古蹟/index.md",
        "../.crewai/矩陣/樓宇/市區建築.md": "樓宇-市區/index.md",
        "../.crewai/矩陣/樓宇/新界建築.md": "樓宇-新界/index.md",
    }
    for old, new in replacements.items():
        intro_content = intro_content.replace(old, new)
    return intro_content


def match_completed_buildings(
    all_buildings: list[dict], building_dir: Path, subdir: str
) -> list[dict]:
    """Filter buildings that have a valid link path and existing handbook file."""
    completed = []
    for b in all_buildings:
        if not b["link_path"]:
            continue
        orig_filename = extract_filename_from_link(b["link_path"])
        if not orig_filename:
            continue
        orig_path = building_dir / subdir / orig_filename
        if orig_path.exists():
            b["handbook_filename"] = orig_filename
            completed.append(b)
    completed.sort(key=lambda x: int(x["N"]))
    return completed


def copy_handbooks(
    completed_buildings: list[dict],
    building_dir: Path,
    subdir: str,
    handbook_dest_dir: Path,
) -> list[dict]:
    """Copy handbook files to book-src, return list of entries for SUMMARY.md."""
    entries = []
    name_collision_check = {}
    for b in completed_buildings:
        orig_filename = b["handbook_filename"]
        safe_filename = sanitize_for_mdbook(orig_filename)
        orig_path = building_dir / subdir / orig_filename
        dest_path = handbook_dest_dir / safe_filename

        if safe_filename in name_collision_check:
            print(
                f"    WARNING: Filename collision after sanitize: {safe_filename}"
                f" (originals: {orig_filename}, {name_collision_check[safe_filename]})"
            )
        name_collision_check[safe_filename] = orig_filename

        shutil.copy2(orig_path, dest_path)

        rel_path = f"建築/{subdir}/{safe_filename}"
        entries.append({"name": b["display_name"], "path": rel_path})
    return entries


def process_category(
    config: dict, matrix_dir: Path, building_dir: Path, book_src: Path
) -> dict | None:
    """Process a single category: parse matrix, match handbooks, generate index + copies."""
    matrix_path = matrix_dir / config["matrix_file"]
    if not matrix_path.exists():
        print(f"  WARNING: Matrix file not found: {matrix_path}")
        return None

    print(f"  Processing {config['matrix_file']}...")

    all_buildings = parse_matrix_file(matrix_path)
    total_count = len(all_buildings)
    print(f"    Matrix entries: {total_count}")

    completed_buildings = match_completed_buildings(
        all_buildings, building_dir, config["subdir"]
    )
    print(f"    Matched: {len(completed_buildings)}")

    index_dir = book_src / config["index_dir"]
    index_dir.mkdir(parents=True, exist_ok=True)
    index_content = generate_index_page(config, completed_buildings, total_count)
    (index_dir / "index.md").write_text(index_content, encoding="utf-8")

    handbook_dest_dir = book_src / "建築" / config["subdir"]
    handbook_dest_dir.mkdir(parents=True, exist_ok=True)
    entries = copy_handbooks(
        completed_buildings, building_dir, config["subdir"], handbook_dest_dir
    )

    return {
        "group": config["group"],
        "part_num": config["part_num"],
        "chapter_num": config["chapter_num"],
        "index_dir": config["index_dir"],
        "index_title": config["index_title"],
        "entries": entries,
        "handbook_count": len(completed_buildings),
    }


def main():
    parser = argparse.ArgumentParser(
        description="Build mdBook source directory from matrix and handbooks"
    )
    parser.add_argument(
        "--root",
        type=Path,
        default=REPO_ROOT_DEFAULT,
        help="Repository root directory (default: parent of script dir)",
    )
    args = parser.parse_args()

    repo_root = args.root.resolve()
    matrix_dir = repo_root / MATRIX_DIR_NAME
    building_dir = repo_root / BUILDING_DIR_NAME
    intro_source = repo_root / INTRO_SOURCE
    book_src = repo_root / BOOK_SRC_DIR_NAME

    if not matrix_dir.exists():
        print(f"ERROR: Matrix directory not found: {matrix_dir}", file=sys.stderr)
        sys.exit(1)
    if not building_dir.exists():
        print(f"ERROR: Building directory not found: {building_dir}", file=sys.stderr)
        sys.exit(1)

    print(f"Repository root: {repo_root}")
    print(f"Building mdBook source in: {book_src}")
    print()

    if book_src.exists():
        print(f"  Removing existing {book_src.name}/")
        shutil.rmtree(book_src)
    book_src.mkdir(parents=True)

    total_handbooks = 0
    section_data = []

    current_group = None
    part_num = 0
    chapter_num = 0

    for config in CATEGORY_CONFIG:
        if config["group"] != current_group:
            current_group = config["group"]
            part_num += 1
            chapter_num = 0
        chapter_num += 1
        config["part_num"] = part_num
        config["chapter_num"] = chapter_num

        result = process_category(config, matrix_dir, building_dir, book_src)
        if result is None:
            continue
        total_handbooks += result["handbook_count"]
        section_data.append(result)

    if intro_source.exists():
        intro_content = intro_source.read_text(encoding="utf-8")
        intro_content = fix_intro_links(intro_content)
        (book_src / "intro.md").write_text(intro_content, encoding="utf-8")
        print(f"\n  Intro page: {intro_source.name} -> intro.md (links fixed)")
    else:
        print(f"\n  WARNING: Intro source not found: {intro_source}")

    summary_content = generate_summary(section_data)
    (book_src / "SUMMARY.md").write_text(summary_content, encoding="utf-8")

    print(f"\n{'='*50}")
    print(f"  Total handbooks included: {total_handbooks}")
    print(f"  SUMMARY.md entries: {sum(len(s['entries']) for s in section_data)}")
    print(f"  Output: {book_src}")
    print(f"{'='*50}")
    print(f"\nNext step: mdbook build {repo_root / 'codebase' / 'site'}")


if __name__ == "__main__":
    main()
