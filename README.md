# 像素工厂 Logic 编程技能

> 系统性整理 Mindustry（像素工厂）中 Logic 汇编编程的积木用法、源码实现要点、代码实战示例及高级主题。
>
> **注意**：本技能文档需要配合 [Mindustry 游戏源码](https://github.com/Anuken/Mindustry) 一起使用，文档中的源码实现分析均基于游戏源码。

## 当前进度

> **重要**：当前技能**仅完善了兵控（单位控制）部分的训练逻辑**，包含完整的单位绑定、控制、雷达、定位指令文档及 12 个实战案例。其他分类虽有积木文档，但**尚未编写针对性的训练逻辑**。

| 分类 | 积木文档 | 训练逻辑 | 说明 |
|------|----------|----------|------|
| 控制单位（01_Control Unit） | ✅ 24 个 | ✅ 12 个实战案例 | ubind、ucontrol（21 子指令）、uradar、ulocate |
| 控制程序（02_Control Flow） | ✅ 5 个 | ❌ 暂无 | noop、wait、stop、end、jump |
| 操作（03_Operations） | ✅ 6 个 | ❌ 暂无 | set、op、select、lookup、packcolor、unpackcolor |
| 输入输出（04_IO） | ✅ 6 个 | ❌ 暂无 | read、write、draw、print、printchar、format |
| 控制方块（05_Block Control） | ✅ 6 个 | ❌ 暂无 | getlink、control、radar、sensor、drawflush、printflush |
| 世界（06_World） | ✅ 26 个 | ❌ 暂无 | setrate、getblock、setblock、spawn 等世界处理器专属指令 |

## 目录结构

```
mindustry logic skill/
├── .github/workflows/merge-docs.yml  # 自动整合 workflow
├── .gitignore
├── AGENTS.md                         # 项目规范
├── README.md
├── merge_docs.py                     # 文档整合脚本
└── logic skill/
    ├── 01_Logic入门与学习大纲.md       # Logic 基础与学习大纲
    ├── 01_Control Unit/               # 控制单位（24 个指令）
    ├── 02_Control Flow/               # 控制程序（5 个指令）
    ├── 03_Operations/                 # 操作（6 个指令）
    ├── 04_IO/                         # 输入输出（6 个指令）
    ├── 05_Block Control/              # 控制方块（6 个指令）
    ├── 06_World/                      # 世界处理器专属（26 个指令）
    └── 07_实战案例/                    # 兵控实战案例（12 个）
```

## 文档整合

运行 `python merge_docs.py` 可将 `logic skill/` 下所有 .md 文件按编号顺序整合为一个文件，输出到 `output/Logic教学文档整合.md`。
