## 目前兵控逻辑一共分为3类,群控,多控,还有单控制.为了不让逻辑与逻辑之间争夺抢单位.在逻喂马辑的编写路上就自我进化出了相关的绑定规则.

1.每个类型的逻辑都有属于自己的绑定规范与绑定优先级.      单控逻辑=多控逻辑>群控逻辑。基于这个绑定优先级衍生出了以下规范

1.单控逻辑在确认要控制的单位之前应该先检查单位的控制方（绑定单位不是控制，单位只有绑定了之后才能使用指令进行控制，如果一个逻辑只绑定单位不控制单位，那就说明这个逻辑没有控制这个单位），如果单位没有被玩家控制则进行下一步检查，
进入下一步检查后检查单位是否被其他逻辑所控制，这时如果单位没有被其他逻辑所控制指责直接选定该单位，如果单位的控制方已经有逻辑了则检查flag，判断他是不是群控逻辑，如果这个时候单位也没有flag就直接选定该单位

在匹配后的第一时间对单位进行flag标识，flag标识也有特定规范，一般为floor(@thisx)*1000+floor(@thisx),这个一千也很有讲究因为大部分的地图的大小长宽都是在一千以内,所以根据这个标识可以很轻松的推断出绑定逻辑的指定位置，为了避免因有些逻辑的大小问题返回的坐标出现小数，所以使用floor进行压制。如果需要flag存储相关数据时，可以将这个flag再次乘以10的倍数从而用flag存储相关数据，这样不同的单位就能分别设置或读取不同的属性信息了。


匹配完单位并标记完flag后并不意味这个单位我们可以一直控制。我们还需要进行flag冲突和绑定控制冲突，为什么要这么说呢。假设我们在同一帧内同时放下两个相同的逻辑（或者在短时间内），这两个逻辑同时执行代码，导致双方都认为单位没有被其他逻辑绑定，同时还伴随及帧差问题，所以两个逻辑都会给单位添加flag，并选定该单位为控制单位，然后就出事了。
所以我们要进行冲突判断，最简单的方式就是每次循环都检测单位的flag是否为逻辑给的flag，如果发生了变化就放弃该单位的控制，并重新寻找单位，这样做有效避免了帧差问题，
jump 10 equal initial true
op floor _0 @thisx 0
op mul _1 _0 1000
op floor _2 @thisy 0
op add unFlag _1 _2
print "▽设置需要绑定的单位"
ubind @poly
sensor unType @unit @type
jump 6 equal unType 0
set initial true
sensor unDead @unit @dead
jump 14 equal unDead 1
sensor flag @unit @flag
jump 23 strictEqual unFlag flag
ubind unType
sensor controlled @unit @controlled
jump 14 greaterThan controlled 1
jump 20 equal controlled 0
sensor flag @unit @flag
jump 14 notEqual flag 0
ucontrol flag unFlag 0 0 0 0
end
print "▽控制流编写"
ucontrol move @thisx @thisy 0 0 0




观察这个逻辑，初始化内容只执行一次就不再执行，这里我们注意到print "▽设置需要绑定的单位"，为啥要把ubind @poly罗到开头呢，因为不会逻辑的玩家在打开逻辑的时候不知道如何更改单位，可能在修改逻辑的过程中将逻辑修改错误，所以直把ubind提到了最头部方便玩家修改控制单位，ubind指令上还自带一个小箭头可以快速修改单位，以防将单位名称收入错误，
因为在放下这个逻辑的时候场上可能还没有单位，为了不让@type检测到空的值导致出现异常，所以加入了jump跳转判断。执行完了一系列初始化后首先判断绑定的单位是否已经死亡，如果死亡则直接触发单位绑定流程，如果单位没有死亡则继续检查单位的flag有没有发生变化，如果发生变化说明绑定过程中发生了冲突也触发重新绑定单位流程，如果两者检查全部都过了，则自动执行相关控制语句。

如果以上两个检查任意一个失败就会重新触发选定单位流程，
总结一下单控逻辑的绑定流程：
1. controlled >1 说明单位在编队或者被玩家控制,因此直接重新寻找单位,
2.检查通过后再检查 controlled 是否被其他逻辑所控制，如果===1说明被其他逻辑控制了，如果==0说明没有任何逻就是他故此直接绑定该单位
3.如果如果===1说明被其他逻辑控制了，这时需要检查单位的flag是否为0，这一步检查是判断他是不是群控逻辑。如果flag为0则选定该单位

这样样是不是写的非常清楚。注意看，jump直接指向了ucontrol move语句，这样既优化了运行效率，他不耽误使用print当注释。继续注意，选择完要绑定的单位后是直接使用了end指令让他回到了头部，而不是向下继续运行控制流，1.是写end能够让我们看到它就能知道上边是单位选择流程与初始化相关，啊简称分界线了简称了，2是不让print执行，虽然我们的逻辑不涉及到信息版打印，但这也是个不错的习惯呢。
但是这个逻辑唯一的缺点就是控制的单位如果在中途被玩家控制就炸了，所以说如果有出生玩家控制了被单控逻辑绑定的单位，那也是神了


##介绍完了单扣我们接下来讲群控，群控逻辑的绑定的优先级是最低的，绑定一个单位，判断这个单位有没有flag，直接跳过就行，如果单位没有flag则正常绑定就行了，无需给单位任何flag，群控逻辑主要是控制批量相同的单位去进行采矿或者执行攻击任务

jump 6 notEqual init 0
set init 1
set core_approach 30
set turret_approach 33.5
set within_t1 36
set within_t2 23
sensor E switch1 @enabled
print "Fortress attack logic \nBy [brown]Hwes[]"
printflush message1
ubind @fortress
sensor range @unit @range
jump 16 equal E 1
sensor controller @unit @controller
jump 6 notEqual controller @this
ucontrol unbind jx jy 0 0 0
end
sensor flag @unit @flag
jump 6 notEqual flag 0
sensor ux @unit @x
sensor uy @unit @y
ulocate building turret true @copper tx ty found turret
ucontrol within tx ty within t1 within
jump 36 equal within 0
ucontrol target tx ty 1 0 0
end
ucontrol approach tx ty turret_approach 0 0
op sub tx1 tx ux
op sub ty1 ty uy
op len len tx1 ty1
op div len_var range len
op mul tx2 tx1 len_var
op mul ty2 ty1 len_var
op add tx3 tx2 ux
op add ty3 ty2 uy
ucontrol target tx3 ty3 1 0 0
end
ulocate building core true @copper cx cy found core
op sub cx1 cx ux
op sub cy1 cy uy
op len len cx1 cy1
op div len_var range len
op mul cx2 cx1 len_var
op mul cy2 cy1 len_var
op add cx3 cx2 ux
op add cy3 cy2 uy
ucontrol target cx3 cy3 1 0 0
ucontrol autoPathfind cx cy core_approach 0 0
这是一个典型的群控逻辑，是专门用于游戏内堡垒的逻辑，
1.注意到print "Fortress attack logic \nBy [brown]Hwes[]"
printflush message1，这两条逻辑适用于在信息版中打印作者的，但是他们应该被加入初始化里边，现在他在初始化外边，说明这个逻辑的作者生怕有小笨蛋修改信息版的信息，导致信息不对，所以在执行后都重新打印一遍作者信息
2.逻辑连接了一个开关，开关开启逻辑才运行，开关关闭则定制运行，开关关闭后的逻辑为什么它要这么写呢，因为逻辑结束单位控制后，玩家还无法第一时间控制单位，还需要等待指定时间，在等待期间内玩家无法通过rts控制单位，具体等多少时间你可以去源码里查阅，所以为了能让单位快速的能被玩家的rts所控制，逻辑直接在循环过程中检查单位是否被自己的逻辑控制，如果是则直接使用指令停止控制。
3.每个单位的属性都是不一样的，比如说攻击距离生命值，以及炮弹是否能溅射，都需要考虑到，因为控制的单位堡垒啊炮弹具有溅射能力，所以设置了两段的攻击距离，within_t1与within_t2。因为攻击距离问题，单位无法直接攻击攻击范围之外的目标，但是炮弹还是有溅射伤害的，实际的攻击范围还会多一些。于是上边这个逻辑通过三角函数运算实现了这个功能，会向着最远处攻击，也最大化溅射伤害
4.但是这个逻辑它只是用进攻地图，它不适合pvp或出怪的地图。一是他没有单位检测，二是逻辑写的太潦草，有很多地方根本没有考虑到，控制的单位很容易死，所以这是个反面教材


我们直接来上另一个逻辑，这个逻辑也是给堡垒使用的，但也是个垃圾逻辑，
print 通用自动进攻-去开关精简版
set rtr 0
set re 0.9
set dtc 31
set fmtr 0
op add aprchdtc dtc 5
ubind @fortress
sensor range @unit @range
op sub range range 1
sensor hp @unit @health
sensor maxhp @unit @maxHealth
op mul rtrhp maxhp rtr
sensor flag @unit @flag
jump 16 equal flag 1
jump 32 greaterThan hp rtrhp
ucontrol flag 1 0 0 0 0
getlink Nihil 0
jump 24 notEqual Nihil null
ulocate building repair 0 @copper rpx rpy found building
jump 22 equal found 1
ucontrol pathfind @thisx @thisy 4 0 0
jump 27 always x false
ucontrol pathfind rpx rpy 4 0 0
jump 27 always x false
sensor rpx Nihil @x
sensor rpy Nihil @y
ucontrol approach rpx rpy 4 0 0
sensor hp @unit @health
op mul rehp re maxhp
jump 31 lessThan hp rehp
ucontrol flag 0 0 0 0 0
end
uradar player ally any distance 0 1 player
jump 36 notEqual player null
set fmt 0
jump -1 always x false
sensor apx player @x
sensor apy player @y
ucontrol within apx apy fmtr fmt 0
jump 46 notEqual fmt 1
sensor x player @shootX
sensor y player @shootY
sensor shoot player @shooting
jump 69 equal shoot 1
jump -1 always x false
end
uradar enemy ground any distance 0 1 enm
jump 71 notEqual enm null
ucontrol targetp enm 0 0 0 0
ulocate building turret true @copper x y found building
ucontrol within x y aprchdtc wth 0
jump 69 notEqual wth 0
ulocate building storage true @copper x y found building
ucontrol within x y 25 wth 0
jump 69 notEqual wth 0
ulocate building generator true @copper x y found building
ucontrol within x y 25 wth 0
jump 69 notEqual wth 0
ulocate building core true @copper x y found building
ucontrol within x y 25 wth 0
jump 69 notEqual wth 0
jump 66 equal fmt 0
sensor x player @shootX
sensor y player @shootY
ucontrol target x y 0 0 0
end
ulocate building generator true @copper x y found building
ucontrol pathfind x y dtc 0 0
end
ucontrol approach x y dtc 0 0
jump 76 always sw2 0
sensor ex enm @x
sensor ey enm @y
ucontrol approach ex ey range 0 0
ucontrol targetp enm 1 0 0 0
end
ucontrol within x y range wth 0
jump 80 equal wth 0
ucontrol target x y 1 0 0
end
ucontrol within x y aprchdtc wth 0
jump 101 notEqual wth 1
sensor ux @unit @x
sensor uy @unit @y
op sub dx x ux
set sgn dx
op sub dy y uy
op div tan dy dx
op atan theta tan dx
op cos cos theta dx
op sin sin theta dx
op mul dx range cos
op mul dy range sin
jump 97 lessThan sgn 0
op add sx ux dx
op add sy uy dy
jump 99 always x false
op sub sx ux dx
op sub sy uy dy
ucontrol target sx sy 1 0 0
end
ucontrol target sx sy 0 0 0
这个逻辑要稍微好一点点吧，因为堡垒的视野范围是29，那武器的攻击范围是30，因此就多了许多点子。这个逻辑它具备单位残血自动找修复器的功能。如果捡到单位残血他就给单位标记上特殊的flag，并寻找维修器，有特殊flag的标记需要血量到达一定程度后才能取消flag标记并继续战斗。防止单位还没加满血就跑了。下面有一个算法我称之为卡距算法吧，这个单位是利用了单位雷达的特性，单位靠近炮台后，首先炮台在单位的视野范围内，因此单位会首先拉开距离，然后触发超视距攻击，为什么叫超视距攻击呢？因为单位离开炮台了一段距离，所以单位又看不见炮台了，所以叫超视距攻击。攻击完成后，因为单位的视野里面没有炮台了，所以单位会继续向前移动。又会发现炮台，并再次执行超视距攻击。所以这玩意比较恶心。

这个逻辑是一个群控逻辑，而且与其他任何逻辑都不兼容，因为它通过flag判断当前是否需要加血。但是因为很少有人拿这个单位比如说干别的事情，所以他通常用于战斗， 故这个逻辑没有兼容其他的逻辑。

为什么说他写的比较屎呢，
1.大量变量没有进入初始化语句，导致逻辑每次循环都会重新执行一遍赋值，常量非常零散，积木多余，
2.跳转混乱，原逻辑几乎很少使用end语句，跳转讲究层层分离，这个跳转写的是乱七八糟。
3.变量命名不规范，这变量缩写是什么玩意啊？根本看不出他想表达的意思。
4.算法冗余，超视距算法
6.我的变量根本没有用上，代码是死代码。还有jump是断掉的


接下来是重构之后的逻辑：
jump 12 equal initial true
print 通用自动进攻-去开关精简版
set dtc 33
print 在下方选择单位
ubind @fortress
sensor unType @unit @type
jump 4 equal unType 0
sensor range @unit @range
op add aprchdtc range 5
sensor maxhp @unit @maxHealth
op mul rehp maxhp 0.9
set initial true
ubind unType
sensor hp @unit @health
op mul rtrhp maxhp rtr
sensor flag @unit @flag
jump 19 equal flag 1
jump 36 greaterThan hp rtrhp
ucontrol flag 1 0 0 0 0
sensor hp @unit @health
jump 23 lessThan hp rehp
ucontrol flag 0 0 0 0 0
end
getlink repair 0
jump 29 equal repair null
sensor rpx repair @x
sensor rpy repair @y
ucontrol approach rpx rpy 4 0 0
end
ulocate building repair 0 @copper rpx rpy found building
jump 33 equal found 1
ucontrol pathfind @thisx @thisy 4 0 0
end
ucontrol pathfind rpx rpy 4 0 0
end
print 上方修复，下方功能_
uradar player ally ground distance 0 1 player
jump 42 equal player null
sensor x player @shootX
sensor y player @shootY
sensor shoot player @shooting
jump 66 equal shoot 1
uradar enemy ground any distance 0 1 enemy
jump 49 equal enemy null
sensor x enemy @x
sensor y enemy @y
ucontrol approach x y range 0 0
ucontrol targetp enemy 1 0 0 0
end
ulocate building turret true @copper x y found enemy
jump 61 notEqual enemy null
ulocate building storage true @copper x y found enemy
jump 61 notEqual enemy null
ulocate building generator true @copper x y found enemy
jump 61 notEqual enemy null
ulocate building core true @copper x y found enemy
jump 61 notEqual enemy null
ucontrol targetp @this 0 0 0 0
ucontrol autoPathfind @this 0 0 0 0
end
end
sensor enemyRange enemy @range
jump 66 greaterThanEq enemyRange range
ucontrol approach x y range 0 0
ucontrol target x y 1 0 0
end
ucontrol approach x y dtc 0 0
ucontrol within x y range wth 0
jump 71 equal wth 0
ucontrol target x y 1 0 0
end
sensor ux @unit @x
sensor uy @unit @y
op sub cx1 x ux
op sub cy1 y uy
op len len cx1 cy1
op div len_var range len
op mul cx2 cx1 len_var
op mul cy2 cy1 len_var
op add cx3 cx2 ux
op add cy3 cy2 uy
ucontrol target cx3 cy3 1 0 0
代码条数缩减了很多去除了不必要的积木，jump跳转是一层一层的，不是混乱的。相关常量移植到了初始化语句只执行一次。修复或新增功能，当玩家附身陆地单位并开火时，周围单位会自动跟随玩家开火。逻辑中还有一个判断当前单位的血量是否达到相关条件如果达到相关条件后就将flag设为0，我把这个功能提取到了上边，这样减少了jump跳转线的使用数量。
当然了如果你想，如果单位检测到了周围有陆地玩家单位，可以让其他周围的单位都自动跟随他。
jump 12 equal initial true
print 通用自动进攻-去开关精简版
set dtc 33
print 在下方选择单位
ubind @fortress
sensor unType @unit @type
jump 4 equal unType 0
sensor range @unit @range
op add aprchdtc range 5
sensor maxhp @unit @maxHealth
op mul rehp maxhp 0.9
set initial true
ubind unType
sensor hp @unit @health
op mul rtrhp maxhp rtr
sensor flag @unit @flag
jump 19 equal flag 1
jump 36 greaterThan hp rtrhp
ucontrol flag 1 0 0 0 0
sensor hp @unit @health
jump 23 lessThan hp rehp
ucontrol flag 0 0 0 0 0
end
getlink repair 0
jump 29 equal repair null
sensor rpx repair @x
sensor rpy repair @y
ucontrol approach rpx rpy 4 0 0
end
ulocate building repair 0 @copper rpx rpy found building
jump 33 equal found 1
ucontrol pathfind @thisx @thisy 4 0 0
end
ucontrol pathfind rpx rpy 4 0 0
end
print 上方修复，下方功能_
uradar player ally ground distance 0 1 player
jump 47 equal player null
sensor x player @shootX
sensor y player @shootY
sensor shoot player @shooting
jump 71 equal shoot 1
sensor x player @x
sensor y player @y
ucontrol approach x y 2 0 0
ucontrol targetp @this 0 2 0 0
end
uradar enemy ground any distance 0 1 enemy
jump 54 equal enemy null
sensor x enemy @x
sensor y enemy @y
ucontrol approach x y range 0 0
ucontrol targetp enemy 1 0 0 0
end
ulocate building turret true @copper x y found enemy
jump 66 notEqual enemy null
ulocate building storage true @copper x y found enemy
jump 66 notEqual enemy null
ulocate building generator true @copper x y found enemy
jump 66 notEqual enemy null
ulocate building core true @copper x y found enemy
jump 66 notEqual enemy null
ucontrol targetp @this 0 0 0 0
ucontrol autoPathfind @this 0 0 0 0
end
end
sensor enemyRange enemy @range
jump 71 greaterThanEq enemyRange range
ucontrol approach x y range 0 0
ucontrol target x y 1 0 0
end
ucontrol approach x y dtc 0 0
ucontrol within x y range wth 0
jump 76 equal wth 0
ucontrol target x y 1 0 0
end
sensor ux @unit @x
sensor uy @unit @y
op sub cx1 x ux
op sub cy1 y uy
op len len cx1 cy1
op div len_var range len
op mul cx2 cx1 len_var
op mul cy2 cy1 len_var
op add cx3 cx2 ux
op add cy3 cy2 uy
ucontrol target cx3 cy3 1 0 0
注意，如果让逻辑控制单位开火，且逻辑不关闭开火的话，单位会一直处于开火状态，所以我添加了一个停火指令。


ubind @mono
sensor fg @unit @flag
jump 0 notEqual fg 0
ucontrol boost 1 0 0 0 0
op sub 探测间隔 @time time
jump 22 lessThan 探测间隔 5000
set cgg null
set sll null
op add a a 1
op mod a a @links
getlink xz1 a
sensor cg xz1 @config
jump 19 equal cg null
ulocate building core 0 @copper x y found h
sensor sl h cg
jump 17 equal cgg null
jump 19 greaterThan sl sll
set cgg cg
set sll sl
jump 8 notEqual a 0
sensor iy h @itemCapacity
set time @time
ulocate ore core true cgg x y found building
sensor fm @unit @firstItem
jump 36 equal fm null
jump 28 notEqual fm cgg
sensor mx @unit @mineX
jump 37 equal mx x
ucontrol mine -1 -1 0 0 0
sensor max? h fm
jump 32 notEqual max? iy
ucontrol itemDrop @air 999 0 0 0
ulocate building core 0 @copper x y found h
ucontrol itemDrop h 999 0 0 0
ucontrol approach x y 3 0 0
end
ucontrol mine x y 0 0 0
ucontrol approach x y 3 0 0
这是一个远古时期的垃圾挖矿逻辑，但是这个逻辑有的地方设置的也是非常精妙的，比如说定期检测，哪个矿物比较少，这个定期就定得非常精妙，他通过计算时间间距，从而极大的减少算力消耗，对于逻辑来说，运算速度是一个无数逻辑人都追求的目标呢，功能多，控制速度还快，多是一件美事呢。逻辑通过连接分类器，定期检测分类器的物品在和核心中的数量。如果分类器选中的物品中有比较少的，则自动挖取该物品。
但是他还是有缺点的，
1.变量命名不规范，含义不明确
2.下方控制挖矿的逻辑比较捡漏，且优化空间很大，而且还可能出现未知bug


