# 18 - setprop（设置属性）

## 导出格式

```
setprop <type> <of> <value>
```

## 参数说明

| 参数  | 类型     | 说明                                                         |
| ----- | -------- | ------------------------------------------------------------ |
| type  | Content  | 属性类型：物品（如 `@copper`）、液体（如 `@water`）或 sensor 属性（如 `@enabled`） |
| of    | 哭建筑引用 | 目标建筑                                                     |
| value | 数值     | 要设置的值                                                   |

## 功能说明

直接设置建筑的属性，包括物品数量、液体数量、启用状态等。根据 type 参数的不同，设置不同的属性。

## 源码实现要点

- 对应指令类：`SetPropI`
- 根据 type 参数的类型执行不同操作：
  - **物品类型**（如 `@copper`）：调用建筑的 `items.set(type, (int)value)` 方法，直接设置建筑中该物品的数量
  - **液体类型**（如 `@water`）：调用建筑的 `liquids.set(type, value)` 方法，直接设置建筑中该液体的数量
  - **sensor 属性**（如 `@enabled`）：设置建筑的启用状态等属性
- of 参数必须为有效的建筑引用

## 注意事项

- 此指令为 **privileged（特权）** 指令，只能在世界处理器上运行
- 世界处理器在服务器端执行，不存在客户端同步问题
- type 参数可以是物品（`@copper` 等）、液体（`@water` 等）或 sensor 属性（`@enabled` 等）
- 此指令直接修改建筑的内部数据，可以绕过正常的物品/液体传输限制
- 设置的值会立即生效，无需等待游戏更新

## 代码示例

```
## 直接设置建筑 myBuild 中的铜数量为 100
setprop @copper myBuild 100

## 直接设置建筑 myBuild 中的水量为 50
setprop @water myBuild 50

## 启用建筑 myBuild
setprop @enabled myBuild 1
end
```

## 未验证内容

- 无
