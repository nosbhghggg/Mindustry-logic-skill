# 05 - ucontrol approach（接近到一定半径）

## 导出格式

```
ucontrol approach x y radius 0 0
```

## 参数

| 参数 | 说明 |
|------|------|
| x | 目标位置的 X 坐标（tile 坐标） |
| y | 目标位置的 Y 坐标（tile 坐标） |
| radius | 接近半径（单位会移动到距离目标此半径范围内停止） |
| p4 ~ p5 | 无实际用途，填 0 |

## 坐标说明

x、y 参数为 **tile 坐标**，处理器内部通过世界坐标转换（`World.unconv`）乘以 tilesize（8）转换为像素坐标。

## 功能

移动单位到距离目标 (x, y) 指定 radius 范围内即停止。适用于需要单位靠近某个目标但不必精确到达目标点的情况。

approach 会触发控制状态（通过 `checkLogicAI()` 将单位控制器替换为 LogicAI 并刷新 10 秒控制计时器 `controlTimer`）。

## 源码实现

1. 设置控制状态为 approach（`ai.control = approach`）
2. 设置移动目标坐标（`ai.moveX = x`，`ai.moveY = y`）
3. 设置接近半径（`ai.moveRad = radius`）
4. 在 LogicAI 的更新移动（updateMovement）中，调用移动到目标（moveTo），参数为：
   - 目标位置：moveX, moveY
   - 实际停止距离：**moveRad - 7**（比指定的 radius 小 7）
   - 接近精度：7

> 注意：源码中实际停止距离为 `moveRad - 7f`，即单位会在距离目标 `radius - 7` 的位置就停止移动。

## 与 move 的区别

| 特性 | move | approach |
|------|------|----------|
| 停止位置 | 精确到目标点（精度 1 格） | 距离目标 radius 范围内 |
| 到达精度 | 1 格 | 7 格 |
| 减速范围 | 30 格 | 7 格 |
| 适用场景 | 需要精确到达某点 | 需要靠近但不必到达 |

- **move** 会一直移动到目标点（精度 1 格），减速范围较大（30 格）
- **approach** 在指定半径外就停止，适用于让单位在安全距离外环绕目标

---

