# 06 - status（应用/清除状态效果）

## 导出格式

```
status <apply|clear> <effect> <unit> <duration>
```

## 参数说明

| 参数     | 类型     | 说明                                        |
| -------- | -------- | ------------------------------------------- |
| apply/clear | 枚举 | 操作模式：`apply` 施加状态，`clear` 清除状态 |
| effect   | Content  | 状态效果类型（如 `@burning`、`@wet` 等）    |
| unit     | 单位引用 | 目标单位                                    |
| duration | 数值     | 持续时间（秒），apply 模式下有效             |

## 功能说明

对指定单位施加或清除状态效果。施加状态时，状态效果会持续指定的时间；清除状态时，立即移除该状态效果。

## 源码实现要点

- 对应指令类：`ApplyEffectI`
- `apply` 模式：调用 `unit.apply(effect, duration * 60)` 方法施加状态效果（duration 乘以 60 是将秒转换为 tick，因为游戏每秒 60 tick）
- `clear` 模式：调用 `unit.unapply(effect)` 方法清除指定状态效果
- effect 参数会被解析为 `StatusEffect` 类型

## 注意事项

- 此指令为 **privileged（特权）** 指令，只能在世界处理器上运行
- 世界处理器在服务器端执行，不存在客户端同步问题
- effect 参数为状态效果类型，必须使用有效值（如 `@burning`、`@wet`、`@frozen` 等）
- `clear` 模式下 duration 参数无效，但导出时仍需写出
- 状态效果可以叠加，多次 apply 同一状态会刷新持续时间

## 代码示例

```
## 对单位 myUnit 施加燃烧状态，持续 5 秒
status apply @burning myUnit 5

## 清除单位的燃烧状态
status clear @burning myUnit 0
end
```

## 未验证内容

- 无
