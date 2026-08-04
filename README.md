# 像素工厂 Logic 编程技能

> 本项目系统性整理了 Mindustry（像素工厂）中 Logic 汇编编程的所有积木用法、源码实现要点、代码实战示例及高级主题。

## 当前进度

| 分类 | 内容 | 状态 |
|------|------|------|
| 控制单位（01_Control Unit） | ubind、ucontrol（21 个子指令）、uradar、ulocate | ✅ 已完成 |
| 控制程序（02_Control Flow） | noop、wait、stop、end、jump | ✅ 已完成 |
| 操作（03_Operations） | set、op、select、lookup、packcolor、unpackcolor | ✅ 已完成 |
| 输入输出（04_IO） | read、write、draw、print、printchar、format | ✅ 已完成 |
| 控制方块（05_Block Control） | getlink、control、radar、sensor、drawflush、printflush | ✅ 已完成 |
| 世界（06_World） | setrate、getblock、setblock、spawn 等 26 个世界处理器专属指令 | ✅ 已完成 |
| 实战案例（07_实战案例） | 兵控逻辑、挖矿逻辑、多核优化、编队控制等 | ✅ 已完成 |

> **注意**：当前技能仅完善了**兵控（单位控制）**部分的训练逻辑，包含完整的单位绑定、控制、雷达、定位指令文档及 14 个实战案例。其他分类（控制程序、操作、IO、方块控制、世界）虽已有积木文档，但尚未编写针对性的训练逻辑。

## 目录结构

```
mindustry logic skill/
├── merge_docs.py                    # 文档整合脚本
├── README.md
├── AGENTS.md                        # 项目规范
├── .github/workflows/merge-docs.yml # 自动整合 workflow
└── logic skill/
    ├── 00_Logic入门与学习大纲.md     # Logic 基础与学习大纲
    ├── 08_学习记录.md                # 学习总结
    ├── 01_Control Unit/             # 控制单位（24 个指令）
    ├── 02_Control Flow/             # 控制程序（5 个指令）
    ├── 03_Operations/               # 操作（6 个指令）
    ├── 04_IO/                       # 输入输出（6 个指令）
    ├── 05_Block Control/            # 控制方块（6 个指令）
    ├── 06_World/                    # 世界处理器专属（26 个指令）
    └── 07_实战案例/                  # 实战案例（14 个）
```

## 文档整合

运行 `python merge_docs.py` 可将 `logic skill/` 下所有 .md 文件按编号顺序整合为一个文件，输出到 `output/Logic教学文档整合.md`。

推送代码后 GitHub Actions 会自动运行整合脚本并提交结果。
