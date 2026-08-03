# 01 - read（读取内存建筑）

> 用途：从内存建筑（Memory Cell、Memory Bank）或其他可读对象中按索引读取一个值，存入指定变量。

## 导出格式

```
read result = cell1 at 0
```

等价的文本指令格式：

```
read <output> <target> <address>
```

- 积木编辑器中显示为 `read result = cell1 at 0`
- 文本格式中三个参数依次为：输出变量、目标建筑、地址索引

## 参数说明

| 参数位置 | 参数名 | 说明 | 默认值 |
|---------|--------|------|--------|
| 1 | output | 接收读取结果的变量名 | result |
| 2 | target | 目标建筑（通过 `@link` 名称或变量引用） | cell1 |
| 3 | address | 读取的地址索引（从 0 开始） | 0 |

## 功能说明

`read` 指令从目标对象的内存中读取指定索引位置的值，并将结果写入输出变量。

核心流程如下：

1. 获取目标对象，检查它是否实现了 `LReadable`（可读）接口。
2. 如果实现了该接口，先调用 `readable()` 方法进行权限校验：
   - 建筑必须有效（`isValid()`）。
   - 处理器必须拥有权限（特权处理器或同队伍且建筑非特权）。
3. 校验通过后调用 `read(position, output)` 完成读取。

### 不同目标对象的读取行为

**内存建筑（Memory Cell / Memory Bank）**：
- 地址参数作为**数字索引**使用，访问 `memory[]` 数组。
- 地址越界（小于 0 或大于等于容量）时，输出变量被设为 `NaN`。
- Memory Cell 容量为 64，Memory Bank 容量为 512。
- 存储类型为 `double`，无法存储对象引用。

**处理器自身（LogicBuild，通过 `@this` 或链接的处理器引用）**：
- 当地址参数为**字符串**时，通过 `executor.optionalVar(varName)` 按变量名查找处理器内部变量。
  - 若找到对应变量，将其值复制到输出变量（可以是对象引用，如单位、建筑等）。
  - 若未找到对应变量，尝试通过 `optionalLink(varName)` 查找同名的链接建筑。
- 当地址参数为**数字**时，将其作为索引访问处理器的 `links` 数组（链接建筑列表），返回对应位置的链接建筑。
- **这是处理器间通信的核心机制**：通过字符串作为变量名键，可以直接读写处理器内部变量，包括对象引用。

**其他可读对象**：
- 如果目标是字符串（CharSequence），则返回对应索引处字符的 Unicode 码点（整数）；越界返回 `NaN`。
- 如果目标是序列（Seq），则返回对应索引处的元素对象；越界返回 `null`。
- 其他不可读对象，输出变量被设为 `null`。

## 源码实现要点

**ReadStatement（语句定义）** — 位于 `LStatements.java`。注册为 `read`，分类为 `LCategory.io`。构建时通过 `builder.var()` 解析三个参数（target、address、output），生成 `ReadI` 指令。

**ReadI（指令执行）** — 位于 `LExecutor.java`。持有 `target`、`position`、`output` 三个 LVar。`run()` 方法中：
- 先将 target 当作对象取出，判断是否为 `LReadable` 实例。
- 若是，进行 `readable()` 权限检查后调用 `read()`。
- 若不是，则按 CharSequence / Seq 的顺序尝试读取，最后兜底设为 `null`。

**LReadable 接口** — 定义了 `readable(LExecutor exec)` 和 `read(LVar position, LVar output)` 两个方法。实现该接口的建筑包括：内存建筑（MemoryBuild）、消息建筑（MessageBuild）、处理器自身（LogicBuild）、画板（CanvasBuild）。

**MemoryBuild.read()** — 地址越界时返回 `Double.NaN`（而非 0），这是通过 `output.setnum(...)` 写入的。

**LogicBuild.read()** — 处理器自身的读取方法，行为与内存建筑完全不同：
- 若 `position` 为字符串对象：调用 `executor.optionalVar(varName)` 按变量名查找处理器内部变量。找到则复制值到输出；未找到则调用 `optionalLink(varName)` 查找同名链接建筑。
- 若 `position` 为数字：将其作为索引访问 `executor.links` 数组，返回对应位置的链接建筑。
- 这使得 `read @this <变量名>` 可以直接读取处理器内部变量，包括对象引用（单位、建筑等），而非仅限 double 数字。

## 注意事项

- 地址索引从 0 开始，最大有效索引为容量减 1（Cell 为 63，Bank 为 511）。
- 越界读取得到的是 `NaN`（Not a Number），可以用 `isfinite` 判断来过滤。
- 内存建筑中存储的值始终是 `double` 类型（数字），无法直接存储对象/建筑引用。`write` 写入时也会调用 `value.num()` 转为数字。
- **处理器自身（`@this`）的读取行为与内存建筑完全不同**：使用字符串作为变量名键可以读取处理器内部变量（包括对象引用），使用数字索引则读取链接建筑列表。这是多核通信的核心机制。
- 读取消息建筑（Message Block）时，返回的是字符的 Unicode 码点而非子字符串。
- 特权处理器可以读取任意队伍的建筑内存。

## 网络同步注意事项

- 内存建筑的内存数据通过建筑的 `write()` / `read()` 方法进行网络序列化保存，存档时会完整保存数组内容。
- 在多人模式下，内存建筑的写入操作会在服务端和客户端之间同步。但由于处理器在客户端和服务端各执行一次，可能存在短暂的同步延迟。
- 被拾起（pickup）的内存建筑无法携带内存数据（`canPickup()` 返回 false），这是为了避免大数组的同步问题。

## 未验证内容

无（所有读取行为均已通过源码验证，包括 LogicBuild 的字符串/数字地址读取、CharSequence 字符码点读取、Seq 元素读取）。
