# ActGame

动作战斗游戏 · UE5 蓝图项目

本文件是项目内「组件 / 接口 / 数据结构」的速查表，写蓝图前先对一遍。

---

# 注：

```
接口名与其实现的组件名相同

```

## 1，CharacterBase（角色基类）

| 组件名                | 组件用途      |
| ------------------ | --------- |
| BPC_Attribute      | 角色属性      |
| BPC_CombatFeedBack | 角色攻击音效，顿帧 |
| BPC_Motor          | 角色运动层控制   |
### 1）类接口方法

#### （1）BPI_CharacterBase

| 方法名                        | 输入  | 输出                     | 作用                        |
| -------------------------- | --- | ---------------------- | ------------------------- |
| GetAttributeComponent      | /   | BPC_Attribute对象引用      | 获取角色的BPC_Attribute对象      |
| GetCombatFeedbackComponent | /   | BPC_CombatFeedBack对象引用 | 获取角色的BPC_CombatFeedBack对象 |
| GetCharacterMovement       | /   | 角色移动组件                 | 获取角色的移动组件                 |
| GetMotorComponent          | /   | BPC_Motor对象引用          | 获取角色的BPC_Motor对象          |


#### （2）BPI_Attribute

| 方法名             | 输入                                | 输出                | 作用                                     |
| --------------- | --------------------------------- | ----------------- | -------------------------------------- |
| GetAttack       | /                                 | float             | 获取角色的攻击值（包括武器基础加成）                     |
| TakeDamage      | float，float                       | bool（是否击破韧性）      | 对角色施加伤害，并返回是否破韧                        |
| AddBonus        | float                             | /                 | 添加武器加成                                 |
| GetDefense      | /                                 | float（0~1）        | 获取角色减伤                                 |
| GetPoiseAttack  | /                                 | float             | 获取角色的削轫值（包括武器基础加成）                     |
| IsDead          | /                                 | bool              | 角色是否死亡                                 |
| ReceiveDamage   | ST_AttackData，float，Vector3，float | E_HitOutCome，bool | 根据攻击的数据，基础伤害值，基础削轫值，受击位置，返回受击类型和是否完美格挡 |
| ClearPoseBroken | /                                 | /                 | 清除削轫破防效果                               |

#### （3）BPI_CombatFeedBack

| 方法名             | 输入                                    | 输出  | 作用                                            |
| --------------- | ------------------------------------- | --- | --------------------------------------------- |
| PlayHitFeedback | E_HitOutCome，Vector3，bool，Actor，float | /   | 根据输入的击中类型，击中位置，是否完美格挡，命中者，顿帧值，播放命中音效，顿帧以及屏幕抖动 |
| PlayHitStop     | Actor，float                           | /   | 根据命中者，延迟时长，播放顿帧                               |
| EndHitStop      | /                                     | /   | 离开顿帧                                          |

#### （4）BPI_Motor

| 方法名              | 输入               | 输出  | 作用               |
| ---------------- | ---------------- | --- | ---------------- |
| ApplyKnockback   | Vector3，bool     | /   | 根据输入的向量给角色施加一个冲量 |
| SetMotionProfile | ST_MotionProfile | /   | 设置代码位移的基础变量      |
| StartMotion      | /                | /   | 开始代码位移           |
| StopMotion       | /                | /   | 停止代码位移           |


### 2）数据类型

#### （1）枚举

##### 一，E_AttackType（攻击类型）

| 枚举值    | 枚举含义 |
| ------ | ---- |
| Common | 普通攻击 |
|        |      |

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
| ID               | name         | none    | 动作名（我感觉可有可无）                 |
| Montage          | 动画蒙太奇        | none    | 动作播放的montage                 |
| SectionStart     | name         | none    | montage开始播放的片段               |
| Next             | ST_Edge数组    | none    | 下一个动作名以及进入所需的操作              |
| CancelStart      | float        | 0       | 取消窗口打开的时间（我感觉可有可无）           |
| DamageRate       | float        | 0       | 伤害倍率                         |
| PoiseDdamageRate | float        | 0       | 削轫倍率                         |
| HitStop          | float        | 0       | 顿帧时长                         |
| LaunchEnemy      | Vector3      | （0，0，0） | 命中敌人时对敌人的力                   |
| CanUseInAir      | bool         | false   | 是否可以在空中使用                    |
| PlayGravity      | float        | 1       | 使用时角色的重力                     |
| LaunchSelf       | Vector3      | （0，0，0） | 命中敌人时对自己的力                   |
| MotionSelf       | Vector3      | （0，0，0） | xy表示角色在播放改动作时位移方向，z表示对角色向上的力 |
| MoveSpeed        | float        | 600     | 角色在水平上的移动速度（大于610才有代码位移）     |
| MoveFriction     | float        | 8       | 移动时角色摩擦力                     |
| bLockPelvisZ     | bool         | false   | 是否锁定角色的Pelvis骨骼的z坐标          |
| AttackType       | E_AttackType | Common  | 动作的攻击类型                      |

