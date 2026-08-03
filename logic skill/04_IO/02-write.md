# 02 - write（写入内存建筑）

> 用途：将一个值按索引写入内存建筑（Memory Cell、Memory Bank）或其他可写对象中。

## 导出格式

```
write result to cell1 at 0
```

等价的文本指令格式：

```
write <value> <target> <address>
```

- 积木编辑器中显示为 `write result to cell1 at 0`
- 文本格式中三个参数依次为：要写入的值、目标建筑、地址索引

## 参数说明

| 参数位置 | 参数名 | 说明 | 默认值 |
|---------|--------|------|--------|
| 1 | value | 要写入的值（变量或常量） | result |
| 2 | target | 目标建筑（通过 `@link` 名称或变量引用） | cell1 |
| 3 | address | 写入的地址索引（从 0 开始） | 0 |

## 功能说明

`write` 指令将指定值写入目标对象的内存中指定索引位置。

核心流程如下：

1. 获取目标对象，检查它是否实现了 `LWritable`（可写）接口。
2. 如果实现了该接口，先调用 `writable()` 方法进行权限校验：
   - 校验逻辑与 `readable()` 完全一致（建筑有效 + 队伍权限）。
3. 校验通过后调用 `write(position, value)` 完成写入。

### 不同目标对象的写入行为

**内存建筑（Memory Cell / Memory Bank）**：
- 地址参数作为**数字索引**使用，写入 `memory[]` 数组。
- 地址越界（小于 0 或大于等于容量）时，直接忽略，不执行写入。
- 写入时通过 `value.num()` 将值转换为 `double` 类型存储，因此**只能存储数字**，无法存储对象引用。
- Memory Cell 容量为 64，Memory Bank 容量为 512。

**处理器自身（LogicBuild，通过 `@this` 或链接的处理器引用）**：
- 仅当地址参数为**字符串**时才执行写入：调用 `executor.optionalVar(varName)` 按变量名查找处理器内部变量。
  - 若找到对应变量且非常量：将值直接赋给该变量（`at.set(value)`），**可以存储对象引用**（如单位、建筑等）。
  - 若未找到对应变量或为常量：不做任何操作。
- 当地址参数为**数字**时：**不做任何操作**（与 `read` 不同，`write` 没有数字索引的处理分支）。
- **这是处理器间通信的核心机制**：通过字符串作为变量名键，可以直接修改处理器内部变量，包括写入对象引用。

**画板（CanvasBuild）**：
- 用于绘制像素图案，写入方式由画板自身定义。

与 `read` 不同的是，`write` 指令仅对实现了 `LWritable` 接口的对象有效。对于字符串、序列等非 `LWritable` 对象，`write` 不会执行任何操作。

## 源码实现要点

**WriteStatement（语句定义）** — 位于 `LStatements.java`。注册为 `write`，分类为 `LCategory.io`。构建时通过 `builder.var()` 解析三个参数（target、address、input），生成 `WriteI` 指令。注意：语句定义中字段名为 `input`，但传入 `WriteI` 构造器的顺序为 `target, address, value`。

**WriteI（指令执行）** — 位于 `LExecutor.java`。持有 `target`、`position`、`value` 三个 LVar。`run()` 方法中：
- 将 target 当作对象取出，判断是否为 `LWritable` 实例。
- 若是，进行 `writable()` 权限检查后调用 `write()`。
- 若不是，直接返回，不做任何处理。

**LWritable 接口** — 定义了 `writable(LExecutor exec)` 和 `write(LVar position, LVar value)` 两个方法。实现此接口的建筑包括：内存建筑（MemoryBuild）、处理器自身（LogicBuild）、画板（CanvasBuild）。

**MemoryBuild.write()** — 地址越界时直接 `return`，不抛出异常。写入时调用 `value.num()` 取数字值赋给 `memory[address]`。

**LogicBuild.write()** — 处理器自身的写入方法，行为与内存建筑完全不同：
- 仅处理字符串类型的 `position`：`if(position.isobj && position.objval instanceof String varName)`
- 调用 `executor.optionalVar(varName)` 按变量名查找处理器内部变量
- 若变量存在且非常量：`at.set(value)` — 直接赋值，**保留对象类型**，可以写入单位引用、建筑引用等
- 若变量不存在或为常量：直接返回，不做任何操作
- **不处理数字索引**：当 `position` 为数字时，`write` 不执行任何操作（与 `read` 不同，`read` 在数字索引时会访问 links 数组）

## 注意事项

- 地址索引从 0 开始，最大有效索引为容量减 1（Cell 为 63，Bank 为 511）。
- 越界写入会被静默忽略，不会报错，也不会自动扩展数组。
- 由于内存建筑存储类型为 `double`，写入的值会丢失对象信息。例如写入一个建筑引用后再读取，得到的只是数字而非建筑本身。
- **处理器自身（`@this`）的写入行为与内存建筑完全不同**：使用字符串作为变量名键可以修改处理器内部变量（包括写入对象引用），使用数字索引则不执行任何操作。这是多核通信中传递单位引用、建筑引用的核心机制。
- 内存建筑无法被拾起（`canPickup()` 返回 false），以避免大数组同步问题。
- 特权处理器可以写入任意队伍的建筑内存。
- 写入操作的权限校验与读取一致：处理器需为特权处理器，或目标建筑与处理器同队伍且建筑非特权类型。

## 网络同步注意事项

- 内存建筑的内存数组通过建筑的 `write()` / `read()` 方法进行网络序列化。存档时完整写入所有 `double` 值，读档时按存储数量恢复。
- 在多人模式下，内存建筑的写入操作会在服务端和客户端之间同步。但处理器在客户端和服务端各执行一次，可能导致重复写入或短暂的数据不一致。
- 大型内存建筑（如 Memory Bank 的 512 个 double）的网络同步开销较大，频繁写入可能影响网络性能。
- 内存建筑的内存数据不参与处理器的变量同步（`vars` 数组），而是作为建筑自身的状态独立同步。

## 源码验证结论

- **LWritable 接口由 3 种建筑实现**：`MemoryBuild`（内存 cell/bank）、`LogicBuild`（处理器自身）、`CanvasBuild`（画板）。因此 write 指令可以向这三种建筑写入数据。
- 处理器写入自身（LogicBuild）时，写入的是处理器的变量存储区，可以通过 write 修改处理器内部变量。**关键区别**：内存建筑写入时通过 `value.num()` 转为 double，丢失对象信息；而 LogicBuild 写入时通过 `at.set(value)` 直接赋值，保留对象类型，可以存储单位引用、建筑引用等。
- LogicBuild.write() 仅处理字符串地址参数（变量名），不处理数字索引参数。当传入数字索引时不执行任何操作。
- 画板（CanvasBlock）的写入用于绘制像素图案。
- 在极高频率写入场景下，网络同步的具体延迟和一致性表现未做详细测试。
