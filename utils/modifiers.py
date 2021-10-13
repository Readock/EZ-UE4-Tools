import bpy

from .objects import set_active

def apply_modifiers(object):
    """ Apply all modifiers """
    for obj in object:
        if obj.type == "MESH":
            set_active(obj)
            for mod in obj.modifiers:
                bpy.ops.object.modifier_apply(modifier=mod.name)