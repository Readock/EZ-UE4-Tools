import bpy


def set_active(obj):
    """ Sets the object as active """
    if obj:
        obj.select_set(True)
        bpy.context.view_layer.objects.active = obj

def unselect_none_solid():
    """ Unselect objects that are displayed as bounds or wire (usualy cutter) """
    for obj in bpy.context.selected_objects:
        if obj and obj.type == 'MESH':
            if obj.display_type == 'WIRE' or obj.display_type == 'BOUNDS':
                obj.select_set(False)