# 04 - sensor（传感器）

> **用途**：读取建筑或单位的属性值，包括物品数量、血量、效率、坐标、队伍等各类可感知属性。

## 导出格式

```
sensor <output> <from> <type>
```

## 参数说明

| 参数 | 类型 | 说明 |
|------|------|------|
| output | 变量名 | 用于存储读取到的属性值 |
| from | 对象引用 | 被感知的建筑或单位引用 |
| type | 属性类型 | LAccess 枚举值（如 `@totalItems`、`@health`）或内容引用（如 `@copper`） |

## 常用可读取属性

### 数值类属性（返回数字）

| 属性 | 说明 | 适用对象 |
|------|------|----------|
| @totalItems | 物品总数 | 建筑 |
| @totalLiquids | 液体总量 | 建筑 |
| @totalPower | 电力状态 | 建筑 |
| @itemCapacity | 物品容量 | 建筑 |
| @liquidCapacity | 液体容量 | 建筑 |
| @powerCapacity | 电力容量 | 建筑 |
| @powerNetStored | 电力网络存储量 | 建筑 |
| @powerNetCapacity | 电力网络总容量 | 建筑 |
| @powerNetIn | 电力网络输入功率 | 建筑 |
| @powerNetOut | 电力网络输出功率 | 建筑 |
| @ammo | 弹药量 | 建筑/单位 |
| @ammoCapacity | 弹药容量 | 建筑/单位 |
| @health | 当前血量 | 建筑/单位 |
| @maxHealth | 最大血量 | 建筑/单位 |
| @heat | 热量 | 建筑/单位 |
| @shield | 护盾 | 建筑/单位 |
| @armor | 护甲 | 建筑/单位 |
| @efficiency | 效率 | 建筑 |
| @progress | 进度 | 建筑/单位 |
| @timescale | 时间缩放 | 建筑 |
| @rotation | 旋转角度 | 建筑/单位 |
| @x | X 坐标（世界坐标） | 建筑/单位 |
| @y | Y 坐标（世界坐标） | 建筑/单位 |
| @range | 射程 | 建筑/单位 |
| @size | 建筑大小（格） | 建筑/单位 |
| @team | 队伍 ID | 建筑/单位 |
| @flag | 标志值 | 建筑/单位 |
| @dead | 是否已死亡（1/0） | 建筑/单位 |
| @solid | 是否实体（1/0） | 建筑 |
| @enabled | 是否启用（1/0） | 建筑 |
| @controlled | 是否被控制（1/0） | 建筑/单位 |
| @shooting | 是否正在射击（1/0） | 建筑/单位 |
| @boosting | 是否加速中（1/0） | 单位 |
| @flying | 是否飞行中（1/0） | 单位 |
| @mining | 是否采矿中（1/0） | 单位 |
| @mineX | 采矿目标 X 坐标 | 单位 |
| @mineY | 采矿目标 Y 坐标 | 单位 |
| @building | 是否建造中（1/0） | 单位 |
| @breaking | 是否拆除中（1/0） | 单位 |
| @speed | 速度 | 单位 |
| @id | 唯一 ID | 建筑/单位 |
| @payloadCount | 载荷数量 | 建筑/单位 |
| @payloadCapacity | 载荷容量 | 建筑/单位 |
| @maxUnits | 最大单位数 | 建筑 |

### 对象类属性（返回对象引用）

| 属性 | 说明 | 适用对象 |
|------|------|----------|
| @type | 建筑类型/单位类型 | 建筑/单位 |
| @firstItem | 第一个物品 | 建筑 |
| @config | 建筑配置 | 建筑 |
| @payloadType | 载荷类型 | 建筑/单位 |
| @name | 名称 | 单位/玩家 |
| @currentAmmoType | 当前弹药类型 | 建筑/单位 |

### 内容类属性（返回指定物品/液体的数量）

当 type 为内容引用（如 `@copper`、`@water`）时，sensor 返回建筑中该物品或液体的存储数量。

| 示例 | 说明 |
|------|------|
| `sensor _result _vault @copper` | 读取仓库中铜的数量 |
| `sensor _result _tank @water` | 读取储罐中水的数量 |
| `sensor _result _vault @titanium` | 读取仓库中钛的数量 |

## 功能说明

