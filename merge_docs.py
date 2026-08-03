# -*- coding: utf-8 -*-
"""
像素工厂 Logic 教学文档整合脚本

扫描规则（遵循 AGENTS.md 规范）：
1. 先扫描当前层级的单个文件（按文件编号排序）
2. 再扫描文件夹（按文件夹编号排序），递归进入文件夹内部按同样规则扫描

用法：python merge_docs.py
输出：output/Logic教学文档整合.md
"""

import os
import re
from pathlib import Path

# 源目录与输出路径
SRC_DIR = Path(__file__).parent / "logic skill"
OUTPUT_DIR = Path(__file__).parent / "output"
OUTPUT_FILE = OUTPUT_DIR / "Logic教学文档整合.md"

# 分隔线
SEPARATOR = "\n\n---\n\n"


def extract_number(name: str) -> int:
    """从文件/文件夹名中提取开头的数字用于排序，如 '01_ubind' -> 1, '00_Logic' -> 0"""
    match = re.match(r"^(\d+)", name)
    return int(match.group(1)) if match else 9999


def scan_and_collect(directory: Path) -> list[tuple[str, str]]:
    """
    递归扫描目录，按规范顺序收集 (相对路径, 文件内容) 列表。

    扫描顺序：
    1. 先扫描当前层级的 .md 文件（按编号排序）
    2. 再扫描子文件夹（按编号排序），递归处理
    """
    entries = list(directory.iterdir())
    # 过滤隐藏文件和 .git 等
    entries = [e for e in entries if not e.name.startswith(".")]

    # 分离文件和文件夹
    md_files = sorted(
        [e for e in entries if e.is_file() and e.suffix == ".md"],
        key=lambda e: extract_number(e.name),
    )
    subdirs = sorted(
        [e for e in entries if e.is_dir()],
        key=lambda e: extract_number(e.name),
    )

    result = []

    # 1. 先处理文件
    for f in md_files:
        rel_path = f.relative_to(SRC_DIR)
        try:
            content = f.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            content = f.read_text(encoding="gbk")
        result.append((str(rel_path), content))

    # 2. 再递归处理文件夹
    for d in subdirs:
        result.extend(scan_and_collect(d))

    return result


def build_merged_doc(items: list[tuple[str, str]]) -> str:
    """将收集到的文件内容合并为单个 Markdown 字符串。"""
    parts = []

    # 文档头部标题与说明
    parts.append("# 像素工厂 Logic 编程教学文档整合\n")
    parts.append(f"> 本文档由 `merge_docs.py` 自动生成，共整合 {len(items)} 个文件。")
    parts.append(f"> 扫描规则：先扫描当前层级文件（按编号排序），再扫描文件夹（按编号排序），递归处理。\n")

    # 目录索引
    parts.append("## 目录索引\n")
    for i, (rel_path, _) in enumerate(items, 1):
        # 去掉扩展名作为目录链接
        anchor = rel_path.replace("\\", "/").replace(".md", "")
        parts.append(f"{i}. [{rel_path}](#{anchor.replace('/', '-')})")
    parts.append("")

    # 各文件内容
    for rel_path, content in items:
        parts.append(f'<!-- 文件: {rel_path} -->')
        parts.append(SEPARATOR)
        parts.append(content)
        parts.append("")  # 末尾空行

    return "\n".join(parts)


def main():
    print(f"源目录: {SRC_DIR}")
    print(f"输出文件: {OUTPUT_FILE}")
    print()

    if not SRC_DIR.exists():
        print(f"[错误] 源目录不存在: {SRC_DIR}")
        return

    # 扫描并收集所有文件
    items = scan_and_collect(SRC_DIR)

    print(f"扫描完成，共找到 {len(items)} 个 .md 文件：\n")
    for i, (rel_path, _) in enumerate(items, 1):
        print(f"  {i:>3}. {rel_path}")

    # 合并并写入输出
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    merged = build_merged_doc(items)
    OUTPUT_FILE.write_text(merged, encoding="utf-8")

    # 统计
    total_lines = merged.count("\n") + 1
    total_chars = len(merged)
    print(f"\n整合完成！")
    print(f"  文件数: {len(items)}")
    print(f"  总行数: {total_lines:,}")
    print(f"  总字符: {total_chars:,}")
    print(f"  输出到: {OUTPUT_FILE}")


if __name__ == "__main__":
    main()
