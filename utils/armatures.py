import bpy

def get_actions(armature):
    if not armature or not armature.animation_data or not armature.data.jk_adc:
        return []
    actions, _ = armature.data.jk_adc.get_actions(armature, False)
    return actions

def create_animation_data(armature):
    if not armature.animation_data:
        armature.animation_data_create()

def clear_pose_transform(armature):
    for pb in armature.pose.bones:
        pb.location, pb.scale, pb.rotation_euler = [0.0, 0.0, 0.0], [1.0, 1.0, 1.0], [0.0, 0.0, 0.0]
        pb.rotation_quaternion, pb.rotation_axis_angle = [1.0, 0.0, 0.0, 0.0], [0.0, 0.0, 1.0, 0.0]