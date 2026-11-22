# CharacterBase（角色基类）

> 本文件是模块文档。项目总导航、规范与历史见 [README.md](../README.md)。

## 1，CharacterBase（角色基类）

| 组件名                | 组件用途      |
| ------------------ | --------- |
| BPC_Attribute      | 角色属性      |
| BPC_CombatFeedBack | 角色攻击音效、顿帧；将战斗反馈路由到玩家镜头 |
| BPC_Motor          | 角色运动层控制   |

### 1）CharacterBase 类接口方法

#### （1）BPI_CharacterBase

| 方法名                        | 输入                           | 输出                         | 作用                       |
| -------------------------- | ---------------------------- | -------------------------- | ------------------------ |
| GetAttributeComponent      | /                            | BPC_Attribute 对象引用         | 获取角色的 BPC_Attribute      |
| GetCombatFeedbackComponent | /                            | BPC_CombatFeedBack 对象引用    | 获取角色的 BPC_CombatFeedBack |
| GetMotorComponent          | /                            | BPC_Motor 对象引用             | 获取角色的 BPC_Motor          |
| GetMotionWarpingComponent  | /                            | MotionWarping 组件引用          | 获取角色的动作扭曲组件（处决/投技对齐用） |
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
| TakeDamage       | float（BaseDamage），float（PoiseDamage），float（PostureDamage） | bool（bIsBroken），bool（bPostureBroken） | **纯执行器**：只扣血/韧/架势并返回两个布尔，不做任何减免或倍率计算。最终数值全在 `ReceiveDamage` 里算好传入 |
| ReceiveDamage    | ST_AttackData，float，Vector3（攻击者位置），Vector3（HitPoint），float（BasePoiseDamage），float（BasePostureDamage） | E_HitOutCome，bool，bool，bool | 完整受击判定：攻击数据、基础伤害、攻击者位置、击中点、基础削轫、基础架势伤害 → 受击类型、是否完美格挡、**是否破韧**、是否完美闪避 |
| GetPostureAttack | /                                    | float（PostureAttack）   | 获取角色的架势攻击力（含武器加成），由攻击方在调用 `ReceiveDamage` 时传入 `BasePostureDamage` |
| ReliefPosture    | /                                    | /                      | 架势自动恢复满值。**离开 KnockDown 收尾、脱战恢复等统一入口**（不暴露 `MaxPosture`） |
| ClearPoseBroken  | /                                    | /                      | 清除削轫破防效果                                        |
| RestorePoise     | /                                    | /                      | 恢复韧性到 MaxPoise（Tick 里调用）                        |
| EnterGuard       | /                                    | /                      | 进入格挡：置 bIsGuarding，记录 LastGuardTime             |
| ExitGuard        | /                                    | /                      | 退出格挡                                            |
| NotifyDodgeStart | float（Time）                          | /                      | 记录闪避起手时刻，供完美闪避窗口判定使用                            |
| SetInvincible    | bool（bInvincible）                     | /                      | 开关无敌。由 `ANS_IFrame` 的 Begin / End 调用              |
| EndPerfectDodge  | /                                    | /                      | 完美闪避收尾：若仍在无敌则关无敌并补一段尾巴。由 Combat 调用 |

`ReceiveDamage` **的四个输出含义：**

| 输出              | 含义                                        |
| --------------- | ----------------------------------------- |
| HitOutCome      | `Ignore` 无伤 / `Hit` 普通受击 / `Blocked` 格挡生效 / `BreakPoise` 格挡中韧性归零 / `BreakPosture` **架势归零（防御崩坏）** |
| bPerfectBlock   | 是否完美格挡（完全免伤）                              |
| IsBroken        | **本次攻击是否破韧**（Poise 归零）—— 直通 `TakeDamage` 的返回值，不再存成员变量 |
| bPerfectDodge   | 是否完美闪避（在无敌帧内**且**处于完美窗口）                  |

**`BreakPoise` 与 `BreakPosture` 是两条平行线：**

