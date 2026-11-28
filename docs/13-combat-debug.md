# 战斗调试可视化

> 本文件是模块文档。项目总导航、规范与历史见 [README.md](../README.md)。
>
> 唯一目的：把「攻击打空」的三种原因区分开——距离不够 / 判定窗口没开 / 判定体挂错位置。
>
> 纯蓝图项目，不新增任何 C++ 类，不修改 `.uproject`，不引入第三方插件，不新增任何 `BPI_` 接口。

---

## 0，已知事实（禁止推翻）

| 项目 | 内容 |
| --- | --- |
| 玩家伤害判定 | `BPC_Combat` 里的 `Box Trace Multi`，Trace Channel = `TraceTypeQuery3` |
| 敌人伤害判定 | `BPC_AttackTrace` 里的 `Box Trace Multi`，Trace Channel = `TraceTypeQuery4` |
| 判定窗口守卫 | 两者都只在攻击窗口内逐帧执行（`BPC_Combat.bAttackWindowOpen` / `BPC_AttackTrace.bWindowOpen`） |
| `Box Trace Multi` 自带调试 | 节点本身有四个引脚：`Draw Debug Type` / `Draw Time` / `Trace Color` / `Trace Hit Color` |
| `TraceStart / TraceEnd` | 是 `Break Hit Result` 的输出引脚，不是组件变量 |
| `OnAttackWindow` | 接口函数（由 `ANS_AttackWindow` 调用），不是 Event Dispatcher，不能 `Bind` |
| 不存在的函数 | `GetInvincible` / `IsCancelWindowOpen` / `IsAttackWindowOpen` / `GetTraceStart` / `GetTraceEnd` |
| 只写不读的函数 | `SetInvincible`（`BPI_Attribute`） / `SetCancelWindow`（`BPI_ActionState`） |
| 取组件写法 | `Get Owner` → `Does Implement Interface` → 接口消息取组件，禁止 `Get Components by Interface` |

---

## 1，阶段一 · 点亮真实判定体（零新增资产，只改 4 个引脚）

### 1.1 要改的两个节点

| 蓝图资产 | Box Trace Multi 节点 | 引脚名 | 改为 |
| --- | --- | --- | --- |
| `BPC_Combat` | 玩家攻击判定的 `Box Trace Multi` | `Draw Debug Type` | `For Duration` |
| `BPC_Combat` | 同上 | `Draw Time` | `0.1` |
| `BPC_Combat` | 同上 | `Trace Color` | `红` (R=255, G=0, B=0) |
| `BPC_Combat` | 同上 | `Trace Hit Color` | `黄` (R=255, G=255, B=0) |
| `BPC_AttackTrace` | 敌人攻击判定的 `Box Trace Multi` | `Draw Debug Type` | `For Duration` |
| `BPC_AttackTrace` | 同上 | `Draw Time` | `0.1` |
| `BPC_AttackTrace` | 同上 | `Trace Color` | `红` (R=255, G=0, B=0) |
| `BPC_AttackTrace` | 同上 | `Trace Hit Color` | `黄` (R=255, G=255, B=0) |

### 1.2 为什么改这一个设置就够了

`Box Trace Multi` 只在攻击窗口内逐帧执行，窗口外不执行。因此：

- **红色框出现 + 命中目标 = 正常命中**
- **红色框出现但没打到任何人 = 距离不够**（判定体在空气里）
- **红色框完全不出现 = 窗口没开**（`Box Trace Multi` 本帧没执行）
- **红色框贴在角色身体上，或远离刀身 = box 尺寸 / socket 挂点配错**（判定体位置不对）

`Draw Time = 0.1` 保证框只在执行帧可见，下一帧消失，不会残留。

### 1.3 Shipping 包影响

`Draw Debug` 节点在 Shipping 打包时会被编译掉，不影响正式版本性能和体积。

### 1.4 做完在 PIE 里应该看到什么

