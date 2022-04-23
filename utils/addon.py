import subprocess
import os
import sys
import bpy

def get_addon_path():
    """Get path of the addon"""
    return os.path.dirname(os.path.dirname(os.path.realpath(__file__)))

def get_addon_name():
    """Get name of the addon"""
    return os.path.basename(get_addon_path())

def get_current_version():
    """Returns the current version of the loaded addon."""
    mod = sys.modules[get_addon_name()]
    current_version = mod.bl_info.get("version", (0, 0, 1))
    return '.'.join([str(num) for num in current_version])

def get_project_name():
    """Get name of the current project"""
    projectName, _ = os.path.splitext(bpy.path.basename(bpy.context.blend_data.filepath))
    return projectName

def get_blend_file_path():
    """Gets the blend file path ex. C:\\myfile.blend """
    return bpy.context.blend_data.filepath

def is_blend_file_saved():
    return bpy.data.is_saved