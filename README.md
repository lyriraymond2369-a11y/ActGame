# ActGame

动作战斗游戏 · UE5 蓝图项目

README 负责项目入口、历史、规范和接口总览；功能细节按模块收录于 docs/。

> **校对说明**：接口函数清单以蓝图编辑器「我的蓝图 → 函数」面板为准。UE 的 name table 会保留已删除函数的 FName，直接扫描 .uasset 会产生误报。

## 历史

| 日期         | 修改内容                 | 具体内容                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                    | 修订人 |
| ---------- | -------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | --- |
| 2026.10.3  | 初稿                   | 系统概括                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                    | 作者  |
| 2026.10.4  | 切换引擎                 | 转为 UE                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                   | 作者  |
| 2026.10.4  | 角色控件                 | 角色控件关系图                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                 | 作者  |
| 2026.10.11 | 角色锁定                 | 角色锁定系统                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                  | 作者  |
| 2026.10.12 | 设置锁定组件               | 更新组件关系图                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                 | 作者  |
| 2026.10.24 | 仓库初始化                | UE 工程首次提交                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                               | 作者  |
| 2026.10.31 | 项目资产入库               | `Config` / `Content Code` / `Player` / `Enemy` 自有资产；补充引擎角色模板资源（骨骼网格 / 动画 / 材质）                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                          | 作者  |
| 2026.10.31 | 分层重构                 | Attribute / ActionState / Combat 三层职责重划；补 `ReceiveDamage` 受击判定与 `ClearPoseBroken`；ActionState 去掉 Motor 依赖                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                               | 作者  |
| 2026.10.31 | 震屏链路                 | `CombatFeedBack` 经 `BPI_CameraDirector.Shake` 接回震屏；`DT_Attacks` 攻击数据更新                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                  | 作者  |
| 2026.11.01 | 位移与受击                | 位移职责移交 Motor；接入玩家受击逻辑                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                   | 作者  |
| 2026.11.01 | 目录重构                 | Attribute 迁至 `ActorComponent/Attribute`；`BPI_HIt` 并入 `BPI_Combat`                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                       | 作者  |
| 2026.11.02 | 运行导图                 | 新增玩家 / 敌人 Mermaid 运行导图；README 增加三级目录与锚点校验                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                               | 作者  |
| 2026.11.03 | 敌人受击                 | 受击状态机 + 受击表现链路                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                          | 作者  |
| 2026.11.05 | 完美闪避                 | 无敌帧 / 完美窗口 / 慢动作奖励；README 重构为「功能实现 + 运行导图」                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                              | 作者  |
| 2026.11.05 | 闪避收尾                 | 改为延时收尾 + 只慢敌人；闪避默认方向按索敌状态                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                               | 作者  |
| 2026.11.06 | 闪避表现                 | MetaSound 合成起始音；PoseableMesh 姿态残影                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                       | 作者  |
| 2026.11.06 | 闪避反击                 | 完美闪避反击窗口与分离动作冲量                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                         | 作者  |
| 2026.11.07 | 刀光                   | 改用 Niagara 条带拖尾，接入动画通知                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                  | 作者  |
| 2026.11.08 | 攻击令牌                 | 限制同屏进攻人数，申请 / 归还 / 兜底三层                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                 | 作者  |
| 2026.11.08 | AI 重构                | 敌人 AI 状态流重构，接入阵营系统                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                      | 作者  |
| 2026.11.09 | 枚举归位                 | `E_Team` 迁至 CharacterBase 枚举                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                            | 作者  |
| 2026.11.10 | 完美格挡                 | 完美格挡判定、格挡 CD、`Block` 反击窗口                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                               | 作者  |
| 2026.11.13 | 格挡反馈增强               | `ReceiveDamage` 加 `HitPoint`；顿帧改双方各停；`BPCS_Perfect` 拆分重命名为 `BPCS_PerfectBlock` 并新建 `BPCS_PerfectDodge`；`BPI_CameraDirector` 新增 FOV 特写接口，并已接入 `PlayHitFeedback` 的 `bPerfect` 分支（震屏 + 音效 + FOV 三项反馈全部打通）                                                                                                                                                                                                                                                                                                                                                                                                                                                                                  | 作者  |
| 2026.11.13 | 完美格挡与反击              | 补充完美格挡实施进度表与（12）完美格挡反击小节；`BPI_CombatFeedBack` 4 → 6（新增 `PlayPerfectDodgeStartSound` / `PlayPerfectBlockSound`），结束音转为【内部函数】由开始音计时；`BlockCounter_*` 实际只有 `H1`，轻击四段与 `H2/H3` 待补                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                            | 作者  |
| 2026.11.14 | 完美格挡反击数据表            | `DT_Attacks` 补齐 `BlockCounter_L1~L2 / H1~H2` 四行，`Montage_BlockCounter` 蒙太奇已建，格挡反击轻 2 + 重 2 = 4 行，与闪避反击轻 4 + 重 3 有意区分                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                    | 作者  |
| 2026.11.14 | 攻击后摇取消与破韧精简          | `CanTransitionTo` 加 `bCanCancel` 判断，无后续连招时攻击后摇可被输入取消；删除 `bPoiseBroken` 成员变量，`ReceiveDamage` 直通 `TakeDamage` 的破韧返回并作为 `IsBroken` 输出（三个输出变四个）                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                             | 作者  |
| 2026.11.14 | 普通格挡受击设计             | 新增 8-3（13）普通格挡受击：弱震屏 0.8 + 沉闷格挡音 + 双方各 0.02s 顿帧，无慢速无 FOV，保持格挡姿态；含节流（音高 ±5% / 震屏递减）与破韧 Guard Break 第二步方案                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                 | 作者  |
| 2026.11.14 | 普通格挡受击实现             | `OnDamageApplied(Blocked)` → `HandleGuardHit`：查 `DT_Reaction` 的 `BlockHit` 行播蒙太奇，`bReliefOriginal=true` 播完保持 Guard；新增 `DT_Reaction`（复用 `ST_AttackData`，仅读 Montage / SectionStart / LaunchSelf / MotionSelf / MoveSpeed / MoveFriction）；破韧直接返回 `Hit` 不经本链路；上半身分离方案（Layered Blend Per Bone + UpperBody Slot，Slot 名即开关，默认 DefaultSlot 全身）                                                                                                                                                                                                                                                                                                                                                  | 作者  |
| 2026.11.17 | 上半身分离实现              | `ABP_Player` 接入 Layered Blend per Bone + UpperBody Slot（**仅上半身，下半身层未实现**）：`Montage_BlockHit` 改走 `DefaultGroup.UpperBody`，上半身受击、下半身保持 BlockState，滑步修复；三条硬约束（混合深度必须 0、`DefaultSlot` 必须在 LayeredBlend 之后、`MainPose` 缓存只包状态机输出）记入 8-3（13.5）；插槽管理器注册 `UpperBody`                                                                                                                                                                                                                                                                                                                                                                                                                             | 作者  |
| 2026.11.17 | 结构文档补全               | 新增 3-0「敌人 vs 玩家双轨制」：敌人不挂 `BPC_Combat`，BT/BTS/BTT 决策、`BPC_AttackTrace` 只做 montage 播放 + BB 写入；规范 1 新增⑥「战斗反馈由攻击方发起、镜头一律玩家」（单玩家视角的有意简化，双人/内讧需改路由）；13.4 震屏链路写明攻击方调 `PlayHitFeedback` → 无条件取玩家 CameraDirector；遗留问题⑬标注玩家/敌人死亡流程未设计；反应表资产名统一记录为 `DT_Reactions`                                                                                                                                                                                                                                                                                                                                                                                                                                  | 作者  |
| 2026.11.17 | 文档拆分                 | README 瘦身为「入口 / 历史 / 规范 / 接口总览」，模块内容按 12 个文件拆分到 `docs/`：01 CharacterBase、02 Player、03 EnemyBase、04 WeaponBase、05 独立接口、06 动画通知、07 敌人受击、08 完美闪避、09 完美格挡、10 其他功能、11 运行导图、12 校对清单；00 接口总览保留在 README                                                                                                                                                                                                                                                                                                                                                                                                                                                                                         | 作者  |
| 2026.11.17 | 格挡破防与完美窗口区间化         | 普通格挡受击 + 格挡破防双分支：`OnDamageApplied` 先分 `HitOutCome`，`Blocked` 走 `HandleGuardHit`，`BreakPoise` 单独路由 `HandleGuardBreak`（ExitGuard → HitHeavy → 全身 `GuardBreak` montage → 收尾回 Locomotion）；完美窗口改为区间 `PerfectGuardWindowStart/End` + `IsPerfectBlock()`（架刀瞬间不再算完美）；格挡 CD 从 `BPC_Combat` 迁入 `BPC_ActionState`（`CanGuard` / `UpdateGuardCD` / `ClearGuardCD`，与闪避 CD 对称），删除 `BPI_Combat.SetLastGuardEndTime`；接口数 99 → 101（ActionState 8→11、Combat 9→8）                                                                                                                                                                                                                                           | 作者  |
| 2026.11.17 | 输入重绑：Shift 双功能       | 闪避迁至左 Shift：点按（<0.2s）闪避、长按（≥0.2s）奔跑；删除 `IA_Run` / `IA_Dodge` 只留 `IA_Shift`；增强输入事件全部移除，改为 `BP_Player` Tick 纯轮询（`ShiftPressStartTime` 单一写者、松开当帧触发，消除点按延迟）；奔跑为 Locomotion 内速度档位（`E_MoveState.Run`）不进 `BufferInput`；闪避可取消格挡（方案 A：ExitGuard，收尾不回格挡）                                                                                                                                                                                                                                                                                                                                                                                                                                          | 作者  |
| 2026.11.17 | 玩家架势与 KnockDown 收尾   | `Posture` 与 `Poise` 平行：架势归零返回 `BreakPosture` → `HandleBreakPosture` → 玩家 `KnockDown`；`BreakPoise` 维持原韧性破防 → `HandleGuardBreak`，两者不互相替代；`TakeDamage` 改为接收最终 `PostureDamage`，只负责扣血/韧/架势并返回两个破坏结果，最终倍率由 `ReceiveDamage` 计算；新增 `GetPostureAttack`、`ReliefPosture`；KnockDown 为不可幂等的受控状态，`Start → Loop → End`，Loop 通知启动 Timer，Timer 到期跳 End，Montage Completed 调接口化 `HandleKnockDownCompleted`，内部状态守卫 + `ReliefLocomotion`；正常完成和投技/处决演出结束均可调用该接口；接口数 101 → 105（Attribute 15→17、Combat 8→10）                                                                                                                                                                                                    | 作者  |
| 2026.11.22 | 敌人投技 / 玩家处决（测试版·变量化） | 投技变量化：新增 `DT_Executions` 数据表与 `ST_GrabMoveData` 结构体（`MoveType` / `StartSectionName` / `EndSectionName` / `TargetLocationOffset` / `RandomWeight` / `bEnabled` 等），按权重随机选行播放；`PlayExecutionVictim(RowName)` 改为带行名参数、无返回值的纯播放器；目标位置按受击者自身三轴计算（X 前后 / Y 左右 / Z 上下）；非所有处决 Montage 都是三件套，`StartSectionName` 指定起始片段，`EndSectionName` 指定 Loop 段跳转段；敌人播放完 Montage 后经 `BPC_AI` 回 `Idle`；新增 `BPI_Execution` 接口（`CanBeGrabbed` / `PlayExecutionVictim` / `JumpExecutionToEnd` / `HandleExecutionCompleted`）、`BPI_CharacterBase.GetMotionWarpingComponent`、`BPI_AttackTrace.OnGrabContact` / `OnGrabDamage`（占位）/ `OnGrabLoopStarted`；接口数 105 → 113（Execution +4、CharacterBase 10→11、AttackTrace 3→6） | 作者  |
| 2026.11.22 | 击倒音效 | 新增 `MS_Knockdown_Impact`（架势归零倒地瞬间：肉体闷响 + 地面撞击双层 MetaSound）与 `MS_Grab_Impact`（投技命中帧：摔投主体 + 锐利瞬态 + 噪声爆发三层 MetaSound），随机化音高/起点；`BPI_CombatFeedBack` 新增 `PlayKnockdownSound` / `PlayGrabImpactSound`，由 `HandleBreakPosture` 与 `OnGrabDamage` 经接口触发；起身音暂缓；接口数 113 → 115（CombatFeedBack 6→8） | 作者  |
| 2026.11.23 | 玩家死亡状态 | `BPI_Attribute.IsDead` 为死亡唯一判据，`BPC_Combat` Tick 守卫式轮询（不满足不修改），`TryEnterState(Dead)` 为绝对终态；新增 `E_DeathType`（None / LightHit / HeavyHit / KnockDown / Execution），死亡蒙太奇全部放入 `DT_Reactions`（`Death_Light` / `Death_Heavy` / `Death_KnockDown` / `Death_Execution` / `Death_Default`），复用 `ST_AttackData` + `BPC_Motor` 播放通道处理位移；致死入口在受击分发最前判定 `IsDead`、写 `PendingDeathType` 后直接返回，不进普通受击/击倒流程；`HandleKnockDownCompleted` / `HandleExecutionCompleted` 加 `IsDead` 守卫，死人绝不回 `Locomotion`；接口数不变 115 | 作者  |
| 2026.11.23 | 处决伤害与击倒反馈 | 处决伤害：`BPI_Attribute.ReceiveExecutionDamage(HealthPercent)` 按 `MaxHealth × Percent` 直扣、无视防御判定，百分比存 `ST_GrabMoveData.ExecutionHealthPercent`，由敌人 `OnGrabDamage` 在打击帧调用一次（`bGrabDamageApplied` 防重），`E_HitOutCome` 末尾追加 `Execution`；击倒反馈改为**受击者 `BPC_CombatFeedBack` 驱动**：`ApplyAttack` 仅调伤害与转发反馈（`ReceiveDamage` → 目标 `GetCombatFeedbackComponent` → `PlayHitFeedback`），`PlayHitFeedback`（5 输入不变）内 `BreakPosture` 分支 → `HandleKnockdownFeedback`（`MS_Knockdown_Impact` + CameraDirector `PlayKnockdownFOV`（`E_CloseUpPhase` 体系）+ 双方 `PlayHitStop` + 局部慢速）；新增 `BPI_CombatFeedBack.PlayLocalSlowMo(OtherActor, Scale, Duration)`（编排双 Actor 慢速）与 `ApplyLocalSlowMo(Scale, Duration)`（单体执行，防递归）；`BPI_CameraDirector.PlayKnockdownFOV`；受击者 `HandleBreakPosture` 删除全部表现调用只留状态与 Montage；接口数 115 → 119（Attribute 17→18、CombatFeedBack 8→10、CameraDirector 2→3） | 作者  |

