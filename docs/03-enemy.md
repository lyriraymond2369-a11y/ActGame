# EnemyBase（敌人角色基类）

> 本文件是模块文档。项目总导航、规范与历史见 [README.md](../README.md)。

## 3，EnemyBase（敌人角色基类）（继承于 CharacterBase）

| 组件名             | 组件用途      |
| --------------- | --------- |
| BPC_AI          | 敌人 AI 控制  |
| BPC_AttackTrace | 敌人攻击执行层：播放攻击蒙太奇、开关攻击窗口、修改 Blackboard 参数；不负责行为树选招与战斗决策 |
| BPC_Attribute   | 复用 CharacterBase 的属性组件 |

### 0）敌人 vs 玩家：两套**有意分开**的攻击执行结构

**⚠️ 敌人不挂 `BPC_Combat`。** 攻击的「决策」与「执行」边界如下，勿混用：

| 环节 | 玩家 | 敌人 |
| --- | --- | --- |
| 选招/选目标决策 | `BPC_Combat`（玩家攻击入口与连招链） | BT / BTS / BTT |
| 攻击执行 | `BPC_Combat`（`EnterHit` 等） | `BPC_AttackTrace` |
| 攻击判定窗口 | `ANS_AttackWindow → OnAttackWindow` | `ANS_AttackWindow → OnAttackWindow`（同一通知，作用在 `BPC_AttackTrace`） |
| 受击处理 | `EnterHit` | `PlayHitMontage` |
| 战斗反馈 | `BPI_CombatFeedBack.PlayHitFeedback` | 同左（`BPC_CombatFeedBack`） |

**⚠️ 定性：** `BPC_AttackTrace` 是敌人的「montage 播放器 + Blackboard 写入器」——**不承担选招逻辑**；决策全部在行为树（BTS/BTT）。它与 `BPC_Combat` 只在「开攻击窗口 / 播放攻击 montage」这一点上重叠。

> 若以后想把这些重叠逻辑抽公共函数，可以；现在故意分开：`BPC_Combat` 需适配玩家输入与连招链，`BPC_AttackTrace` 需适配 BT 与 Blackboard，强行合并会生出两套依赖。

### 1）EnemyBase 类接口方法

#### （1）BPI_EnemyBase

| 方法名                     | 输入  | 输出                  | 作用                     |
| ----------------------- | --- | ------------------- | ---------------------- |
| GetAttackTraceComponent | /   | BPC_AttackTrace 对象引用 | 获取 BPC_AttackTrace      |
| GetAIComponent          | /   | BPC_AI 对象引用          | 获取 BPC_AI               |

> `GetMesh`、`GetHitBox`、`GetEnemyAttributeComponent` **已全部上收到** `BPI_CharacterBase`（属性统一走 `GetAttributeComponent`），敌人侧不再各自声明。

#### （2）BPI_AttackTrace

| 方法名            | 输入                                    | 输出   | 作用                    |
| -------------- | ------------------------------------- | ---- | --------------------- |
| OnAttackWindow | bool                                  | /    | 开关攻击窗口                |
| AttackByType   | E_AttackType                          | /    | 根据攻击类型发动攻击            |
| PlayHitMontage | E_AIState（受击等级），E_HitDirection（受击方向） | bool | 查蒙太奇表并播放敌人的受击蒙太奇      |

#### （3）BPI_AI

| 方法名                     | 输入                             | 输出        | 作用                        |
| ----------------------- | ------------------------------ | --------- | ------------------------- |
| AI_GetCurrentTarget     | /                              | Actor     | 获取当前锁定的对象                 |
| AI_GetAIState           | /                              | E_AIState | 获取当前 AI 状态                |
| AI_SetState             | E_AIState（NewState）            | /         | 普通状态写入，内部转 `ApplyState`。**决策层确认后调用** |
| AI_TryEnterState        | E_AIState（NewState）            | bool      | 带优先级闸门的状态进入，返回是否进入。**受击 / 死亡走这个** |
| AI_ReturnToInitialState | /                              | /         | 动作结束后回流：有目标 → `Chase`，无目标 → `Idle` |
| AI_IsAlive              | /                              | bool      | 角色当前是否活着                  |
| AI_HandleSight          | Actor，bool（bSensed）           | /         | 处理视觉感知的进入/丢失。**只维护感知池，不改状态** |
| AI_GetHitStamp          | /                              | int       | 取当前受击戳，供表现层读取             |
| AI_ConsumeHit           | int（Stamp）                    | bool      | 表现层回写已消费的戳，返回是否已全部消费完     |

