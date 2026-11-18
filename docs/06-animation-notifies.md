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