ubind @quasar
ucontrol boost 1 y 5 0 0
sensor config sorter1 @config
sensor unitF @unit @firstItem
sensor unitT @unit @totalItems
sensor unitC @unit @itemCapacity
ulocate building core false @copper coreX coreY 0 core
ulocate ore core true config itemX itemY 0 building
jump 41 strictEqual unitF config
jump 41 equal unitF 0
sensor coreitemNmr core config
sensor coreC core @itemCapacity
jump 36 lessThanEq coreC coreitemNmr
sensor coreid coreid @id
jump 17 lessThan coreid 100
jump 36 strictEqual config @sand
jump 36 strictEqual config @coal
ucontrol within coreX coreY 7 result 0
jump 22 equal result false
ucontrol mine -1145 -14 0 0 0
ucontrol itemDrop core 114.514 0 0 0
end
op mul unitC03 unitC 0.3
jump 36 greaterThanEq unitC03 unitT
ucontrol within coreX coreY 27 result 0
jump 34 equal result false
ulocate ore core true unitF itemX itemY found building
op sub minusX itemX coreX
op sub minusY itemY coreY
op len within minusX minusY
jump 41 lessThanEq within 35
sensor unitX @unit @x
sensor unitY @unit @y
ucontrol mine unitX unitY 0 0 0
ucontrol move coreX coreY 0 0 0
end
ucontrol mine -1145 -14 0 0 0
ucontrol itemDrop @air 114.514 0 0 0
end
print △非选择矿物处理
print ▽正常挖矿一处理
sensor coreid core @type
sensor coreid coreid @id
jump 46 lessThan coreid 100
jump 91 strictEqual config @sand
jump 91 strictEqual config @coal
jump 105 greaterThanEq unitT unitC
op sub minusX coreX itemX
op sub minusY coreY itemY
op len within minusX minusY
jump 88 greaterThan within 35
ucontrol within coreX coreY 21 result 0
jump 88 equal result true
op mul 0.75unitC unitC 0.90
jump 68 lessThan unitT 0.75unitC
ucontrol within coreX coreY 27 result 0
jump 68 equal result false
op angle arc minusX minusY
op cos x arc minusy
op mul x x 7.5
op sin y arc minusy
op mul y y 7.5
op add x x itemX
op add y y itemY
ucontrol mine itemX itemY 0 0 0
ucontrol move x y 5 0 0
end
print ▽大风车
sensor unitX @unit @x
sensor unitY @unit @y
op sub minusX unitX itemX
op sub minusY unitY itemY
op len within minusX minusY
op sub within within 1.5
op abs within within 3
op angle arc minusX minusY
op mul withinArc within 13
op add arc arc withinArc
op mod arc arc 360
op cos x arc b
op mul x x within
op sin y arc b
op mul y y within
op add x x itemX
op add y y itemY
ucontrol mine itemX itemY 0 0 0
ucontrol move x y 7 0 0
end
ucontrol move itemX itemY 7 0 0
end
print ▽煤炭沙子处理
op add unitT unitT 5
jump 96 greaterThanEq unitT unitC
ucontrol move itemX itemY 7 0 0
ucontrol mine itemX itemY 7 0 0
end
ucontrol mine -1145 -14 7 0 0
ulocate building storage 0 @copper vaultX vaultY 0 vault
sensor vaultC vault @itemCapacity
jump 101 lessThanEq vaultC 1000
ucontrol itemDrop vault 999 0 0 0
ucontrol move coreX coreY 0 0 0
end
end
print ▽同种矿提交///////
sensor mining @unit @mining
jump 109 equal mining false
end
print ▽e核提交矿物
ulocate building storage 0 @copper vaultX vaultY 0 vault
ucontrol within vaultX vaultY 7 result 0
jump 117 equal result false
sensor vaultC vault @itemCapacity
jump 117 lessThanEq vaultC 1000
ucontrol itemDrop vault 999 0 0 0
end
print ▽复合判断__核心判断
ucontrol within coreX coreY 27 result 0
jump 139 equal result false
sensor coreid core @type
sensor coreid coreid @id
jump 124 lessThan coreid 100
jump 139 strictEqual config @sand
jump 139 strictEqual config @coal
ucontrol within coreX coreY 7 result 0
jump 129 equal result false
ucontrol itemDrop core 999 0 0 0
end
print ▽长距离交矿尝试
ulocate ore core true config itemX itemY 0 building
ucontrol within itemX itemY 9 result 0
jump 135 equal result false
ucontrol itemDrop @air 1 0 0 0
ucontrol mine itemX itemY 0 0 0
end
sensor unitX @unit @x
sensor unitY @unit @y
ucontrol mine unitX unitY type 0 flor
end
ucontrol move coreX coreY type 0 flor
end
end
print 低控速-高挖效/V1.0
这是一个142高级的挖矿逻辑，这个逻辑的控制流是非常先进了，

# 矿物采集与提交流程
## Ⅰ. 背包矿物检测（目标矿物且非空）
1. 检测是没有爆仓
   - **是** → 容器相关检测：
     - 在容器旁边 **且** 容器贴近核心？
       - **是** → 将矿物提交至容器
       - **否** → 检测矿物是否可提交
         - **可提交** → 单位是否靠近核心？
           - **是** → 将矿物提交至核心
           - **否** → 矿物数量 > 背包容量 20%？
             - **是** → 单位是否在核心27格内？
               - **是** → 目标矿物在7格范围内？
                 - **是** → 启动背包未满挖矿程序
                 - **否** → 挖掘脚下沙子
             - **否** → 移动单位靠近核心
             - **否** → 丢弃矿物（直接扔）
         - **不可提交** → 丢弃矿物（直接扔）
   - **否** → 丢弃矿物（直接扔）

## Ⅱ. 背包容量未满
1. 搜索目标矿物
2. 挖取目标矿物
3. 目标矿物在核心34格内 **且** 可提交 **且** 单位不在20格范围？
   - **是** → 检测：
     - 背包矿物 > 80% **且** 单位在核心27格内？
       - **是** → 调整采集姿态
       - **否** → 执行优化挖矿路径（原"大风车"）
   - **否** → 常规靠近矿物

## Ⅲ. 背包已满
1. 单位未进行开采：
   - 在容器旁边 **且** 容器贴近核心？
     - **是** → 提交矿物至容器
     - **否** → 在核心27格内 **且** 矿物可提交？
       - **是** → 7格内有目标矿物？
         - **是** → 丢弃1个单位矿物
         - **否** → 
           1. 挖掘脚下沙子
           2. 提交矿物至核心
       - **否** → 进入待机状态
       
据我发现，普通的挖矿逻辑需要靠近核心比较近的距离才能提交矿物。
而玩家却可以在非常远的地方，直接将背包的物品放入核心，我又通过观察发现，如果单位靠近核心指定距离，且单位的背包上有物品。如果在这时候挖不同的矿物，背包的物品会自动进入核心内。从而实现超远距离交矿，你可以从java源码考证
至于这个大风车是什么呢，如果矿物离核心比较近，为了能让单位快速将矿物提交至核心，所以我开发出了路径优化，如果单位的背包快要满时，则自动向核心靠拢，在靠拢期间并不会终止挖矿，这样单位就能成功提交矿物
这个挖矿逻辑还有一个比较高级的地方，就是e核优化，这个游戏里边有两个星球，另一个星球就是e星，e星的核心无法提交沙子和煤炭，如果将沙子与煤炭矿物直接丢进异星核心里面，矿物会被直接销毁。为了解决这个问题，就有了一系列相关控制流程。
但是随着游戏的更新，RTS可以直接控制单位进行挖矿，又因这个逻辑的执行效率又太低了，所以这个逻辑也没有走上舞台。


sensor dead chushi @dead
jump 6 strictEqual dead 0
set 数 0
ubind @fortress
set chushi @unit
end
op add 数 数 1
ubind @fortress
jump 0 notEqual @unit chushi
set 当前单位数量 数
set 数 0
这是一个单位数量检测逻辑，利用绑定的特性通过循环判断当前单位数量，为了防止起始单位在中途死亡又加了死亡判断

set unitN 0
ubind @flare
set firstUnit @unit
sensor dead firstUnit @dead
jump 0 equal dead 1
op add unitN unitN 1
ubind @flare
jump 3 notEqual @unit firstUnit
print ""
print unitN
printflush message1
这两个是一个逻辑，加了信息版打印与图标打印功能

借助lookup指令，我们就得到了一个可以打印在场全部单位数量的逻辑，当然了只能检查友方单位。
lookup unit unitType idUnit
op add idUnit idUnit 1
jump 5 lessThan idUnit @unitCount
set idUnit 0
printflush message1
set unitN 0
ubind unitType
set firstUnit @unit
sensor dead firstUnit @dead
jump 5 equal dead 1
op add unitN unitN 1
ubind unitType
jump 8 notEqual @unit firstUnit
printchar unitType
print unitN


##接下来就开始介绍多控逻辑，多控逻辑与单控逻辑的绑定方法一样，绑定优先级相同
首先是登场的是我们老祖宗最喜欢用的flag，它的优点是可以通过直接修改数值的方式绑定大量的单位，从而对他们进行控制
jump 13 lessThan @second second
set unitCN 2
ubind @poly
set firstUnit @unit
set unitN 0
sensor dead firstUnit @dead
jump 2 equal dead 1
sensor flag @unit @flag
jump 10 notEqual flag 114514
op add unitN unitN 1
ubind @poly
jump 5 notEqual @unit firstUnit
op add second @second 5
ubind @poly
sensor flag @unit @flag
jump 20 notEqual flag 0
jump 19 greaterThanEq unitN unitCN
op add unitN unitN 1
ucontrol flag 114514 0 0 0 0
end
jump 24 notEqual flag 114514
jump 25 lessThanEq unitN unitCN
op sub unitN unitN 1
ucontrol flag 0 0 0 0 0
end
ucontrol move @thisx @thisy 0 0 0
这个逻辑也使用了定期检查功，能定期检查场上拥有指定标记的单位，
这个逻辑的缺点也很明显，
1.flag没有按规则生成生成方式应该为，floor(@thisx)*1000+floor(@thisx)，把这个逻辑使用了固定flag，容易发生冲突，不推荐这种做法
2。逻辑分别在三库使用了绑定指令，如果需要更改单位则需要同步修改另外两处，不落下一处都不行，应该将选择单位功能提到逻辑最开头，并加入初始化语句
3.这是使用flag绑定单位的通病，控制速度低下，这种绑定方法逐渐被淘汰，当然这里展示的还是优化程度比较高的逻辑了


jump 9 equal initial true
op floor _0 @thisx 0
op mul _1 _0 1000
op floor _2 @thisy 0
op add unFlag _1 _2
print "▽设置需要绑定的单位"
ubind @poly
sensor unType @unit @type
jump 6 equal unType 0
set initial true
op add ts ts 1
op mod ts ts 6
op mul counter ts 2
op add @counter @counter counter
ubind un1
jump 25 always un false
ubind un2
jump 25 always un false
ubind un3
jump 25 always un false
ubind un4
jump 25 always un false
ubind un5
jump 25 always un false
ubind un6
sensor unDead @unit @dead
jump 31 equal unDead 1
sensor flag @unit @flag
jump 31 notEqual unFlag flag
ucontrol move @thisx @thisy 0 0 0
end
ubind unType
sensor controlled @unit @controlled
jump 30 greaterThan controlled 1
jump 37 equal controlled 0
sensor flag @unit @flag
jump 30 notEqual flag 0
ucontrol flag unFlag 0 0 0 0
op add @counter @counter counter
set un1 @unit
end
set un2 @unit
end
set un3 @unit
end
set un4 @unit
end
set un5 @unit
end
set un6 @unit
end
end
这种绑定方式目前是比较流行的，通过@counter指令实现伪列表功能，@counter实现跳转功能，这种逻辑优点是：绑定速度快维护成本低，除了有点废人以外没有别的缺点，可以判断这个逻辑绑定方法和单控逻辑一样，这样写会不会感觉有点长呢，我们可以优化一下。
jump 10 equal initial true
op floor _0 @thisx 0
op mul _1 _0 1000
op floor _2 @thisy 0
op add unFlag _1 _2
print "▽设置需要绑定的单位"
ubind @poly
sensor unType @unit @type
jump 6 equal unType 0
set addUnit true
set initial true
op mod ts ts 6
op mul counter ts 3
op add counter addUnit counter
op add @counter @counter counter
set un1 @unit
ubind un1
jump 32 always un false
set un2 @unit
ubind un2
jump 32 always un false
set un3 @unit
ubind un3
jump 32 always un false
set un4 @unit
ubind un4
jump 32 always un false
set un5 @unit
ubind un5
jump 32 always un false
set un6 @unit
ubind un6
sensor unDead @unit @dead
jump 40 equal unDead 1
sensor flag @unit @flag
jump 40 notEqual unFlag flag
ucontrol move @thisx @thisy 0 0 0
set addUnit true
op add ts ts 1
end
ubind unType
sensor controlled @unit @controlled
jump 38 greaterThan controlled 1
jump 46 equal controlled 0
sensor flag @unit @flag
jump 38 notEqual flag 0
ucontrol flag unFlag 0 0 0 0
set addUnit false
这样写的效果是一样的，逻辑长度还更短通过addUnit判断是否要修改单位，不知道你有没有注意到单控逻辑绑定单位是，如果单位不符合目标，会直接循环，绑定并验证。多控逻辑的不一样，如果绑定的单位不符合预期则会继续执行对其他单位的控制，这是为了防止在寻找单位的时候，不控制其他单位导致的问题。


那么再不给单位flag的情况下，在同一帧或者短时间内放置多个相同逻辑，普通的单控逻辑必然会触发重新选择单位流程。如何避免这种情况呢？下面这个逻辑会给出答案。

jump 25 always SF/// SF///
stop
print ────────────────────────────────────
print 完美小逻辑多控v0.5
print By:SF///
print 本程序可以保证不与使用相同方式获取新单位的逻辑抢单位！
print 单位损失了会自动重新抓！
print 并且尽可能优化了（也许不是最优的）！
print 如果有bug或更好的思路,请通过发送邮件到
print saltedfishiii@yeah.net
print 或qq聊天群组等方式联系作者并反馈！
print /───────使用说明────────
print 本程序是一个轮子，实际的控制单位代码需要你自己写
print uCount控制单位数量，最多13个。需要注意让uCount数值等于需求
print 的单位数量，否则会影响后续控制单位，
print 的单位数量，否则会影响后续控制单位，
print 你问你的代码要写哪里？看看下面这条jump跳转到哪里吧!
jump 128 always SF/// false
print /───────更新日志────────
print /────v0.4─────
print 修复：搜索单位失败后LIST不清空导致同一单位多次重抓的错误
print /────v0.5─────
print 修复：重抓单位时偶尔抢单位的BUG，如果这个问题再出现，请立即反馈！！
print ───────────────────────────────────
stop
set uCount 0
jump 25 lessThanEq uCount SF///
jump 25 greaterThan uCount 13
op shl jMax uCount 1
ubind @flare
sensor uType @unit @type
set I uCount
set LIST 0
op shl LIST LIST 4
op xor LIST LIST I
op sub I I 1
jump 33 greaterThan I 0
ubind uType
sensor uCtrl @unit @controlled
jump 37 greaterThan uCtrl 0
ucontrol within 0 0 0 0 0
op add tCheck @time 6500
jump 48 always SF/// false
jump 92 equal LIST false
ubind uType
jump 91 greaterThan @time tCheck
sensor uCtrl @unit @controlled
jump 44 notEqual uCtrl false
ucontrol within 0 0 0 0 0
set t @time
jump 50 equal @time t
set t @time
jump 52 equal @time t
sensor uCter @unit @controller
jump 44 notEqual uCter @this
op and j LIST 0xF
op shr LIST LIST 4
op shl j j 1
op add @counter @counter j
jump -1 always SF/// false
jump -1 always SF/// false
set u0 @unit
jump 43 always SF/// false
set u1 @unit
jump 43 always SF/// false
set u2 @unit
jump 43 always SF/// false
set u3 @unit
jump 43 always SF/// false
set u4 @unit
jump 43 always SF/// false
set u5 @unit
jump 43 always SF/// false
set u6 @unit
jump 43 always SF/// false
set u7 @unit
jump 43 always SF/// false
set u8 @unit
jump 43 always SF/// false
set u9 @unit
jump 43 always SF/// false
set u10 @unit
jump 43 always SF/// false
set u11 @unit
jump 43 always SF/// false
set u12 @unit
jump 43 always SF/// false
jump -1 always SF/// false
print TODO_更好的重新寻找单位的逻辑
set rbFail 1
set rbFail 0
set LIST 0
set j 0
op add @counter @counter j
ubind u0
jump 119 always SF/// false
ubind u1
jump 119 always SF/// false
ubind u2
jump 119 always SF/// false
ubind u3
jump 119 always SF/// false
ubind u4
jump 119 always SF/// false
ubind u5
jump 119 always SF/// false
ubind u6
jump 119 always SF/// false
ubind u7
jump 119 always SF/// false
ubind u8
jump 119 always SF/// false
ubind u9
jump 119 always SF/// false
ubind u10
jump 119 always SF/// false
ubind u11
jump 119 always SF/// false
ubind u12
jump 128 equal check false
sensor dead @unit @dead
jump 128 equal dead false
op shr I j 1
op add I I 1
op shl LIST LIST 4
op xor LIST LIST I
jump 131 always SF/// false
print 你的代码应该写在下面这行到__j=j+2__那一行之间
op add x @thisx j
ucontrol move x @thisy 0 0 0
ucontrol target @thisx 1000 1 0 0
op add j j 2
jump 93 lessThan j jMax
set check 0
jump 92 lessThan @time tCheck
op add tCheck @time 6500
jump 44 notEqual LIST false
set check 1
jump 92 always SF/// false
jump -1 always SF/// false
作者用16进制思维来压缩存储，实现了代码片段压缩，利用定时检查方式，减少算力消耗
这次我们重点研究它的绑定规则在前面，控制指令它是有帧延迟的，第一帧执行的指令，要到第二帧才能生效。如果在没有生效的时候就直接检查，会出现检查问题等情况。逻辑里有@time，每帧只刷新一次，所以利用这个特性，可以检测当前这一帧有没有过完，如果过完了之后才去执行下面一系列指令，如果没有过完，则继续等待。
至于为什么使用两遍检查，我猜测是为了防止在短时间内建造多个相同的逻辑时，出现两个相同逻辑运行代码进度不一样，导致单位绑定出现失误，亦或者增加逻辑的安全性。
不过这种逻辑的使用条件极其少见，一个多控逻辑，甚至比群控逻辑的优先级还要低，但是这个逻辑也为我们提供了很高的研究价值。



#接下来登场的是利用lookup构造字符串，实现多控的方法。
jump 10 equal initial true
op floor thisFlag @thisx b
op mul thisFlag thisFlag 1000
op add thisFlag thisFlag @thisy
op floor thisFlag thisFlag @thisy
print "▽设置需要绑定的单位"
ubind @horizon
sensor unType @unit @type
jump 6 equal unType 0
set initial true
op add itemid itemid 1
op mod itemid itemid 5
lookup item item itemid
sensor itemName item @name
read unit @this itemName
sensor dead unit @dead
jump 22 equal dead 1
sensor flag unit @flag
jump 22 notEqual thisFlag flag
ubind unit
ucontrol move @thisx @thisy 0 0 0
end
ubind unType
sensor controlled @unit @controlled
jump 30 greaterThan controlled 1
jump 28 equal controlled 0
sensor flag @unit @flag
jump 30 notEqual flag 0
ucontrol flag thisFlag 0 0 0 0
write @unit @this itemName
end
draw triangle copper lead metaglass graphite sand 0
lookup指令可以苹果id读取游戏内的各种元素，我们可以先获取元素，然后再将元素转化为名称，rande读取元素名称里的单位，write 将单位写入元素变量中。，实现单位的多控。最下边的draw值0永远运行不到他是用来装变量的，也就是我们所说的元素变量。
它的好处是想控多少单位就空多少单位，
为什么要用来装变量呢，因为它拥有全游戏中最多变量槽，所以用draw，但是我推荐使用ucontrol_within，draw是绘制质量，绘制指令可以在显示屏上绘制内容，为了不让服务器的玩家们用处理器绘制涩涩图片，所以有的服务器会对使用了多个绘制指令的逻辑进行封禁。



接下来我们学习多核优化控制，单个逻辑的运算能力终究是有限的，所以玩家们会通过放置更多处理核心来增强逻辑对单位的控制能力，但是普通的逻辑堆叠核心之后它会重复绑定单位，导致有的时候叠了核弹和没叠一样，比如说在同一帧内放置多个相同的逻辑，这就导致了他们每次执行绑定指令时绑定的都是一个单位，所以叠了和没叠一样。所以有了多核优化
多核优化逻辑一般分为一个分配核和多个控制核，
--------------------------------------------------------------
分配核心：
ubind @flare
sensor dead firstUnit @dead
jump 5 equal dead 0
set firstUnit @unit
jump 13 always x false
jump 14 notEqual @unit firstUnit
op add endI unitI @links
op mod processorI unitI @links
getlink processor processorI
op idiv blockTI unitI @links
write blockTI processor "unitIEnd"
op add unitI unitI 1
jump 7 lessThan unitI endI
set unitI 0
op mod processorI unitI @links
getlink processor processorI
op idiv blockTI unitI @links
lookup block blockT blockTI
sensor blockTN blockT @name
write @unit processor blockTN
op add unitI unitI 1

