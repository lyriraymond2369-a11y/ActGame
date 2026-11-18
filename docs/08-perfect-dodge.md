# 完美闪避与无敌帧

> 本文件是模块文档。项目总导航、规范与历史见 [README.md](../README.md)。

### 2）完美闪避与无敌帧

#### （1）三个概念必须分开

| 概念 | 定义 | 由什么决定 |
| --- | --- | --- |
| 无敌帧 | 闪避动作中一段完全免伤的区间 | `ANS_IFrame` → `SetInvincible(bool)` |
| 完美窗口 | 闪避起手后 N 毫秒 | `NotifyDodgeStart` + `PerfectDodgeWindow`（纯计时） |
| 奖励 | 判定成功后给什么 | `OnPerfectDodge` 分发器 |

```
无敌是「一段区间」 → 用动画通知表达，美术能随动作调
完美是「一个瞬间」 → 用纯计时表达，手感全局统一
两者完全独立，谁先结束都不影响另一方
```

#### （2）变量

**`BPC_Attribute`** —— 判定层

| 变量 | 类型 | 默认 | 说明 |
| --- | --- | --- | --- |
| `LastDodgeTime` | float | 0 | 闪避起手时刻，由 `NotifyDodgeStart` 写入 |
| `PerfectDodgeWindow` | float | 0.15 | 完美窗口长度 |
| `bInvincible` | bool | false | 动画无敌，**只由 `ANS_IFrame` 的 Begin / End 改** |
| `bInvincibleTail` | bool | false | 收尾时补的无敌尾巴，**只由内部计时器改** |
| `PerfectDodgeTailDuration` | float | 0.15 | 尾巴时长 |
| `TailTimerHandle` | TimerHandle | — | 尾巴计时器 |
| `bPerfectDodgeUsed` | bool | false | 本轮闪避是否已奖励过，由 `NotifyDodgeStart` 复位 |

**`BPC_Combat`** —— 收尾层

| 变量 | 类型 | 默认 | 说明 |
| --- | --- | --- | --- |
| `PerfectDodgeCancelDelay` | float | 0.25 | 收尾的时间上限，**早于慢动作结束**，见（6） |
| `PerfectDodgeMaxDistance` | float | 150 | 收尾的距离上限，**从完美闪避判定成功点累计** |
| `DodgeStartLocation` | Vector | — | 判定成功时的位置，`HandlePerfectDodge` 里记录 |
| `PerfectDodgeFinishTimer` | TimerHandle | — | 时间上限计时 |
| `bPerfectDodgePending` | bool | false | 是否处于「已判定成功、待收尾」状态 |

**`BPC_CombatFeedBack`** —— 表现层

| 变量 | 类型 | 默认 | 说明 |
| --- | --- | --- | --- |
| `SlowMoScale` | float | 0.1 | 敌人时间倍率 |
| `SlowMoDuration` | float | 0.5 | 慢动作的**实时**秒数 |
| `SlowMoActors` | Actor 数组 | 空 | 本轮被减速的敌人 |
| `SlowMoTimerHandle` | TimerHandle | — | 单次重入用 |

**`bInvincible` 与 `bInvincibleTail` 为什么用两个 bool 而不是一个：**

```
bInvincible       归动画通知管
bInvincibleTail   归完美闪避管

合并成一个的话：尾巴计时器到期，会把"正在播的下一套闪避动画"的无敌一起关掉
```

#### （3）判定

**判定写在 `ReceiveDamage` 里，分支见 [CharacterBase 接口文档](01-character-base.md) 的 `BPI_Attribute` 小节。**
**要点只有一句：完美 = `bInvincible` 为真，且处于 `PerfectDodgeWindow` 内 —— 两个条件是 AND。**

#### （4）判定成功后发生什么

**判定层只做两件事：置 flag、广播。所有收尾动作都不在这一层。**

```
ReceiveDamage 的 ② 条：
   bPerfectDodgeUsed == false ?
      → bPerfectDodgeUsed = true
      → Broadcast OnPerfectDodge
   return (Ignore, false, true)
```

**⚠️ 这里**不要**关 `bInvincible`、不要给尾巴、不要停动作 —— 闪避动画还要继续播。**

`BPC_Combat` 绑了 `OnPerfectDodge`，`HandlePerfectDodge` 只施加效果、不做收尾：