挥攻击时，武器路径上会闪现一条红色盒状框，命中目标时框尖端变黄；攻击结束或打空时框立即消失。

---

## 2，阶段二 · 受击盒 + 状态角标（只读，不新增接口）

### 2.1 新建组件：`BPC_CombatDebug`

| 项目 | 内容 |
| --- | --- |
| 类型 | `ActorComponent`（蓝图） |
| 路径 | `Code/ActorComponent/CombatDebug/BPC_CombatDebug` |
| 挂载对象 | `BP_Player`、`BP_EnemyBase`（分别挂载，不挂 `CharacterBase`） |
| 不挂载 | `CharacterBase`（项目没有中间基类蓝图） |
| 只读约束 | 组件内只允许 `Get`，禁止 `Set` 别人的东西；禁止 `Set Timer`；不改任何数据表或组件属性；唯一允许写的是自己的 `bEnableDebug` |

### 2.2 成员变量（BeginPlay 赋一次，Tick 中只用不重取）

| 变量名 | 类型 | 默认值 | 作用 |
| --- | --- | --- | --- |
| `bEnableDebug` | Boolean | `true` | 主开关。`false` 时 Tick 首行 `Early Return`，不调用任何接口（零开销） |
| `DebugDrawDuration` | Float | `0.05` | 调试图元持续时间，单位秒 |
| `CachedAttribute` | `BPI_Attribute` 引用 | 空 | 角色属性组件，用于读血量 / 架势百分比 |
| `CachedHitBox` | `BoxComponent` 引用 | 空 | 角色受击盒，用于画灰色线框 |
| `CachedCombat` | `BPI_Combat` 引用 | 空 | 玩家攻击组件（敌人无此组件，为空时跳过） |
| `CachedActionState` | `BPI_ActionState` 引用 | 空 | 玩家状态组件（敌人无此组件，为空时跳过） |
| `CachedAI` | `BPI_AI` 引用 | 空 | 敌人 AI 组件（玩家无此组件，为空时跳过） |
| `CachedAttackTrace` | `BPI_AttackTrace` 引用 | 空 | 敌人攻击组件（玩家无此组件，为空时跳过） |

> 变量通过 `Get Owner` → `Does Implement Interface` → 接口消息取得，见 2.3 节。

### 2.3 `Event BeginPlay`：取组件引用（只执行一次）

```text
Owner = Get Owner

CachedAttribute = Owner → BPI_CharacterBase.GetAttributeComponent()
CachedHitBox    = Owner → BPI_CharacterBase.GetHitBoxComponent()

若 Owner 实现 BPI_Player:
  CachedCombat     = Owner → BPI_Player.GetCombatComponent()
  CachedActionState= Owner → BPI_Player.GetActionStateComponent()

若 Owner 实现 BPI_EnemyBase:
  CachedAI         = Owner → BPI_EnemyBase.GetAIComponent()
  CachedAttackTrace= Owner → BPI_EnemyBase.GetAttackTraceComponent()
```

> 禁止使用 `Get Components by Interface`。若某个接口不存在（例如敌人没有 `BPI_Combat`），对应缓存变量为空，Tick 中按 `IsValid` 守卫跳过。

### 2.4 `Event Tick`：实现顺序（按此顺序连节点，禁止调整）

```text
步骤 1：Branch: bEnableDebug == false
  ├─ True → Return（不调用任何接口，不执行后续任何节点，零开销）
  └─ False → 继续

步骤 2：若 CachedHitBox 有效
  └─ Draw Debug Box
       Center = CachedHitBox.Get Component Location()
       Extent = CachedHitBox.Get Scaled Box Extent()
       Rotation = CachedHitBox.Get Component Rotation()
       Color = 灰 (128,128,128)
       Life Time = DebugDrawDuration
       Persistent Lines = false

步骤 3：角标节流（见 2.5 / 2.6）
```