> **`AI_SetState` 是内部 `ApplyState` 的薄包装** —— 真正写状态的是 `ApplyState`（写 `CurrentState`、同步 `Blackboard.AIState`、处理受击幂等、执行状态副作用）。
>
> **`AI_SetState` 绕过优先级** —— 何时可调由调用方负责。受击、死亡一律走 `AI_TryEnterState`。
>
> **已移除的旧接口**：`AI_AddPerceivedActor` / `AI_RemovePerceivedActor` / `AI_RefreshTarget` / `HandleDamageApplied` 转为内部方法；`AI_ResetAIState` 已删除（无引用）；旧名 `AI_SetAIState` 已改为 `AI_SetState`。
>
> ⚠️ 二进制里仍能搜到 `AI_SetAIState` 等旧名，是 Name Table 残留，以编辑器「我的蓝图 → 函数」面板为准（见遗留问题 ⑦）。

### 2）EnemyBase 数据类型

#### （1）EnemyBase 枚举

##### 一，E_AIState

| 枚举值       | 枚举含义    |
| --------- | ------- |
| Idle      | 站立（待机）  |
| Chase     | 追击      |
| Attack    | 攻击      |
| HitLight  | 轻受击（受控） |
| HitHeavy  | 重受击（受控） |
| KnockDown | 倒地（受控）  |
| Dead      | 死亡（受控）  |

**优先级与受控标记（与 [敌人受击状态机](07-enemy-hit.md) 的 `AIStateProperty` 同源）：**

```
4  Dead        受控，终态
3  KnockDown   受控
2  HitHeavy    受控
1  HitLight    受控
0  Idle / Chase / Attack   非受控，优先级一律为 0
```

> `AI_TryEnterState` 按这张表判断能否进入；`AI_SetState` 绕过优先级（调用方负责时机）。
>
> **⭐ `Attack` 不会被 `Chase` 覆盖，靠的不是优先级** —— 而是 `BTS_UpdateAIState` 在 Attack 期间直接 Return（见下节）。非受控状态优先级都是 0，本来就拦不住彼此。

##### 二，E_Team（已移至 [CharacterBase 数据类型](01-character-base.md)）

**E_Team 属于 CharacterBase 层：阵营是所有角色的固有属性，与敌人无关。见上文的 CharacterBase 枚举。**

---

> 敌人运行导图 → [运行导图 · 敌人](11-run-maps.md)
> 受击状态机 → [敌人受击状态机](07-enemy-hit.md)

---

### 3）AI 分层与职责约定

**层序（越靠上权限越大，只允许上层往下写）：**

```
BPC_AttackTrace     执行攻击 / 结束攻击 / 归还令牌 / 通知动作结束
        ↓
BT · BTS / BTD / BTT   BTS 决策，BTD 只读，BTT 只执行
        ↓
BPC_AI              状态存储 + 优先级仲裁 + 感知 / 目标 / 距离数据
        ↓
Blackboard          共享数据，所有组件都能读
```

**⭐ 核心：`BPC_AI` 不决策，只仲裁 —— 形态与 `BPC_ActionState` 一致。**

#### 黑板读写权限

| 模块 | 读 | 写 | 改 AI 状态 |
| --- | --- | --- | --- |
| `BPC_AI` | ✅ | ✅ 维护自己的数据（`TargetActor` / `DisToTarget` / `AIState`） | 提供接口 |
| `BTS` | ✅ | ✅ 决策数据 | 调 `AI_SetState` |
| `BTD` | ✅ | ❌ | ❌ |
| `BTT` | ✅ | ❌ | ❌ |
| `BPC_AttackTrace` | ✅ | ❌ | 只通过接口通知 |

**⚠️ `Blackboard.AIState` 只能由 `ApplyState` 内部同步，任何人都不得直接写 —— 否则 `CurrentState` 和黑板会分叉，且极难发现。**

