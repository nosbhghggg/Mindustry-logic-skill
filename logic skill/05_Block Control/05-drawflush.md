# 05 - drawflush（刷新绘制到显示屏）

> **用途**：将处理器图形缓冲区（graphicsBuffer）中的绘制指令刷新到逻辑显示屏建筑，使绘制内容在显示屏上可见。

## 导出格式

```
drawflush <building>
```

## 参数说明

| 参数 | 类型 | 说明 |
|------|------|------|
| building | 建筑引用 | 目标显示屏建筑（LogicDisplay 类型） |

## 功能说明

`drawflush` 指令将处理器内部维护的图形缓冲区（graphicsBuffer）中的所有绘制指令一次性提交到指定的逻辑显示屏建筑。

处理器通过 `draw` 系列指令（如 `draw line`、`draw rect`、`draw color` 等）将绘制操作写入图形缓冲区，这些操作不会立即显示在显示屏上。只有执行 `drawflush` 后，缓冲区中的绘制指令才会被提交到显示屏并渲染出来。

执行流程：
1. 从 building 变量获取目标建筑。
2. 验证目标建筑是否为 LogicDisplayBuild（逻辑显示屏），且有效且同队伍（或特权处理器）。
3. 验证通过后，调用显示屏的 `flushCommands()` 方法提交图形缓冲区内容。
4. 无论验证是否通过，都会清空图形缓冲区（graphicsBuffer）。

**图形缓冲区限制**：图形缓冲区最大容量为 256 条绘制指令（maxGraphicsBuffer = 256）。当缓冲区满时，后续的 draw 指令会被忽略。显示屏自身的显示缓冲区容量为 1024（maxDisplayBuffer = 1024）。

## 源码实现要点

### DrawFlushI（刷新绘制指令）

位于 `LExecutor.java`，核心逻辑如下：

- 从 target 变量获取目标建筑，通过 `building()` 方法获取 Building 实例。
- 验证目标是否为 `LogicDisplayBuild`，且 `isValid()` 为真，且 `d.team == exec.team`（或 `exec.privileged` 为特权处理器）。
- 验证通过后调用 `d.flushCommands(exec.graphicsBuffer)` 提交图形缓冲区。
- 最后无条件执行 `exec.graphicsBuffer.clear()` 清空缓冲区。

### graphicsBuffer（图形缓冲区）

- 类型为 `LongSeq`，存储打包后的绘制指令（每条指令为一个 long 值）。
- 由 `DrawI` 指令在执行 draw 操作时写入。
- 最大容量 256 条指令，超过后新的 draw 指令不再写入。
- 每次 `drawflush` 执行后清空。

### LogicDisplayBuild.flushCommands

接收图形缓冲区中的绘制指令，存入显示屏的显示缓冲区（displayBuffer），由显示屏在渲染时执行。

## 注意事项

1. 目标建筑必须是逻辑显示屏（Logic Display），其他建筑类型会导致指令静默失败。
2. 显示屏必须与处理器同队伍（特权处理器除外），且必须有效（未被摧毁）。
3. `drawflush` 会清空图形缓冲区，因此每次刷新后需要重新执行 draw 指令才能绘制新内容。
4. 如果不执行 `drawflush`，draw 指令的绘制内容不会显示在显示屏上。
5. 图形缓冲区上限 256 条指令，显示缓冲区上限 1024 条指令。多次 drawflush 可累积超过 256 条指令到显示屏。
6. 在无头服务器（headless）上，draw 指令本身不会执行（直接返回），但 drawflush 仍会清空缓冲区。
7. 显示屏的渲染由客户端处理，服务端不需要实际渲染图形。

## 网络同步注意事项

- `drawflush` 产生的绘制指令需要通过网络同步到所有客户端的显示屏。
- 绘制指令的同步数据量可能较大（最多 256 条指令），在多人模式下可能增加网络负载。
- 客户端看到的显示屏内容可能存在短暂延迟，因为指令需要先发送到服务端再同步到各客户端。
- 特权处理器（世界处理器）的 drawflush 直接在服务端执行，但仍需同步绘制指令到客户端。
- 频繁执行 drawflush（如每 tick 执行）可能导致网络带宽压力，建议适当降低刷新频率。

## 未验证内容

- 多个处理器同时向同一显示屏 drawflush 时的行为（绘制指令是否会混合或覆盖）。
- 显示缓冲区满（1024 条）后新指令的处理方式（推测为丢弃最旧指令或忽略新指令）。
- drawflush 在客户端处理器中的执行时序（是否等待服务端确认后再清空缓冲区）。
