# -*- coding: utf-8 -*-
"""
像素工厂 Logic 教学文档整合脚本

扫描规则（遵循 AGENTS.md 规范）：
1. 先扫描当前层级的单个文件（按文件编号排序）
2. 再扫描文件夹（按文件夹编号排序），递归进入文件夹内部按同样规则扫描

用法：python merge_docs.py
输出：output/Logic教学文档整合.md
"""

import re
from pathlib import Path

SRC_DIR = Path(__file__).parent / "logic skill"
OUTPUT_DIR = Path(__file__).parent / "output"
OUTPUT_FILE = OUTPUT_DIR / "Logic教学文档整合.md"


def extract_number(name: str) -> int:
    match = re.match(r"^(\d+)", name)
    return int(match.group(1)) if match else 9999


def scan_and_collect(directory: Path) -> list[tuple[str, str]]:
    entries = [e for e in directory.iterdir() if not e.name.startswith(".")]

    md_files = sorted(
        [e for e in entries if e.is_file() and e.suffix == ".md"],
        key=lambda e: extract_number(e.name),
    )
    subdirs = sorted(
        [e for e in entries if e.is_dir()],
        key=lambda e: extract_number(e.name),
    )

    result = []
    for f in md_files:
        rel_path = f.relative_to(SRC_DIR)
        try:
            content = f.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            content = f.read_text(encoding="gbk")
        result.append((str(rel_path), content))

    for d in subdirs:
        result.extend(scan_and_collect(d))

    return result


def build_merged_doc(items: list[tuple[str, str]]) -> str:
    parts = []
    for _, content in items:
        parts.append(content)
    return "\n".join(parts)


def main():
    print(f"源目录: {SRC_DIR}")
    print(f"输出文件: {OUTPUT_FILE}")

    if not SRC_DIR.exists():
        print(f"[错误] 源目录不存在: {SRC_DIR}")
        return

    items = scan_and_collect(SRC_DIR)

    print(f"扫描完成，共找到 {len(items)} 个 .md 文件\n")
    for i, (rel_path, _) in enumerate(items, 1):
        print(f"  {i:>3}. {rel_path}")

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    merged = build_merged_doc(items)
    OUTPUT_FILE.write_text(merged, encoding="utf-8")

    total_lines = merged.count("\n") + 1
    print(f"\n整合完成！")
    print(f"  文件数: {len(items)}")
    print(f"  总行数: {total_lines:,}")
    print(f"  输出到: {OUTPUT_FILE}")


if __name__ == "__main__":
    main()
