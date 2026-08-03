# 04 - spawn（生成单位）

## 导出格式

```
spawn <type> <x> <y> <rotation> <team> <result> <effect>
```

## 参数说明

| 参数     | 类型     | 说明                                       |
| -------- | -------- | ------------------------------------------ |
| type     | Content  | 单位类型（如 `@dagger`、`@mono` 等）       |
| x        | 数值     | 生成位置 X（像素坐标）                      |
| y        | 数值     | 生成位置 Y（像素坐标）                      |
| rotation | 数值     | 生成朝向（角度）                            |
| team     | Team     | 队伍（如 `sharded`、`crux` 等）            |
| result   | 输出变量 | 输出：生成的单位引用                        |
| effect   | 数值     | 是否显示生成效果（1=有效果，0=无效果）     |

## 功能说明

在指定位置生成一个指定类型的单位，并输出该单位的引用。可以选择是否显示生成特效。

## 源码实现要点

- 对应指令类：`SpawnUnitI`
- 调用 `UnitTypes.create()` 方法创建单位实例
- 坐标为像素坐标，通过 `(int)p2.num() * tilesize` 等方式转换（具体取决于实现）
- 生成后设置单位的朝向（`unit.rotation`）、队伍（`unit.team`）
- 如果 effect 为 true，会播放单位的生成特效
- 生成的单位会被添加到全局单位列表中

## 注意事项

- 此指令为 **privileged（特权）** 指令，只能在世界处理器上运行
- 世界处理器在服务器端执行，不存在客户端同步问题
- type 参数为 content 类型的单位类型，必须使用有效值（如 `@dagger`）
- result 输出生成的单位引用，可以用于后续的单位控制
- 大量生成单位可能导致服务器性能下降

## 代码示例

```
## 在坐标(100, 100)处生成一个 dagger 单位，朝向右，属于 crux 队伍
spawn @dagger 100 100 0 crux _spawnedUnit 1

## 读取生成单位的血量
sensor _hp _spawnedUnit @health
print _hp
printflush message1
end
```

## 未验证内容

- 无
