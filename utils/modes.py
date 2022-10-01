import bpy

def switch_to_object():
    """ Switch mode to object mode """
    if bpy.context.active_object and bpy.context.active_object.mode != 'OBJECT':
        bpy.ops.object.mode_set(mode='OBJECT')

def switch_to_edit():
    """ Switch mode to object mode """
    if bpy.context.active_object and bpy.context.active_object.mode != 'EDIT':
        bpy.ops.object.mode_set(mode='EDIT')

def is_in_local_view():
    for area in bpy.context.screen.areas:
        if area.type == 'VIEW_3D':
            space = area.spaces[0]
            return space.local_view
    return False

def switch_to_local_view():
    """ Switch view to local view """
    if not is_in_local_view():
        bpy.ops.view3d.localview()

def switch_to_not_local_view():
    """ Switch view to not be in local view """
    if is_in_local_view():
        bpy.ops.view3d.localview()