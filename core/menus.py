"""Menus"""

import bpy
from .ui import menu_draw
from .. import operators
from . import find_exportable_armatures, find_exportable_collections


SEPARATOR = 'SEPARATOR'


def _draw_separator(self, context):
    """Just draw a separator."""
    self.layout.row().separator()


class MenuBuilder():
    """Helper class for building and updating menus consistently."""

    _items = ()

    def __init__(self, menu):
        self._menu = menu

    def add_items(self, *args):
        """Add the arguments as operators."""
        self._items = args

    def register(self):
        """Register the items with the menu."""
        for item in self._items:
            if item is SEPARATOR:
                self._menu.append(_draw_separator)
            elif getattr(item, 'menu_draw', None) is not None:
                self._menu.append(item.menu_draw)
            else:
                print(f"Warning: {item} has been added to a menu, but has no 'menu_draw' method!")

    def unregister(self):
        """Unregister the operators from the menu."""
        for item in reversed(self._items):
            if item is SEPARATOR:
                self._menu.remove(_draw_separator)
            else:
                self._menu.remove(item.menu_draw)

        self._items = ()


__registered_menus__ = []


def register():
    """Register all of the classes and build the menus"""

    bpy.types.TOPBAR_MT_editor_menus.append(menu_draw)

    ezue4_menu = MenuBuilder(bpy.types.TOPBAR_MT_EZUE4)
    ezue4_menu.add_items(
        # operators.documentation,
        operators.open_source_path,
        SEPARATOR,
        operators.animation_export,
        operators.collection_exporter,
    )

    classes = (
        ezue4_menu,
    )

    for cls in classes:
        cls.register()
        __registered_menus__.append(cls)


def unregister():
    """Unregister all of the classes and clean up"""
    for cls in reversed(__registered_menus__):
        cls.unregister()

    bpy.types.TOPBAR_MT_editor_menus.remove(menu_draw)


class CollectionsInfoPanel(bpy.types.Panel):
    bl_idname = "export_collection_info_panel"
    bl_label = "Export Collection Info Panel"

    def menu_draw(self, context):
        """Draw the export panel."""        
        export_collections = find_exportable_collections()

        if not export_collections:
            self.layout.label(text="No Export Collections in scene!")
            return

        self.layout.label(text=f"{len(export_collections)} Export Collections in scene")



class ArmatureInfoPanel(bpy.types.Panel):
    bl_idname = "export_armature_info_panel"
    bl_label = "Export Armature Info Panel"

    def menu_draw(self, context):
        """Draw the export panel."""        
        export_objects = find_exportable_armatures()

        if not export_objects:
            self.layout.label(text="No Export Armatures in scene!")
            return

        self.layout.label(text=f"{len(export_objects)} Export Armatures in scene")
