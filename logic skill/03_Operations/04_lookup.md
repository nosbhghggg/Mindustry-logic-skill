# 04 - lookup（内容查找）

## 导出格式

```
lookup <type> <result> <id>
```

## 参数说明

| 参数 | 说明 |
|------|------|
| type | 内容类型。可选值：`block`、`unit`、`item`、`liquid`、`team` |
| result | 结果变量名。查找结果（content 对象）写入此变量 |
| id | 逻辑 ID（logic ID）。从 0 开始的整数索引 |

## 功能说明

**用途：通过逻辑 ID 查找游戏内容对象（方块、单位、物品、液体或队伍），返回可用于 sensor、ucontrol 等指令的 content 引用。**

`lookup` 是连接"数字"与"游戏内容对象"的桥梁。许多指令需要 content 对象作为参数（如 `ubind @mono` 中的 `@mono` 就是 content），而 `lookup` 允许你通过数字 ID 动态获取这些对象。

### 可查找的内容类型

| 类型 | 说明 | 数量变量 | ID 范围 |
|------|------|----------|---------|
| `block` | 方块类型（如传送带、炮塔等） | `@blockCount` | 0 ~ @blockCount-1 |
| `unit` | 单位类型（如 mono、poly 等） | `@unitCount` | 0 ~ @unitCount-1 |
| `item` | 物品类型（如铜、铅等） | `@itemCount` | 0 ~ @itemCount-1 |
| `liquid` | 液体类型（如水、矿渣等） | `@liquidCount` | 0 ~ @liquidCount-1 |
| `team` | 队伍 | 无 | 0 ~ 255 |

### 使用示例

```
# 查找 ID 为 0 的物品，存入 myItem
lookup item myItem 0

# 遍历所有方块类型
set _i 0
loop:
op lessThan _cond _i @blockCount
jump skip equal _cond 0
lookup block _result _i
# 此处可对 _result 进行操作，如 sensor 读取信息
op add _i _i 1
jump loop always
skip:
end
```

## 源码实现要点

### 语句定义（LookupStatement）

`LookupStatement` 包含三个字段：`type`（ContentType 枚举）、`result`、`id`。构建指令时生成 `LookupI`：`new LookupI(builder.var(result), builder.var(id), type)`。

### 指令执行（LookupI.run）

核心逻辑：

```java
dest.setobj(logicVars.lookupContent(type, from.numi()));
```

- 将 `id` 转为整数（`from.numi()`），调用 `GlobalVars.lookupContent(type, id)` 查找内容
- 结果通过 `setobj()` 写入，始终为对象类型
- 如果 ID 超出范围，返回 null 对象

### lookupContent 方法

查找逻辑分两种情况：

1. **team 类型**：直接从 `Team.all[id]` 数组中取，ID 范围 0~255。队伍不是真正的 content，但可以在此查找
2. **其他类型**：从 `logicIdToContent` 数组中取。这个数组以逻辑 ID 为索引，存储对应的 `UnlockableContent` 对象

### 逻辑 ID（logic ID）与内容 ID（content ID）的区别

- **逻辑 ID**：由 `logicids.dat` 文件定义，专门供 Logic 使用。从 0 开始连续编号，是 `lookup` 指令使用的 ID
- **内容 ID**：游戏内部的 content ID（`content.id`），用于游戏其他系统。与逻辑 ID **不一定相同**

游戏在初始化时读取 `logicids.dat`，建立逻辑 ID 到 content 的映射表（`logicIdToContent`）和反向映射表（`contentIdToLogicId`）。

### 数量变量

对于 block、unit、item、liquid 四种类型，系统会注册对应的数量变量（`@blockCount`、`@unitCount`、`@itemCount`、`@liquidCount`），表示可查找的 content 总数。team 类型没有数量变量，但 ID 范围固定为 0~255。

## 注意事项

- **结果为对象类型**：`lookup` 的结果通过 `setobj()` 写入，是 content 对象引用，不是数字。可以与 `@copper` 等 content 常量用 `op equal` 比较
- **ID 超范围返回 null**：如果 ID 为负数或超出数量范围，结果为 null 对象。对其进行 `num()` 取值返回 0
- **逻辑 ID 不等于内容 ID**：不要将 `sensor` 读到的 `@id` 直接用作 `lookup` 的 ID。`@id` 是内容 ID，`lookup` 需要的是逻辑 ID
- **team 查找的特殊性**：team 不是 content，但可以在 `lookup` 中查找。查找结果可以用于需要 team 参数的指令
- **遍历安全**：使用 `@xxxCount` 变量作为遍历上限，可以安全遍历所有 content，无需硬编码数量
- **content 可能因模组而变**：不同模组环境下的逻辑 ID 映射不同，`@xxxCount` 的值也会变化。始终使用数量变量而非硬编码

## 未验证内容

无
