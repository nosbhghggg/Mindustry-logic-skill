# 03 - draw（绘制指令）

> 用途：向处理器的图形缓冲区（graphicsBuffer）写入绘制命令，用于在逻辑显示屏（Logic Display）上绘制图形、文本和图片。绘制内容需通过 `drawflush` 指令刷新到显示屏后才会显示。

## 导出格式

draw 指令的导出格式随绘制模式（type）不同而变化。通用格式为：

```
draw <type> <参数...>
```

积木编辑器中通过下拉菜单选择绘制模式，不同模式显示不同的参数输入框。

## 参数说明

draw 指令内部持有 7 个参数位：`type`（模式，byte 类型）和 `x`、`y`、`p1`、`p2`、`p3`、`p4`（6 个 LVar 参数）。不同模式下各参数含义不同：

| 参数位 | 通用名 | 说明 |
|--------|--------|------|
| type | 模式 | 绘制模式（见下表） |
| x | 参数1 | 通常为 X 坐标或 R 通道 |
| y | 参数2 | 通常为 Y 坐标或 G 通道 |
| p1 | 参数3 | 含义随模式变化 |
| p2 | 参数4 | 含义随模式变化 |
| p3 | 参数5 | 含义随模式变化 |
| p4 | 参数6 | 含义随模式变化 |

### 绘制模式总表

| 模式名 | 内部命令常量 | 参数（x y p1 p2 p3 p4） | 说明 |
|--------|-------------|------------------------|------|
| clear | commandClear (0) | r g b — — — | 清屏，用指定 RGB 颜色填充整个显示屏 |
| color | commandColor (1) | r g b a — — | 设置后续绘制的颜色（RGBA，0-255） |
| col | commandColorPack (2) | packedColor — — — — | 用打包颜色值设置颜色（虚拟命令，自动解包为 color） |
| stroke | commandStroke (3) | width — — — — | 设置后续线条的宽度 |
| line | commandLine (4) | x y x2 y2 — — | 绘制一条线段，从 (x,y) 到 (x2,y2) |
| rect | commandRect (5) | x y width height — — | 绘制填充矩形 |
| lineRect | commandLineRect (6) | x y width height — — | 绘制线框矩形 |
| poly | commandPoly (7) | x y sides radius rotation — | 绘制填充正多边形 |
| linePoly | commandLinePoly (8) | x y sides radius rotation — | 绘制线框正多边形 |
| triangle | commandTriangle (9) | x y x2 y2 x3 y3 | 绘制填充三角形（三个顶点） |
| image | commandImage (10) | x y content size rotation — | 绘制内容图标或显示屏截图 |
| print | commandPrint (11) | x y align — — — | 将 textBuffer 中的文本绘制到显示屏 |
| translate | commandTranslate (12) | x y — — — — | 平移变换矩阵 |
| scale | commandScale (13) | x y — — — — | 缩放变换矩阵（步长为 0.05） |
| rotate | commandRotate (14) | — — degrees — — — | 旋转变换矩阵 |
| reset | commandResetTransform (15) | — — — — — — | 重置变换矩阵为单位矩阵 |

## 功能说明

### 工作原理

draw 指令不直接在显示屏上绘制，而是将绘制命令写入处理器的 `graphicsBuffer`（图形缓冲区）。缓冲区中的命令需要通过 `drawflush` 指令刷新到逻辑显示屏（Logic Display）后，才会被实际渲染。

图形缓冲区（graphicsBuffer）最大容量为 **256** 条命令（`maxGraphicsBuffer = 256`）。当缓冲区已满时，新的 draw 指令会被忽略。

在无头服务器（headless）上，所有 draw 指令都不会执行，因为服务器端没有图形渲染需求。

### 各模式详细说明

**clear（清屏）**
用指定的 RGB 颜色清除整个显示屏画面。参数为 r、g、b 三个通道（0-255），Alpha 固定为 1（完全不透明）。执行时会先丢弃所有待处理的批量精灵，再清除画面。