---

## 目录

- [规范](#规范)
- [接口总览](#0接口总览)
- [CharacterBase](docs/01-character-base.md)
- [Player](docs/02-player.md)
- [EnemyBase](docs/03-enemy.md)
- [WeaponBase](docs/04-weapon.md)
- [其他独立接口](docs/05-independent-interfaces.md)
- [玩家侧动画通知与职责](docs/06-animation-notifies.md)
- [敌人受击状态机](docs/07-enemy-hit.md)
- [完美闪避与无敌帧](docs/08-perfect-dodge.md)
- [完美格挡](docs/09-perfect-block.md)
- [其他功能实现](docs/10-misc-features.md)
- [运行导图](docs/11-run-maps.md)
- [校对差异清单](docs/12-audit.md)

# 注：

```
接口名与其实现的组件名相同
```

---

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
   例：LastGuardEndTime 只能通过 BPI_ActionState.UpdateGuardCD / ClearGuardCD 修改
       外部直接写变量会让 CD 逻辑分叉到两处

⑤ 跨组件链路要沿既定的中转走，不要抄近道
   例：BPC_Combat 不直接碰 BPC_CameraDirector
       走 CombatFeedBack → BPI_CameraDirector

⑥ 战斗反馈由「攻击方」发起，镜头一律是玩家的
   攻击方（玩家或敌人）调 PlayHitFeedback
   → BPC_CombatFeedBack 无条件取玩家 CameraDirector → 震屏永远作用在玩家镜头
   ⚠️ 这是「单玩家视角」的有意简化：敌人打玩家被格挡时，震屏是敌人发起、震玩家
      如果以后出现敌人打敌人 / 双人模式，反馈会路由到玩家镜头产生错乱，
      届时改成「取受击方的视角/指定观察者」
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

**⭐ 「接口数 101」只统计【接口】，其余三类都不计。**

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

⑤ 「开始 / 结束」两段式的机制，收尾一律由发起方计时，不单独开接口
   PlayEnemySlowMo(Scale, Duration)       → Timer → RestoreSlowMo()
   PlayPerfectDodgeStartSound(Duration)    → Timer → PlayPerfectDodgeEndSound()
   收尾函数做成【内部函数】，不暴露到 BPI
   → 外部只需要「发起」，不需要也拿不到「收尾」

⑥ 音效接口与时间接口分离，一个接口只做一件事
   PlayEnemySlowMo 只管时间膨胀，不播任何音效
   → 否则共用它的另一个机制（完美格挡）会误播别人的音效

⑦ 全体敌人慢速与单体慢速必须使用不同接口
   PlayEnemySlowMo 只用于完美格挡 / 完美闪避奖励，作用对象是全体敌人
   PlayLocalSlowMo(OtherActor, Scale, Duration) 只用于击倒 / 处决等局部打击感，
   负责同时安排受击者与攻击者两个 Actor 的局部慢速
   → 禁止用 PlayEnemySlowMo 替代局部时间膨胀，避免影响无关敌人
   → 单体执行拆分为 ApplyLocalSlowMo(Scale, Duration)（外部只走它），
     由 PlayLocalSlowMo 内部派发，避免 OtherActor ↔ Self 递归调用

⑧ 顿帧与局部慢速必须串行
   ApplyLocalSlowMo 若发现目标仍在 HitStop 窗口内，只记录待执行参数并立即结束当前函数
   BPC_CombatFeedBack Tick 在 GetGameTime >= HitStopEndTime 后启动待执行慢速
   → 不新增“是否正在顿帧”布尔，统一用 HitStopEndTime 判断
   → 待执行慢速必须由发起方组件自动消费并清空，不能依赖外部再次调用
   → 恢复时必须还原到慢速前保存的原始 Dilation，禁止把减速后的值当新的原始值
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

   项目实例：bPoiseBroken 已删除
   ReceiveDamage 直接透传 TakeDamage 的返回值（IsBroken 输出）
   → 韧性扣除与破韧判断都在函数内部，成员变量只写不读就是死重量

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
| BPI_CharacterBase        | Code/Interface                     | 11  | 无（纯接口，所有组件获取的统一入口） |
| BPI_Attribute            | Code/ActorComponent/Attribute      | 18  | BPC_Attribute      |
| BPI_CombatFeedBack       | Code/ActorComponent/CombatFeedBack | 10  | BPC_CombatFeedBack |
| BPI_Motor                | Code/ActorComponent/Motor          | 9   | BPC_Motor          |
| BPI_WeaponBase           | Code/Weapon                        | 3   | BP_WeaponBase      |
| BPI_GameState            | Code/GameState                     | 3   | 待接入                |
| BPI_Player               | Player                             | 12  | BP_Player          |
| BPI_ActionState          | Player/Component/ActionState       | 11  | BPC_ActionState    |
| BPI_BufferInput          | Player/Component/BufferInput       | 3   | BPC_BufferInput    |
| BPI_CameraDirector       | Player/Component/CameraDirector    | 3   | BPC_CameraDirector |
| BPI_Combat               | Player/Component/Combat            | 10  | BPC_Combat         |
| BPI_LockOn               | Player/Component/LockOn            | 5   | BPC_LockOn         |
| BPI_EnemyBase            | Enemy                              | 2   | BP_EnemyBase       |
| BPI_AttackTrace          | Enemy/Component/AttackTrace        | 6   | BPC_AttackTrace    |
| BPI_AI                   | Enemy/Component/AI                 | 9   | BPC_AI             |
| BPI_Execution            | Player/Component/Combat            | 4   | BPC_Combat         |

合计 119 个接口函数。

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

---

[↑ 回到目录](#目录)
