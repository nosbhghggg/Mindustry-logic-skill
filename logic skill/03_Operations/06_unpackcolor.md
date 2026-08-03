# 06 - unpackcolor（解包颜色）

## 导出格式

```
unpackcolor <r> <g> <b> <a> <value>
```

## 参数说明

| 参数 | 说明 |
|------|------|
| r | 红色通道输出变量名。解包后的红色分量（0~1）写入此变量 |
| g | 绿色通道输出变量名。解包后的绿色分量（0~1）写入此变量 |
| b | 蓝色通道输出变量名。解包后的蓝色分量（0~1）写入此变量 |
| a | 透明度通道输出变量名。解包后的透明度分量（0~1）写入此变量 |
| value | 待解包的颜色值（double，由 `packcolor` 或颜色字面量生成） |

## 功能说明

**用途：将一个打包的颜色 double 值解包为四个独立的 RGBA 通道变量（每个范围 0~1）。是 `packcolor` 的逆操作。**

`unpackcolor` 将颜色值拆分为四个通道，方便单独读取或修改颜色分量。

### 使用示例

```
# 将红色字面量解包到四个变量
unpackcolor _r _g _b _a %ff0000ff
# _r=1, _g=0, _b=0, _a=1

# 修改透明度后重新打包
unpackcolor _r _g _b _a myColor
op mul _newA _a 0.5
packcolor dimColor _r _g _b _newA
# dimColor 是 myColor 的半透明版本
```

## 源码实现要点

### 语句定义（UnpackColorStatement）

`UnpackColorStatement` 包含五个字段：`r`、`g`、`b`、`a`、`value`。注意与前四个输出变量在前，输入值在最后。构建指令时生成 `UnpackColorI`。

### 指令执行（UnpackColorI.run）

核心逻辑：

```java
var color = Tmp.c1.fromDouble(value.num());
r.setnum(color.r);
g.setnum(color.g);
b.setnum(color.b);
a.setnum(color.a);
```

- 调用 `Tmp.c1.fromDouble()` 将 double 值还原为 Color 对象。该方法从 double 的原始位模式中提取 32 位整数，再拆分为 RGBA 四个 0~255 的字节，最后归一化为 0~1 的浮点数
- 将四个通道分别通过 `setnum()` 写入对应的输出变量
- 所有结果都是数字类型，范围 0~1

### 与 packcolor 的关系

`unpackcolor` 是 `packcolor` 的逆操作：

```
packcolor result r g b a    → result = toDoubleBits(r, g, b, a)
unpackcolor r g b a result  → r, g, b, a = fromDouble(result)
```

先 pack 再 unpack，能还原出原始的 RGBA 值（在 0~1 范围内无损，因为 double 的位模式直接存储了 32 位颜色）。

## 注意事项

- **参数顺序与 packcolor 不同**：`packcolor` 是先 result 后 RGBA，`unpackcolor` 是先 RGBA 后 value。使用时注意不要混淆
- **输出变量必须是可写变量**：四个输出变量不能是常量（如数字字面量），否则写入被静默跳过
- **解包结果范围 0~1**：所有通道值归一化为 0~1 范围，与 `packcolor` 的输入范围一致
- **对非颜色值解包**：如果 `value` 不是由 `packcolor` 或颜色字面量生成的值，解包结果是无意义的随机颜色
- **使用临时变量**：解包通常用于临时分析或修改颜色，建议输出变量使用 `_` 开头的临时变量命名

## 未验证内容

无
