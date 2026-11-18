# 完美格挡

> 本文件是模块文档。项目总导航、规范与历史见 [README.md](../README.md)。

### 3）完美格挡

> **状态：判定链与反馈已完整（震动 / 音效 / FOV 特写全部接入）；完美格挡反击已完成（详见（12））；普通格挡受击已实现（详见（13），含上半身分离，下半身层未实现）；格挡破防已实现（详见（14））；完美窗口已区间化（起止两值）；格挡 CD 已迁入 `BPC_ActionState`。**
>
> **⚠️ （1）~（12）只写完美格挡；（13）普通格挡受击；（14）格挡破防 —— 三者共用同一套判定，只在表现层分叉。**

**实施进度总览：**

| 环节 | 状态 | 位置 |
| --- | --- | --- |
| 判定（格挡 + 正面 + `Poise > 0` + 完美窗口区间） | ✅ 已实现 | `ReceiveDamage` 第 ③ 条 → `IsPerfectBlock()` |
| 完美窗口区间化（Start / End 两值） | ✅ 已实现 | `BPC_Attribute.IsPerfectBlock` |
| 防重复 `bPerfectBlockUsed` | ✅ 已实现 | `BPC_Attribute` |
| 判定后收尾（退格挡 / 回 Locomotion / 清 CD / 开窗口） | ✅ 已实现 | `HandlePerfectBlock`（4）的第 1~3 步 |
| 格挡入口门槛（`TryGuard` + `CanGuard`） | ✅ 已实现 | （6） |
| 格挡 CD（迁入 `BPC_ActionState`） | ✅ 已实现 | （5） |
| 顿帧 0.04s（双方各停） | ✅ 已实现 | 双方各调 `PlayHitStop(Self, 0.04)` |
| 敌人慢速 `PlayEnemySlowMo(0.15, 0.12)` | ✅ 已实现 | （4）第 5 步 |
| 完美格挡撞击音 `PlayPerfectBlockSound()` | ✅ 已实现 | 独立接口，不复用闪避音效 |
| 强震屏 `Shake(PerfectBlock, HitPoint, 2.0)` | ✅ 已实现 | （11.1） |
| FOV 特写 `PlayPerfectBlockCloseUp()` | ✅ 已接入 `PlayHitFeedback` 的 `bPerfect` 分支 | （11.3） |
| 完美格挡反击 `BlockCounter_*` | ✅ 已实现（轻击 2 段 + 重击 2 段） | （12） |
| 普通格挡受击 `BlockHit` | ✅ 已实现 | （13） |
| 上半身分离（UpperBody Slot） | ✅ 已实现（下半身层未实现） | （13.5） |
| 格挡破防 `GuardBreak` | ✅ 已实现 | （14） |
| 火花 / 后处理爆闪 / 敌人被弹开 / 手柄震动 | ⬜ 未开始 | （11.6） |

#### （1）完美格挡与完美闪避的定位差别

| 项 | 完美闪避 | 完美格挡 |
| --- | --- | --- |
| 判定条件 | 无敌帧内**且**处于完美窗口 | 格挡中 + **正面** + `Poise > 0` + 处于完美窗口 |
| 判定位置 | `ReceiveDamage` 第 ② 条 | `ReceiveDamage` 第 ③ 条 |
| 结果 | `Ignore` 完全不受伤 | `Blocked` 完全不受伤（免伤） |
| 后续奖励 | 慢动作 + 残影 + 反击窗口 | 顿帧 + 强震屏 + **FOV 特写** + 退出格挡 + 清 CD + 反击窗口 |
| 感知核心 | **时间变慢** | **空间撞击** |
| 反击窗口 | `Counter_*` | `BlockCounter_*` |
| 窗口优先级 | 高 | 低 |

```
两者共用同一套「反击窗口」机制，只在两个地方分叉：
   ① 开窗时传的 E_CounterType（Dodge / Block）
   ② GetAttackRowPrefix 选的行名前缀
```

**⭐ 完美闪避优先级更高（`E_CounterType.Dodge` > `E_CounterType.Block`）：**

```
完美闪避要求无敌帧恰好覆盖判定点，条件更苛刻
→ 如果两种窗口冲突（例如闪避收尾瞬间正好完美格挡），以闪避为准
→ 实现方式是 OpenCounterWindow 里 Block 不覆盖 Dodge
```

#### （2）判定：复用 `ReceiveDamage` 已有输出

**不新增判定函数。`BPI_Attribute.ReceiveDamage` 第 ③ 条已经返回 `bPerfectBlock`：**

```
③ 格挡 + 正面 + Poise > 0
     IsPerfectBlock() == true   → Blocked + bPerfectBlock = true（免伤）
     否则                       → Blocked，伤害 ×(1−GuardDamageRate)，削轫 ×GuardPoiseRate
```

**⭐ 所以"判定"这件事本来就完成了，本节要补的是**判定成功之后发生什么**。**

**完美窗口是区间，不是"架刀瞬间即完美"（`BPC_Attribute.IsPerfectBlock`）：**

```
IsPerfectBlock() → bool
  ├─ bIsGuarding == false → false
  └─ Elapsed = Get Game Time in Seconds − LastGuardTime
       Elapsed InRange [PerfectGuardWindowStart, PerfectGuardWindowEnd] → true
       否则 → false
```

| 变量（`BPC_Attribute`） | 类型 | 说明 |
| --- | --- | --- |
| `LastGuardTime` | float | `EnterGuard` 时记录 |
| `PerfectGuardWindowStart` | float | 完美窗口起点（架刀后 N 秒，**大于 0 —— 架刀瞬间不算完美**） |
| `PerfectGuardWindowEnd` | float | 完美窗口终点 |

```
调参起点（非定论）：
  Start = 0.08~0.12   给物理反应时间，架刀瞬间受击是普通格挡
  End   = 0.25~0.30   窗口总长 0.15~0.2s
  窗口太长 → 完美格挡烂大街；太短 → 靠运气
```

**⚠️ 旧的单值变量 `PerfectGuardWindow` 已删除，不要残留 —— 判定口径只能有一处（`IsPerfectBlock`），`ReceiveDamage` 里不要重复写区间计算。**

**`ReceiveDamage` 的五个输入里，本节只用到两个位置：**

```
攻击者位置  → 判「从哪个方向来」→ 决定正面 / 背面格挡     ← 判定用
HitPoint    → 判「打在哪里」   → 火花 / 震屏 / 特写锚点   ← 表现用
```

**⚠️ `HitPoint` **不参与判定**，只在完美格挡时透传给 `OnPerfectBlock`。**

```
ReceiveDamage 第 ③ 条，完美命中且本轮未奖励：
   bPerfectBlockUsed == false ?
      → bPerfectBlockUsed = true
      → Broadcast OnPerfectBlock(HitPoint)      ← 带 Vector3，给表现层做锚点
   return (Blocked, true, false)
```

**⭐ `OnPerfectBlock` 从无参数改为 `Vector3（HitPoint）` —— 表现层需要接触点才能把火花和震屏放对位置。**

**⚠️ 改分发器签名后，`BPC_Combat` 里旧的绑定会**静默断开**，编辑器不报错，表现是"完美格挡的所有反馈全部消失"。改完必须进 `BeginPlay` 确认绑定线还在。**

#### （3）防重复：`bPerfectBlockUsed`

**和 `bPerfectDodgeUsed` 完全同构。**

| 变量 | 所在 | 类型 | 默认 | 说明 |
| --- | --- | --- | --- | --- |
| `bPerfectBlockUsed` | `BPC_Attribute` | bool | false | 本轮格挡段是否已奖励过完美 |

