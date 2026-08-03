# 23 - uradar（单位雷达搜索）

## 导出格式

```
uradar target1 target2 target3 sort 0 order output
```

## 参数说明

| 参数位置 | 参数名   | 类型     | 说明                                                         |
| -------- | -------- | -------- | ------------------------------------------------------------ |
| p1       | target1  | RadarTarget | 第一个筛选器                                                 |
| p2       | target2  | RadarTarget | 第二个筛选器                                                 |
| p3       | target3  | RadarTarget | 第三个筛选器                                                 |
| p4       | sort     | RadarSort | 排序依据                                                     |
| p5       | -        | -        | 占位符，固定为 0（源码中为 radar 字段，构造时设为 "0"）      |
| p6       | order    | 数值     | 排序方向：0=反序（最远/最低优先），1=正序（最近/最高优先）   |
| p7       | output   | 输出变量 | 输出：搜索到的目标单位引用，未找到则为 null                 |

### 筛选器（RadarTarget）可选值

| 筛选器    | 说明                   |
| --------- | ---------------------- |
| any       | 任意单位               |
| enemy     | 敌方单位               |
| ally      | 友方单位               |
| player    | 玩家单位               |
| attacker  | 攻击型单位             |
| flying    | 飞行单位               |
| boss      | Boss 单位              |
| ground    | 地面单位               |

### 排序依据（RadarSort）可选值

| 排序依据   | 说明         |
| ---------- | ------------ |
| distance   | 距离         |
| health     | 当前血量     |
| shield     | 护盾         |
| armor      | 装甲         |
| maxHealth  | 最大血量     |

## 功能说明

以当前绑定的单位（`@unit`）为中心，在其雷达范围内搜索符合筛选条件的单位，并按指定方式排序后返回最优先的一个目标。三个筛选器之间为 **AND（与）** 关系，即目标单位必须同时满足所有筛选条件才会被选中。

## 源码实现要点

- **搜索中心**：以 `@unit` 为中心进行搜索，搜索范围为单位的雷达范围。
- **筛选逻辑**：三个筛选器（target1、target2、target3）为 AND 关系，单位必须同时满足所有三个条件才被纳入候选。
- **排序逻辑**：根据 sort 指定的属性对候选单位排序，order 决定排序方向：
  - order=0：反序，返回排序值最小/最远的单位（如 distance 返回最远的）。
  - order=1：正序，返回排序值最大/最近的单位（如 distance 返回最近的）。
- **指令复用**：底层复用 `RadarI` 指令实现，但搜索来源固定为 `@unit`（而非雷达建筑）。
- **缓存机制**：使用 LogicAI 的 radars 缓存集。在 **40 tick** 内重复执行相同的 uradar 指令会返回缓存的旧结果，而不是重新搜索。这避免了高频搜索带来的性能开销。

## 注意事项

- uradar 是 **单位控制语句**，会通过 `checkLogicAI()` 将单位标记为被逻辑控制。但与 ucontrol/ulocate 不同，uradar **不会刷新控制计时器**（`controlTimer`），因此如果仅使用 uradar 而不执行其他 ucontrol/ulocate 指令，单位将在 10 秒后恢复原 AI。
- 由于缓存机制，如果需要实时获取最新目标，需要间隔超过 40 tick 或改变筛选条件。
- 当未找到符合条件的单位时，output 输出为 null。
- 三个筛选器是 AND 关系，如果某个筛选器设为 `any`，则该条件不产生限制（等同于"不限"）。
- order=0 和 order=1 的语义：
  - 对于 distance：0=最远，1=最近。
  - 对于 health/shield/armor/maxHealth：0=最低，1=最高。

## 未验证内容

- 无

