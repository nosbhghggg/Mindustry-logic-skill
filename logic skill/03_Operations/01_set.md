# 01 - set（变量赋值）

## 导出格式

```
set <result> <value>
```

## 参数说明

| 参数 | 说明 |
|------|------|
| result | 目标变量名。赋值的结果将写入此变量 |
| value | 源值。可以是数字字面量、变量名、或 `@` 开头的系统变量 |

## 功能说明

**用途：将一个值赋给目标变量。**

`set` 是最基本的赋值指令。它将 `value` 的值完整复制到 `result` 中。赋值时会保留源变量的类型——如果源是数字，目标也变成数字；如果源是对象（如单位引用、建筑引用、content 引用），目标也变成对象。

### 赋值类型示例

```
set myNum 42
set myFlag 1
set savedUnit @unit
set myColor %ff0000ff
```

- `set myNum 42`：将数字 42 赋给 `myNum`
- `set savedUnit @unit`：将当前绑定单位的对象引用赋给 `savedUnit`
- `set myColor %ff0000ff`：将颜色字面量（红色，不透明）赋给 `myColor`

## 源码实现要点

### 语句定义（SetStatement）

`SetStatement` 包含两个字段：`to`（目标变量）和 `from`（源值）。构建指令时生成 `SetI`，参数顺序为 `new SetI(builder.var(from), builder.var(to))`。

### 指令执行（SetI.run）

核心逻辑只有一行：

```java
if(!to.constant) to.set(from);
```

- 首先检查目标变量是否为常量（`to.constant`）。如果是常量（如数字字面量、`@` 开头的系统只读变量），则**静默跳过**，不执行赋值
- 非常量时，调用 `to.set(from)` 完成赋值

### LVar.set 方法

`set(LVar other)` 会完整复制源变量的状态：

- 复制 `isobj` 标志（标识变量是数字还是对象）
- 如果是对象，复制 `objval`（对象引用）
- 如果是数字，复制 `numval`（数值），并将无效值（NaN/Infinity）归零

这意味着 `set` 是**类型感知**的赋值，不会将对象引用强转为数字或反之。

## 注意事项

- **写入常量变量无效**：如果 `result` 是数字字面量（如 `set 10 5`）或 `@` 开头的只读系统变量（如 `@time`、`@tick` 等），赋值会被静默忽略
- **`@counter` 可以被 set**：`@counter` 不是常量变量，可以用 `set @counter 0` 来重置程序计数器实现跳转。但这种跳转方式容易出错，建议优先使用 `jump` 标签跳转或 `end` 指令
- **对象赋值是引用复制**：`set savedUnit @unit` 后，`savedUnit` 和 `@unit` 指向同一个单位对象，修改单位属性会同时影响两者
- **变量默认值**：未初始化的变量默认是 null 对象。对其进行 `num()` 取值会返回 0

## 未验证内容

无