```
EnterGuard()        → bPerfectBlockUsed = false     进入格挡时复位
完美格挡判定成功     → 只有 false 时才广播，然后置 true
```

**为什么必须有：**

```
敌人三连击，第一段完美格挡、第二三段仍在完美窗口内
→ 没有这个标志会连续触发三次：三次退格挡、三次清 CD、三次开窗、三次震屏
```

**⚠️ 和 `bPerfectDodgeUsed` 一样，它是"一次格挡段只奖励一次"的唯一保证。不能靠"格挡已经退出了"兜底 —— 判定发生在退出之前。**

#### （4）判定成功后发生什么：判定层只广播，战斗层才动作

**判定层（`BPC_Attribute`）只做两件事：置 flag、广播带 `HitPoint`。所有收尾与反馈都不在这一层。**

**`BPC_Combat` 绑了 `OnPerfectBlock`，`HandlePerfectBlock(HitPoint)` 按固定顺序做五步：**

```
HandlePerfectBlock(HitPoint)                        【内部函数】BPC_Combat
  ├─【1】退出格挡
  │        → BPI_Attribute.ExitGuard()              【接口】
  │        → BPI_ActionState.SetState(Locomotion)   【接口】
  ├─【2】BPI_ActionState.ClearGuardCD()             【接口】清格挡 CD（防御性，见（5））
  ├─【3】OpenCounterWindow(Block)                   【内部函数】开格挡反击窗口
  ├─【4】BPI_CombatFeedBack.PlayHitFeedback(        【接口】
  │           Outcome = Blocked,
  │           ImpactLocation = HitPoint,
  │           bPerfect = true,                      ← 内部据此选 PerfectBlock 震动 + FOV 特写
  │           OtherActor = None,                    ← 防守方拿不到攻击者，见下
  │           BaseHitStop = 0)                      ← 顿帧不在这里做
  └─【5】BPI_CombatFeedBack.PlayHitStop(Self, 0.04) 【接口】只停自己
```

**⭐ 第 1~3 步必须最先执行：玩家能不能立刻反击，优先级高于所有表现。表现晚 1 帧没人察觉，反击晚 1 帧会漏输入。**

### 顿帧：双方各停自己，不在同一处调

**防守方拿不到攻击者的 `Actor`（`ReceiveDamage` 只传了攻击者的**位置**，没有传引用），所以 `PlayHitFeedback` 的 `OtherActor` 只能传 `None`，顿帧也交给双方各自处理：**

```
防守方  BPC_Combat.HandlePerfectBlock      → PlayHitStop(Self, 0.04)
攻击方  BPC_AttackTrace · bPerfectBlock    → PlayHitStop(Self, 0.04)
         分支（命中返回值判定）
```

**两个各停 0.04s，视觉上就是双方同时卡住 0.04s。**

| 方案 | 影响范围 | 问题 |
| --- | --- | --- |
| `SetGlobalTimeDilation` | 全场所有 Actor | 会影响 `Set Timer` 的游戏时间 → 反击窗口被拖长 |
| **双方各调 `PlayHitStop(Self)`** | 只有交战双方 | 不波及第三方，可单独调 ✅ |

**⚠️ 必须先确认 `PlayHitStop` 内部实现是「给传入的 Actor 设时间膨胀」。如果是「内部固定遍历全场敌人」，那 `PlayHitStop(Self, ...)` 会**静默无效**：玩家看起来根本没顿帧。**

**⭐ `OnPerfectBlock` 与 `OnPerfectDodge` 用同一个模式 —— 独立分发器、由 `BPC_Combat` 订阅，不塞进 `OnDamageApplied`。**

**⚠️ 完美格挡**不进入受击状态**：**

```
完美格挡 = 你挡住了，而且挡得漂亮
→ 玩家应该立刻能反击，不能被受击动画锁住
→ 所以 HandlePerfectBlock 里直接回 Locomotion，不走 EnterHit
```

**📌 当前进度：第 1~5 步已全部实现 —— 反馈转发与玩家侧顿帧均已接入。**

#### （5）格挡 CD：为什么需要，加在哪

**问题：** 完美格挡会强制退出格挡。如果没有任何代价，玩家可以「格挡 → 完美 → 立刻再格挡」无限循环，等于无敌。

**所以普通退出格挡要付一点冷却，而完美格挡把这个冷却免掉 —— 这才是奖励。**

| 变量 | 所在 | 类型 | 默认 | 说明 |
| --- | --- | --- | --- | --- |
| `GuardCD` | `BPC_ActionState` | float | 0.4 | 普通退出格挡后的冷却（秒） |
| `LastGuardEndTime` | `BPC_ActionState` | float | -9999 | 上次**退出格挡**的时刻 |

**派生判断（不存 bool，避免状态量泄漏）：**

```
bGuardOnCooldown = (Get Game Time in Seconds - LastGuardEndTime) < GuardCD
```

**⚠️ 时间源用 `Get Game Time in Seconds`，不用 `Tick` 的 DeltaTime 累加** —— 顿帧会把该 Actor 的 DeltaTime 压到 0，用 DeltaTime 累加会让 CD 在顿帧时停走。

**启动 / 清空路径表：**

| 路径 | 时刻 | 动作 | 语义 |
| --- | --- | --- | --- |
| 主动松开格挡 | 退出瞬间 | `ActionState.UpdateGuardCD(Now)` | 普通代价 |
| 普通格挡受击（BlockHit） | 播完保持 Guard | **不动** | 没退出格挡，不算一次"格挡结束" |
| 完美格挡（`HandlePerfectBlock`） | 判定成功 | `ActionState.ClearGuardCD()` | **奖励，免冷却** |
| 格挡被破防 | **破防 montage 播完** | `ActionState.UpdateGuardCD(Now)` | 最重惩罚 |
| 普通受击破韧 | **收尾时刻** | `ActionState.UpdateGuardCD(Now)` | 同上 |

**⚠️ 破防 / 破韧的 CD 从「收尾」起算，不能从判定瞬间起算：**  
破防 montage 锁 0.7s > GuardCD 0.4s。如果在破韧瞬间就起算，CD 会在播放期间耗光，播完回 Locomotion 立刻就能格挡，等于没有惩罚。播完后起算，破防总惩罚 = 0.7s（montage）+ 0.4s（CD）≈ 1.1s。

**⚠️ 依赖方向：** `BPC_Attribute` 是通用组件（敌人也有），不该反过来调 Player 特有的 `BPC_Combat`。所以 "启动 CD" 这件事放在 `BPC_ActionState`（状态层），`BPC_Combat` 只负责在合适的时机调用它。

#### （6）格挡入口：只在原流程前加一道门槛

**原流程（不动）：**

```
TryEnterState(Guard) → Attribute.EnterGuard() → 锁定动作
```

**新增门槛（`BPC_Combat.TryGuard`）：**

```
TryGuard() → bool
  ├─【1】ActionState.CanGuard() == false ?
  │        → ReturnValue = false       ← CD / 受控状态，一次判断全拦
  ├─【2】GetActionState() == Guard ?
  │        → ReturnValue = false       ← 已在格挡（状态查重）
  ├─【3】TryEnterState(Guard)
  │        ├─ false → ReturnValue = false   ← 转场矩阵拒绝（受控状态兜底）
  │        └─ true  → 继续
  ├─【4】Attribute.EnterGuard()          ← bIsGuarding = true，bPerfectBlockUsed = false
  └─【5】ReturnValue = true
```

**⚠️ 第 1 步放在 `CanGuard` 里做，把 CD + 受控状态合并判断；第 2 步保留在 `TryGuard` 做状态查重。**

