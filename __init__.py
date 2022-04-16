""" A Blender add-on for faster fbx exporting """

from . import operators
from .core import menus, preferences, ui, keymap, register_recursive, unregister_recursive

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


def unregister():
    """Unregister all of the Addon classes."""
    unregister_recursive(REGISTER_CLASSES)
