# -*- coding: utf-8 -*-
"""
战斗调试可视化组件脚手架脚本（修正版）

用途：
  在 UE 编辑器 Python 环境中运行，仅完成 BPC_CombatDebug 蓝图资产的新建与编译。
  加变量、给蓝图加组件、连节点图等 Python API 做不到的步骤，一律 print
  明确提示「需在编辑器中手工完成：xxx」，不得静默跳过。

约束：
  - 纯蓝图项目，不新增 C++ 类，不修改 .uproject，不引入第三方插件。
  - 不写 .uasset 二进制文件，不使用反射 hack 建节点图。
  - 脚本可重复执行：已存在则跳过，不报错。

运行方式：
  在 UE 编辑器 Python 控制台执行：
    import tools.ue_python.bootstrap_combat_debug as bcd
    bcd.main()
"""

import unreal


COMPONENT_BP_PATH = "/Game/Code/ActorComponent/CombatDebug/BPC_CombatDebug"
COMPONENT_CLASS_NAME = "BPC_CombatDebug"


def log(msg):
    print(f"[bootstrap_combat_debug] {msg}")


def asset_exists(asset_path):
    return unreal.EditorAssetLibrary.does_asset_exist(asset_path)


def create_component_blueprint():
    """
    新建 BPC_CombatDebug 蓝图（父类 ActorComponent），并尝试编译。
    已存在则跳过，不报错。
    """
    if asset_exists(COMPONENT_BP_PATH):
        log(f"跳过创建，蓝图已存在：{COMPONENT_BP_PATH}")
        return True

    try:
        unreal.EditorAssetLibrary.create_blueprint(
            parent_class=unreal.ActorComponent,
            name=COMPONENT_CLASS_NAME,
            path="/Game/Code/ActorComponent/CombatDebug"
        )
        log(f"已创建蓝图资产：{COMPONENT_BP_PATH}")
    except Exception as e:
        log(f"创建蓝图失败：{e}")
        return False

    # 尝试编译蓝图（API 支持时执行，不支持时忽略）
    try:
        blueprint = unreal.EditorAssetLibrary.load_blueprint_class(COMPONENT_BP_PATH)
        if blueprint is not None:
            blueprint.compile()
            log(f"已编译蓝图：{COMPONENT_BP_PATH}")
    except Exception as e:
        log(f"编译蓝图时出错（可能需在编辑器中手工编译）：{e}")

    return True


def main():
    log("===== 开始执行 bootstrap_combat_debug.py =====")

    create_component_blueprint()

    log("===== bootstrap_combat_debug.py 执行结束 =====")
    log("以下步骤无法通过 Python API 自动完成，请在编辑器中手工操作：")
    log("  1. 需在编辑器中手工完成：打开 BPC_CombatDebug，在「我的蓝图 → 变量」添加 bEnableDebug(Boolean, 默认 true)、DebugDrawDuration(Float, 默认 0.05) 及 BeginPlay 赋值的组件引用变量。")
    log("  2. 需在编辑器中手工完成：在 BPC_CombatDebug.Event BeginPlay 中，通过 Get Owner → Does Implement Interface → 接口消息取 Attribute / HitBox / Combat / ActionState / AI / AttackTrace 组件引用并赋值。")
    log("  3. 需在编辑器中手工完成：在 BPC_CombatDebug.Event Tick 中实现 bEnableDebug early return、Draw Debug Box（受击盒灰色线框）及角标节流逻辑。")
    log("  4. 需在编辑器中手工完成：将 BPC_CombatDebug 组件添加到 BP_Player 与 BP_EnemyBase。")
    log("  5. 需在编辑器中手工完成：新建 WBP_DebugOverlay UMG 小部件并按 docs/13 表格绑定字段数据源，添加到 Viewport。")
    log("  6. 需在编辑器中手工完成：改 BPC_Combat 与 BPC_AttackTrace 中 Box Trace Multi 的四个调试引脚（Draw Debug Type / Draw Time / Trace Color / Trace Hit Color）。")


if __name__ == "__main__":
    main()