**⚠️ 第 1 步用 `ActionState.CanGuard()`，不要在 `TryGuard` 里自己读 `bGuardOnCooldown`（该变量不存在于 `BPC_Combat`，只在 `BPC_ActionState` 内部派生）。**

**⭐ 玩家蓝图里不加任何新变量 —— `GuardCD` / `LastGuardEndTime` 全在 `BPC_ActionState` 内部，外部只调 `TryGuard()`（启动）与 `ActionState.UpdateGuardCD` / `ClearGuardCD`（收尾）。**

#### （7）完整时间轴

```
t = 0.00   按下格挡
           ├─ BPI_Combat.TryGuard()
           │    ├─ ActionState.CanGuard() == true ✅   ← CD + 受控状态
           │    ├─ GetActionState() != Guard ✅        ← 状态查重
           │    └─ TryEnterState(Guard) → EnterGuard()
           │         └─ bIsGuarding = true，bPerfectBlockUsed = false
           └─ 进入格挡，锁定动作

t = 0.10   敌人攻击命中
           └─ ReceiveDamage 第 ③ 条
                ├─ 正面 ✅  Poise > 0 ✅  IsPerfectBlock() ✅
                ├─ bPerfectBlockUsed == false → 置 true → Broadcast OnPerfectBlock(HitPoint)
                └─ Return (Blocked, true, false)

           OnPerfectBlock(HitPoint) → HandlePerfectBlock()
                ├─【1】退出格挡 → 回 Locomotion
                ├─【2】ActionState.ClearGuardCD()      CD 清空
                ├─【3】OpenCounterWindow(Block)        窗口立刻开
                ├─【4】PlayHitFeedback(Blocked, HitPoint, true, None, 0)
                │        ├─ Shake(PerfectBlock, HitPoint, 2.0)   ← 强震屏
                │        └─ PlayPerfectBlockCloseUp()            ← FOV 收窄开始
                └─【5】PlayHitStop(Self, 0.04)                   ← 玩家顿帧

           同时（攻击方侧，BPC_AttackTrace）
                └─ 命中返回值 bPerfectBlock == true
                     ├─ PlayHitStop(Self, 0.04)                  ← 敌人顿帧
                     └─ 0.04s 后 PlayEnemySlowMo(0.15, 0.12)     ← 敌人慢速

t = 0.10 ~ 0.14  ★ 顿帧：双方同时停住
                 FOV 在这 0.04s 内从 BaseFOV 收到 BaseFOV−16
t = 0.14   顿帧结束
           ├─ 玩家恢复操作（顿帧期间按的攻击由输入缓冲接住）
           ├─ 敌人进入 0.15 倍速
           └─ FOV 保持收窄，再维持 0.06s
t = 0.20   敌人慢速结束，恢复 1.0
t = 0.20 ~ 0.45  FOV 平滑回位到 BaseFOV
t = 0.10 ~ 0.90   ★ 格挡反击窗口
           按轻击 → BlockCounter_L1 → L2 → 空
           按重击 → BlockCounter_H1 → H2 → 空
t = 0.90   CloseCounterWindow() → CounterType = None
```

**⭐ 三个时间量的关系要记清：**

| 量 | 区间 | 驱动 |
| --- | --- | --- |
| 顿帧 | `0.10 ~ 0.14` | `PlayHitStop` 的 `CustomTimeDilation` |
| 敌人慢速 | `0.14 ~ 0.26` | `PlayEnemySlowMo(0.15, 0.12)` |
| FOV 特写 | `0.10 ~ 0.45` | `PlayPerfectBlockCloseUp`（三段） |

**⚠️ 顿帧和敌人慢速必须**串行**，不能同时开：同时开的话慢速期间的 `CustomTimeDilation` 又被顿帧覆盖，`0.12s` 的计时会被拖长到看不出效果。**

**⭐ 窗口从**完美格挡那一刻**开始算（不是像闪避那样从收尾算）：**

```
完美格挡没有"锁在动作里"的收尾期
→ 玩家在 t=0.10 就已经能动
→ 窗口必须从这一刻开始计时，否则等于白送 0.25s
```

#### （8）涉及变量与接口

> **函数类型标注**：**【接口】** = 定义在 `BPI_xxx` 里，跨组件调用必须走它；**【接口实现】** = `BPC_xxx` 里实现某个 `BPI` 函数；**【内部函数】** = 组件自己的函数，外部不可调；**【事件】** = 分发器 / 自定义事件，不占接口计数；**【引擎 API】** = UE 自带节点。

**`BPC_Attribute`：**

| 名称 | 类型 | 说明 |
| --- | --- | --- |
| `bPerfectBlockUsed` | bool | `EnterGuard` 复位，一次格挡段只奖励一次 |
| `OnPerfectBlock(Vector3)` | **【事件】** 分发器 | 判定成功时广播，参数为 `HitPoint` |
| `EnterGuard` / `ExitGuard` | **【接口实现】** 现有 | 内部逻辑不动 |
| `LastGuardTime` | float | `EnterGuard` 时记录，完美窗口区间的起点参照 |
| `PerfectGuardWindowStart` / `PerfectGuardWindowEnd` | float | 完美窗口区间（**已取代旧的单值 `PerfectGuardWindow`**） |
| `IsPerfectBlock()` | **【内部函数】** | `bIsGuarding` + 区间判断，判定口径唯一入口 |

**`BPC_ActionState`（格挡 CD 在此，与闪避 CD 对称）：**

| 名称 | 类型 | 说明 |
| --- | --- | --- |
| `GuardCD` | float | 0.4 |
| `LastGuardEndTime` | float | -9999（**退出**格挡的时刻，不是起手） |
| `CanGuard()` | **【接口实现】** | CD + 受控状态判断 |
| `UpdateGuardCD(Time)` | **【接口实现】** | 记录退出时刻（启动 CD） |
| `ClearGuardCD()` | **【接口实现】** | 清空（完美格挡调用） |

**`BPC_Combat`：**

| 名称 | 类型 | 说明 |
| --- | --- | --- |
| `CounterType` | `E_CounterType` | 替代原 `bCounterWindowOpen` |
| `CounterTypeUsed` | bool | 替代原 `bCounterUsed` |
| `TryGuard()` | **【接口实现】** | 门槛（CanGuard + 状态查重 + TryEnterState） |
| `HandlePerfectBlock(HitPoint)` | **【内部函数】** | 退格挡 + 清 CD + 开窗 + 顿帧 + 转发反馈 |

**`BPI_ActionState`：**

| 方法名 | 输入 | 输出 | 作用 |
| --- | --- | --- | --- |
| `CanGuard` | / | bool | **【接口】** CD 与受控状态判断 |
| `UpdateGuardCD` | float（Time） | / | **【接口】** 启动格挡 CD（记录退出时刻） |
| `ClearGuardCD` | / | / | **【接口】** 清空格挡 CD（完美格挡奖励） |

**`BPI_Combat`：**

| 方法名 | 输入 | 输出 | 作用 |
| --- | --- | --- | --- |
| `TryGuard` | / | bool | **【接口】** 格挡入口：`CanGuard` + 状态查重 + 进状态 + `EnterGuard` |

> `SetLastGuardEndTime` 已删除（接口与实现），格挡 CD 相关调用全部改走 `BPI_ActionState` 三个新接口。

**`BPC_CameraDirector`（FOV 特写）：**

