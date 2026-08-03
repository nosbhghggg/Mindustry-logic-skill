# 11 - ucontrol itemDrop（放置物品）

## 导出格式

```
ucontrol itemDrop to amount 0 0 0
```

共7个token：`ucontrol` `itemDrop` `<p1=to>` `<p2=amount>` `<p3=0>` `<p4=0>` `<p5=0>`

## 参数说明

| 参数 | 位置 | 类型 | 说明 |
|------|------|------|------|
| to | p1 | Building / Blocks | 目标建筑；传 `@air` 表示丢弃到地面 |
| amount | p2 | number | 传输的物品数量 |
| p3 | p3 | - | 保留参数，固定为0 |
| p4 | p4 | - | 保留参数，固定为0 |
| p5 | p5 | - | 保留参数，固定为0 |

## 功能说明

让单位将携带的物品传输到目标建筑中，或将物品丢弃到地面（当目标为 `@air` 时）。

## 源码实现要点

- **目标是空气方块时**（`Blocks.air`）：直接清空单位携带物品（`unit.clearItem()`），将物品丢弃到地面
- **目标是建筑时**：
  - 获取建筑（`p1.building()`）
  - 检查建筑是否同队、有效、允许存入（`allowDeposit`）、单位是否在范围内
  - 满足条件后调用传输物品到目标（`Call.transferItemTo`）

## 注意事项

- **距离检查**：逻辑物品传输范围 + 建筑大小 * tileSize / 2（`logicItemTransferRange = 5.625` tiles）。单位必须在范围内才能传输
- **传输超时**：1.5 秒传输延迟（`transferDelay = 60f * 1.5f`），即两次传输之间需要间隔一定时间
- **传输条件**（全部满足才能传输）：
  1. 建筑必须与单位同队
  2. 建筑必须有效（未摧毁）
  3. 建筑必须允许存入物品（`allowDeposit`）
  4. 单位必须在传输范围内
  5. 建筑必须接受该物品类型
- itemDrop 会触发控制状态（通过 `checkLogicAI()` 将单位标记为被逻辑控制），与所有 ucontrol 子指令行为一致。

