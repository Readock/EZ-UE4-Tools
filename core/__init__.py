""" Useful utilities and constants for the addon """

import os
from importlib import reload
from inspect import isclass
from os.path import normpath
import sys
import bpy
from pathlib import Path
from ..utils import collections, modifiers, objects

def find_exportable_collections():
    """Finds all the collections marked for export"""
    from . import preferences
    export_collections = []
    for collection in bpy.data.collections:
        if collection.name.startswith(preferences.export_prefix()) and not collections.is_linked(collection) and collections.is_in_current_Scene(collection):
            export_collections.append(collection)
    return export_collections

def find_exportable_armatures():
    """Finds all the collections marked for export"""
    from . import preferences
    export_armatures = []
    for armature in objects.find_all_of_type('ARMATURE'):
        if armature.name.startswith(preferences.export_prefix()) and objects.is_in_current_Scene(armature):
            export_armatures.append(armature)
    return export_armatures

def unselect_unwanted_objects_for_export():
    """Excludes unwanted objects from the selection"""
    from . import preferences
    for obj in bpy.context.selected_objects:
        if obj.name.startswith(preferences.export_exclude_object_prefix()):
            objects.remove_from_selection(obj)

def set_selection_priority_object_as_active():
    """Selects the first or marked object of the selected objects as active"""
    from . import preferences
    if not bpy.context.selected_objects:
        return
    for obj in bpy.context.selected_objects:
        if obj.name.startswith(preferences.export_priority_object_prefix()):
            objects.set_active(obj)
            return
    objects.set_active(bpy.context.selected_objects[0])

# def reload_addon():
#     """Reloads the Addon and all of its modules."""

#     pref_items = get_preferences().items()
#     bpy.ops.preferences.addon_disable(module=get_addon_name())

#     bpy.ops.preferences.addon_enable(module=get_addon_name())

#     # Reset the previous preference items onto the reloaded preferences
#     get_preferences().set_items(pref_items)


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