`sensor` 指令从指定的建筑或单位读取属性值。type 参数可以是 LAccess 枚举值（以 `@` 前缀表示，如 `@health`）或内容引用（如 `@copper`）。

读取流程：
1. 从 from 变量获取目标对象。
2. 从 type 变量获取感知类型。
3. 如果目标为 null 且感知类型为 `@dead`，直接返回 1（null 对象视为已死亡）。
4. 如果目标实现了 Senseable 接口：
   - 感知类型为 Content（物品/液体/单位类型/方块）：调用 `sense(content)` 返回数值。
   - 感知类型为 LAccess：先调用 `senseObject(la)`，如果返回 `noSensed` 则调用 `sense(la)` 返回数值，否则返回对象。
5. 如果目标未实现 Senseable 但感知类型为 `@size` 或 `@bufferSize`，返回字符串长度或序列大小。
6. 其他情况返回 null。

## 源码实现要点

### SenseI（感知指令）

位于 `LExecutor.java`，核心逻辑如下：

- 从 from 变量获取目标对象，从 type 变量获取感知类型（对象）。
- 特殊处理：目标为 null 且感知类型为 `@dead` 时返回 1。
- 目标实现 Senseable 接口时：
  - Content 类型：调用 `se.sense(co)` 返回数值。
  - LAccess 类型：调用 `se.senseObject(la)`，返回值为 `noSensed` 时改调 `se.sense(la)` 返回数值，否则返回对象引用。
- 目标未实现 Senseable 时，对 `@size`/`@bufferSize` 特殊处理（返回 CharSequence 长度或 Seq 大小），其余返回 null。

### BuildingComp.sense（建筑感知）

位于 `BuildingComp.java`，处理的 LAccess 属性包括：
- 坐标：x, y（通过 `World.conv()` 转换为世界坐标）
- 状态：color, dead, solid, team, health, maxHealth, efficiency, timescale, range, rotation, enabled, controlled
- 物品/液体/电力：totalItems, totalLiquids, totalPower, itemCapacity, liquidCapacity, powerCapacity, powerNetIn, powerNetOut, powerNetStored, powerNetCapacity
- 载荷：payloadCount
- 其他：size, cameraX, cameraY, cameraWidth, cameraHeight

### BuildingComp.senseObject（建筑对象感知）

处理的 LAccess 属性：type（返回 Block）、firstItem（返回第一个物品）、config（返回配置）、payloadType（返回载荷类型）。

### BuildingComp.sense(Content)（建筑内容感知）

- Item 类型：返回建筑中该物品的数量。
- Liquid 类型：返回建筑中该液体的数量。
- UnitType/Block 类型：返回载荷中该单位/方块的数量。

## 注意事项

1. type 参数以 `@` 前缀表示，如 `@health`、`@totalItems`，内容引用也以 `@` 前缀表示，如 `@copper`。
2. 不同建筑支持的感知属性不同，不支持的属性返回 `null`（数值类）或 `NaN`。
3. 坐标属性（@x, @y）返回的是世界坐标（格为单位），通过 `World.conv()` 从内部浮点坐标转换而来。
4. 对象类属性（如 @type, @firstItem）返回的是对象引用，可以进一步用于其他指令。
5. 感知 null 对象的 `@dead` 属性返回 1，这是特殊设计，可用于检查建筑/单位是否已被摧毁。
6. 远程建筑和单位也可以被感知（源码注释说明），不受链接范围限制。
7. sensor 可以读取单位属性，不限于建筑。

## 网络同步注意事项

- `sensor` 指令只读取属性，不产生网络同步操作。
- 在多人模式下，感知到的建筑/单位属性值反映的是本地的最新同步状态，可能与服务端有短暂差异。
- 对象类属性（如 @firstItem, @type）返回的对象引用在客户端可能与服务端不同步。
- 特权处理器感知的属性直接来自服务端数据，准确性更高。

## 未验证内容

- 各类炮塔/工厂特有的感知属性（如 @currentAmmoType 的具体返回值格式）。
- 单位感知的完整属性列表（UnitComp 中的 sense 实现）。
- @config 对不同建筑返回的具体值格式（可能因建筑类型而异）。
- @flag 属性的默认值和设置方式（通过 setProp 设置）。