| 名称 | 类型 | 默认 | 说明 |
| --- | --- | --- | --- |
| `BaseFOV` | float | 0 | `BeginPlay` 从 `CameraComponent` 缓存一次 |
| `CloseUpFOVDelta` | float | 16 | 收窄度数 |
| `CloseUpInTime` | float | 0.04 | 收窄时长，与顿帧同步 |
| `CloseUpHoldTime` | float | 0.06 | 保持时长 |
| `CloseUpOutTime` | float | 0.25 | 回位时长 |
| `CloseUpPhase` | `E_CloseUpPhase` | `None` | `None` 兼作空闲态，不需要额外 `bCloseUpActive` |
| `CloseUpPhaseStartTime` | float | 0 | World 时间戳 |
| `TargetFOV` | float | 0 | |

**`BPI_CameraDirector`（本次新增 1 个）：**

| 方法名 | 输入 | 输出 | 作用 |
| --- | --- | --- | --- |
| `PlayPerfectBlockCloseUp` | / | / | **【接口】** 完美格挡 FOV 特写：收窄 → 保持 → 回位 |

**⭐ `PlayPerfectBlockCloseUp` 必须是【接口】而不是【内部函数】—— `BPC_CombatFeedBack` 要跨组件调用它，按分层约定跨组件调用必须走 `BPI_CameraDirector`。**

**`BPI_CombatFeedBack`（已有，本次新增 2 个）：**

| 方法名 | 输入 | 输出 | 变化 |
| --- | --- | --- | --- |
| `PlayEnemySlowMo` | float（Scale），float（Duration） | / | 原 `PlayPerfectDodgeSlowMo` 改名 + 加参数。**完美闪避传 (0.1, 0.5)，完美格挡传 (0.15, 0.12)**。**音效已移出，只调时间膨胀** |
| `PlayHitStop` | Actor，float | / | 现有。**只对传入的 Actor 生效 —— 防守方传 `Self`，攻击方也传 `Self`** |
| `PlayPerfectDodgeStartSound` | float（Duration） | / | **【接口】新增**。播开始音 + 内部计时 → Duration 后自动播结束音 |
| `PlayPerfectBlockSound` | / | / | **【接口】新增**。完美格挡撞击音，单一瞬态 |

**`BPC_CombatFeedBack` 的音效变量与内部函数：**

| 名称 | 类型 | 说明 |
| --- | --- | --- |
| `PerfectDodgeStartSound` | `USoundBase` | 完美闪避开始音 |
| `PerfectDodgeEndSound` | `USoundBase` | 完美闪避结束音 |
| `PerfectDodgeEndSoundVolume` | float | 结束音音量 |
| `PerfectDodgeSoundTimer` | Timer Handle | 开始音 → 结束音的计时器 |
| `PerfectBlockSound` | `USoundBase` | 完美格挡撞击音 |
| `PlayPerfectDodgeEndSound()` | **【内部函数】** | 计时器回调，播结束音 |

**`DT_Attacks`：** 轻击 `BlockCounter_L1~L2` + 重击 `BlockCounter_H1~H2`，共 4 行；与闪避反击（轻 4 + 重 3）有意区分。格挡反击链路已打通，见（12）。

**`E_CounterType`：** 新建枚举，`None` / `Block` / `Dodge`。

**`E_CloseUpPhase`：** 新建枚举，`None` / `In` / `Hold` / `Out`。

**⭐ `E_CameraShakeType` 里已经有 `PerfectBlock` 与 `Block`，不需要新增。**

#### （9）验证

```
【判定】
□ 正面格挡 + 完美窗口内 → 退回格挡、清 CD、开 Block 窗口
□ 架刀瞬间（窗口 Start 之前）被打 → 普通格挡，不是完美（区间起点生效）
□ 窗口 End 之后被打 → 普通格挡（区间终点生效）
□ 三连击都在完美窗口内 → 只触发一次完美（bPerfectBlockUsed）
□ 背面被打 → 不触发完美格挡
□ Poise == 0 → 不触发完美格挡

【格挡 CD】
□ 主动松开格挡后 0.4s 内按格挡 → TryGuard 返回 false
□ 0.4s 后按格挡 → 正常进入
□ 完美格挡后立刻按格挡 → 正常进入（CD 已清）
□ 完美格挡后松开格挡键 → 不启动 CD（松开路径有「当前在 Guard」前提）
□ 已在格挡中再按格挡 → TryGuard 返回 false
□ 顿帧期间 CD 照常流逝（时间源为 World 时间）

【反击窗口】
□ 完美格挡后轻击 → BlockCounter_L1 → L2
□ 完美格挡后重击 → BlockCounter_H1 → H2
□ 窗口过期后轻击 → Attack1
□ 完美闪避在 Block 窗口期间触发 → CounterType 变 Dodge（闪避优先）
□ Block 守在 Dodge 窗口期间触发 → CounterType 保持 Dodge，不降级
□ 挨打 / 死亡 / 重新闪避 / 跳跃 → 窗口关闭

【接口数】
□ BPI_ActionState +3（CanGuard / UpdateGuardCD / ClearGuardCD）
□ BPI_Combat −1（删 SetLastGuardEndTime）
□ BPI_CameraDirector 不变（PlayPerfectBlockCloseUp 已计入 2 个）
□ 当前总数以「0，接口总览」为准
```

#### （10）六个最容易写错的点

```
① OnPerfectBlock 必须独立于 OnDamageApplied
   OnDamageApplied 的参数里没有 bPerfectBlock（第三个 bool 是轻重等级）
   不要为了省一个分发器去塞进它的签名 —— 所有绑定点都要跟着动
   但 OnPerfectBlock 自己的签名已从「无参数」改为 Vector3(HitPoint)
   ⚠️ 改分发器签名后旧绑定静默断开，不报错，只表现为「反馈全部消失」
   改完必须进 BPC_Combat.BeginPlay 确认绑定线还在

② 完美格挡不要走 EnterHit
   走了就会锁在受击动画里，反击窗口等于白送
   HandlePerfectBlock 直接回 Locomotion

③ 格挡入口判断"是否已在格挡"要用 ActionState，不是 bIsGuarding
   但"受击结束后要不要回格挡"必须用 bIsGuarding（那时 ActionState 已经不是 Guard）

④ LastGuardEndTime 只能通过 ActionState.UpdateGuardCD / ClearGuardCD 修改
   格挡 CD 已迁入 BPC_ActionState（与闪避 CD 对称三件套），
   BPC_Combat 不再持有 GuardCD / LastGuardEndTime 变量

⑤ 顿帧不要用 SetGlobalTimeDilation，双方各调 PlayHitStop(Self)
   GlobalTimeDilation 会拖慢 Set Timer 的游戏时间 → 反击窗口被拉长
   且会一并冻住远处敌人的动画、粒子、音效

⑥ PlayPerfectBlockCloseUp 必须是【接口】不是【内部函数】
   BPC_CombatFeedBack 跨组件调用它，按分层约定必须走 BPI_CameraDirector
```

#### （11）反馈：震屏 + FOV 特写

> **范围**：本节只写**震屏**、**音效**与**FOV 特写**三项。火花 / 后处理爆闪 / 敌人被弹开 / 手柄震动暂不设计 —— 等这三项的手感确认之后再补，否则一次改太多分不清是哪个起的作用。
>
> **进度**：震屏 ✅ 已接入；撞击音 ✅ 已接入（`PlayPerfectBlockSound`）；FOV 特写 ✅ 已接入 `PlayHitFeedback` 的 `bPerfect` 分支 —— 三项反馈已全部打通。详见下文【11.3 触发链路与当前进度】。

##### 设计原则：和完美闪避彻底分开

```
完美闪避 = "我从时间里溜走了"  → 时间被拉长，画面变冷，人闪走了
完美格挡 = "我把你的攻击撞回去了" → 时间不变，空间被压缩，人站住了
```