#### 状态接口分工

| 触发源 | 场景 | 用哪个 |
| --- | --- | --- |
| `BTS` | `Idle → Chase`、`Chase → Idle`、`Chase → Attack` | `AI_SetState`（绕过优先级，时机由 BTS 保证） |
| `BPC_Attribute` | 任何 → `HitLight` / `HitHeavy` / `KnockDown` | `AI_TryEnterState` |
| `BPC_Attribute` | 任何 → `Dead` | `AI_TryEnterState`（`Dead` 也必须走优先级判定） |
| `BPC_AttackTrace` | 动作结束回流 | `AI_ReturnToInitialState` |

**规律：计划内的正常转换走 `AI_SetState`；外部突发事件走 `AI_TryEnterState`。**

#### `BPC_AI` 的 Tick 只做三件事

```
Tick
├─【1】UpdatePerception()   剔除失效 / 死亡 / 非敌对 / 自己
├─【2】RefreshTarget()      粘性选目标 → 同步 BB.TargetActor
└─【3】UpdateDistances()    算 2D 距离 → 同步 BB.DisToTarget
```

**三条实现要点：**

```
① UpdatePerception 先收集 BadActors 再统一 Remove（不在遍历中删）
② RefreshTarget 是「粘性」的：当前目标仍有效就不换，否则两个近距离目标会让敌人每帧抖动
③ 黑板只在值真的变化时才写（尤其 TargetActor），否则装饰器每帧被无谓触发
```

**⚠️ `UpdatePerception` 不做距离剔除** —— 视野范围由感知系统负责，两处都判会导致每帧反复增删。距离判断属于 `RefreshTarget` 的「选谁」，不属于「谁还在」。

**⚠️ 不要给 `BB.DisToTarget` 加黑板观察者** —— 它每帧都变。需要距离条件时用布尔键（如 `bInAttackRange`），只在跨阈值时写。

#### `BTS_UpdateAIState` 决策流程

**资产：`Enemy/AI/Service/BTS_UpdateAIState`，挂在 `BT_EnemyBase` 的 Root 上，每帧执行。**

```
① 当前是受控状态（HitLight / HitHeavy / KnockDown / Dead）→ 直接 Return
② 当前是 Attack → 直接 Return                  ← 攻击期间完全不决策
③ TargetActor 无效 → 仅当当前是 Chase 才回初始态
④ 距离 > AttackRange → 需要时转 Chase
⑤ 距离够 + 冷却完成 + 令牌到手 → AI_SetState(Attack)
```

**⭐ ② 是修掉「攻击中丢失目标导致状态错乱」的关键：攻击期间 BTS 闭嘴，等 `BPC_AttackTrace` 结束回流。**

**⭐ ③ 的「仅当当前是 Chase」不能放宽成「任何状态 + 无目标 → Idle」—— 那会打断攻击、受击、倒地。**

**⚠️ BTS 是**唯一**做普通状态决策的地方。它只调 `AI_SetState`，不写 `Blackboard.AIState`，也不执行任何行为。**

#### 攻击时序

```
BTS 拿到令牌 → AI_SetState(Attack)
    → BTD 选中 Attack 分支 → BTT_EnemyAttack 调 AttackTrace.AttackByType
    → 攻击期间玩家离开视野：TargetActor 被清，但 BTS 在 Attack 直接 Return，攻击照常播完
    → 蒙太奇结束：AttackTrace 先 RemoveToken，再 AI_ReturnToInitialState
        → 有目标 → Chase，无目标 → Idle
```

**⚠️ 顺序必须是「先还令牌，再回初始状态」。反过来的话，回到 Chase 后 BTS 可能立刻判定可再次攻击，但旧令牌还没释放，状态与资源不同步。**

#### 令牌归属

```
申请   BTS（进入 Attack 之前）—— 申请失败就停在 Chase，不进入 Attack
归还   BPC_AttackTrace（回合结束时）
兜底   BP_GameState · Tick（无效引用 / IsCharacterDead / 持有超时）
```

**⚠️ 不要让 BTT 申请令牌** —— 若 AI 状态已进 `Attack` 而令牌申请失败，BTT 回退但没人结束攻击，会把 AI 卡在 `Attack`。

---