控制核心：
set unitI 0
jump 1 lessThanEq unitIEnd 0
lookup block unitRT unitI
sensor unitRTN unitRT @name
read unit @this unitRTN
sensor dead unit @dead
jump 11 equal dead 1
ubind unit
op mul xx unitI 3
op add x @thisx xx
ucontrol move x @thisy 0 0 0
op add unitI unitI 1
jump 2 lessThan unitI unitIEnd
end
draw triangle graphite-press multi-press silicon-smelter silicon-crucible kiln plastanium-compressor
draw triangle phase-weaver cryofluid-mixer pyratite-mixer blast-mixer melter separator
draw triangle disassembler spore-press pulverizer coal-centrifuge incinerator copper-wall
draw triangle copper-wall-large titanium-wall titanium-wall-large plastanium-wall plastanium-wall-large thorium-wall
draw triangle thorium-wall-large phase-wall phase-wall-large surge-wall surge-wall-large door
draw triangle door-large scrap-wall scrap-wall-large scrap-wall-huge scrap-wall-gigantic mender
draw triangle mend-projector overdrive-projector overdrive-dome force-projector shock-mine conveyor
draw triangle titanium-conveyor plastanium-conveyor armored-conveyor junction bridge-conveyor phase-conveyor
draw triangle sorter inverted-sorter router distributor overflow-gate underflow-gate
draw triangle mass-driver duct duct-router duct-bridge mechanical-pump rotary-pump
draw triangle conduit pulse-conduit plated-conduit liquid-router liquid-tank liquid-junction
draw triangle bridge-conduit phase-conduit power-node power-node-large surge-tower diode
draw triangle battery battery-large combustion-generator thermal-generator steam-generator differential-generator
draw triangle rtg-generator solar-panel solar-panel-large thorium-reactor impact-reactor mechanical-drill
draw triangle pneumatic-drill laser-drill blast-drill water-extractor cultivator oil-extractor
draw triangle core-shard core-foundation core-nucleus vault container unloader
draw triangle duo scatter scorch hail wave lancer
draw triangle arc parallax swarmer salvo segment tsunami
draw triangle fuse ripple cyclone foreshadow spectre meltdown
draw triangle command-center ground-factory air-factory naval-factory additive-reconstructor multiplicative-reconstructor
draw triangle exponential-reconstructor tetrative-reconstructor repair-point repair-turret payload-conveyor payload-router
draw triangle power-source power-void item-source item-void liquid-source liquid-void
draw triangle payload-void payload-source illuminator launch-pad interplanetary-accelerator message
draw triangle switch micro-processor logic-processor hyper-processor memory-cell memory-bank
draw triangle logic-display large-logic-display liquid-container deconstructor constructor thruster
draw triangle large-constructor payload-loader payload-unloader silicon-arc-furnace cliff-crusher plasma-bore
draw triangle reinforced-liquid-junction breach core-bastion turbine-condenser beam-node beam-tower
draw triangle build-tower impact-drill carbide-crucible surge-conveyor duct-unloader surge-router
draw triangle reinforced-conduit reinforced-liquid-router reinforced-liquid-container reinforced-liquid-tank reinforced-bridge-conduit core-citadel
draw triangle core-acropolis heat-reactor impulse-pump reinforced-pump electrolyzer oxidation-chamber
draw triangle surge-smelter surge-crucible overflow-duct large-plasma-bore cyanogen-synthesizer slag-centrifuge
draw triangle electric-heater slag-incinerator phase-synthesizer sublimate reinforced-container reinforced-vault
draw triangle atmospheric-concentrator unit-cargo-loader unit-cargo-unload-point chemical-combustion-chamber pyrolysis-generator regen-projector
draw triangle titan small-deconstructor vent-condenser phase-heater heat-redirector tungsten-wall
draw triangle tungsten-wall-large tank-assembler beryllium-wall beryllium-wall-large eruption-drill ship-assembler
draw triangle mech-assembler shield-projector beam-link world-processor reinforced-payload-conveyor reinforced-payload-router
draw triangle disperse large-shield-projector payload-mass-driver world-cell carbide-wall carbide-wall-large
draw triangle tank-fabricator mech-fabricator ship-fabricator reinforced-surge-wall radar blast-door
draw triangle canvas armored-duct unit-repair-tower diffuse prime-refabricator basic-assembler-module
draw triangle reinforced-surge-wall-large tank-refabricator mech-refabricator ship-refabricator slag-heater afflict
draw triangle shielded-wall lustre scathe smite underflow-duct malign
draw triangle shockwave-tower heat-source flux-reactor neoplasia-reactor heat-router large-payload-mass-driver
draw triangle reinforced-message world-message world-switch small-heat-redirector large-cliff-crusher advanced-launch-pad
draw triangle landing-pad 0 0 0 0 unitIEnd

分配盒通过获取已连接的控制核，获取控制核的数量，来均匀分配每个控制核控制的单位，并把他们需要控制的单位写入到对应的控制核心里。
--------------------------------------------------------------
我们再看一组逻辑：
--------------------------------------------------------------
这个逻辑的名字叫做自定义单位点阵，它可以控制单位摆出相应的阵型，可以对阵型进行旋转等操作，配备了多核优化。
主要涉及的代码有4个，分配核，主控核，热操作核，与点阵生成核心。其中点阵生成核心专门用于生成相应的点阵，不与前三个核心为一个整体。
分配核心
jump 18 equal initial true
print "▽阵列代码(通过外部逻辑修改可支持热操作)"
set array "$*%*&*'*(*)***+*,*(.(-(,(+()'(''&&&%%$$###)()'*&*%+$,#-#1.1-0,0+/*.)0*0)0(0'0&0%0$0#2,3,4,5,6,1)2)3)5)6)7)8)4.4-4+4*8-8,7+6*4)4(3'3&2&1%3%3$4#5#6#7#8#8$7'6&5&4%"
print "▽旋转角度(通过外部逻辑修改可支持热操作)"
set angle 0
print "▽阵列间距(通过外部逻辑修改可支持热操作)"
set spacing 1.8
print "▽XY偏移值,(角度修改时偏移刷新,热操作不灵敏)"
set offsetX 12
set offsetY 3
ubind @horizon
sensor unitType @unit @type
jump 10 equal unitType 0
op floor thisFlag @thisx b
op mul thisFlag thisFlag 1000
op add thisFlag thisFlag @thisy
op floor thisFlag thisFlag @thisy
set initial true
jump 26 strictEqual array array1
set array1 array
set unitBindNub -1
op add unitBindNub unitBindNub 1
op mul idReadNull unitBindNub 2
read notNull array idReadNull
jump 21 notEqual notNull null
set angle1 1145141919810
jump 53 strictEqual angle1 angle
jump 53 equal bank1 0
set angle1 angle
op mod angle angle 360
sensor arraySize array @size
op sub arraySize arraySize 1
op angle offsetX1 offsetX 35
op add offsetY1 offsetY 35
op add offsetX1 offsetX 35
set forReadxy -2
op add forReadxy forReadxy 2
read reaeX array forReadxy
op sub reaeX reaeX offsetX1
op add forReadxy1 forReadxy 1
read reaeY array forReadxy1
op sub reaeY reaeY offsetY1
op angle originalAngle reaeX reaeY
op add newAngle originalAngle angle
op len lenReaeXY reaeX reaeY
op cos cos newAngle 2
op sin sin newAngle 2
op mul lenReaeXY lenReaeXY spacing
op mul newY sin lenReaeXY
op mul newX cos lenReaeXY
write newX bank1 forReadxy
write newY bank1 forReadxy1
jump 36 greaterThan arraySize forReadxy1
jump 86 greaterThan second @second
op add second @second 5
set prAvailableNub 0
set idBlock 0
set unitNub 101
getlink pr idBlock
op add idBlock idBlock 1
set thisMarking 0
read thisMarking pr "thisMarking"
jump 67 notEqual thisMarking "CustomDotMatrix-byNOSBHG2g"
write @this pr "centralPr"
write arc1 pr "arc"
write bank1 pr "bank"
op add prAvailableNub prAvailableNub 1
jump 58 lessThan idBlock @links
set idBlock 0
set prNub 0
set origin 0
set endPoint1 0
getlink pr idBlock
op add idBlock idBlock 1
set thisMarking 0
read thisMarking pr "thisMarking"
jump 85 notEqual thisMarking "CustomDotMatrix-byNOSBHG2g"
op add prNub prNub 1
op sub unitNub1 unitBindNub prNub
op idiv endPoint unitNub1 prAvailableNub
op add endPoint endPoint 1
op add endPoint1 endPoint1 endPoint
write endPoint1 pr "endPoint"
write origin pr "origin"
set origin endPoint1
jump 72 lessThan idBlock @links
op add itemid itemid 1
op mod itemid itemid unitBindNub
lookup block item itemid
sensor itemName item @name
read unit @this itemName
sensor dead unit @dead
jump 96 equal dead 1
sensor flag unit @flag
jump 96 notEqual flag thisFlag
end
ubind unitType
sensor controlled @unit @controlled
jump 102 equal controlled 0
sensor flag @unit @flag
jump 102 equal flag 0
end
ucontrol flag thisFlag 0 0 0 0
write @unit @this itemName
end
packcolor graphite-press multi-press silicon-smelter silicon-crucible kiln
packcolor plastanium-compressor phase-weaver cryofluid-mixer pyratite-mixer blast-mixer
packcolor melter separator disassembler spore-press pulverizer
packcolor coal-centrifuge incinerator copper-wall copper-wall-large titanium-wall
packcolor titanium-wall-large plastanium-wall plastanium-wall-large thorium-wall thorium-wall-large
packcolor phase-wall phase-wall-large surge-wall surge-wall-large door
packcolor door-large scrap-wall scrap-wall-large scrap-wall-huge scrap-wall-gigantic
packcolor mender mend-projector overdrive-projector overdrive-dome force-projector
packcolor shock-mine conveyor titanium-conveyor plastanium-conveyor armored-conveyor
packcolor junction bridge-conveyor phase-conveyor sorter inverted-sorter
packcolor router distributor overflow-gate underflow-gate mass-driver
packcolor duct duct-router duct-bridge mechanical-pump rotary-pump
packcolor conduit pulse-conduit plated-conduit liquid-router liquid-tank
packcolor liquid-junction bridge-conduit phase-conduit power-node power-node-large
packcolor surge-tower diode battery battery-large combustion-generator
packcolor thermal-generator steam-generator differential-generator rtg-generator solar-panel
packcolor solar-panel-large thorium-reactor impact-reactor mechanical-drill pneumatic-drill
packcolor laser-drill blast-drill water-extractor cultivator oil-extractor
packcolor core-shard core-foundation core-nucleus vault container
packcolor unloader duo scatter scorch hail
packcolor wave lancer arc parallax swarmer
packcolor salvo segment tsunami fuse ripple
packcolor cyclone foreshadow spectre meltdown command-center
packcolor ground-factory air-factory naval-factory additive-reconstructor multiplicative-reconstructor
packcolor exponential-reconstructor tetrative-reconstructor repair-point repair-turret payload-conveyor
packcolor payload-router power-source power-void item-source item-void
packcolor liquid-source liquid-void payload-void payload-source illuminator
packcolor launch-pad interplanetary-accelerator message switch micro-processor
packcolor logic-processor hyper-processor memory-cell memory-bank logic-display
packcolor large-logic-display liquid-container deconstructor constructor thruster
packcolor large-constructor payload-loader payload-unloader silicon-arc-furnace cliff-crusher
packcolor plasma-bore reinforced-liquid-junction breach core-bastion turbine-condenser
packcolor beam-node beam-tower build-tower impact-drill carbide-crucible
packcolor surge-conveyor duct-unloader surge-router reinforced-conduit reinforced-liquid-router
packcolor reinforced-liquid-container reinforced-liquid-tank reinforced-bridge-conduit core-citadel core-acropolis
packcolor heat-reactor impulse-pump reinforced-pump electrolyzer oxidation-chamber
packcolor surge-smelter surge-crucible overflow-duct large-plasma-bore cyanogen-synthesizer
packcolor slag-centrifuge electric-heater slag-incinerator phase-synthesizer sublimate
packcolor reinforced-container reinforced-vault atmospheric-concentrator unit-cargo-loader unit-cargo-unload-point
packcolor chemical-combustion-chamber pyrolysis-generator regen-projector titan small-deconstructor
packcolor vent-condenser phase-heater heat-redirector tungsten-wall tungsten-wall-large
packcolor tank-assembler beryllium-wall beryllium-wall-large eruption-drill ship-assembler
packcolor mech-assembler shield-projector beam-link world-processor reinforced-payload-conveyor
packcolor reinforced-payload-router disperse large-shield-projector payload-mass-driver world-cell
packcolor carbide-wall carbide-wall-large tank-fabricator mech-fabricator ship-fabricator
packcolor reinforced-surge-wall radar blast-door canvas armored-duct
packcolor unit-repair-tower diffuse prime-refabricator basic-assembler-module reinforced-surge-wall-large
packcolor tank-refabricator mech-refabricator ship-refabricator slag-heater afflict
packcolor shielded-wall lustre scathe smite underflow-duct
packcolor malign shockwave-tower heat-source flux-reactor neoplasia-reactor
packcolor heat-router large-payload-mass-driver reinforced-message world-message world-switch
packcolor small-heat-redirector large-cliff-crusher advanced-launch-pad landing-pad tile-logic-display
packcolor null null null null null
noop
end
print "变量表版本-152.2"
print "版本更新可能导致变量表出现异常"
-------
控制核心：
jump 5 equal initial true
set endPoint origin
set centralPr centralPr
set thisMarking "CustomDotMatrix-byNOSBHG2g"
set initial true
op add idUnit idUnit 1
select idUnit lessThan idUnit endPoint idUnit origin
lookup block item idUnit
sensor itemName item @name
read unit centralPr itemName
ubind unit
sensor shootX arc @shootX
sensor shootY arc @shootY
op mul idUnit1 idUnit 2
read offsetX bank idUnit1
op add idUnit2 idUnit1 1
read offsetY bank idUnit2
op add moveX offsetX shootX
op add moveY offsetY shootY
ucontrol move moveX moveY 0 0 0
--------
热操作核心
format ▽自定义热操作：快速修改阵型角度
sensor shooting arc1 @shooting
jump 1 equal shooting 0
sensor shootX arc1 @shootX
sensor shootY arc1 @shootY
wait 0.2
sensor shootX1 arc1 @shootX
sensor shootY1 arc1 @shootY
op sub differenceX shootX1 shootX
op sub differenceY shootY1 shootY
op angle angle differenceX differenceY
sensor shooting arc1 @shooting
write angle processor1 "angle"
jump 6 equal shooting 1
write angle processor1 "angle"

可以看见主控核心通过连接控制核心，内存库和arc电弧。
是核心，无需与任何逻辑连接，
热操作逻辑只与分配核心连接。

可以看到分配核通过将自己的引用传给各个主控核，主控核读取相应区间的分配核里边存储的单位变量，以此实现单位分配。
阵生成核心在这里：
set 墙体 @copper-wall
sensor swj switch1 @enabled
jump 1 equal swj 0
set minY 999
set minX 999
set maxX 0
set maxY 0
set id 0
getlink block id
sensor type block @type
jump 17 notEqual type 墙体
sensor x block @x
sensor y block @y
op min minX x minX
op min minY y minY
op max maxX x maxX
op max maxY y maxY
op add id id 1
jump 8 lessThan id @links
set id 0
printchar 34
getlink block id
sensor type block @type
jump 32 notEqual type 墙体
sensor x block @x
sensor y block @y
op sub x x minX
op sub y y minY
op add utf x 35
printchar utf
op add utf y 35
printchar utf
op add id id 1
jump 21 lessThan id @links
printchar 34
printflush message1
control enabled switch1 0 0 0 0
op sub differenceX maxX minX
op sub differenceY maxY minY
print "字体点阵生成端\n\n生成使用墙体:"
print 墙体
printchar 墙体
print "\n字体 长: {0} 高: {0}  \n中心点偏移量  x : {0}  y : {0}"
format differenceX
format differenceY
op idiv offsetX differenceX 2
op idiv offsetY differenceY 2
format offsetX
format offsetY
printflush message2
他通过连接防御方块生成矩阵，并将生成的矩阵存储进信息板里

