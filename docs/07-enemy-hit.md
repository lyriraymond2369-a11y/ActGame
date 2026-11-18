# 敌人受击状态机

> 本文件是模块文档。项目总导航、规范与历史见 [README.md](../README.md)。

### 1）敌人受击状态机

敌人没有 `BPC_ActionState`，受击状态由 `BPC_AI` 自己维护。
**所有转换规则收在 `AI_TryEnterState` / `AI_SetState` 两个入口里，行为树只读状态、不做判断。**

> **两个入口的分工：**
> `AI_TryEnterState` 走优先级闸门，受击 / 死亡走这里；`AI_SetState` 是内部 `ApplyState` 的薄包装，绕过优先级，供决策层（BTS）和动作回流（`AI_ReturnToInitialState`）使用。

#### （1）状态分级

| E_AIState | Priority | 受控 | 说明     |
| --------- | -------- | -- | ------ |
| Idle      | 0        | 否  | 待机     |
| Chase     | 0        | 否  | 追击     |
| Attack    | 0        | 否  | 攻击     |
| HitLight  | 1        | 是  | 轻受击    |
| HitHeavy  | 2        | 是  | 重受击    |
| KnockDown | 3        | 是  | 倒地     |
| Dead      | 4        | 是  | 死亡（终态） |

> 蓝图里落地为 `AIStateProperty` 映射表，字段：`Priority` / `IsControlled`。

#### （2）三条不变量

```
① 所有非受控状态的 Priority 必须为 0
   「不可转出」是「非受控 0 < 受控 ≥1」的推论。
   一旦给某个非受控状态更高优先级，转出规则会静默失效，而且不会报错。

② Dead 是唯一禁止幂等的状态
   Dead → Dead 返回 false；其余同级转换返回 true。

③ 受控状态的唯一出口是 AI_ReturnToInitialState
   它不判优先级，只回答「动作结束了，该回哪儿」：有目标 → Chase，无目标 → Idle。
   受击表现播完、攻击蒙太奇结束都走它。
   别的地方想改状态一律走 AI_SetState（绕过优先级）或 AI_TryEnterState（走闸门）。
```

#### （3）AI_TryEnterState —— 优先级闸门

```
[1] NewState == Dead ?
      CurrentState == Dead → return false        （死亡禁止幂等）
      否则 ApplyState(Dead); return true          （死亡从任何状态都能进）

[2] NewState == CurrentState ?
      return true                                （幂等命中，不写黑板）

[3] Priority(New) < Priority(Current) ?
      return false                               （降级 / 转出 一并拦下）

[4] ApplyState(New); return true
```

**返回值语义：`true` = 调用结束后当前状态等于 NewState（无论是刚写入还是本来就是）；`false` = 没达成。**

判断表：

| Current   | New       | 出口 | 返回        |
| --------- | --------- | -- | --------- |
| Idle      | Chase     | 4  | true      |
| Chase     | HitLight  | 4  | true      |
| HitLight  | HitLight  | 2  | true（幂等）   |
| HitLight  | HitHeavy  | 4  | true（升级）   |
| HitHeavy  | HitLight  | 3  | false（降级）  |
| HitHeavy  | Chase     | 3  | false（转出）  |
| KnockDown | Attack    | 3  | false（转出）  |
| 任意非 Dead  | Dead      | 1  | true      |
| Dead      | Dead      | 1  | **false** |
| Dead      | HitLight  | 3  | false     |

**⚠️ `ApplyState` 才是真正写状态的地方**（写 `CurrentState`、同步黑板 `AIState`、处理受击幂等、执行状态副作用）。两个入口都只是它的包装，不要在包装里重复这些逻辑。

#### （4）AI_SetState / AI_ReturnToInitialState —— 绕过优先级的两个出口

**`AI_SetState`** 是 `ApplyState` 的薄包装，**不判优先级**：

```
AI_SetState(NewState)
  └─ ApplyState(NewState)
```

**谁可以调、为什么安全：**

| 调用方 | 场景 | 它凭什么保证时机 |
| --- | --- | --- |
| `BTS_UpdateAIState` | `Idle → Chase`、`Chase → Idle`、`Chase → Attack` | BTS 在受控状态和 Attack 期间直接 Return，不会在这些时候调 |
| `BPC_AttackTrace` | 攻击蒙太奇结束回流 | 只在攻击结束时调一次 |

**⭐ 绕过优先级不等于不安全 —— 安全性由**调用方的前置判断**保证。这是「权限下放」的必然代价：谁能写，谁就要负责时机。**