**color（设置颜色）**
设置后续绘制操作使用的颜色。参数为 r、g、b、a 四个通道（0-255）。此颜色会一直生效直到再次更改。使用 `col` 模式时可以通过颜色选择器自动生成打包颜色值（以 `%` 开头的字符串）。

**stroke（设置线宽）**
设置后续线条绘制（line、lineRect、linePoly）的线宽。参数为宽度值（x 位）。

**line（线段）**
从点 (x, y) 到点 (x2, y2) 绘制一条线段，使用当前颜色和线宽。

**rect / lineRect（矩形）**
以 (x, y) 为左下角，绘制宽度为 width、高度为 height 的矩形。`rect` 为填充模式，`lineRect` 为线框模式。

**poly / linePoly（正多边形）**
以 (x, y) 为中心，绘制 sides 条边、半径为 radius 的正多边形，旋转角度为 rotation。`poly` 为填充模式，`linePoly` 为线框模式。边数上限为 25（`maxSides = 25`）。

**triangle（三角形）**
通过三个顶点 (x,y)、(x2,y2)、(x3,y3) 绘制填充三角形。

**image（图片）**
在 (x, y) 处绘制内容图标。参数 p1 可以是内容引用（如 `@copper`）或其他显示屏建筑。size 为绘制尺寸，rotation 为旋转角度。如果目标是内容图标，会按其原始宽高比缩放；如果目标是另一个显示屏，会绘制该显示屏的画面截图。

**print（文本绘制）**
将处理器 `textBuffer` 中的文本内容绘制到显示屏上。参数为起始坐标 (x, y) 和对齐方式（align）。此模式会将 textBuffer 中的文本逐字符拆分为多条 `commandPrint` 命令写入图形缓冲区，绘制完成后清空 textBuffer。

对齐方式使用 `@` 前缀的名称，可选值包括：`@center`、`@top`、`@bottom`、`@left`、`@right`、`@topLeft`、`@topRight`、`@bottomLeft`、`@bottomRight`。文本支持换行符 `\n`，遇到换行时 Y 坐标下移一行。

**translate / scale / rotate / reset（变换矩阵）**
这四种模式操作显示屏的变换矩阵，影响后续所有绘制操作的位置：
- `translate`：平移 (x, y) 像素。
- `scale`：缩放，实际缩放倍数为 x * 0.05 和 y * 0.05（`scaleStep = 0.05f`）。例如 x=20 表示缩放 1 倍。
- `rotate`：旋转 p1 度。
- `reset`：重置变换矩阵为单位矩阵。

变换矩阵会随显示屏建筑一起保存和加载。

## 源码实现要点

**DrawStatement（语句定义）** — 位于 `LStatements.java`。注册为 `draw`，分类为 `LCategory.io`。持有一个 `GraphicsType type` 枚举和 6 个字符串参数（x、y、p1、p2、p3、p4）。`rebuild()` 方法根据当前模式动态构建不同的参数输入界面。`build()` 方法将 type 的序号转为 byte，连同 6 个参数生成 `DrawI` 指令。

**DrawI（指令执行）** — 位于 `LExecutor.java`。持有 `byte type` 和 6 个 LVar。`run()` 方法分为三个分支：
1. `commandColorPack` 分支：将打包的 double 值按位解包为 RGBA 四个分量，再作为 `commandColor` 命令写入缓冲区。
2. `commandPrint` 分支：将 textBuffer 中的文本逐字符展开为多条 `commandPrint` 命令，计算文本对齐偏移量，处理换行，写入完成后清空 textBuffer。
3. 通用分支：处理其余所有模式。对坐标和参数进行有符号打包（`packSign`，保留符号位和 9 位数值），特殊处理 `commandImage`（将内容 ID 和类型打包）和 `commandScale`（除以 scaleStep）。最终通过 `DisplayCmd.get()` 打包为 long 值加入 graphicsBuffer。