---------------------------------------------------------------------------------------------------------------------
接下来介绍一组高价值的学习逻辑，逻辑通过开关选择要挖取矿物的单位，通过分类器选择要挖哪些矿物，计算每个矿物的衰减趋势，实现单位的均衡挖矿，并且配有单位分配，
这个蓝图包含4个不同的逻辑，
一个设置核，用于连接多个开关与多个分类器，并与分配核心链接，用于选择要控制的单位和需要挖取的矿物，并且涉及核心算法
一个打印核，用于处理信息板的打印，打印数据和作者信息，链接设置核与分配核。
一个分配核，和多个主控核心。是我们主要学习的地方。
--------
设置核心：
set 保底 0
sensor mono switch1 @enabled
write mono processor1 "monoEn"
jump 5 equal mono lastMono
write 1 processor1 "switchChanged"
sensor poly switch2 @enabled
write poly processor1 "polyEn"
jump 9 equal poly lastPoly
write 1 processor1 "switchChanged"
sensor mega switch3 @enabled
write mega processor1 "megaEn"
jump 13 equal mega lastMega
write 1 processor1 "switchChanged"
sensor pulsar switch4 @enabled
write pulsar processor1 "pulsarEn"
jump 17 equal pulsar lastPulsar
write 1 processor1 "switchChanged"
sensor quasar switch5 @enabled
write quasar processor1 "quasarEn"
jump 21 equal quasar lastQuasar
write 1 processor1 "switchChanged"
read stop1 processor1 "stop1"
jump 1 equal stop1 0
set lastMono mono
set lastPoly poly
set lastMega mega
set lastPulsar pulsar
set lastQuasar quasar
write -1 processor1 "stop1"
jump 33 equal mono 0
read 一二三 processor1 "firstMono"
sensor dead 一二三 @dead
jump 49 equal dead 0
jump 37 equal poly 0
read 一二三 processor1 "firstPoly"
sensor dead 一二三 @dead
jump 49 equal dead 0
jump 41 equal mega 0
read 一二三 processor1 "firstMega"
sensor dead 一二三 @dead
jump 49 equal dead 0
jump 45 equal pulsar 0
read 一二三 processor1 "firstPulsar"
sensor dead 一二三 @dead
jump 49 equal dead 0
jump 1 equal quasar 0
read 一二三 processor1 "firstQuasar"
sensor dead 一二三 @dead
jump 1 notEqual dead 0
ubind 一二三
ulocate building core 0 @copper outx outy found 核心
sensor 核心上限 核心 @itemCapacity
op sub 核心上限_sub 核心上限 200
write 核心上限 processor1 "coreItCap"
ulocate ore core 0 @copper outx outy 铜矿 hx
ulocate ore core 0 @lead outx outy 铅矿 hx
ulocate ore core 0 @titanium outx outy 钛矿 hx
ulocate ore core 0 @sand outx outy 沙矿 hx
ulocate ore core 0 @coal outx outy 煤矿 hx
ulocate ore core 0 @scrap outx outy 废矿 hx
ulocate ore core 0 @beryllium outx outy 铍矿 hx
set i 0
set 分类器打表 0
getlink sorter i
sensor 矿 sorter @config
jump 72 equal 矿 nulll
sensor 矿id 矿 @id
op shr 检查 0b10000000101110011 矿id
op mod 检查 检查 2
jump 72 notEqual 检查 1
op shl c 1 矿id
op add 分类器打表 分类器打表 c
op add i i 1
jump 63 lessThan i @links
op shr 铜表 分类器打表 0
op shr 铅表 分类器打表 1
op shr 钛表 分类器打表 6
op shr 沙表 分类器打表 4
op shr 煤表 分类器打表 5
op shr 废表 分类器打表 8
op shr 铍表 分类器打表 16
jump 109 equal 初始化 1
op add 保底 保底 0
sensor 铜0 核心 @copper
sensor 铅0 核心 @lead
sensor 钛0 核心 @titanium
sensor 沙0 核心 @sand
sensor 煤0 核心 @coal
sensor 废0 核心 @scrap
sensor 铍0 核心 @beryllium
set T3铜系数 0.2
set T2铜系数 0.2
set T1铜系数 0.2
set T3铅系数 0.2
set T2铅系数 0.2
set T1铅系数 0.2
set T3钛系数 0.2
set T3沙系数 0.2
set T2沙系数 0.2
set T1沙系数 0.2
set T3煤系数 0.2
set T2煤系数 0.2
set T3废系数 0.2
set T2废系数 0.2
set T1废系数 0.2
set T3铍系数 0.2
set 基础权重 0.08
set 加速权重 0.8
set 初始化 1
set T3min 999999999999999
set T2min 999999999999999
set T1min 999999999999999
op mul 预期上限 核心上限 基础权重
set T3总分母 0
set T2总分母 0
set T1总分母 0
op and 挖铜 铜矿 铜表
op and 挖铅 铅矿 铅表
op and 挖钛 钛矿 钛表
op and 挖沙 沙矿 沙表
op and 挖煤 煤矿 煤表
op and 挖废 废矿 废表
op and 挖铍 铍矿 铍表
sensor 铜 核心 @copper
sensor 铅 核心 @lead
sensor 钛 核心 @titanium
sensor 沙 核心 @sand
sensor 煤 核心 @coal
sensor 废 核心 @scrap
sensor 铍 核心 @beryllium
sensor coreItemCap 核心 @itemCapacity
op div 敏感度钝化 核心上限 2.56
op mul 敏感度钝化 敏感度钝化 基础权重
jump 135 lessThan 敏感度钝化 750
set 敏感度钝化 750
op sub dt @time t0
op abs dt dt t0
jump 139 greaterThan dt 6500
end
jump 165 equal 挖铜 0
op add 铜 1 铜
op sub a铜 铜 铜0
op mul a铜 a铜 加速权重
op mul 预期铜 铜 基础权重
op add 预期铜 预期铜 a铜
jump 147 greaterThanEq 预期铜 1
set 预期铜 1
jump 149 lessThanEq 预期铜 预期上限
set 预期铜 预期上限
op add 预期铜 预期铜 敏感度钝化
op min T3min T3min 铜
op min T2min T2min 铜
op min T1min T1min 铜
jump 155 notEqual T3min 铜
set T3写入e 9999900
jump 157 notEqual T2min 铜
set T2写入e 9999900
jump 159 notEqual T1min 铜
set T1写入e 9999900
op div 铜分子 1 预期铜
op pow 铜分子 铜分子 2
op add T3总分母 T3总分母 铜分子
op add T2总分母 T2总分母 铜分子
op add T1总分母 T1总分母 铜分子
set 铜0 铜
jump 191 equal 挖铅 0
op add 铅 1 铅
op sub a铅 铅 铅0
op mul a铅 a铅 加速权重
op mul 预期铅 铅 基础权重
op add 预期铅 预期铅 a铅
jump 173 greaterThanEq 预期铅 1
set 预期铅 1
jump 175 lessThanEq 预期铅 预期上限
set 预期铅 预期上限
op add 预期铅 预期铅 敏感度钝化
op min T3min T3min 铅
op min T2min T2min 铅
op min T1min T1min 铅
jump 181 notEqual T3min 铅
set T3写入e 9999901
jump 183 notEqual T2min 铅
set T2写入e 9999901
jump 185 notEqual T1min 铅
set T1写入e 9999901
op div 铅分子 1 预期铅
op pow 铅分子 铅分子 2
op add T3总分母 T3总分母 铅分子
op add T2总分母 T2总分母 铅分子
op add T1总分母 T1总分母 铅分子
set 铅0 铅
jump 209 equal 挖钛 0
op add 钛 1 钛
op sub a钛 钛 钛0
op mul a钛 a钛 加速权重
op mul 预期钛 钛 基础权重
op add 预期钛 预期钛 a钛
jump 199 greaterThanEq 预期钛 1
set 预期钛 1
jump 201 lessThanEq 预期钛 预期上限
set 预期钛 预期上限
op add 预期钛 预期钛 敏感度钝化
op min T3min T3min 钛
jump 205 notEqual T3min 钛
set T3写入e 9999906
op div 钛分子 1 预期钛
op pow 钛分子 钛分子 2
op add T3总分母 T3总分母 钛分子
set 钛0 钛
jump 214 greaterThanEq T3min 保底
set T3沙系数 0.01
set T3煤系数 0.01
set T3废系数 0.01
set T3铍系数 0.01
jump 218 greaterThanEq T2min 保底
set T2沙系数 0.01
set T2煤系数 0.01
set T2废系数 0.01
jump 221 greaterThanEq T1min 保底
set T1沙系数 0.01
set T1废系数 0.01
jump 247 equal 挖沙 0
op add 沙 1 沙
op sub a沙 沙 沙0
op mul a沙 a沙 加速权重
op mul 预期沙 沙 基础权重
op add 预期沙 预期沙 a沙
jump 229 greaterThanEq 预期沙 1
set 预期沙 1
jump 231 lessThanEq 预期沙 预期上限
set 预期沙 预期上限
op add 预期沙 预期沙 敏感度钝化
op min T3min T3min 沙
op min T2min T2min 沙
op min T1min T1min 沙
jump 237 notEqual T3min 沙
set T3写入e 9999904
jump 239 notEqual T2min 沙
set T2写入e 9999904
jump 241 notEqual T1min 沙
set T1写入e 9999904
op div 沙分子 1 预期沙
op pow 沙分子 沙分子 2
op add T3总分母 T3总分母 沙分子
op add T2总分母 T2总分母 沙分子
op add T1总分母 T1总分母 沙分子
set 沙0 沙
jump 269 equal 挖煤 0
op add 煤 1 煤
op sub a煤 煤 煤0
op mul a煤 a煤 加速权重
op mul 预期煤 煤 基础权重
op add 预期煤 预期煤 a煤
jump 255 greaterThanEq 预期煤 1
set 预期煤 1
jump 257 lessThanEq 预期煤 预期上限
set 预期煤 预期上限
op add 预期煤 预期煤 敏感度钝化
op min T3min T3min 煤
op min T2min T2min 煤
jump 262 notEqual T3min 煤
set T3写入e 9999905
jump 264 notEqual T2min 煤
set T2写入e 9999905
op div 煤分子 1 预期煤
op pow 煤分子 煤分子 2
op add T3总分母 T3总分母 煤分子
op add T2总分母 T2总分母 煤分子
set 煤0 煤
jump 295 equal 挖废 0
op add 废 1 废
op sub a废 废 废0
op mul a废 a废 加速权重
op mul 预期废 废 基础权重
op add 预期废 预期废 a废
jump 277 greaterThanEq 预期废 1
set 预期废 1
jump 279 lessThanEq 预期废 预期上限
set 预期废 预期上限
op add 预期废 预期废 敏感度钝化
op min T3min T3min 废
op min T2min T2min 废
op min T1min T1min 废
jump 285 notEqual T3min 废
set T3写入e 9999908
jump 287 notEqual T2min 废
set T2写入e 9999908
jump 289 notEqual T1min 废
set T1写入e 9999908
op div 废分子 1 预期废
op pow 废分子 废分子 2
op add T3总分母 T3总分母 废分子
op add T2总分母 T2总分母 废分子
op add T1总分母 T1总分母 废分子
set 废0 废
jump 313 equal 挖铍 0
op add 铍 1 铍
op sub a铍 铍 铍0
op mul a铍 a铍 加速权重
op mul 预期铍 铍 基础权重
op add 预期铍 预期铍 a铍
jump 303 greaterThanEq 预期铍 1
set 预期铍 1
jump 305 lessThanEq 预期铍 预期上限
set 预期铍 预期上限
op add 预期铍 预期铍 敏感度钝化
op min T3min T3min 铍
jump 309 notEqual T3min 铍
set T3写入e 9999916
op div 铍分子 1 预期铍
op pow 铍分子 铍分子 2
op add T3总分母 T3总分母 铍分子
set 铍0 铍
set 取出比例 0.5
op sub 剩余比例 1 取出比例
set T3分配系数分母 0
set T2分配系数分母 0
set T1分配系数分母 0
set 系数T3总分母 0
set 系数T2总分母 0
set 系数T1总分母 0
jump 340 equal 挖铜 0
jump 324 greaterThan T3铜系数 0.01
set T3铜系数 0.01
op div T3铜分配系数 铜分子 T3总分母
op mul T3铜分配系数 T3铜分配系数 T3铜系数
op add T3分配系数分母 T3分配系数分母 T3铜分配系数
op add 系数T3总分母 系数T3总分母 T3铜系数
jump 330 greaterThan T2铜系数 0.01
set T2铜系数 0.01
op div T2铜分配系数 铜分子 T2总分母
op mul T2铜分配系数 T2铜分配系数 T2铜系数
op add T2分配系数分母 T2分配系数分母 T2铜分配系数
op add 系数T2总分母 系数T2总分母 T2铜系数
jump 336 greaterThan T1铜系数 0.01
set T1铜系数 0.01
op div T1铜分配系数 铜分子 T1总分母
op mul T1铜分配系数 T1铜分配系数 T1铜系数
op add T1分配系数分母 T1分配系数分母 T1铜分配系数
op add 系数T1总分母 系数T1总分母 T1铜系数
jump 359 equal 挖铅 0
jump 343 greaterThan T3铅系数 0.01
set T3铅系数 0.01
op div T3铅分配系数 铅分子 T3总分母
op mul T3铅分配系数 T3铅分配系数 T3铅系数
op add T3分配系数分母 T3分配系数分母 T3铅分配系数
op add 系数T3总分母 系数T3总分母 T3铅系数
jump 349 greaterThan T2铅系数 0.01
set T2铅系数 0.01
op div T2铅分配系数 铅分子 T2总分母
op mul T2铅分配系数 T2铅分配系数 T2铅系数
op add T2分配系数分母 T2分配系数分母 T2铅分配系数
op add 系数T2总分母 系数T2总分母 T2铅系数
jump 355 greaterThan T1铅系数 0.01
set T1铅系数 0.01
op div T1铅分配系数 铅分子 T1总分母
op mul T1铅分配系数 T1铅分配系数 T1铅系数
op add T1分配系数分母 T1分配系数分母 T1铅分配系数
op add 系数T1总分母 系数T1总分母 T1铅系数
jump 366 equal 挖钛 0
jump 362 greaterThan T3钛系数 0.01
set T3钛系数 0.01
op div T3钛分配系数 钛分子 T3总分母
op mul T3钛分配系数 T3钛分配系数 T3钛系数
op add T3分配系数分母 T3分配系数分母 T3钛分配系数
op add 系数T3总分母 系数T3总分母 T3钛系数
jump 385 equal 挖沙 0
jump 369 greaterThan T3沙系数 0.01
set T3沙系数 0.01
op div T3沙分配系数 沙分子 T3总分母
op mul T3沙分配系数 T3沙分配系数 T3沙系数
op add T3分配系数分母 T3分配系数分母 T3沙分配系数
op add 系数T3总分母 系数T3总分母 T3沙系数
jump 375 greaterThan T2沙系数 0.01
set T2沙系数 0.01
op div T2沙分配系数 沙分子 T2总分母
op mul T2沙分配系数 T2沙分配系数 T2沙系数
op add T2分配系数分母 T2分配系数分母 T2沙分配系数
op add 系数T2总分母 系数T2总分母 T2沙系数
jump 381 greaterThan T1沙系数 0.01
set T1沙系数 0.01
op div T1沙分配系数 沙分子 T1总分母
op mul T1沙分配系数 T1沙分配系数 T1沙系数
op add T1分配系数分母 T1分配系数分母 T1沙分配系数
op add 系数T1总分母 系数T1总分母 T1沙系数
jump 398 equal 挖煤 0
jump 388 greaterThan T3煤系数 0.01
set T3煤系数 0.01
op div T3煤分配系数 煤分子 T3总分母
op mul T3煤分配系数 T3煤分配系数 T3煤系数
op add T3分配系数分母 T3分配系数分母 T3煤分配系数
op add 系数T3总分母 系数T3总分母 T3煤系数
jump 394 greaterThan T2煤系数 0.01
set T2煤系数 0.01
op div T2煤分配系数 煤分子 T2总分母
op mul T2煤分配系数 T2煤分配系数 T2煤系数
op add T2分配系数分母 T2分配系数分母 T2煤分配系数
op add 系数T2总分母 系数T2总分母 T2煤系数
jump 417 equal 挖废 0
jump 401 greaterThan T3废系数 0.01
set T3废系数 0.01
op div T3废分配系数 废分子 T3总分母
op mul T3废分配系数 T3废分配系数 T3废系数
op add T3分配系数分母 T3分配系数分母 T3废分配系数
op add 系数T3总分母 系数T3总分母 T3废系数
jump 407 greaterThan T2废系数 0.01
set T2废系数 0.01
op div T2废分配系数 废分子 T2总分母
op mul T2废分配系数 T2废分配系数 T2废系数
op add T2分配系数分母 T2分配系数分母 T2废分配系数
op add 系数T2总分母 系数T2总分母 T2废系数
jump 413 greaterThan T1废系数 0.01
set T1废系数 0.01
op div T1废分配系数 废分子 T1总分母
op mul T1废分配系数 T1废分配系数 T1废系数
op add T1分配系数分母 T1分配系数分母 T1废分配系数
op add 系数T1总分母 系数T1总分母 T1废系数
jump 424 equal 挖铍 0
jump 420 greaterThan T3铍系数 0.01
set T3铍系数 0.01
op div T3铍分配系数 铍分子 T3总分母
op mul T3铍分配系数 T3铍分配系数 T3铍系数
op add T3分配系数分母 T3分配系数分母 T3铍分配系数
op add 系数T3总分母 系数T3总分母 T3铍系数
op div T3分配系数分母 取出比例 T3分配系数分母
op div T2分配系数分母 取出比例 T2分配系数分母
op div T1分配系数分母 取出比例 T1分配系数分母
jump 440 equal 挖铜 0
op mul T3铜系数0 T3铜分配系数 T3分配系数分母
op mul T3铜系数 T3铜系数 剩余比例
op add T3铜系数 T3铜系数 T3铜系数0
op div T3铜系数 T3铜系数 系数T3总分母
op mul T2铜系数0 T2铜分配系数 T2分配系数分母
op mul T2铜系数 T2铜系数 剩余比例
op add T2铜系数 T2铜系数 T2铜系数0
op div T2铜系数 T2铜系数 系数T2总分母
op mul T1铜系数0 T1铜分配系数 T1分配系数分母
op mul T1铜系数 T1铜系数 剩余比例
op add T1铜系数 T1铜系数 T1铜系数0
op div T1铜系数 T1铜系数 系数T1总分母
jump 453 equal 挖铅 0
op mul T3铅系数0 T3铅分配系数 T3分配系数分母
op mul T3铅系数 T3铅系数 剩余比例
op add T3铅系数 T3铅系数 T3铅系数0
op div T3铅系数 T3铅系数 系数T3总分母
op mul T2铅系数0 T2铅分配系数 T2分配系数分母
op mul T2铅系数 T2铅系数 剩余比例
op add T2铅系数 T2铅系数 T2铅系数0
op div T2铅系数 T2铅系数 系数T2总分母
op mul T1铅系数0 T1铅分配系数 T1分配系数分母
op mul T1铅系数 T1铅系数 剩余比例
op add T1铅系数 T1铅系数 T1铅系数0
op div T1铅系数 T1铅系数 系数T1总分母
jump 458 equal 挖钛 0
op mul T3钛系数0 T3钛分配系数 T3分配系数分母
op mul T3钛系数 T3钛系数 剩余比例
op add T3钛系数 T3钛系数 T3钛系数0
op div T3钛系数 T3钛系数 系数T3总分母
jump 471 equal 挖沙 0
op mul T3沙系数0 T3沙分配系数 T3分配系数分母
op mul T3沙系数 T3沙系数 剩余比例
op add T3沙系数 T3沙系数 T3沙系数0
op div T3沙系数 T3沙系数 系数T3总分母
op mul T2沙系数0 T2沙分配系数 T2分配系数分母
op mul T2沙系数 T2沙系数 剩余比例
op add T2沙系数 T2沙系数 T2沙系数0
op div T2沙系数 T2沙系数 系数T2总分母
op mul T1沙系数0 T1沙分配系数 T1分配系数分母
op mul T1沙系数 T1沙系数 剩余比例
op add T1沙系数 T1沙系数 T1沙系数0
op div T1沙系数 T1沙系数 系数T1总分母
jump 480 equal 挖煤 0
op mul T3煤系数0 T3煤分配系数 T3分配系数分母
op mul T3煤系数 T3煤系数 剩余比例
op add T3煤系数 T3煤系数 T3煤系数0
op div T3煤系数 T3煤系数 系数T3总分母
op mul T2煤系数0 T2煤分配系数 T2分配系数分母
op mul T2煤系数 T2煤系数 剩余比例
op add T2煤系数 T2煤系数 T2煤系数0
op div T2煤系数 T2煤系数 系数T2总分母
jump 493 equal 挖废 0
op mul T3废系数0 T3废分配系数 T3分配系数分母
op mul T3废系数 T3废系数 剩余比例
op add T3废系数 T3废系数 T3废系数0
op div T3废系数 T3废系数 系数T3总分母
op mul T2废系数0 T2废分配系数 T2分配系数分母
op mul T2废系数 T2废系数 剩余比例
op add T2废系数 T2废系数 T2废系数0
op div T2废系数 T2废系数 系数T2总分母
op mul T1废系数0 T1废分配系数 T1分配系数分母
op mul T1废系数 T1废系数 剩余比例
op add T1废系数 T1废系数 T1废系数0
op div T1废系数 T1废系数 系数T1总分母
jump 498 equal 挖铍 0
op mul T3铍系数0 T3铍分配系数 T3分配系数分母
op mul T3铍系数 T3铍系数 剩余比例
op add T3铍系数 T3铍系数 T3铍系数0
op div T3铍系数 T3铍系数 系数T3总分母
jump 528 equal mega 0
read 可抓单位数 processor1 "mega"
op mul 铜分配数 T3铜系数 可抓单位数
op mul 铜分配数 铜分配数 挖铜
op floor 铜分配数 铜分配数 可抓单位数
write 铜分配数 processor1 "mega铜"
op mul 铅分配数 T3铅系数 可抓单位数
op mul 铅分配数 铅分配数 挖铅
op floor 铅分配数 铅分配数 可抓单位数
write 铅分配数 processor1 "mega铅"
op mul 钛分配数 T3钛系数 可抓单位数
op mul 钛分配数 钛分配数 挖钛
op floor 钛分配数 钛分配数 可抓单位数
write 钛分配数 processor1 "mega钛"
op mul 沙分配数 T3沙系数 可抓单位数
op mul 沙分配数 沙分配数 挖沙
op floor 沙分配数 沙分配数 可抓单位数
write 沙分配数 processor1 "mega沙"
op mul 煤分配数 T3煤系数 可抓单位数
op mul 煤分配数 煤分配数 挖煤
op floor 煤分配数 煤分配数 可抓单位数
write 煤分配数 processor1 "mega煤"
op mul 废分配数 T3废系数 可抓单位数
op mul 废分配数 废分配数 挖废
op floor 废分配数 废分配数 可抓单位数
write 废分配数 processor1 "mega废"
op mul 铍分配数 T3铍系数 可抓单位数
op mul 铍分配数 铍分配数 挖铍
op floor 铍分配数 铍分配数 可抓单位数
write 铍分配数 processor1 "mega铍"
jump 558 equal quasar 0
read 可抓单位数 processor1 "quasar"
op mul 铜分配数 T3铜系数 可抓单位数
op mul 铜分配数 铜分配数 挖铜
op floor 铜分配数 铜分配数 可抓单位数
write 铜分配数 processor1 "quasar铜"
op mul 铅分配数 T3铅系数 可抓单位数
op mul 铅分配数 铅分配数 挖铅
op floor 铅分配数 铅分配数 可抓单位数
write 铅分配数 processor1 "quasar铅"
op mul 钛分配数 T3钛系数 可抓单位数
op mul 钛分配数 钛分配数 挖钛
op floor 钛分配数 钛分配数 可抓单位数
write 钛分配数 processor1 "quasar钛"
op mul 沙分配数 T3沙系数 可抓单位数
op mul 沙分配数 沙分配数 挖沙
op floor 沙分配数 沙分配数 可抓单位数
write 沙分配数 processor1 "quasar沙"
op mul 煤分配数 T3煤系数 可抓单位数
op mul 煤分配数 煤分配数 挖煤
op floor 煤分配数 煤分配数 可抓单位数
write 煤分配数 processor1 "quasar煤"
op mul 废分配数 T3废系数 可抓单位数
op mul 废分配数 废分配数 挖废
op floor 废分配数 废分配数 可抓单位数
write 废分配数 processor1 "quasar废"
op mul 铍分配数 T3铍系数 可抓单位数
op mul 铍分配数 铍分配数 挖铍
op floor 铍分配数 铍分配数 可抓单位数
write 铍分配数 processor1 "quasar铍"
jump 580 equal poly 0
read 可抓单位数 processor1 "poly"
op mul 铜分配数 T2铜系数 可抓单位数
op mul 铜分配数 铜分配数 挖铜
op floor 铜分配数 铜分配数 可抓单位数
write 铜分配数 processor1 "poly铜"
op mul 铅分配数 T2铅系数 可抓单位数
op mul 铅分配数 铅分配数 挖铅
op floor 铅分配数 铅分配数 可抓单位数
write 铅分配数 processor1 "poly铅"
op mul 沙分配数 T2沙系数 可抓单位数
op mul 沙分配数 沙分配数 挖沙
op floor 沙分配数 沙分配数 可抓单位数
write 沙分配数 processor1 "poly沙"
op mul 煤分配数 T2煤系数 可抓单位数
op mul 煤分配数 煤分配数 挖煤
op floor 煤分配数 煤分配数 可抓单位数
write 煤分配数 processor1 "poly煤"
op mul 废分配数 T2废系数 可抓单位数
op mul 废分配数 废分配数 挖废
op floor 废分配数 废分配数 可抓单位数
write 废分配数 processor1 "poly废"
jump 602 equal pulsar 0
read 可抓单位数 processor1 "pulsar"
op mul 铜分配数 T2铜系数 可抓单位数
op mul 铜分配数 铜分配数 挖铜
op floor 铜分配数 铜分配数 可抓单位数
write 铜分配数 processor1 "pulsar铜"
op mul 铅分配数 T2铅系数 可抓单位数
op mul 铅分配数 铅分配数 挖铅
op floor 铅分配数 铅分配数 可抓单位数
write 铅分配数 processor1 "pulsar铅"
op mul 沙分配数 T2沙系数 可抓单位数
op mul 沙分配数 沙分配数 挖沙
op floor 沙分配数 沙分配数 可抓单位数
write 沙分配数 processor1 "pulsar沙"
op mul 煤分配数 T2煤系数 可抓单位数
op mul 煤分配数 煤分配数 挖煤
op floor 煤分配数 煤分配数 可抓单位数
write 煤分配数 processor1 "pulsar煤"
op mul 废分配数 T2废系数 可抓单位数
op mul 废分配数 废分配数 挖废
op floor 废分配数 废分配数 可抓单位数
write 废分配数 processor1 "pulsar废"
jump 620 equal mono 0
read 可抓单位数 processor1 "mono"
op mul 铜分配数 T1铜系数 可抓单位数
op mul 铜分配数 铜分配数 挖铜
op floor 铜分配数 铜分配数 可抓单位数
write 铜分配数 processor1 "mono铜"
op mul 铅分配数 T1铅系数 可抓单位数
op mul 铅分配数 铅分配数 挖铅
op floor 铅分配数 铅分配数 可抓单位数
write 铅分配数 processor1 "mono铅"
op mul 沙分配数 T1沙系数 可抓单位数
op mul 沙分配数 沙分配数 挖沙
op floor 沙分配数 沙分配数 可抓单位数
write 沙分配数 processor1 "mono沙"
op mul 废分配数 T1废系数 可抓单位数
op mul 废分配数 废分配数 挖废
op floor 废分配数 废分配数 可抓单位数
write 废分配数 processor1 "mono废"
set t0 @time
write 1 processor1 "!stop2"
end
print 123的挖矿单位分配总核心v0.5-2025.5.2
print aaa魔改-2025.5.10
-----------
信息打印核心
set title ""
print "{0}{0}[sky]单位挖矿逻辑{0}{0}[white]\nby [scarlet]a[][lime]a[][blue]a[] & [cyan]123[][gray]xFG[]\nv0.4测试中\nE核挖煤沙适配\n\n[accent]单位均摊处理，充分利用算力\n分配挖矿，同时挖多种矿物[]\n\n开关选单位，分类器选物品\n若分配逻辑刷新速度过慢可换超核\n每挖矿逻辑上限260单位\n\n[accent]拓展逻辑[]\n复制下方中核，用上方中核链接新造的逻辑块\n或\n建造新的逻辑块，复制粘贴下方中核的代码到新造的逻辑，用上方中核链接"
set i 0
op add ri i offset
op mod ri ri 6
read char title ri
jump 10 equal char 59406
jump 12 equal char 59501
format "[orange]"
jump 14 always x false
format "[#8982edff]"
jump 14 always x false
format "[acid]"
jump 14 always x false
op add i i 1
jump 3 lessThan i 4
op add offset offset 1
op mod offset offset 6
printflush message1
print "{0}\n\n{0}\n\n{0}\n\n{0}\n\n{0}\n总{0}\n           开关对应\n   实际控制数量\n\n挖矿逻辑数量：{0}\n平均控制数量：{0}\n模式：{0}\n      {0}\n"
read monoEn processor1 "mono"
jump 25 equal monoEn 0
read monoNum processor2 "mono"
format monoNum
jump 27 always x false
format "[scarlet][]"
set monoNum 0
read polyEn processor1 "poly"
jump 32 equal polyEn 0
read polyNum processor2 "poly"
format polyNum
jump 34 always x false
format "[scarlet][]"
set polyNum 0
read megaEn processor1 "mega"
jump 39 equal megaEn 0
read megaNum processor2 "mega"
format megaNum
jump 41 always x false
format "[scarlet][]"
set megaNum 0
read pulsarEn processor1 "pulsar"
jump 46 equal pulsarEn 0
read pulsarNum processor2 "pulsar"
format pulsarNum
jump 48 always x false
format "[scarlet][]"
set pulsarNum 0
read quasarEn processor1 "quasar"
jump 53 equal quasarEn 0
read quasarNum processor2 "quasar"
format quasarNum
jump 55 always x false
format "[scarlet][]"
set quasarNum 0
op add totalUnitN monoNum polyNum
op add totalUnitN totalUnitN megaNum
op add totalUnitN totalUnitN pulsarNum
op add totalUnitN totalUnitN quasarNum
format totalUnitN
read links processor2 "links"
format links
op div average totalUnitN links
op idiv average average 0.01
op mul average average 0.01
format average
read forceMode processor2 "forceMode"
jump 70 notEqual forceMode 0
format "自动"
jump 71 always x false
format "强制"
read eCore processor2 "eCore"
jump 75 notEqual eCore 0
format "不兼容E核煤沙"
jump 76 always x false
format "兼容E核煤沙"
read refreshTime processor2 "refreshTime"
jump 80 notEqual refreshTime null
print "分配逻辑未刷新过\n\n"
jump 84 always x false
print "分配逻辑刷新在{0}s前\n\n"
op sub diffTime @second refreshTime
op floor diffTime diffTime refreshTime
format diffTime
print "{2}\n{0}{1} / {2}%\n{0}{1} / {2}%\n{0}{1} / {2}%\n{0}{1} / {2}%\n{0}{1} / {2}%\n{0}{1} / {2}%\n{0}{1} / {2}%"
read 铜矿 processor1 "铜矿"
jump 89 notEqual 铜矿 0
format "[scarlet][]"
jump 90 always x false
format ""
read 铅矿 processor1 "铅矿"
jump 94 notEqual 铅矿 0
format "[scarlet][]"
jump 95 always x false
format ""
read 钛矿 processor1 "钛矿"
jump 99 notEqual 钛矿 0
format "[scarlet][]"
jump 100 always x false
format ""
read 沙矿 processor1 "沙矿"
jump 104 notEqual 沙矿 0
format "[scarlet][]"
jump 105 always x false
format ""
read 煤矿 processor1 "煤矿"
jump 109 notEqual 煤矿 0
format "[scarlet][]"
jump 110 always x false
format ""
read 废矿 processor1 "废矿"
jump 114 notEqual 废矿 0
format "[scarlet][]"
jump 115 always x false
format ""
read 铍矿 processor1 "铍矿"
jump 119 notEqual 废矿 0
format "[scarlet][]"
jump 120 always x false
format ""
read 铜 processor1 "铜"
format 铜
read 铅 processor1 "铅"
format 铅
read 钛 processor1 "钛"
format 钛
read 沙 processor1 "沙"
format 沙
read 煤 processor1 "煤"
format 煤
read 废 processor1 "废"
format 废
read 铍 processor1 "铍"
format 铍
read coreItemCap processor1 "coreItemCap"
format coreItemCap
op div coreItemCap coreItemCap 1000
op idiv 铜ratio 铜 coreItemCap
op div 铜ratio 铜ratio 10
format 铜ratio
op idiv 铅ratio 铅 coreItemCap
op div 铅ratio 铅ratio 10
format 铅ratio
op idiv 钛ratio 钛 coreItemCap
op div 钛ratio 钛ratio 10
format 钛ratio
op idiv 沙ratio 沙 coreItemCap
op div 沙ratio 沙ratio 10
format 沙ratio
op idiv 煤ratio 煤 coreItemCap
op div 煤ratio 煤ratio 10
format 煤ratio
op idiv 废ratio 废 coreItemCap
op div 废ratio 废ratio 10
format 废ratio
op idiv 铍ratio 铍 coreItemCap
op div 铍ratio 铍ratio 10
format 铍ratio
read hasVoidProcessor processor2 "hasVoidProcessor"
jump 174 equal hasVoidProcessor 0
read voidProcessor processor2 "voidProcessor"
jump 169 notEqual voidProcessor null
print "\n\n[scarlet]错误[]\n({0},{0})处的分配逻辑未链接挖矿逻辑"
sensor processor2X processor2 @x
sensor processor2Y processor2 @y
format processor2X
format processor2Y
printflush message2
end
sensor voidProcessorX voidProcessor @x
sensor voidProcessorY voidProcessor @y
print "\n\n[scarlet]错误[]\n({0},{0})处的挖矿逻辑为无效挖矿逻辑"
format voidProcessorX
format voidProcessorY
read hasMissingStorage processor2 "hasMissingStorage"
jump 186 equal hasMissingStorage 0
read missingStorageCore processor2 "missingStorage"
sensor missingStorageCoreX missingStorageCore @x
sensor missingStorageCoreY missingStorageCore @y
print "\n\n[scarlet]错误[]\n无法找到({0},{0})处核心的贴核容器/仓库"
set errorRecord "\n\n[scarlet]上个错误[]({0}s)\n无法找到({0},{0})处核心的贴核容器/仓库"
op add errorTimeRecord @second 10
format missingStorageCoreX
format missingStorageCoreY
printflush message2
end
jump 194 strictEqual errorRecord null
jump 194 lessThan errorTimeRecord @second
print errorRecord
op sub diffTime errorTimeRecord @second
op floor diffTime diffTime @second
format diffTime
format missingStorageCoreX
format missingStorageCoreY
printflush message2
-----------------
分配核心
print "▼0 -> 自动判断 是否兼容e核煤沙/1 -> 强制不兼容/2 -> 强制兼容▼"
set forceMode 2
set stop1 1
jump 3 equal stop1 1
jump 9 equal monoEn 0
set countUT @mono
set firstUnitV "firstMono"
op add _countReturn @counter 1
jump 30 always x false
jump 14 equal polyEn 0
set countUT @poly
set firstUnitV "firstPoly"
op add _countReturn @counter 1
jump 30 always x false
jump 19 equal megaEn 0
set countUT @mega
set firstUnitV "firstMega"
op add _countReturn @counter 1
jump 30 always x false
jump 24 equal pulsarEn 0
set countUT @pulsar
set firstUnitV "firstPulsar"
op add _countReturn @counter 1
jump 30 always x false
jump 52 equal quasarEn 0
set countUT @quasar
set firstUnitV "firstQuasar"
op add _countReturn @counter 1
jump 30 always x false
jump 52 always x false
set firstUnit null
ubind countUT
sensor dead firstUnit @dead
jump 38 equal dead 0
set countUN 0
jump 47 strictEqual @unit null
set firstUnit @unit
jump 39 always x false
jump 47 equal @unit firstUnit
sensor ctd @unit @controlled
jump 44 equal ctd 0
jump 31 notEqual ctd 1
sensor flag @unit @flag
jump 31 notEqual flag 0
ucontrol flag %FFFFFFFF 0 0 0 0
op add countUN countUN 1
jump 31 always firstUnit @unit
sensor countUTN countUT @name
write countUN @this countUTN
write firstUnit @this firstUnitV
set @counter _countReturn
end
jump 4 equal !stop2 0
set links @links
jump 57 notEqual eCore 1
set loopEnd 64
jump 58 always x false
set loopEnd 0
set hasVoidProcessor_private 0
set hasMissingStorage_private 0
set processorI 0
getlink processor processorI
write loopEnd processor "loopEnd"
jump 65 equal switchOffUnit 0
write 52 processor "@counter"
jump 72 equal hasVoidProcessor_private 1
set check null
read check processor "readerI"
jump 70 strictEqual check null
jump 72 always check null
set voidProcessor processor
set hasVoidProcessor_private 1
jump 80 equal eCore 0
jump 80 equal hasMissingStorage_private 1
read hasMissingStorage_private? processor "hasMissingStorage"
read missingStorage processor "missingStorage"
sensor missingStorageCoreType missingStorage @type
sensor missingStorageCoreTypeId missingStorageCoreType @id
jump 80 lessThanEq missingStorageCoreTypeId 92
set hasMissingStorage_private hasMissingStorage_private?
op add processorI processorI 1
jump 61 lessThan processorI @links
set hasVoidProcessor hasVoidProcessor_private
set hasMissingStorage hasMissingStorage_private
set switchOffUnit 0
set writerI 0
jump 142 equal monoEn 0
set unitNum 0
set firstMono null
jump 94 equal mono铜 0
set item @copper
set bindNum mono铜
op add _return @counter 1
jump 113 always x false
jump 99 equal mono铅 0
set item @lead
set bindNum mono铅
op add _return @counter 1
jump 113 always x false
jump 104 equal mono沙 0
set item @sand
set bindNum mono沙
op add _return @counter 1
jump 113 always x false
jump 109 equal mono废 0
set item @scrap
set bindNum mono废
op add _return @counter 1
jump 113 always x false
set bindNum 999999
op add _return @counter 1
jump 115 always x false
jump 141 always x false
sensor itemId item @id
op mul flagSet itemId %00000001
op add writerEnd writerI bindNum
ubind @mono
sensor dead firstMono @dead
jump 123 equal dead 0
set unitNum 0
jump 141 strictEqual @unit null
set firstMono @unit
jump 124 always x false
jump 141 equal @unit firstMono
sensor ctd @unit @controlled
jump 128 equal ctd 1
jump 130 equal ctd 0
jump 116 always ctd 0
sensor flag @unit @flag
jump 116 notEqual flag 0
op mod processorI writerI @links
getlink processor processorI
op idiv _ writerI @links
lookup block _ _
sensor _ _ @name
write @unit processor _
ucontrol flag flagSet 0 0 0 0
op add unitNum unitNum 1
op add writerI writerI 1
jump 116 lessThan writerI writerEnd
set @counter _return
set mono unitNum
jump 203 equal polyEn 0
set unitNum 0
set firstPoly null
jump 150 equal poly铜 0
set item @copper
set bindNum poly铜
op add _return @counter 1
jump 174 always x false
jump 155 equal poly铅 0
set item @lead
set bindNum poly铅
op add _return @counter 1
jump 174 always x false
jump 160 equal poly沙 0
set item @sand
set bindNum poly沙
op add _return @counter 1
jump 174 always x false
jump 165 equal poly煤 0
set item @coal
set bindNum poly煤
op add _return @counter 1
jump 174 always x false
jump 170 equal poly废 0
set item @scrap
set bindNum poly废
op add _return @counter 1
jump 174 always x false
set bindNum 999999
op add _return @counter 1
jump 176 always x false
jump 202 always x false
sensor itemId item @id
op mul flagSet itemId %00000001
op add writerEnd writerI bindNum
ubind @poly
sensor dead firstPoly @dead
jump 184 equal dead 0
set unitNum 0
jump 202 strictEqual @unit null
set firstPoly @unit
jump 185 always x false
jump 202 equal @unit firstPoly
sensor ctd @unit @controlled
jump 189 equal ctd 1
jump 191 equal ctd 0
jump 177 always ctd 0
sensor flag @unit @flag
jump 177 notEqual flag 0
op mod processorI writerI @links
getlink processor processorI
op idiv _ writerI @links
lookup block _ _
sensor _ _ @name
write @unit processor _
ucontrol flag flagSet 0 0 0 0
op add unitNum unitNum 1
op add writerI writerI 1
jump 177 lessThan writerI writerEnd
set @counter _return
set poly unitNum
jump 274 equal megaEn 0
set unitNum 0
set firstMega null
jump 211 equal mega铜 0
set item @copper
set bindNum mega铜
op add _return @counter 1
jump 245 always x false
jump 216 equal mega铅 0
set item @lead
set bindNum mega铅
op add _return @counter 1
jump 245 always x false
jump 221 equal mega钛 0
set item @titanium
set bindNum mega钛
op add _return @counter 1
jump 245 always x false
jump 226 equal mega沙 0
set item @sand
set bindNum mega沙
op add _return @counter 1
jump 245 always x false
jump 231 equal mega煤 0
set item @coal
set bindNum mega煤
op add _return @counter 1
jump 245 always x false
jump 236 equal mega废 0
set item @scrap
set bindNum mega废
op add _return @counter 1
jump 245 always x false
jump 241 equal mega铍 0
set item @beryllium
set bindNum mega铍
op add _return @counter 1
jump 245 always x false
set bindNum 999999
op add _return @counter 1
jump 247 always x false
jump 273 always x false
sensor itemId item @id
op mul flagSet itemId %00000001
op add writerEnd writerI bindNum
ubind @mega
sensor dead firstMega @dead
jump 255 equal dead 0
set unitNum 0
jump 273 strictEqual @unit null
set firstMega @unit
jump 256 always x false
jump 273 equal @unit firstMega
sensor ctd @unit @controlled
jump 260 equal ctd 1
jump 262 equal ctd 0
jump 248 always flag 0
sensor flag @unit @flag
jump 248 notEqual flag 0
op mod processorI writerI @links
getlink processor processorI
op idiv _ writerI @links
lookup block _ _
sensor _ _ @name
write @unit processor _
ucontrol flag flagSet 0 0 0 0
op add unitNum unitNum 1
op add writerI writerI 1
jump 248 lessThan writerI writerEnd
set @counter _return
set mega unitNum
jump 336 equal pulsarEn 0
set unitNum 0
set firstPulsar null
jump 282 equal pulsar铜 0
set item @copper
set bindNum pulsar铜
op add _return @counter 1
jump 306 always x false
jump 287 equal pulsar铅 0
set item @lead
set bindNum pulsar铅
op add _return @counter 1
jump 306 always x false
jump 292 equal pulsar沙 0
set item @sand
set bindNum pulsar沙
op add _return @counter 1
jump 306 always x false
jump 297 equal pulsar煤 0
set item @coal
set bindNum pulsar煤
op add _return @counter 1
jump 306 always x false
jump 302 equal pulsar废 0
set item @scrap
set bindNum pulsar废
op add _return @counter 1
jump 306 always x false
set bindNum 999999
op add _return @counter 1
jump 308 always x false
jump 335 always x false
sensor itemId item @id
op mul flagSet itemId %00000001
op add writerEnd writerI bindNum
ubind @pulsar
sensor dead firstPulsar @dead
jump 316 equal dead 0
set unitNum 0
jump 335 strictEqual @unit null
set firstPulsar @unit
jump 317 always x false
jump 335 equal @unit firstPulsar
sensor ctd @unit @controlled
jump 321 equal ctd 1
jump 323 equal ctd 0
jump 309 always ctd 0
sensor flag @unit @flag
jump 309 notEqual flag 0
op mod processorI writerI @links
getlink processor processorI
op idiv _ writerI @links
lookup block _ _
sensor _ _ @name
write @unit processor _
ucontrol flag flagSet 0 0 0 0
ucontrol boost 1 0 0 0 0
op add unitNum unitNum 1
op add writerI writerI 1
jump 309 lessThan writerI writerEnd
set @counter _return
set pulsar unitNum
jump 408 equal quasarEn 0
set unitNum 0
set firstQuasar null
jump 344 equal quasar铜 0
set item @copper
set bindNum quasar铜
op add _return @counter 1
jump 378 always x false
jump 349 equal quasar铅 0
set item @lead
set bindNum quasar铅
op add _return @counter 1
jump 378 always x false
jump 354 equal quasar钛 0
set item @titanium
set bindNum quasar钛
op add _return @counter 1
jump 378 always x false
jump 359 equal quasar沙 0
set item @sand
set bindNum quasar沙
op add _return @counter 1
jump 378 always x false
jump 364 equal quasar煤 0
set item @coal
set bindNum quasar煤
op add _return @counter 1
jump 378 always x false
jump 369 equal quasar废 0
set item @scrap
set bindNum quasar废
op add _return @counter 1
jump 378 always x false
jump 374 equal quasar铍 0
set item @beryllium
set bindNum quasar铍
op add _return @counter 1
jump 378 always x false
set bindNum 999999
op add _return @counter 1
jump 380 always x false
jump 407 always x false
sensor itemId item @id
op mul flagSet itemId %00000001
op add writerEnd writerI bindNum
ubind @quasar
sensor dead firstQuasar @dead
jump 388 equal dead 0
set unitNum 0
jump 407 strictEqual @unit null
set firstQuasar @unit
jump 389 always x false
jump 407 equal @unit firstQuasar
sensor ctd @unit @controlled
jump 393 equal ctd 1
jump 395 equal ctd 0
jump 381 always ctd 0
sensor flag @unit @flag
jump 381 notEqual flag 0
op mod processorI writerI @links
getlink processor processorI
op idiv _ writerI @links
lookup block _ _
sensor _ _ @name
write @unit processor _
ucontrol flag flagSet 0 0 0 0
ucontrol boost 1 0 0 0 0
op add unitNum unitNum 1
op add writerI writerI 1
jump 381 lessThan writerI writerEnd
set @counter _return
set quasar unitNum
jump 411 equal forceMode 0
op sub eCore forceMode 1
jump 458 always x false
op add sandOrCoal mono沙 poly沙
op add sandOrCoal sandOrCoal mega沙
op add sandOrCoal sandOrCoal pulsar沙
op add sandOrCoal sandOrCoal quasar沙
op add sandOrCoal sandOrCoal poly煤
op add sandOrCoal sandOrCoal mega煤
op add sandOrCoal sandOrCoal pulsar煤
op add sandOrCoal sandOrCoal quasar煤
jump 422 greaterThan sandOrCoal 0
set eCore 0
jump 458 always sandOrCoal 0
jump 427 equal monoEn 0
ubind firstMono
ulocate building core 0 @copper coreX coreY 0 core
sensor coreT core @type
sensor maxCoreTId coreT @id
jump 433 equal polyEn 0
ubind firstPoly
ulocate building core 0 @copper coreX coreY 0 core
sensor coreT core @type
sensor coreTId coreT @id
op max maxCoreTId maxCoreTId coreTId
jump 439 equal megaEn 0
ubind firstMega
ulocate building core 0 @copper coreX coreY 0 core
sensor coreT core @type
sensor coreTId coreT @id
op max maxCoreTId maxCoreTId coreTId
jump 445 equal pulsarEn 0
ubind firstPulsar
ulocate building core 0 @copper coreX coreY 0 core
sensor coreT core @type
sensor coreTId coreT @id
op max maxCoreTId maxCoreTId coreTId
jump 451 equal quasarEn 0
ubind firstQuasar
ulocate building core 0 @copper coreX coreY 0 core
sensor coreT core @type
sensor coreTId coreT @id
op max maxCoreTId maxCoreTId coreTId
op greaterThan eCore? maxCoreTId 92
jump 456 notEqual eCore? 0
jump 456 notEqual eCore 1
op add eCoreTimes eCoreTimes 1
jump 458 lessThan eCoreTimes 5
set eCoreTimes 0
set eCore eCore?
op add writerEnd writerI @links
op mod processorI writerI @links
getlink processor processorI
op idiv _ writerI @links
write _ processor "readerEnd"
op add writerI writerI 1
jump 459 lessThan writerI writerEnd
set refreshTime @second
jump 53 always writerI writerEnd
end
draw triangle mono poly mega pulsar quasar 0
--------------
主控核心：
set readerI 0
jump 49 lessThanEq readerEnd 0
lookup block readerT readerI
sensor readerN readerT @name
read unit @this readerN
sensor flag unit @flag
jump 20 notEqual flag 0
ubind unit
sensor mining @unit @mining
jump 23 notEqual mining 1
sensor uItN @unit @totalItems
jump 20 greaterThan uItN 5
op div itemId flag %00000001
lookup item item itemId
sensor uIt @unit @firstItem
jump 20 equal uIt item
ulocate ore core true item oreX oreY oreFound 0
ucontrol mine oreX oreY 0 0 0
ucontrol move oreX oreY 0 0 0
ucontrol itemDrop @air 9999 0 0 0
op add readerI readerI 1
jump 2 lessThan readerI readerEnd
set @counter loopEnd
sensor uItN @unit @totalItems
jump 33 notEqual uItN 0
op div itemId flag %00000001
lookup item item itemId
ulocate ore core true item oreX oreY oreFound 0
ucontrol move oreX oreY 0 0 0
ucontrol mine oreX oreY 0 0 0
op add readerI readerI 1
jump 2 lessThan readerI readerEnd
set @counter loopEnd
jump 38 equal uItN 1
ulocate building core 0 @copper coreX coreY coreFound core
ucontrol within coreX coreY 7 withinCore7 0
jump 44 notEqual withinCore7 1
ucontrol itemDrop core 9999 0 0 0
ucontrol itemDrop @air 9999 0 0 0
ulocate ore core true item oreX oreY oreFound 0
ucontrol move oreX oreY 0 0 0
op add readerI readerI 1
jump 2 lessThan readerI readerEnd
set @counter loopEnd
ucontrol approach coreX coreY 5 0 0
op add readerI readerI 1
jump 2 lessThan readerI readerEnd
set @counter loopEnd
set readerI 0
lookup block readerT readerI
sensor readerN readerT @name
read check @this readerN
jump 54 notEqual check null
set @counter loopEnd
sensor flag check @flag
jump 58 notEqual flag 0
ubind check
ucontrol unbind 0 0 0 0 0
write null @this readerN
op add readerI readerI 1
jump 49 lessThan readerI @blockCount
set @counter loopEnd
end
print "兼容e核沙煤:"
set readerI 0
jump 49 lessThanEq readerEnd 0
lookup block readerT readerI
sensor readerN readerT @name
read unit @this readerN
sensor flag unit @flag
jump 110 notEqual flag 0
ubind unit
sensor mining @unit @mining
jump 124 notEqual mining 1
ulocate building core 0 @copper coreX coreY coreFound core
ucontrol within coreX coreY 27 withinCore27 0
jump 91 equal withinCore27 1
sensor uItN @unit @totalItems
jump 87 greaterThan uItN 5
op div itemId flag %00000001
lookup item item itemId
sensor uIt @unit @firstItem
jump 87 equal uIt item
ulocate ore core true item oreX oreY oreFound building
ucontrol mine oreX oreY 0 0 0
ucontrol move oreX oreY 0 0 0
ucontrol itemDrop @air 9999 0 0 0
op add readerI readerI 1
jump 66 lessThan readerI readerEnd
set @counter loopEnd
print "withinCore27: <core>"
sensor uItCap @unit @itemCapacity
op mul uItNThr uItCap 0.85
sensor uItN @unit @totalItems
jump 110 lessThan uItN uItNThr
ulocate building storage 0 @copper storage?X storage?Y storageFound storage?
sensor storage?ItCap storage? @itemCapacity
sensor coreItCap core @itemCapacity
jump 103 equal storage?ItCap coreItCap
sensor hasMissingStorage storage @dead
jump 106 equal hasMissingStorage 0
set missingStorage core
jump 165 always storageDead 1
set storage storage?
set storageX storage?X
set storageY storage?Y
ucontrol within storageX storageY 7 withinStorage7 0
jump 113 equal withinStorage7 1
ucontrol approach storageX storageY 5 0 0
ucontrol mine -1 -1 0 0 0
op add readerI readerI 1
jump 66 lessThan readerI readerEnd
set @counter loopEnd
ucontrol itemDrop storage 9999 0 0 0
ucontrol itemDrop @air 9999 0 0 0
op div itemId flag %00000001
lookup item item itemId
ulocate ore core true item oreX oreY oreFound 0
ucontrol move oreX oreY 0 0 0
ucontrol mine oreX oreY 0 0 0
op add readerI readerI 1
jump 66 lessThan readerI readerEnd
set @counter loopEnd
print "上->mining == 1;  下->mining == 0"
sensor uItN @unit @totalItems
jump 134 notEqual uItN 0
op div itemId flag %00000001
lookup item item itemId
ulocate ore core true item oreX oreY oreFound 0
ucontrol move oreX oreY 0 0 0
ucontrol mine oreX oreY 0 0 0
op add readerI readerI 1
jump 66 lessThan readerI readerEnd
set @counter loopEnd
jump 168 equal uItN 1
ulocate building storage 0 @copper storage?X storage?Y storageFound storage?
ulocate building core 0 @copper coreX coreY coreFound core
sensor storage?ItCap storage? @itemCapacity
sensor coreItCap core @itemCapacity
jump 144 equal storage?ItCap coreItCap
sensor hasMissingStorage storage @dead
jump 147 equal hasMissingStorage 0
set missingStorage core
jump 165 always storageDead 1
set storage storage?
set storageX storage?X
set storageY storage?Y
ucontrol within storageX storageY 7 withinStorage7 0
jump 154 equal withinStorage7 1
ucontrol approach storageX storageY 5 0 0
ucontrol mine -1 -1 5 0 0
op add readerI readerI 1
jump 66 lessThan readerI readerEnd
set @counter loopEnd
ucontrol itemDrop storage 9999 0 0 0
ucontrol itemDrop @air 9999 0 0 0
op div itemId flag %00000001
lookup item item itemId
ulocate ore core true item oreX oreY oreFound 0
ucontrol move oreX oreY 0 0 0
ucontrol mine oreX oreY 0 0 0
op add readerI readerI 1
jump 66 lessThan readerI readerEnd
set @counter loopEnd
ulocate building core 0 @copper coreX coreY coreFound core
ucontrol within coreX coreY 7 withinCore7 0
jump 176 notEqual withinCore7 1
ucontrol itemDrop core 9999 0 0 0
ucontrol itemDrop @air 9999 0 0 0
op div itemId flag %00000001
lookup item item itemId
ulocate ore core true item oreX oreY oreFound 0
ucontrol move oreX oreY 0 0 0
op add readerI readerI 1
jump 66 lessThan readerI readerEnd
set @counter loopEnd
ucontrol approach coreX coreY 5 0 0
op add readerI readerI 1
jump 66 lessThan readerI readerEnd
set @counter loopEnd
end
draw triangle graphite-press multi-press silicon-smelter silicon-crucible kiln plastanium-compressor
draw triangle phase-weaver cryofluid-mixer pyratite-mixer blast-mixer melter separator
draw triangle disassembler spore-press pulverizer coal-centrifuge incinerator copper-wall
draw triangle copper-wall-large titanium-wall titanium-wall-large plastanium-wall plastanium-wall-large thorium-wall
draw triangle thorium-wall-large phase-wall phase-wall-large surge-wall surge-wall-large door
draw triangle door-large scrap-wall scrap-wall-large scrap-wall-huge scrap-wall-gigantic mender
draw triangle mend-projector overdrive-projector overdrive-dome force-projector shock-mine conveyor
draw triangle titanium-conveyor plastanium-conveyor armored-conveyor junction bridge-conveyor phase-conveyor
draw triangle sorter inverted-sorter router distributor overflow-gate underflow-gate
draw triangle mass-driver duct duct-router duct-bridge mechanical-pump rotary-pump
draw triangle conduit pulse-conduit plated-conduit liquid-router liquid-tank liquid-junction
draw triangle bridge-conduit phase-conduit power-node power-node-large surge-tower diode
draw triangle battery battery-large combustion-generator thermal-generator steam-generator differential-generator
draw triangle rtg-generator solar-panel solar-panel-large thorium-reactor impact-reactor mechanical-drill
draw triangle pneumatic-drill laser-drill blast-drill water-extractor cultivator oil-extractor
draw triangle core-shard core-foundation core-nucleus vault container unloader
draw triangle duo scatter scorch hail wave lancer
draw triangle arc parallax swarmer salvo segment tsunami
draw triangle fuse ripple cyclone foreshadow spectre meltdown
draw triangle command-center ground-factory air-factory naval-factory additive-reconstructor multiplicative-reconstructor
draw triangle exponential-reconstructor tetrative-reconstructor repair-point repair-turret payload-conveyor payload-router
draw triangle power-source power-void item-source item-void liquid-source liquid-void
draw triangle payload-void payload-source illuminator launch-pad interplanetary-accelerator message
draw triangle switch micro-processor logic-processor hyper-processor memory-cell memory-bank
draw triangle logic-display large-logic-display liquid-container deconstructor constructor thruster
draw triangle large-constructor payload-loader payload-unloader silicon-arc-furnace cliff-crusher plasma-bore
draw triangle reinforced-liquid-junction breach core-bastion turbine-condenser beam-node beam-tower
draw triangle build-tower impact-drill carbide-crucible surge-conveyor duct-unloader surge-router
draw triangle reinforced-conduit reinforced-liquid-router reinforced-liquid-container reinforced-liquid-tank reinforced-bridge-conduit core-citadel
draw triangle core-acropolis heat-reactor impulse-pump reinforced-pump electrolyzer oxidation-chamber
draw triangle surge-smelter surge-crucible overflow-duct large-plasma-bore cyanogen-synthesizer slag-centrifuge
draw triangle electric-heater slag-incinerator phase-synthesizer sublimate reinforced-container reinforced-vault
draw triangle atmospheric-concentrator unit-cargo-loader unit-cargo-unload-point chemical-combustion-chamber pyrolysis-generator regen-projector
draw triangle titan small-deconstructor vent-condenser phase-heater heat-redirector tungsten-wall
draw triangle tungsten-wall-large tank-assembler beryllium-wall beryllium-wall-large eruption-drill ship-assembler
draw triangle mech-assembler shield-projector beam-link world-processor reinforced-payload-conveyor reinforced-payload-router
draw triangle disperse large-shield-projector payload-mass-driver world-cell carbide-wall carbide-wall-large
draw triangle tank-fabricator mech-fabricator ship-fabricator reinforced-surge-wall radar blast-door
draw triangle canvas armored-duct unit-repair-tower diffuse prime-refabricator basic-assembler-module
draw triangle reinforced-surge-wall-large tank-refabricator mech-refabricator ship-refabricator slag-heater afflict
draw triangle shielded-wall lustre scathe smite underflow-duct malign
draw triangle shockwave-tower heat-source flux-reactor neoplasia-reactor heat-router large-payload-mass-driver
draw triangle reinforced-message world-message world-switch small-heat-redirector large-cliff-crusher advanced-launch-pad
draw triangle landing-pad 0 0 0 0 0
至于运行原理，请你自行探索。
-----------------------------