```
① CameraDirector.Shake(PerfectDodge)          震屏                      【接口】
② CombatFeedBack.PlayPerfectDodgeStartSound(0.5)  开始音，0.5s 后自动播结束音  【接口】
③ CombatFeedBack.PlayEnemySlowMo(0.1, 0.5)    只慢敌人（0.1 倍 × 0.5s）   【接口】
④ Motor.SetMotionScale(0.3)                   位移衰减，控距离
⑤ bPerfectDodgePending = true
   Set Timer(PerfectDodgeCancelDelay → TryFinishPerfectDodge)
```

**⭐ 第 ② ③ 两步是**两个独立接口**，不能合并：**

```
PlayPerfectDodgeStartSound(0.5) → 影音层：开始音 + 内部计时 → 0.5s 后播结束音
PlayEnemySlowMo(0.1, 0.5)       → 时间层：只调敌人的 CustomTimeDilation

两者的 0.5 必须一致 → 结束音正好落在慢动作恢复的那一刻
```

**⚠️ 音效不能写在 `PlayEnemySlowMo` 内部：完美格挡也调它，会误播闪避音效。**

**为什么不立即取消动画：**

```
立即取消 → 玩家停在 Locomotion 站姿，敌人在 0.1 倍速里挥刀
          → 画面不协调，像卡住了

继续播   → 玩家在慢动作里把闪避动作走完，敌人几乎不动
          → 这才是「我躲开了」该有的画面
```

#### （5）防重复：`bPerfectDodgeUsed`

**因为判定成功后动画不取消，`bInvincible` 还在、窗口还开着 —— 第二段攻击会再次触发。**

```
NotifyDodgeStart   →  bPerfectDodgeUsed = false
判定成功           →  只有 false 时才广播，然后置 true
```

**这是「一次闪避只奖励一次」的唯一保证。不能靠"动作被取消了"来兜底，因为动作现在不取消。**

#### （6）收尾：时间与距离取先到

**收尾由两个条件之一触发：**

```
时间上限   PerfectDodgeCancelDelay 到点
距离上限   从闪避起点累计的位移 ≥ PerfectDodgeMaxDistance
```

**为什么不能只用时间：**

```
闪避位移是 MotionSelf + Motor 驱动的，有加速度和摩擦衰减
同样的 0.25s：
   前闪可能滑出 500 单位
   后闪可能只有 200 单位
   → 一个够得着敌人，一个够不着

时间只能保证"动画播了多久"，保证不了"离敌人多远"
```

**⚠️ 距离从**判定成功点**算，不是从闪避起点算：**

```
150 这个值小于"闪避起手到被打中"之间已经走掉的位移
（闪避 0.05s 起手、0.1s 被打，这时已经滑了 ~200）

如果从起点算 → 判定成功的瞬间就超限 → 收尾立即触发
             → 退化成"立刻取消动画"，正好是这套设计要避免的

从判定点算 → 玩家还能再滑 150，配合 0.3 的位移衰减，约 0.1~0.15s
```

**所以记录位置的地方不是 `DoDodge`，而是判定成功的那一刻。**

**`PerfectDodgeMaxDistance` 的倒推公式（算的是"判定之后还能滑多远"）：**

```
延伸攻击射程 − 判定时已滑出的距离 − 攻击自带前冲 + 余量 ≈ 150
```

**更彻底的做法是让延伸攻击自带前冲/吸附** —— 那样"闪避别跑太远"就从硬约束降成软约束。

`Tick` 里的距离检查：

```
Tick
   Branch: bPerfectDodgePending == true
      Distance = Length(角色当前位置 − DodgeStartLocation)
      Branch: Distance >= PerfectDodgeMaxDistance → TryFinishPerfectDodge()
```

`TryFinishPerfectDodge` 的固定顺序：

```
① 守卫      bPerfectDodgePending / 当前 State 仍是 Dodge
② 无敌收尾   Attribute.EndPerfectDodge()
③ 动画收尾   Montage_Stop(0.12, 当前闪避蒙太奇)
④ 位移收尾   Motor.StopMotion() + Motor.SetMotionScale(1.0)
⑤ 行动权     ActionState.ClearDodgeCD()
⑥ 状态       ActionState.SetState(Locomotion)
```

**为什么用 `SetState` 而不是 `TryEnterState`：**

