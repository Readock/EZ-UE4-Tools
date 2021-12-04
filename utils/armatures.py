import bpy

def get_actions(armature):
    if not armature or not armature.animation_data or not armature.data:
        return []
    actions = [act for act in bpy.data.actions if is_armature_using_action(armature, act)]
    return actions


def is_armature_using_action(armature, action):
    return True if any(fc.data_path.partition('"')[2].split('"')[0] in armature.data.bones for fc in action.fcurves) else False

def create_animation_data(armature):
    if not armature.animation_data:
        armature.animation_data_create()

def clear_pose_transform(armature):
    for pb in armature.pose.bones:
        pb.location, pb.scale, pb.rotation_euler = [0.0, 0.0, 0.0], [1.0, 1.0, 1.0], [0.0, 0.0, 0.0]
        pb.rotation_quaternion, pb.rotation_axis_angle = [1.0, 0.0, 0.0, 0.0], [0.0, 0.0, 1.0, 0.0]