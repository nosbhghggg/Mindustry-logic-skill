# 05 - bullet（生成子弹）

## 导出格式

```
bullet <result> <from> <index> <x> <y> <rotation> <team> <owner> <damage> <velocityScl> <lifeScl> <aimX> <aimY>
```

## 参数说明

| 参数        | 类型     | 说明                                            |
| ----------- | -------- | ----------------------------------------------- |
| result      | 输出变量 | 输出：生成的子弹引用                            |
| from        | 建筑引用 | 子弹来源建筑（用于确定武器类型）                |
| index       | 数值     | 武器索引（建筑上的第几个武器）                  |
| x           | 数值     | 生成位置 X（像素坐标）                           |
| y           | 数值     | 生成位置 Y（像素坐标）                           |
| rotation    | 数值     | 子弹飞行方向（角度）                            |
| team        | Team     | 队伍                                            |
| owner       | 建筑引用 | 子弹所有者（用于伤害归属判定）                  |
| damage      | 数值     | 伤害缩放（1=原始伤害，0=无伤害）                |
| velocityScl | 数值     | 速度缩放（1=原始速度）                          |
| lifeScl     | 数值     | 寿命缩放（1=原始寿命）                          |
| aimX        | 数值     | 瞄准位置 X（用于子弹追踪等逻辑）                |
| aimY        | 数值     | 瞄准位置 Y                                      |

## 功能说明

从指定建筑的指定武器创建一颗子弹，可以自定义子弹的位置、方向、队伍、伤害、速度、寿命等参数。

## 源码实现要点

- 对应指令类：`SpawnBulletI`
- 从 `from` 建筑的武器列表中，按 `index` 索引取出对应的 `Weapon` 类型
- 调用武器的子弹创建方法，根据各项缩放参数生成子弹
- 子弹的 `owner` 和 `team` 可以与 `from` 不同，提供了灵活的子弹归属控制
- damage、velocityScl、lifeScl 均为缩放系数，1 表示使用武器原始值

## 注意事项

- 此指令为 **privileged（特权）** 指令，只能在世界处理器上运行
- 世界处理器在服务器端执行，不存在客户端同步问题
- `from` 参数必须为有效的建筑引用，且该建筑必须有武器（如炮塔）
- `index` 参数对应建筑武器数组的索引，如果超出范围可能导致异常
- `owner` 参数用于伤害归属判定，如果为 null 则伤害归属于 `from` 建筑

## 代码示例

```
## 从炮塔 turret1 的第一个武器发射子弹，朝向 90 度
bullet _bullet turret1 0 400 400 90 sharded turret1 1 1 1 0 0

## 读取子弹的伤害值
sensor _dmg _bullet @damage
print _dmg
printflush message1
end
```

## 未验证内容

- 无