```
闪避刚播了 0.1s，取消窗口根本没开
TryEnterState 走转场矩阵，直接被拒 → 状态卡在 Dodge
SetState 不判断，是唯一能满意回 Locomotion 的入口
```

**⚠️ `SetState` 不做收尾，取消窗口的残留值要顺手清（`SetCancelWindow(false)`）。**

**⚠️ 动画收尾必须用 `Montage_Stop(0.12)`，不能用 `StopAnimMontage`：**

```
StopAnimMontage      默认 blend out 极短 → "啪"一下站住
Montage_Stop(0.12)   0.12 秒淡出 → 能接上 Locomotion
```

#### （7）无敌尾巴：只在需要时补

**尾巴不是恒定给的，是「收尾时如果还在无敌，就补平」。**

```
收尾发生在 t，ANS_IFrame 的 End 在 t_End

情况 A：t > t_End   → bInvincible 已是 false，无敌自然结束，不需要尾巴
情况 B：t < t_End   → 停蒙太奇会掐断 ANS，End 不一定触发
                   → 必须显式关 bInvincible，并补一段尾巴
```

**这个判断放在 `EndPerfectDodge` 内部：**

```
EndPerfectDodge()
   ├─ Branch: bInvincible == false → 什么都不做
   └─ Branch: bInvincible == true
         ├─ SetInvincible(false)
         ├─ bInvincibleTail = true
         └─ Set Timer(PerfectDodgeTailDuration → 关尾巴)
```

**为什么不让外部自己判断"要不要尾巴"：**

```
外部需要知道 bInvincible 当前值，那是内部状态
暴露 getter 等于把判定层的职责泄漏到收尾层
→ 只给一个语义明确的入口，判断留在 Attribute
```

**没有尾巴会发生什么：**

```
完美闪避 → 收尾掐断无敌 → 敌人三连击第二段到达 → 玩家吃满伤害
玩家："我明明完美闪避了"
```

#### （8）慢动作：只慢敌人

**用 `CustomTimeDilation` 挂在敌人身上，不碰全局时间。**

```
PlayEnemySlowMo(Scale, Duration)          【接口实现】BPC_CombatFeedBack
   ├─ 若 SlowMoActors 非空 → 先 RestoreSlowMo()          ← 防叠加
   ├─ Clear and Invalidate Timer(SlowMoTimerHandle)
   ├─ ForEach GetAllActorsOfClass(BP_EnemyBase)
   │     IsValid? → Set CustomTimeDilation(Scale)
   │              → Add 到 SlowMoActors
   └─ Set Timer by Event(Duration → RestoreSlowMo)

RestoreSlowMo()
   ├─ ForEach SlowMoActors → IsValid? → Set CustomTimeDilation(1.0)
   └─ SlowMoActors 清空

EndPlay → RestoreSlowMo()      兜底
```

**为什么不用全局膨胀：**

```
全局慢    → 玩家也慢，等于只是"顿了一下"，没有行动优势
只慢敌人  → 玩家真的获得了时间差，可以走位、绕后、反击
```

**逐角色膨胀还顺手省掉了一整段换算：**

```
全局膨胀时：Timer 值 = 实时时长 × 膨胀系数（还得防 0 导致 Timer 停摆）
逐角色时：  全局始终是 1.0，Timer 直接用实时秒数
```

**四条必须处理的坑：**

```
① CustomTimeDilation 不影响 Timer
   敌人"想得快、动得慢" —— 通常反而是好事，但要知道它存在

② 慢动作期间敌人被击杀
   SlowMoActors 里是失效引用 → 恢复时必须逐个 IsValid

③ 重入要 Set 不要乘
   Set 0.1 就是 0.1；写乘会变成 0.01，敌人基本静止
   重入前先 RestoreSlowMo 把上一轮还原

④ 遍历全场敌人是"省事但粗糙"
   更精细的做法是只慢攻击者，但那需要攻击者引用
   （ReceiveDamage 目前只有 ImpactLocation，没有 Attacker）
```

#### （9）位移衰减与倍率复位

**`Motor.SetMotionScale(0.3)` 是「粘性」状态，不是一次性参数。**

```
完美闪避 → SetMotionScale(0.3)
   ↓ 收尾忘记复位
之后所有招式位移只有三成速度
   ↓
玩家觉得"手感突然变肉"，但不会报任何错
```

**复位点必须收口，三条路径全覆盖：**

