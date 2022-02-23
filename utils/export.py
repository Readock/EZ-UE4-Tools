import bpy
import os

def units_blender_to_fbx_factor():
    """Use scene to determine the scale factor for unreal export"""
    # 100 because bender is in cm but we need meters
    scene = bpy.context.scene
    return 100.0 if scene and (scene.unit_settings.system == 'NONE') else (100.0 * scene.unit_settings.scale_length)



def selected_objects_as_fbx(fix_scale, export_path):
    """ Exports selected objects as fbx """
    from . import objects

    if fix_scale:
        # scale to fix ue4 scaling issues
        export_scale_factor = units_blender_to_fbx_factor()
        objects.unit_scale_selected(export_scale_factor)
        objects.apply_scale_and_rotation_to_selected()
    bpy.ops.export_scene.fbx(filepath=export_path, 
        use_selection=True,            
        apply_scale_options='FBX_SCALE_ALL', 
        apply_unit_scale= True,
        bake_space_transform=False,
        global_scale= 1.0,
        mesh_smooth_type="EDGE")
    if fix_scale:
        # revert the scaling (for better debugging and ucx was scaled as well)
        objects.unit_scale_selected(1.0/export_scale_factor)
        objects.apply_scale_and_rotation_to_selected()