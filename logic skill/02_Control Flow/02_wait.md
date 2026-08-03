# 02 - wait（等待）

## 导出格式

```
wait <value>
```

## 参数

| 参数 | 说明 |
|------|------|
| value | 等待时间，单位为秒。可以是数值常量（如 `0.5`）或变量名。支持小数 |

## 功能

**用途：暂停处理器执行指定时间，到时后继续执行下一条指令。**

`wait` 让处理器在当前指令处"停留"指定的秒数。在等待期间，处理器每个游戏 tick 都会重新执行该 `wait` 指令，累计已等待的时间，直到时间满足后才放行。

## 源码实现要点

### 语句定义

`WaitStatement` 包含一个字符串字段 `value`（默认值 `"0.5"`），构建指令时通过 `builder.var(value)` 解析为 LVar 变量后传入 `WaitI`。

### 指令执行

`WaitI` 的执行方法（`run`）包含三个分支：

**1. 等待时间 <= 0 时：**
- 设置 yield 标志为 true（`exec.yield = true`），中断当前 tick 的执行
- 重置累计时间为 0（`curTime = 0f`）
- 不回退计数器，下一条指令将在下一个 tick 执行

这相当于"让出一个 tick"——处理器暂停当前 tick 的剩余指令配额，下一个 tick 从下一条指令继续。

**2. 累计时间已达到等待时间时（`curTime >= value`）：**
- 重置累计时间为 0（`curTime = 0f`）
- 不设置 yield，不回退计数器
- 处理器继续执行下一条指令

**3. 累计时间尚未达到等待时间时：**
- 回退计数器（`exec.counter.numval --`），使下一个 tick 重新执行本条 `wait` 指令
- 设置 yield 标志为 true（`exec.yield = true`），中断当前 tick 的执行
- 累加已等待时间（`curTime += Time.delta / 60f`）

### 时间累计机制

`wait` 的等待不是一次性完成的，而是跨多个 tick 逐步累计。每个 tick 执行 `wait` 时：

1. `runOnce()` 先递增计数器，然后执行 `wait` 指令
2. 如果时间未到，`wait` 将计数器减 1（回到自身），并设置 yield
3. yield 导致当前 tick 的执行循环中断
4. 下一个 tick，处理器再次执行同一条 `wait` 指令，继续累计时间
5. 当累计时间达到指定值时，`wait` 放行，计数器指向下一条指令

### yield 与执行循环

处理器的执行循环（`LogicBlock.update`）在每次调用 `runOnce()` 后检查 yield 标志。如果 yield 为 true，则重置 yield 为 false 并跳出循环，保留剩余的指令配额到下一个 tick。这是 `wait` 能够实现"暂停"的核心机制。

## 注意事项

- `wait 0` 或 `wait` 后跟负数会让出一个 tick（相当于暂停一帧），而不是无限等待。下一个 tick 会继续执行下一条指令
- `value` 是变量引用而非快照值。如果在等待期间 `value` 被其他处理器远程修改，`wait` 会使用新的值来判断。这就是源码中 `value.num()` 每次都重新读取的原因
- `wait` 的时间单位是秒，基于游戏时间（`Time.delta`）。在游戏暂停时，等待不会推进
- 等待期间处理器的指令配额被保留（accumulator 不递减），因此等待结束后不会"补偿性"地 burst 执行大量指令
- `wait` 会占用一个指令位

## 源码验证结论

- **游戏加速影响**：当游戏速度加快（如 2 倍速）时，`Time.delta` 按倍率增长。`wait` 的 `curTime += Time.delta / 60f` 会因此累加更快，`wait` 在游戏时间内的等待时长不变，但在现实时间中会按倍率缩短。
- **处理器执行同步**：处理器的 `accumulator += edelta() * ipt` 也依赖 `Time.delta`（通过 `edelta()`），因此处理器在加速时每 tick 执行更多指令，与 `wait` 的加速保持同步。
- **同步机制**：`wait` 的 `curTime` 和处理器的 `accumulator` 均被序列化同步（见 `LogicBlock.write()`/`read()`），多人模式下状态是同步的。但由于不同客户端的 `Time.delta` 可能存在微小差异，wait 计时可能有轻微偏差。