| 路径 | 复位 | 说明 |
| --- | --- | --- |
| `TryFinishPerfectDodge` | ✅ | 主路径 |
| `InterruptPerfectDodge`（受击 / 死亡打断） | ✅ | 慢动作期间被打 |
| `DoDodge` 开头 | ✅ 防御性 | 万一上面漏了 |

```
InterruptPerfectDodge()
   ├─ bPerfectDodgePending = false
   ├─ Clear and Invalidate Timer(PerfectDodgeFinishTimer)
   └─ Motor.SetMotionScale(1.0)
```

**`InterruptPerfectDodge` 要接到 `EnterHit` 和死亡处理的开头** —— 否则慢动作期间被打断时，`Tick` 里的距离检查还会试图 `SetState(Locomotion)`，把受击状态覆盖掉。

#### （10）完整时间轴

**以下按实际值代入（`CancelDelay` 0.25 / `SlowMo` 0.1 × 0.5s）：**

```
t = 0.00   DoDodge：选行 / 设朝向 / SetMotionScale(1.0) / SetMotionProfile / 播放
t = 0.05   ANS_IFrame Begin → bInvincible = true
t = 0.10   被打 → 判定成功
           ├─ bPerfectDodgeUsed = true + 广播 OnPerfectDodge
           ├─ 震屏 + 音效
           ├─ 敌人变慢（0.1 倍，持续 0.5 实时秒）
           ├─ Motor.SetMotionScale(0.3)
           ├─ Player.StartAfterimage()
           └─ 记录当前位置，开启收尾监视
t = 0.10~0.35   动画继续播，无敌继续，玩家滑得慢，敌人几乎定格
                每 0.05s 留一个残影，共 5 个
t = 0.35   收尾（时间到点；或中途位移超 150 提前触发）
           ├─ EndPerfectDodge（按需关无敌 + 尾巴）
           ├─ Montage_Stop(0.12)
           ├─ StopMotion + SetMotionScale(1.0)
           ├─ ClearDodgeCD
           ├─ Player.StopAfterimage()
           └─ SetState(Locomotion)
t = 0.35~0.75   5 个残影各自淡出销毁
t = 0.35~0.60   ★ 玩家已经自由，敌人还在 0.1 倍速里
t = 0.60   敌人恢复
```

**⭐ 这组数值最关键的一点：`收尾在 0.35，慢动作到 0.60`。**

```
PerfectDodgeCancelDelay 0.25  <  SlowMoDuration 0.5

→ 玩家提前 0.25s 拿回行动权
→ 这 0.25s 里敌人只有 0.1 倍速（只推进了 0.025s 的动作）
→ 这 0.25s 就是"延伸攻击"的窗口，几乎白送
```

**慢动作恢复与收尾是两个独立计时器** —— 前者控敌人，后者控玩家。
**不要为了对齐把这两个数值耦合死，它们的差值本身就是奖励的一部分。**

#### （11）涉及资产与接口

```
资产   ANS_IFrame                              无敌区间通知
       Montage_Dodge / Montage_Dodge_Air       各段内挂 ANS_IFrame
       E_CameraShakeType + PerfectDodge        追加到枚举末尾，别插中间
       BPC_CameraDirector · Shake 分支          PerfectDodge → BPCS_PerfectDodge
                                                ⚠️ 参数暂未调整，与 PerfectBlock 尚未拉开差异

接口   BPI_Attribute      + SetInvincible / EndPerfectDodge
       BPI_CombatFeedBack + PlayEnemySlowMo（原 PlayPerfectDodgeSlowMo，加 Scale / Duration）
       BPI_ActionState    + ClearDodgeCD
       BPI_Motor          + SetMotionScale
       BPI_Player         + StartAfterimage / StopAfterimage

常量   Motor.SetMotionScale 衰减倍率      0.3
       Montage_Stop blend out            0.12
       Dodge_F 行的 MotionSelf 幅值       要能被 0.3 衰减后仍有可读的位移
```

#### （12）残影：生成、淡出与打断

**判定成功到收尾之间的位移，用"留在原地的静态姿态快照"表达。**

```
资产    M_Afterimage         Unlit + Additive + Fresnel，参数 Opacity / Color
        BP_Afterimage        PoseableMeshComponent + Timeline 淡出
        BPI_Afterimage       CopyPoseFrom(TargetMesh)
```

**三者的分工：**

