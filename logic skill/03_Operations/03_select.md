# 03 - select（条件选择）

## 导出格式

```
select <result> <op> <comp0> <comp1> <a> <b>
```

## 参数说明

| 参数 | 说明 |
|------|------|
| result | 结果变量名。条件选择的结果写入此变量 |
| op | 条件运算符（ConditionOp 枚举名，见下方列表） |
| comp0 | 条件比较的第一个操作数 |
| comp1 | 条件比较的第二个操作数 |
| a | 条件为真时返回的值 |
| b | 条件为假时返回的值 |

## 功能说明

**用途：根据条件比较结果，从两个值中选择一个赋给目标变量。相当于三元运算符 `result = (comp0 op comp1) ? a : b`。**

`select` 指令先对 `comp0` 和 `comp1` 进行条件运算（使用指定的 `op` 运算符），如果条件成立则将 `a` 赋给 `result`，否则将 `b` 赋给 `result`。

### 条件运算符列表

| 运算符名 | 符号 | 说明 |
|----------|------|------|
| `equal` | `==` | 相等。数字比较使用浮点容差 0.000001；对象使用 `Structs.eq` |
| `notEqual` | `not` | 不等。与 `equal` 相反 |
| `lessThan` | `<` | 小于 |
| `lessThanEq` | `<=` | 小于等于 |
| `greaterThan` | `>` | 大于 |
| `greaterThanEq` | `>=` | 大于等于 |
| `strictEqual` | `===` | 严格相等。类型与值都必须相同，数字比较无浮点容差 |
| `always` | `always` | 恒真。始终返回 a，忽略 comp0 和 comp1 |

### 使用示例

```
# 如果 hp 小于 50，返回 0（危险），否则返回 1（安全）
select status lessThan hp 50 0 1

# 如果单位是 null（comp0 与 null 比较），选择备用值
select backup equal myUnit null 1 0

# always 运算符：始终选择 a
select result always 0 0 myValue 0
```

## 源码实现要点

### 语句定义（SelectStatement）

`SelectStatement` 包含六个字段：`result`、`op`（ConditionOp 枚举）、`comp0`、`comp1`、`a`、`b`。构建指令时生成 `SelectI`。

### 指令执行（SelectI.run）

核心逻辑：

```java
if(result.constant) return;
result.set(op.test(comp0, comp1) ? a : b);
```

- 首先检查 `result` 是否为常量，如果是则直接返回（静默跳过）
- 调用 `op.test(comp0, comp1)` 进行条件判断，根据结果选择 `a` 或 `b`
- 使用 `result.set()` 赋值，保留所选值的类型（数字或对象）

### ConditionOp.test 方法

条件判断的内部逻辑：

1. **`strictEqual`（===）**：检查两个变量的类型是否一致（`isobj` 相同），再比较值。数字用精确 `==`，对象用 `Structs.eq`
2. **其他运算符**：
   - 如果运算符提供了对象函数（`objFunction`），且两个操作数**都是对象**，则使用对象函数比较。`equal` 和 `notEqual` 提供了对象函数
   - 否则，对两个操作数调用 `num()` 取数值后，用数值函数比较
3. **`always`**：直接返回 true，不检查任何操作数

### 与 jump 指令的关系

`select` 使用的 `ConditionOp` 与 `jump` 指令使用的是同一套条件运算符枚举。区别在于：
- `jump`：条件成立时跳转
- `select`：条件成立时选择 a，否则选择 b

## 注意事项

- **结果保留类型**：`select` 使用 `set()` 赋值而非 `setnum()`，所以 a 或 b 如果是对象（如单位引用），结果也会是对象。这是 `select` 与 `op` 的重要区别——`op` 的结果始终是数字
- **`always` 运算符的用途**：当 `op` 为 `always` 时，条件恒为真，`select` 始终返回 a。这可以用于简化代码或作为占位
- **`equal` 与 `strictEqual` 的区别**：与 `op` 指令中一致，`equal` 有浮点容差，`strictEqual` 无容差且要求类型一致
- **comp0 和 comp1 是比较对象，a 和 b 是选择对象**：不要混淆这两组参数。comp0/comp1 用于条件判断，a/b 是待选择的值
- **写入常量无效**：如果 `result` 是常量变量，赋值被静默跳过

## 未验证内容

无
