# Player（玩家）

> 本文件是模块文档。项目总导航、规范与历史见 [README.md](../README.md)。

## 2，Player（玩家特有）（继承于 CharacterBase）

| 组件名                | 组件用途     |
| ------------------ | -------- |
| BPC_ActionState    | 玩家当前状态   |
| BPC_BufferInput    | 玩家输入缓存   |
| BPC_CameraDirector | 玩家相机控制   |
| BPC_Combat         | 玩家角色动作控制 |
| BPC_LockOn         | 玩家索敌控制   |

### 1）Player 类接口方法

#### （1）BPI_Player

| 方法名                     | 输入   | 输出                      | 作用                     |
| ----------------------- | ---- | ----------------------- | ---------------------- |
| GetActionStateComponent | /    | BPC_ActionState 对象引用    | 获取 BPC_ActionState     |
| GetCombatComponent      | /    | BPC_Combat 对象引用         | 获取 BPC_Combat          |
| GetBufferInputComponent | /    | BPC_BufferInput 对象引用    | 获取 BPC_BufferInput     |
| GetCameraDirectorComponent | /  | BPC_CameraDirector 对象引用 | 获取 BPC_CameraDirector（相机控制组件） |
| GetCameraComponent      | /    | CameraComponent         | 获取角色的 CameraComponent（相机组件） |
| GetLockComponent        | /    | BPC_LockOn 对象引用         | 获取 BPC_LockOn          |
| StartJump               | /    | /                       | 让角色跳跃                  |
| IntoHardLockState       | /    | /                       | 进入硬锁                   |
| OutHardLockState        | /    | /                       | 退出硬锁                   |
| SetLockPlevisZ          | bool | /                       | 设置是否锁定 Plevis 骨骼的 z 位置 |
| StartAfterimage         | /    | /                       | 开始按 `GhostInterval` 循环生成残影。**由完美闪避启动** |
| StopAfterimage          | /    | /                       | 停止生成残影并清空计数数组。**已生成的残影不销毁，交给各自淡出** |

> `GetMesh`、`GetHitBox`、`GetWeapon`、`GetAttributeComponent`、`GetCharacterMovement` **已全部上收到** `BPI_CharacterBase`，玩家侧不再各自声明。写蓝图时统一走基类接口。

> **`GetCameraComponent` 与 `GetCameraDirectorComponent` 是两个不同的东西，可以同时存在：**

```
CameraComponent         UE 自带的相机组件 —— 挂在角色上的实际摄像机
BPC_CameraDirector      项目自研的相机控制组件 —— 锁定、震动、视角过渡
                        它不持有相机，只下指令
```

#### （2）BPI_ActionState

| 方法名             | 输入                      | 输出            | 作用                                        |
| --------------- | ----------------------- | ------------- | ----------------------------------------- |
| TryEnterState   | E_ActionState（NewState） | bool          | 一级状态转换：走转场矩阵与受控状态优先级。**永远不能回 Locomotion** |
| ForceEnterState | E_ActionState（NewState） | bool          | 二级状态转换：连招续接。需取消窗口打开，不受控状态下一律无效            |
| SetState        | E_ActionState（NewState） | /             | 收尾复位，无校验、幂等。**唯一能回 Locomotion 的入口**       |
| GetActionState  | /                       | E_ActionState | 获取角色当前状态                                  |
| SetCancelWindow | bool                    | /             | 开关取消窗口。只允许 Combat 与动画通知调用                 |
| CanDodge        | /                       | bool          | 当前是否可以冲刺（受 CD 与非受控状态约束）                   |
| UpdateDodgeCD   | float（Time）             | /             | 记录冲刺起手时刻，用于 CD 判定                         |
| ClearDodgeCD    | /                       | /             | 清空冲刺冷却。**仅供完美闪避调用**，让玩家立刻可以再闪              |
| CanGuard        | /                       | bool          | 当前是否可以格挡（受 CD 与非受控状态约束）                   |
| UpdateGuardCD   | float（Time）             | /             | 记录格挡退出时刻，启动格挡 CD                            |
| ClearGuardCD    | /                       | /             | 清空格挡冷却。**仅供完美格挡调用**                       |

**三个转换入口的分工：**

```
TryEnterState    状态层说了算 —— 查转场矩阵
ForceEnterState  战斗层说了算 —— 战斗层已判定连招成立，状态层照做
SetState         不用判断   —— 复位收尾
```

**`CanTransitionTo`（内部函数）是所有试转场的统一闸门，攻击后摇取消就在这里放行：**

```
CanTransitionTo(NewState)
  ├─ 默认：查转场矩阵
  └─ 攻击态（CurrentState == Attack）+ bCanCancel 为真
       → 允许转出到 Locomotion（取消后摇）
         ⚠️ 只有「无后续连招」时才会走到这里：
           有 Next 的段优先走 ForceEnterState 续接，不会进取消分支
```

