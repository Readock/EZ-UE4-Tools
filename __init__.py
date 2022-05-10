""" A Blender add-on for faster fbx exporting """
import time
import bpy
from . import operators
from .core import menus, preferences, ui, keymap
from .utils import perforce, message
from inspect import isclass
from bpy.app.handlers import persistent

bl_info = {
        "name": "EZ-UE4 Tools",
        "description": "A tool for exporting fbx for unreal engine 4",
        "author": "Felix",
        "version": (0, 2),
        "blender": (2, 93, 0),
        "location": "EZ-UE4 Menu",
        "warning": "",
        "wiki_url": "https://github.com/Readock/EZ-UE4-Tools",
        "tracker_url": "https://github.com/Readock/EZ-UE4-Tools/issues/new/choose",
        "support": "COMMUNITY",
        "category": "Import-Export"
}


REGISTER_CLASSES = (
    preferences,
    ui,
    menus,
    keymap,
    operators,
)


def register():
    """Register all of the Addon classes."""
    register_recursive(REGISTER_CLASSES)
    bpy.app.handlers.load_post.append(check_for_p4)
    bpy.app.handlers.save_post.append(check_for_p4)

def unregister():
    """Unregister all of the Addon classes."""
    unregister_recursive(REGISTER_CLASSES)

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


@persistent
def check_for_p4(dummy):
    """Check if blend file needs checkout"""
    if preferences.perforce_enabled() and perforce.is_checkout_needed():
        message.show("ERROR: ", "Blend file needs checkout!", "ERROR")