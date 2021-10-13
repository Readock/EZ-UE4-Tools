""" A Blender add-on for faster fbx exporting """

from . import operators
from .core import menus, preferences, ui, register_recursive, unregister_recursive

bl_info = {
        "name": "EZ UE4 Tools",
        "description": "A tool for exporting fbx",
        "author": "Felix",
        "version": (1, 0),
        "blender": (2, 93, 0),
        "location": "EZ-UE4 menu",
        "warning": "",
        "wiki_url": "https://github.com/Readock/EZ-UE4-Tools",
        "tracker_url": "https://github.com/Readock/EZ-UE4-Tools/issues/new/choose",
        "support": "COMMUNITY",
        "category": "Import-Export"
}


REGISTER_CLASSES = (
    preferences,
    ui,
    operators,
    menus,
)


def register():
    """Register all of the Addon classes."""
    register_recursive(REGISTER_CLASSES)


def unregister():
    """Unregister all of the Addon classes."""
    unregister_recursive(REGISTER_CLASSES)
