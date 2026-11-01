# ActGame

动作战斗游戏 · UE5 蓝图项目

本文件是项目内「组件 / 接口 / 数据结构」的速查表，写蓝图前先对一遍。

> **校对说明**：本文件已按 `Content/` 下的实际资产重新扫描校对（共 16 个 `BPI_`*、10 个 `E_`*、2 个 `ST_*`）。
> **接口函数清单以蓝图编辑器「我的蓝图 → 函数」面板为准** —— UE 的 name table 会保留已删除函数的 FName 条目，直接扫二进制会把历史函数误报成现存函数。
> 与旧版不一致的地方统一记在文末的「七、校对差异清单」里，方便逐条确认。

---

# 注：

```
接口名与其实现的组件名相同
```

## 0，接口总览

| 接口                       | 目录                                 | 函数数 | 对应实现               |
| ------------------------ | ---------------------------------- | --- | ------------------ |
| BPI_CharacterBase        | Code/Interface                     | 8   | 无（纯接口，所有组件获取的统一入口） |
| BPI_Attribute            | Code/ActorComponent/DamageSystem   | 12  | BPC_Attribute      |
| BPI_CombatFeedBack       | Code/ActorComponent/CombatFeedBack | 3   | BPC_CombatFeedBack |
| BPI_Motor                | Code/ActorComponent/Motor          | 8   | BPC_Motor          |
| BPI_WeaponBase           | Code/Weapon                        | 2   | BP_WeaponBase      |
| BPI_GameState            | Code/GameState                     | 3   | 待接入                |
| BPI_HIt                  | Code/Interface                     | 1   | 待接入                |
| BPI_Player               | Player                             | 9   | BP_Player          |
| BPI_ActionState          | Player/Component/ActionState       | 7   | BPC_ActionState    |
| BPI_BufferInput          | Player/Component/BufferInput       | 3   | BPC_BufferInput    |
| BPI_CameraDirector       | Player/Component/CameraDirector    | 1   | BPC_CameraDirector |
| BPI_Combat               | Player/Component/Combat            | 8   | BPC_Combat         |
| BPI_LockOn               | Player/Component/LockOn            | 6   | BPC_LockOn         |
| BPI_EnemyBase            | Enemy                              | 2   | BP_EnemyBase       |
| BPI_AttackTrace          | Enemy/Component/AttackTrace        | 2   | BPC_AttackTrace    |
| BPI_AI                   | Enemy/Component/AI                 | 9   | BPC_AI             |

合计 84 个接口函数。

---

## 1，CharacterBase（角色基类）

| 组件名                | 组件用途      |
| ------------------ | --------- |
| BPC_Attribute      | 角色属性      |
| BPC_CombatFeedBack | 角色攻击音效，顿帧 |
| BPC_Motor          | 角色运动层控制   |

### 1）类接口方法

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

> **这里是全部「取组件 / 取引用」的唯一入口。**
> `BPI_Player` 与 `BPI_EnemyBase` 不再重复声明 `GetMesh` / `GetHitBox` / `GetWeapon` / `GetAttributeComponent`，写蓝图时统一从基类接口取。

#### （2）BPI_Attribute

| 方法名             | 输入                                             | 输出                                     | 作用                                              |
| --------------- | ---------------------------------------------- | -------------------------------------- | ----------------------------------------------- |
| GetAttack       | /                                              | float（Attack）                          | 获取角色的攻击值（包括武器基础加成）                              |
| GetDefense      | /                                              | float（Defenses，0~1）                    | 获取角色减伤                                          |
| GetPoiseAttack  | /                                              | float（PoiseAttack）                     | 获取角色的削轫值（包括武器基础加成）                              |
| AddBonus        | float（AttackDelta）                            | /                                      | 添加武器加成                                          |
| IsDead          | /                                              | bool（Dead）                             | 角色是否死亡                                          |
| TakeDamage      | float（BaseDamage），float（PoiseDamage）          | bool（bIsBroken）                        | 扣血扣韧，返回是否破韧。**内部不再乘防御**                        |
| ReceiveDamage   | ST_AttackData，float，Vector3，float             | E_HitOutCome，bool，bool                 | 完整受击判定：攻击数据、基础伤害、受击位置、基础削轫 → 受击类型、是否完美格挡、是否完美闪避 |
| ClearPoseBroken | /                                              | /                                      | 清除削轫破防效果                                        |
| RestorePoise    | /                                              | /                                      | 恢复韧性到 MaxPoise（Tick 里调用）                       |
| EnterGuard      | /                                              | /                                      | 进入格挡：置 bIsGuarding，记录 LastGuardTime          |
| ExitGuard       | /                                              | /                                      | 退出格挡                                            |
| NotifyDodgeStart | float（Time）                                  | /                                      | 记录闪避起手时刻，供完美闪避无敌帧判定使用                          |