```
BP_Afterimage      只管"一个影子怎么活"——复制姿态、铺材质、淡出、自销毁
BP_Player          只管"什么时候生、生成几个"——Timer 循环 Spawn
BPC_Combat         只管"什么时候开始/停止"——调接口，不碰生成细节
```

**为什么用 PoseableMesh 而不是 Niagara 或 Ribbon：**

```
Ribbon / Trail 只有"轨迹"，没有姿态 → 看起来像风，不像人
PoseableMesh + Copy Pose From Skeletal Component → 真·姿态快照
成本：每个残影一次 draw call + 一份骨骼矩阵，5 个完全无压力
```

**⭐ 三个必须守住的点：**

```
① PoseableMesh 必须预先指定「骨骼网格体资源」
   CopyPose 只复制骨骼变换，不复制网格资源
   不填的话姿态复制成功但画面全空，极易误判成"复制失败"

② 材质槽必须遍历，不能只设 index 0
   角色通常 3~5 个槽（身体/衣服/头发/眼睛）
   只设 0 会出现"身体是残影、衣服是原材质"的错位

③ 绝不 Attach 到玩家
   残影固定在生成瞬间的位置，跟随就失去了"残影"的意义
```

**`BP_Afterimage` 的淡出链路：**

```
BeginPlay
  → Create Dynamic Material Instance(M_Afterimage)  → MID
  → For Each Loop(0 .. GetNumMaterials()-1)
        → Set Material(Index, MID)
  → Timeline(0 → 1, FadeTime) → Play

Timeline · Update  → Set Scalar Parameter Value(MID, "Opacity", 1 − Alpha)
Timeline · Finished → DestroyActor
```

**⚠️ 必须用 MID（动态材质实例）。直接用母材质的话，改参数会改到所有残影上 —— 结果是 5 个影子同时消失，而不是各自淡出。**

**⚠️ UE 里有**两个**同名节点「Set Scalar Parameter Value」：**

```
一个 Target 是 Material Instance Dynamic  → 改材质参数
一个 Target 是 Audio Component           → 改 MetaSound 参数

从内容浏览器拖节点时很容易选错
选错的表现：Get 读回来永远是母材质的默认值，且没有任何报错
→ 排查方法：把材质里该参数的默认值改成一个特殊数字，
            看 Get 是否跟着变；不变就是写到了别的对象上
```

**`BP_Player` 的生成侧：**

```
变量   AfterimageClass : BP_Afterimage 类引用
       GhostInterval  : 0.05
       MaxGhosts      : 5
       GhostTimerHandle / ActiveGhosts(数组)

StartAfterimage  → 清 Timer → Set Timer(GhostInterval → SpawnGhost, Looping)
SpawnGhost       → 剪枝 → Num >= MaxGhosts? Return → Spawn + CopyPoseFrom + Add
StopAfterimage   → 清 Timer → ActiveGhosts.Clear()
```

**⭐ `ActiveGhosts` 必须清理，这是本节最大的坑：**

```
残影淡出后自销毁，但数组里的引用不会自动移除
→ Num() 持续虚高
→ 第 2 次完美闪避时 Num(5) >= MaxGhosts(5) → 一个都不生成
→ 表现：只有第一次完美闪避有残影，之后永远没有，且不报任何错
```

**两种清理方式，建议都做：**

```
StopAfterimage 时 Clear()                  ← 必需，每轮重新计数
Start/Spawn 时按 IsValid 剪枝               ← 可选，给"高频连闪"兜底
```

**⚠️ `StopAfterimage` 里**不要** `DestroyActor` 已生成的残影 —— 它们有自己的淡出 Timeline，强行销毁会从"渐隐"变成"啪一下消失"。**

**接线（三个点，缺一不可）：**

```
HandlePerfectDodge      → Player.StartAfterimage()
TryFinishPerfectDodge   → Player.StopAfterimage()    放在 SetState 之前
InterruptPerfectDodge   → Player.StopAfterimage()
```

**⚠️ `InterruptPerfectDodge` 那条最容易漏。慢动作期间受击时不停止生成，Timer 会继续跑到超过 `MaxGhosts`，表现就是"挨打了还在冒影子"。**

**时间对齐：**

```
t = 0.10   判定成功 → StartAfterimage
t = 0.10~0.35   每 0.05s 一个，共 5 个
t = 0.35   收尾 → StopAfterimage（只停生成，已有残影继续淡出）
t = 0.35~0.75   5 个残影各自淡出销毁
```

