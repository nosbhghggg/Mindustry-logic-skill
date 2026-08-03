# 01 - ubind（单位绑定）

## 导出格式

```
ubind <type>
```

## 参数

| 参数 | 说明 |
|------|------|
| type | 绑定目标。可以是 **content类型的单位类型**（如 `@mono`、`@poly`），也可以是 **unit实例变量**（存储了单位引用的变量） |

## 功能

将处理器绑定到一个单位，绑定结果存入环境变量 `@unit`。`@unit` 是所有 `ucontrol` 指令的操作对象——只有先通过 `ubind` 绑定了单位，后续的控制指令才会生效。

---

## 深度分析

### 两种绑定方式

#### 1. content类型绑定（如 `ubind @mono`）

处理器内部维护一个 **binds 数组**，以 `UnitType.id` 为索引。每次执行 `ubind` 时：

- 从队伍数据（team data）的单位缓存（unitCache）中取出该类型的单位列表
- 用一个计数器记录当前取到了第几个，通过 **取模运算**（`binds[type.id] %= seq.size`）实现循环
- 每次执行都取下一个同类型单位，遍历完一遍后从头开始

#### 2. unit实例绑定（如 `ubind myUnit`）

直接将 `@unit` 设置为该变量引用的单位，**不参与 binds 计数器的循环**。这是一种"指定单位"的绑定方式。

### 为什么两行代码能控制所有同类单位？

处理器以极高频率循环执行代码。每轮循环中：

1. `ubind @mono` 取出下一个 mono 单位存入 `@unit`
2. `ucontrol move x y 0 0 0` 控制该单位移动

由于 binds 计数器每轮递增并取模循环，处理器在多轮循环中依次绑定到每一个同类单位，从而实现"批量控制"。

### 绑定计数器的独立性

- 不同 content 类型（如 `@mono` 和 `@omura`）的绑定计数器 **完全独立**，互不影响
- **unit实例绑定不影响 content 类型的循环计数器**。也就是说，`ubind myUnit` 不会打乱 `ubind @mono` 的计数进度

### 绑定顺序的本质

绑定顺序本质上是 **单位的生成顺序**，来源于 `Groups.unit` 的迭代顺序。需要注意的是：

- 单位死亡时，缓存列表使用 **置换删除**（swap and pop）方式移除该单位
- 这种删除方式会将末尾单位移动到被删除位置，**会导致顺序变化**
- 因此在单位频繁死亡/生成时，绑定顺序可能发生跳变

### 绑定限制

- **不能绑定非 logicControllable 的单位**：只有控制器（controller）为 logicControllable 的单位才能被绑定
- **非特权处理器不能绑定敌方单位**：只有特权世界处理器（privileged processor）才能绑定敌方队伍的单位

---

## 重要提示

- **每次 `ubind` 都会覆盖 `@unit`**：之前的绑定结果会丢失。如果需要保留某个单位的引用，应在绑定后立即将其保存到其他变量（如 `set savedUnit @unit`）
- `@unit` 的初始值为 `null`，在首次 `ubind` 之前，所有 `ucontrol` 指令都不会产生效果

---

## 关于绑定玩家单位

可以绑定玩家单位到 `@unit`（获取引用），但能否实际控制取决于 `isLogicControllable` 检查。

## 源码验证结论

- ubind 可以绑定玩家控制的单位（`@unit` 变量会指向该单位），但所有 ucontrol/uradar/ulocate 指令对玩家单位无效。原因是 `checkLogicAI()` 会检查 `unit.controller().isLogicControllable()`，而 `Player.isLogicControllable()` 返回 `false`。
- 当玩家正在控制的单位被 ubind 绑定后，若玩家停止控制（如切到其他单位或死亡），单位恢复默认 AI，此时逻辑指令才能生效。

---