| 维度 | 完美闪避 | 完美格挡 |
| --- | --- | --- |
| 核心感知 | 时间变慢 | **空间撞击** |
| 时间处理 | 长慢动作 `0.5s` | 极短 `0.12s`（只弹住敌人） |
| 镜头 | 轻震，慢频率 | **强震 + FOV 收窄特写** |
| 震屏资产 | `BPCS_PerfectDodge` | `BPCS_PerfectBlock` |

**⭐ 所以完美格挡的全部反馈都应该是「短、硬、有方向」，绝不能加慢动作长尾 —— 那是闪避的语言。**

##### 11.1 震屏：改 `BPCS_PerfectBlock`

**资产内确认是 `CameraShakeBase` + `PerlinNoiseCameraShakePattern`。**

**Perlin 模式的参数单位必须记清：**

```
Location  Amplitude → 厘米
Rotation  Amplitude → 度
FOV       Amplitude → 度
```

**⚠️ Perlin 的 `Amplitude` 是**单值**，Location 的 X/Y/Z 用同一振幅（三个不同噪声通道，方向随机）。想给 Yaw / Pitch 不同振幅，Perlin 做不到，必须换 Legacy Camera Shake。**

| 参数 | 值 | 理由 |
| --- | --- | --- |
| `Duration` | `0.20` | 短促，超过 0.3 就变"晃" |
| `BlendInTime` | `0.00` | **必须 0**，第 0 帧就是满振幅 |
| `BlendOutTime` | `0.18` | 几乎全程衰减，接近冲击型 |
| `Location.Amplitude` | `1.2` | **基准值**，实际由 Scale 放大 |
| `Location.Frequency` | `15` | 中高频，抖得密 |
| `Rotation.Amplitude` | `0.8` | **基准值** |
| `Rotation.Frequency` | `12` | 比位置稍慢，避免"抽搐" |
| `FOV.Amplitude` | `0` | 不用 Perlin 做 FOV，交给 `PlayPerfectBlockCloseUp` 的三阶段插值精确控制 |

**⭐⭐ 现在震动"不够大"，最可能的原因不是振幅小，而是 `BlendInTime` 有值：**

```
BlendInTime = 0      → 第 0 帧就是满振幅           ← 冲击型必须这样
BlendInTime > 0      → 振幅从 0 慢慢涨上来          ← 只适合持续型震动
```

**完美格挡的感知窗口只有 0.1s 左右，`BlendInTime` 只要有值，大半时间都在渐入 —— 等于振幅白配。**

**⭐ 频率不是越低越"重"：**

```
1~5 Hz    缓慢摇晃，像坐船 → 晕，但不"重"
10~20 Hz  明显抖动        → 撞击感       ← 这里
30 Hz+    细密震颤，像手机 → 不"重"
```

**撞击感来自「大振幅 + 快速衰减 + 中高频」，不是低频。**

**⭐ 最终震动强度是「三层相乘」，调的时候只改一层：**

```
最终振幅 = 资产内 Amplitude × Shake_Multiplier × Shake 的 Strength 参数
```

```
资产 Amplitude    配基准（1.2 / 0.8）
Shake_Multiplier  保持 1.0
只调 Strength 参数    完美格挡 2.0，普通格挡 1.0
```

**⚠️ 不要把振幅直接配到最大再传 Scale 2.5 —— 那样实际是 7.5cm，会晕。超过 3.5 基本必晕。**

**⚠️ `BPCS_PerfectDodge` 已从原 `BPCS_Perfect` 拆分出来，但参数暂不调整 —— 现在沿用拆分时的默认值，与 `BPCS_PerfectBlock` 尚未拉开差异，等格挡手感确认之后再改。**

##### 11.2 FOV 特写：新增 `PlayPerfectBlockCloseUp`【接口】

**为什么 FOV 特写比单纯震屏有效：**

```
震屏   = 相机"抖"   → 幅度上的冲击
FOV 收窄 = 视野"聚焦" → 空间上的压迫感

两者叠加 = "这一击把世界压缩了"
而且和顿帧天然咬合：顿帧让时间停住，FOV 让空间收拢
两个维度同时"收紧"，比单独任何一个都强
```

**参数：**

| 参数 | 值 | 说明 |
| --- | --- | --- |
| `BaseFOV` | 运行时读取 | `BeginPlay` 从 `CameraComponent` 缓存一次 |
| `CloseUpFOVDelta` | `16` | 收窄度数 |
| `CloseUpInTime` | `0.04` | 和顿帧同步，快速收拢 |
| `CloseUpHoldTime` | `0.06` | 保持 |
| `CloseUpOutTime` | `0.25` | 平滑回位 |
| 总时长 | `0.35` | |

**⚠️ 收窄幅度：**

```
10 度   有感觉但不明显
16 度   明显特写，不晕        ← 这里
20 度   开始有压迫感，部分人会晕
25 度+  晕，且视野太窄，看不到其他敌人
```

**⚠️ 总时长不能超过 0.4s —— 特写期间视野变小，看不到侧后方的攻击。**

**实现位置：`BPC_CameraDirector`（ActorComponent）。**

**⚠️ ActorComponent 蓝图里不能用 Timeline 节点：**

```
Blueprint 的 Timeline 节点依赖 UTimelineComponent 作为成员
而 Add Component(Timeline) 只在 Actor 蓝图里提供
→ ActorComponent / SceneComponent 蓝图里右键搜不到 Timeline

替代方案：TickComponent 手动插值
（Set Timer by Event 在 ActorComponent 里是可用的，所以顿帧 / 慢动作的恢复不受影响）
```

**`PlayPerfectBlockCloseUp()`【接口实现】：**

```
PlayPerfectBlockCloseUp()
  ├─【1】Branch: CloseUpPhase != None → Return        ← 防重入
  ├─【2】TargetFOV = BaseFOV − CloseUpFOVDelta
  ├─【3】CloseUpPhase = In
  └─【4】CloseUpPhaseStartTime = Get Game Time in Seconds
```

**`TickComponent` 三阶段插值：**

```
TickComponent(DeltaTime)
  └─ Branch: CloseUpPhase == None → Return
     │
     ├─ Now = Get Game Time in Seconds                 【引擎 API】
     ├─ Elapsed = Now − CloseUpPhaseStartTime
     │
     └─ Switch on E_CloseUpPhase
        ├─ In:
        │    ├─ Alpha = Saturate(Elapsed / CloseUpInTime)
        │    ├─ CameraRef → Set Field of View(Lerp(BaseFOV, TargetFOV, Alpha))   【引擎 API】
        │    └─ Branch: Alpha >= 1.0 → CloseUpPhase = Hold，StartTime = Now
        │
        ├─ Hold:
        │    ├─ CameraRef → Set Field of View(TargetFOV)
        │    └─ Branch: Elapsed >= CloseUpHoldTime → CloseUpPhase = Out，StartTime = Now
        │
        └─ Out:
             ├─ Alpha = Saturate(Elapsed / CloseUpOutTime)
             ├─ CameraRef → Set Field of View(Lerp(TargetFOV, BaseFOV, Alpha))
             └─ Branch: Alpha >= 1.0
                  ├─ CameraRef → Set Field of View(BaseFOV)     ← 必须显式回位
                  └─ CloseUpPhase = None
```

**⭐⭐ 必须用 `Get Game Time in Seconds`，不能用 Tick 的 `DeltaTime` 累加：**

```
完美格挡会 PlayHitStop(Self, 0.04)
  → 玩家 Actor 的 CustomTimeDilation 被设成 0
  → 挂在玩家身上的 BPC_CameraDirector 的 TickComponent 的 DeltaTime 也变 0
  → 如果 Elapsed += DeltaTime，顿帧的 0.04s 里 Elapsed 完全不增长
  → FOV 收窄被"冻住"，顿帧结束后才开始收
  → 结果：先抖一下，然后才拉近 —— 冲击感全散
```