**`AI_ReturnToInitialState`** 是动作结束的统一回流：

```
[1] 当前状态不是 Attack / 受控状态 → return     （幂等，别的地方误调也无害）
[2] TargetActor 有效 → SetState(Chase)
[3] TargetActor 无效 → SetState(Idle)
```

**⭐ 为什么由它判断“回 Chase 还是 Idle”：`AttackTrace` 不该知道有没有目标 —— 那是 AI 的数据。它只负责说「我这边结束了」，去向由 AI 用自己的数据决定。**

**⚠️ 调用顺序必须是「先 `RemoveToken`，再 `AI_ReturnToInitialState`」**：反过来的话，回到 Chase 的那一帧 BTS 可能判定可再次攻击，但旧令牌还没释放，状态与资源不同步。

#### （5）重播机制：状态幂等 ≠ 表现幂等

受击状态是幂等的（`HitLight → HitLight` 状态不变），但**表现必须重播**（连砍两刀要看到两次受击）。
这个矛盾靠两个计数器把「状态」和「表现」解耦：

```
HitStamp       每次状态被接受时 +1，永不清零
HandledStamp   表现层（BTT_PlayHitReaction）已消费到哪
bHitPending    = (HitStamp != HandledStamp)，实时写入黑板
```

**三个写入点：**

```
ApplyState           → CurrentState + 黑板 AIState（+ bControlled）
HandleDamageApplied  → 状态被接受后 HitStamp++，再刷黑板
AI_ConsumeHit        → HandledStamp = max(本次 Stamp)，再刷黑板
```

**时序：**

| 时刻 | 事件                    | HitStamp | HandledStamp | bHitPending |
| -- | --------------------- | -------- | ------------ | ----------- |
| T0 | 初始                    | 0        | 0            | false       |
| T1 | 挨第一刀，状态被接受            | **1**    | 0            | **true**    |
| T2 | Task 执行，先消费再播          | 1        | **1**        | **false**   |
| T3 | 播放中挨第二刀（同级）           | **2**    | 1            | **true**    |
| T4 | 旧蒙太奇被新蒙太奇覆盖，新 Task 消费 | 2        | **2**        | **false**   |
| T5 | 播完，无新受击，复位            | 2        | 2            | false       |

> **`AI_ConsumeHit` 必须放在 Task 执行的开头**：它把 `bHitPending` 置回 false，下一次受击才能产生 `false → true` 的边沿，从而立刻打断上一轮、由新蒙太奇覆盖旧蒙太奇。

#### （6）黑板键

| 键            | 类型              | 写入方                 | 说明                       |
| ------------ | --------------- | ------------------- | ------------------------ |
| AIState      | E_AIState       | ApplyState          | 状态机同步（**唯一写入点**）         |
| bHitPending  | bool            | SyncBlackboard      | 是否有未消费的受击                |
| HitDirection | E_HitDirection  | 内部受击处理（原 HandleDamageApplied） | 本次受击方向，只与 HitStamp 同步更新   |
| TargetActor  | Actor           | Tick · RefreshTarget | 当前目标（**值变化时才写**）         |
| DisToTarget  | float           | Tick · UpdateDistances | 与目标的 2D 距离（无目标时为 -1）     |

**行为树的 `BTT` 与 `BTD` 一律只读黑板，不写任何值；只有 `BTS` 和 `BPC_AI` 自己会写。**

#### （7）受击蒙太奇表

| 项     | 内容                                              |
| ----- | ----------------------------------------------- |
| 资产    | `Player/DataTable/DT_Reactions`（敌我共用）            |
| 行结构   | `ST_AttackData`                                 |
| 行名格式  | `{受击等级}_{受击方向}`，例如 `HitLight_Front`             |
| 现有行   | `HitLight` / `HitHeavy` × `Front` / `Back` / `Left` / `Right` |
| 查表回退  | 先找 `{等级}_{方向}`，找不到再找 `{等级}`（倒地 / 死亡不分方向） |
| 播放方式  | 覆盖式播放，不手动 Stop 旧蒙太奇                             |

**受击行里只认以下字段，其余（`DamageRate` / `PoiseDdamageRate` / `Next` / `CancelStart` / `AttackType` 等）在受击语境下无效：**

```
✅ Montage     受击动画
✅ HitStop     受击顿帧
🚫 其余        留空
```

**⚠️ 拼行名不要用 `Enum to String`** —— 它的输出带 `E_AIState::` 前缀或受 DisplayName 影响，拼出来的行名查不到，而且查表失败是静默的。用 `Switch` 映射到字面量。

---