```
BreakPoise   = 格挡中 Poise 归零 → HandleGuardBreak → HitHeavy + GuardBreak 蒙太奇（韧性逻辑）
BreakPosture = Posture 归零（格挡或命中共通）→ HandleBreakPosture → KnockDown（架势逻辑）
两者同时归零 → BreakPosture 优先（KnockDown 比 HitHeavy 高一级）
```

**判定优先级（顺序不能调）：**

```
① 已死亡                        → Ignore
② 无敌中（bInvincible 或 无敌尾巴）
     且在完美窗口内              → Ignore + bPerfectDodge = true
     仅无敌、不在完美窗口        → Ignore，bPerfectDodge = false
③ 格挡 + 正面 + Poise>0         → 完美格挡窗口内？Blocked + bPerfectBlock 免伤（架势不扣）
                                  否则：最终伤害 = Base×(1−GuardDamageReduction)
                                        最终削轫 = BasePoiseDamage × GuardPoiseScale
                                        最终架势 = BasePostureDamage
                                        TakeDamage(三者) →
                                          bPostureBroken？→ BreakPosture
                                          bIsBroken？     → BreakPoise
                                          否则            → Blocked
④ 其余（含背面格挡）             → 最终伤害 = Base×(1−Defense)，削轫/架势原值
                                  TakeDamage(三者) →
                                    bPostureBroken？→ BreakPosture（优先于 HitHeavy）
                                    bIsBroken？     → Hit + IsBroken=true
                                    否则            → Hit
```

**② 的两个条件是 `AND`：只判时间会把闪避结束后的受击误判成完美；只判无敌会把整个无敌区间都算成完美，缓冲带就没了。**

**破韧不单独存状态：**

```
韧性扣除与破韧判断都在 TakeDamage 内部完成（扣到 0 时返回 bIsBroken = true）
ReceiveDamage 把它直通为 IsBroken 输出，不再维护 bPoiseBroken 成员变量
→ 调用方拿到 IsBroken 决定破韧表现（硬直/动画/音效），无需再查询 Attribute
```

**⭐ 这是「规范 · 状态表达」第 ② 条的直接应用：能从函数返回值得到的，不要额外存 bool。**

**六个输入的分工：**

| 输入 | 参与判定 | 用途 |
| --- | --- | --- |
| `ST_AttackData` | ✅ | 伤害倍率、削轫倍率 |
| `BaseDamage` | ✅ | 基础伤害 |
| `攻击者位置` | ✅ | **算受击方向**（正面 / 背面 / 左 / 右） |
| `HitPoint` | ❌ | **只用于表现**：火花位置、震屏位置、FOV 特写锚点 |
| `BasePoiseDamage` | ✅ | 基础削轫 |
| `BasePostureDamage` | ✅ | 基础架势伤害（攻击方传 `GetPostureAttack()`） |

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

**架势（Posture）与韧性平行、独立结算：**

```
Posture 满值 = 稳，0 = 崩（初始 = MaxPosture）
格挡与命中都扣架势（命中扣得更多），归零 → BreakPosture → KnockDown
与 Poise 互不替代：Poise 归零走 HitHeavy/GuardBreak，Posture 归零走 KnockDown
```

| 变量 | 类型 | 默认 | 说明 |
| --- | --- | --- | --- |
| `Posture` | float | 100 | 当前架势（初始 = `MaxPosture`） |
| `MaxPosture` | float | 100 | 上限 |
| `PostureAttack` | float | 10 | 攻击方的架势攻击力（含武器加成，`GetPostureAttack` 读取） |
| `LastCombatTime` | float | -9999 | 最后一次参与战斗的时刻（脱战判定） |
| `CombatDisengageTime` | float | 5.0 | 多久无战斗交互视为脱战（秒） |
| `PostureRegenRate` | float | 30 | 脱战后的恢复速率（+值/秒） |

**架势恢复只有三条途径（全部收敛到 `ReliefPosture` / 脱战 Tick）：**