`ReceiveDamage` **的三个输出含义：**

| 输出              | 含义                                        |
| --------------- | ----------------------------------------- |
| HitOutCome      | `Ignore` 无伤 / `Hit` 普通受击 / `Blocked` 格挡生效 |
| bPerfectBlock   | 是否完美格挡（完全免伤）                              |
| bPerfectDodge   | 是否完美闪避（无敌帧内受击）                            |

**判定优先级（顺序不能调）：**

```
① 已死亡                → Ignore
② 完美闪避窗口内         → Ignore + bPerfectDodge
③ 格挡 + 正面 + Poise>0 → 完美格挡窗口内？Blocked + bPerfectBlock 免伤
                          否则 Blocked，伤害 ×(1−GuardDamageReduction)，削轫 ×GuardPoiseScale
④ 其余（含背面格挡）      → Hit，伤害 ×(1−Defense)
```

**韧性为 0 时格挡完全失效，完美格挡也一并失效。**

#### （3）BPI_CombatFeedBack

| 方法名             | 输入                                            | 输出  | 作用                                            |
| --------------- | --------------------------------------------- | --- | --------------------------------------------- |
| PlayHitFeedback | E_HitOutCome（Outcome），Vector3（ImpactLocation），bool（bPerfect），Actor（OtherActor），float（BaseHitStop） | /   | 播放命中音效、顿帧、屏幕抖动                                |
| PlayHitStop     | Actor，float                                   | /   | 根据命中者与时长播放顿帧                                  |
| EndHitStop      | /                                             | /   | 离开顿帧                                          |

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

### 2）数据类型

#### （1）枚举

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

### 1）类接口方法

#### （1）BPI_Player

| 方法名                     | 输入   | 输出                     | 作用                |
| ----------------------- | ---- | ---------------------- | ----------------- |
| GetActionStateComponent | /    | BPC_ActionState 对象引用    | 获取 BPC_ActionState |
| GetCombatComponent      | /    | BPC_Combat 对象引用         | 获取 BPC_Combat      |
| GetBufferInputComponent | /    | BPC_BufferInput 对象引用    | 获取 BPC_BufferInput |
| GetDirectorComponent    | /    | BPC_CameraDirector 对象引用 | 获取 BPC_CameraDirector |
| GetLockComponent        | /    | BPC_LockOn 对象引用         | 获取 BPC_LockOn      |
| StartJump               | /    | /                      | 让角色跳跃             |
| IntoHardLockState       | /    | /                      | 进入硬锁              |
| OutHardLockState        | /    | /                      | 退出硬锁              |
| SetLockPlevisZ          | bool | /                      | 设置是否锁定 Plevis 骨骼的 z 位置 |

> `GetMesh`、`GetHitBox`、`GetWeapon`、`GetAttributeComponent`、`GetCharacterMovement` **已全部上收到** `BPI_CharacterBase`，玩家侧不再各自声明。写蓝图时统一走基类接口。

#### （2）BPI_ActionState

| 方法名             | 输入                   | 输出              | 作用                                |
| --------------- | -------------------- | --------------- | --------------------------------- |
| TryEnterState   | E_ActionState（NewState） | bool            | 一级状态转换：走转场矩阵与受控状态优先级。**永远不能回 Locomotion** |
| ForceEnterState | E_ActionState（NewState） | bool            | 二级状态转换：连招续接。需取消窗口打开，不受控状态下一律无效    |
| SetState        | E_ActionState（NewState） | /               | 收尾复位，无校验、幂等。**唯一能回 Locomotion 的入口** |
| GetActionState  | /                    | E_ActionState   | 获取角色当前状态                          |
| SetCancelWindow | bool                 | /               | 开关取消窗口。只允许 Combat 与动画通知调用         |
| CanDodge        | /                    | bool            | 当前是否可以冲刺（受 CD 与非受控状态约束）            |
| UpdateDodgeCD   | float（Time）          | /               | 记录冲刺起手时刻，用于 CD 判定                  |

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

#### （5）BPI_Combat

| 方法名              | 输入   | 输出            | 作用             |
| ---------------- | ---- | ------------- | -------------- |
| DoLight          | /    | /             | 操作轻击           |
| DoHeavy          | /    | /             | 操作重击           |
| DoJump           | /    | /             | 操作跳跃           |
| DoDodge          | /    | /             | 操作冲刺           |
| GetCurrentAttack | /    | ST_AttackData | 获取当前动作的数据      |
| OnAttackWindow   | bool | /             | 开关攻击窗口         |
| MoveStart        | /    | /             | 招式位移开始         |
| MoveEnd          | /    | /             | 招式位移结束         |

#### （6）BPI_LockOn

