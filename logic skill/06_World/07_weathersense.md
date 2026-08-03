# 07 - weathersense（检测天气）

## 导出格式

```
weathersense <weather> <result>
```

## 参数说明

| 参数    | 类型     | 说明                                   |
| ------- | -------- | -------------------------------------- |
| weather | Content  | 天气类型（如 `@rain`、`@snow` 等）     |
| result  | 输出变量 | 输出：1=该天气正在生效，0=未生效       |

## 功能说明

检测指定的天气是否正在世界中生效。

## 源码实现要点

- 对应指令类：`SenseWeatherI`
- 遍历当前活跃的天气列表（`state.rules.weather`），检查指定天气是否在其中
- 如果天气正在活跃状态，输出 1；否则输出 0

## 注意事项

- 此指令为 **privileged（特权）** 指令，只能在世界处理器上运行
- 世界处理器在服务器端执行，不存在客户端同步问题
- weather 参数为天气类型，必须使用有效值（如 `@rain`、`@snow`、`@sandstorm` 等）
- 天气需要通过 `weatherset` 指令或游戏规则设置后才能被检测到

## 代码示例

```
## 检测是否正在下雨
weathersense @rain _isRaining

## 根据天气状态显示消息
op equal _raining _isRaining 1
jump notRaining label_skipRain
  print "It's raining!"
  printflush message1
  jump label_done label_end
label_skipRain:
  print "No rain."
  printflush message1
label_end:
end
```

## 未验证内容

- 无
