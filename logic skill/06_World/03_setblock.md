# 03 - setblock（设置方块）

## 导出格式

```
setblock <x> <y> <block> <team> <rotation> <layer>
```

## 参数说明

| 参数     | 类型     | 说明                                            |
| -------- | -------- | ----------------------------------------------- |
| x        | 数值     | tile 坐标 X                                     |
| y        | 数值     | tile 坐标 Y                                     |
| block    | Content  | 方块类型（如 `@conveyor`、`@dirt` 等）          |
| team     | Team     | 队伍（如 `derelict`、`sharded` 等）             |
| rotation | 数值     | 旋转方向（0-3，对应 0°/90°/180°/270°）          |
| layer    | 枚举     | 图层类型：`block`/`floor`/`overlay`             |

## 功能说明

在指定 tile 坐标处设置方块、地板或覆盖层。根据 layer 参数的不同，修改不同图层的内容。

## 源码实现要点

- 对应指令类：`SetBlockI`
- 根据 `TileLayer` 枚举执行不同操作：
  - `block`：设置该坐标处的建筑方块，需要 team 和 rotation 参数。通过 `tile.setBlock()` 方法设置
  - `floor`：设置该坐标处的地板，通过 `tile.setFloor()` 方法设置。不需要 team 和 rotation
  - `overlay`：设置该坐标处的覆盖层，通过 `tile.setOverlay()` 方法设置。不需要 team 和 rotation
- block 参数会被解析为对应的 `Block` 类型内容

## 注意事项

- 此指令为 **privileged（特权）** 指令，只能在世界处理器上运行
- 世界处理器在服务器端执行，不存在客户端同步问题
- layer 参数为 `TileLayer` 枚举值，必须使用有效值（`block`/`floor`/`overlay`），否则会导致灰色积木
- x、y 参数为 **tile 坐标**（瓦片坐标），不是像素坐标
- 当 layer 为 `block` 时，team 和 rotation 参数必须有效；当 layer 为 `floor`/`overlay` 时，team 和 rotation 参数会被忽略
- 使用 `block` 图层设置建筑时，会触发建筑放置事件，可能影响游戏逻辑（如触发触发器）

## 代码示例

```
## 在坐标(50, 50)处放置一个传送带，朝向右（rotation=1），属于 derelict 队伍
setblock 50 50 @conveyor derelict 1 block

## 将坐标(50, 50)的地板改为 dirt
setblock 50 50 @dirt derelict 0 floor
end
```

## 未验证内容

- 无