| 方法名              | 输入  | 输出            | 作用          |
| ---------------- | --- | ------------- | ----------- |
| GetFocusTarget   | /   | Actor         | 获取当前锁定的对象   |
| GetTarget        | /   | Actor         | 获取候选/当前目标   |
| GetLockState     | /   | E_LockOnState | 获取当前锁定状态    |
| HardLockPress    | /   | /             | 硬锁键按下       |
| HardLockRelease  | /   | /             | 硬锁键松开       |
| SimpleAimCorrect | /   | /             | 软锁下修正角色朝向   |

### 2）数据类型

#### （1）枚举

##### 一，E_ActionState

| 枚举值        | 枚举含义         |
| ---------- | ------------ |
| Locomotion | 一般状态（最低级，回它只能走 SetState） |
| Jump       | 跳跃状态（含下落）    |
| Attack     | 攻击状态         |
| Dodge      | 冲刺状态         |
| Guard      | 格挡状态         |
| HitLight   | 轻受击（受控）      |
| HitHeavy   | 重受击（受控）      |
| KnockDown  | 倒地（受控）       |
| Dead       | 死亡（受控，绝对终态）  |

##### 二，E_CameraShakeType（屏幕抖动类型）

| 枚举值          | 枚举含义   |
| ------------ | ------ |
| Hit          | 普通受击抖动 |
| Block        | 格挡抖动   |
| PerfectBlock | 完美格挡抖动 |
| Break        | 破韧抖动   |
| Kill         | 死亡抖动   |

##### 三，E_InputType

| 枚举值     | 枚举含义 |
| ------- | ---- |
| Light   | 轻击   |
| Heavy   | 重击   |
| Dodge   | 冲刺   |
| Jump    | 跳跃   |
| Execute | 处决   |

##### 四，E_LockOnState（锁定状态）

| 枚举值  | 枚举含义 |
| ---- | ---- |
| None | 无锁定  |
| Soft | 软锁   |
| Hard | 硬锁   |

##### 五，E_MoveState（移动状态）

| 枚举值  | 枚举含义 |
| ---- | ---- |
| Idle | 站立   |
| Walk | 走路   |
| Run  | 奔跑   |

---

## 3，EnemyBase（敌人角色基类）（继承于 CharacterBase）

| 组件名             | 组件用途      |
| --------------- | --------- |
| BPC_AI          | 敌人 AI 控制  |
| BPC_AttackTrace | 敌人攻击判定    |
| BPC_Attribute   | 复用 CharacterBase 的属性组件 |

### 1）类接口方法

#### （1）BPI_EnemyBase

| 方法名                     | 输入  | 输出                  | 作用                     |
| ----------------------- | --- | ------------------- | ---------------------- |
| GetAttackTraceComponent | /   | BPC_AttackTrace 对象引用 | 获取 BPC_AttackTrace      |
| GetAIComponent          | /   | BPC_AI 对象引用          | 获取 BPC_AI               |

> `GetMesh`、`GetHitBox`、`GetEnemyAttributeComponent` **已全部上收到** `BPI_CharacterBase`（属性统一走 `GetAttributeComponent`），敌人侧不再各自声明。

#### （2）BPI_AttackTrace

| 方法名            | 输入           | 输出  | 作用           |
| -------------- | ------------ | --- | ------------ |
| OnAttackWindow | bool         | /   | 开关攻击窗口       |
| AttackByType   | E_AttackType | /   | 根据攻击类型发动攻击   |

#### （3）BPI_AI

| 方法名                     | 输入                     | 输出        | 作用                |
| ----------------------- | ---------------------- | --------- | ----------------- |
| AI_AddPerceivedActor    | Actor                  | /         | 添加感受到的对象          |
| AI_RemovePerceivedActor | Actor                  | /         | 从感受列表中删除对象        |
| AI_GetCurrentTarget     | /                      | Actor     | 获取当前锁定的对象         |
| AI_RefreshTarget        | /                      | /         | 重算并写入黑板 TargetActor |
| AI_GetAIState           | /                      | E_AIState | 获取当前 AI 状态        |
| AI_SetAIState           | E_AIState（NewState）    | /         | 设置 AI 状态（同步黑板）    |
| AI_IsAlive              | /                      | bool      | 角色当前是否活着          |
| AI_HandleSight          | Actor，bool（bSensed）    | /         | 处理视觉感知的进入/丢失      |
| HandleDamageApplied     | 参数待确认                  | /         | 受击后由伤害系统回调        |

### 2）数据类型

#### （1）枚举

##### 一，E_AIState

| 枚举值       | 枚举含义      |
| --------- | --------- |
| Idle      | 站立（待机）    |
| Chase     | 追击        |
| Attack    | 攻击        |
| HitLight  | 轻受击（受控）   |
| HitHeavy  | 重受击（受控）   |
| KnockDown | 倒地（受控）    |
| Dead      | 死亡（受控）    |

##### 二，E_EnemyAttackType