**距离上限（150）提前触发收尾时只会有 2~3 个残影 —— 这是合理的：位移短本来就不需要那么多。**

| 参数 | 默认 | 调法 |
| --- | --- | --- |
| `GhostInterval` | 0.05 | 太糊 → 0.07；太稀 → 0.04 |
| `MaxGhosts` | 5 | 最多到 7，超过 8 开始掉帧 |
| `FadeTime` | 0.4 | 想拖更久 → 0.7 |
| Color | (0.3, 0.75, 1.0) | 冷色调与"时间变慢"呼应 |
| Fresnel 指数 | 3~5 | 越大边缘越细，6 已经偏虚 |

**⚠️ 材质里的参数名必须与蓝图完全一致（`Opacity` / `Color`，大小写敏感）。写错不报错，只表现为"残影不淡出"或"颜色不对"。**

**接线后最容易出现的四个现象与原因：**

```
残影跟着人跑             → Spawn 时 Attach 到了角色
残影永远是 T-Pose        → CopyPoseFrom 没调，或晚了一帧
第一次正常、之后再也不出   → ActiveGhosts 没清理，Num() 虚高
只亮身体、衣服是原材质     → 材质槽只设了 index 0
```

#### （13）反击窗口：同样的按键，不同的起手

**核心：反击不是新输入，而是"同一颗按键在窗口内被解析成不同的起始行"。**

```
E_InputType 只有 Light / Heavy / Dodge / Jump / Execute
→ 没有、也不需要 "Counter" 这个输入
→ 变化发生在 DoLight / DoHeavy 的**选行**这一步
```

**为什么这样最省事：**

```
① 连招系统天然复用 —— Counter_L1 → L2 → L3 就是普通连招，只是行名不同
② 状态机不动 —— 反击期间依然是 Attack 状态
③ 输入层不动 —— 不需要新的 InputAction、不需要改 BufferInput
④ 过期即失效 —— 窗口一关就自动回到普通轻重击，不需要额外复位
```

**⭐ 因为连招推进用的是 `ST_AttackData.Next` 行名跳转（不是字符串拼接），所以**只有"起手选行"需要分支，连招推进完全由数据驱动，这一步一行都不用改。**

**反击窗口由完美闪避与完美格挡共用，用枚举区分来源：**

| `E_CounterType` | 含义 | 优先级 |
| --- | --- | --- |
| `None` | 无窗口 | 0 |
| `Block` | 格挡反击窗口 | 1 |
| `Dodge` | 闪避反击窗口 | **2（高）** |

> **完美闪避更难（需要无敌帧恰好覆盖判定点），所以闪避反击优先级高于格挡反击。**

**变量（`BPC_Combat`）：**

| 变量 | 类型 | 默认 | 说明 |
| --- | --- | --- | --- |
| `CounterType` | `E_CounterType` | `None` | 当前处于哪个反击窗口 |
| `CounterWindowDuration` | float | 1.0 | 窗口时长，从收尾时刻算 |
| `CounterTimerHandle` | TimerHandle | — | |
| `CounterTypeUsed` | bool | false | 本轮是否已消费过反击起手 |

**窗口从**收尾**开始算，不是从判定成功算：**

```
0.10~0.35 玩家锁在闪避动作里，按不出攻击
从 0.35 收尾那一刻开始计时，才是玩家真正"能按"的时间
若从 0.10 算，可用时间会凭空少 0.25s
```

**开窗与关窗：**

```
OpenCounterWindow(NewType : E_CounterType)
  ├─ Branch: NewType == Block && CounterType == Dodge
  │     → Return                              ← 闪避反击优先级更高，Block 不覆盖
  ├─ CounterType = NewType
  ├─ CounterTypeUsed = false
  ├─ Clear and Invalidate Timer(CounterTimerHandle)
  └─ Set Timer(CounterWindowDuration → CloseCounterWindow)

CloseCounterWindow()
  ├─ CounterType = None
  └─ CounterTypeUsed = false
```

**⚠️ `OpenCounterWindow` 必须排在 `SetState(Locomotion)` **之前**：**

```
玩家可能在 0.35 之前就按了攻击 → 进 BufferInput 缓存
收尾回 Locomotion 后消费缓存 → 触发 DoLight
如果开窗晚于 SetState，缓存消费可能赶在开窗之前，反击判定落空
```

