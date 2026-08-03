# 08 - ucontrol boost（助推）

## 导出格式

```
ucontrol boost enable 0 0 0 0
```

## 参数

| 参数 | 说明 |
|------|------|
| enable | 助推开关。**0 = 关闭助推**，**非 0 = 开启助推** |
| p2 ~ p5 | 无实际用途，填 0 |

> 布尔参数规则：0 表示 false，非 0 表示 true。

## 功能

控制单位的助推状态。助推可以使单位升空飞行或加速移动。

## 源码实现

1. 设置助推状态（`ai.boost = bool(p1)`），将参数转换为布尔值
2. 在 LogicAI 的更新移动（updateMovement）中，如果单位 **可助推**（canBoost）且 **非飞行类型**：
   - 判断是否应该助推：助推开启 **或** 站在固体方块上 **或** 飞行中且无法降落
   - 根据判断结果调整单位升降高度（elevation）

## 注意事项

- **只有 canBoost 的单位才有效**。部分单位类型不支持助推，对它们使用 boost 没有任何效果
- **飞行类型单位本身就在飞行**，boost 对它们无额外的升空效果
- boost 的主要作用是让地面单位临时升空越过障碍物或在必要时加速
- boost 会触发控制状态（通过 `checkLogicAI()` 将单位标记为被逻辑控制），与所有 ucontrol 子指令行为一致。

> **源码验证**：boost 对飞行类型单位（`unit.type.flying == true`）完全无效。源码中 boost 逻辑的条件为 `unit.type.canBoost && !unit.type.flying`，飞行类型单位的整个 boost 代码块被跳过。

## 适用单位示例

- 支持 boost 的地面单位（如部分机甲）可以使用 boost 临时升空
- 纯飞行单位（如 mono、flare）使用 boost 通常无效

---

