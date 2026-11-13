# ActGame

动作战斗游戏 · UE5 蓝图项目

本文件是项目内「组件 / 接口 / 数据结构」的速查表，写蓝图前先对一遍。

> **校对说明**：本文件已按 `Content/` 下的实际资产重新扫描校对（共 15 个 `BPI_`*、10 个 `E_`*、3 个 `ST_*`）。
> **接口函数清单以蓝图编辑器「我的蓝图 → 函数」面板为准** —— UE 的 name table 会保留已删除函数的 FName 条目，直接扫二进制会把历史函数误报成现存函数。
> 与旧版不一致的地方统一记在文末的「[10，校对差异清单](#10校对差异清单)」里，方便逐条确认。

---

## 历史

| 日期 | 修改内容 | 具体内容 | 修订人 |
| --- | --- | --- | --- |
| 2026.10.3 | 初稿 | 系统概括 | 作者 |
| 2026.10.4 | 切换引擎 | 转为 UE | 作者 |
| 2026.10.4 | 角色控件 | 角色控件关系图 | 作者 |
| 2026.10.11 | 角色锁定 | 角色锁定系统 | 作者 |
| 2026.10.12 | 设置锁定组件 | 更新组件关系图 | 作者 |
| 2026.10.24 | 仓库初始化 | UE 工程首次提交 | 作者 |
| 2026.10.31 | 项目资产入库 | `Config` / `Content Code` / `Player` / `Enemy` 自有资产；补充引擎角色模板资源（骨骼网格 / 动画 / 材质） | 作者 |
| 2026.10.31 | 分层重构 | Attribute / ActionState / Combat 三层职责重划；补 `ReceiveDamage` 受击判定与 `ClearPoseBroken`；ActionState 去掉 Motor 依赖 | 作者 |
| 2026.10.31 | 震屏链路 | `CombatFeedBack` 经 `BPI_CameraDirector.Shake` 接回震屏；`DT_Attacks` 攻击数据更新 | 作者 |
| 2026.11.01 | 位移与受击 | 位移职责移交 Motor；接入玩家受击逻辑 | 作者 |
| 2026.11.01 | 目录重构 | Attribute 迁至 `ActorComponent/Attribute`；`BPI_HIt` 并入 `BPI_Combat` | 作者 |
| 2026.11.02 | 运行导图 | 新增玩家 / 敌人 Mermaid 运行导图；README 增加三级目录与锚点校验 | 作者 |
| 2026.11.03 | 敌人受击 | 受击状态机 + 受击表现链路 | 作者 |
| 2026.11.05 | 完美闪避 | 无敌帧 / 完美窗口 / 慢动作奖励；README 重构为「功能实现 + 运行导图」 | 作者 |
| 2026.11.05 | 闪避收尾 | 改为延时收尾 + 只慢敌人；闪避默认方向按索敌状态 | 作者 |
| 2026.11.06 | 闪避表现 | MetaSound 合成起始音；PoseableMesh 姿态残影 | 作者 |
| 2026.11.06 | 闪避反击 | 完美闪避反击窗口与分离动作冲量 | 作者 |
| 2026.11.07 | 刀光 | 改用 Niagara 条带拖尾，接入动画通知 | 作者 |
| 2026.11.08 | 攻击令牌 | 限制同屏进攻人数，申请 / 归还 / 兜底三层 | 作者 |
| 2026.11.08 | AI 重构 | 敌人 AI 状态流重构，接入阵营系统 | 作者 |
| 2026.11.09 | 枚举归位 | `E_Team` 迁至 CharacterBase 枚举 | 作者 |
| 2026.11.10 | 完美格挡 | 完美格挡判定、格挡 CD、`Block` 反击窗口 | 作者 |

---

## 目录

- [历史](#历史) —— 版本变更记录
- [规范](#规范) —— 写代码前必须遵守的硬规则
- [0，接口总览](#0接口总览) —— 全部接口与函数数的总表，找不到东西先看这里
- [1，CharacterBase（角色基类）](#1characterbase角色基类)
    - [1）CharacterBase 类接口方法](#1characterbase-类接口方法)
        - [BPI_CharacterBase](#1bpi_characterbase)
        - [BPI_Attribute](#2bpi_attribute)
        - [BPI_CombatFeedBack](#3bpi_combatfeedback)
        - [BPI_Motor](#4bpi_motor)
    - [2）CharacterBase 数据类型](#2characterbase-数据类型)
        - [CharacterBase 枚举](#1characterbase-枚举)
        - [结构体](#2结构体)
- [2，Player（玩家特有）](#2player玩家特有继承于-characterbase)
    - [1）Player 类接口方法](#1player-类接口方法)
        - [BPI_Player](#1bpi_player)
        - [BPI_ActionState](#2bpi_actionstate)
        - [BPI_BufferInput](#3bpi_bufferinput)
        - [BPI_CameraDirector](#4bpi_cameradirector)
        - [BPI_Combat](#5bpi_combat)
        - [BPI_LockOn](#6bpi_lockon)
    - [2）Player 数据类型](#2player-数据类型)
        - [Player 枚举](#1player-枚举)
- [3，EnemyBase（敌人角色基类）](#3enemybase敌人角色基类继承于-characterbase)
    - [1）EnemyBase 类接口方法](#1enemybase-类接口方法)
        - [BPI_EnemyBase](#1bpi_enemybase)
        - [BPI_AttackTrace](#2bpi_attacktrace)
        - [BPI_AI](#3bpi_ai)
    - [2）EnemyBase 数据类型](#2enemybase-数据类型)
        - [EnemyBase 枚举](#1enemybase-枚举)
- [4，WeaponBase（武器基类）](#4weaponbase武器基类)
    - [1）WeaponBase 类接口方法](#1weaponbase-类接口方法)
        - [BPI_WeaponBase](#1bpi_weaponbase)
- [5，其他独立接口](#5其他独立接口)
    - [BPI_GameState](#1bpi_gamestatecodegamestate)
    - [BPI_HIt（已删除）](#2bpi_hit)
    - [BPI_Interaction（已删除）](#3bpi_interaction)
- [6，写蓝图时的三条硬规矩](#6写蓝图时的三条硬规矩) —— 分层约定，动手前先读
- [7，玩家侧动画通知与职责](#7玩家侧动画通知与职责) —— 四个动画通知分别调谁
- [8，功能实现](#8功能实现) —— 单个机制的设计细则
    - [1）敌人受击状态机](#1敌人受击状态机) —— 等级、优先级、幂等与重播
    - [2）完美闪避与无敌帧](#2完美闪避与无敌帧) —— 无敌区间 / 完美窗口 / 奖励链
    - [3）完美格挡](#3完美格挡) —— 判定、格挡 CD、反击窗口、与闪避反击的优先级
    - [4）闪避方向（四向）](#4闪避方向四向) —— 方向判定、参考系对齐、四行数据
    - [5）动作位移：水平与垂直冲量必须分开处理](#5动作位移水平与垂直冲量必须分开处理) —— 近身撞人时上挑被吞的原因
    - [6）刀光：Niagara 条带拖尾](#6刀光niagara-条带拖尾) —— 为什么不用静态弧面、条带的三条硬设置
    - [7）攻击令牌：同屏进攻名额](#7攻击令牌同屏进攻名额) —— 四道守卫、三层兜底、永远留一个在外围
- [9，运行导图](#9运行导图) —— 组件之间的实际流转
    - [1）玩家运行导图](#1玩家运行导图) —— 输入到伤害
    - [2）敌人运行导图](#2敌人运行导图) —— 感知到伤害
- [10，校对差异清单](#10校对差异清单)
    - [已修正的文档错误](#已修正的文档错误)
    - [需要在编辑器里处理的遗留问题](#需要在编辑器里处理的遗留问题)

---

# 注：

```
接口名与其实现的组件名相同
```

---

## 规范

> **这一节是硬规则清单。** 写蓝图之前先过一遍 —— 不符合的要么改代码，要么先改本节，**不要在代码里开特例**。
>
> 分层职责的深度展开另见 [6，写蓝图时的三条硬规矩](#6写蓝图时的三条硬规矩)。

### 1）调用边界：跨组件只能走接口

```
① 一个蓝图只能通过目标组件实现的 BPI 接口调用它
   不能 Cast To 具体组件蓝图，再调它的内部函数

② Cast 的目标一律是基类接口（BPI_CharacterBase），不 Cast To BPI_Player
   → 敌人挂同一套动画通知也不用改

③ 组件自己的内部函数（【内部函数】）对外一律不可见
   需要外部调用 → 先在 BPI 里加方法，再在组件里实现

④ 数据的读取与写入同样走接口
   例：LastGuardEndTime 只能通过 BPI_Combat.SetLastGuardEndTime 修改
       外部直接写变量会让 CD 逻辑分叉到两处

⑤ 跨组件链路要沿既定的中转走，不要抄近道
   例：BPC_Combat 不直接碰 BPC_CameraDirector
       走 CombatFeedBack → BPI_CameraDirector
```

**反例：**

```
✗ BPC_Combat → Cast To BPC_CameraDirector → 直接 PlayPerfectBlockCloseUp
✓ BPC_Combat → BPI_CombatFeedBack.PlayHitFeedback → BPI_CameraDirector.PlayPerfectBlockCloseUp
```

### 2）函数类型：四种标注，缺一不可

**文档与蓝图里提到函数时，必须能一眼看出它属于哪一类：**

| 标注 | 含义 | 占接口计数 |
| --- | --- | --- |
| **【接口】** | 定义在 `BPI_xxx` 里，跨组件调用必须走它 | ✅ |
| **【接口实现】** | `BPC_xxx` 里实现某个 `BPI` 函数 | ✅（归接口） |
| **【内部函数】** | 组件自己的函数，外部不可调用 | ❌ |
| **【事件】** | 分发器 / 自定义事件 | ❌ |
| **【引擎 API】** | UE 自带节点 | ❌ |

**⭐ 「接口数 98」只统计【接口】，其余三类都不计。**

### 3）组件实现约束

```
① ActorComponent / SceneComponent 蓝图里不能用 Timeline 节点
   Timeline 依赖 UTimelineComponent 作为成员，而 Add Component(Timeline)
   只在 Actor 蓝图里提供
   → 组件内需要插值的一律用 TickComponent 手动推进
   → Set Timer by Event 在组件里可用，不受此限制

② 组件内做插值时，时间源用 Get Game Time in Seconds
   不要用 Tick 的 DeltaTime 累加 —— 顿帧会把该 Actor 的 DeltaTime 压到 0

③ 组件的 Tick 只在必要时开启，用完立刻关
   常开的 Tick 组件越多，帧预算越难控
```

### 4）时间与缩放

```
① 只慢敌人用 SetCustomTimeDilation，不用 SetGlobalTimeDilation
   GlobalTimeDilation 会一并拖慢 Set Timer 的游戏时间
   → 反击窗口、CD 的计时全部变长

② 任何时间缩放都必须有恢复入口
   开缩放时 Clear and Invalidate Timer，恢复时显式 Set 回 1.0
   → 否则重复触发会叠加，或永久停在慢速

③ 顿帧只作用于单个 Actor
   需要「双方都停」时，双方各调一次 PlayHitStop(Self, 时长)

④ 顿帧与慢速必须串行，不能同时开
   同时开的话慢速期间的时间膨胀被顿帧覆盖，慢速时长会被拉长
```

### 5）位移与冲量

```
① 单体位移用 AddImpulse(bVelChange = true)
   不要用 Launch Character —— 它会强制切到 MOVE_Falling，
   后续 IsFalling 判定、空中动画全部被误触发

② 水平与垂直冲量必须分开处理
   不分开的话，近身撞人时上挑的垂直分量会被水平位移吞掉
   （详见 8-5）

③ 位移窗口由动画通知（ANS_Move）开合，不由 Combat 直接调
   → 前摇不会提前滑出去
```

### 6）状态表达

```
① 一个状态只用一个变量表达
   不要同时用 bool + enum / 两个 bool 描述同一件事
   → 只要有一条路径忘了同步，就会出现「标志位说没在做、枚举停在中间」
   → 这种 bug 不报错，只能靠读代码发现

② 能从别的量算出来的，不要额外存 bool
   bGuardOnCooldown = (Now - LastGuardEndTime) < GuardCD
   → 不存 bGuardOnCooldown 本身

③ 枚举新值一律追加在末尾，不插中间
   插中间会让已保存的枚举值全部错位，而且不报错
```

### 7）依赖方向

```
① 状态层（BPC_ActionState）不引用任何其他组件
   只管 CurrentState、bCanCancel 和转场规则

② 通用组件（BPC_Attribute，敌人也有）不反向依赖玩家特有组件（BPC_Combat）
   → 「启动格挡 CD」放在 Player 侧入口，Combat 只提供接口

③ 伤害规则全部收在 BPC_Attribute
   无敌、完美格挡、完美闪避、减伤、削轫、破韧都在这一个地方判定

④ 判定与表现分离
   Attribute 判定 + 广播带位置 → Combat 收尾 + 转发反馈
   Attribute 不生成粒子、不震屏、不播音效
```

### 8）文档约定

```
① 接口函数清单以蓝图编辑器「我的蓝图 → 函数」面板为准
   不要直接 grep .uasset —— name table 会保留已删除函数的 FName

② 每个函数必须标注类型（见本节 2）
③ 每次设计变更同时更新「历史」表与「10，校对差异清单」
④ 接口数变化必须同步「0，接口总览」与本节的统计口径
```

---

## 0，接口总览

| 接口                       | 目录                                 | 函数数 | 对应实现               |
| ------------------------ | ---------------------------------- | --- | ------------------ |
| BPI_CharacterBase        | Code/Interface                     | 10  | 无（纯接口，所有组件获取的统一入口） |
| BPI_Attribute            | Code/ActorComponent/Attribute      | 15  | BPC_Attribute      |
| BPI_CombatFeedBack       | Code/ActorComponent/CombatFeedBack | 4   | BPC_CombatFeedBack |
| BPI_Motor                | Code/ActorComponent/Motor          | 9   | BPC_Motor          |
| BPI_WeaponBase           | Code/Weapon                        | 3   | BP_WeaponBase      |
| BPI_GameState            | Code/GameState                     | 3   | 待接入                |
| BPI_Player               | Player                             | 12  | BP_Player          |
| BPI_ActionState          | Player/Component/ActionState       | 8   | BPC_ActionState    |
| BPI_BufferInput          | Player/Component/BufferInput       | 3   | BPC_BufferInput    |
| BPI_CameraDirector       | Player/Component/CameraDirector    | 2   | BPC_CameraDirector |
| BPI_Combat               | Player/Component/Combat            | 9   | BPC_Combat         |
| BPI_LockOn               | Player/Component/LockOn            | 6   | BPC_LockOn         |
| BPI_EnemyBase            | Enemy                              | 2   | BP_EnemyBase       |
| BPI_AttackTrace          | Enemy/Component/AttackTrace        | 3   | BPC_AttackTrace    |
| BPI_AI                   | Enemy/Component/AI                 | 9   | BPC_AI             |

合计 98 个接口函数。

---

## 1，CharacterBase（角色基类）

| 组件名                | 组件用途      |
| ------------------ | --------- |
| BPC_Attribute      | 角色属性      |
| BPC_CombatFeedBack | 角色攻击音效，顿帧 |
| BPC_Motor          | 角色运动层控制   |

### 1）CharacterBase 类接口方法

#### （1）BPI_CharacterBase

| 方法名                        | 输入                           | 输出                         | 作用                       |
| -------------------------- | ---------------------------- | -------------------------- | ------------------------ |
| GetAttributeComponent      | /                            | BPC_Attribute 对象引用         | 获取角色的 BPC_Attribute      |
| GetCombatFeedbackComponent | /                            | BPC_CombatFeedBack 对象引用    | 获取角色的 BPC_CombatFeedBack |
| GetMotorComponent          | /                            | BPC_Motor 对象引用             | 获取角色的 BPC_Motor          |
| GetCharacterMovement       | /                            | CharacterMovementComponent | 获取角色的移动组件                |
| GetMeshComponent           | /                            | SkeletalMeshComponent      | 获取角色的骨骼网格体组件             |
| GetHitBoxComponent         | /                            | BoxComponent               | 获取角色的受击盒                 |
| GetWeapon                  | /                            | BP_WeaponBase 对象引用         | 获取角色当前武器                 |
| ApplyImpulse               | Vector3，XYOverride，ZOverride | /                          | 按状态计算当前应施加的冲量            |
| IsCharacterDead            | /                            | bool                       | 角色是否死亡。**不依赖 Attribute 组件，供 GameState 等全局层判断** |
| IsHostile                  | Actor（Other）                 | bool                       | 判断 Other 是否为敌对。**对方未实现本接口 / 同队 → false**。在 `BP_Player` 与 `BP_EnemyBase` 各实现一份 |

> **这里是全部「取组件 / 取引用」的唯一入口。**
> `BPI_Player` 与 `BPI_EnemyBase` 不再重复声明 `GetMesh` / `GetHitBox` / `GetWeapon` / `GetAttributeComponent`，写蓝图时统一从基类接口取。

#### （2）BPI_Attribute

| 方法名              | 输入                                   | 输出                     | 作用                                              |
| ---------------- | ------------------------------------ | ---------------------- | ----------------------------------------------- |
| GetAttack        | /                                    | float（Attack）          | 获取角色的攻击值（包括武器基础加成）                              |
| GetDefense       | /                                    | float（Defenses，0~1）    | 获取角色减伤                                          |
| GetPoiseAttack   | /                                    | float（PoiseAttack）     | 获取角色的削轫值（包括武器基础加成）                              |
| GetTeam          | /                                    | E_Team                  | 获取阵营。`Neutral` / `Player` / `Enemy`，用于敌我判定         |
| AddBonus         | float（AttackDelta）                   | /                      | 添加武器加成                                          |
| IsDead           | /                                    | bool（Dead）             | 角色是否死亡                                          |
| TakeDamage       | float（BaseDamage），float（PoiseDamage） | bool（bIsBroken）        | 扣血扣韧，返回是否破韧。**内部不再乘防御**                         |
| ReceiveDamage    | ST_AttackData，float，Vector3（攻击者位置），Vector3（HitPoint），float | E_HitOutCome，bool，bool | 完整受击判定：攻击数据、基础伤害、攻击者位置、击中点、基础削轫 → 受击类型、是否完美格挡、是否完美闪避 |
| ClearPoseBroken  | /                                    | /                      | 清除削轫破防效果                                        |
| RestorePoise     | /                                    | /                      | 恢复韧性到 MaxPoise（Tick 里调用）                        |
| EnterGuard       | /                                    | /                      | 进入格挡：置 bIsGuarding，记录 LastGuardTime             |
| ExitGuard        | /                                    | /                      | 退出格挡                                            |
| NotifyDodgeStart | float（Time）                          | /                      | 记录闪避起手时刻，供完美闪避窗口判定使用                            |
| SetInvincible    | bool（bInvincible）                     | /                      | 开关无敌。由 `ANS_IFrame` 的 Begin / End 调用              |
| EndPerfectDodge  | /                                    | /                      | 完美闪避收尾：若仍在无敌则关无敌并补一段尾巴。由 Combat 调用 |

`ReceiveDamage` **的三个输出含义：**

| 输出              | 含义                                        |
| --------------- | ----------------------------------------- |
| HitOutCome      | `Ignore` 无伤 / `Hit` 普通受击 / `Blocked` 格挡生效 |
| bPerfectBlock   | 是否完美格挡（完全免伤）                              |
| bPerfectDodge   | 是否完美闪避（在无敌帧内**且**处于完美窗口）                  |

**判定优先级（顺序不能调）：**

```
① 已死亡                        → Ignore
② 无敌中（bInvincible 或 无敌尾巴）
     且在完美窗口内              → Ignore + bPerfectDodge = true
     仅无敌、不在完美窗口        → Ignore，bPerfectDodge = false
③ 格挡 + 正面 + Poise>0         → 完美格挡窗口内？Blocked + bPerfectBlock 免伤
                                  否则 Blocked，伤害 ×(1−GuardDamageReduction)，削轫 ×GuardPoiseScale
④ 其余（含背面格挡）             → Hit，伤害 ×(1−Defense)
```

**② 的两个条件是 `AND`：只判时间会把闪避结束后的受击误判成完美；只判无敌会把整个无敌区间都算成完美，缓冲带就没了。**

**五个输入的分工：**

| 输入 | 参与判定 | 用途 |
| --- | --- | --- |
| `ST_AttackData` | ✅ | 伤害倍率、削轫倍率 |
| `BaseDamage` | ✅ | 基础伤害 |
| `攻击者位置` | ✅ | **算受击方向**（正面 / 背面 / 左 / 右） |
| `HitPoint` | ❌ | **只用于表现**：火花位置、震屏位置、FOV 特写锚点 |
| `BasePoiseDamage` | ✅ | 基础削轫 |

**⭐ `攻击者位置` 与 `HitPoint` 是两个不同的量，不能互相替代：**

```
攻击者位置 → 判断「攻击从哪个方向来」→ 决定正面/背面格挡
HitPoint   → 判断「打在哪里」       → 决定火花生成在哪里

贴身攻击时两者相差很小，长武器时相差很大
用 HitPoint 算方向 → 长武器从侧面挥来会被判成正面格挡
用攻击者位置做火花 → 火花会在敌人身上而不是武器接触点
```

**⚠️ `HitPoint` 不参与任何判定，加它只是为了让表现层有正确的锚点。**

**韧性为 0 时格挡完全失效，完美格挡也一并失效。**

#### （3）BPI_CombatFeedBack

| 方法名             | 输入                                            | 输出  | 作用                                            |
| --------------- | --------------------------------------------- | --- | --------------------------------------------- |
| PlayHitFeedback | E_HitOutCome（Outcome），Vector3（ImpactLocation），bool（bPerfect），Actor（OtherActor），float（BaseHitStop） | /   | 播放命中音效、顿帧、屏幕抖动                                |
| PlayHitStop     | Actor，float                                   | /   | 根据命中者与时长播放顿帧                                  |
| EndHitStop      | /                                             | /   | 离开顿帧                                          |
| PlayEnemySlowMo | float（Scale），float（Duration） | /   | 按倍率与时长放慢全场敌人（自带恢复计时）。**完美闪避传 (0.1, 0.5)，完美格挡传 (0.15, 0.12)** |

#### （4）BPI_Motor

| 方法名                | 输入                          | 输出   | 作用               |
| ------------------ | --------------------------- | ---- | ---------------- |
| ApplyKnockback     | Vector3（Force），bool（bIgnoreMove） | /    | 施加一个冲量           |
| SetMotionProfile   | ST_MotionProfile（profile）   | /    | 设置代码位移的基础变量      |
| StartMotion        | /                           | /    | 开始代码位移           |
| StopMotion         | /                           | /    | 停止代码位移           |
| IsMoving           | /                           | bool | 当前是否在代码位移中       |
| IsBeingKnockedBack | /                           | bool | 当前是否在被击退         |
| SetGravity         | float（Scale）               | /    | 设置重力倍率           |
| ResetGravity       | /                           | /    | 重力恢复默认值          |
| SetMotionScale     | float（Scale）               | /    | 位移速度倍率。完美闪避时降到 0.3 控距离，收尾必须复位为 1.0 |

### 2）CharacterBase 数据类型

#### （1）CharacterBase 枚举

##### 一，E_AttackType（攻击类型）

| 枚举值    | 枚举含义 |
| ------ | ---- |
| Common | 普通攻击 |

##### 二，E_HitOutCome（受击类型）

| 枚举值     | 枚举含义 |
| ------- | ---- |
| Ignore  | 忽略   |
| Hit     | 普通受击 |
| Blocked | 防御   |

##### 三，E_HitDirection

| 枚举值   | 枚举含义 |
| ----- | ---- |
| Front | 前方   |
| Back  | 后方   |
| Left  | 左边   |
| Right | 右边   |

##### 四，E_Team（阵营）

| 枚举值       | 枚举含义          |
| --------- | ------------- |
| Neutral   | 中立 / 无阵营（环境物件） |
| Player    | 玩家            |
| Enemy     | 敌人（含训练木桩）     |

> **资产位置**：`Code/Enum/E_Team`，与 `E_AttackType` / `E_HitOutCome` / `E_HitDirection` 同目录。
>
> **新值一律追加在末尾，不要插入中间** —— 插在中间会让已保存资产按旧索引解析。
>
> 敌我判定统一走 `BPI_CharacterBase.IsHostile`，规则：**对方未实现接口 / 同队 → `false`；不同阵营 → `true`**。`Neutral` 不做例外，所以「忘记配 Team」的失败表现是「打不到它」而不是「互相误伤」。
>
> **归属**：阵营是所有角色的固有属性（玩家 / 敌人 / 未来的友军共用一套），因此属于 CharacterBase 层，不属于 EnemyBase。

#### （2）结构体

##### 一，ST_AttackData

| 值名               | 类型           | 默认值     | 含义                           |
| ---------------- | ------------ | ------- | ---------------------------- |
| ID               | name         | none    | 动作名                          |
| Montage          | 动画蒙太奇        | none    | 动作播放的 montage                |
| SectionStart     | name         | none    | montage 开始播放的片段              |
| Next             | ST_Edge 数组   | none    | 下一个动作名以及进入所需的操作              |
| CancelStart      | float        | 0       | 取消窗口打开的时间                    |
| DamageRate       | float        | 0       | 伤害倍率                         |
| PoiseDdamageRate | float        | 0       | 削轫倍率（**资产里就是两个 d，别改成 Ddamage 以外**） |
| HitStop          | float        | 0       | 顿帧时长                         |
| LaunchEnemy      | Vector3      | （0，0，0） | 命中敌人时对敌人的力                   |
| LaunchSelf       | Vector3      | （0，0，0） | 命中敌人时对自己的力                   |
| MotionSelf       | Vector3      | （0，0，0） | xy 表示位移方向，z 表示对角色向上的力        |
| CanUseInAir      | bool         | false   | 是否可以在空中使用                    |
| PlayGravity      | float        | 1       | 使用时角色的重力                     |
| MoveSpeed        | float        | 600     | 水平移动速度（大于 610 才有代码位移）        |
| MoveFriction     | float        | 8       | 移动时角色摩擦力                     |
| bLockPelvisZ     | bool         | false   | 是否锁定 Pelvis 骨骼的 z 坐标         |
| AttackType       | E_AttackType | Common  | 动作的攻击类型                      |

##### 二，ST_Edge

| 值名     | 类型          | 默认值  | 含义           |
| ------ | ----------- | ---- | ------------ |
| NextID | name        | none | 下一个动作的 ID    |
| Input  | E_InputType | none | 进入下一个动作所需的输入 |

##### 三，ST_MotionProfile

| 值名           | 类型      | 默认值     | 含义   |
| ------------ | ------- | ------- | ---- |
| speed        | float   | 0       | 水平速度 |
| direction    | vector3 | （0，0，0） | 水平方向 |
| friction     | float   | 8       | 摩擦力  |
| gravityScale | float   | 1       | 重力大小 |

---

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

**三个转换入口的分工：**

```
TryEnterState    状态层说了算 —— 查转场矩阵
ForceEnterState  战斗层说了算 —— 战斗层已判定连招成立，状态层照做
SetState         不用判断   —— 复位收尾
```

**受控状态（HitLight / HitHeavy / KnockDown / Dead）内部有优先级，可升级、可幂等，不可降级、不可逃逸。**

#### （3）BPI_BufferInput

| 方法名     | 输入          | 输出   | 作用                 |
| ------- | ----------- | ---- | ------------------ |
| Push    | E_InputType | /    | 向缓存中推入新的输入         |
| Comsume | E_InputType | bool | 读取缓存中的指定输入，并返回是否成功 |
| Peek    | E_InputType | bool | 看缓存中是否有指定且没过期的输入   |

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
| TryGuard         | /    | bool          | 格挡入口：状态判断 + CD 判断 + 原流程。**门槛统一在这里，玩家蓝图不存变量** |
| SetLastGuardEndTime | float（Time） | /   | 启动或清空格挡 CD（传 -9999 即清空）。**格挡 CD 只由这个接口修改** |

> **位移不再经过 Combat。** `ANS_Move` 直接调 `BPI_Motor.StartMotion` / `StopMotion`，
> Combat 只负责在动作开始时用 `SetMotionProfile` 下发速度和方向。
> 原先的 `MoveStart` / `MoveEnd` 两个纯转发函数已删除。

#### （6）BPI_LockOn

| 方法名              | 输入  | 输出            | 作用        |
| ---------------- | --- | ------------- | --------- |
| GetFocusTarget   | /   | Actor         | 获取当前锁定的对象 |
| GetTarget        | /   | Actor         | 获取候选/当前目标 |
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
| KnockDown  | 倒地（受控）                   |
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
| Run  | 奔跑   |

---

> 玩家运行导图 → [9，运行导图 · 1）玩家运行导图](#1玩家运行导图)

---

## 3，EnemyBase（敌人角色基类）（继承于 CharacterBase）

| 组件名             | 组件用途      |
| --------------- | --------- |
| BPC_AI          | 敌人 AI 控制  |
| BPC_AttackTrace | 敌人攻击判定    |
| BPC_Attribute   | 复用 CharacterBase 的属性组件 |

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

**优先级与受控标记（与 [8，功能实现 · 1）敌人受击状态机](#1敌人受击状态机) 的 `AIStateProperty` 同源）：**

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

##### 二，E_Team（已移至 [1，CharacterBase · 2）CharacterBase 数据类型](#2characterbase-数据类型)）

**E_Team 属于 CharacterBase 层：阵营是所有角色的固有属性，与敌人无关。见上文的 CharacterBase 枚举。**

---

> 敌人运行导图 → [9，运行导图 · 2）敌人运行导图](#2敌人运行导图)
> 受击状态机 → [8，功能实现 · 1）敌人受击状态机](#1敌人受击状态机)

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

## 4，WeaponBase（武器基类）

### 1）WeaponBase 类接口方法

#### （1）BPI_WeaponBase

| 方法名             | 输入  | 输出    | 作用             |
| --------------- | --- | ----- | -------------- |
| GetWeaponBonus  | /   | float | 获取武器的攻击力加成     |
| GetWeaponHitBox | /   | 盒体碰撞  | 获取武器碰撞箱        |
| SetTrailActive  | bool | /     | 开关武器拖尾，`true` 激活 / `false` 停用（停用不销毁已生成粒子） |

---

## 5，其他独立接口

### （1）BPI_GameState（Code/GameState）

| 方法名         | 输入            | 输出   | 作用        |
| ----------- | ------------- | ---- | --------- |
| AddToken    | Actor（Holder） | /    | 为持有者登记令牌  |
| RemoveToken | Actor（Holder） | /    | 移除持有者的令牌  |
| HasToken    | Actor（Holder） | bool | 查询持有者是否有令牌 |

### （2）BPI_HIt

**已删除。`EnterHit` 已合并进 `BPI_Combat`，签名改为 `EnterHit(E_ActionState HitType, E_HitDirection HitLoc)`。**

### （3）BPI_Interaction

**已删除（原为空壳，0 个函数）。**

---

## 6，写蓝图时的三条硬规矩

> 本节是 [规范](#规范) 第 7 条「依赖方向」的深度展开。完整规则清单见规范，这里是分层职责的具体边界。

```
① 状态层（BPC_ActionState）不引用任何其他组件
   它只管 CurrentState、bCanCancel 和转场规则

② 伤害规则全部收在 BPC_Attribute
   无敌、完美格挡、完美闪避、减伤、削轫、破韧都在这一个地方判定

③ 战斗层负责「用什么参数」，动画通知负责「什么时候」
   Combat → SetMotionProfile / 调 ReceiveDamage / 调 PlayHitFeedback
   通知   → Motor.StartMotion / StopMotion（位移窗口和动画帧对齐）
   Motor  → 只执行，不判断该不该动

   位移**不**经过 Combat。ANS_Move 直连 BPI_Motor
```

`BPC_CombatFeedBack` **内部再调** `BPC_CameraDirector.Shake`**，Combat 不直接碰 CameraDirector。**

---

## 7，玩家侧动画通知与职责

| 通知                 | 类型          | 调用的接口                                  | 职责                                        |
| ------------------ | ----------- | -------------------------------------- | ----------------------------------------- |
| `ANS_AttackWindow` | NotifyState | `BPI_Combat.OnAttackWindow(bool)`      | 开合攻击判定窗口，驱动 AttackTrace 的命中检测             |
| `ANS_Move`         | NotifyState | `BPI_Motor.StartMotion` / `StopMotion` | 开合代码位移窗口                                  |
| `ANS_LandCheck`    | NotifyState | 自有逻辑（不经过 Combat）                       | 落地检测                                      |
| `ANS_WeaponTrail`  | NotifyState | `BPI_WeaponBase.SetTrailActive(bool)`  | 开合武器拖尾（Niagara 条带）的生成区间 |
| `AN_Cancel`        | Notify      | 目前**未接** `SetCancelWindow`             | 取消窗口时机改由 `ST_AttackData.CancelStart` 数据驱动 |

**三个要点：**

```
① 通知统一走 BPI_CharacterBase → GetMotorComponent / GetCombatComponent
   Cast 目标是基类接口，不 Cast To BPI_Player
   → 敌人挂同一套通知也不用改

② 位移窗口由通知控制，不是「整个蒙太奇都在动」
   → 前摇不会提前滑出去，位移只发生在配了 ANS_Move 的那一段

③ AN_Cancel 目前是空壳
   取消窗口由 Combat 按 CancelStart 自己开合
   要么删掉这个通知，要么改成让它调 SetCancelWindow —— 别两边都做

④ ANS_WeaponTrail 是唯一操作「武器」的通知
   武器通过 BPI_CharacterBase.Get Weapon 拿到，不 Cast 具体武器蓝图
   → 换刀、双持都不用改通知
```

---

## 8，功能实现

> 单个机制的设计细则：规则、判定顺序、数据来源。
> 只讲「怎么判」，不讲「谁调谁」—— 组件流转看 [9，运行导图](#9运行导图)。

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

**判定写在 `ReceiveDamage` 里，分支见 [BPI_Attribute](#2bpi_attribute) 的 ② 条。**
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
① CameraDirector.Shake(PerfectDodge)          震屏
② 音效
③ CombatFeedBack.PlayEnemySlowMo(0.1, 0.5)    只慢敌人（0.1 倍 × 0.5s）
④ Motor.SetMotionScale(0.3)                   位移衰减，控距离
⑤ bPerfectDodgePending = true
   Set Timer(PerfectDodgeCancelDelay → TryFinishPerfectDodge)
```

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
| `BlockCounter_L2` | `BlockCounter_L3` |
| `BlockCounter_L3` | `BlockCounter_L4` |
| `BlockCounter_L4` | 空（收招） |
| `BlockCounter_H1` | `BlockCounter_H2` |
| `BlockCounter_H2` | `BlockCounter_H3` |
| `BlockCounter_H3` | 空（收招） |

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

### 3）完美格挡

> **状态：设计已定稿，实现进行中。**
>
> **⚠️ 本节只写完美格挡。普通格挡受击（`Blocked` 非完美）的表现与状态处理尚未完善，不在此列。**

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
     在 PerfectGuardWindow 内   → Blocked + bPerfectBlock = true（免伤）
     否则                       → Blocked，伤害 ×(1−GuardDamageRate)，削轫 ×GuardPoiseRate
```

**⭐ 所以"判定"这件事本来就完成了，本节要补的是**判定成功之后发生什么**。**

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
  ├─【2】BPI_Combat.SetLastGuardEndTime(-9999)      【接口】清格挡 CD
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

#### （5）格挡 CD：为什么需要，加在哪

**问题：** 完美格挡会强制退出格挡。如果没有任何代价，玩家可以「格挡 → 完美 → 立刻再格挡」无限循环，等于无敌。

**所以普通退出格挡要付一点冷却，而完美格挡把这个冷却免掉 —— 这才是奖励。**

| 变量 | 所在 | 类型 | 默认 | 说明 |
| --- | --- | --- | --- | --- |
| `GuardCD` | `BPC_Combat` | float | 0.4 | 普通退出格挡后的冷却 |
| `LastGuardEndTime` | `BPC_Combat` | float | -9999 | 上次退出格挡的时刻 |

**派生判断（不存 bool，避免状态量泄漏）：**

```
bGuardOnCooldown = (Now - LastGuardEndTime) < GuardCD
```

**⚠️ `LastGuardEndTime` 是 `BPC_Combat` 的变量，外部**不能直接写**，必须走接口：**

```
BPI_Combat.SetLastGuardEndTime(Time : float)
   Player 主动松开格挡 → SetLastGuardEndTime(Now)        → 启动 CD
   HandlePerfectBlock  → SetLastGuardEndTime(-9999)     → 清空 CD
```

**⭐ 依赖方向：`BPC_Attribute` 是通用组件（敌人也有），不该反过来调 Player 特有的 `BPC_Combat`。所以"启动 CD"这件事放在 Player 侧的入口，Combat 只提供接口。**

#### （6）格挡入口：只在原流程前加一道门槛

**原流程（不动）：**

```
TryEnterState(Guard) → Attribute.EnterGuard() → 锁定动作
```

**新增门槛（`BPC_Combat.TryGuard`）：**

```
TryGuard() → bool
  ├─【1】Branch: BPI_ActionState.GetActionState() == Guard
  │        → Return false                ← 已在格挡（用状态判断，最本质）
  ├─【2】Branch: bGuardOnCooldown == true
  │        → Return false                ← CD 内
  └─【3】原流程：TryEnterState(Guard) → EnterGuard() → Return true
```

**⚠️ 第 1 步用 `GetActionState() == Guard`，不要用 `bIsGuarding`：**

```
ActionState.Guard   = 当前正在执行格挡动作     ← 判断"能不能再进格挡"用这个
bIsGuarding         = 玩家仍持有格挡意图       ← 跨受击保留，用于伤害判定
两者语义不同，不能互相替代
```

**⭐ 玩家蓝图里不加任何新变量 —— `GuardCD` / `LastGuardEndTime` 全在 `BPC_Combat`，外部只调 `TryGuard()` 与 `SetLastGuardEndTime()`。**

#### （7）完整时间轴

```
t = 0.00   按下格挡
           ├─ BPI_Combat.TryGuard()
           │    ├─ GetActionState() != Guard ✅
           │    ├─ bGuardOnCooldown == false ✅
           │    └─ TryEnterState(Guard) → EnterGuard()
           │         └─ bIsGuarding = true，bPerfectBlockUsed = false
           └─ 进入格挡，锁定动作

t = 0.10   敌人攻击命中
           └─ ReceiveDamage 第 ③ 条
                ├─ 正面 ✅  Poise > 0 ✅  在 PerfectGuardWindow 内 ✅
                ├─ bPerfectBlockUsed == false → 置 true → Broadcast OnPerfectBlock(HitPoint)
                └─ Return (Blocked, true, false)

           OnPerfectBlock(HitPoint) → HandlePerfectBlock()
                ├─【1】退出格挡 → 回 Locomotion
                ├─【2】SetLastGuardEndTime(-9999)      CD 清空
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
           按轻击 → BlockCounter_L1 → L2 → L3 → L4
           按重击 → BlockCounter_H1 → H2 → H3
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
| `PerfectGuardWindow` | 现有 | 完美窗口长度 |

**`BPC_Combat`：**

| 名称 | 类型 | 说明 |
| --- | --- | --- |
| `GuardCD` | float | 0.4 |
| `LastGuardEndTime` | float | -9999 |
| `CounterType` | `E_CounterType` | 替代原 `bCounterWindowOpen` |
| `CounterTypeUsed` | bool | 替代原 `bCounterUsed` |
| `TryGuard()` | **【内部函数】** | 门槛 + 原流程 |
| `SetLastGuardEndTime(Time)` | **【接口实现】** | 启动 / 清空格挡 CD |
| `HandlePerfectBlock(HitPoint)` | **【内部函数】** | 退格挡 + 清 CD + 开窗 + 顿帧 + 转发反馈 |

**`BPI_Combat`：**

| 方法名 | 输入 | 输出 | 作用 |
| --- | --- | --- | --- |
| `TryGuard` | / | bool | **【接口】** 格挡入口：状态判断 + CD 判断 + 原流程 |
| `SetLastGuardEndTime` | float（Time） | / | **【接口】** 启动或清空格挡 CD（传 -9999 即清空） |

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

**`BPI_CombatFeedBack`（已有，仅参数语义变更）：**

| 方法名 | 输入 | 输出 | 变化 |
| --- | --- | --- | --- |
| `PlayEnemySlowMo` | float（Scale），float（Duration） | / | 原 `PlayPerfectDodgeSlowMo` 改名 + 加参数。**完美闪避传 (0.1, 0.5)，完美格挡传 (0.15, 0.12)** |
| `PlayHitStop` | Actor，float | / | 现有。**只对传入的 Actor 生效 —— 防守方传 `Self`，攻击方也传 `Self`** |

**`DT_Attacks`：** 新增 `BlockCounter_L1..L4` / `BlockCounter_H1..H3`（见（13）节的行表）。

**`E_CounterType`：** 新建枚举，`None` / `Block` / `Dodge`。

**`E_CloseUpPhase`：** 新建枚举，`None` / `In` / `Hold` / `Out`。

**⭐ `E_CameraShakeType` 里已经有 `PerfectBlock` 与 `Block`，不需要新增。**

#### （9）验证

```
【判定】
□ 正面格挡 + 完美窗口内 → 退回格挡、清 CD、开 Block 窗口
□ 三连击都在完美窗口内 → 只触发一次完美（bPerfectBlockUsed）
□ 背面被打 → 不触发完美格挡
□ Poise == 0 → 不触发完美格挡

【格挡 CD】
□ 主动松开格挡后 0.4s 内按格挡 → TryGuard 返回 false
□ 0.4s 后按格挡 → 正常进入
□ 完美格挡后立刻按格挡 → 正常进入（CD 已清）
□ 已在格挡中再按格挡 → TryGuard 返回 false

【反击窗口】
□ 完美格挡后轻击 → BlockCounter_L1 → L2 → L3 → L4
□ 完美格挡后重击 → BlockCounter_H1 → H2 → H3
□ 窗口过期后轻击 → Attack1
□ 完美闪避在 Block 窗口期间触发 → CounterType 变 Dodge（闪避优先）
□ Block 守在 Dodge 窗口期间触发 → CounterType 保持 Dodge，不降级
□ 挨打 / 死亡 / 重新闪避 / 跳跃 → 窗口关闭

【接口数】
□ BPI_Combat 7 → 9（TryGuard / SetLastGuardEndTime）
□ BPI_CameraDirector 1 → 2（PlayPerfectBlockCloseUp）
□ 总数 95 → 98
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

④ LastGuardEndTime 只能通过 SetLastGuardEndTime 修改
   BPC_Attribute 不该反向依赖 Player 特有的 BPC_Combat

⑤ 顿帧不要用 SetGlobalTimeDilation，双方各调 PlayHitStop(Self)
   GlobalTimeDilation 会拖慢 Set Timer 的游戏时间 → 反击窗口被拉长
   且会一并冻住远处敌人的动画、粒子、音效

⑥ PlayPerfectBlockCloseUp 必须是【接口】不是【内部函数】
   BPC_CombatFeedBack 跨组件调用它，按分层约定必须走 BPI_CameraDirector
```

#### （11）反馈：震屏 + FOV 特写

> **范围**：本节只写**震屏**与**FOV 特写**两项。火花 / 音效 / 后处理爆闪 / 敌人被弹开 / 手柄震动暂不设计 —— 等这两项的手感确认之后再补，否则一次改太多分不清是哪个起的作用。

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

##### 11.3 触发链路

```
BPC_CombatFeedBack · PlayHitFeedback 【接口实现】
  └─ Branch: bPerfect == true
       ├─ BPI_CameraDirector.Shake(PerfectBlock, ImpactLocation, 2.0)      【接口】
       └─ BPI_CameraDirector.PlayPerfectBlockCloseUp()                     【接口】

BPC_Combat · HandlePerfectBlock(HitPoint) 【内部函数】
  └─ BPI_CombatFeedBack.PlayHitFeedback(Blocked, HitPoint, true, None, 0)  【接口】
```

**⭐ `ImpactLocation` 传 `HitPoint` 而不是角色位置 —— 震屏会朝接触点方向偏，有"来向感"。**

##### 11.4 验证

```
【震屏】
□ 完美格挡第 0 帧就有明显位移（BlendInTime = 0 生效）
□ 0.20s 内衰减到 0，不是突然停
□ 有旋转感，不只是平移
□ Shake_Multiplier 保持 1.0，强度只靠 Strength 参数调
□ 强度 2.0 不晕，3.5 是上限

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

##### 11.6 暂不设计（等这两项确认手感后再补）

```
□ 火花 / 冲击波 Niagara（沿格挡面法线，生成在 HitPoint）
□ 三层音效（金属撞击 + Sub 低频 + 混响尾，音高随机 ±5%）
□ 后处理爆闪（Bloom / Exposure / ChromaticAberration）
□ 敌人被弹开（Parried 蒙太奇 + 位移 + 0.3s 僵直，由攻击方执行）
□ 手柄震动（左右马达时长不同）
□ BPCS_PerfectDodge 参数调整（已拆分出来，暂沿用默认值）
```

---

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

## 9，运行导图

> 组件之间的实际流转。图上只画调用关系，判断规则看 [8，功能实现](#8功能实现)。

### 1）玩家运行导图

```mermaid
flowchart TD
    Input([外部输入]) -->|"BPI_Player<br/>DoLight / DoHeavy / DoDodge / DoJump"| Buffer["BPC_BufferInput<br/>缓存输入 + 过期时间"]
    Scheduler[["调度者"]] --> Tick["BP_Player Tick"]
    Buffer -->|"Consume（一帧只吃一个）"| Tick

    Tick -->|"TryEnterState（主动）"| ActionState["BPC_ActionState<br/>状态仲裁 / 取消窗口"]
    Tick -->|"DoAttack → DoLight / DoHeavy"| Combat["BPC_Combat<br/>连招链 / 蒙太奇 / 受击"]

    Combat -->|PlayAnimMontage| ABP["ABP_Player<br/>角色动画蓝图"]
    ABP -->|"ANS_AttackWindow → OnAttackWindow"| Combat
    ABP -->|"ANS_Move → StartMotion / StopMotion"| Motor["BPC_Motor<br/>代码位移"]

    Combat -->|SetMotionProfile| Motor
    Motor -->|推进位移| Pawn([角色 Pawn])

    Combat -->|ReceiveDamage| EnemyAttr["敌人 BPC_Attribute<br/>算伤害 / 削韧"]
    SelfAttr["自身 BPC_Attribute"] -->|"OnDamageApplied"| Combat
    Combat -->|"EnterHit → TryEnterState"| ActionState

    Combat -->|PlayHitFeedback| FB["BPC_CombatFeedBack<br/>顿帧 / 音效"]
    FB -->|Shake| Cam["BPC_CameraDirector"]

    LockOn["BPC_LockOn<br/>锁定索敌"] -->|修改朝向 / 部分动作| Combat
    LockOn -->|转向| Pawn
```

**与手绘原图相比，这一版修正了 5 处：**

```
① AbP_Player → ABP_Player（拼写）
② 删掉「BPC_Attribute → 敌人」这条线
   伤害不是从 Attribute 流向敌人，而是 Combat 调「目标」的 ReceiveDamage
③ 标签 GetAttack / TakeDamage → ReceiveDamage
   TakeDamage 是 Attribute 内部自己调的，外部只调 ReceiveDamage
④ 补上 BPC_Motor：ANS_Move 直连 Motor.StartMotion / StopMotion
   Combat 只负责 SetMotionProfile 下发参数（位移职责已移交）
⑤ 补上 BPC_CombatFeedBack + BPC_CameraDirector，以及受击回路
   Attribute.OnDamageApplied → Combat.EnterHit
```

---

### 2）敌人运行导图

```mermaid
flowchart TD
    Sight([视觉感知]) -->|"AI_HandleSight<br/>只维护感知池"| AI["BPC_AI<br/>感知 / 目标 / 距离<br/>+ 状态仲裁"]
    SelfAttr["自身 BPC_Attribute<br/>受击判定"] -->|"AI_TryEnterState<br/>HitLight / HitHeavy / KnockDown / Dead"| AI

    AI -->|"Tick：UpdatePerception<br/>RefreshTarget / UpdateDistances"| BB[("黑板<br/>TargetActor / DisToTarget<br/>AIState / HitPending / bControlled")]

    BB -.->|只读| BTD["BTD 装饰器<br/>按 AIState 选分支"]
    AIC["AIC_EnemyBase<br/>AIController"] -->|RunBehaviorTree| BT["BT_EnemyBase"]

    BTS["BTS_UpdateAIState<br/>每帧决策<br/>前提：非受控、非 Attack"] -->|"AI_SetState<br/>Idle / Chase / Attack"| AI
    BTS -->|"AddToken 成功才进 Attack"| GS["BP_GameState<br/>攻击令牌"]
    BT --> BTS

    BTD -->|"AIState == Attack"| T1["BTT_EnemyAttack<br/>只执行，不改状态"]
    BTD -->|"AIState == Chase"| T2["BTTask_MoveTo<br/>引擎内置，Key = TargetActor"]
    BTD -->|"受控状态"| T3["BT_ControlledState<br/>PlayHitMontage"]

    T1 -->|AttackByType| Trace["BPC_AttackTrace<br/>攻击判定 / 蒙太奇生命周期"]
    T3 -->|PlayHitMontage| Trace

    Trace -->|"蒙太奇结束<br/>先 RemoveToken<br/>再 AI_ReturnToInitialState"| AI
    Trace -->|"查受击蒙太奇表"| DT[("DT_Reactions<br/>ST_AttackData")]
    Trace -->|AttackByType / PlayHitMontage| ABP["敌人动画蓝图"]
    Trace -->|SetMotionProfile| Motor["BPC_Motor<br/>招式代码位移"]
    ABP -->|"ANS_AttackWindow → OnAttackWindow"| Trace
    ABP -->|"ANS_Move → StartMotion / StopMotion"| Motor

    Trace -->|命中| Target["目标 BPC_Attribute<br/>ReceiveDamage"]
    Trace -->|PlayHitFeedback| FB["BPC_CombatFeedBack<br/>顿帧 / 音效"]
```

**四处最容易画错的连线：**

```
① 行为树不调 BPC_Motor
   BT 里的 MoveTo 走的是 CharacterMovement（寻路移动），不经过 BPC_Motor。
   BPC_Motor 只管「招式代码位移」，调用方只有两个：
     · BPC_AttackTrace（SetMotionProfile）
     · 动画通知 ANS_Move（StartMotion / StopMotion）

② 状态写入只有一个方向：BTS → BPC_AI
   BPC_AI 不决策、不查询上层。
   BTS 用 AI_SetState 请求普通转换，BPC_Attribute 用 AI_TryEnterState 抢占受击/死亡，
   BPC_AttackTrace 用 AI_ReturnToInitialState 回流 —— 三者都是「上层往下写」。

③ BTT / BTD 只读黑板，不改任何值
   改值只有 BTS（决策数据）和 BPC_AI（自己的数据 + AIState）。

④ 受击方向和受击等级是一起走的
   AI_TryEnterState 抢到受控状态后，ApplyState 同步 HitDirection / HitPending，
   Task 读黑板再传给 PlayHitMontage，中间任何一环都不要自己重新算方向。
```

**敌人侧和玩家侧的结构差别：**

```
玩家    输入 → BufferInput → Tick → Combat → 蒙太奇 / Motor / 伤害
        状态归 BPC_ActionState（组件），受击走 Combat.EnterHit

敌人    感知 → BPC_AI（维护数据）→ 黑板 → BTS（决策）→ BTT（执行）
        没有 BPC_ActionState，状态归 E_AIState，由 BPC_AI 仲裁并写进黑板
        受击走 Attribute.OnDamageApplied → 内部受击处理 → AI_TryEnterState，不做 EnterHit

两边共用：BPI_CharacterBase（取组件 / IsCharacterDead / IsHostile）、
         BPC_Attribute（伤害 / GetTeam）、BPC_Motor（招式位移）、
         BPC_CombatFeedBack（反馈）
```

**敌人行为树全部由引擎内置节点 + 三个自定义资产搭成，没有自定义 BTT_MoveToActor / BTD：**

```
BT_EnemyBase
├─ BTS_UpdateAIState            自定义服务（Enemy/AI/Service）
├─ Selector
│   ├─ [BTDecorator_Blackboard] 受控状态 → BTTask_RunBehavior(BT_ControlledState)
│   ├─ [BTDecorator_Blackboard] AIState == Attack → BTT_EnemyAttack
│   ├─ [BTDecorator_Blackboard] AIState == Chase  → BTTask_MoveTo（引擎内置）
│   └─ BTTask_Wait（引擎内置，待机）
```

**⭐ `Chase` 分支直接用引擎的 `Move To`，目标填黑板键 `TargetActor`：**

```
Move To 的 Blackboard Key 选 TargetActor
→ 目标在动，导航系统自动重算路径，敌人持续跟随
→ 不需要每帧下发指令，也不需要一个自定义任务去包一层
```

**⚠️ `Move To` 只在序列/选择器里持续运行时才会持续跟踪。如果它被上层 abort 掉（比如状态切到 Attack），跟随会停止 —— 这是期望行为。**

---

## 10，校对差异清单

以下是本次扫描发现、与旧版 README 不一致的地方。已按「实际资产」更新到上文，这里留档备查。

### 已修正的文档错误

| #   | 位置                            | 旧版写法                             | 实际情况                                                                                                                         |
| --- | ----------------------------- | -------------------------------- | ---------------------------------------------------------------------------------------------------------------------------- |
| 1   | BPI_Attribute                 | 只有 8 个函数                         | 实际 12 个，补 `EnterGuard` / `ExitGuard` / `NotifyDodgeStart` / `RestorePoise`                                                   |
| 2   | BPI_Attribute.ReceiveDamage   | 描述为「是否完美格挡，以及是否破韧」               | 两个 bool 是 `bPerfectBlock` 和 `bPerfectDodge`，**没有破韧输出**                                                                       |
| 3   | BPI_ActionState               | 5 个函数                            | 实际 7 个，补 `SetState` / `SetCancelWindow`                                                                                      |
| 4   | BPI_CharacterBase             | 4 个函数                            | 实际 8 个，补 `GetMeshComponent` / `GetHitBoxComponent` / `GetWeapon` / `GetImpulse`                                              |
| 5   | BPI_Motor                     | 4 个函数                            | 实际 8 个，补 `IsMoving` / `IsBeingKnockedBack` / `SetGravity` / `ResetGravity`                                                   |
| 6   | BPI_Player                    | 14 个函数                           | **实际 9 个**：`GetMesh` / `GetHitBox` / `GetWeapon` / `GetAttributeComponent` / `GetCharacterMovement` 已上收到 `BPI_CharacterBase` |
| 7   | BPI_EnemyBase                 | 5 个函数                            | **实际 2 个**：`GetMesh` / `GetHitBox` / `GetEnemyAttributeComponent` 已上收到 `BPI_CharacterBase`                                   |
| 8   | BPI_AI                        | 7 个函数                            | 实际 9 个，补 `AI_SetAIState` / `HandleDamageApplied`（后续受击逻辑又扩到 12 个，见 #18）                                                          |
| 9   | BPI_LockOn                    | 5 个函数                            | 实际 6 个，补 `GetTarget`                                                                                                         |
| 10  | BPI_Combat                    | 7 个函数                            | **实际 7 个**：**没有** `ClearAttackData`；`MoveStart` / `MoveEnd` 已删除（位移改由 `ANS_Move` 直连 Motor）；新增 `EnterHit`                      |
| 11  | E_AIState                     | 4 个值                             | 实际 7 个，补 `HitLight` / `HitHeavy` / `KnockDown`                                                                               |
| 12  | ST_AttackData                 | 写作 `PoiseDamageRate`             | 资产里是 `PoiseDdamageRate`（多一个 d）                                                                                               |
| 13  | 缺失整节                          | 无                                | 补 `BPI_GameState` / `E_EnemyAttackType`                                                                                      |
| 14  | BPI_HIt                       | 1 个函数（EnterHit）                  | **已删除**，`EnterHit` 合并进 `BPI_Combat`，签名改为 `(E_ActionState HitType, E_HitDirection HitLoc)`                                    |
| 15  | BPI_Combat.MoveStart/MoveEnd  | 2 个函数                            | **已删除**，`ANS_Move` 改为直连 `BPI_Motor.StartMotion` / `StopMotion`                                                               |
| 16  | AN_MoveEnd                    | 独立通知                             | **已删除**。`ANS_Move` 的 NotifyEnd 已负责收尾，该通知与它重复                                                                                 |
| 17  | BPI_Attribute / BPC_Attribute | Code/ActorComponent/DamageSystem | 已迁到 `Code/ActorComponent/Attribute`                                                                                          |
| 18  | BPI_AI / BPI_AttackTrace      | BPI_AI 9 个、BPI_AttackTrace 2 个；`AI_SetAIState` 无返回值；`HandleDamageApplied` 参数待确认 | BPI_AI 12 个（补 `AI_ResetAIState` / `AI_GetHitStamp` / `AI_ConsumeHit`），`AI_SetAIState` 改为返回 bool；BPI_AttackTrace 3 个（补 `PlayHitMontage`）；`HandleDamageApplied` 参数为 `(E_HitOutCome, E_HitDirection, bool)`；接口总数 82 → 86 |
| 19  | 完美闪避 / 闪避四向            | 接口总览停在 86，无受击状态机之外的功能章节 | 总数 86 → 90：BPI_Attribute 12→13（`SetInvincible`）、BPI_CombatFeedBack 3→4（`PlayPerfectDodgeSlowMo`）、BPI_ActionState 7→8（`ClearDodgeCD`）、BPI_Player 9→10（`GetCameraComponent`）；新增 `8，功能实现` 与 `9，运行导图` 两个一级模块 |
| 20  | BPI_Player 相机相关            | 只有 `GetDirectorComponent`          | 已改名为 `GetCameraDirectorComponent`；并新增 `GetCameraComponent`（返回 UE 的 `CameraComponent`，与 `BPC_CameraDirector` 不是一回事，两者可同时存在） |
| 21  | 完美闪避的收尾方式              | 文档写的是「判定成功即立即取消闪避 + 全局时间膨胀」 | 改为「动画继续播，靠时间 / 距离先到收尾 + 只慢敌人」：新增 `EndPerfectDodge`（尾巴判断收进 Attribute）、`SetMotionScale`（位移衰减），接口总数 90 → 92；`bPerfectDodgeUsed` 成为防重复的唯一保证 |
| 22  | 闪避的默认方向                  | 无输入一律前闪                        | 无输入时按索敌状态决定：`E_LockOnState` 为 `Soft` / `Hard` → 默认右闪，`None` → 默认前闪；有输入时永远以输入为准。不使用距离阈值 |
| 23  | 完美闪避的残影                  | 文档未涉及                            | 新增 `M_Afterimage` / `BP_Afterimage` / `BPI_Afterimage` + `BPI_Player.StartAfterimage` / `StopAfterimage`，接口总数 92 → 94；`ActiveGhosts` 必须清理，否则只有首次完美闪避能出残影 |
| 24  | 完美闪避反击                    | 完美闪避后没有限时反击奖励              | 新增反击窗口：窗口内轻 / 重击选择 `Counter_L1` / `Counter_H1` 起始行，后续连招继续走 `ST_AttackData.Next`；窗口过期回归普通攻击，接口不新增 |
| 25  | 武器刀光                        | 攻击蒙太奇没有统一的刀光开关              | 新增 `M_WeaponTrail` / `NS_WeaponTrail` / `ANS_WeaponTrail`；通过 `BPI_WeaponBase.SetTrailActive(bool)` 控制 Niagara Ribbon，接口总数 94 → 95 |
| 26  | 攻击令牌                        | 文档 3.6 要求「同屏 1~2 个敌人同时进攻」，工程内无实现 | `BPI_GameState` 接入 `AddToken` / `RemoveToken` / `HasToken`；`Tokens` 用 `Map<Actor, Float>` 记录持有时刻；`BTT_EnemyAttack` 申请、`BPC_AttackTrace` 归还、`BP_GameState` 三层兜底；`BPI_CharacterBase` 新增 `IsCharacterDead`，接口总数 95 → 96 |
| 27  | 敌我阵营 + AI 分层重构             | 无阵营概念，敌人会互相误伤；AI 每帧 `ComputeNextState` 直接覆盖状态，攻击中被切走导致「一边跑一边砍」 | 新增 `E_Team` 与 `BPI_Attribute.GetTeam`、`BPI_CharacterBase.IsHostile`；`BPI_AI` 12 → 9，删除 `AI_AddPerceivedActor` / `AI_RemovePerceivedActor` / `AI_RefreshTarget` / `HandleDamageApplied`（转内部方法）、`AI_ResetAIState`（无引用），`AI_SetAIState` 改名 `AI_SetState`，新增 `AI_TryEnterState` / `AI_ReturnToInitialState`；决策权移到已接入的 `BTS_UpdateAIState`，`BPC_AI` 退化为仲裁器；Chase 使用行为树内置 `BTTask_MoveTo`，目标键为 `TargetActor`；接口总数 96 → 95 |
| 28  | 完美格挡                        | 完美格挡只停留在 `ReceiveDamage` 的返回值，没有任何后续奖励；格挡没有冷却，可以无限重进 | 新增 `8，功能实现 · 3）完美格挡` 整节；`E_CounterType` 取代 `bCounterWindowOpen`（`None` / `Block` / `Dodge`，Dodge 优先级更高），`CounterTypeUsed` 取代 `bCounterUsed`；`BPC_Attribute` 新增 `bPerfectBlockUsed` 与 `OnPerfectBlock` 分发器；`BPC_Combat` 新增 `GuardCD` / `LastGuardEndTime` / `TryGuard` / `SetLastGuardEndTime` / `HandlePerfectBlock`，`OpenCounterWindow` 改收 `E_CounterType`；`DT_Attacks` 新增 `BlockCounter_L1..L4` / `BlockCounter_H1..H3`；接口总数 95 → 98（`BPI_Combat` 7 → 9、`BPI_CameraDirector` 1 → 2）；**普通格挡受击（`Blocked` 非完美）的表现与状态处理尚未定稿，本节不含** |
| 29  | 完美格挡的反馈                  | 完美格挡只有震屏，且不够大；`ReceiveDamage` 拿不到击中点；`PlayHitStop` 只对传入的攻击者生效，做不到"双方都停"；完美闪避与完美格挡共用一个抖动资产 | `ReceiveDamage` 新增 `HitPoint` 入参（第三个仍是攻击者位置 —— 判定用位置、表现用击中点，不能互相替代）；`OnPerfectBlock` 改为带 `Vector3`；`PlayPerfectDodgeSlowMo` 改名 `PlayEnemySlowMo(Scale, Duration)`（闪避 0.1/0.5，格挡 0.15/0.12）；顿帧改为双方各调 `PlayHitStop(Self, 0.04)`，明确不用 `GlobalTimeDilation`（会拖慢 `Set Timer` 导致反击窗口变长）；新增 `BPI_CameraDirector.PlayPerfectBlockCloseUp`（FOV 特写 `BaseFOV−16`，`TickComponent` 三阶段插值，**用 `Get Game Time in Seconds` 而非 `DeltaTime`** 规避顿帧冻结）；新增 `E_CloseUpPhase`（`None` 兼作空闲态，不再需要 `bCloseUpActive`）；`E_CameraShakeType` 补 `PerfectDodge`（共 6 个，文档此前漏写）；`BPCS_PerfectBlock` 参数改为冲击型（`BlendInTime = 0`），`BPCS_PerfectDodge` 已拆分但参数暂不调；接口总数仍为 98 |

### 需要在编辑器里处理的遗留问题

```
① BPI_Combat 里没有 ClearAttackData
   已确认：计划后续补，暂不处理。补之前切招式不会清旧数据

② BPI_Interaction 已删除（原为空壳）

③ GetAttibuteComponent 的拼写问题已随迁移消失
   玩家侧那个少一个 r 的 GetAttibuteComponent 已删除，
   统一使用基类的 GetAttributeComponent（拼写正确）

④ ST_AttackData.PoiseDdamageRate 拼写多一个 d
   同上，改名要连带所有读取点

⑤ 原 BPI_AI.HandleDamageApplied 已转为 BPC_AI 内部方法
   受击流程改为 Attribute.OnDamageApplied → 内部处理 → AI_TryEnterState
   不再作为接口暴露，外部不应再有绑定残留

⑥ Get* 归属已统一到 BPI_CharacterBase（已完成）
   基类持有：GetAttributeComponent、GetCombatFeedbackComponent、GetMotorComponent、
             GetCharacterMovement、GetMeshComponent、GetHitBoxComponent、
             GetWeapon、GetImpulse

   BPI_Player 只剩 9 个玩家专属函数
   BPI_EnemyBase 只剩 2 个敌人专属函数（GetAttackTraceComponent、GetAIComponent）

   ⚠ 待确认：基类的 GetHitBoxComponent 是否计划改名为 GetWeaponHitBox
     当前编辑器里仍显示 GetHitBoxComponent，本文档按实际名字记录

⑦ 二进制扫描的坑（给以后自己看）
   UE 保存蓝图后，name table 里仍保留已删除函数的 FName。
   直接 grep .uasset 会搜到 GetMesh / GetHitBox 这类历史名字，误判为"函数还在"。
   确认接口函数一律以编辑器「我的蓝图 → 函数」面板为准

⑧ BPI_Combat.EnterHit 的参数名和类型不一致
   实际签名：EnterHit(HitType : E_ActionState, HitLoc : E_HitDirection)
   第二个参数类型已经是「方向」了，但 pin 名还叫 HitLoc（位置）
   建议改名为 HitDirection，否则读代码的人会以为要传坐标

⑨ AN_Cancel 尚未接入 SetCancelWindow
   取消窗口现在由 Combat 按 ST_AttackData.CancelStart 数据驱动
   AN_Cancel 只引用了 ActionState、没调 SetCancelWindow
   要么删掉这个通知，要么改成让它调 SetCancelWindow，别两边并存

⑩ 静态弧面刀光已废弃，BP_Slash / BPI_Slash 已删除
   刀光改用 NS_WeaponTrail 的 Ribbon Renderer
   静态弧面需要为每个攻击方向单独对齐 socket 坐标系，已确认不划算
   ⚠ M_SwordSlash 材质已无引用，可一并删除

⑪ BPC_AttackTrace 的 TraceStart / TraceEnd / TraceColor 是伤害判定
   不是调试绘制，与玩家侧判定同源
   → 判定框可视化调试工具仍然缺失，这是调招式数据时的主要盲区

⑫ ActorComponent 蓝图里不能用 Timeline 节点
   Blueprint 的 Timeline 依赖 UTimelineComponent 作为成员，
   而 Add Component(Timeline) 只在 Actor 蓝图里提供
   → BPC_Combat / BPC_CameraDirector / BPC_Attribute / BPC_Motor
     等组件里右键搜不到 Timeline
   → 组件内需要插值的一律用 TickComponent 手动推进
     （Set Timer by Event 在组件里可用，顿帧 / 慢动作的恢复不受影响）

   ⚠ 组件内做主插值时，时间源要用 Get Game Time in Seconds，
     不能用 Tick 的 DeltaTime 累加 —— 顿帧会把该 Actor 的
     DeltaTime 压到 0，插值会被冻住
```

---

[↑ 回到目录](#目录)