```
① 脱战：Now − LastCombatTime ≥ CombatDisengageTime → 以 PostureRegenRate 每秒恢复
② 离开 KnockDown（起身收尾）→ ReliefPosture() 回满
③ 接受投技 / 被处决结束后 → ReliefPosture() 回满（由演出收尾调用）
```

**`LastCombatTime` 刷新点：受击（`ReceiveDamage` 结算时）与攻击命中他人时。**

#### （3）BPI_CombatFeedBack

| 方法名             | 输入                                            | 输出  | 作用                                            |
| --------------- | --------------------------------------------- | --- | --------------------------------------------- |
| PlayHitFeedback | E_HitOutCome（Outcome），Vector3（ImpactLocation），bool（bPerfect），Actor（OtherActor），float（BaseHitStop） | /   | 播放命中音效、顿帧、屏幕抖动                                |
| PlayHitStop     | Actor，float                                   | /   | 根据命中者与时长播放顿帧                                  |
| EndHitStop      | /                                             | /   | 离开顿帧                                          |
| PlayEnemySlowMo | float（Scale），float（Duration） | /   | **只放慢全场敌人，不播任何音效**（自带恢复计时）。完美闪避传 (0.1, 0.5)，完美格挡传 (0.15, 0.12) |
| PlayPerfectDodgeStartSound | float（Duration）                  | /   | 播放完美闪避开始音，并在 **Duration 后自动播结束音**（内部计时，见下） |
| PlayPerfectBlockSound | /                                     | /   | 播放完美格挡撞击音（单一瞬态，无尾音计时）                |

**音效接口与慢动作接口是分离的两组，不能合并：**

```
完美闪避：PlayPerfectDodgeStartSound(0.5) + PlayEnemySlowMo(0.1, 0.5)
完美格挡：PlayPerfectBlockSound()          + PlayEnemySlowMo(0.15, 0.12)

⚠️ 如果音效写在 PlayEnemySlowMo 内部，完美格挡调用慢动作时会误播闪避音效
```

**`BPC_CombatFeedBack` 内部的音效收尾（不对外暴露）：**

| 名称 | 归属 | 说明 |
| --- | --- | --- |
| `PlayPerfectDodgeEndSound()` | **【内部函数】** | 由 `PlayPerfectDodgeStartSound` 的计时器触发，播结束音 |
| `PlayPerfectDodgeEndSound` | 变量 | 结束音资产 |
| `PerfectDodgeEndSoundVolume` | 变量 | 结束音音量 |
| `PerfectDodgeSoundTimer` | 变量 | 开始音 → 结束音的计时器句柄 |
| `PerfectBlockSound` | 变量 | 完美格挡撞击音资产 |

**⭐ 结束音不做成接口，理由和 `RestoreSlowMo` 一样 —— 它是「开始动作的收尾」，由发起方自己计时，外部不需要也**不能**直接调：**

```
PlayPerfectDodgeStartSound(Duration) 【接口实现】
  ├─【1】Clear and Invalidate Timer(PerfectDodgeSoundTimer)   ← 防叠加
  ├─【2】Spawn Sound 2D: PerfectDodgeStartSound
  └─【3】Set Timer by Event(Duration → PlayPerfectDodgeEndSound)

PlayPerfectDodgeEndSound() 【内部函数】
  └─ Spawn Sound 2D: PerfectDodgeEndSound（Volume = PerfectDodgeEndSoundVolume）
```

**⚠️ 第 1 步不能省：连续两次完美闪避时，第一次的结束音会和第二次的开始音叠在一起。这和 `PlayEnemySlowMo` 里「先 RestoreSlowMo 再重启」是同一个道理。**

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
| BreakPoise | 格挡中韧性（Poise）归零 —— 韧性逻辑，走 `HandleGuardBreak` |
| BreakPosture | 架势（Posture）归零 —— 架势逻辑，走 `HandleBreakPosture` → KnockDown |

> **共 5 个值。** `BreakPoise` 与 `BreakPosture` 平行：前者是格挡被击碎（HitHeavy），后者是防御崩坏（KnockDown）。两者同时触发时 `BreakPosture` 优先。

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

