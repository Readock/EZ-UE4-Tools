import bpy
import os


def set_active(obj):
    """ Sets the object as active """
    if obj:
        obj.select_set(True)
        bpy.context.view_layer.objects.active = obj

def deselect():
    """ Deselects all active elements """
    bpy.ops.object.select_all(action='DESELECT')

def find_with_name(name):
    return bpy.context.scene.objects[name]

def set_active_with_name(name):
    set_active(find_with_name(name))

def smooth_normals_of_selected():
    if bpy.context.selected_objects:
        # make shure we have one object active selected
        if not bpy.context.view_layer.objects.active:
            set_active(bpy.context.selected_objects[0])
        bpy.ops.object.mode_set(mode='EDIT')
        bpy.ops.mesh.smooth_normals()
        switch_to_object_mode()

def unselect_none_solid():
    """ Unselect objects that are displayed as bounds or wire (usualy cutter) """
    for obj in bpy.context.selected_objects:
        if obj and obj.type == 'MESH':
            if obj.display_type == 'WIRE' or obj.display_type == 'BOUNDS':
                obj.select_set(False)

def switch_to_object_mode():
    """ Switch mode to object mode """
    if bpy.context.active_object and bpy.context.active_object.mode != 'OBJECT':
        bpy.ops.object.mode_set(mode='OBJECT')

def get_direct_children_of(obj):
    """ Get all direct childs of a object """
    if not obj:
        return []
    child_objects = []
    for childObj in bpy.data.objects:
        if childObj.library is None:
            pare = childObj.parent
            if pare is not None:
                if pare.name == obj.name:
                    child_objects.append(childObj)
    return child_objects

def get_children_of(obj):
    """ Get all (recrusive) childs of an object """
    child_objects = []
    if not obj:
        return child_objects
    def tryAppend(obj):
        if obj.name in bpy.context.scene.objects:
            child_objects.append(obj)

    for newobj in get_direct_children_of(obj):
        for childs in get_children_of(newobj):
            tryAppend(childs)
        tryAppend(newobj)
    return child_objects

def find_all_of_type(object_type):
    """ Finds all the objects of an type (eg. 'MESH' or 'ARMATURE') """
    objects = []
    for obj in bpy.data.objects:
        if obj.type == object_type:
            objects.append(obj)
    return objects


def unit_scale_selected(unit_scaling):
    """Scales selected objects to another unit scale"""
    for obj in bpy.context.selected_objects:
        # multiply location to get offsets right
        obj.location = [obj.location.x * unit_scaling, obj.location.y * unit_scaling, obj.location.z * unit_scaling]
        obj.scale = [obj.scale.x * unit_scaling, obj.scale.y * unit_scaling, obj.scale.z * unit_scaling]