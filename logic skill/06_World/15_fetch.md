# 15 - fetch（获取数量）

## 导出格式

```
fetch <type> <result> <team> <index> <extra>
```

## 参数说明

| 参数   | 类型     | 说明                                                         |
| ------ | -------- | ------------------------------------------------------------ |
| type   | 枚举     | 查询类型（FetchType 枚举值，见下方可选值）                   |
| result | 输出变量 | 输出：数量或单位/建筑引用                                    |
| team   | Team     | 队伍                                                         |
| index  | 数值     | 索引（获取具体实例时使用，从 0 开始）                        |
| extra  | 数值     | 额外参数（单位类型 ID 或建筑类型 ID，部分类型使用）           |

## 功能说明

获取指定队伍的单位/建筑数量，或通过索引获取指定类型的单位/建筑实例。

### 查询类型（FetchType）可选值

| 类型         | 说明                                       | extra 参数     |
| ------------ | ------------------------------------------ | -------------- |
| unit         | 获取指定索引的单位实例                     | 单位类型 ID    |
| build        | 获取指定索引的建筑实例                     | 建筑类型 ID    |
| coreCount    | 获取核心数量                               | 不使用         |
| unitCount    | 获取指定类型单位数量                       | 单位类型 ID    |
| buildCount   | 获取指定类型建筑数量                       | 建筑类型 ID    |
| playerCount  | 获取玩家数量                               | 不使用         |

## 源码实现要点

- 对应指令类：`FetchI`
- 根据 `FetchType` 枚举执行不同查询：
  - `unit`：从队伍的单位列表中按索引取出单位实例
  - `build`：从队伍的建筑列表中按索引取出建筑实例
  - `coreCount`：统计队伍的核心数量
  - `unitCount`：统计队伍中指定类型单位的数量
  - `buildCount`：统计队伍中指定类型建筑的数量
  - `playerCount`：统计队伍中的玩家数量
- team 参数决定查询哪个队伍的数据

## 注意事项

- 此指令为 **privileged（特权）** 指令，只能在世界处理器上运行
- 世界处理器在服务器端执行，不存在客户端同步问题
- type 参数为 `FetchType` 枚举值，必须使用有效值，否则会导致灰色积木
- 使用 `unit`/`build` 类型时，需要先用对应的 `Count` 类型获取总数，再用索引逐个获取实例
- extra 参数为单位类型 ID 或建筑类型 ID，可通过 `lookup` 指令获取

## 代码示例

```
## 获取 sharded 队伍的核心数量
fetch coreCount _coreCount sharded 0 0

## 获取 sharded 队伍的第 0 个核心
fetch build _core sharded 0 @core

## 获取 sharded 队伍的 mono 单位数量
lookup _monoId @mono 0
fetch unitCount _monoCount sharded 0 _monoId
print _monoCount
printflush message1
end
```

## 未验证内容

- 无
