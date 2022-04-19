import bpy
from . import objects
from .selection_context import SelectionContext

def apply_modifiers(objectList):
    """ Apply all modifiers """
    with SelectionContext():
        for obj in objectList:
            if obj.type == "MESH":
                objects.set_active(obj)
                for mod in obj.modifiers:
                    try:
                        bpy.ops.object.modifier_apply(modifier=mod.name)
                    except Exception as ex: 
                        print(f"WARNING: Could not apply modifier {mod.name} of {obj.name}")    