**受控状态（HitLight / HitHeavy / KnockDown / Dead）内部有优先级，可升级、可幂等，不可降级、不可逃逸。**

#### （3）BPI_BufferInput

| 方法名     | 输入          | 输出   | 作用                 |
| ------- | ----------- | ---- | ------------------ |
| Push    | E_InputType | /    | 向缓存中推入新的输入         |
| Comsume | E_InputType | bool | 读取缓存中的指定输入，并返回是否成功 |
| Peek    | E_InputType | bool | 看缓存中是否有指定且没过期的输入   |

#### 输入映射：Shift 双功能（点按闪避 / 长按奔跑）

| 项目 | 内容 |
| --- | --- |
| 物理键 | 左 Shift（唯一）；`IA_Run` / `IA_Dodge` 已删除，只保留 `IA_Shift` |
| 奔跑 | `Locomotion` 内的速度档位（`E_MoveState.Run`），持续状态，**不进** `BufferInput` |
| 闪避 | 输入事件（`E_InputType.Dodge`），Push 进 `BufferInput` |
| 阈值 | `ShiftPressThreshold = 0.2s`（松开瞬间时长小于阈值 → 闪避；大于等于 → 奔跑/松手） |

**增强输入事件已全部移除，改为 BP_Player 的 `Tick` 纯轮询 `IA_Shift`（`IsPressed` / `GetBoundActionValue`），仅有一处写入：**

```
Tick 每帧：
  ├─ Pressed = 轮询 IA_Shift
  ├─ Pressed && !bWasShiftPressed
  │     → ShiftPressStartTime = Now            （ShiftPressStartTime 唯一写入点）
  ├─ !Pressed && bWasShiftPressed
  │     → Elapsed = Now - ShiftPressStartTime
  │       Elapsed < 0.2 ? → Push(E_Dodge)（闪避；方案 A：格挡中先 ExitGuard，不回格挡）
  ├─ 奔跑判定：Pressed && (Now - ShiftPressStartTime) >= 0.2 && 有移动输入
  │     → E_MoveState = Run
  └─ bWasShiftPressed = Pressed
```

**为什么纯轮询、不保留增强输入事件：**

```
事件（Completed）→ Push BufferInput → 下一帧 Tick 消费，两跳 = 两帧延迟
纯轮询在松开当帧完成判定并直接 DoDodge，零帧延迟，适合点按闪避

⚠️ 边界：
① 单帧内按又松（<~16ms）轮询会漏；人类点按普遍 > 30ms，可接受
② 轮询依赖映射上下文已添加（BeginPlay），未添加表现为 Shift 完全无响应，不报错
③ ShiftPressStartTime 初始 -9999，读取时加 > 0 守卫，防止未按过误判奔跑
```

**方案 A 行为：**

```
点按 Shift（<0.2s）= 闪避
  └─ 格挡中短按 → 直接取消格挡进入闪避（主动设计）
  └─ 闪避收尾回 Locomotion，不回格挡（ExitGuard，bIsGuarding = false）
     想继续格挡必须松开重按 TryGuard

长按 Shift（≥0.2s）= 奔跑
  └─ E_MoveState = Run；松开自动回 Walk/Idle
  └─ 无移动输入时 → Idle，不误入奔跑
```

#### （4）BPI_CameraDirector

| 方法名   | 输入                              | 输出  | 作用                           |
| ----- | ------------------------------- | --- | ---------------------------- |
| Shake | E_CameraShakeType，Vector3，float | /   | 根据抖动类型、受击位置、强度制造屏幕抖动         |
| PlayPerfectBlockCloseUp | /                      | /   | 完美格挡的 FOV 特写：收窄 → 保持 → 回位。**收窄与顿帧同时开始** |

#### （5）BPI_Combat

| 方法名              | 输入   | 输出            | 作用             |
| ---------------- | ---- | ------------- | -------------- |
| DoLight          | /    | /             | 操作轻击           |
| DoHeavy          | /    | /             | 操作重击           |
| DoJump           | /    | /             | 操作跳跃           |
| DoDodge          | /    | /             | 操作冲刺           |
| GetCurrentAttack | /    | ST_AttackData | 获取当前动作的数据      |
| OnAttackWindow   | bool | /             | 开关攻击窗口（由 ANS_AttackWindow 触发） |
| EnterHit         | E_ActionState，E_HitDirection | /   | 进入受击处理（由 Attribute 的 OnDamageApplied 触发） |
| TryGuard         | /    | bool          | 格挡入口：`CanGuard`（CD + 受控）+ 状态查重 + 进状态 + `EnterGuard`。**门槛统一在这里，玩家蓝图不存变量** |
| OnKnockDownLoopStarted | / | / | 击倒蒙太奇进入 Loop 段的通知（由 `AN_KnockDownLoopStart` 触发）：置位 + 启动躺地计时器 |
| HandleKnockDownCompleted | / | / | 击倒收尾（**接口化**，供投技/处决演出结束后直接调用）：清计时器/标志 + `ReliefPosture` + `UpdateGuardCD` + `ReliefLocomotion`。开头有状态守卫（仅 `KnockDown` 放行） |