------------------------
这是一个比较久远的逻辑，通过控制单，向逻辑连接的建筑中自动放置物品，即使用了远古的打表手段，比现在的技术手段来说，效率低下，但还是有很高的研究价值。
print "小撒的搬运豆2.2.2"
print "单位数量可选范围[1-9]"
set 单位数量 1
set 物品数量下限 100
set 单位造价倍率 1
set 建筑造价倍率 1
ubind 首选单位
print "首选单位会替换单位种类1"
set 单位种类1 @flare
set 单位种类2 @mono
set 单位种类3 @poly
set 单位种类4 @mega
set 大超速特化 1
set 搬运布特化 1
print "2023 01 30"
print "始于2020寒假"
print "呜，三年了欸"
print "现支持所有兵厂+布热+立场+超速"
print "连接分类器/装卸器指定物品且不解绑"
print "2.1版本优化了查表速率，现在可以控更多兵啦（来自枕头的方法"
print "2.1版本修复了某些情况下不会运玻璃的bug"
print "2.1.3 版本文辞优化了构筑器体验"
print "2.1.4 版本文辞添加了建筑造价倍率和单位造价倍率"
print "2.1.5 恢复支持超速，添加自动选单位"
sensor 首选单位type @unit @type
jump 27 equal 首选单位type null
set 单位种类1 首选单位type
set 切换单位种类时间间隔 5000
set 常数时间 99999999999999
set 切换单位标记位 0
op add 切换单位种类time @time 常数时间
op mul 指针跳转 单位种类指针 2
op add @counter @counter 指针跳转
set 单位type 单位种类1
jump 40 always x false
set 单位type 单位种类2
jump 40 always x false
set 单位type 单位种类3
jump 40 always x false
set 单位type 单位种类4
op add 单位种类指针 单位种类指针 1
op mod 单位种类指针 单位种类指针 4
ubind 单位type
sensor type @unit @type
jump 29 equal type null
jump 189 notEqual 初始化完成标记位 null
set 初始化完成标记位 1
ulocate building core 0 @copper corex corey found core
op mul flag @thisx 1000
op add flag @thisy flag
op mul flag 100 flag
op add flag1 1 flag
op add flag2 2 flag
op add flag3 3 flag
op add flag4 4 flag
op add flag5 5 flag
op add flag6 6 flag
op add flag7 7 flag
op add flag8 8 flag
op add flag9 9 flag
set 单位循环 -1
set 建筑循环 -1
set 铜 @copper
set 铅 @lead
set 玻璃 @metaglass
set 石墨 @graphite
set 沙 @sand
set 煤 @coal
set 钛 @titanium
set 钍 @thorium
set 硅 @silicon
set 塑钢 @plastanium
set 布 @phase-fabric
set 合金 @surge-alloy
set 铍 @beryllium
set 钨 @tungsten
set 氧化铍 @oxide
set 碳化钨 @carbide
jump 115 greaterThan 过期时间 @time
sensor 单位标记 xs1 @flag
jump 83 notEqual 单位标记 flag1
ubind xs1
ucontrol flag 0 0 0 0 0
sensor 单位标记 xs2 @flag
jump 87 notEqual 单位标记 flag2
ubind xs2
ucontrol flag 0 0 0 0 0
sensor 单位标记 xs3 @flag
jump 91 notEqual 单位标记 flag3
ubind xs3
ucontrol flag 0 0 0 0 0
sensor 单位标记 xs4 @flag
jump 95 notEqual 单位标记 flag4
ubind xs4
ucontrol flag 0 0 0 0 0
sensor 单位标记 xs5 @flag
jump 99 notEqual 单位标记 flag5
ubind xs5
ucontrol flag 0 0 0 0 0
sensor 单位标记 xs6 @flag
jump 103 notEqual 单位标记 flag6
ubind xs6
ucontrol flag 0 0 0 0 0
sensor 单位标记 xs7 @flag
jump 107 notEqual 单位标记 flag7
ubind xs7
ucontrol flag 0 0 0 0 0
sensor 单位标记 xs8 @flag
jump 111 notEqual 单位标记 flag8
ubind xs8
ucontrol flag 0 0 0 0 0
sensor 单位标记 xs9 @flag
jump 115 notEqual 单位标记 flag9
ubind xs9
ucontrol flag 0 0 0 0 0
op add 单位循环 单位循环 1
op mod 单位循环 单位循环 单位数量
op mul 单位循环跳转 单位循环 6
op add @counter @counter 单位循环跳转
ubind xs1
set xsflag flag1
set 建筑 建筑1
set 建筑容量 建筑容量1
set 建筑需求种类 建筑需求种类1
jump 172 always x false
ubind xs2
set xsflag flag2
set 建筑 建筑2
set 建筑容量 建筑容量2
set 建筑需求种类 建筑需求种类2
jump 172 always x false
ubind xs3
set xsflag flag3
set 建筑 建筑3
set 建筑容量 建筑容量3
set 建筑需求种类 建筑需求种类3
jump 172 always x false
ubind xs4
set xsflag flag4
set 建筑 建筑4
set 建筑容量 建筑容量4
set 建筑需求种类 建筑需求种类4
jump 172 always x false
ubind xs5
set xsflag flag5
set 建筑 建筑5
set 建筑容量 建筑容量5
set 建筑需求种类 建筑需求种类5
jump 172 always x false
ubind xs6
set xsflag flag6
set 建筑 建筑6
set 建筑容量 建筑容量6
set 建筑需求种类 建筑需求种类6
jump 172 always x false
ubind xs7
set xsflag flag7
set 建筑 建筑7
set 建筑容量 建筑容量7
set 建筑需求种类 建筑需求种类7
jump 172 always x false
ubind xs8
set xsflag flag8
set 建筑 建筑8
set 建筑容量 建筑容量8
set 建筑需求种类 建筑需求种类8
jump 172 always x false
ubind xs9
set xsflag flag9
set 建筑 建筑9
set 建筑容量 建筑容量9
set 建筑需求种类 建筑需求种类9
jump 240 equal 建筑需求种类 0
sensor 建筑状态 建筑 @dead
jump 240 equal 建筑状态 1
sensor 建筑已有物品 建筑 建筑需求种类
op sub 建筑需求数量 建筑容量 建筑已有物品
jump 240 lessThanEq 建筑需求数量 0
jump 181 notEqual 建筑需求种类 @phase-fabric
jump 181 equal 搬运布特化 0
op sub 建筑需求数量 建筑容量 0
op add 过期时间 @time 5000
sensor 单位状态 @unit @dead
jump 189 equal 单位状态 1
sensor 单位标记 @unit @flag
jump 221 equal 单位标记 xsflag
jump 220 equal 单位标记 0
sensor 单位状态 @unit @controlled
jump 220 equal 单位状态 0
ubind type
jump 29 lessThan 切换单位种类time @time
jump 194 equal 切换单位标记位 1
op add 切换单位种类time @time 切换单位种类时间间隔
set 切换单位标记位 1
sensor 单位标记 @unit @flag
jump 199 equal 单位标记 xsflag
jump 199 equal 单位标记 0
sensor 单位状态 @unit @controlled
jump 78 notEqual 单位状态 0
op mul 单位获取跳转 单位循环 2
op add 切换单位种类time @time 常数时间
set 切换单位标记位 0
op add @counter @counter 单位获取跳转
set xs1 @unit
jump 220 always x false
set xs2 @unit
jump 220 always x false
set xs3 @unit
jump 220 always x false
set xs4 @unit
jump 220 always x false
set xs5 @unit
jump 220 always x false
set xs6 @unit
jump 220 always x false
set xs7 @unit
jump 220 always x false
set xs8 @unit
jump 220 always x false
set xs9 @unit
ucontrol flag xsflag 0 0 0 0
sensor 单位背包数量 @unit 建筑需求种类
jump 231 greaterThan 单位背包数量 0
ulocate building core 0 @copper corex corey found core
ucontrol boost 1 0 0 0 0
ucontrol move corex corey 0 0 0
ucontrol itemDrop core 9999 0 0 0
ucontrol itemTake core 建筑需求种类 建筑需求数量 0 0
sensor 单位背包数量 @unit 建筑需求种类
jump 231 greaterThan 单位背包数量 0
jump 78 equal 执行结束 0
sensor x 建筑 @x
ucontrol boost 1 0 0 0 0
sensor y 建筑 @y
ucontrol move x y 0 0 0
ucontrol itemDrop 建筑 9999 0 0 0
sensor 单位背包数量 @unit 建筑需求种类
jump 223 lessThanEq 单位背包数量 0
jump 78 equal 执行结束 0
print "获取需求"
op add 建筑循环 建筑循环 1
op mod 建筑循环 建筑循环 @links
getlink 建筑 建筑循环
sensor 建筑容量 建筑 @itemCapacity
jump 517 lessThan 建筑容量 10
sensor 建筑需求种类 unloader1 @config
jump 479 notEqual 建筑需求种类 0
sensor 建筑需求种类 sorter1 @config
jump 479 notEqual 建筑需求种类 0
print "查表"
sensor 兵种 建筑 @config
jump 310 equal 兵种 null
jump 260 notEqual 兵种 @dagger
set 物品种类数目 2
set 物品1 铅
op mul 数量1 40 单位造价倍率
set 物品2 硅
op mul 数量2 60 单位造价倍率
jump 453 equal 查表完成 null
print "新星"
jump 270 notEqual 兵种 @nova
set 物品种类数目 3
set 物品1 铅
op mul 数量1 40 单位造价倍率
set 物品2 硅
op mul 数量2 60 单位造价倍率
set 物品3 钛
op mul 数量3 40 单位造价倍率
jump 453 equal 查表完成 null
print "苦力怕"
jump 278 notEqual 兵种 @crawler
set 物品种类数目 2
set 物品1 硅
op mul 数量1 60 单位造价倍率
set 物品2 煤
op mul 数量2 20 单位造价倍率
jump 453 equal 查表完成 null
print "星辉"
jump 284 notEqual 兵种 @flare
set 物品种类数目 1
set 物品1 硅
op mul 数量1 60 单位造价倍率
jump 453 equal 查表完成 null
print "矿机"
jump 292 notEqual 兵种 @mono
set 物品种类数目 2
set 物品1 硅
op mul 数量1 60 单位造价倍率
set 物品2 铅
op mul 数量2 30 单位造价倍率
jump 453 equal 查表完成 null
print "梭鱼"
jump 300 notEqual 兵种 @risso
set 物品种类数目 2
set 物品1 硅
op mul 数量1 40 单位造价倍率
set 物品2 玻璃
op mul 数量2 70 单位造价倍率
jump 453 equal 查表完成 null
print "潜螺"
jump 310 notEqual 兵种 @retusa
set 物品种类数目 3
set 物品1 硅
op mul 数量1 40 单位造价倍率
set 物品2 玻璃
op mul 数量2 70 单位造价倍率
set 物品3 钛
op mul 数量3 40 单位造价倍率
jump 453 equal 查表完成 null
jump 517 equal 查无此人 null
sensor 建筑大小 建筑 @size
sensor 建筑种类 建筑 @type
jump 412 greaterThan 建筑大小 3
print "T2"
jump 322 notEqual 建筑种类 @additive-reconstructor
set 物品种类数目 2
set 物品1 硅
op mul 数量1 80 单位造价倍率
set 物品2 石墨
op mul 数量2 80 单位造价倍率
jump 453 equal 查表完成 null
print "坦克-T1"
jump 330 notEqual 建筑种类 @tank-fabricator
set 物品种类数目 2
set 物品1 硅
op mul 数量1 100 单位造价倍率
set 物品2 铍
op mul 数量2 80 单位造价倍率
jump 453 equal 查表完成 null
print "飞船-T1"
jump 338 notEqual 建筑种类 @ship-fabricator
set 物品种类数目 2
set 物品1 硅
op mul 数量1 140 单位造价倍率
set 物品2 石墨
op mul 数量2 100 单位造价倍率
jump 453 equal 查表完成 null
print "机甲-T1"
jump 346 notEqual 建筑种类 @mech-fabricator
set 物品种类数目 2
set 物品1 硅
op mul 数量1 140 单位造价倍率
set 物品2 铍
op mul 数量2 100 单位造价倍率
jump 453 equal 查表完成 null
print "坦克-T2"
jump 354 notEqual 建筑种类 @tank-refabricator
set 物品种类数目 2
set 物品1 硅
op mul 数量1 80 单位造价倍率
set 物品2 钨
op mul 数量2 60 单位造价倍率
jump 453 equal 查表完成 null
print "机甲-T2"
jump 362 notEqual 建筑种类 @mech-refabricator
set 物品种类数目 2
set 物品1 硅
op mul 数量1 100 单位造价倍率
set 物品2 钨
op mul 数量2 80 单位造价倍率
jump 453 equal 查表完成 null
print "飞船-T2"
jump 373 notEqual 建筑种类 @ship-refabricator
set 物品种类数目 2
set 物品1 硅
op mul 数量1 120 单位造价倍率
set 物品2 钨
op mul 数量2 80 单位造价倍率
jump 453 equal 查表完成 null
print "小超速"
print "布热"
print "力墙"
print "修复"
jump 377 equal 建筑种类 @mend-projector
jump 377 equal 建筑种类 @force-projector
jump 377 equal 建筑种类 @phase-heater
jump 382 notEqual 建筑种类 @overdrive-projector
set 物品种类数目 1
set 物品1 布
set 数量1 10
jump 453 equal 查表完成 null
print "大超速"
jump 391 notEqual 建筑种类 @overdrive-dome
jump 518 equal 大超速特化 1
set 物品种类数目 2
set 物品1 布
set 数量1 10
set 物品2 硅
set 数量2 10
jump 453 equal 查表完成 null
print "构筑器"
jump 410 notEqual 建筑种类 @constructor
sensor 构筑器设置 建筑 @config
jump 398 notEqual 构筑器设置 @beryllium-wall-large
set 物品种类数目 1
set 物品1 铍
op mul 数量1 48 建筑造价倍率
jump 453 equal 查表完成 null
jump 403 notEqual 构筑器设置 @tungsten-wall-large
set 物品种类数目 1
set 物品1 钨
op mul 数量1 48 建筑造价倍率
jump 453 equal 查表完成 null
jump 410 notEqual 构筑器设置 @carbide-wall-large
set 物品种类数目 2
set 物品1 钍
op mul 数量1 48 建筑造价倍率
set 物品2 碳化钨
op mul 数量2 48 建筑造价倍率
jump 453 equal 查表完成 null
jump 517 equal 查无此人 null
print "T3"
jump 422 notEqual 建筑种类 @multiplicative-reconstructor
set 物品种类数目 3
set 物品1 硅
op mul 数量1 260 单位造价倍率
set 物品2 钛
op mul 数量2 160 单位造价倍率
set 物品3 玻璃
op mul 数量3 80 单位造价倍率
jump 453 equal 查表完成 null
print "s星重构厂"
jump 430 notEqual 建筑种类 @prime-refabricator
set 物品种类数目 2
set 物品1 硅
op mul 数量1 200 单位造价倍率
set 物品2 钍
op mul 数量2 160 单位造价倍率
jump 453 equal 查表完成 null
print "T4"
jump 440 notEqual 建筑种类 @exponential-reconstructor
set 物品种类数目 3
set 物品1 硅
op mul 数量1 1700 单位造价倍率
set 物品2 钛
op mul 数量2 1500 单位造价倍率
set 物品3 塑钢
op mul 数量3 1300 单位造价倍率
jump 453 equal 查表完成 null
print "T5"
jump 451 notEqual 建筑种类 @tetrative-reconstructor
set 物品种类数目 4
set 物品1 硅
op mul 数量1 2000 单位造价倍率
set 物品2 合金
op mul 数量2 1000 单位造价倍率
set 物品3 塑钢
op mul 数量3 1200 单位造价倍率
set 物品4 布
op mul 数量4 700 单位造价倍率
jump 453 equal 查表完成 null
jump 517 equal 查无此人 null
print "选择物品"
op rand 物品循环 物品种类数目 b
op idiv 物品循环 物品循环 1
set 物品循环计数 0
op add 物品循环 物品循环 1
op mod 物品循环 物品循环 物品种类数目
op add 物品循环计数 物品循环计数 1
jump 517 greaterThan 物品循环计数 物品种类数目
op mul 物品循环跳转 物品循环 3
op add @counter @counter 物品循环跳转
set 建筑容量 数量1
set 建筑需求种类 物品1
jump 473 always 选取完成 13
set 建筑容量 数量2
set 建筑需求种类 物品2
jump 473 always 选取完成 13
set 建筑容量 数量3
set 建筑需求种类 物品3
jump 473 always 选取完成 13
set 建筑容量 数量4
set 建筑需求种类 物品4
jump 456 lessThanEq 建筑容量 0
sensor 核心物品数量 core 建筑需求种类
jump 456 lessThanEq 核心物品数量 物品数量下限
sensor 建筑已有物品 建筑 建筑需求种类
jump 456 greaterThanEq 建筑已有物品 建筑容量
print "选择物品"
op mul 建筑需求跳转 单位循环 4
op add @counter @counter 建筑需求跳转
set 建筑1 建筑
set 建筑需求种类1 建筑需求种类
set 建筑容量1 建筑容量
jump 516 always 获取需求成功 0
set 建筑2 建筑
set 建筑需求种类2 建筑需求种类
set 建筑容量2 建筑容量
jump 516 always 获取需求成功 0
set 建筑3 建筑
set 建筑需求种类3 建筑需求种类
set 建筑容量3 建筑容量
jump 516 always 获取需求成功 0
set 建筑4 建筑
set 建筑需求种类4 建筑需求种类
set 建筑容量4 建筑容量
jump 516 always 获取需求成功 0
set 建筑5 建筑
set 建筑需求种类5 建筑需求种类
set 建筑容量5 建筑容量
jump 516 always 获取需求成功 0
set 建筑6 建筑
set 建筑需求种类6 建筑需求种类
set 建筑容量6 建筑容量
jump 516 always 获取需求成功 0
set 建筑7 建筑
set 建筑需求种类7 建筑需求种类
set 建筑容量7 建筑容量
jump 516 always 获取需求成功 0
set 建筑8 建筑
set 建筑需求种类8 建筑需求种类
set 建筑容量8 建筑容量
jump 516 always 获取需求成功 0
set 建筑9 建筑
set 建筑需求种类9 建筑需求种类
set 建筑容量9 建筑容量
jump 181 equal 获取需求成功 0
jump 78 equal 获取需求失败 0
set 大超速 建筑
sensor 大超速硅 大超速 @silicon
sensor 大超速布 大超速 @phase-fabric
set 建筑需求种类 @silicon
op sub 建筑需求数量 10 大超速硅
jump 526 lessThanEq 大超速硅 大超速布
set 建筑需求种类 @phase-fabric
op sub 建筑需求数量 10 大超速布
jump 181 equal 获取需求成功 0
至于运行原理，请你自行探索。
------------------------


