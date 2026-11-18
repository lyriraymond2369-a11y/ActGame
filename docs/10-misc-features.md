# 其他功能实现

> 本文件是模块文档。项目总导航、规范与历史见 [README.md](../README.md)。

### 4）闪避方向（四向）

> **状态：设计已定稿，实现进行中。** 下面只写已经确认的部分，未决项列在最后。

#### （1）数据层

**`Montage_Dodge` 是合成蒙太奇，四个 Section：`F` / `B` / `L` / `R`，分别对应 `Doge_Combat_{F,B,L,R}_Seq`。**

**`DT_Attacks` 用四行区分：**

| 行名 | SectionStart | MotionSelf |
| --- | --- | --- |
| `Dodge_F` | `F` | (+Speed, 0, 0) |
| `Dodge_B` | `B` | (−Speed, 0, 0) |
| `Dodge_L` | `L` | (0, −Speed, 0) |
| `Dodge_R` | `R` | (0, +Speed, 0) |

**四行共用同一个 `Montage`，只有 `SectionStart` 和 `MotionSelf` 不同。**
**`Dodge_F_Air` 保持原样，本轮不改。**

#### （2）方向判定

**在 `BP_Player` 里做，`BPC_Combat` 不接触输入。**

```
① 采样 IA_Move（X 右正 / Y 前正，W = +1）
② (|X| > 0.2) or (|Y| > 0.2) ?
     有输入 → X != 0 ? (X > 0 ? Front : Back)
                      : (Y > 0 ? Right : Left)
     无输入 → ③
③ 无输入时按索敌状态决定默认方向
     LockOn.GetLockState() == None → Front
     LockOn.GetLockState() == Soft → Right
     LockOn.GetLockState() == Hard → Right
④ 调 DoDodge(Direction)
```

**默认方向规则：**

```
有方向输入 → 永远以玩家输入为准，索敌状态不覆盖
无方向输入 + 无索敌 → 默认前闪
无方向输入 + 软锁或硬锁 → 默认右闪
```

**因此这里不使用敌人距离阈值 —— 索敌状态本身就是是否默认右闪的依据。**

**⚠️ 默认右闪的「右」是相对参考系的右：**

```
硬锁 → 参考系 = 锁定目标      → 绕目标右侧侧闪
软锁 → 参考系 = 候选/索敌目标 → 同上
无索敌 → 参考系 = 相机         → 相对相机的右侧

因为 Combat 会在播蒙太奇前把朝向对齐参考系（见（4）），
所以 BP_Player 只要给出「Right」这个枚举值，不需要自己算方向向量
```

**② 是「X 优先」规则：斜向输入一律判成前 / 后，侧闪只在纯 Y 输入时触发。**
**若要改成「谁大听谁」，把 ② 换成比较 `|X|` 与 `|Y|`。**

**方向枚举用 `E_Direction`（前后左右上下 6 值），不用 `E_HitDirection`：**

```
E_Direction     方位通用，用于闪避 / 移动
E_HitDirection  受击专用，后续会扩到前左 / 前右等 8 方向
两者语义不同，不要互相替代
```

#### （3）`DoDodge` 的顺序

```
① 守卫          CanDodge / IsAlive
② 连招优先      有可接连招 → 交给连招，直接 Return（状态由连招自己设）
③ 方向选行      E_Direction → "Dodge_F/B/L/R"
④ 设朝向        见下
⑤ 关自动转向    bOrientRotationToMovement = false
⑥ SetMotionProfile(MotionSelf)
⑦ PlayMontageByID(Row.ID, Row.SectionStart)
⑧ SetState(Dodge) / NotifyDodgeStart / UpdateDodgeCD
```

**④ 必须在 ⑥ 之前 —— 否则 `MotionSelf` 会用旧朝向转成世界向量，表现成"动画对了但人往错方向滑"。**

#### （4）设朝向：对齐参考系，不是转身闪避

```
有锁定目标 → SetActorRotation(指向目标的 Yaw)
无锁定目标 → SetActorRotation(ControlRotation 的 Yaw)

理由：分类用的是「原始输入轴」，只有把角色对齐参考系，
      角色的「前/后/左/右」才等于玩家认知的前/后/左/右
```

**向后闪不转身 —— 方向由 Section 表达，`bOrientRotationToMovement` 关掉就行。**

#### （5）未决项

```
① MotionSelf 是角色局部空间还是世界空间（决定四行的数值怎么写）
② 四段动画的实际位移距离是否一致（不一致要按段调幅值）
③ 连招解析要不要抽成共享函数（DoLight / DoHeavy 也要用）
④ 四段是否各自都有 ANS_IFrame（缺一段则那一段无法完美闪避）
```

