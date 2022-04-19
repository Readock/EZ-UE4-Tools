""" Useful utilities and constants for the addon """
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