现在的打表手段是，将建筑相关的数据直接存在变量名字这个变量里边，然后通过look up+read进行读取
以下是一个获取建筑需求的了逻辑，一表示无，丁表示有
set bdi 1
getlink bd bdi
sensor type bd @type
sensor id type @id
read copper "一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一丁一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一丁" id
read lead "一一一一丁一一一丁一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一丁一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一丁" id
read metaglass "一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一丁" id
read graphite "一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一丁一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一丁一一一一一一一一一一丁一一一一一一一一一一一一一一一一一一一丁一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一丁一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一丁" id
read sand "一一丁丁丁一丁一丁一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一丁一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一丁一一丁" id
read coal "丁丁丁丁一一一一丁" id
read titanium "一一一一一丁一丁一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一丁丁一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一丁" id
read thorium "一一一一一一丁一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一丁一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一丁一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一丁一一一一一一一一一一一一丁一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一丁" id
read scrap "一一一一一一一一一一丁一丁一丁" id
read silicon "一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一丁一一丁一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一丁丁丁丁丁丁丁一一一一一一一一一一一一一一丁一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一丁丁一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一丁丁丁一一一一一一一丁一一丁丁丁" id
read plastanium "一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一丁丁" id
read phase-fabric "一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一丁丁丁丁一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一丁一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一丁一一一丁一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一丁" id
read surge-alloy "一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一丁一一一一一一一一一丁一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一丁" id
read spore-pod "一一一一一一一一一丁一一一丁" id
read blast-compound "一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一丁" id
read pyratite "一一一一一一一一一丁" id
read beryllium "一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一丁一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一丁丁" id
read tungsten "一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一丁一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一丁丁丁" id
printchar type
set i 0
lookup item item i
sensor name item @name
set need 0
read need @this name
jump 30 notEqual need 19969
printchar item
op add i i 1
jump 24 lessThan i @itemCount
wait 0.5
op add bdi bdi 1
print "\n"
jump 1 lessThan bdi @links
printflush 


