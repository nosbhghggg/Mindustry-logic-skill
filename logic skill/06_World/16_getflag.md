# 16 - getflag（获取全局标记）

## 导出格式

```
getflag <result> <flag>
```

## 参数说明

| 参数   | 类型     | 说明                                   |
| ------ | -------- | -------------------------------------- |
| result | 输出变量 | 输出：标记对应的值                     |
| flag   | 字符串   | 标记名（键名）                         |

## 功能说明

读取全局标记的值。全局标记是跨处理器共享的键值对，存储在 `state.rules.tag` 中。所有世界处理器都可以读写同一个全局标记，从而实现世界处理器间的通信。

## 源码实现要点

- 对应指令类：`GetFlagI`
- 通过 `state.rules.tag` 获取全局标记值
- `state.rules.tag` 是一个 `ObjectMap<String, Object>`，以字符串为键存储任意值
- 如果标记不存在，输出 null（在 Logic 中表现为 0）

## 注意事项

- 此指令为 **privileged（特权）** 指令，只能在世界处理器上运行
- 世界处理器在服务器端执行，不存在客户端同步问题
- flag 参数为字符串类型（标记名），如 `"myFlag"`
- 全局标记是 **世界处理器间通信的重要方式**，可以用于在不同世界处理器之间传递数据
- 配合 `setflag` 指令使用，实现跨处理器的状态同步

## 代码示例

```
## 读取全局标记 "waveCount" 的值
getflag _waveCount "waveCount"

## 打印波次计数
print "Wave count: "
print _waveCount
printflush message1
end
```

## 未验证内容

- 无
