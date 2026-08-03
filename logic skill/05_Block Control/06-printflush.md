# 06 - printflush（刷新打印到消息建筑）

> **用途**：将处理器文本缓冲区（textBuffer）中的内容刷新到消息建筑（Message Block），使文本内容在消息建筑上显示。

## 导出格式

```
printflush <building>
```

## 参数说明

| 参数 | 类型 | 说明 |
|------|------|------|
| building | 建筑引用 | 目标消息建筑（Message Block 类型） |

## 功能说明

`printflush` 指令将处理器内部维护的文本缓冲区（textBuffer）中的所有文本内容一次性提交到指定的消息建筑。

处理器通过 `print` 指令将文本内容写入文本缓冲区，这些内容不会立即显示在消息建筑上。只有执行 `printflush` 后，缓冲区中的文本才会被提交到消息建筑并显示出来。

执行流程：
1. 从 building 变量获取目标建筑。
2. 验证目标建筑是否为 MessageBuild（消息建筑），且有效且同队伍（或特权处理器且目标非特权建筑）。
3. 验证通过后：
   - 清空消息建筑的原有内容（`d.message.setLength(0)`）。
   - 将文本缓冲区内容追加到消息建筑，截断至消息建筑的最大文本长度（maxTextLength）。
4. 无论验证是否通过，都会清空文本缓冲区（textBuffer）。

**文本缓冲区限制**：文本缓冲区最大容量为 400 个字符（maxTextBuffer = 400）。当缓冲区满时，后续的 print 指令不会写入。

## 源码实现要点

### PrintFlushI（刷新打印指令）

位于 `LExecutor.java`，核心逻辑如下：

- 从 target 变量获取目标建筑，通过 `building()` 方法获取 Building 实例。
- 验证目标是否为 `MessageBuild`，且 `isValid()` 为真，且满足权限条件：
  - 特权处理器：直接通过（但目标建筑不能是特权建筑，除非处理器自身为特权）。
  - 普通处理器：需 `d.team == exec.team` 且 `!d.block.privileged`。
- 验证通过后：
  - 清空消息建筑内容：`d.message.setLength(0)`。
  - 追加文本缓冲区内容：`d.message.append(exec.textBuffer, 0, Math.min(exec.textBuffer.length(), maxTextLength))`。
- 最后无条件执行 `exec.textBuffer.setLength(0)` 清空文本缓冲区。

### textBuffer（文本缓冲区）

- 类型为 `StringBuilder`，存储待输出的文本内容。
- 由 `PrintI` 指令在执行 print 操作时写入。
- 最大容量 400 个字符，超过后新的 print 指令不再写入。
- 每次 `printflush` 执行后清空。
- 数字值在写入时会智能转换：接近整数的值显示为整数，否则显示为浮点数。

### MessageBuild

消息建筑的显示内容由 `message` 字段（StringBuilder）维护。printflush 会完全替换消息建筑的原有内容。

## 注意事项

1. 目标建筑必须是消息建筑（Message Block），其他建筑类型会导致指令静默失败。
2. 消息建筑必须与处理器同队伍（特权处理器除外），且必须有效（未被摧毁）。
3. `printflush` 会完全替换消息建筑的原有内容，而非追加。
4. `printflush` 会清空文本缓冲区，因此每次刷新后需要重新执行 print 指令才能输出新内容。
5. 如果不执行 `printflush`，print 指令的文本内容不会显示在消息建筑上。
6. 文本缓冲区上限 400 个字符，消息建筑的最大文本长度由 MessageBlock 定义。
7. print 指令对对象值的字符串转换规则：
   - null -> "null"
   - String -> 原文
   - 内容对象（MappableContent）-> 名称
   - Building -> 方块名称
   - Unit -> 单位类型名称
   - Enum -> 枚举名称
   - Team -> 队伍名称
   - 其他对象 -> "[object]"

## 网络同步注意事项

- `printflush` 产生的文本内容需要通过网络同步到所有客户端的消息建筑。
- 文本同步的数据量通常较小（最多 400 字符），对网络负载影响有限。
- 客户端看到的消息建筑内容可能存在短暂延迟，因为指令需要先发送到服务端再同步到各客户端。
- 特权处理器（世界处理器）的 printflush 直接在服务端执行，但仍需同步文本到客户端。
- 频繁执行 printflush（如每 tick 执行）可能导致频繁的网络同步，建议适当降低刷新频率。

## 源码验证结论

- **MessageBlock 的 maxTextLength = 400**（源码 `MessageBlock.java` 第 29 行：`public int maxTextLength = 400`）。同时 `maxNewlines = 24`，即最多 24 个换行符。超出长度的文本会被截断（config 方法中检查 `text.length() > maxTextLength` 则直接 return）。
- 多个处理器同时向同一消息建筑 printflush 时，后执行的覆盖先执行的（每次 printflush 调用 `handleString` 方法，该方法先 `message.setLength(0)` 再 `message.append(value)`，即完全替换而非追加）。
