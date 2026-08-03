# 15 - ucontrol payEnter（进入建筑）

## 导出格式

```
ucontrol payEnter 0 0 0 0 0
```

共7个token：`ucontrol` `payEnter` `<p1=0>` `<p2=0>` `<p3=0>` `<p4=0>` `<p5=0>`

## 参数说明

| 参数 | 位置 | 类型 | 说明 |
|------|------|------|------|
| p1 | p1 | - | 无参数，固定为0 |
| p2 | p2 | - | 无参数，固定为0 |
| p3 | p3 | - | 无参数，固定为0 |
| p4 | p4 | - | 无参数，固定为0 |
| p5 | p5 | - | 无参数，固定为0 |

## 功能说明

让单位进入当前所在位置的建筑，进行交互操作。

典型用途包括：mono 进入修复厂维修、大型单位进入载荷工厂等。

## 源码实现要点

- 获取当前位置建筑（`world.buildWorld`）
- 检查建筑是否同队且可选择控制进入（`canControlSelect`）
- 满足条件后调用单位建筑控制选择（`Call.unitBuildingControlSelect`），让单位进入该建筑

## 注意事项

- 单位必须位于目标建筑上方（即单位当前位置存在建筑）才能触发进入
- 建筑必须与单位同队，且支持控制进入功能（`canControlSelect`）
- payEnter 会触发控制状态（通过 `checkLogicAI()` 将单位标记为被逻辑控制），与所有 ucontrol 子指令行为一致。

## 源码验证结论

- 通过源码验证，以下建筑实现了 `canControlSelect` 且支持 payEnter：
  - **载荷建筑（PayloadBlock）**：如载荷装载器、载荷卸载器等。条件：单位非核心产出（`!spawnedByCore`）、允许进入载荷（`allowedInPayloads`）、建筑当前无载荷（`payload == null`）、单位接受载荷（`acceptUnitPayload`）、单位站在建筑上。
  - **载荷传送带（PayloadConveyor）**：条件类似，额外限制单位大小（`unit.hitSize / tilesize <= payloadLimit`）。
  - **核心（CoreBlock）**：`canControlSelect` 返回 `player.isPlayer()`，逻辑控制的单位不是玩家单位，因此 **核心不支持逻辑 payEnter**。
  - 其他默认建筑：`canControlSelect` 返回 `false`，不支持 payEnter。

