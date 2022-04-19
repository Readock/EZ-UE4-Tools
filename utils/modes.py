import bpy

def switch_to_object():
    """ Switch mode to object mode """
    if bpy.context.active_object and bpy.context.active_object.mode != 'OBJECT':
        bpy.ops.object.mode_set(mode='OBJECT')

def switch_to_edit():
    """ Switch mode to object mode """
    if bpy.context.active_object and bpy.context.active_object.mode != 'EDIT':
        bpy.ops.object.mode_set(mode='EDIT')