| 时间源 | 受 `GlobalTimeDilation` | 受 `CustomTimeDilation` | 能用吗 |
| --- | --- | --- | --- |
| `DeltaTime`（Tick 入参） | 受影响 | **受影响** | ❌ |
| `Get Game Time in Seconds` | 受影响 | **不受影响** | ✅ |
| `Get Real Time Seconds` | 不受影响 | 不受影响 | ✅ 也可用 |

**⭐ `CustomTimeDilation` 只作用于单个 Actor，不影响 `UWorld::GetTimeSeconds()`。所以用 World 时间戳做差，顿帧期间 FOV 照常收窄 —— 这才是"同时开始"的感觉。**

**⚠️ 如果将来改用 `GlobalTimeDilation` 做顿帧，`Get Game Time in Seconds` 也会被拖慢，那时必须换成 `Get Real Time Seconds`。**

**⚠️ `Out` 阶段结束必须显式 `Set Field of View(BaseFOV)`：靠 Lerp 到 1.0 理论值相同，但浮点残差会在连续触发几十次后看出来。**

**`BeginPlay` 缓存：**

```
BeginPlay
  ├─ CameraRef = BPI_Player.GetCameraComponent()          【接口】
  └─ BaseFOV   = CameraRef → Field of View               【引擎 API】
```

**⚠️ 不能在 `TickComponent` 里读"当前 FOV"当起点 —— 连续两次完美格挡，第二次的起点已经是 74 了，会越收越小。**

##### 11.3 触发链路与当前进度

**实际链路（已打通）：**

```
BPC_Combat · HandlePerfectBlock(HitPoint) 【内部函数】
  ├─ BPI_CombatFeedBack.PlayHitFeedback(Blocked, HitPoint, true, None, 0)  【接口】
  │    └─ Branch: bPerfect == true
  │         ├─ BPI_CameraDirector.Shake(PerfectBlock, ImpactLocation, 2.0)      【接口】
  │         ├─ BPI_CameraDirector.PlayPerfectBlockCloseUp()                     【接口】
  │         └─ BPI_CombatFeedBack.PlayPerfectBlockSound()                       【接口】
  └─ BPI_CombatFeedBack.PlayHitStop(Self, 0.04)                                 【接口】
```

**⭐ `ImpactLocation` 传 `HitPoint` 而不是角色位置 —— 震屏会朝接触点方向偏，有"来向感"。**

**当前实现进度：**

| 环节 | 归属 | 状态 |
| --- | --- | --- |
| `BPI_CameraDirector.PlayPerfectBlockCloseUp`（接口声明） | `BPI_CameraDirector` | ✅ 已完成 |
| `PlayPerfectBlockCloseUp` 实现 + `TickComponent` 三阶段插值 | `BPC_CameraDirector` | ✅ 已完成 |
| 8 个 `CloseUp*` / `BaseFOV` 变量 | `BPC_CameraDirector` | ✅ 已完成 |
| `BeginPlay` 缓存 `BaseFOV` | `BPC_CameraDirector` | ✅ 已完成 |
| `PlayPerfectBlockSound()`（撞击音） | `BPC_CombatFeedBack` | ✅ 已接入 |
| `PlayEnemySlowMo(0.15, 0.12)` | `BPC_CombatFeedBack` | ✅ 已接入 |
| `PlayHitStop` 双方各停 0.04s | `BPC_Combat` / `BPC_AttackTrace` | ✅ 已接入 |
| `Shake(PerfectBlock, HitPoint, 2.0)` | `BPC_CombatFeedBack` | ✅ 已接入 |
| `PlayHitFeedback` 的 `bPerfect == true` 分支调 `PlayPerfectBlockCloseUp()` | `BPC_CombatFeedBack` | ✅ **已接入** |

**⭐ 完美格挡的三项反馈已全部打通：震动、撞击音、FOV 特写，与顿帧 / 敌人慢速同步发生。**

```
t = 0.10  判定成功
          ├─ 强震屏（第 0 帧满振幅）
          ├─ 撞击音（第 0 帧）
          ├─ FOV 收窄开始（0.04s 内收到 BaseFOV−16）
          └─ 双方顿帧 0.04s（FOV 在顿帧期间照常收窄，因为用的是 World 时间）
```

##### 11.4 验证

> **⚠️ 三项反馈已全部接入，下表可以直接在游戏里跑。**

```
【震屏】
□ 完美格挡第 0 帧就有明显位移（BlendInTime = 0 生效）
□ 0.20s 内衰减到 0，不是突然停
□ 有旋转感，不只是平移
□ Shake_Multiplier 保持 1.0，强度只靠 Strength 参数调
□ 强度 2.0 不晕，3.5 是上限

【音效】
□ 完美格挡播的是撞击音，不是完美闪避的开始音
□ 连续两次完美格挡，音高略有不同（Pitch 随机生效）
□ 完美格挡不播完美闪避的结束音

【FOV 特写】
□ 特写和顿帧同时开始（顿帧期间 FOV 仍在收窄）
□ 从 BaseFOV 收到 BaseFOV−16，再平滑回到 BaseFOV
□ 连续三次完美格挡，FOV 不会越收越小
□ 特写结束后 FOV 精确回到 BaseFOV（打印对比）
□ 特写期间能看到侧后方（视野没被压太窄）
□ 特写 + 震屏叠加不晕
□ BPC_CameraDirector / BPC_Combat / BPC_Attribute 里没有任何 Timeline 节点

【分层】
□ Combat 只调 PlayHitFeedback，没直接碰 CameraDirector
□ bPerfect == false 时走 BPCS_Block，没有特写
□ PlayPerfectBlockCloseUp 定义在 BPI_CameraDirector 里
```

##### 11.5 三个最容易写错的点

```
① BaseFOV 必须在 BeginPlay 读一次并缓存
   TickComponent 里读当前 FOV 当起点 → 连续触发会越收越小

② CloseUpPhase 的 None 兼作空闲态，不要再加 bCloseUpActive
   两个变量表达同一个状态，只要有一条路径忘了同步就会分叉，且不报错

③ 时间源必须用 Get Game Time in Seconds
   用 DeltaTime 累加的话，顿帧期间 FOV 被冻住
   → 先抖一下再拉近，冲击感全散
```

##### 11.6 暂不设计（等手感确认后再补）

```
□ 火花 / 冲击波 Niagara（沿格挡面法线，生成在 HitPoint）
□ 三层音效的细化（当前是单一撞击音，Sub 低频与混响尾未做）
□ 后处理爆闪（Bloom / Exposure / ChromaticAberration）
□ 敌人被弹开（Parried 蒙太奇 + 位移 + 0.3s 僵直，由攻击方执行）
□ 手柄震动（左右马达时长不同）
□ BPCS_PerfectDodge 参数调整（已拆分出来，暂沿用默认值）
```

#### （12）完美格挡反击：已实现

> **状态：已设计并实现。轻击 2 段 + 重击 2 段，与完美闪避反击（轻 4 + 重 3）有意区分，格挡反击更短更紧凑。**

##### 12.1 当前实际状态

**`E_CounterType.Block` 开窗之后，`GetAttackRowPrefix` 返回 `BlockCounter_`，拼上行号去 `DT_Attacks` 查。**

**`DT_Attacks` 里现有的格挡反击行（实际扫描结果）：**

