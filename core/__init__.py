""" Useful utilities and constants for the addon """

import os
from importlib import reload
from inspect import isclass
from os.path import normpath
import sys
import bpy
from pathlib import Path
from ..utils import collections, modifiers, objects


def get_addon_path():
    """Get path of the addon"""
    return os.path.dirname(os.path.dirname(os.path.realpath(__file__)))

def get_addon_name():
    """Get name of the addon"""
    return os.path.basename(get_addon_path())

def get_project_name():
    """Get name of the current project"""
    projectName, _ = os.path.splitext(bpy.path.basename(bpy.context.blend_data.filepath))
    return projectName

def get_current_version():
    """Returns the current version of the loaded addon."""
    mod = sys.modules[get_addon_name()]
    current_version = mod.bl_info.get("version", (0, 0, 1))
    return '.'.join([str(num) for num in current_version])

def get_preferences():
    """Returns the addon's Preferences object."""
    return bpy.context.preferences.addons[get_addon_name()].preferences

def get_source_path():
    """Returns the Addon's Project source path."""
    source_path = get_preferences().source_path
    if not source_path:
        # use path of blend file as default
        return Path(bpy.data.filepath).parent
    return bpy.path.abspath(normpath(source_path))

def get_export_prefix():
    """Returns the Addon's export prefix for collections."""
    return get_preferences().export_prefix

def get_export_priority_object_prefix():
    """Returns the Addon's export prefix for priority objects."""
    return get_preferences().export_priority_object_prefix

def get_export_exclude_object_prefix():
    """Returns the Addon's export prefix for object exclude."""
    return get_preferences().export_exclude_object_prefix

def get_collision_prefix():
    """Returns the Addon's collision prefix for collections."""
    return get_preferences().collision_prefix

def get_lowpoly_regex():
    """Returns the Addon's lp regex for collections."""
    return get_preferences().lowpoly_regex

def get_highpoly_regex():
    """Returns the Addon's hp regex for collections."""
    return get_preferences().highpoly_regex

def get_export_collection_name():
    """Returns the Addon's export collections name"""
    return get_preferences().export_collection_name
    
def get_show_export_dialog():
    """Returns the Addon's Project source path."""
    return get_preferences().show_export_dialog

def get_collection_export_name_template():
    """Export current scene only."""
    return get_preferences().collection_export_name_template

def get_armature_export_name_template():
    """Export current scene only."""
    return get_preferences().armature_export_name_template

def find_exportable_collections():
    """Finds all the collections marked for export"""
    export_collections = []
    for collection in bpy.data.collections:
        if collection.name.startswith(get_export_prefix()) and not collections.is_linked(collection) and collections.is_in_current_Scene(collection):
            export_collections.append(collection)
    return export_collections

def find_exportable_armatures():
    """Finds all the collections marked for export"""
    export_armatures = []
    for armature in objects.find_all_of_type('ARMATURE'):
        if armature.name.startswith(get_export_prefix()) and objects.is_in_current_Scene(armature):
            export_armatures.append(armature)
    return export_armatures

def unselect_unwanted_objects_for_export():
    """Excludes unwanted objects from the selection"""
    for obj in bpy.context.selected_objects:
        if obj.name.startswith(get_export_exclude_object_prefix()):
            objects.remove_from_selection(obj)

def set_selection_priority_object_as_active():
    """Selects the first or marked object of the selected objects as active"""
    if not bpy.context.selected_objects:
        return
    for obj in bpy.context.selected_objects:
        if obj.name.startswith(get_export_priority_object_prefix()):
            objects.set_active(obj)
            return
    objects.set_active(bpy.context.selected_objects[0])

def reload_addon():
    """Reloads the Addon and all of its modules."""

    pref_items = get_preferences().items()
    bpy.ops.preferences.addon_disable(module=get_addon_name())

    bpy.ops.preferences.addon_enable(module=get_addon_name())

    # Reset the previous preference items onto the reloaded preferences
    get_preferences().set_items(pref_items)


def register_recursive(objects):
    """Registers classes with Blender recursively from modules."""
    for obj in objects:
        if isclass(obj):
            bpy.utils.register_class(obj)
        elif hasattr(obj, "register"):
            obj.register()
        elif hasattr(obj, "REGISTER_CLASSES"):
            register_recursive(obj.REGISTER_CLASSES)
        else:
            print(f"Warning: Failed to find anything to register for '{obj}'")


def unregister_recursive(objects):
    """Unregisters classes from Blender recursively from modules."""
    for obj in reversed(objects):
        if isclass(obj):
            bpy.utils.unregister_class(obj)
        elif hasattr(obj, "unregister"):
            obj.unregister()
        elif hasattr(obj, "REGISTER_CLASSES"):
            unregister_recursive(obj.REGISTER_CLASSES)
        else:
            print(f"Warning: Failed to find anything to unregister for '{obj}'")
