# 05 - packcolor（打包颜色）

## 导出格式

```
packcolor <result> <r> <g> <b> <a>
```

## 参数说明

| 参数 | 说明 |
|------|------|
| result | 结果变量名。打包后的颜色值（double）写入此变量 |
| r | 红色通道，范围 0~1 |
| g | 绿色通道，范围 0~1 |
| b | 蓝色通道，范围 0~1 |
| a | 透明度通道，范围 0~1（0=全透明，1=不透明） |

## 功能说明

**用途：将四个 0~1 范围的颜色通道值打包为一个 double 数值，供 `draw color` 等绘制指令使用。**

Logic 中的颜色以 double 类型存储。`packcolor` 将 RGBA 四个通道压缩到一个 double 值中，方便在变量中传递和存储。

### 使用示例

```
# 打包红色（R=1, G=0, B=0, A=1）
packcolor red 1 0 0 1

# 打包半透明绿色
packcolor semiGreen 0 1 0 0.5

# 将打包后的颜色用于绘制
draw color red 0 0 0 0
draw rect 10 10 50 50 0 0
```

## 源码实现要点

### 语句定义（PackColorStatement）

`PackColorStatement` 包含五个字段：`result`、`r`、`g`、`b`、`a`。构建指令时生成 `PackColorI`。

### 指令执行（PackColorI.run）

核心逻辑：

```java
result.setnum(Color.toDoubleBits(
    Mathf.clamp(r.numf()),
    Mathf.clamp(g.numf()),
    Mathf.clamp(b.numf()),
    Mathf.clamp(a.numf())
));
```

- 对每个通道调用 `Mathf.clamp()` 将值限制在 [0, 1] 范围内。超出范围的值会被截断
- 调用 `Color.toDoubleBits()` 将四个通道打包为一个 double 值
- 结果通过 `setnum()` 写入，为数字类型

### Color.toDoubleBits 方法

将 RGBA 四个 [0, 1] 范围的浮点数转换为 0~255 的整数，然后组合为一个 32 位整数，最终存储为 double 的原始位表示。这个 double 值不是常规的数学数值，而是将颜色信息的位模式直接存储在 double 中。

## 注意事项

- **通道范围会被钳制**：所有通道值会被 `Mathf.clamp` 限制在 [0, 1] 范围内。传入负数变为 0，传入大于 1 的值变为 1
- **结果不是常规数字**：打包后的 double 值是颜色的位模式，不能用于数学运算。对其进行 `op` 运算没有意义
- **与颜色字面量的关系**：Logic 支持颜色字面量（如 `%ff0000ff`），在解析时也是调用 `Color.toDoubleBits` 生成相同的 double 值。因此 `packcolor red 1 0 0 1` 和 `set red %ff0000ff` 效果相同
- **命名颜色**：Logic 还支持命名颜色语法 `%[colorName]`，如 `%[accent]`。这与 `packcolor` 无直接关系，但生成相同格式的值
- **a=0 为全透明**：透明度通道 a 为 0 时颜色完全不可见，为 1 时完全不透明

## 未验证内容

无
