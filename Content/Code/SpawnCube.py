import unreal

# 在当前编辑器关卡中生成一个 Cube，位置 (0,0,100)
# 用法: Tools -> Execute Python Script 选择本文件，或在 Output Log 的 Python 页粘贴运行
subsystem = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
cube = subsystem.spawn_actor_from_class(
    unreal.StaticMeshActor,
    unreal.Vector(0.0, 0.0, 100.0),
    unreal.Rotator(0.0, 0.0, 0.0),
)
mesh = unreal.load_asset("/Engine/BasicShapes/Cube.Cube")
cube.static_mesh_component.set_static_mesh(mesh)
cube.set_actor_label("MyCube")
subsystem.set_selected_level_actors([cube])
unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).save_all_dirty_levels()
print("Cube 已创建: %s" % cube.get_actor_label())