### 2.5 角标做法 A：临时版（推荐先用）

在 `Event Tick` 中累计 `DeltaTime`，每 `0.2` 秒执行一次 `Print String`，拼一行：

```text
状态 / AI 状态 / 血量% / 架势% / 招式 ID / 是否持令牌
```

每个字段的数据源（只用现有函数）：

| 字段 | 数据源接口 | 函数 | 输出 |
| --- | --- | --- | --- |
| 状态 | `BPI_ActionState` | `GetActionState()` | `E_ActionState` |
| AI 状态 | `BPI_AI` | `AI_GetAIState()` | `E_AIState` |
| 血量% | `BPI_Attribute` | `GetHealthPercent()` | float (0~1) |
| 架势% | `BPI_Attribute` | `GetPosturePercent()` | float (0~1) |
| 招式 ID | `BPI_Combat` | `GetCurrentAttack()` → `ST_AttackData.ID` | Name |
| 是否持令牌 | `BPI_GameState` | `HasToken(OwnerActor)` | Boolean |

```text
Tick 内：
  Accumulator += DeltaTime
  若 Accumulator >= 0.2:
    Accumulator = 0
    拼接字符串：
      [状态]=[GetActionState] [AI状态]=[AI_GetAIState] [血%]=[GetHealthPercent] [架%]=[GetPosturePercent] [招式]=[GetCurrentAttack.ID] [令牌]=[HasToken]
    Print String
```

> 不要每帧 `Print String`，避免输出窗口刷屏。

### 2.6 角标做法 B：正式版

新建 `WBP_DebugOverlay` UMG 小部件，挂到 `BP_PlayerController` 的 Viewport，只读上面列出的缓存引用。具体字段 → 接口 → 函数对照表同上。暂不实现无敌、取消窗口、攻击窗口标志（读不到，属于阶段三）。

### 2.7 这一层明确不做

- 不做无敌帧可视化（`BPI_Attribute` 没有 `GetInvincible`，`SetInvincible` 只写不读）
- 不做取消窗口可视化（`BPI_ActionState` 没有 `IsCancelWindowOpen`，`SetCancelWindow` 只写不读）
- 不做攻击窗口标志（`OnAttackWindow` 是接口函数，不是 Event Dispatcher，不能 `Bind`）

### 2.8 做完在 PIE 里应该看到什么

角色身上常驻一个灰色线框（受击盒），跟随角色移动；每 0.2 秒屏幕左上角（或控制台）打印一行状态字符串。

---

## 3，阶段三 · 时间窗口（只写方案，暂不实现）

### 3.1 要解决什么

阶段一给的是空间（判定体在哪），阶段二给的是对象状态（血量、架势、当前招式）。还缺一层时间：

- **无敌帧** = 完美闪避 / 完美格挡的真实起止时刻，调无敌时长与尾巴时需要看到；
- **取消窗口** = `bCanCancel`，由 `ST_AttackData.CancelStart` 驱动，调连招手感时需要看到。

### 3.2 两个 getter 的签名和落点（未获批准，暂不实现）

| 接口 | 函数签名 | 落点实现 | 返回值来源 |
| --- | --- | --- | --- |
| `BPI_Attribute` | `IsInvincible() → bool` | `BPC_Attribute` | `Return bInvincible`（变量名在编辑器核对） |
| `BPI_ActionState` | `IsCancelWindowOpen() → bool` | `BPC_ActionState` | `Return bCanCancel`（变量名在编辑器核对） |

> 状态标注：**未获批准，暂不实现**。不要把这两个 getter 混进阶段二的步骤里。

### 3.3 接口数影响（方案层面说明）

若未来获批并实现这两个接口：

```text
BPI_Attribute   20 → 21
BPI_ActionState 11 → 12
接口函数总数    128 → 130
```

README 接口总览需同步更新。本阶段不做任何接口修改。

### 3.4 做完在 PIE 里应该看到什么（方案阶段，预期）