##### 二，ST_Edge

| 值名     | 类型          | 默认值  | 含义           |
| ------ | ----------- | ---- | ------------ |
| NextID | name        | none | 下一个动作的ID     |
| Input  | E_InputType | none | 进入下一个动作所需的输入 |

##### 三，ST_MotionProfile

| 值名           | 类型      | 默认值     | 含义   |
| ------------ | ------- | ------- | ---- |
| speed        | float   | 0       | 水平速度 |
| direction    | vector3 | （0，0，0） | 水平方向 |
| friction     | float   | 8       | 摩擦力  |
| gravityScale | float   | 1       | 重力大小 |

## 2，Player（玩家特有）（继承于CharacterBase）

| 组件名                | 组件用途     |
| ------------------ | -------- |
| BPC_ActionState    | 玩家当前状态   |
| BPC_BufferInput    | 玩家输入缓存   |
| BPC_CameraDirector | 玩家相机控制   |
| BPC_Combat         | 玩家角色动作控制 |
| BPC_LockOn         | 玩家索敌控制   |

### 1）类接口方法

#### （1）BPI_Player

| 方法名                     | 输入   | 输出                     | 作用                        |
| ----------------------- | ---- | ---------------------- | ------------------------- |
| GetActionStateComponent | /    | BPC_ActionState对象引用    | 获取角色的BPC_ActionState对象    |
| GetBufferInputComponent | /    | BPC_BufferInput对象引用    | 获取角色的BPC_BufferInput对象    |
| GetDirectorComponent    | /    | BPC_CameraDirector对象引用 | 获取角色的BPC_CameraDirector对象 |
| GetCombatComponent      | /    | BPC_Combat对象引用         | 获取角色的BPC_Combat对象         |
| GetLockComponent        | /    | BPC_LockOn对象引用         | 获取角色的BPC_LockOn对象         |
| GetMesh                 | /    | 骨骼网格体组件                | 获取角色的骨骼网格体组件              |
| GetWeapon               | /    | BP_WeaponBase对象引用      | 获取角色的武器                   |
| GetWeaponHitBox         | /    | 盒体碰撞                   | 获取角色武器碰撞箱                 |
| StartJump               | /    | /                      | 让角色跳跃（给Combat的接口）         |
| IntoHardLockState       | /    | /                      | 进入硬锁                      |
| OutHardLockState        | /    | /                      | 退出硬锁                      |
| SetLockPlevisZ          | bool | /                      | 设置是否锁定Plevis骨骼的z位置        |


#### （2）BPI_ActionState

| 方法名             | 输入            | 输出            | 作用                                |
| --------------- | ------------- | ------------- | --------------------------------- |
| TryEnterState   | E_ActionState | bool          | 尝试进入新的状态，并返回是否成功                  |
| GetActionState  | /             | E_ActionState | 获取角色当前的状态                         |
| ForceEnterState | E_ActionState | bool          | 强制进入新的状态（当前处于控制状态不能转移），返回是否成功转移状态 |
| CanDodge        | /             | bool          | 返回是否可以冲刺（冲刺有CD）                   |
| UpdateDodgeCD   | float         | /             | 更新冲刺CD                            |

#### （3）BPI_BufferInput

| 方法名     | 输入          | 输出   | 作用                 |
| ------- | ----------- | ---- | ------------------ |
| Push    | E_InputType | /    | 向缓存中推入新的输入         |
| Comsume | E_InputType | bool | 读取缓存中的指定输入，并返回是否成功 |
| Peek    | E_InputType | bool | 看缓存中是否有指定且没过期的输入   |

#### （4）BPI_CameraDirector

| 方法名   | 输入                              | 输出  | 作用                           |
| ----- | ------------------------------- | --- | ---------------------------- |
| Shake | E_CameraShakeType，Vector3，float | /   | 根据输入的相机抖动枚举，受击位置，抖动强度，制造屏幕抖动 |

