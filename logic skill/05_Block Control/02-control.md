# 02 - control（控制建筑）

> **用途**：对已链接的建筑发送控制指令，包括启用/禁用、设置配置（如传送带筛选物品）、设置颜色、炮塔射击坐标、炮塔射击目标等。

## 导出格式

```
control <type> <building> <p1> <p2> <p3> <p4>
```

## 参数说明

| 参数 | 类型 | 说明 |
|------|------|------|
| type | 控制类型 | 控制子类型，取值为 `enabled`、`config`、`color`、`shoot`、`shootp` |
| building | 建筑引用 | 目标建筑（通过 getlink 或其他方式获取） |
| p1 | 参数1 | 含义随 type 不同而变化 |
| p2 | 参数2 | 含义随 type 不同而变化 |
| p3 | 参数3 | 含义随 type 不同而变化 |
| p4 | 参数4 | 含义随 type 不同而变化 |

## 控制子类型说明

### enabled（启用/禁用）

```
control enabled <building> <p1> 0 0 0
```

| 参数 | 说明 |
|------|------|
| p1 | 1 = 启用，0 = 禁用 |

控制建筑的开关状态。当 p1 为 1 时，建筑被唤醒（noSleep）；当 p1 为 0 时，记录禁用来源为当前处理器。适用于所有可被禁用的建筑，如工厂、炮塔、传送带等。

### config（设置配置）

```
control config <building> <p1> 0 0 0
```

| 参数 | 说明 |
|------|------|
| p1 | 配置对象（物品、液体等内容对象），如 `@copper`、`@water` |

设置建筑的配置项。典型应用场景：
- 传送带/分选器的筛选物品
- 分配器的目标物品
- 卸料器的目标物品
- 脉冲节点等建筑的配置

注意：p1 是对象类型参数，需传入内容引用（如 `@copper`），而非数字。该指令会忽略对处理器建筑自身（LogicBuild）的配置，以避免极端卡顿。

### color（设置颜色）

```
control color <building> <p1> 0 0 0
```

| 参数 | 说明 |
|------|------|
| p1 | 打包的颜色值（double 类型，通过颜色打包函数生成） |

设置建筑的颜色。主要用于照亮器（Light Block），将打包的颜色值解包为 RGBA 设置建筑颜色。

### shoot（射击坐标）

```
control shoot <building> <p1> <p2> <p3> 0
```

| 参数 | 说明 |
|------|------|
| p1 | 目标 X 坐标（世界坐标，单位为格） |
| p2 | 目标 Y 坐标（世界坐标，单位为格） |
| p3 | 是否射击（1 = 射击，0 = 停止射击） |

控制炮塔射击指定坐标。坐标会通过 `World.unconv()` 转换为内部坐标。该指令仅在炮塔未被玩家控制时生效，并设置逻辑控制冷却时间。

### shootp（射击目标）

```
control shootp <building> <p1> <p2> 0 0
```

| 参数 | 说明 |
|------|------|
| p1 | 目标对象（单位或建筑引用） |
| p2 | 是否射击（1 = 射击，0 = 停止射击） |

控制炮塔射击指定单位或建筑。p1 是对象类型参数，需传入单位或建筑引用。该指令仅在炮塔未被玩家控制时生效。

## 功能说明

`control` 指令是处理器控制建筑行为的核心指令。它根据控制类型（type）和参数对目标建筑执行不同的控制操作。

源码中通过 `LAccess.controls` 筛选出可用的控制类型，共 5 种：`enabled`、`config`、`color`、`shoot`、`shootp`。

执行流程：
1. 从 building 变量获取目标建筑对象。
2. 验证目标建筑是否为有效链接（或处理器为特权处理器）。
3. 对 `enabled` 类型做特殊处理（noSleep / lastDisabler）。
4. 根据 type 是否为对象类型（isObj）及 p1 是否为对象，选择调用对象版本或数值版本的 `control` 方法。
5. 由各建筑子类的 `control` 方法实现具体行为。

## 源码实现要点

### ControlI（控制指令）

位于 `LExecutor.java`，核心逻辑如下：

- 从 target 变量获取建筑对象，检查是否为 Building 实例。
- 验证链接有效性：普通处理器需 `exec.build.validLink(b)`，特权处理器直接通过。
- 对 `enabled` 类型：p1 为真时调用 `b.noSleep()` 唤醒建筑，否则设置 `b.lastDisabler = exec.build`。
- 根据 `type.isObj` 和 `p1.isobj` 判断使用对象版还是数值版的 `control` 方法：
  - 对象版：`b.control(type, p1.obj(), p2.num(), p3.num(), p4.num())`
  - 数值版：`b.control(type, p1.num(), p2.num(), p3.num(), p4.num())`

### BuildingComp.control（建筑控制基类）

位于 `BuildingComp.java`，默认实现：
- 数值版：仅处理 `enabled` 类型，设置 `enabled = !Mathf.zero(p1)`。
- 对象版：仅处理 `config` 类型，在 `block.logicConfigurable` 为真且目标非 LogicBuild 时调用 `configured(null, p1)`。

### 各子类的 control 重写

- **Turret（炮塔）**：重写 `shoot` 和 `shootp` 的控制逻辑，设置目标位置/目标对象、射击状态和逻辑控制冷却时间。
- **Door（门）**：重写 `enabled` 控制，切换门的开关状态。
- **PayloadRouter（载荷路由器）**：重写 `config` 控制，设置旋转方向。
- **LightBlock（照亮器）**：重写 `color` 控制，设置颜色。

## 注意事项

1. 目标建筑必须是处理器已链接的建筑，否则指令不执行。
2. `config` 和 `shootp` 的 p1 参数是对象类型，需传入内容引用（如 `@copper`）或建筑/单位引用，而非数字。
3. `shoot` 的坐标参数是世界坐标（格为单位），会自动转换为内部浮点坐标。
4. 炮塔被玩家手动控制时，`shoot` 和 `shootp` 指令不生效。
5. 对 LogicBuild 自身执行 `config` 控制会被忽略，以防止逻辑递归导致的卡顿。
6. 不同建筑支持的 control 类型不同，对不支持的控制类型会静默忽略。

## 网络同步注意事项

- **多人模式下，control 指令由服务端执行**。客户端处理器的 control 指令会发送到服务端处理。
- `config` 控制会触发 `configured()` 方法，该方法在服务端执行后通过网络同步配置变化到所有客户端。
- `enabled` 控制改变建筑启用状态，通过建筑的 `enabled` 字段同步。
- `shoot` 和 `shootp` 控制的炮塔目标位置和射击状态，由服务端的炮塔逻辑处理并同步。
- 客户端看到的建筑控制效果可能存在短暂延迟，因为指令需要先发送到服务端再同步回来。
- 特权处理器（世界处理器）的 control 指令直接在服务端执行，同步延迟更小。

## 未验证内容

- `color` 控制的颜色打包值的具体计算方式（是否与 draw 指令的 colorPack 使用相同格式）。
- 连续快速发送 `shoot` 指令时，炮塔的响应频率是否有上限。
- `config` 控制对各类建筑的完整适用范围（哪些建筑支持 logicConfigurable）。