完美闪避/完美格挡触发时，角色周身出现蓝色指示；连招后摇可取消的窗口期内出现绿色提示。暂不实现。

---

## 4，阶段四 · 只读约束

`BPC_CombatDebug` 组件里只允许 `Get`，不允许 `Set` 别人的东西；不允许 `Set Timer`（角标节流用 `Tick` 里累计 `DeltaTime`）；不允许改 `ST_AttackData` / `DT_Attacks` / `DT_Reactions` / 任何组件属性；唯一允许写的是自己的 `bEnableDebug`。

---

## 5，还需要在编辑器里手工完成的事项

按顺序编号，每项写成：改哪个资产 → 打开哪个图/节点 → 改哪个引脚或加什么节点 → 连到哪。

1. **`BPC_Combat`** → 打开 `Event Graph`，找到玩家攻击判定的 `Box Trace Multi` 节点 → `Draw Debug Type` 设为 `For Duration`，`Draw Time` 设为 `0.1`，`Trace Color` 设为红 (255,0,0)，`Trace Hit Color` 设为黄 (255,255,0)。

2. **`BPC_AttackTrace`** → 打开 `Event Graph`，找到敌人攻击判定的 `Box Trace Multi` 节点 → `Draw Debug Type` 设为 `For Duration`，`Draw Time` 设为 `0.1`，`Trace Color` 设为红 (255,0,0)，`Trace Hit Color` 设为黄 (255,255,0)。

3. **新建 `BPC_CombatDebug` 蓝图** → 路径 `Code/ActorComponent/CombatDebug/BPC_CombatDebug`，父类选 `ActorComponent` → 在「我的蓝图 → 变量」添加表 2.2 列出的全部变量。

4. **`BPC_CombatDebug.Event BeginPlay`** → 加 `Get Owner` → `Does Implement Interface(BPI_CharacterBase)` → 接口消息 `GetAttributeComponent` / `GetHitBoxComponent` → 分别设到 `CachedAttribute` / `CachedHitBox`；再按 Owner 是否实现 `BPI_Player` / `BPI_EnemyBase`，通过对应接口消息设到 `CachedCombat` / `CachedActionState` / `CachedAI` / `CachedAttackTrace`。

5. **`BPC_CombatDebug.Event Tick`** → 加 `Branch: bEnableDebug == false`，True 直接 `Return`；False 继续 → 若 `CachedHitBox` 有效，加 `Draw Debug Box`，`Center` 接 `CachedHitBox.Get Component Location()`，`Extent` 接 `Get Scaled Box Extent()`，`Rotation` 接 `Get Component Rotation()`，`Color` 设灰 (128,128,128)，`Life Time` 接 `DebugDrawDuration`。

6. **角标临时版（Print String）** → 在 `BPC_CombatDebug.Event Tick` 中加 `DeltaTime` 累加器，每 `0.2` 秒触发一次 `Print String`，字符串拼接 `GetActionState()` / `AI_GetAIState()` / `GetHealthPercent()` / `GetPosturePercent()` / `GetCurrentAttack().ID` / `BPI_GameState.HasToken(Owner)`。

7. **角标正式版（可选）** → 新建 `WBP_DebugOverlay` UMG 小部件，添加文本框/进度条，逐项绑定 2.5 表中的接口函数；在 `BP_PlayerController` 中 `Create Widget` → `Add to Viewport`。

8. **在 `BP_Player` 上添加组件** → 打开 `BP_Player` 蓝图 → 左侧「组件」面板 → `Add` → 搜索 `BPC_CombatDebug` → 添加，`bEnableDebug` 保持默认 `true`。

9. **在 `BP_EnemyBase` 上添加组件** → 打开 `BP_EnemyBase` 蓝图 → 左侧「组件」面板 → `Add` → 搜索 `BPC_CombatDebug` → 添加，`bEnableDebug` 保持默认 `true`。