#### （5）BPI_Combat

| 方法名              | 输入   | 输出            | 作用             |
| ---------------- | ---- | ------------- | -------------- |
| DoLight          | /    | /             | 操作轻击           |
| DoHeavy          | /    | /             | 操作重击           |
| DoJump           | /    | /             | 操作跳跃           |
| DoDodge          | /    | /             | 操作冲刺           |
| GetCurrentAttack | /    | ST_AttackData | 获取当前动作的数据（结构体） |
| OnAttackWindow   | bool | /             | 操作攻击窗口（包括关开）   |
| ClearAttackData  | /    | /             | 清除当前的动作数据      |

#### （6） BPI_LockOn

| 方法名              | 输入  | 输出            | 作用          |
| ---------------- | --- | ------------- | ----------- |
| GetFocusTarget   | /   | Actor         | 获取角色当前锁定的对象 |
| GetLockState     | /   | E_LockOnState | 获取角色当前的锁定状态 |
| HardLockPress    | /   | /             | 硬锁按键按下后的操作  |
| HardLockRelease  | /   | /             | 硬锁按键松开后的操作  |
| SimpleAimCorrect | /   | /             | 软锁下修改角色的朝向  |

### 2）数据类型

#### （1）枚举

##### 一，E_ActionState

| 枚举值        | 枚举含义         |
| ---------- | ------------ |
| Locomotion | 一般状态         |
| Jump       | 跳跃状态（包括下落状态） |
| Attack     | 攻击状态         |
| Dodge      | 冲刺状态         |
| HitLight   | 轻受击          |
| HitHeavy   | 重受击          |
| KnockDown  | 倒地           |
| Dead       | 死亡状态         |
| Guard      | 格挡状态         |

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

## 3，EnemyBase（敌人角色基类）（继承于CharacterBase）

| 组件名             | 组件用途      |
| --------------- | --------- |
| BPC_AI          | 敌人AI控制器控制 |
| BPC_AttackTrace | 敌人角色动作控制  |
### 1）类接口方法

#### （1）BPI_EnemyBase

| 方法名                     | 输入  | 输出                  | 作用                     |
| ----------------------- | --- | ------------------- | ---------------------- |
| GetWeaponHitBox         | /   | 盒体碰撞                | 获取角色武器碰撞箱              |
| GetAttackTraceComponent | /   | BPC_AttackTrace对象引用 | 获取角色的BPC_AttackTrace对象 |
| GetMesh                 | /   | 骨骼网格体组件             | 获取角色的骨骼网格体组件           |
| GetAIComponent          | /   | BPC_AI对象引用          | 获取角色的BPC_AI对象          |

#### （2）BPI_AttackTrace

| 方法名            | 输入           | 输出  | 作用           |
| -------------- | ------------ | --- | ------------ |
| OnAttackWindow | bool         | /   | 操作攻击窗口（包括关开） |
| AttackByType   | E_AttackType | /   | 根据攻击类型发动攻击   |

#### （3）BPI_AI

| 方法名                     | 输入         | 输出        | 作用                |
| ----------------------- | ---------- | --------- | ----------------- |
| AI_AddPerceivedActor    | Actor      | /         | 添加感受到的对象          |
| AI_RemovePerceivedActor | Actor      | /         | 删除指定对象（在感受对象的数组中） |
| AI_GetCurrentTarget     | /          | Actor     | 获取当前锁定的对象         |
| AI_GetAIState           | /          | E_AIState | 获取当前的AI状态         |
| AI_IsAlive              | /          | bool      | 角色当前是否活着          |
| AI_RefreshTarget        | /          | /         | 更新锁定的目标           |
| AI_HandleSight          | Actor，bool | /         | 处理视觉感受的情况         |

### 2）数据类型

#### （1）枚举

##### 一，E_AIState

| 枚举值    | 枚举含义   |
| ------ | ------ |
| Idle   | 站立（待机） |
| Chase  | 追击     |
| Dead   | 死亡     |
| Attack | 攻击     |

## 3，WeaponBase（武器基类）

### 1）类接口方法

#### （1）BPI_WeaponBase

| 方法名             | 输入  | 输出    | 作用             |
| --------------- | --- | ----- | -------------- |
| GetWeaponBonus  | /   | float | 获取武器的加成（攻击力加成） |
| GetWeaponHitBox | /   | 盒体碰撞  | 获取武器碰撞箱        |
