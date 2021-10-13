import bpy

from . import objects

def apply_modifiers(objectList):
    """ Apply all modifiers """
    for obj in objectList:
        if obj.type == "MESH":
            objects.set_active(obj)
            for mod in obj.modifiers:
                bpy.ops.object.modifier_apply(modifier=mod.name)