---

### 5）动作位移：水平与垂直冲量必须分开处理

**约定：`MotionSelf` 里的水平分量（Forward / Right）与垂直分量（Up）在 `BPC_Motor` 内部**分开移动**，不合成一个 Sweep。**

```
水平 Delta = ForwardVector × Forward + RightVector × Right   → 一次移动（Sweep）
垂直 Delta = UpVector × Up                                   → 另一次移动（Sweep）
```

**为什么必须分开 —— 这是一个真实踩过的坑：**

```
动作数据：Forward = 300, Up = 150

合成成一个 Sweep 时：
   离敌人近 → 前方撞到敌人胶囊体 → 整个位移被阻挡/投影
            → 向上分量一起被吞掉，角色跳不起来
   离敌人稍远 → 没有碰撞 → 垂直分量正常

表现就是"距离近就没有上挑，退后半步就好了"，
而且不会报任何错，极难定位到碰撞上
```

**关键判断：**

```
这个现象**不是数据表的问题，也不是冲量叠加的问题**
——同一个动作在近距离失效、远距离正常，只可能是碰撞相关的分支
→ 优先查 Motor 里是否把水平与垂直合成了一个 Delta
```

**如果分开之后仍然被吞，按这个顺序继续查：**

```
① 移动后是否又把 Z 强制贴回地面
   Snap To Floor / Move Along Floor / 每帧 Set Actor Location 复用当前 Z
   → 垂直到位了又被压回去

② 碰撞后是否把整个 Delta 清 0
   → 应该是"投影到碰撞平面"，而不是"整体作废"

③ 是否用了 Slide Along Surface 并且法线来自敌人胶囊体
   → 非竖直法线会把垂直分量一起吃掉
```

**验证方法（最快的定位顺序）：**

```
① 临时把敌人 Pawn 碰撞设为 Ignore → 近距离测
   恢复了 → 确认是敌人碰撞导致
② 恢复碰撞，临时禁用贴地 / Snap To Floor → 近距离测
   恢复了 → 确认是贴地逻辑导致
③ 移动前打印 OriginalDelta / FinalDelta / BlockingHit / Normal
   近距离那次大概率是 BlockingHit = true 且 FinalDelta ≈ 0
```

**执行顺序建议：**

```
先垂直后水平，还是先水平后垂直，取决于动作语义：
   上挑 / 跃起突进 → 先给垂直冲量，再走水平位移
                    → 避免贴着敌人时"起不来"
   纯地面突进       → 水平即可，Up = 0
```

**⚠️ 不要用 `Launch Character` 绕过 Motor：**

```
它会绕开 MotionProfile、重力、摩擦与 SetMotionScale
→ 位移距离不可控，还可能和闪避的 0.3 倍率冲突
动作位移继续交给 BPC_Motor 管
```

---

### 6）刀光：Niagara 条带拖尾

**武器的挥砍轨迹用 Niagara 的 Ribbon Renderer 生成，不用静态弧面网格。**

```
资产   Code/Material/M_WeaponTrail         Unlit + Additive + 贴图遮罩
       Code/VFX/Slash/NS_WeaponTrail       条带系统
       Code/Weapon/BP_Player_Sword         挂 NiagaraComponent 到刀尖 socket
       Code/AnimNotify/ANS_WeaponTrail     开合区间
```

**为什么不用静态弧面（这条路走过，结论是不划算）：**

```
SM_SlashArc 这类网格是美术在自己的坐标系里做的
   弧面躺哪个平面、pivot 在哪、单位尺度多少 —— 都与 socket 无关
直接套 socket 变换 = 两套无关坐标系相乘 → 朝向和大小都不对

要修就得给每个攻击方向单独加 Offset Rotation / Mirror
四向闪避 + 轻重击 + 反击 → 对齐工作量极大，而且一改动画全废

条带完全不碰这个问题：
   方向由轨迹自动生成（socket 走过的路径就是方向）
   长度由挥动幅度决定
   粗细只有一个 Ribbon Width 参数
```

**三个必须守住的设置：**

```
① 发射器 Local Space = false
   开着的话粒子存的是「相对发射器」的坐标
   武器一动粒子跟着动 → 所有粒子叠在同一点 → 条带长度为 0，什么都画不出来

② Ribbon Width > 0，且不要用 Scale Ribbon Width 模块把曲线从 0 起
   宽度被乘成 0 时，渲染器正常工作但画面全空，零报错

③ SetTrailActive(false) 用 Deactivate，不要用 Destroy
   Deactivate → 停止生成，已有粒子活完 lifetime 自然淡出（刀光该有的收尾）
   Destroy    → 立刻全消，看起来像被硬切断
```