| 前缀 | 轻击 | 重击 | 归属 |
| --- | --- | --- | --- |
| `Counter_*` | `Counter_L1` ~ `Counter_L4` ✅ 齐全 | `Counter_H1` ~ `Counter_H3` ✅ 齐全 | 完美闪避反击 |
| `BlockCounter_*` | `BlockCounter_L1` ~ `L2` ✅ 齐全 | `BlockCounter_H1` ~ `H2` ✅ 齐全 | 完美格挡反击 |

**⭐ 结论：**

```
完美格挡后按轻击 → L1 → L2，两段连招
完美格挡后按重击 → H1 → H2，两段连招
```

##### 12.2 数据表结构（与 `Counter_*` 同构）

| 要填的行 | 段数 | 说明 |
| --- | --- | --- |
| `BlockCounter_L1` / `L2` | 2 | 轻击反击，两段连招，`Next`：`L2` → 空 |
| `BlockCounter_H1` / `H2` | 2 | 重击反击，两段连招，`Next`：`H2` → 空 |

**每行最少要填的字段（与 `Counter_*` 保持同构）：**

```
Montage + SectionStart   格挡反击的蒙太奇段
Next                     下一段行名，末段留空
CancelStart              取消窗口起点
MotionSelf               位移（格挡反击应比闪避反击更小，人站住不动）
DamageScale / PoiseScale 伤害与削轫
```

**⭐ `Next` 链必须首尾相接：`L1→L2`、`H1→H2`，末段为空。漏一环就会出现「打到第二段就断」。**

##### 12.3 需要优化的点

```
① 位移量尚未区分（P1）
   完美闪避反击自带位移（人闪走了），格挡反击是原地站稳
   MotionSelf 应该显著小于 Counter_*，甚至为 0

② 段数与闪避反击不对称（P2）
   闪避反击 轻 4 + 重 3 = 7 行；格挡反击 轻 2 + 重 2 = 4 行
   这是有意设计：格挡后硬直更短，反击更快结束

③ 命中反馈未区分（P2）
   格挡反击应该更"重"：更强震屏 + 更重的受击音
   目前沿用的是普通攻击的反馈
```

##### 12.4 验证顺序

```
① 完美格挡 → 按轻击 → L1→L2 两段都能打出
② 完美格挡 → 按重击 → H1→H2 两段都能打出
③ 窗口过期后按攻击 → 回落 Attack1（不是 BlockCounter）
④ 完美格挡 → 按轻击 → 再按重击 → 确认不会混链
⑤ 敌人三连击全完美格挡 → 只触发一次开窗（bPerfectBlockUsed）
```

##### 12.5 兜底行为待确认

**行名找不到时 `GetAttackRowPrefix` 的返回值，目前文档未记录。** 建议明确两条之一：

```
方案 A：找不到行 → 回落到 Attack1（玩家至少能出招，不"卡住"）
方案 B：找不到行 → 不出招，但打 Print Warning（开发期暴露问题）
```

**⭐ 开发期用 B，发布前改 A。这样缺行不会被静默吞掉。**

#### （13）普通格挡受击：已实现（轻受击）

> **状态：已实现（暂只有轻受击一种）。** 链路：`OnDamageApplied(Blocked)` → `HandleGuardHit` → 查 `DT_Reactions` 的 `BlockHit` 行 → 播蒙太奇，播完保持格挡。

##### 13.1 链路

```
敌人攻击命中玩家（被格挡）
   ↓
BPC_Attribute.ReceiveDamage 第 ③ 条
  格挡 + 正面 + Poise>0 + 不在完美窗口 → Blocked
   ↓
OnDamageApplied.Broadcast(Blocked, HitDirection, bPoiseBroken)
   ↓
BPC_Combat 分流（按 HitOutCome）
   ├─ Hit     → EnterHit（受击硬直）
   └─ Blocked → HandleGuardHit
                  ├─ DT_Reactions 查 "BlockHit" 行
                  └─ PlayReactionMontage(Data, bReliefOriginal = true)
                       └─ 播完：true → 什么都不做（保持 Guard）；false → SetState(Locomotion)
```

**`bReliefOriginal` 复用**：`EnterHit` 也调 `PlayReactionMontage`，传 `false` → 播完回 Locomotion；格挡受击传 `true` → 播完保持原状态（Guard）。两个场景共用一条播放链路，只在「播完去哪」分叉。

**⚠️ `OnDamageApplied` 不是 100% 触发：** 完美格挡（走 `OnPerfectBlock`）、完美闪避、无敌帧、死亡都不触发。但需要受击反馈的两种情况（Hit / Blocked）恰好都会触发，所以分流入口正确。

##### 13.2 数据：DT_Reactions

**新表，复用 `ST_AttackData` 结构（为省事，不另建结构体）。**

```
行：HitLight_Front / HitLight_Back / HitLight_Left / HitLight_Right
    HitHeavy_Front / HitHeavy_Back / HitHeavy_Left / HitHeavy_Right
    BlockHit
```

**查表规则：** `EnterHit` 按 `HitType + "_" + HitDirection` 拼行名（如 `HitLight_Front`）；格挡固定查 `BlockHit`，不分方向。

**⚠️ 反应表只读以下字段，其余字段不生效（复用结构体的冗余）：**

| 生效字段 | 用途 |
| --- | --- |
| `Montage` | 反应动画 |
| `SectionStart` | 动画起始段 |
| `LaunchSelf` | 自身击退位移 |
| `MotionSelf` | 自身姿态位移 |
| `MoveSpeed` | 位移速度 |
| `MoveFriction` | 位移摩擦 |

```
不生效：DamageRate / PoiseDamageRate / Next / CancelStart / HitStop /
        LaunchEnemy / CanLaunchAir / PlayGravity
→ 反应行是“受击表现”，不是“出招”；填了攻击字段也不会被读取
```

**`BlockHit` 只有一行、不分方向** —— 格挡只存在正面受击（判定层保证），不存在左右后的格挡，不需要方向变体。

##### 13.3 三向分流（互不交叉）

| 情况 | 走哪条路 | 经过 HandleGuardHit |
| --- | --- | --- |
| 完美格挡 | `OnPerfectBlock` → `HandlePerfectBlock` | ❌ |
| 普通格挡（未破韧） | `OnDamageApplied(Blocked)` → `HandleGuardHit`（PoiseBroken=false） | ✅ |
| 格挡被破防 | `OnDamageApplied(Blocked)` → `HandleGuardHit`（PoiseBroken=true）→ 破防分支 | ✅（内部再分，见（14）） |
| 完美闪避 / 无敌帧 / 死亡 | 不触发 `OnDamageApplied` | ❌ |

**所以 `HandleGuardHit` 会收到两条路径（普通 / 破防），在内部按 `PoiseBroken` 二分：破防走（14），普通走本节。**

##### 13.4 交互约束

```
不能移动      播 montage 期间（格挡受击是站桩）
不能取消      反应表的 CancelStart 不生效（仅为复用结构体）
无自身顿帧    顿帧由攻击方 PlayHitFeedback 产生（与玩家攻击命中敌人一致）
震屏          攻击方（敌人）调 PlayHitFeedback(Blocked) → Shake(Block)
              → CombatFeedBack 无条件取【玩家】CameraDirector → 震到玩家镜头
              ⚠️ 不在 HandleGuardHit 里重复调，否则一格挡震两次
Delegate       OnCompleted / OnBlendOut 在 BeginPlay 绑定一次，不每次播放都绑
```

##### 13.5 上半身分离（已实现，下半身未分离）

> **范围说明：目前只实现了上半身分离（`UpperBody` Slot），下半身层（`LowerBody` Slot）尚未实现。** 现有需求（格挡受击）只需要上半身，下半身层留到出现「下半身动作 montage」需求（如滑铲、蹲扫）时再加，结构与上半身层对称，见本节末尾。

