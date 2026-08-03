# 06 - ucontrol pathfind（寻路移动）

## 导出格式

```
ucontrol pathfind x y 0 0 0
```

## 参数

| 参数 | 说明 |
|------|------|
| x | 目标位置的 X 坐标（tile 坐标） |
| y | 目标位置的 Y 坐标（tile 坐标） |
| p3 ~ p5 | 无实际用途，填 0 |

## 坐标说明

x、y 参数为 **tile 坐标**，处理器内部通过世界坐标转换（`World.unconv`）乘以 tilesize（8）转换为像素坐标。

## 功能

使用寻路算法移动到目标坐标。与 move 不同，pathfind 会为地面单位计算绕过障碍物的路径。

## 源码实现

1. 设置控制状态为 pathfind（`ai.control = pathfind`）
2. 设置移动目标坐标（`ai.moveX = x`，`ai.moveY = y`）
3. 在 LogicAI 的更新移动（updateMovement）中，根据单位类型采取不同策略：
   - **飞行单位**：直接移动到目标（moveTo），与 move 行为相同
   - **地面单位**：使用寻路路径获取（controlPath.getPathPosition）获取路径节点，沿路径逐段移动

## 与 move 的区别

| 特性 | move | pathfind |
|------|------|----------|
| 飞行单位 | 直线移动 | 直线移动（行为相同） |
| 地面单位 | 直线移动，可能卡墙 | 绕过障碍物寻路移动 |
| 性能开销 | 低 | 较高（需计算路径） |

- **move** 是直线移动，地面单位遇到墙壁等障碍物时可能卡住
- **pathfind** 会为地面单位计算绕行路径，避免卡墙

## 注意事项

- 旧版本中的 `pathfind` 实际执行的是 `autoPathfind` 的功能（自动寻路至敌方核心）
- 新版本中 `pathfind` 已改为按指定坐标寻路。如果导入旧版本的处理器代码，旧的 `pathfind` 指令会寻路至坐标 (0, 0)

---