**Ribbon 的朝向由「模式 + 粒子属性」共同决定，不是在渲染器里填一个向量：**

```
Ribbon Renderer · Facing Mode
    Screen（相机朝向）        → 永不扭面，但没有平面感，适合先验证
    Custom / Custom Side Vector → 需要粒子属性 RibbonFacing（Vector）
                                  在「粒子更新」栈里写入，可由 User Parameter 从蓝图传
```

**⭐ 排查顺序建议：先用 Screen 确认轨迹本身对（长度、渐隐、跟随），再切 Custom 追求平面感。方向不对时优先怀疑 Facing Mode，不要去改武器挂载。**

**材质分工（`M_WeaponTrail`）：**

```
粒子颜色 RGB  → 刀光颜色          （Niagara 控制）
粒子颜色 A    → 整条刀光淡出      （Niagara 按年龄衰减）
贴图 RGB/遮罩 → 刀光形状与沿条带的渐隐
```

**⚠️ Additive 本身就是"越叠越亮"：条带自交或贴近相机时会爆白。控制手段有两个 ——**
**降低材质的自发光乘数（Additive 下乘 2 以上必然过曝），或改用 Translucent 让重叠变成覆盖而非相加。**

**接线（走接口，不 Cast 具体武器）：**

```
ANS_WeaponTrail · NotifyBegin
    → BPI_CharacterBase.Get Weapon(Owner)
    → BPI_WeaponBase.SetTrailActive(true)

ANS_WeaponTrail · NotifyEnd
    → BPI_WeaponBase.SetTrailActive(false)
```

**⚠️ 动画被 `Montage_Stop` 或受击打断时，NotifyEnd 可能不触发，刀光会一直挂着。**
**兜底放在 `BPC_Combat` 的收尾路径里（和 `StopAfterimage()` 同一处）主动调一次 `SetTrailActive(false)`。**

**挂载与区间：**

```
NiagaraComponent 附在武器 Mesh 的「刀尖」socket 上
    刀根 socket 位移太小 → 轨迹短到看不出来
    Auto Activate 关，由通知控制

每段攻击各挂一个 ANS_WeaponTrail，不要用一条长通知覆盖整段连招
    → 否则两段之间的过渡动作也会被采样，连出一条直线光带

区间宽度不必精确到帧：
    比静态弧面宽容得多 —— 宽一点轨迹长，窄一点轨迹短，不会「提前亮 / 追不上」
```

---

### 7）攻击令牌：同屏进攻名额

**多个敌人同时进攻时，玩家无法同时观察多条前摇 —— 完美闪避的 0.15s 窗口、格挡的朝向判断都会退化成运气。令牌就是限制同屏进攻人数的全局闸门。**

**⭐ 设计原则：永远至少留 1 个敌人在外围。玩家永远要有喘息窗口。**

```
场上存活      MaxToken     效果
1             1            单人正常打
2             1            一个打、一个绕
3             2            两个打、一个绕
4 以上        2            不再放宽
```

```
MaxToken = Clamp(存活敌人数 − 1, 1, 2)
```

**数据结构（`BP_GameState`）：**

| 变量 | 类型 | 默认 | 说明 |
| --- | --- | --- | --- |
| `Tokens` | **Map\<Actor, Float\>** | 空 | 持有者 → 拿令牌的时刻 |
| `MaxToken` | Int | 2 | 同时持有上限，按存活人数动态算 |
| `TokenTimeout` | Float | 5.0 | 单人单次持有上限（秒） |
| `TokenCooldown` | Float | 0.4 | 全局释放冷却（秒） |
| `LastReleaseTime` | Float | -1000 | 上次释放时刻 |

**⭐ 必须用 Map 而不是「Actor 数组 + Float 数组」：**

```
超时判断需要「谁持有 + 何时开始持有」两份信息
平行数组只要有一次 Add / Remove 忘了同步 → 索引错位
→ 超时判断取到别人的时间 → 某人莫名被踢，且不报错
Map 的 Add(Key, Value) / Remove(Key) 天然不会错位
```

**`AddToken` 的四道守卫（缺一不可）：**

```
① IsValid(Holder) == false              → false    空引用
② Tokens.Contains(Holder) == true       → true     幂等：已持有视为成功
③ Tokens.Length() >= MaxToken           → false    名额满
④ Now − LastReleaseTime < TokenCooldown → false    冷却中
⑤ 通过 → Tokens.Add(Holder, Now)        → true
```

