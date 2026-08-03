# 02 - getblock（获取方块）

## 导出格式

```
getblock <result> <x> <y> <layer>
```

## 参数说明

| 参数   | 类型     | 说明                                         |
| ------ | -------- | -------------------------------------------- |
| result | 输出变量 | 输出：获取到的方块/地板/覆盖层内容           |
| x      | 数值     | tile 坐标 X                                  |
| y      | 数值     | tile 坐标 Y                                  |
| layer  | 枚举     | 图层类型：`block`/`floor`/`overlay`          |

## 功能说明

获取指定 tile 坐标处的方块、地板或覆盖层信息。根据 layer 参数的不同，返回不同图层的内容。

## 源码实现要点

- 对应指令类：`GetBlockI`
- 根据 `TileLayer` 枚举获取不同图层内容：
  - `block`：获取该坐标处的建筑（Building），输出为建筑引用
  - `floor`：获取该坐标处的地板（Floor），输出为地板类型
  - `overlay`：获取该坐标处的覆盖层（Overlay），输出为覆盖层类型
- 坐标会被截断为整数，对应世界中的 tile 坐标系统

## 注意事项

- 此指令为 **privileged（特权）** 指令，只能在世界处理器上运行
- 世界处理器在服务器端执行，不存在客户端同步问题
- layer 参数为 `TileLayer` 枚举值，必须使用有效值（`block`/`floor`/`overlay`），否则会导致灰色积木
- x、y 参数为 **tile 坐标**（瓦片坐标），不是像素坐标（像素坐标 = tile 坐标 × tilesize=8）
- 当 layer 为 `block` 时，如果该坐标没有建筑，输出为 null

## 代码示例

```
## 获取坐标(50, 50)处的建筑
getblock _building 50 50 block

## 判断是否有建筑
op notEqual _hasBuild _building 0
jump ifBuild label_checkDone
  print "no building here"
  printflush message1
label_checkDone:
end
```

## 未验证内容

- 无