**问题**：所有 montage 走 `DefaultSlot`（全身），格挡受击时下半身被 montage 接管，玩家移动输入仍推进 → 滑步。

**已实现的 AnimGraph 结构（ABP_Player，上半身层）：**

```
StateMachine（Locomotion / BlockStart / BlockState ...）
   ↓
Save Cached Pose "MainPose"        ← 只存状态机输出，不含 DefaultSlot
   ↓
Layered Blend per Bone
   Base Pose    ← Use cached pose MainPose
   Blend Pose 0 ← Slot("UpperBody")，输入接 Use cached pose MainPose
   Layer Setup  = spine_01 / BlendDepth 0 / 网格空间旋转混合勾选
   ↓
Slot("DefaultSlot")                ← 全身 montage 最后应用，最高优先级
   ↓
Output Pose
```

**开关设计：montage 的 Slot 名就是开关，默认全身。**

```
Slot = DefaultSlot（UE 默认）→ 全身控制（开关关，默认行为）
Slot = UpperBody            → 只控制上半身
```

**⭐ LayeredBlend 不是「按动作启用的节点」，它永远在；Slot 里没有 montage 时直通，等于不生效。开关在 montage 资产上，不在 AnimGraph 里。**

**三条硬约束（踩坑记录，全部实测）：**

```
① 混合深度必须是 0，不能是 -1
   BlendDepth = -1 → 从 spine_01 向父级方向混合
   → 手臂、头不在混合范围内 → 上半身 montage 看起来「完全不播」
   BlendDepth = 0  → spine_01 及其整个子树 → 正常

② DefaultSlot 必须在 LayeredBlend 之后（主链最后）
   如果 DefaultSlot 藏在 MainPose 缓存里（LayeredBlend 之前）：
   → Blend 链无 montage 时输出「不含攻击的姿势」→ 覆盖 Base 的上半身
   → 其他 montage（攻击）的上半身被吃掉

③ MainPose 缓存只包 StateMachine 输出
   不能包含 DefaultSlot，否则 ② 的「吃半身」问题复现
```

**效果（已验证）：**

```
移动中格挡受击 → 上半身后仰 + 下半身行走（不滑步）
站定格挡受击   → 上半身后仰 + 下半身格挡站姿（BlockState）
攻击           → DefaultSlot 最后覆盖全身，上半身正常
```

**症状 → 修复 对照表：**

| 症状 | 根因 | 修复 |
| --- | --- | --- |
| 上半身 montage 完全不播 | 混合深度 -1（只向父级混合） | 改为 0 |
| 其他 montage 上半身丢失 | DefaultSlot 在 LayeredBlend 之前，或 MainPose 缓存含 DefaultSlot | DefaultSlot 挪到主链最后，MainPose 只存状态机输出 |
| montage 不播且无报错 | Slot 名三处不一致（AnimGraph / 插槽管理器 / montage 槽名） | 逐字对齐（区分大小写与空格） |

**交付物：**

```
插槽管理器：DefaultGroup / DefaultSlot + UpperBody
Montage_BlockHit 的 Slot：DefaultGroup.UpperBody
```

**下半身分离 —— 未实现（未来需求再做）：**

```
⚠️ 当前没有 LowerBody 层，也没有任何 montage 只控制下半身。
   现有 montage 现状：
     全身    → DefaultSlot
     上半身  → UpperBody
     下半身  → 无（未来再加）

届时叠一层 LayeredBlend（LowerBody Slot），放在上半身层之前：
  Layer Setup = pelvis(0) + thigh_l(-1) + thigh_r(-1)
⚠️ 不要 pelvis(-1)：pelvis 的后代会包含 spine_01，上半身会被一起罩进来
```

##### 13.6 验证清单

```
□ 格挡受击：上半身播放受击动画，播完回到格挡姿态（BlockState）
□ 攻击不受影响：DefaultSlot 全身覆盖正常
□ 移动中格挡受击：下半身继续走，不滑步
□ 站定格挡受击：下半身格挡站姿不动
□ 连续格挡：montage 重播不报错
□ 普通受击破韧（未格挡）：走 EnterHit(HitHeavy)，收尾启动格挡 CD
□ 格挡被破防：走 HandleGuardHit 破防分支（见（14）），收尾启动格挡 CD
□ 完美格挡：走 HandlePerfectBlock，不经过 HandleGuardHit
□ 完美闪避 / 无敌帧 / 死亡：不触发 OnDamageApplied，无残留
```

---

#### （14）格挡破防：已实现

格挡成功但 Poise 已耗尽（Blocked + IsBroken = true），防御被击碎。

##### 14.1 链路

`
敌人攻击命中玩家（格挡中且被击破）
   ↓
BPC_Attribute.ReceiveDamage 第 ③ 条
  格挡 + 正面 + Poise>0 → 削轫扣到 0
   ↓
Return (Blocked, false, true)      ← HitOutCome=Blocked，IsBroken=true
   ↓
OnDamageApplied.Broadcast(Blocked, HitDirection, true)
   ↓
BPC_Combat.HandleGuardHit(PoiseBroken=true)
   ├─【1】bGuardLockPending = true        ← 标记收尾要启动 CD
   ├─【2】Attribute.ExitGuard()           ← bIsGuarding = false
   ├─【3】BPI_ActionState.TryEnterState(HitHeavy)
   │       ↓
   │   若失败 → SetState(Locomotion)（受控状态兜底）
   │   若成功 → 进入 HitHeavy（受控态，锁住移动/攻击/闪避/格挡）
   ├─【4】播放 GuardBreak montage（DT_Reactions 查 "GuardBreak" 行，Slot=DefaultSlot）
   │       ↓
   │   播完（SetState(Locomotion) 处）：
   │   ├─ ActionState.UpdateGuardCD(Get Game Time in Seconds)   ← CD 从收尾起算
   │   └─ bGuardLockPending = false
`

**两条破韧路径都走收尾启动 CD：**

`	ext
格挡被破防：Blocked + true → HandleGuardHit → GuardBreak → 收尾启动 CD
普通受击破韧：Hit + true   → EnterHit（HitHeavy）→ 收尾启动 CD
`

**关键：CD 不是破韧瞬间调 UpdateGuardCD(Now)，而是播完收尾时调。**  
破防 montage 锁 0.7s > GuardCD 0.4s。播之前起算 → CD 在蒙太奇期间耗光，播完立刻能格挡，等于没有惩罚。

**破防 Montage 用全身 Slot（不是 UpperBody）：**

`
Montage_BlockHit   → UpperBody Slot（普通格挡受击，只动上半身）
Montage_GuardBreak → DefaultSlot 全身（骨盆 + 双腿都要动，表现"防御被击碎"）
`

**收尾回 State：** 播完 SetState(Locomotion)，不走 SetState(Guard) —— 破防后不自动重进格挡，玩家需松开再按（若 CD 已过）。

##### 14.2 验证清单

`
□ 格挡被击破：ActionState 进入 HitHeavy，播放全身破防 montage，不播 BlockHit
□ 破防期间按格挡键：无效（受控状态拦下）
□ 破防播完：回 Locomotion，0.4s 内再按格挡 → 无效（CD 起算于收尾）
□ 0.4s 后：可重新进入格挡
□ 普通受击破韧（未格挡）：同样收尾启动 CD，播完 0.4s 内不可格挡
□ 破防不进入完美格挡分支，不开反击窗口，不播 FOV 特写
□ 攻击方反馈：PlayHitFeedback(Blocked, bPoiseBroken=true) → Break 震屏、破防音
`

---