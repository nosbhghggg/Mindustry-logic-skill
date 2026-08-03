# 10 - setrule（设置游戏规则）

## 导出格式

```
setrule <rule> <value> <p1> <p2> <p3> <p4>
```

## 参数说明

| 参数  | 类型     | 说明                                             |
| ----- | -------- | ------------------------------------------------ |
| rule  | 枚举     | 规则类型（LogicRule 枚举值，如 `waveSpacing`、`wave`、`buildSpeed` 等） |
| value | 数值     | 规则值                                           |
| p1    | 数值     | 附加参数1（部分规则使用）                         |
| p2    | 数值     | 附加参数2（部分规则使用）                         |
| p3    | 数值     | 附加参数3（部分规则使用）                         |
| p4    | 数值     | 附加参数4（部分规则使用）                         |

## 功能说明

修改游戏规则，可以调整波次间隔、波次编号、建造速度、光照、核心数量等多种游戏参数。不同规则类型使用不同的参数。

## 源码实现要点

- 对应指令类：`SetRuleI`
- 根据 `LogicRule` 枚举类型执行不同的操作：
  - `waveSpacing`：设置波次间隔（秒），`state.rules.spawner.pauseSpacing = value * 60`（转换为 tick）
  - `wave`：设置当前波次编号，`state.rules.wave = (int)value`
  - `buildSpeed`：设置建造速度倍率，`state.rules.buildSpeedMultiplier = value`
  - `lighting`：设置是否开启光照系统
  - `ambientLight`：设置环境光颜色
  - `solarMultiplier`：设置太阳能倍率
  - 各规则的具体参数数量和含义不同，p1-p4 用于传递附加参数

## 注意事项

- 此指令为 **privileged（特权）** 指令，只能在世界处理器上运行
- 世界处理器在服务器端执行，不存在客户端同步问题
- rule 参数为 `LogicRule` 枚举值，必须使用有效值，否则会导致灰色积木
- 修改游戏规则会立即生效，且影响全局
- 部分规则修改后不会被持久化保存（取决于游戏存档逻辑）

## 代码示例

```
## 设置波次间隔为 120 秒
setrule waveSpacing 120 0 0 0 0

## 设置当前波次为 10
setrule wave 10 0 0 0 0

## 设置建造速度为 2 倍
setrule buildSpeed 2 0 0 0 0
end
```

## 未验证内容

- LogicRule 枚举的完整列表需要从源码确认
