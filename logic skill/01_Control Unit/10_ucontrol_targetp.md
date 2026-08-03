# 10 - ucontrol targetp（瞄准对象）

## 导出格式

```
ucontrol targetp unit shoot 0 0 0
```

共7个token：`ucontrol` `targetp` `<p1=unit>` `<p2=shoot>` `<p3=0>` `<p4=0>` `<p5=0>`

## 参数说明

| 参数 | 位置 | 类型 | 说明 |
|------|------|------|------|
| unit | p1 | Teamc | 目标对象，可以是 Unit 或 Building |
| shoot | p2 | number | 射击开关，0=只瞄准不射击，非0=射击 |
| p3 | p3 | - | 保留参数，固定为0 |
| p4 | p4 | - | 保留参数，固定为0 |
| p5 | p5 | - | 保留参数，固定为0 |

## 功能说明

让单位武器瞄准指定的对象（单位或建筑），并可选择是否射击。

与 `target` 不同，`targetp` 瞄准的是一个具体的游戏对象而非固定坐标，因此当目标移动时，单位的瞄准位置会跟随目标实时更新。

## 源码实现要点

- 设置瞄准控制模式（`ai.aimControl = targetp`）：标记当前为对象瞄准模式
- 设置主目标（`ai.mainTarget = p1.obj() instanceof Teamc t ? t : null`）：判断 p1 是否为 `Teamc` 接口实例，是则设为主目标，否则设为 null
- 设置射击开关（`ai.shoot = bool(p2)`）
- **`Teamc` 接口说明**：`Teamc` 是 `Unit` 和 `Building` 共同实现的接口，所以 `targetp` 既可以瞄准单位，也可以瞄准建筑

## 注意事项

- p1 参数**必须是 `Teamc` 接口实例**。如果传入的不是 `Teamc`（例如传了数字或 null），主目标会被设为 null，单位不会瞄准任何目标
- 布尔参数规则：0 = false，非0 = true
- 目标移动时，单位武器会自动跟随瞄准
- targetp 会触发控制状态（通过 `checkLogicAI()` 将单位标记为被逻辑控制），与所有 ucontrol 子指令行为一致。

## 源码验证结论

- `targetp` 的 `p1` 参数接受任何 `Teamc` 对象（包括己方单位、己方建筑、敌方单位、敌方建筑），不进行队伍过滤。源码中仅检查 `p1.obj() instanceof Teamc t`，无 team 判断。
- `shoot` 参数由 `p2.bool()` 设置，同样不区分队伍。但实际是否射击取决于武器系统的逻辑，武器系统通常不会射击己方目标。
- 因此 targetp 可以用于瞄准己方建筑/单位（如维修场景），但不会实际射击己方目标。

