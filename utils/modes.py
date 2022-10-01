import bpy

def switch_to_object():
    """ Switch mode to object mode """
    if bpy.context.active_object and bpy.context.active_object.mode != 'OBJECT':
        bpy.ops.object.mode_set(mode='OBJECT')

def switch_to_edit():
    """ Switch mode to object mode """
    if bpy.context.active_object and bpy.context.active_object.mode != 'EDIT':
        bpy.ops.object.mode_set(mode='EDIT')


def exit_local_view():
    """ Switch view to not be in local view """
    for area in bpy.context.screen.areas:
        if area.type == 'VIEW_3D':
            space = area.spaces[0]
            if space.local_view: #check if using local view
                for region in area.regions:
                    if region.type == 'WINDOW':
                        override = {'area': area, 'region': region} #override context
                        bpy.ops.view3d.localview(override) #switch to global view