**选行前缀：**

```
GetAttackRowPrefix(bIsHeavy : bool) → String
  ├─ Branch: CounterType == Dodge AND CounterTypeUsed == false
  │     → 返回 bIsHeavy ? "Counter_H" : "Counter_L"
  ├─ Branch: CounterType == Block AND CounterTypeUsed == false
  │     → 返回 bIsHeavy ? "BlockCounter_H" : "BlockCounter_L"
  └─ 否则
        → 返回 bIsHeavy ? "Heavy" : "Attack"
```

**`DoLight` / `DoHeavy` 的改动只有两处：**

```
① 起手行 = GetAttackRowPrefix(自身类型) + "1"
   ← 只在"开一条新连招"时用；已经在连招中则继续走 CurrentAttack.Next

② 若起手行以 "Counter" 或 "BlockCounter" 开头 → CounterTypeUsed = true（消费掉）
```

**⭐ 最容易写错的一句：**

```
不要在每次 DoLight / DoHeavy 时都按窗口强制选反击起手
只有「开始一条新连招」才选起手行
正在连招中必须优先沿用 CurrentAttack.Next
否则反击连招会被自己打断成"永远在打第一段"
```

**数据行（`DT_Attacks`）：**

| 行名 | `Next` 指向 |
| --- | --- |
| `Counter_L1` | `Counter_L2` |
| `Counter_L2` | `Counter_L3` |
| `Counter_L3` | `Counter_L4` |
| `Counter_L4` | 空（收招） |
| `Counter_H1` | `Counter_H2` |
| `Counter_H2` | `Counter_H3` |
| `Counter_H3` | 空（收招） |
| `BlockCounter_L1` | `BlockCounter_L2` |
| `BlockCounter_L2` | 空（收招） |
| `BlockCounter_H1` | `BlockCounter_H2` |
| `BlockCounter_H2` | 空（收招） |

**格挡反击段数比闪避反击短（4 vs 7 行），是有意设计：格挡后硬直更短，反击更快结束。**

**`MotionSelf` 建议带向前位移：**

```
完美闪避后玩家离敌人最多 150（PerfectDodgeMaxDistance）
反击第一段向前冲 150~250
→ 即使闪避把人带远了，反击也能自己补上
→ "闪避别跑太远"从硬约束降成软约束

BlockCounter 是原地格挡，玩家本来就在近身
→ 位移给 100~150 即可，不需要补距离
```

**时序：**

```
t = 0.35   收尾
           ├─ Player.StopAfterimage()
           ├─ OpenCounterWindow(Dodge)   ← 先开窗
           └─ SetState(Locomotion)       ← 再交还控制权
t = 0.35~1.35   ★ 反击窗口（1.0s）
              按轻击 → Counter_L1 → L2 → L3 → L4
              按重击 → Counter_H1 → H2 → H3
t = 1.35   CloseCounterWindow()
           → 之后再按，回到 Attack1 / Heavy
```

**窗口只控制"能不能起手"，不控制"能不能续接"：**

```
窗口 1.35 关闭，但玩家已经打出 Counter_L2
→ Counter_L2 的 Next 仍然指向 Counter_L3
→ 连招照常继续，不会被计时器腰斩

这是 Next 链结构带来的天然好处：续接属于数据，不受窗口影响
```

**清理路径（四条，缺一不可）：**

```
EnterHit              → CloseCounterWindow()    挨打就没了
死亡                   → CloseCounterWindow()
DoDodge（重新闪避）    → CloseCounterWindow()    开新一轮，旧窗口作废
DoJump                → CloseCounterWindow()    跳跃也是重开动作
```

**⚠️ 和 `bSlowMoActive` / `bPerfectDodgeUsed` 同一类问题：窗口是状态量，必须显式关闭。少了 `DoDodge` 那一处，会出现"闪避失败后仍能打出反击"。**

**⚠️ `DoJump` 那条同理：不关的话会出现"跳起来还能打出反击"。**

**每轮只奖励一次起手：**

```
窗口内打出 Counter_L1 → CounterTypeUsed = true
→ 窗口剩余时间里再按攻击 → 前缀回落到 Attack / Heavy
→ 但已经开始的反击连招继续按 Next 走完
```

**这就是 `CounterTypeUsed` 与 `CurrentAttack.Next` 的分工：前者管"能不能起手"，后者管"能不能续接"。**

---