| 枚举值    | 枚举含义 |
| ------ | ---- |
| Common | 普通攻击 |

---

## 4，WeaponBase（武器基类）

### 1）类接口方法

#### （1）BPI_WeaponBase

| 方法名             | 输入  | 输出    | 作用             |
| --------------- | --- | ----- | -------------- |
| GetWeaponBonus  | /   | float | 获取武器的攻击力加成     |
| GetWeaponHitBox | /   | 盒体碰撞  | 获取武器碰撞箱        |

---

## 5，其他独立接口

### （1）BPI_GameState（Code/GameState）

| 方法名         | 输入            | 输出   | 作用        |
| ----------- | ------------- | ---- | --------- |
| AddToken    | Actor（Holder） | /    | 为持有者登记令牌  |
| RemoveToken | Actor（Holder） | /    | 移除持有者的令牌  |
| HasToken    | Actor（Holder） | bool | 查询持有者是否有令牌 |

### （2）BPI_HIt（Code/Interface）

| 方法名      | 输入                             | 输出  | 作用      |
| -------- | ------------------------------ | --- | ------- |
| EnterHit | E_ActionState（HitType），Vector（HitLoc） | /   | 进入受击处理 |

### （3）BPI_Interaction

**已删除（原为空壳，0 个函数）。**

---

## 6，写蓝图时的三条硬规矩

```
① 状态层（BPC_ActionState）不引用任何其他组件
   它只管 CurrentState、bCanCancel 和转场规则

② 伤害规则全部收在 BPC_Attribute
   无敌、完美格挡、完美闪避、减伤、削轫、破韧都在这一个地方判定

③ 副作用全部由 BPC_Combat 下发
   Motor 的位移、Attribute 的伤害、CombatFeedBack 的反馈，Combat 是唯一的发起者
```

`BPC_CombatFeedBack` **内部再调** `BPC_CameraDirector.Shake`**，Combat 不直接碰 CameraDirector。**

---

## 七、校对差异清单

以下是本次扫描发现、与旧版 README 不一致的地方。已按「实际资产」更新到上文，这里留档备查。

### 已修正的文档错误

| #   | 位置                          | 旧版写法                 | 实际情况                                                                                                                         |
| --- | --------------------------- | -------------------- | ---------------------------------------------------------------------------------------------------------------------------- |
| 1   | BPI_Attribute               | 只有 8 个函数             | 实际 12 个，补 `EnterGuard` / `ExitGuard` / `NotifyDodgeStart` / `RestorePoise`                                                   |
| 2   | BPI_Attribute.ReceiveDamage | 描述为「是否完美格挡，以及是否破韧」   | 两个 bool 是 `bPerfectBlock` 和 `bPerfectDodge`，**没有破韧输出**                                                                       |
| 3   | BPI_ActionState             | 5 个函数                | 实际 7 个，补 `SetState` / `SetCancelWindow`                                                                                      |
| 4   | BPI_CharacterBase           | 4 个函数                | 实际 8 个，补 `GetMeshComponent` / `GetHitBoxComponent` / `GetWeapon` / `GetImpulse`                                              |
| 5   | BPI_Motor                   | 4 个函数                | 实际 8 个，补 `IsMoving` / `IsBeingKnockedBack` / `SetGravity` / `ResetGravity`                                                   |
| 6   | BPI_Player                  | 14 个函数               | **实际 9 个**：`GetMesh` / `GetHitBox` / `GetWeapon` / `GetAttributeComponent` / `GetCharacterMovement` 已上收到 `BPI_CharacterBase` |
| 7   | BPI_EnemyBase               | 5 个函数                | **实际 2 个**：`GetMesh` / `GetHitBox` / `GetEnemyAttributeComponent` 已上收到 `BPI_CharacterBase`                                   |
| 8   | BPI_AI                      | 7 个函数                | 实际 9 个，补 `AI_SetAIState` / `HandleDamageApplied`                                                                             |
| 9   | BPI_LockOn                  | 5 个函数                | 实际 6 个，补 `GetTarget`                                                                                                         |
| 10  | BPI_Combat                  | 7 个函数                | 实际 8 个：**没有** `ClearAttackData`，新增 `MoveStart` / `MoveEnd`                                                                   |
| 11  | E_AIState                   | 4 个值                 | 实际 7 个，补 `HitLight` / `HitHeavy` / `KnockDown`                                                                               |
| 12  | ST_AttackData               | 写作 `PoiseDamageRate` | 资产里是 `PoiseDdamageRate`（多一个 d）                                                                                               |
| 13  | 缺失整节                        | 无                    | 补 `BPI_GameState` / `BPI_HIt` / `E_EnemyAttackType`                                                                          |

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

⑤ BPI_AI.HandleDamageApplied 的参数没确认
   扫描只能看到函数名，看不到引脚。需要打开资产确认

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
```
