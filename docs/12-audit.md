# 校对差异清单

> 本文件是模块文档。项目总导航、规范与历史见 [README.md](../README.md)。

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
| 9   | BPI_LockOn                    | 5 个函数                            | 实际 6 个，补 `GetTarget`（后 `GetTarget` 并入 `GetFocusTarget`，降回 5 个，见 #30）                                                        |
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
| 30  | BPI_LockOn.GetTarget          | 文档与实际都列有该函数，`GetFocusTarget` 与 `GetTarget` 并存 | 实际已删除，内容并入 `GetFocusTarget`（锁定中返回锁定对象，未锁定时返回候选）；`BPI_LockOn` 6 → 5，接口总数 98 → 97 |
| 31  | BPI_CombatFeedBack            | 4 个函数；`PlayEnemySlowMo` 内部播完美闪避音效 | 实际 6 个：新增 `PlayPerfectDodgeStartSound(Duration)` / `PlayPerfectBlockSound`；**音效已从 `PlayEnemySlowMo` 移出**，慢动作接口只调时间膨胀；结束音 `PlayPerfectDodgeEndSound` 为【内部函数】由开始音的计时器触发；接口总数 97 → 99 |
| 32  | DT_Attacks 的 BlockCounter_*  | 文档写轻击 4 段 + 重击 3 段（对齐闪避反击） | 实际是轻击 `BlockCounter_L1~L2` + 重击 `BlockCounter_H1~H2`，共 4 行；比闪避反击（轻 4 + 重 3）短，是有意设计。`Montage_BlockCounter` 已建，格挡反击链路已打通 |
| 33  | BPC_Attribute.bPoiseBroken    | 作为成员变量存储破韧状态 | **已删除**：变量完全没被读取（韧性扣除与破韧判断都在 `TakeDamage` 内部），改用内部变量；`ReceiveDamage` 输出从 3 个变 4 个（新增 `IsBroken`），直通 `TakeDamage` 的返回 |
| 34  | BPC_ActionState.CanTransitionTo | 转场只查转场矩阵 | 新增 `bCanCancel` 判断：攻击态 + 取消窗口内 → 允许转出到 Locomotion。**无后续连招时攻击后摇可被输入取消**，是 `CanTransitionTo` 唯一改动，见 8-8 |

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

⑬ 死亡流程未设计（玩家 + 敌人）
   现状：
     玩家死亡 → 仅取消交互，无死亡动画收尾、无重开/复活流程
     敌人死亡 → 仅进入 Dead 终态，无尸体处理、无清理流程
   Dead 是受控终态枚举，但「终态之后」的流程完全没有
   → 不是 bug，是缺口。做死亡流程时统一设计：
     玩家：死亡表现 → UI → 重开
     敌人：死亡表现 → 令牌归还（三层兜底里的死亡路径确认）→ 尸体/销毁
```

---

[↑ 回到 README](../README.md#目录)