> **位移不再经过 Combat。** `ANS_Move` 直接调 `BPI_Motor.StartMotion` / `StopMotion`，
> Combat 只负责在动作开始时用 `SetMotionProfile` 下发速度和方向。
> 原先的 `MoveStart` / `MoveEnd` 两个纯转发函数已删除。

> **格挡 CD 已迁入 `BPI_ActionState`**（与闪避 CD 对称）：`CanGuard` / `UpdateGuardCD` / `ClearGuardCD`。
> 原 `BPI_Combat.SetLastGuardEndTime` 已删除。

#### （6）BPI_LockOn

| 方法名              | 输入  | 输出            | 作用        |
| ---------------- | --- | ------------- | --------- |
| GetFocusTarget   | /   | Actor         | 获取当前焦点目标（已并入原 `GetTarget` 的候选目标逻辑） |
| GetLockState     | /   | E_LockOnState | 获取当前锁定状态  |
| HardLockPress    | /   | /             | 硬锁键按下     |
| HardLockRelease  | /   | /             | 硬锁键松开     |
| SimpleAimCorrect | /   | /             | 软锁下修正角色朝向 |

### 2）Player 数据类型

#### （1）Player 枚举

##### 一，E_ActionState

| 枚举值        | 枚举含义                     |
| ---------- | ------------------------ |
| Locomotion | 一般状态（最低级，回它只能走 SetState） |
| Jump       | 跳跃状态（含下落）                |
| Attack     | 攻击状态                     |
| Dodge      | 冲刺状态                     |
| Guard      | 格挡状态                     |
| HitLight   | 轻受击（受控）                  |
| HitHeavy   | 重受击（受控）                  |
| KnockDown  | 倒地（受控）。**禁止幂等**：`KnockDown → KnockDown` 在 `TryEnterState` 公共闸门返回 false（倒地期间再触发不重启蒙太奇）；可被 `Dead` 升级 |
| Dead       | 死亡（受控，绝对终态）              |

##### 二，E_CounterType（反击窗口类型）

| 枚举值   | 含义           | 优先级 |
| -------- | ------------ | ---- |
| None     | 无窗口       | 0    |
| Block    | 格挡反击窗口 | 1    |
| Dodge    | 闪避反击窗口 | **2（高）** |

> **完美闪避更难，所以 `Dodge` 优先级更高**：两种窗口冲突时以 `Dodge` 为准，`Block` 不覆盖 `Dodge`。

##### 三，E_CameraShakeType（屏幕抖动类型）

| 枚举值          | 枚举含义   |
| ------------ | ------ |
| Hit          | 普通受击抖动 |
| Block        | 格挡抖动   |
| PerfectBlock | 完美格挡抖动 |
| Break        | 破韧抖动   |
| Kill         | 死亡抖动   |
| PerfectDodge | 完美闪避抖动 |