我们可以对它进行升级，升级一下就可以得到以下逻辑
jump 95 equal init 1
print "▼单位类型"
set unitT @flare
printflush ▲请回▲
op mul flag @thisy @mapw
op add flag flag @thisx
op add dagger @counter 1
jump 10 always x false
set lead 19969
jump 95 always x false
op add crawler @counter 1
jump 14 always x false
set coal 19969
jump 95 always x false
op add nova @counter 1
jump 19 always x false
set lead 19969
set titanium 19969
jump 95 always x false
op add mono @counter 1
jump 23 always x false
set lead 19969
jump 95 always x false
op add risso @counter 1
jump 27 always x false
set metaglass 19969
jump 95 always x false
op add retusa @counter 1
jump 31 always x false
set titanium 19969
jump 95 always x false
op add tungsten-wall-large @counter 1
jump 35 always x false
set tungsten 19969
jump 95 always x false
op add beryllium-wall-large @counter 2
op add beam-node @counter 1
jump 40 always x false
set beryllium 19969
jump 95 always x false
op add carbide-wall-large @counter 1
jump 45 always x false
set thorium 19969
set carbide 19969
jump 95 always x false
op add reinforced-surge-wall-large @counter 1
jump 50 always x false
set surge-alloy 19969
set tungsten 19969
jump 95 always x false
op add reinforced-liquid-container @counter 1
jump 55 always x false
set beryllium 19969
set tungsten 19969
jump 95 always x false
op add reinforced-container @counter 1
jump 60 always x false
set graphite 19969
set tungsten 19969
jump 95 always x false
set init 1
print "[acid]建筑物品选择逻辑-需求识别逻辑[] |v1 |by [scarlet]a[][lime]a[][blue]a[]\n链接所选建筑，自动识别需求\n除大型构筑器外全支持，选择炮塔当前弹药\n电弧选中主逻辑\n"
control enabled arc1 0 0 0 0
set bdi 2
set list 0
jump 69 lessThan bdi @links
print "0"
printflush message1
jump 61 always x false
getlink bd bdi
sensor type bd @type
sensor id type @id
read copper "一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一丁一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一丁" id
read lead "一一一一丁一一一丁一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一丁一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一丁" id
read metaglass "一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一丁" id
read graphite "一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一丁一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一丁一一一一一一一一一一丁一一一一一一一一一一一一一一一一一一一丁一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一丁一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一丁" id
read sand "一一丁丁丁一丁一丁一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一丁一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一丁一一丁" id
read coal "丁丁丁丁一一一一丁" id
read titanium "一一一一一丁一丁一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一丁丁一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一丁" id
read thorium "一一一一一一丁一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一丁一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一丁一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一丁一一一一一一一一一一一一丁一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一丁" id
read scrap "一一一一一一一一一一丁一丁一丁" id
read silicon "一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一丁一一丁一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一丁丁丁丁丁丁丁一一一一一一一一一一一一一一丁一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一丁丁一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一丁丁丁一一一一一一一丁一一丁丁丁" id
read plastanium "一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一丁丁" id
read phase-fabric "一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一丁丁丁丁一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一丁一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一丁一一一丁一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一丁" id
read surge-alloy "一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一丁一一一一一一一一一丁一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一丁" id
read spore-pod "一一一一一一一一一丁一一一丁" id
read blast-compound "一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一丁" id
read pyratite "一一一丁一一一一一丁一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一丁" id
read beryllium "一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一丁一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一丁丁" id
read tungsten "一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一丁一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一一丁丁丁" id
read oxide "" id
read carbide "" id
sensor config bd @config
sensor configName config @name
read @counter @this configName
sensor ammoT bd @currentAmmoType
sensor ammoTN ammoT @name
write 19969 @this ammoTN
printchar type
printchar config
set i 0
lookup item item i
sensor name item @name
set need 0
read need @this name
jump 109 notEqual need 19969
printchar item
op shl mask 1 i
op or list list mask
op add i i 1
jump 101 lessThan i @itemCount
print "\n"
op add bdi bdi 1
jump 69 lessThan bdi @links
op shl list? list 3
print "{0}."
format list?
printflush message1
op shl list list 1
sensor dead mainLogic @dead
jump 127 notEqual dead 0
jump 147 strictEqual arc1 null
sensor shootX arc1 @shootX
jump 128 notEqual shootX mainLogicX
sensor shootY arc1 @shootY
jump 128 notEqual shootY mainLogicY
jump 147 always dead 0
jump 130 strictEqual arc1 null
sensor mainLogicX arc1 @shootX
sensor mainLogicY arc1 @shootY
ubind unitT
sensor ctd @unit @controlled
jump 136 equal ctd 0
sensor flagCheck @unit @flag
jump 136 equal flagCheck 0
jump 130 notEqual flagCheck flag
ucontrol flag flag 0 0 0 0
ucontrol move mainLogicX mainLogicY 0 0 0
ucontrol getBlock mainLogicX mainLogicY checkT mainLogic 0
jump 143 notEqual checkT null
sensor uDead @unit @dead
jump 130 equal uDead 1
jump 131 always uDead 0
sensor ctr @unit @controller
jump 148 notEqual ctr @this
ucontrol unbind 0 0 0 0 0
jump 148 always x false
jump 61 equal list lastList
write list mainLogic "itemList"
read counter mainLogic ":介绍"
write counter mainLogic "@counter"
set lastList list
jump 61 always x false

