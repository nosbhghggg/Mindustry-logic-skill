# 01 - setrate（设置处理器执行速度）

## 导出格式

```
setrate <amount>
```

## 参数说明

| 参数   | 类型 | 说明                             |
| ------ | ---- | -------------------------------- |
| amount | 数值 | 每 tick 执行的指令数（最大 1000） |

## 功能说明

设置世界处理器的执行速度，即修改 `@ipt`（每 tick 指令数）的值。世界处理器默认 `@ipt` 为 8，通过 `setrate` 可以将其提升至最高 1000，从而实现极高的逻辑执行速度。

## 源码实现要点

- 对应指令类：`SetRateI`
- 执行时直接设置 `executor.ipt = (int)p1.num()`，将处理器的每 tick 指令数修改为指定值
- 设置后会立即生效，下一帧的指令执行将使用新的 `@ipt` 值
- 数值会被截断为整数，且不会进行范围校验（超过 1000 的值仍会被设置，但实际执行中由 `maxInstructionScale` 限制累积上限）

## 注意事项

- 此指令为 **privileged（特权）** 指令，只能在世界处理器上运行，普通处理器无法使用
- 世界处理器在服务器端执行，不存在客户端同步问题
- `@ipt` 的实际累积上限为 `maxInstructionScale * ipt`（默认 maxInstructionScale=5），即累积的执行点数不会超过 5 倍 ipt
- 过高的 `@ipt` 值可能导致服务器性能下降，应根据实际需求合理设置
- 可以通过 `sensor result @ipt` 读取当前的 `@ipt` 值

## 代码示例

```
## 将世界处理器速度设置为最大值
setrate 1000

## 读取当前速度
sensor currentRate @ipt
print currentRate
printflush message1
end
```

## 未验证内容

- 无