**⭐ ②返回 `true` 不是笔误：AI 每次决策都会问一次，返回 false 会让它误以为没拿到而反复重试。**

**`RemoveToken`：**

```
① Tokens.Contains(Holder) == false → Return        幂等
② Tokens.Remove(Holder)
③ LastReleaseTime = Now
```

**⚠️ 顺序不能反。先记冷却再判 Contains 的话，玩家的攻击结束（从不持有令牌）也会刷新冷却，敌人会集体变懒 —— 而且这个 bug 极难联想到玩家攻击上。**

**申请与归还的分工：**

```
申请（决策层）   BTT_EnemyAttack · Execute
                   → AddToken(Owner)
                   → 失败即 Finish Execute(false)，让 BT 回退到绕圈分支
                   → BTT 只回答"这次攻击能不能执行"，不问"不能执行时干什么"

归还（执行层）   BPC_AttackTrace · OnMontageFinished
                   → RemoveToken(Owner)
                   → 谁拥有蒙太奇生命周期，谁负责收尾
```

**⭐ 为什么不两边都放 BTT：任务 `Finish Execute` 之后回调状态是否有效不确定，容易出「回调执行了但拿不到 Owner」。而蒙太奇一定有终点，AttackTrace 的释放更可靠。**

**⭐ 为什么不放 `BPC_AI`：`OnMontageFinished` 已在 BTT 里绑定，再加一处订阅会冲突。**

**三层兜底（`BP_GameState` · Tick，间隔 0.5s）：**

```
① IsValid(Holder) 失败                          → 移除
② 实现 BPI_CharacterBase 且 IsCharacterDead      → 移除
③ Now − Tokens.Find(Holder) > TokenTimeout      → 移除
```

**先收集到临时数组，再统一 Remove —— 不要边遍历边改 Map。**

**⚠️ 这三层不能省。敌人死亡、被击倒、BTT 异常中止、组件被禁用，任意一条路径漏了释放，令牌就永久占用。**

```
表现：全场只剩 MaxToken−1 个敌人能动
特征：不报错、不崩溃，只表现为"敌人越来越懒"
时效：前 10 秒完全正常，越往后越明显
```

**没有令牌的敌人：**

```
保持距离 800~1200（与软锁 1200 呼应）
绕圈位移，始终朝向玩家
偶尔播一个前摇然后取消（假动作）
```

**⭐ 假动作成本几乎为零（播蒙太奇 → 判定帧前 Stop），但能把"打木桩"变成"同时管理多个威胁"。**

**⚠️ 拿到令牌后立刻出招。拿着令牌发呆会白占名额，玩家看到的是敌人不动。**

---

### 8）攻击后摇取消（无后续连招时）

**可行，已实现。** 攻击后摇段若没有后续连招，可被玩家输入取消，直接起新攻击。

**实现位置：`BPC_ActionState.CanTransitionTo`（内部函数）**

状态层只管"能不能转场"，改动只在一个闸门：

```
CanTransitionTo(NewState)
  ├─ 默认：查转场矩阵
  └─ CurrentState == Attack && bCanCancel == true
       → 允许转出到 Locomotion（取消后摇，立即可起新攻击）
```

**与连招续接的区分：**

```
连招续接：有 Next 段 → Combat 用 ForceEnterState（走转场闸门，需窗口打开）
后摇取消：无 Next 段（或输入别的动作）→ TryEnterState(Locomotion) 退出攻击态
→ 两者不混淆：ForceEnterState 天然只在有 Next 时可用，后摇取消发生在"没连招可走"的最后一段
```

**数据驱动：**

| 数据 | 作用 |
| --- | --- |
| `ST_AttackData.CancelStart` | 取消窗口打开的时刻（攻击起手后 N 秒） |
| `BPI_ActionState.SetCancelWindow(bool)` | Combat 开合取消窗口，只允许 Combat 与动画通知调用 |
| `bCanCancel` | ActionState 内部标志，当前是否在可取消窗口内 |

**时间顺序：**

```
攻击起手 → Set Timer(CancelStart → SetCancelWindow(true))
   │
   ├─ 有 Next + 按攻击 → ForceEnterState(Next) 续接连招
   ├─ 无 Next + 输入攻击/闪避/跳跃 → TryEnterState(Locomotion) 取消后摇，立即起新动作
   └─ Cancel 窗口结束 → SetCancelWindow(false)
```

**不改的地方：** `TryEnterState` 的"永远不能回 Locomotion"不变；取消后摇走的是在窗口内从 Attack 转 Locomotion，属于转场闸门放行，不违背该约定。

---

