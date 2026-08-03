# 09 - ucontrol target（瞄准坐标）

## 导出格式

```
ucontrol target x y shoot 0 0
```

共7个token：`ucontrol` `target` `<p1=x>` `<p2=y>` `<p3=shoot>` `<p4=0>` `<p5=0>`

## 参数说明

| 参数 | 位置 | 类型 | 说明 |
|------|------|------|------|
| x | p1 | number | 目标坐标x（tile坐标） |
| y | p2 | number | 目标坐标y（tile坐标） |
| shoot | p3 | number | 射击开关，0=只瞄准不射击，非0=射击 |
| p4 | p4 | - | 保留参数，固定为0 |
| p5 | p5 | - | 保留参数，固定为0 |

## 功能说明

让单位武器瞄准指定坐标，并可选择是否射击。

该指令只控制单位的瞄准方向和射击行为，**不控制单位移动**。单位会停留在原地，武器自动转向目标坐标。

## 源码实现要点

- 设置位置目标（`ai.posTarget.set(x, y)`）：将传入的坐标写入AI的位置目标缓存
- 设置瞄准控制模式（`ai.aimControl = target`）：标记当前为坐标瞄准模式
- 清空主目标（`ai.mainTarget = null`）：因为是坐标瞄准，不需要具体对象目标
- 设置射击开关（`ai.shoot = bool(p3)`）：根据第三个参数决定是否开火
- 在 `LogicAI` 的 `target()` 方法中返回 `posTarget`，单位武器自动瞄准该位置

## 注意事项

- **只控制瞄准和射击，不控制移动**。若需要单位移动到某处，请配合 `ucontrol move` 使用
- 所有 x、y 参数均为 **tile坐标**，处理器内部通过世界坐标转换（`World.unconv`）转为像素坐标（乘以 `tilesize = 8`）
- 布尔参数规则：0 = false，非0 = true
- 武器是否能实际射击还取决于武器自身的射程、冷却等属性
- target 会触发控制状态（通过 `checkLogicAI()` 将单位标记为被逻辑控制），与所有 ucontrol 子指令行为一致。

