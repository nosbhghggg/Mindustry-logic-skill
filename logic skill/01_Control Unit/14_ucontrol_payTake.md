# 14 - ucontrol payTake（拾取载荷）

## 导出格式

```
ucontrol payTake takeUnits 0 0 0 0
```

共7个token：`ucontrol` `payTake` `<p1=takeUnits>` `<p2=0>` `<p3=0>` `<p4=0>` `<p5=0>`

## 参数说明

| 参数 | 位置 | 类型 | 说明 |
|------|------|------|------|
| takeUnits | p1 | number | 拾取模式，0=拾取建筑载荷，非0=拾取单位载荷 |
| p2 | p2 | - | 保留参数，固定为0 |
| p3 | p3 | - | 保留参数，固定为0 |
| p4 | p4 | - | 保留参数，固定为0 |
| p5 | p5 | - | 保留参数，固定为0 |

## 功能说明

让单位拾取附近的载荷。根据 `takeUnits` 参数的不同，可以拾取建筑载荷（如建筑方块）或单位载荷（如地面单位）。

## 源码实现要点

- **takeUnits 非0（拾取单位载荷）**：
  - 查找附近的 AI 地面单位，查找距离 = `unit.type.hitSize * 2f`（与单位体积相关）
  - 筛选条件：目标不等于自身（`u != unit`）、是 AI 单位（`u.isAI()`）、已落地（`u.isGrounded()`）、可被拾取（`canPickup`）、在范围内（`within`）
  - 满足条件后调用拾取单位载荷（`Call.pickedUnitPayload`）
- **takeUnits 为0（拾取建筑载荷）**：
  - 获取当前位置建筑
  - 拾取建筑载荷或直接拾取建筑（`Call.pickedBuildPayload`）

## 注意事项

- **传输超时**：同 `itemDrop`（1.5 秒传输延迟，`transferDelay = 60f * 1.5f`）
- 布尔参数规则：0 = false，非0 = true
- 拾取单位载荷时，查找范围与单位体积相关（`unit.type.hitSize * 2f`），体积越大的单位搜索范围越广
- 拾取单位载荷时，目标单位必须是已落地的 AI 地面单位
- 单位必须具备载荷携带能力（实现 `Payloadc` 接口）
- payTake 会触发控制状态（通过 `checkLogicAI()` 将单位标记为被逻辑控制），与所有 ucontrol 子指令行为一致。

