# 05 - printchar（打印字符）

> 用途：通过 Unicode 码点或内容引用向处理器的文本缓冲区（textBuffer）追加单个字符。适用于打印特殊字符、控制字符或游戏内容图标。缓冲区内容需通过 `printflush` 刷新到消息建筑后才会显示。

## 导出格式

```
printchar 65
```

等价的文本指令格式：

```
printchar <value>
```

- 积木编辑器中显示为 `char 65`，旁边有一个字符选择按钮（点击可弹出 ASCII 字符 32-126 的选择面板）
- 文本格式中参数为 Unicode 码点（数字）或内容引用

## 参数说明

| 参数位置 | 参数名 | 说明 | 默认值 |
|---------|--------|------|--------|
| 1 | value | Unicode 码点（整数）或内容引用对象 | 65 |

## 功能说明

`printchar` 指令向处理器的 `textBuffer`（文本缓冲区）追加单个字符。与 `print` 不同的是，`printchar` 通过 Unicode 码点来指定要打印的字符，而非直接打印字符串。

文本缓冲区（textBuffer）最大容量为 **400** 个字符（`maxTextBuffer = 400`）。当缓冲区长度达到上限时，`printchar` 指令会被忽略。

### 两种工作模式

**数字模式（通过 Unicode 码点）：**
当值为数字时，将数字向下取整后作为 Unicode 码点，追加对应的字符到缓冲区。例如：
- `printchar 65` → 追加字符 `A`
- `printchar 97` → 追加字符 `a`
- `printchar 48` → 追加字符 `0`
- `printchar 10` → 追加换行符 `\n`
- `printchar 32` → 追加空格

**对象模式（通过内容引用）：**
当值为对象且为 `UnlockableContent`（可解锁内容，如物品、方块、单位等）时，追加该内容的 emoji 字符到缓冲区。这可以在消息建筑上显示内容图标。如果对象不是 `UnlockableContent`，则不做任何操作。

### 积木编辑器字符选择器

积木编辑器中，`printchar` 旁边有一个铅笔图标按钮，点击后会弹出一个包含 ASCII 字符 32（空格）到 126（`~`）的选择面板。选择某个字符后，输入框会自动填入对应的 Unicode 码点数值。面板按每行 8 个字符排列。

## 源码实现要点

**PrintCharStatement（语句定义）** — 位于 `LStatements.java`。注册为 `printchar`，分类为 `LCategory.io`。持有一个字符串字段 `value`，默认值为 `"65"`（即字符 `A`）。`build()` 方法通过 `builder.var(value)` 解析参数，生成 `PrintCharI` 指令。`build()` 方法中还构建了字符选择面板，遍历 char 值 32 到 126 生成按钮。

**PrintCharI（指令执行）** — 位于 `LExecutor.java`。持有一个 LVar `value`。`run()` 方法中：
- 先检查 textBuffer 长度是否已达上限（400），若是则直接返回。
- 如果值是对象（`value.isobj`），检查是否为 `UnlockableContent`，若是则追加其 `emojiChar()` 返回的字符，否则直接返回。
- 如果值是数字，调用 `Math.floor(value.numval)` 取整后转为 char 追加到缓冲区。

**emojiChar()** — `UnlockableContent` 接口的方法，返回该内容对应的 emoji 字符码点。用于在消息建筑上显示物品/方块的图标。

## 注意事项

- `printchar` 与 `print` 一样，只是向缓冲区追加内容，需要配合 `printflush` 刷新才能显示。
- 数字值会通过 `Math.floor()` 向下取整，因此 `printchar 65.9` 会打印字符 `A`（码点 65）。
- 通过内容引用打印 emoji 字符时，需要在消息建筑上才能正确显示图标。在逻辑显示屏上通过 `draw print` 绘制时，emoji 字符的显示效果取决于逻辑字体是否包含对应字形。
- ASCII 可打印字符的码点范围为 32（空格）到 126（`~`）。码点 10 为换行符，码点 9 为制表符。
- 可以使用 `printchar` 打印 `print` 指令难以直接输入的字符，如换行符（10）、制表符（9）或其他特殊符号。
- 积木编辑器的字符选择器仅覆盖 ASCII 32-126 范围。超出此范围的字符需要手动在输入框中输入码点数值。
- 文本缓冲区上限为 400 个字符，与 `print` 共享同一缓冲区。

## 网络同步注意事项

- textBuffer 本身不进行网络同步，与 `print` 指令共享同一缓冲区。
- `printflush` 刷新后，内容写入消息建筑的 `message` 字段并参与建筑同步。
- 内容 emoji 字符在消息建筑上的显示依赖客户端的内容资源，不同客户端应能一致显示。
- 在多人模式下，`printchar` 的行为与 `print` 一致，缓冲区在客户端和服务端各自独立维护。

## 未验证内容

- Unicode 码点超出基本多文种平面（BMP，0-65535）时的行为未做测试，Java 的 char 类型为 16 位，可能无法正确表示补充字符。
- 内容 emoji 字符在逻辑显示屏（`draw print`）上的渲染效果未做详细验证，可能不支持图标显示。
- 在消息建筑上，内容 emoji 字符与普通文本混排时的对齐和显示效果需要实际验证。
