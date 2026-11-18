# WeaponBase（武器基类）

> 本文件是模块文档。项目总导航、规范与历史见 [README.md](../README.md)。

## 4，WeaponBase（武器基类）

### 1）WeaponBase 类接口方法

#### （1）BPI_WeaponBase

| 方法名             | 输入  | 输出    | 作用             |
| --------------- | --- | ----- | -------------- |
| GetWeaponBonus  | /   | float | 获取武器的攻击力加成     |
| GetWeaponHitBox | /   | 盒体碰撞  | 获取武器碰撞箱        |
| SetTrailActive  | bool | /     | 开关武器拖尾，`true` 激活 / `false` 停用（停用不销毁已生成粒子） |

---