有这个逻辑不够，还需要配合其他逻辑使用
print "配置代码，请在=右边粘贴(复制时没有末尾的点可能不完全)"
set configCode 0
print "▼阈值[0,1](选最少->大于则关/选最多->小于则关)"
set threshold 0.3
print "▼远程容器模式(0->关闭/1->远程核心/2->指定坐标)"
set remote 0
print "▼2->远程容器坐标"
set remoteX 166
set remoteY 39
print "▼2->用于获取建筑的一次性单位"
set remoteUnit @flare
printflush 请回
op shr itemList configCode 3
op shl itemList itemList 1
op and running configCode 0b100
op shr running running 2
op and controlAllBuT configCode 0b10
op shr controlAllBuT controlAllBuT 1
op and reversed configCode 0b1
op log log2 2 b
op mul flag @thisy @mapw
op add flag flag @thisx
set :介绍 @counter
print "[acid]建筑物品选择逻辑[] |v4 |by [scarlet]a[][lime]a[][blue]a[]\n用于等的自动控制\n逻辑里面有更多配置\n"
jump 27 notEqual remote 0
print "模式：链接容器\n"
jump 37 always x false
jump 30 notEqual remote 1
print "模式：远程核心\n"
jump 37 always x false
jump 35 notEqual remote 2
print "模式：远程容器({0},{0})\n"
format remoteX
format remoteY
jump 37 always x false
print "模式：[scarlet]错误[]\n"
end
sensor _ sorter1 @type
jump 42 equal _ @sorter
print "[scarlet][] 未找到"
printflush message1
set @counter :介绍
sensor _ sorter2 @type
jump 47 equal _ @inverted-sorter
print "[scarlet][] 未找到"
printflush message1
set @counter :介绍
op and jstep itemList 0b111110
op add @counter @counter jstep
print "\ns星一般物品 |物品清单\n|[grey][]\n"
jump 112 always 0 0
print "\ns星一般物品 |物品清单\n|[grey][]\n"
jump 112 always 0 0
print "\ns星一般物品 |物品清单\n|[grey][][grey][]\n"
jump 112 always 0 0
print "\ns星一般物品 |物品清单\n|[grey][]\n"
jump 112 always 0 0
print "\ns星一般物品 |物品清单\n|[grey][][grey][]\n"
jump 112 always 0 0
print "\ns星一般物品 |物品清单\n|[grey][][grey][]\n"
jump 112 always 0 0
print "\ns星一般物品 |物品清单\n|[grey][][grey][]\n"
jump 112 always 0 0
print "\ns星一般物品 |物品清单\n|[grey][]\n"
jump 112 always 0 0
print "\ns星一般物品 |物品清单\n|[grey][][grey][]\n"
jump 112 always 0 0
print "\ns星一般物品 |物品清单\n|[grey][][grey][]\n"
jump 112 always 0 0
print "\ns星一般物品 |物品清单\n|[grey][][grey][][grey][]\n"
jump 112 always 0 0
print "\ns星一般物品 |物品清单\n|[grey][][grey][]\n"
jump 112 always 0 0
print "\ns星一般物品 |物品清单\n|[grey][][grey][]\n"
jump 112 always 0 0
print "\ns星一般物品 |物品清单\n|[grey][][grey][]\n"
jump 112 always 0 0
print "\ns星一般物品 |物品清单\n|[grey][][grey][]\n"
jump 112 always 0 0
print "\ns星一般物品 |物品清单\n|[grey][]\n"
jump 112 always 0 0
print "\ns星一般物品 |物品清单\n|[grey][]\n"
jump 112 always 0 0
print "\ns星一般物品 |物品清单\n|[grey][]\n"
jump 112 always 0 0
print "\ns星一般物品 |物品清单\n|[grey][][grey][]\n"
jump 112 always 0 0
print "\ns星一般物品 |物品清单\n|[grey][]\n"
jump 112 always 0 0
print "\ns星一般物品 |物品清单\n|[grey][][grey][]\n"
jump 112 always 0 0
print "\ns星一般物品 |物品清单\n|[grey][][grey][]\n"
jump 112 always 0 0
print "\ns星一般物品 |物品清单\n|[grey][][grey][]\n"
jump 112 always 0 0
print "\ns星一般物品 |物品清单\n|[grey][]\n"
jump 112 always 0 0
print "\ns星一般物品 |物品清单\n|[grey][]\n"
jump 112 always 0 0
print "\ns星一般物品 |物品清单\n|[grey][]\n"
jump 112 always 0 0
print "\ns星一般物品 |物品清单\n|[grey][][grey][]\n"
jump 112 always 0 0
print "\ns星一般物品 |物品清单\n|[grey][]\n"
jump 112 always 0 0
print "\ns星一般物品 |物品清单\n|[grey][]\n"
jump 112 always 0 0
print "\ns星一般物品 |物品清单\n|[grey][]\n"
jump 112 always 0 0
print "\ns星一般物品 |物品清单\n|[grey][]\n"
jump 112 always 0 0
print "\ns星一般物品 |物品清单\n|\n"
op shr _ itemList 5
op and jstep _ 0b111110
op add @counter @counter jstep
print "|[grey][]\n"
jump 178 always 0 0
print "|[grey][]\n"
jump 178 always 0 0
print "|[grey][][grey][]\n"
jump 178 always 0 0
print "|[grey][]\n"
jump 178 always 0 0
print "|[grey][][grey][]\n"
jump 178 always 0 0
print "|[grey][][grey][]\n"
jump 178 always 0 0
print "|[grey][][grey][]\n"
jump 178 always 0 0
print "|[grey][]\n"
jump 178 always 0 0
print "|[grey][][grey][]\n"
jump 178 always 0 0
print "|[grey][][grey][]\n"
jump 178 always 0 0
print "|[grey][][grey][][grey][]\n"
jump 178 always 0 0
print "|[grey][][grey][]\n"
jump 178 always 0 0
print "|[grey][][grey][]\n"
jump 178 always 0 0
print "|[grey][][grey][]\n"
jump 178 always 0 0
print "|[grey][][grey][]\n"
jump 178 always 0 0
print "|[grey][]\n"
jump 178 always 0 0
print "|[grey][]\n"
jump 178 always 0 0
print "|[grey][]\n"
jump 178 always 0 0
print "|[grey][][grey][]\n"
jump 178 always 0 0
print "|[grey][]\n"
jump 178 always 0 0
print "|[grey][][grey][]\n"
jump 178 always 0 0
print "|[grey][][grey][]\n"
jump 178 always 0 0
print "|[grey][][grey][]\n"
jump 178 always 0 0
print "|[grey][]\n"
jump 178 always 0 0
print "|[grey][]\n"
jump 178 always 0 0
print "|[grey][]\n"
jump 178 always 0 0
print "|[grey][][grey][]\n"
jump 178 always 0 0
print "|[grey][]\n"
jump 178 always 0 0
print "|[grey][]\n"
jump 178 always 0 0
print "|[grey][]\n"
jump 178 always 0 0
print "|[grey][]\n"
jump 178 always 0 0
print "|\n"
op shr _ itemList 10
op and jstep _ 0b111110
op add @counter @counter jstep
print "|[grey][]\n"
jump 244 always 0 0
print "|[grey][]\n"
jump 244 always 0 0
print "|[grey][][grey][]\n"
jump 244 always 0 0
print "|[grey][]\n"
jump 244 always 0 0
print "|[grey][][grey][]\n"
jump 244 always 0 0
print "|[grey][][grey][]\n"
jump 244 always 0 0
print "|[grey][][grey][]\n"
jump 244 always 0 0
print "|[grey][]\n"
jump 244 always 0 0
print "|[grey][][grey][]\n"
jump 244 always 0 0
print "|[grey][][grey][]\n"
jump 244 always 0 0
print "|[grey][][grey][][grey][]\n"
jump 244 always 0 0
print "|[grey][][grey][]\n"
jump 244 always 0 0
print "|[grey][][grey][]\n"
jump 244 always 0 0
print "|[grey][][grey][]\n"
jump 244 always 0 0
print "|[grey][][grey][]\n"
jump 244 always 0 0
print "|[grey][]\n"
jump 244 always 0 0
print "|[grey][]\n"
jump 244 always 0 0
print "|[grey][]\n"
jump 244 always 0 0
print "|[grey][][grey][]\n"
jump 244 always 0 0
print "|[grey][]\n"
jump 244 always 0 0
print "|[grey][][grey][]\n"
jump 244 always 0 0
print "|[grey][][grey][]\n"
jump 244 always 0 0
print "|[grey][][grey][]\n"
jump 244 always 0 0
print "|[grey][]\n"
jump 244 always 0 0
print "|[grey][]\n"
jump 244 always 0 0
print "|[grey][]\n"
jump 244 always 0 0
print "|[grey][][grey][]\n"
jump 244 always 0 0
print "|[grey][]\n"
jump 244 always 0 0
print "|[grey][]\n"
jump 244 always 0 0
print "|[grey][]\n"
jump 244 always 0 0
print "|[grey][]\n"
jump 244 always 0 0
print "|\n"
op shr _ itemList 15
op and jstep _ 0b111110
op add @counter @counter jstep
print "|[grey][]\n"
jump 310 always 0 0
print "|[grey][]\n"
jump 310 always 0 0
print "|[grey][][grey][]\n"
jump 310 always 0 0
print "|[grey][]\n"
jump 310 always 0 0
print "|[grey][][grey][]\n"
jump 310 always 0 0
print "|[grey][][grey][]\n"
jump 310 always 0 0
print "|[grey][][grey][]\n"
jump 310 always 0 0
print "|[grey][]\n"
jump 310 always 0 0
print "|[grey][][grey][]\n"
jump 310 always 0 0
print "|[grey][][grey][]\n"
jump 310 always 0 0
print "|[grey][][grey][][grey][]\n"
jump 310 always 0 0
print "|[grey][][grey][]\n"
jump 310 always 0 0
print "|[grey][][grey][]\n"
jump 310 always 0 0
print "|[grey][][grey][]\n"
jump 310 always 0 0
print "|[grey][][grey][]\n"
jump 310 always 0 0
print "|[grey][]\n"
jump 310 always 0 0
print "|[grey][]\n"
jump 310 always 0 0
print "|[grey][]\n"
jump 310 always 0 0
print "|[grey][][grey][]\n"
jump 310 always 0 0
print "|[grey][]\n"
jump 310 always 0 0
print "|[grey][][grey][]\n"
jump 310 always 0 0
print "|[grey][][grey][]\n"
jump 310 always 0 0
print "|[grey][][grey][]\n"
jump 310 always 0 0
print "|[grey][]\n"
jump 310 always 0 0
print "|[grey][]\n"
jump 310 always 0 0
print "|[grey][]\n"
jump 310 always 0 0
print "|[grey][][grey][]\n"
jump 310 always 0 0
print "|[grey][]\n"
jump 310 always 0 0
print "|[grey][]\n"
jump 310 always 0 0
print "|[grey][]\n"
jump 310 always 0 0
print "|[grey][]\n"
jump 310 always 0 0
print "|\n"
op shr _ itemList 20
op and jstep _ 0b111110
op add @counter @counter jstep
print "清空|[grey][]\n\n刷新\n"
jump 320 always 0 0
print "清空|[grey][]\n\n刷新\n"
jump 320 always 0 0
print "清空|[grey][]\n\n刷新\n"
jump 320 always 0 0
print "清空|\n\n刷新\n"
jump 323 notEqual running 0
print "[scarlet]已暂停[]/[grey]运行中[]\n"
jump 324 always x false
print "[grey]已暂停[]/[acid]运行中[]\n"
jump 327 notEqual controlAllBuT 0
print "仅控制/[grey]控制各种建筑[]\n"
jump 328 always x false
print "[grey]仅控制[]/控制各种建筑\n"
jump 331 notEqual reversed 0
print "选最少物品/[grey]选最多物品[]\n\n\n选择/取消所选物品\n\n"
jump 332 always x false
print "[grey]选最少物品[]/选最多物品\n\n\n选择/取消所选物品\n\n"
op shl configCodeItemList itemList 2
op shl configCodeRunning running 2
op shl configCodeControlAllBuT controlAllBuT 1
op add configCodeOut configCodeItemList configCodeRunning
op add configCodeOut configCodeOut configCodeControlAllBuT
op add configCodeOut configCodeOut reversed
print configCodeOut
print "."
printflush message1
jump 421 equal running 1
sensor config1 sorter1 @config
jump 412 strictEqual config1 null
sensor id1 config1 @id
op add @counter @counter id1
jump 369 always x false
jump 410 always x false
jump 410 always x false
jump 383 always x false
jump 376 always x false
jump 410 always x false
jump 410 always x false
jump 410 always x false
jump 390 always x false
jump 403 always x false
jump 400 always x false
jump 410 always x false
jump 393 always x false
jump 406 always x false
jump 410 always x false
jump 396 always x false
jump 383 always x false
jump 390 always x false
jump 393 always x false
jump 410 always x false
jump 410 always x false
jump 410 always x false
print "s星一般物品"
op and _ itemList 0b11110110011110
jump 373 notEqual _ 0b11110110011110
op sub itemList itemList 0b11110110011110
jump 410 always x false
op or itemList itemList 0b11110110011110
jump 410 always x false
print ""
op and _ itemList 0b11100001001100000
jump 380 notEqual _ 0b11100001001100000
op sub itemList itemList 0b11100001001100000
jump 410 always x false
op or itemList itemList 0b11100001001100000
jump 410 always x false
print ""
op and _ itemList 0b111100000000000000000
jump 387 notEqual _ 0b111100000000000000000
op sub itemList itemList 0b111100000000000000000
jump 410 always x false
op or itemList itemList 0b111100000000000000000
jump 410 always x false
print ""
op xor itemList itemList 0b1000000000000000000000
jump 410 always x false
print ""
op xor itemList itemList 0b10000000000000000000000
jump 410 always x false
print "清除"
op shr itemList itemList 23
op shl itemList itemList 23
jump 410 always x false
print "running"
op notEqual running running 1
jump 410 always x false
print "controlAllBuT"
op notEqual controlAllBuT controlAllBuT 1
jump 410 always x false
print "reversed"
op notEqual reversed reversed 1
jump 410 always x false
print "运行"
jump 410 always x false
control config sorter1 null 0 0 0
set @counter :介绍
sensor config2 sorter2 @config
jump 342 strictEqual config2 null
sensor id2 config2 @id
op shl mask 1 id2
op shl mask mask 1
op xor itemList itemList mask
control config sorter2 null 0 0 0
set @counter :介绍
end
jump 511 notEqual remote 0
jump 468 equal controlAllBuT 1
set maxItemC 0
set i 3
getlink building i
sensor type building @type
jump 432 equal type @item-source
sensor itemC building @itemCapacity
jump 434 lessThanEq itemC maxItemC
set maxItemC itemC
set maxItemCBu building
control config building targetItem 0 0 0
control enabled building enabled 0 0 0
op add i i 1
jump 425 lessThan i @links
op mul maxItemC.th maxItemC threshold
set targetItem null
jump 463 lessThanEq itemList 0
jump 441 notEqual reversed 1
set maxItemC 0
op shr itemList? itemList 1
op log logItemList? itemList? log2
op idiv ii logItemList? log2
op shl _ 1 ii
op sub itemList? itemList? _
jump 449 notEqual ii 20
set item @fissile-matter
jump 453 always x false
jump 452 notEqual ii 21
set item @dormant-cyst
jump 453 always x false
lookup item item ii
sensor itemNum maxItemCBu item
jump 457 notEqual reversed 0
jump 460 greaterThan itemNum maxItemC
jump 458 always itemNum maxItemC
jump 460 lessThan itemNum maxItemC
set targetItem item
set maxItemC itemNum
jump 442 greaterThan itemList? 0
op lessThan enabled maxItemC maxItemC.th
op notEqual enabled enabled reversed
sensor config1 sorter1 @config
jump 344 notEqual config1 null
sensor config2 sorter2 @config
jump 414 notEqual config2 null
jump 423 always x false
set maxItemC 0
set i 3
getlink building i
sensor itemC building @itemCapacity
jump 475 lessThanEq itemC maxItemC
set maxItemC itemC
set maxItemCBu building
control config building targetItem 0 0 0
control enabled building enabled 0 0 0
op add i i 1
jump 470 lessThan i @links
op mul maxItemC.th maxItemC threshold
set targetItem null
jump 506 lessThanEq itemList 0
jump 484 notEqual reversed 1
set maxItemC 0
op shr itemList? itemList 1
op log logItemList? itemList? log2
op idiv ii logItemList? log2
op shl _ 1 ii
op sub itemList? itemList? _
jump 492 notEqual ii 20
set item @fissile-matter
jump 496 always x false
jump 495 notEqual ii 21
set item @dormant-cyst
jump 496 always x false
lookup item item ii
sensor itemNum maxItemCBu item
jump 500 notEqual reversed 0
jump 503 greaterThan itemNum maxItemC
jump 501 always itemNum maxItemC
jump 503 lessThan itemNum maxItemC
set targetItem item
set maxItemC itemNum
jump 485 greaterThan itemList? 0
op lessThan enabled maxItemC maxItemC.th
op notEqual enabled enabled reversed
sensor config1 sorter1 @config
jump 344 notEqual config1 null
sensor config2 sorter2 @config
jump 414 notEqual config2 null
jump 468 always x false
jump 583 equal controlAllBuT 1
sensor remoteDead remoteBd @dead
jump 542 equal remoteDead 0
jump 527 equal remote 2
set unitTId 0
lookup unit unitT unitTId
ubind unitT
jump 524 strictEqual @unit null
ulocate building core 0 @copper remoteBdX remoteBdY remoteFound remoteBd
sensor ctr @unit @controller
jump 523 notEqual ctr @this
ucontrol unbind 0 0 0 0 0
jump 512 equal remoteFound 1
op add unitTId unitTId 1
jump 516 lessThan unitTId @unitCount
jump 512 always x false
ubind remoteUnit
sensor remoteUDead @unit @dead
jump 527 equal remoteUDead 1
sensor ctd @unit @controlled
jump 535 equal ctd 0
sensor uFlag @unit @flag
jump 535 equal uFlag 0
jump 527 notEqual uFlag flag
ucontrol flag flag 0 0 0 0
ucontrol pathfind remoteX remoteY 0 0 0
ucontrol getBlock remoteX remoteY check remoteBd 0
jump 528 strictEqual check null
ucontrol flag 0 0 0 0 0
ucontrol unbind 0 0 0 0 0
jump 512 always x false
sensor maxItemC remoteBd @itemCapacity
op mul maxItemC.th maxItemC threshold
set i 3
getlink building i
sensor type building @type
jump 550 notEqual type @item-source
control config building targetItem 0 0 0
control enabled building enabled 0 0 0
op add i i 1
jump 545 lessThan i @links
set targetItem null
jump 578 lessThanEq itemList 0
jump 556 notEqual reversed 1
set maxItemC 0
op shr itemList? itemList 1
op log logItemList? itemList? log2
op idiv ii logItemList? log2
op shl _ 1 ii
op sub itemList? itemList? _
jump 564 notEqual ii 20
set item @fissile-matter
jump 568 always x false
jump 567 notEqual ii 21
set item @dormant-cyst
jump 568 always x false
lookup item item ii
sensor itemNum remoteBd item
jump 572 notEqual reversed 0
jump 575 greaterThan itemNum maxItemC
jump 573 always itemNum maxItemC
jump 575 lessThan itemNum maxItemC
set targetItem item
set maxItemC itemNum
jump 557 greaterThan itemList? 0
op lessThan enabled maxItemC maxItemC.th
op notEqual enabled enabled reversed
sensor config1 sorter1 @config
jump 344 notEqual config1 null
sensor config2 sorter2 @config
jump 414 notEqual config2 null
jump 512 always x false
sensor remoteDead remoteBd @dead
jump 613 equal remoteDead 0
jump 598 equal remote 2
set unitTId 0
lookup unit unitT unitTId
ubind unitT
jump 595 strictEqual @unit null
ulocate building core 0 @copper remoteBdX remoteBdY remoteFound remoteBd
sensor ctr @unit @controller
jump 594 notEqual ctr @this
ucontrol unbind 0 0 0 0 0
jump 583 equal remoteFound 1
op add unitTId unitTId 1
jump 587 lessThan unitTId @unitCount
jump 583 always x false
ubind remoteUnit
sensor remoteUDead @unit @dead
jump 598 equal remoteUDead 1
sensor ctd @unit @controlled
jump 606 equal ctd 0
sensor uFlag @unit @flag
jump 606 equal uFlag 0
jump 598 notEqual uFlag flag
ucontrol flag flag 0 0 0 0
ucontrol pathfind remoteX remoteY 0 0 0
ucontrol getBlock remoteX remoteY check remoteBd 0
jump 599 strictEqual check null
ucontrol flag 0 0 0 0 0
ucontrol unbind 0 0 0 0 0
jump 583 always x false
sensor maxItemC remoteBd @itemCapacity
op mul maxItemC.th maxItemC threshold
set i 3
getlink building i
control config building targetItem 0 0 0
control enabled building enabled 0 0 0
op add i i 1
jump 616 lessThan i @links
set targetItem null
jump 647 lessThanEq itemList 0
jump 625 notEqual reversed 1
set maxItemC 0
op shr itemList? itemList 1
op log logItemList? itemList? log2
op idiv ii logItemList? log2
op shl _ 1 ii
op sub itemList? itemList? _
jump 633 notEqual ii 20
set item @fissile-matter
jump 637 always x false
jump 636 notEqual ii 21
set item @dormant-cyst
jump 637 always x false
lookup item item ii
sensor itemNum remoteBd item
jump 641 notEqual reversed 0
jump 644 greaterThan itemNum maxItemC
jump 642 always itemNum maxItemC
jump 644 lessThan itemNum maxItemC
set targetItem item
set maxItemC itemNum
jump 626 greaterThan itemList? 0
op lessThan enabled maxItemC maxItemC.th
op notEqual enabled enabled reversed
sensor config1 sorter1 @config
jump 344 notEqual config1 null
sensor config2 sorter2 @config
jump 414 notEqual config2 null
jump 583 always x false

这个逻辑通过控制卸载器等选择最低数量的物品，适用于工厂物资运输与核心物品装填
-------------------------------
在打表的时候很容易出现因失误导致的变量不全问题，
set id -1
op add id id 1
lookup block team id
sensor name team @name
write id processor1 name
jump 1 notEqual team 0
set max id
print "停止位置为:"
set id -1
op add id id 1
lookup block team id
sensor name team @name
read read processor1 name
jump 16 strictEqual read id
print id
print "，"
jump 9 lessThan id max
set id 0
printflush message1
逻辑可以帮我们发现表断在了哪里。
---------------------------
