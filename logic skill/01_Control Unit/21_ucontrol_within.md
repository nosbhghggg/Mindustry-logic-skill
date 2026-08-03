# 21 - within（范围检测）

## 导出格式

```
ucontrol within x y radius result
```

## 参数说明

| 参数位置 | 参数名 | 类型 | 说明                         |
| -------- | ------ | ---- | ---------------------------- |
| p1       | x      | 数值 | 目标位置的 tile 坐标 X       |
| p2       | y      | 数值 | 目标位置的 tile 坐标 Y       |
| p3       | radius | 数值 | 检测半径（tile 单位）        |
| p4       | result | 输出变量 | 输出：在范围内返回 1，否则返回 0 |
| p5       | -      | -    | 占位符，固定为 0             |

## 功能说明

检测当前绑定的单位是否在指定坐标的指定半径范围内，结果输出为 1（在范围内）或 0（不在范围内）。

## 源码实现要点

- **范围检测**：调用单位的范围检查方法（`unit.within`），判断单位与目标坐标的距离是否在指定半径内。
- **结果输出**：在范围内则 `result = 1`，不在范围内则 `result = 0`。

## 注意事项

- 坐标参数 x、y 均为 **tile 坐标**，处理器内部会通过世界坐标转换（`World.unconv`，即乘以 tilesize=8）转为像素坐标。
- within 会触发控制状态（通过 `checkLogicAI()` 将单位标记为被逻辑控制），与所有 ucontrol 子指令行为一致。这是因为 within 属于 ucontrol 指令，在执行前会调用 `checkLogicAI()` 并刷新控制计时器。
- **替代方案**：如果只需要检查距离而不想触发控制状态，应手动用 `op len` 计算单位与目标点的距离，再与半径比较：
  ```
  # 手动距离检查（不触发控制）
  op sub dx @unitx targetX
  op sub dy @unity targetY
  op len dist dx dy
  op lessThan result dist radius
  ```
- 适合在已经控制单位的场景下使用，避免在仅需信息查询时意外控制单位。

## 未验证内容

- 无

