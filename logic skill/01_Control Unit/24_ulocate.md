# 24 - ulocate（单位定位）

## 导出格式

```
ulocate locate flag enemy ore outX outY outFound outBuild
```

共 9 个 token。所有参数在导出时始终全部写出，无论 locate 模式是什么。

## 参数说明

| 参数位置 | 参数名   | 类型     | 说明                                                   |
| -------- | -------- | -------- | ------------------------------------------------------ |
| p1       | locate   | LLocate  | 定位模式（见下方可选值）                               |
| p2       | flag     | BlockFlag | 建筑类型标记。**必须是有效的 BlockFlag 枚举值**（如 `core`、`battery`），即使 locate 模式不是 building 也必须填写有效值，否则导入时 `BlockFlag.valueOf()` 会抛出异常导致灰色积木 |
| p3       | enemy    | 数值     | 是否搜索敌方：1=true（搜索敌方），0=false（搜索己方） |
| p4       | ore      | Content  | 矿物类型（仅 ore 模式使用，如 `@copper`）              |
| p5       | outX     | 输出变量 | 输出：找到目标的 X 坐标                                 |
| p6       | outY     | 输出变量 | 输出：找到目标的 Y 坐标                                 |
| p7       | outFound | 输出变量 | 输出：是否找到（1=找到，0=未找到）                     |
| p8       | outBuild | 输出变量 | 输出：找到的建筑引用（仅 building/damaged 模式有效）   |

> **导入陷阱**：在 ore/spawn/damaged 模式下，flag 参数虽然不参与逻辑运算，但解析时仍会调用 `BlockFlag.valueOf()`。如果填 `0` 或其他非法值，会导致整条指令变为 InvalidStatement（灰色积木）。正确做法是始终填写一个有效的 BlockFlag 值（如 `core`）。

### 定位模式（LLocate）可选值

| 模式       | 说明                                       |
| ---------- | ------------------------------------------ |
| building   | 定位建筑                                   |
| ore        | 定位矿脉                                   |
| spawn      | 定位出生点                                 |
| damaged    | 定位受损建筑                               |

### 建筑类型（BlockFlag）可选值

| 建筑类型 | 说明       |
| -------- | ---------- |
| core     | 核心       |
| storage  | 仓储       |
| generator | 发电设施  |
| turret   | 炮塔       |
| factory  | 工厂       |
| repair   | 维修站     |
| battery  | 电池       |
| reactor  | 反应堆     |
| drill    | 钻头       |
| shield   | 力场投影器 |

## 功能说明

以当前绑定的单位（`@unit`）为中心，根据指定模式定位最近的目标建筑或资源，并输出其坐标、是否找到以及建筑引用。

## 源码实现要点

- **定位逻辑**：以 `@unit` 为中心，按照不同模式搜索目标。
- **距离规则**：
  - **友方建筑**（building 模式，enemy=0）：始终返回最近的符合条件的友方建筑，无范围限制。
  - **敌方建筑**（building 模式，enemy=1）：搜索所有敌方建筑，坐标（outX、outY）和是否找到（outFound）始终输出。但建筑引用（outBuild）仅在单位处于 `max(unit.range(), buildingRange)`（buildingRange=220 像素=27.5 格）范围内时才输出，否则 outBuild 为 null。
  - **矿物**（ore 模式）：返回最近的指定类型矿脉。
  - **出生点**（spawn 模式）：返回最近的敌方出生点。
  - **受损建筑**（damaged 模式）：返回最近的己方受损建筑。
- **缓存机制**：使用缓存机制，在 **40 tick** 内重复执行相同的 ulocate 指令会返回缓存结果。

## 注意事项

- ulocate 是 **单位控制语句**，会通过 `checkLogicAI()` 将单位标记为被逻辑控制，并刷新控制计时器（`controlTimer = logicControlTimeout`，即 10 秒）。
- 坐标输出（outX、outY）为 **tile 坐标**（瓦片坐标），处理器内部会通过世界坐标转换（`World.unconv`，即乘以 tilesize=8）转为像素坐标。
- **重要**：游戏内编辑器中，"是否搜索敌方"默认为 true（1）。如果需要搜索己方建筑，必须将该参数改为 0/false。
- flag 参数仅在 building 模式下有效；矿物类型（ore）参数仅在 ore 模式下有效。其他模式下这些参数被忽略。
- outBuild 输出在 building 和 damaged 模式下返回建筑引用，在 ore 和 spawn 模式下通常为 null。
- 由于缓存机制，如果需要实时获取最新目标，需要间隔超过 40 tick 或改变搜索参数。
- 敌方建筑搜索中，outBuild（建筑引用）有范围限制（`max(unit.range(), buildingRange)`，buildingRange=220 像素），但 outX/outY/outFound 不受此限制。友方建筑的 outBuild 始终输出，不受范围限制。

## 未验证内容

- 无