> **共 6 个值。** `BPC_CameraDirector` 里有 6 个对应变量：`Shake_Hit` / `Shake_Block` / `Shake_PerfectBlock` / `Shake_Break` / `Shake_Kill` / `Shake_PerfectDodge`，一一指向 `Player/CameraShake/BPCS_*`。
>
> **⚠️ `BPCS_PerfectDodge` 已从原 `BPCS_Perfect` 拆分出来，但参数暂未调整** —— 目前沿用拆分时的默认值，与 `BPCS_PerfectBlock` 尚未拉开差异。调法与参数见 [8，功能实现 · 3）完美格挡](#3完美格挡) 的（11）。

##### 四，E_CloseUpPhase（完美格挡特写阶段）

| 枚举值   | 含义      |
| ----- | ------- |
| None  | 无特写（空闲） |
| In    | 收窄      |
| Hold  | 保持      |
| Out   | 回位      |

> **`None` 兼作空闲态** —— 有了它就不再需要 `bCloseUpActive`。两个变量表达同一个状态，只要有一条路径忘了同步就会出现「标志位说没在做、枚举却停在 Out」的分叉，而且不报错。

##### 五，E_InputType

| 枚举值     | 枚举含义 |
| ------- | ---- |
| Light   | 轻击   |
| Heavy   | 重击   |
| Dodge   | 冲刺   |
| Jump    | 跳跃   |
| Execute | 处决   |

##### 六，E_LockOnState（锁定状态）

| 枚举值  | 枚举含义 |
| ---- | ---- |
| None | 无锁定  |
| Soft | 软锁   |
| Hard | 硬锁   |

##### 七，E_MoveState（移动状态）

| 枚举值  | 枚举含义 |
| ---- | ---- |
| Idle | 站立   |
| Walk | 走路   |
| Run  | 奔跑（Shift 长按 ≥0.2s 的速度档位，见输入映射小节） |

---

### 3）架势与击倒（Posture & KnockDown）

> **状态：已实现。** 架势是防御结构值（满 = 稳，0 = 崩），与韧性（Poise）平行；归零 → `BreakPosture` → 玩家倒地。姿态变量与恢复规则见 [CharacterBase · 架势](01-character-base.md)。

#### 3.1 分流：BreakPoise 与 BreakPosture 平行

```text
OnDamageApplied 分流（BPC_Combat）：
  ├─ Ignore        → 无
  ├─ BreakPosture  → HandleBreakPosture   ← 架势归零 → KnockDown
  ├─ BreakPoise    → HandleGuardBreak     ← 韧性破防 → HitHeavy + GuardBreak（原逻辑不动）
  ├─ Blocked       → HandleGuardHit       ← 纯普通格挡
  └─ Hit           → EnterHit             ← 普通受击（IsBroken → HitHeavy）
```

#### 3.2 `HandleBreakPosture` 与 KnockDown 播放结构

```text
HandleBreakPosture
  ├─ ExitGuard
  ├─ TryEnterState(KnockDown)             ← 禁止幂等：已在 KnockDown/Dead 时返回 false → 直接 Return
  ├─ ClearTimer(KnockDownTimerHandle)
  ├─ bKnockDownLoopStarted = false
  └─ PlayReactionMontage("KnockDown" 行, bReliefOriginal = false)
       └─ 播放失败（无行/无蒙太奇）→ SetState(Locomotion) 兜底
```

**击倒蒙太奇为 `Start → Loop（自循环）→ End` 三段结构：**

```text
Start（倒地，播一次）→ Loop（躺地，自循环）→ End（起身，播一次）

Loop 段第一帧：AN_KnockDownLoopStart
  → BPI_Combat.OnKnockDownLoopStarted()
       ├─ 状态 == KnockDown？  否 → Return
       ├─ bKnockDownLoopStarted 防重
       └─ SetTimer(KnockDownLoopDuration)（默认 1.5s）

Timer 到期（内联事件）：
  ├─ 状态 == KnockDown？       否 → Return（死亡/处决/投技接管后直接退出）
  ├─ IsPlaying(KnockDownMontage)？否 → Return（蒙太奇已被 Stop）
  └─ Montage Jump to Section("End")
```

**Timer 必须在 Loop 通知里启动，不能在 `HandleBreakPosture` 里启动** —— 否则 Start 段时长会被算进躺地时间。

#### 3.3 `HandleKnockDownCompleted`（接口，收尾）

```text
HandleKnockDownCompleted()（BPI_Combat 接口）
  ├─【0】状态守卫：当前不是 KnockDown → Return
  │        （共用 OnCompleted 路径时，普通受击播完会被这行拦下）
  ├─【1】ClearTimer(KnockDownTimerHandle)
  ├─【2】bKnockDownLoopStarted = false
  ├─【3】Attribute.ReliefPosture()            ← 架势回满
  ├─【4】ActionState.UpdateGuardCD(Now)       ← 格挡 CD 收尾起算
  └─【5】ReliefLocomotion()                   ← Combat 内部函数（SetState(Locomotion) + 其他复位）
```

**两个入口：**

```text
正常完成：PlayReactionMontage 的 On Completed（未被打断）→ 直接调 HandleKnockDownCompleted
投技/处决：演出蒙太奇播完后由演出流程直接调用（先 Stop 击倒蒙太奇，再调接口）
被打断（死亡等）：On Completed 不触发 → 什么都不做（Dead 是绝对终态）
```

#### 3.4 验证

```text
□ 格挡中 Poise 归零 → BreakPoise → HitHeavy + GuardBreak（与架势无关）
□ Posture 归零（格挡/命中共通）→ BreakPosture → KnockDown
□ 同一击两者同时归零 → BreakPosture 优先
□ 倒地期间挨打 → 状态不变、蒙太奇不重启（禁幂等）
□ 倒地期间被打死 → 进 Dead，无收尾触发
□ Start 段不被计入躺地时间（Timer 从 Loop 通知起算）
□ Loop 多次进入不重复 SetTimer
□ End 播完 → 收尾（架势满、CD 启动、回 Locomotion）
□ 普通受击播完不误触发 KnockDown 收尾（状态守卫）
```

---

> 玩家运行导图 → [运行导图 · 玩家](11-run-maps.md)

---

