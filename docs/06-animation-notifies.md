# 玩家侧动画通知与职责

> 本文件是模块文档。项目总导航、规范与历史见 [README.md](../README.md)。

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

## 7-1，敌人侧动画通知与职责

> 敌人与玩家共用动画通知链路，但**预警与倒地演出是敌人专属通知**：玩家攻击 Montage 不放预警通知，避免玩家自身触发红光。

| 通知                          | 类型          | 调用的接口                                   | 职责                                                       |
| --------------------------- | ----------- | --------------------------------------- | -------------------------------------------------------- |
| `ANS_AttackWarning`         | NotifyState | `BPI_CombatFeedBack.SetAttackWarning(bool)` | 覆盖攻击前摇段：Begin 开启全身红光 + `Custom Depth` 描边 + 预警音，End 全部关闭 |
| `ANS_Enemy_AttackWindow`    | NotifyState | `BPI_AttackTrace.OnAttackWindow(bool)`  | 敌人攻击判定窗口开合（与玩家 `ANS_AttackWindow` 同一职责位，按敌人 Montage 配置） |
| `ANS_Telegraph`             | NotifyState | 依具体实现（预警段计时/表现开关）                        | 攻击预警段的区间标记，用于驱动预警表现时长（与 `ANS_AttackWarning` 配合或替代） |
| `AN_Enemy_KnockDownLoopStart` | Notify    | `BPI_AttackTrace.OnKnockDownLoopStarted` | 敌人倒地 Montage 进入 Loop：启动倒地计时器，到期跳转 `End`                     |

**要点：**

```
① ANS_AttackWarning 只放在敌人攻击 Montage，玩家攻击 Montage 不放
   → 否则玩家攻击时自身也会发红光

② 预警通知的位置由动画师决定：起点在前摇 25%~35% 处，终点与攻击窗口开启帧对齐
   → 红光灭 = 判定即将生效，是给玩家的"该防了"信号

③ AN_Enemy_KnockDownLoopStart 只发通知，不做 SetTimer / JumpToSection
   → Timer 与跳段全部由 BPC_AttackTrace 内部处理

④ 敌人播完倒地后保持受控，不回流 Chase/Idle（死亡优先）
```

---