**GraphicsType 枚举** — 位于 `LogicDisplay.java`。定义了 16 种绘制模式，其序号与 `command*` 常量一一对应。其中 `col` 和 `print` 是虚拟命令：`col` 在指令层被解包为 `commandColor`，`print` 在指令层被展开为多条单字符的 `commandPrint` 命令。

**DisplayCmd 结构体** — 使用 `@Struct` 注解自动生成的位打包结构。每个命令为一个 long 值，包含 type（4 位）和 x、y、p1、p2、p3、p4（各 10 位）。坐标和参数通过 `packSign` 进行有符号打包，支持 -511 到 511 的范围。

**LogicDisplayBuild 渲染** — 位于 `LogicDisplay.java`。显示屏在 `draw()` 方法中从命令队列取出命令并执行实际渲染。使用 FrameBuffer 离屏渲染，支持变换矩阵（translate/scale/rotate/reset）。`commandPrint` 通过逻辑字体的字形纹理逐字符绘制。`commandImage` 支持绘制内容图标和其他显示屏的画面截图。

## 注意事项

- 所有 draw 命令只是写入图形缓冲区，必须配合 `drawflush <display>` 指令才能在显示屏上显示。
- 图形缓冲区上限为 256 条命令。`print` 模式会将文本逐字符展开，长文本可能快速占满缓冲区。
- 坐标和参数使用 10 位有符号整数打包，有效范围为 -511 到 511。超出范围的值会被截断。
- 显示屏坐标系的原点 (0, 0) 在左下角，X 轴向右，Y 轴向上。
- Logic Display 的显示尺寸为 80x80 像素，Large Logic Display 为 176x176 像素。超出显示尺寸的绘制内容会被裁剪。
- 多边形的边数上限为 25，超过会被限制为 25。
- `scale` 模式的实际缩放倍数为参数值乘以 0.05。要实现 1 倍缩放（不变），需要传入 20。
- 颜色参数范围为 0-255，超出部分会被 `pack()` 方法截断为 9 位（0-511，但实际渲染时按 255 归一化）。
- 无头服务器上 draw 指令完全不执行。
- `print` 模式绘制完成后会清空 textBuffer，因此需要先用 `print` / `printchar` 指令填充文本，再用 `draw print` 绘制到显示屏。

## 网络同步注意事项

- 图形缓冲区（graphicsBuffer）本身不进行网络同步，它是处理器本地的临时缓冲区。
- 显示屏的命令队列（`commands`）通过 `drawflush` 刷新后存储在显示屏建筑上。显示屏的命令队列和变换矩阵通过建筑的 `write()` / `read()` 方法进行存档序列化。
- 在多人模式下，`drawflush` 刷新的命令会在客户端和服务端各自执行。由于图形渲染仅在客户端发生，服务端（headless）上的 draw 指令不产生效果。
- 显示屏的 FrameBuffer 内容不进行网络同步，每个客户端独立渲染。因此所有客户端看到的画面是一致的（只要处理器逻辑同步）。
- 变换矩阵（translate/scale/rotate）会随显示屏建筑保存，但不会在客户端之间实时同步，仅在存档加载时恢复。

## 未验证内容

- `image` 模式绘制其他显示屏截图时的具体行为和性能表现未做详细测试。
- 变换矩阵嵌套使用时的渲染顺序和矩阵叠加效果需要实际验证。
- `col` 模式（commandColorPack）的打包颜色值格式（`%` 开头的字符串）在不同输入方式下的具体编码规则。
- `reset` 模式在积木编辑器中是否有对应的 UI 入口（源码 switch 中未见 reset 的 case 处理），可能需要通过文本指令直接使用。
- 坐标值超出 -511 到 511 范围时的具体截断行为和视觉表现。
