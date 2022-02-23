"""Keymap functionality."""

import bpy
from .ui import PieSave

__classes__ = (
)

addon_keymaps = []

def get_addon_keymaps():
    return addon_keymaps

def register():
    """Load keymaps"""
    # handle the keymap
    wm = bpy.context.window_manager
    km = wm.keyconfigs.addon.keymaps.new(name='Window', space_type='EMPTY')

    kmi = km.keymap_items.new('wm.call_menu_pie', 'W', 'PRESS', ctrl=True, shift=True, alt=True)
    kmi.properties.name = PieSave.bl_idname
    addon_keymaps.append((km, kmi))


def unregister():
    """Remove keymaps"""
    for km, kmi in addon_keymaps:
        km.keymap_items.remove(kmi)
    addon_keymaps.clear()