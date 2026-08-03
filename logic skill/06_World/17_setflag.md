# 17 - setflag（设置全局标记）

## 导出格式

```
setflag <flag> <value>
```

## 参数说明

| 参数  | 类型   | 说明                             |
| ----- | ------ | -------------------------------- |
| flag  | 字符串 | 标记名（键名）                   |
| value | 数值   | 要设置的值                       |

## 功能说明

设置全局标记的值。全局标记是跨处理器共享的键值对，存储在 `state.rules.tag` 中。所有世界处理器都可以读写同一个全局标记，从而实现世界处理器间的通信。

## 源码实现要点

- 对应指令类：`SetFlagI`
- 通过 `state.rules.tag.put(flag, value)` 设置全局标记值
- `state.rules.tag` 是一个 `ObjectMap<String, Object>`，以字符串为键存储任意值
- 设置后立即生效，其他世界处理器可以通过 `getflag` 读取到最新值
- 如果 value 为 null 或 0，效果取决于具体实现（可能删除该标记或存储为 0）

## 注意事项

- 此指令为 **privileged（特权）** 指令，只能在世界处理器上运行
- 世界处理器在服务器端执行，不存在客户端同步问题
- flag 参数为字符串类型（标记名），如 `"myFlag"`
- **这是世界处理器间通信的重要方式**，可用于在不同世界处理器之间传递数据、同步状态
- 配合 `getflag` 指令使用，实现跨处理器的状态同步
- 设置后立即生效，同一 tick 内其他处理器执行 `getflag` 可读取到新值（取决于处理器执行顺序）

## 代码示例

```
## 设置全局标记 "waveCount" 为 10
setflag "waveCount" 10

## 读取并验证
getflag _count "waveCount"
print "Wave count set to: "
print _count
printflush message1
end
```

## 未验证内容

- 无
