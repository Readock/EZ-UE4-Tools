import bpy
import os

def units_blender_to_fbx_factor():
    """Use scene to determine the scale factor for unreal export"""
    # 100 because bender is in cm but we need meters
    scene = bpy.context.scene
    return 100.0 if scene and (scene.unit_settings.system == 'NONE') else (100.0 * scene.unit_settings.scale_length)