# 其他独立接口

> 本文件是模块文档。项目总导航、规范与历史见 [README.md](../README.md)。

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

